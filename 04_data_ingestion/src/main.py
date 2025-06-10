from highway_ingester.github_downloader import download_github_dir, upload_to_s3, get_boto3_client
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

print(f"REPO_OWNER {os.getenv('REPO_OWNER')}  --   AWS_SECRET_ACCESS_KEY {os.getenv('AWS_SECRET_ACCESS_KEY')}")

local_downloaded_path = Path(os.getenv('LOCAL_DOWNLOADED_PATH'))  # or wherever your files are
bucket = os.getenv('BUCKET')
s3_path = os.getenv('S3_PATH')


download_github_dir(
    repo_owner=os.getenv('REPO_OWNER'),
    repo_name=os.getenv('REPO_NAME'),
    dir_path=os.getenv('DIR_PATH'),
    branch="master",
    local_dir=Path('data'),
    token=os.getenv('GITHUB_TOKEN')
)

s3_client = get_boto3_client(service_name="s3", aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('REGION_NAME'),
                             endpoint_url=os.getenv('S3_ENDPOINT'))

upload_to_s3(local_dir=Path('data'), bucket_name='bronze', s3_prefix='yellow_tripdata_partitioned_by_day',
s3_client=s3_client)