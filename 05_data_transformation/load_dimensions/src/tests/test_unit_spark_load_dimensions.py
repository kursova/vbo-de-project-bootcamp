import pytest
import tempfile
from unittest.mock import Mock, patch
from pyspark.sql import SparkSession
import logging

# Import the module under test
from src.load_dimensions.spark_load_dimensions import (get_spark_session, create_nessie_database, write_dimpayment,
                                                       write_dimtime, write_dimlocation, write_dimratecode)

# Create a logger for testing
logger = logging.getLogger(__name__)


class TestSparkFixture:
    """Base test class providing Spark session fixture"""

    @pytest.fixture(scope="class")
    def spark(self):
        """Create a test Spark session"""
        spark = SparkSession.builder \
            .appName("TestLoadDimensions") \
            .master("local[2]") \
            .config("spark.sql.warehouse.dir", tempfile.mkdtemp()) \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .getOrCreate()

        spark.sparkContext.setLogLevel("WARN")
        yield spark
        spark.stop()


# ===== UNIT TESTS =====

class TestUnitTests(TestSparkFixture):
    """Unit tests for individual functions"""

    def test_get_spark_session(self):
        """Test Spark session creation"""
        with patch('src.load_dimensions.spark_load_dimensions.SparkSession.builder') as mock_builder:
            mock_session = Mock()
            mock_builder.appName.return_value.getOrCreate.return_value = mock_session

            result = get_spark_session("TestApp")

            mock_builder.appName.assert_called_once_with("TestApp")
            assert result == mock_session

    def test_get_spark_session_default_name(self):
        """Test Spark session creation with default app name"""
        with patch('src.load_dimensions.spark_load_dimensions.SparkSession.builder') as mock_builder:
            mock_session = Mock()
            mock_builder.appName.return_value.getOrCreate.return_value = mock_session

            result = get_spark_session()

            mock_builder.appName.assert_called_once_with("Load Dimensions")

    def test_create_nessie_database(self, spark):
        """Test database creation"""
        with patch.object(spark, 'sql') as mock_sql:
            create_nessie_database(spark, "test_db")
            mock_sql.assert_called_once_with("CREATE NAMESPACE IF NOT EXISTS nessie.test_db")

    def test_create_nessie_database_default_name(self, spark):
        """Test database creation with default name"""
        with patch.object(spark, 'sql') as mock_sql:
            create_nessie_database(spark)
            mock_sql.assert_called_once_with("CREATE NAMESPACE IF NOT EXISTS nessie.silver")


class TestDimPaymentUnit(TestSparkFixture):
    """Unit tests for dimpayment function"""

    def test_write_dimpayment_data_structure(self, spark):
        """Test that dimpayment creates correct data structure"""
        with patch.object(spark, 'sql'), \
                patch.object(spark, 'createDataFrame') as mock_create_df, \
                patch('src.load_dimensions.spark_load_dimensions.logger', logger):
            # Mock the dataframe creation
            mock_df = Mock()
            mock_df.schema = "test_schema"
            mock_df.count.return_value = 6
            mock_df.write.format.return_value.mode.return_value.save.return_value = None
            mock_create_df.return_value = mock_df

            # Mock the writeTo chain
            mock_write_to = Mock()
            mock_write_to.create.return_value = None
            mock_create_df.return_value.writeTo.return_value = mock_write_to

            write_dimpayment(spark, "test_dimpayment")

            # Verify the data structure passed to createDataFrame
            call_args = mock_create_df.call_args_list[0][0]  # First call args
            expected_data = [
                (1, "Credit card"),
                (2, "Cash"),
                (3, "No charge"),
                (4, "Dispute"),
                (5, "Unknown"),
                (0, "Voided trip")
            ]
            expected_schema = ['paymenttypeid', 'paymenttype']

            assert call_args[0] == expected_data
            assert call_args[1] == expected_schema


class TestDimRateCodeUnit(TestSparkFixture):
    """Unit tests for dimratecode function"""

    def test_write_dimratecode_data_structure(self, spark):
        """Test that dimratecode creates correct data structure"""
        with patch.object(spark, 'sql'), \
                patch.object(spark, 'createDataFrame') as mock_create_df, \
                patch('src.load_dimensions.spark_load_dimensions.logger', logger):
            mock_df = Mock()
            mock_df.schema = "test_schema"
            mock_df.count.return_value = 8
            mock_df.write.format.return_value.mode.return_value.save.return_value = None
            mock_create_df.return_value = mock_df

            mock_write_to = Mock()
            mock_write_to.create.return_value = None
            mock_create_df.return_value.writeTo.return_value = mock_write_to

            write_dimratecode(spark, "test_dimratecode")

            call_args = mock_create_df.call_args_list[0][0]
            expected_data = [
                (1.0, "Standard rate"),
                (2.0, "JFK"),
                (3.0, "Newark"),
                (4.0, "Nassau or Westchester"),
                (5.0, "Negotiated fare"),
                (6.0, "Group ride"),
                (7.0, "Not recorded"),
                (99.0, "Unknown or other")
            ]
            expected_schema = ['ratecodeid', 'ratedescription']

            assert call_args[0] == expected_data
            assert call_args[1] == expected_schema


class TestDimLocationUnit(TestSparkFixture):
    """Unit tests for dimlocation function"""

    @pytest.mark.skip(
        reason="Spark DataFrame write chain mocking issue - requires Iceberg dependencies for full testing")
    def test_write_dimlocation_csv_reading(self, spark):
        """Test that dimlocation reads CSV correctly"""
        # Use comprehensive mocking to prevent any real Spark operations
        with patch('src.load_dimensions.spark_load_dimensions.logger') as mock_logger, \
                patch.object(spark, 'sql') as mock_sql, \
                patch.object(spark.read, 'csv') as mock_csv, \
                patch.object(spark, 'createDataFrame') as mock_create_df:
            # Create a mock DataFrame that completely avoids real Spark operations
            mock_df = Mock()
            mock_df.schema = Mock()
            mock_df.count.return_value = 100

            # Create a mock write object that handles the entire chain
            mock_write = Mock()
            # Make the write chain return the same mock to handle chaining
            mock_write.format = Mock(return_value=mock_write)
            mock_write.mode = Mock(return_value=mock_write)
            mock_write.save = Mock(return_value=None)

            # Assign the mock write to the DataFrame
            mock_df.write = mock_write

            # Mock writeTo chain
            mock_write_to = Mock()
            mock_write_to.create = Mock(return_value=None)
            mock_df.writeTo = mock_write_to

            # Make sure CSV returns our completely mocked DataFrame
            mock_csv.return_value = mock_df

            # Mock empty DataFrame creation
            mock_empty_df = Mock()
            mock_empty_df.writeTo = mock_write_to
            mock_create_df.return_value = mock_empty_df

            # Call the function
            test_path = "/tmp/taxi_zones.csv"
            write_dimlocation(spark, test_path, "test_dimlocation")

            # Verify the operations were called correctly
            mock_csv.assert_called_once_with(test_path, header=True, inferSchema=True)
            mock_sql.assert_called_with("DROP TABLE IF EXISTS nessie.silver.test_dimlocation")
            mock_create_df.assert_called_once()

            # Verify write chain was called
            mock_write.format.assert_called_with("iceberg")
            mock_write.mode.assert_called_with("overwrite")
            mock_write.save.assert_called_with("nessie.silver.test_dimlocation")


class TestDimTimeUnit(TestSparkFixture):
    """Unit tests for dimtime function"""

    @patch('src.load_dimensions.spark_load_dimensions.logger')
    def test_write_dimtime_sql_generation(self, mock_logger, spark):
        """Test that dimtime generates correct SQL"""
        with patch.object(spark, 'sql') as mock_sql, \
                patch.object(spark, 'createDataFrame') as mock_create_df:

            # Mock the SQL result for sequence generation
            mock_df = Mock()
            mock_df.withColumn.return_value = mock_df
            mock_df.drop.return_value = mock_df
            mock_df.schema = "test_schema"
            mock_df.count.return_value = 1000

            # Mock the write chain completely
            mock_write = Mock()
            mock_write.format.return_value = mock_write
            mock_write.mode.return_value = mock_write
            mock_write.save.return_value = None
            mock_df.write = mock_write

            # Mock the writeTo chain
            mock_write_to = Mock()
            mock_write_to.create.return_value = None
            mock_df.writeTo = mock_write_to

            # Mock empty dataframe creation
            mock_empty_df = Mock()
            mock_empty_df.writeTo = mock_write_to
            mock_create_df.return_value = mock_empty_df

            # Set up SQL mock to return our mock DataFrame for the sequence query
            def sql_side_effect(query):
                if "sequence" in query:
                    return mock_df
                return None

            mock_sql.side_effect = sql_side_effect

            write_dimtime(spark, "test_dimtime", "2022-01-01", "2022-01-02")

            # Verify SQL was called with sequence generation
            sql_calls = mock_sql.call_args_list
            sequence_call = None
            for call in sql_calls:
                if "sequence" in str(call):
                    sequence_call = call
                    break

            assert sequence_call is not None
            assert "2022-01-01" in str(sequence_call)
            assert "2022-01-02" in str(sequence_call)

            # Verify DataFrame operations were called
            assert mock_df.withColumn.call_count >= 8  # Multiple withColumn calls
            mock_df.drop.assert_called_once()

            # Verify write operations were called
            mock_write.format.assert_called_with("iceberg")
            mock_write.mode.assert_called_with("overwrite")
            mock_write.save.assert_called_with("nessie.silver.test_dimtime")