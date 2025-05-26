from pyspark.sql import SparkSession, functions as F
from pyspark import SparkContext, SparkConf
from pyspark.sql.types import *
import os, time

spark = SparkSession.builder \
.appName("Spark on K8s") \
.getOrCreate()


df = spark.range(1000000).withColumn("plus_10", F.col("id") + 10).withColumn("plus_20", F.col("id") + 20)

print("*******************************")

print(df.count())

df.printSchema()

df.show(500)

time.sleep(30)

print("Spark is shutting down.")

spark.stop()