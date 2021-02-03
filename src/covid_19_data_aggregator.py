import sys
from datetime import datetime, timedelta
from types import SimpleNamespace
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import *
import boto3
import logging

# Setup Logging
def setup_logger(log_level):
    log_msg_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    log_datetime_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_msg_format, datefmt=log_datetime_format)
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    return logger
    
# Function to compute the current quarter
def get_quarter(run_date):
    return (run_date.month - 1) // 3 + 1

# Function to compute the first date of the quarter
def get_first_day_of_the_quarter(run_date):
    quarter = get_quarter(run_date)
    return datetime(run_date.year, 3 * quarter - 2, 1)

# Function to compute start and end date for Daily, Monthly and Quarterly runs
def get_start_end_dates(run_date, period):
    # Process Date
    one_day_before_run_date = run_date - timedelta(days=1)

    # Monthly
    monthly_period_start_date = one_day_before_run_date.replace(day=1)
    monthly_period_end_date = run_date

    # Quarterly
    quarterly_period_start_date = get_first_day_of_the_quarter(one_day_before_run_date)
    quarterly_period_end_date = run_date

    # Get Start End Dates
    if period == 'MONTHLY':
        start_date = monthly_period_start_date
        end_date = monthly_period_end_date
    elif period == 'QUARTERLY':
        start_date = quarterly_period_start_date
        end_date = quarterly_period_end_date
    else:
        raise ValueError("Unknown value in parameter --PERIOD.")

    cfg = SimpleNamespace(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    return cfg

# Create Data frame
def create_df(spark, s3_path):
    # Read the csv formatted S3 files
    df = spark.read.format("csv").option("inferSchema", "true").option("header", "true").load(s3_path)

    return df
    

# Read parameters
args = getResolvedOptions(sys.argv, ['LOG_LEVEL', 'PERIOD', 'S3_WORLD_CASES_DEATHS_TESTING_PATH', 'S3_COUNTRYCODE_PATH','S3_OUTPUT_BASE_PATH'])

# Parse Paramaters
log_level = args['LOG_LEVEL']
period =  args['PERIOD']
s3_world_cases_deaths_testing_path = args['S3_WORLD_CASES_DEATHS_TESTING_PATH']
s3_countrycode_path = args['S3_COUNTRYCODE_PATH']
s3_output_base_path = args['S3_OUTPUT_BASE_PATH']

# Set Logging
logger = setup_logger(log_level)
logger = logging.getLogger(__name__)

# Log Parameters
logger.info(f"log_level : {log_level}")
logger.info(f"period : {period}")
logger.info(f"s3_world_cases_deaths_testing_path : {s3_world_cases_deaths_testing_path}")
logger.info(f"s3_countrycode_path : {s3_countrycode_path}")
logger.info(f"s3_output_base_path : {s3_output_base_path}")

# Create a Global Glue context
glueContext = GlueContext(SparkContext.getOrCreate())

# Spark Session
spark = glueContext.spark_session
spark.conf.set("spark.sql.parquet.enableVectorizedReader", "false")
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

# Get current datetime
run_date = datetime.today()
# Get period start and end date.
cfg = get_start_end_dates(run_date, period)

# Create df_world
df_world = create_df(spark, s3_world_cases_deaths_testing_path)

# Create df_countrycode
df_countrycode = create_df(spark, s3_countrycode_path)

# Create Views to use Spark SQL 
df_world.createOrReplaceTempView("view_world")
df_countrycode.createOrReplaceTempView("view_countrycode")

# Aggregate 
query_aggregate = ("SELECT "
                   "c.`country`, "
                   "t.`iso_code`, "
                   f"'{cfg.start_date}' AS start_date, "
                   f"'{cfg.end_date}' AS end_date, "
                   "SUM(t.`new_cases`) AS new_cases, "
                   "SUM(t.`new_deaths`) AS new_deaths "
                   "FROM view_world t, view_countrycode c "
                   f"WHERE t.`date` >= '{cfg.start_date}' AND t.`date` < '{cfg.end_date}' "
                   "AND t.`iso_code` = c.`alpha-3 code` "
                   "GROUP BY 1, 2, 3, 4 "
                   "HAVING LENGTH(TRIM(t.`iso_code`)) > 1 "
                   "ORDER BY 1, 2, 3, 4 "
                   )
logger.info(f"query_aggregate : {query_aggregate}")

# Execute the SQL to create df
df_aggregate = spark.sql(query_aggregate)

# Write 
df_aggregate.coalesce(1).write.mode("overwrite").parquet(s3_output_base_path + "/world-cases-deaths-aggregates/" + "/aggregate=" + period)
