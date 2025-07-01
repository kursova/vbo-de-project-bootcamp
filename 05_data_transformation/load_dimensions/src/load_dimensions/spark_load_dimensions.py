import os
import pandas as pd
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import *
import logging

TAXI_ZONES_PATH="s3a://bronze/taxi_zone_lookup.csv"

# Ensure the log directory exists
# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

def get_spark_session(app_name: str = "Load Dimensions") -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


def create_nessie_database(spark: SparkSession, name: str = "silver"):
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS nessie.{name}")


# Write dimlocation
def write_dimlocation(spark: SparkSession, path: str = TAXI_ZONES_PATH, table_name: str = "dimlocation"):
    # Read txi zones
    taxi_zones_df = spark.read.csv(path, header=True, inferSchema=True)

    spark.sql(f"DROP TABLE IF EXISTS nessie.silver.{table_name}")

    spark.createDataFrame([], taxi_zones_df.schema).writeTo(f"nessie.silver.{table_name}").create()

    logger.info(f"taxi_zones_df count: {taxi_zones_df.count()}")

    taxi_zones_df.write.format("iceberg").mode("overwrite") \
        .save(f"nessie.silver.{table_name}")


def write_dimpayment(spark: SparkSession, table_name: str = "dimpayment"):
    dimpayment_df = spark.createDataFrame([
        (1, "Credit card"),
        (2, "Cash"),
        (3, "No charge"),
        (4, "Dispute"),
        (5, "Unknown"),
        (0, "Voided trip")
    ],
        ['paymenttypeid', 'paymenttype']
    )

    spark.sql(f"DROP TABLE IF EXISTS nessie.silver.{table_name}")

    spark.createDataFrame([], dimpayment_df.schema).writeTo(f"nessie.silver.{table_name}").create()

    logger.info(f"dimpayment_df count: {dimpayment_df.count()}")

    dimpayment_df.write.format("iceberg").mode("overwrite") \
        .save(f"nessie.silver.{table_name}")


def write_dimratecode(spark: SparkSession, table_name: str = "dimratecode"):
    dimratecode_df = spark.createDataFrame([
        (1.0, "Standard rate"),
        (2.0, "JFK"),
        (3.0, "Newark"),
        (4.0, "Nassau or Westchester"),
        (5.0, "Negotiated fare"),
        (6.0, "Group ride"),
        (7.0, "Not recorded"),
        (99.0, "Unknown or other")
    ],
        ['ratecodeid', 'ratedescription']
    )
    spark.sql(f"DROP TABLE IF EXISTS nessie.silver.{table_name}")

    spark.createDataFrame([], dimratecode_df.schema).writeTo(f"nessie.silver.{table_name}").create()
    logger.info(f"dimratecode_df count: {dimratecode_df.count()}")
    dimratecode_df.write.format("iceberg").mode("overwrite") \
        .save(f"nessie.silver.{table_name}")


def write_dimtime(spark: SparkSession, table_name: str = "dimtime", start_date: str = "2022-01-01",
                  end_date: str = "2024-12-31"):
    try:
        # Convert string dates to timestamp
        start_ts = F.to_timestamp(F.lit(start_date))
        end_ts = F.to_timestamp(F.lit(end_date))

        # Generate minute-level timestamps using Spark
        dimtime_df = spark.sql(f"""
            SELECT explode(sequence(
                to_timestamp('{start_date}'), 
                to_timestamp('{end_date}'), 
                interval 1 minute
            )) as minutes
        """)

    except Exception as e:
        logger.exception(f"Error generating DataFrame: {str(e)}")

    dimtime_df2 = (dimtime_df.withColumn("timeid", F.date_format("minutes", "yyyyMMddHHmm").cast("long"))
                    .withColumn("Date", F.to_date("minutes"))
                   .withColumn("dayofmonth", F.dayofmonth("minutes"))
                   .withColumn("weekofyear", ((F.dayofyear("minutes") - 1) / 7 + 1).cast("int"))
                   .withColumn("month", F.month("minutes").cast("smallint"))
                   .withColumn("year", F.year("minutes").cast("smallint"))
                   .withColumn("minute", F.minute("minutes").cast("smallint"))
                   .withColumn("second", F.second("minutes").cast("smallint"))
                   ).drop("minutes", "unix_time_minutes")

    spark.sql(f"DROP TABLE IF EXISTS nessie.silver.{table_name}")

    spark.createDataFrame([], dimtime_df2.schema).writeTo(f"nessie.silver.{table_name}").create()

    logger.info(f"dimtime_df2 count: {dimtime_df2.count()}")

    dimtime_df2.write.format("iceberg").mode("overwrite") \
        .save(f"nessie.silver.{table_name}")

if __name__ == '__main__':
    spark = get_spark_session("Load Dimensions")

    create_nessie_database(spark, name="silver")

    write_dimlocation(spark, path=TAXI_ZONES_PATH, table_name='dimlocation')

    write_dimpayment(spark, table_name="dimpayment")

    write_dimratecode(spark, table_name="dimratecode")

    write_dimtime(spark, "dimtime", "2022-01-01", "2025-12-31")