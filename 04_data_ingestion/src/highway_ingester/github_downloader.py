# import libs
import boto3
import logging
from dotenv import load_dotenv
import os
import requests
from pathlib import Path

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT')
REPO_OWNER = os.getenv('REPO_OWNER')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        #logging.FileHandler("logs/download_github_dir.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# get s3 client
def get_boto3_client(service_name="s3", aws_access_key_id=None, aws_secret_access_key=None, region_name=None,
                     endpoint_url=None):
    return boto3.client(
        service_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        endpoint_url=endpoint_url

    )

# Download files from github to local
def download_github_dir(repo_owner, repo_name, dir_path, branch="master", local_dir="data", token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{dir_path}?ref={branch}"
    logger.info(f"Fetching directory: {api_url}")

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    items = response.json()
    os.makedirs(local_dir, exist_ok=True)

    for item in items:
        name = item["name"]
        path = os.path.join(local_dir, name)

        if item["type"] == "file":
            file_content = requests.get(item["download_url"])
            file_content.raise_for_status()
            logger.info(f"Writing {name}")
            with open(path, "wb") as f:
                f.write(file_content.content)
        elif item["type"] == "dir":
            download_github_dir(
                repo_owner, repo_name, item["path"],
                branch=branch,
                local_dir=path,
                token=token
            )

# Upload local files to S3
def upload_to_s3(local_dir: Path, bucket_name: str, s3_prefix: str, s3_client=None):
    if s3_client is None:
        logger.info("Creating new boto3 S3 client...")
        s3_client = boto3.client("s3")

    if not local_dir.exists():
        logger.error(f"Local directory does not exist: {local_dir}")
        return

    files_found = False

    logger.info(f"Uploading files from: {local_dir}")
    for root, _, files in os.walk(local_dir):
        for file in files:
            files_found = True
            local_file_path=Path(root) / file
            rel_path = local_file_path.relative_to(local_dir)
            s3_key   = f"{s3_prefix}/{rel_path.as_posix()}"

            logger.info(f"Uploading {local_file_path} to s3://{bucket_name}/{s3_key}")
            try:
                s3_client.upload_file(str(local_file_path), bucket_name, s3_key)
                logger.info(f"✅ Uploaded: {local_file_path}")
            except Exception as e:
                logger.exception(f"❌ Failed to upload {local_file_path}: {e}")

    if not files_found:
        logger.warning(f"No files found in {local_dir} to upload.") 



""" if __name__=='__main__':
    s3_client=get_boto3_client('s3', AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,REGION_NAME,S3_ENDPOINT_URL)
    download_github_dir(REPO_OWNER,'datasets','yellow_tripdata_partitioned_by_day/year=2023/month=10/day=1/', 'master', 'data', GITHUB_TOKEN) """