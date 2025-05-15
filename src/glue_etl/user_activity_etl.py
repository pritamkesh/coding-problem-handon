"""
AWS Glue ETL Job for User Activity Data
Transforms raw Avro data into processed Parquet format
"""

import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import (
    col, from_unixtime, current_timestamp, to_date,
    when, get_json_object
)

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Configuration
INPUT_DATABASE = "user_activity_db"
INPUT_TABLE = "raw_events"
OUTPUT_BUCKET = "your-unique-bucket-name"
OUTPUT_PREFIX = "processed_events/user_activity"

try:
    # Read raw data from catalog
    dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
        database=INPUT_DATABASE,
        table_name=INPUT_TABLE,
        transformation_ctx="raw_data"
    )

    # Convert to Spark DataFrame for easier transformations
    df = dynamic_frame.toDF()

    # Apply transformations
    transformed_df = df.select(
        col("user_id"),
        # Convert timestamp from Unix millis to ISO 8601
        from_unixtime(col("event_timestamp") / 1000).alias("event_timestamp"),
        col("event_type"),
        col("product_id"),
        # Add processing timestamp
        current_timestamp().alias("processing_timestamp"),
        # Extract price from event_properties if event_type is purchase
        when(
            col("event_type") == "purchase",
            col("event_properties.price").cast("float")
        ).otherwise(None).alias("price")
    )

    # Add processing_date partition column
    transformed_df = transformed_df.withColumn(
        "processing_date",
        to_date(col("processing_timestamp"))
    )

    # Convert back to DynamicFrame
    output_dyf = DynamicFrame.fromDF(
        transformed_df,
        glueContext,
        "output_dyf"
    )

    # Write to S3 in Parquet format with partitioning
    glueContext.write_dynamic_frame.from_options(
        frame=output_dyf,
        connection_type="s3",
        connection_options={
            "path": f"s3://{OUTPUT_BUCKET}/{OUTPUT_PREFIX}",
            "partitionKeys": ["event_type", "processing_date"]
        },
        format="parquet",
        transformation_ctx="output_data"
    )

    # Log success
    print("ETL job completed successfully")

except Exception as e:
    # Log error and raise
    print(f"ETL job failed: {str(e)}")
    raise

finally:
    # Commit the job
    job.commit() 