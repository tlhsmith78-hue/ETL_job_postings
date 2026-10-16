from dotenv import load_dotenv
import os
import datetime
import boto3
from botocore.config import Config
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, get

class Cleaner:
    def __init__(self):

        print("----- INITIALISING CLEANER -----")
        
        load_dotenv()
        self.bucket = os.environ["BUCKET"]
        today = datetime.date.today()
        self.filename = f"{today}_jobs.json"
        self.key = f"{today.year}/{today.month:02d}/{today.day:02d}/{self.filename}"
        self.path = f"""{os.environ["RAW_PATH"]}\{self.filename}"""

        self.s3 = boto3.client(
            "s3",
            aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"],
            config=Config(request_checksum_calculation="when_required")
        )

        self.spark = SparkSession.builder.appName("Cleaner").getOrCreate()

    def load(self):

        print("----- LOADING FILE FROM S3 -----")
        
        self.s3.download_file(
            Bucket = self.bucket,
            Key = f"raw/{self.key}",
            Filename = self.path
        )

        self.raw_data = self.spark.read.json(self.path)

    def flatten(self):

        print("----- HARMONISING COLUMNS -----")

        self.df_flat = self.raw_data.select(
            "adref",
            col("category.label").alias("category_label"),
            col("category.tag").alias("category_tag"),
            col("company.display_name").alias("company_display_name"),
            "contract_time",
            "contract_type",
            "created",
            "description",
            "id",
            get(col("location.area"), 0).alias("location_country"),
            get(col("location.area"), 1) .alias("location_region"),
            get(col("location.area"), 2) .alias("location_city"),
            get(col("location.area"), 3) .alias("location_district"),
            col("location.display_name").alias("location_display_name"),
            "redirect_url",
            "salary_is_predicted",
            "salary_max",
            "salary_min",
            "title"
        )

    def standardise(self):

        print("----- STANDARDISING DATA -----")

        self.df_flat.createOrReplaceTempView("df_flat")
        self.df_stand = self.spark.sql("""
            SELECT adref,
            category_label,
            category_tag,
            company_display_name,
            contract_time,
            contract_type,
            CAST(created AS DATE) AS created,
            description,
            CAST(id AS BIGINT) AS id,
            location_country,
            location_region,
            location_city,
            location_district,
            location_display_name,
            redirect_url,
            CAST(salary_is_predicted AS BOOLEAN) AS salary_is_predicted,
            CAST(salary_max AS FLOAT) AS salary_max,
            CAST(salary_min AS FLOAT) AS salary_min,
            title
            FROM df_flat;
        """)

    def clean(self):

        print("----- CLEANING ROW VALUES -----")

        self.df_stand.createOrReplaceTempView("df_stand")
        self.df_clean = self.spark.sql("""
            SELECT adref,
            REPLACE(LOWER(TRIM(category_label)), "emplois", "") AS category_label,
            REPLACE(LOWER(TRIM(category_tag)), "-jobs", "") AS category_tag,
            TRIM(LOWER(company_display_name)) AS company_display_name,
            LOWER(TRIM(contract_time)) AS contract_time,
            LOWER(TRIM(contract_type)) AS contract_type,
            created,
            LOWER(TRIM(description)) AS description,
            id,
            LOWER(TRIM(location_country)) AS location_country,
            LOWER(TRIM(location_region)) AS location_region,
            LOWER(TRIM(location_city)) AS location_city,
            LOWER(TRIM(location_display_name)) AS location_display_name,
            TRIM(redirect_url) AS redirect_url,
            salary_is_predicted,
            salary_max,
            salary_min,
            LOWER(TRIM(title)) AS title
            FROM df_stand;
            """)

    def selection(self):

        print("----- FILTERING ROWS -----")

        self.df_clean = self.df_clean.dropDuplicates(["id"])

        self.df_clean.createOrReplaceTempView("df_clean")

        self.df_select = self.spark.sql("""
            SELECT * FROM df_clean
            WHERE company_display_name IS NOT NULL
            AND contract_time IS NOT NULL
            AND contract_type IS NOT NULL
            AND created IS NOT NULL
            AND location_region IS NOT NULL
            AND location_city IS NOT NULL
            AND location_display_name IS NOT NULL
            AND redirect_url IS NOT NULL
            AND salary_min IS NOT NULL
            AND title IS NOT NULL;
            """)


    def trace(self):

        print("----- ADDING COLUMNS FOR TRACEABILITY -----")

        self.df_select.createOrReplaceTempView("df_select")
        self.df_trace = self.spark.sql("""
            SELECT *,
            {source} AS source,
            current_timestamp() AS trans_run
            FROM df_select
            """, source = self.filename)

    def upload(self):

        print("----- UPLOADING CLEANED DATA -----")

        self.path = f"""{os.environ["CLEANED_PATH"]}\{self.filename.replace(".json", "")}"""
        self.df_trace.write.mode("overwrite").format("csv").save(self.path)

        for loc_file in os.listdir(self.path):
            self.s3.upload_file(
                Filename = f"{self.path}\{loc_file}",
                Bucket = os.environ["BUCKET"],
                Key = f"clean/{self.key.replace(self.filename, loc_file)}"
                )

        print("----- CLEANED DATA UPLOADED -----")


    def stop(self):

        self.spark.stop()

        print("----- PROCESS ENDED -----")


def main():

    try:
        cleaner = Cleaner()
        cleaner.load()
        cleaner.flatten()
        cleaner.standardise()
        cleaner.clean()
        cleaner.selection()
        cleaner.trace()
        cleaner.upload()

        cleaner.stop()
    except Exception as e:
        print(e)
        cleaner.stop()
    



if __name__ == "__main__":
    main()