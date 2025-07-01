import os
import sys
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType
from pyspark.sql import Column
import logging
from datetime import datetime, timedelta
import argparse


# Configuration class for better parameter management
# Take a look at dataclass in python: https://www.youtube.com/watch?v=mVea6Mu15l8
@dataclass
class FactConfig:
    """Configuration class for fact loading parameters"""
    bronze_base_path: str = "s3a://bronze/yellow_tripdata_partitioned_by_day"
    database_name: str = "silver"
    start_date: Optional[str] = None  # If None, defaults to yesterday
    end_date: Optional[str] = None  # If None, defaults to start_date
    data_year_offset: int = 1  # Process data from 1 year ago by default

    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            bronze_base_path=os.getenv("BRONZE_BASE_PATH", "s3a://bronze/yellow_tripdata_partitioned_by_day"),
            database_name=os.getenv("DATABASE_NAME", "silver"),
            start_date=os.getenv("START_DATE"),
            end_date=os.getenv("END_DATE"),
            data_year_offset=int(os.getenv("DATA_YEAR_OFFSET", "1"))
        )


# Enhanced logging configuration
def setup_logging() -> logging.Logger:
    """Setup logging configuration with proper formatting and handlers"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("Starting Spark Load Facts Application")
    logger.info("=" * 80)

    return logger


# Initialize logger
logger = setup_logging()


def get_spark_session(app_name: str = "Load Facts") -> SparkSession:
    """
    Create and configure Spark session with optimized settings

    Args:
        app_name: Name of the Spark application

    Returns:
        Configured SparkSession
    """
    try:
        logger.info(f"Creating Spark session: {app_name}")
        spark = SparkSession.builder.appName(app_name).getOrCreate()

        # Log Spark configuration
        logger.info(f"Spark version: {spark.version}")
        logger.info(f"Spark master: {spark.sparkContext.master}")
        logger.info(f"Application ID: {spark.sparkContext.applicationId}")

        return spark
    except Exception as e:
        logger.error(f"Failed to create Spark session: {str(e)}")
        raise


def create_nessie_database(spark: SparkSession, name: str = "silver") -> None:
    """
    Create Nessie database/namespace if it doesn't exist

    Args:
        spark: SparkSession instance
        name: Database name to create
    """
    try:
        logger.info(f"Creating Nessie database: {name}")
        spark.sql(f"CREATE NAMESPACE IF NOT EXISTS nessie.{name};")
        logger.info(f"Successfully created/verified database: nessie.{name}")
    except Exception as e:
        logger.error(f"Failed to create database {name}: {str(e)}")
        logger.warning(
            f"Continuing without database creation - table creation will handle namespace creation if needed")


def calculate_processing_dates(config: FactConfig) -> List[str]:
    """
    Calculate the dates to process based on configuration

    Args:
        config: Configuration object

    Returns:
        List of dates to process in YYYY-MM-DD format
    """
    try:
        # If no start_date provided, default to yesterday
        if not config.start_date:
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime("%Y-%m-%d")
        else:
            start_date = config.start_date

        # If no end_date provided, use start_date (single day)
        if not config.end_date:
            end_date = start_date
        else:
            end_date = config.end_date

        # Convert to datetime objects for processing
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Apply year offset to get actual data year
        data_start_dt = start_dt.replace(year=start_dt.year - config.data_year_offset)
        data_end_dt = end_dt.replace(year=end_dt.year - config.data_year_offset)

        # Generate list of dates
        dates = []
        current_dt = data_start_dt
        while current_dt <= data_end_dt:
            dates.append(current_dt.strftime("%Y-%m-%d"))
            current_dt += timedelta(days=1)

        logger.info(f"Processing dates: {dates}")
        logger.info(f"Data source year offset: {config.data_year_offset}")
        logger.info(f"Target dates: {start_date} to {end_date}")
        logger.info(f"Source data dates: {data_start_dt.strftime('%Y-%m-%d')} to {data_end_dt.strftime('%Y-%m-%d')}")

        return dates

    except Exception as e:
        logger.error(f"Failed to calculate processing dates: {str(e)}")
        raise


def convert_to_timeid(timestamp_col: str) -> Column:
    """
    Convert timestamp to timeid format (YYYYMMDDHHMM) for dimension table join

    Args:
        timestamp_col: Column name containing timestamp

    Returns:
        TimeID column in YYYYMMDDHHMM format (matching dimtime table)
    """
    return F.date_format(F.col(timestamp_col), "yyyyMMddHHmm").cast("long")


def add_quality_checks(df: DataFrame) -> DataFrame:
    """
    Add data quality checks and quality_issue column

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with quality_issue column added
    """
    return df.withColumn(
        "quality_issue",
        F.when(
            (F.col("tpep_pickup_datetime").isNull()) |
            (F.col("tpep_dropoff_datetime").isNull()) |
            (F.col("tpep_pickup_datetime") > F.col("tpep_dropoff_datetime")) |
            (F.col("PULocationID").isNull()) |
            (F.col("DOLocationID").isNull()),
            F.lit("corrupted")
        ).otherwise(F.lit("good"))
    )


def transform_fact_data(df: DataFrame) -> DataFrame:
    """
    Transform raw trip data to fact table format

    Args:
        df: Raw trip data DataFrame

    Returns:
        Transformed fact DataFrame
    """
    logger.info("Transforming fact data...")

    # Add quality checks first
    df_with_quality = add_quality_checks(df)

    # Transform to fact table format
    fact_df = df_with_quality.select(
        F.monotonically_increasing_id().alias("TripID"),
        convert_to_timeid("tpep_pickup_datetime").alias("PickupDateTimeID"),
        convert_to_timeid("tpep_dropoff_datetime").alias("DropOffDateTimeID"),
        F.col("PULocationID").cast("int").alias("PULocationID"),
        F.col("DOLocationID").cast("int").alias("DOLocationID"),
        F.col("RatecodeID").cast("int").alias("RateCodeID"),
        F.col("payment_type").cast("int").alias("PaymentTypeID"),
        F.col("passenger_count").cast("int").alias("PassengerCount"),
        F.col("trip_distance").cast("double").alias("TripDistance"),
        F.col("fare_amount").cast("double").alias("FareAmount"),
        F.col("tip_amount").cast("double").alias("TipAmount"),
        F.col("tolls_amount").cast("double").alias("TollsAmount"),
        F.col("airport_fee").cast("double").alias("AirportAmount"),
        F.col("total_amount").cast("double").alias("TotalAmount"),
        F.col("extra").cast("double").alias("Extra"),
        F.col("mta_tax").cast("double").alias("MTATax"),
        F.col("congestion_surcharge").cast("double").alias("CongestionSurcharge"),
        F.col("quality_issue")
    )

    logger.info(f"Transformed fact data schema: {fact_df.schema}")
    return fact_df


def read_bronze_data(spark: SparkSession, config: FactConfig, date: str) -> Optional[DataFrame]:
    """
    Read data from bronze layer for a specific date

    Args:
        spark: SparkSession instance
        config: Configuration object
        date: Date in YYYY-MM-DD format

    Returns:
        DataFrame if data exists, None otherwise
    """
    try:
        # Parse date to get year, month, day
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        # Construct path
        data_path = f"{config.bronze_base_path}/year={year}/month={month}/day={day}"

        logger.info(f"Reading data from: {data_path}")

        # Check if path exists by trying to read
        try:
            df = spark.read.parquet(data_path)
            row_count = df.count()

            if row_count == 0:
                logger.warning(f"No data found for date {date} at path {data_path} (empty DataFrame)")
                return None

            logger.info(f"Successfully read {row_count} rows for date {date}")
            return df

        except Exception as e:
            error_msg = str(e)
            if "Path does not exist" in error_msg or "No files found" in error_msg:
                logger.warning(f"No data found for date {date} at path {data_path}: Path does not exist")
            elif "AnalysisException" in error_msg:
                logger.warning(f"No data found for date {date} at path {data_path}: Analysis exception - {error_msg}")
            else:
                logger.warning(f"Error reading data for date {date} at path {data_path}: {error_msg}")
            return None

    except Exception as e:
        logger.error(f"Failed to read data for date {date}: {str(e)}")
        return None


def write_fact_table(spark: SparkSession, df: DataFrame, date: str, config: FactConfig) -> bool:
    """
    Write fact table data with day-based partitioning

    Args:
        spark: SparkSession instance
        df: DataFrame to write
        date: Processing date for partitioning (source date)
        config: Configuration object

    Returns:
        True if successful, False otherwise
    """
    try:
        # Parse source date (the date we're reading from)
        source_date_obj = datetime.strptime(date, "%Y-%m-%d")

        # Calculate target date (the date we want in the fact table)
        # If we're reading from 2024-06-01 with offset=1, we want to write to 2025-06-01
        target_date_obj = source_date_obj.replace(year=source_date_obj.year + config.data_year_offset)
        target_year = target_date_obj.year
        target_month = target_date_obj.month
        target_day = target_date_obj.day

        table_name = f"nessie.{config.database_name}.fact_trip"

        logger.info(
            f"Writing fact data for source date {date} to target partition year={target_year}/month={target_month}/day={target_day}")

        # Add partitioning columns to the DataFrame
        df_with_partitions = df.withColumn("year", F.lit(target_year)) \
            .withColumn("month", F.lit(target_month)) \
            .withColumn("day", F.lit(target_day))

        # Check if table exists
        table_exists = False
        try:
            spark.sql(f"SELECT 1 FROM {table_name} LIMIT 1")
            table_exists = True
            logger.info(f"Table {table_name} already exists")
        except Exception:
            table_exists = False
            logger.info(f"Table {table_name} does not exist, will create it")

        # Create table with schema if it doesn't exist
        if not table_exists:
            try:
                spark.createDataFrame([], df_with_partitions.schema).writeTo(table_name).create()
                logger.info(f"Created table schema: {table_name}")
            except Exception as e:
                logger.info(f"Table {table_name} might already exist: {str(e)}")

        # Write data with partitioning
        df_with_partitions.write.format("iceberg").mode("append").saveAsTable(table_name)

        logger.info(f"✅ Successfully wrote fact data for date {date}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to write fact data for date {date}: {str(e)}")
        return False


def process_date_range(spark: SparkSession, config: FactConfig) -> Dict[str, bool]:
    """
    Process a range of dates and return results

    Args:
        spark: SparkSession instance
        config: Configuration object

    Returns:
        Dictionary mapping dates to success status
    """
    dates = calculate_processing_dates(config)
    results = {}

    logger.info(f"Processing {len(dates)} dates: {dates}")

    for date in dates:
        logger.info(f"Processing date: {date}")

        # Read bronze data
        bronze_df = read_bronze_data(spark, config, date)

        if bronze_df is None:
            logger.warning(f"No data available for date {date}, skipping")
            results[date] = False
            continue

        # Transform data
        fact_df = transform_fact_data(bronze_df)

        # Validate data
        row_count = fact_df.count()
        if row_count == 0:
            logger.warning(f"No valid records after transformation for date {date}")
            results[date] = False
            continue

        # Write to fact table
        success = write_fact_table(spark, fact_df, date, config)
        results[date] = success

        if success:
            logger.info(f"✅ Successfully processed date {date} with {row_count} records")
        else:
            logger.error(f"❌ Failed to process date {date}")

    return results


def main():
    """Main function to orchestrate the fact loading process"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Load fact tables from bronze layer")
        parser.add_argument("--start-date", help="Start date (YYYY-MM-DD), defaults to yesterday")
        parser.add_argument("--end-date", help="End date (YYYY-MM-DD), defaults to start-date")
        parser.add_argument("--data-year-offset", type=int, default=1,
                            help="Year offset for data source (default: 1)")

        args = parser.parse_args()

        # Create configuration
        config = FactConfig.from_env()
        if args.start_date:
            config.start_date = args.start_date
        if args.end_date:
            config.end_date = args.end_date
        if args.data_year_offset:
            config.data_year_offset = args.data_year_offset

        logger.info(f"Configuration: {config}")

        # Create Spark session
        spark = get_spark_session()

        # Create database
        create_nessie_database(spark, config.database_name)

        # Process date range
        results = process_date_range(spark, config)

        # Log summary
        successful_dates = [date for date, success in results.items() if success]
        failed_dates = [date for date, success in results.items() if not success]

        logger.info("=" * 80)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total dates processed: {len(results)}")
        logger.info(f"Successful dates: {len(successful_dates)}")
        logger.info(f"Failed dates: {len(failed_dates)}")

        if successful_dates:
            logger.info(f"✅ Successfully processed: {successful_dates}")
        if failed_dates:
            logger.warning(f"⚠️ Failed to process: {failed_dates}")

        # Stop Spark session
        spark.stop()

        # More resilient error handling: only exit with error if ALL dates failed
        if failed_dates and not successful_dates:
            logger.error("❌ All dates failed to process - exiting with error")
            sys.exit(1)
        elif failed_dates:
            logger.warning(
                f"⚠️ Some dates failed to process ({len(failed_dates)}/{len(results)}), but {len(successful_dates)} dates succeeded")
            logger.info("✅ Continuing with successful processing - not exiting with error")
            sys.exit(0)  # Exit successfully even with partial failures
        else:
            logger.info("✅ All dates processed successfully")
            sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Application failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 