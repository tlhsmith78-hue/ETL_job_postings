import boto3
import requests
import json
import datetime
import time
import math
from dotenv import load_dotenv 
import os

def main():

    load_dotenv()

    s3 = boto3.client("s3",
                    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    adzuna = {
        "id": os.environ["ID"],
        "key": os.environ["KEY"]
    }

    search = {
        "country": "fr",
        "job_key": "commercial",
        "job_excluded": "java",
        "localisation": "paris",
        "minimum_salary": 40000,
        "full_time": 1,
        "permanent": 1,
        "results_per_page": 50
    }

    url = f"http://api.adzuna.com:80/v1/api/jobs/{search["country"]}/search/1?app_id={adzuna['id']}&app_key={adzuna['key']}&results_per_page=1&what={search["job_key"]}&what_exclude={search["job_excluded"]}&where={search["localisation"]}&salary_min={search["minimum_salary"]}&full_time={search["full_time"]}&permanent={search["permanent"]}&content-type=application/json"

    response = requests.get(url)

    if status_check(response.status_code) == 429:
        response = requests.get(url)
        if response.status_code == 429:
            raise Exception("Too many attempts, try again later.")

    job_count = response.json()["count"]
    num_pages = math.ceil(job_count / 50)

    total_jobs = []

    for page in range(1, num_pages + 1):
        url = f"http://api.adzuna.com:80/v1/api/jobs/{search["country"]}/search/{page}?app_id={adzuna['id']}&app_key={adzuna['key']}&results_per_page={search["results_per_page"]}&what={search["job_key"]}&what_exclude={search["job_excluded"]}&where={search["localisation"]}&salary_min={search["minimum_salary"]}&full_time={search["full_time"]}&permanent={search["permanent"]}&content-type=application/json"
        response = requests.get(url)
        if status_check(response.status_code) == 429:
            response = requests.get(url)
            if response.status_code == 429:
                raise Exception("Too many attempts, try again later.")
        total_jobs.extend(response.json()["results"])

    data = json.dumps(total_jobs, ensure_ascii=False).encode("utf-8")

    upload(data, s3)


def status_check(status, ):
    if status == 401:
        raise Exception("Invalid authentification. Check your id or key.")

    elif status == 404:
        raise Exception("Page could not be found. Check that the URL leads to Adzuna.")

    elif status == 429:
        print("Too many requests, waiting to refresh.")
        time.sleep(10)
        return 429

    return True

def upload(data, s3):
    day = datetime.date.today()
    now = datetime.datetime.now()
    s3.put_object(
        Bucket = os.environ["BUCKET"],
        Key= f"raw/{now.year}/{now.month:02d}/{now.day:02d}/{day}_jobs.json",
        Body=data
    )


if __name__ == "__main__":
    main()