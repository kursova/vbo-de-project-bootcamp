import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from src.load_facts.spark_load_facts import write_fact_trip

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local[1]") \
        .appName("TestSession") \
        .getOrCreate()


def test_write_fact_trip_structure(spark, monkeypatch):
    # Create a test DataFrame
    test_data = [{
        "tpep_pickup_datetime": "2024-01-01 08:00:00",
        "tpep_dropoff_datetime": "2024-01-01 08:30:00",
        "passenger_count": 1,
        "trip_distance": 2.5,
        "RatecodeID": 1,
        "store_and_fwd_flag": "N",
        "PULocationID": 100,
        "DOLocationID": 200,
        "payment_type": 2,
        "fare_amount": 10.0,
        "extra": 0.5,
        "mta_tax": 0.5,
        "tip_amount": 2.0,
        "tolls_amount": 0.0,
        "improvement_surcharge": 0.3,
        "total_amount": 13.3,
        "congestion_surcharge": 2.5,
        "Airport_fee": 1.25
    }]

    df = spark.createDataFrame(test_data)

    # Patch spark.read.parquet
    from pyspark.sql.readwriter import DataFrameReader
    monkeypatch.setattr(DataFrameReader, "parquet", lambda self, path: df)

    # Patch spark.sql
    monkeypatch.setattr(spark, "sql", lambda query: None)

    # Patch DataFrame write methods
    monkeypatch.setattr(df.write, "format", lambda fmt: df.write)
    monkeypatch.setattr(df.write, "mode", lambda m: df.write)
    monkeypatch.setattr(df.write, "save", lambda path: None)

    # Run the function (should no longer fail)
    write_fact_trip(spark, path="fake_path", table_name="test_fact_trip")

    # Check key columns exist
    result = df.withColumn("PickupDateTimeID", F.date_format("tpep_pickup_datetime", "yyyyMMddHHmm").cast("long")) \
        .withColumn("DropOffDateTimeID", F.date_format("tpep_dropoff_datetime", "yyyyMMddHHmm").cast("long"))

    assert "PickupDateTimeID" in result.columns
    assert "DropOffDateTimeID" in result.columns