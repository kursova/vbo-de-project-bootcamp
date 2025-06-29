import os
import requests
import logging
import boto3
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
import urllib3

load_dotenv()

# Ensure the log directory exists
os.makedirs("logs", exist_ok=True)

# Enhanced logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/download_github_dir.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_retry_session(max_retries: int = 3, backoff_factor: float = 1) -> requests.Session:
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_boto3_client(service_name="s3", aws_access_key_id=None, aws_secret_access_key=None,
                     region_name=None, endpoint_url=None) -> boto3.client:
    """Create a boto3 client with error handling and MinIO fallbacks."""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Try different configurations for MinIO compatibility
    configs_to_try = [
        # Configuration 1: Standard MinIO config
        {
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'region_name': region_name or 'us-east-1',
            'endpoint_url': endpoint_url,
            'use_ssl': False,
            'verify': False
        },
        # Configuration 2: MinIO with specific signature version
        {
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'region_name': 'us-east-1',  # Fixed region for MinIO
            'endpoint_url': endpoint_url,
            'use_ssl': False,
            'verify': False,
            'config': boto3.session.Config(signature_version='s3v4')
        },
        # Configuration 3: MinIO with path style
        {
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'region_name': 'us-east-1',
            'endpoint_url': endpoint_url,
            'use_ssl': False,
            'verify': False,
            'config': boto3.session.Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            )
        }
    ]

    for i, config in enumerate(configs_to_try, 1):
        try:
            logger.info(f"Trying MinIO configuration {i}/3...")
            client = boto3.client(service_name, **config)

            # Test the client with a simple operation
            client.list_buckets()
            logger.info(f"Successfully created {service_name} client for endpoint: {endpoint_url} (config {i})")
            return client

        except Exception as e:
            logger.warning(f"MinIO configuration {i} failed: {e}")
            continue

    # If all configurations fail, raise the last error
    raise Exception(f"Failed to create {service_name} client with any configuration for endpoint: {endpoint_url}")


def validate_github_token(token: str) -> bool:
    """Validate GitHub token by making a test API call."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            logger.info(f"GitHub token validated for user: {user_info.get('login', 'Unknown')}")
            return True
        else:
            logger.error(f"GitHub token validation failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error validating GitHub token: {e}")
        return False


def download_github_dir(repo_owner: str, repo_name: str, dir_path: str, branch: str = "main",
                        local_dir: str = "data", token: Optional[str] = None) -> Dict[str, int]:
    """
    Download a directory from GitHub repository with enhanced error handling.

    Returns:
        Dict with download statistics
    """
    stats = {
        "files_downloaded": 0,
        "directories_processed": 0,
        "errors": 0,
        "total_size_bytes": 0
    }

    # Validate token if provided
    if token and not validate_github_token(token):
        raise ValueError("Invalid GitHub token provided")

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    session = create_retry_session()

    def download_directory_contents(path: str, local_path: str) -> None:
        """Recursively download directory contents."""
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={branch}"
        logger.info(f"Fetching directory: {api_url}")

        try:
            response = session.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            items = response.json()

            # Handle single file case
            if not isinstance(items, list):
                items = [items]

            os.makedirs(local_path, exist_ok=True)
            stats["directories_processed"] += 1

            for item in items:
                name = item["name"]
                item_path = os.path.join(local_path, name)

                if item["type"] == "file":
                    try:
                        download_file_with_progress(item, item_path, session, headers)
                        stats["files_downloaded"] += 1
                        stats["total_size_bytes"] += item.get("size", 0)
                    except Exception as e:
                        logger.error(f"Failed to download file {name}: {e}")
                        stats["errors"] += 1

                elif item["type"] == "dir":
                    download_directory_contents(item["path"], item_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch directory {path}: {e}")
            stats["errors"] += 1
            raise

    def download_file_with_progress(item: Dict, local_file_path: str, session: requests.Session,
                                    headers: Dict) -> None:
        """Download a single file with progress tracking."""
        download_url = item["download_url"]
        file_size = item.get("size", 0)

        logger.info(f"Downloading {item['name']} ({file_size} bytes)")

        try:
            response = session.get(download_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()

            with open(local_file_path, "wb") as f:
                downloaded_bytes = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_bytes += len(chunk)

                        # Log progress for large files
                        if file_size > 1024 * 1024:  # 1MB
                            progress = (downloaded_bytes / file_size) * 100
                            if downloaded_bytes % (1024 * 1024) == 0:  # Log every MB
                                logger.info(f"Downloaded {downloaded_bytes}/{file_size} bytes ({progress:.1f}%)")

            # Verify file size
            actual_size = os.path.getsize(local_file_path)
            if file_size > 0 and actual_size != file_size:
                logger.warning(f"File size mismatch for {item['name']}: expected {file_size}, got {actual_size}")

            logger.info(f"✅ Successfully downloaded: {item['name']}")

        except Exception as e:
            logger.error(f"❌ Failed to download {item['name']}: {e}")
            # Clean up partial download
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
            raise

    try:
        download_directory_contents(dir_path, local_dir)
        logger.info(f"Download completed. Stats: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise


def test_s3_connection(s3_client) -> bool:
    """Test S3 connection by listing buckets."""
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
        logger.info(f"S3 connection successful. Available buckets: {buckets}")
        return True
    except Exception as e:
        logger.error(f"S3 connection test failed: {e}")
        return False


def ensure_bucket_exists(bucket_name: str, s3_client) -> bool:
    """Ensure the S3 bucket exists, create it if it doesn't."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} already exists")
        return True
    except Exception as e:
        if '404' in str(e) or 'NoSuchBucket' in str(e):
            try:
                logger.info(f"Creating bucket {bucket_name}...")
                s3_client.create_bucket(Bucket=bucket_name)
                logger.info(f"✅ Successfully created bucket {bucket_name}")
                return True
            except Exception as create_error:
                logger.error(f"Failed to create bucket {bucket_name}: {create_error}")
                return False
        else:
            logger.error(f"Error checking bucket {bucket_name}: {e}")
            return False


def upload_to_s3(local_dir: Path, bucket_name: str, s3_prefix: str, s3_client=None) -> Dict[str, int]:
    """
    Upload files to S3 with enhanced error handling and validation.

    Returns:
        Dict with upload statistics
    """
    stats = {
        "files_uploaded": 0,
        "files_skipped": 0,
        "errors": 0,
        "total_size_bytes": 0
    }

    if s3_client is None:
        logger.info("Creating new boto3 S3 client...")
        s3_client = get_boto3_client("s3")

    if not local_dir.exists():
        logger.error(f"Local directory does not exist: {local_dir}")
        raise FileNotFoundError(f"Directory not found: {local_dir}")

    # Ensure bucket exists before uploading
    if not ensure_bucket_exists(bucket_name, s3_client):
        raise Exception(f"Failed to ensure bucket {bucket_name} exists")

    files_found = False
    logger.info(f"Uploading files from: {local_dir} to s3://{bucket_name}/{s3_prefix}")

    for root, _, files in os.walk(local_dir):
        for file in files:
            files_found = True
            local_file_path = Path(root) / file
            relative_path = local_file_path.relative_to(local_dir)
            s3_key = f"{s3_prefix}/{relative_path.as_posix()}"

            file_size = local_file_path.stat().st_size
            logger.info(f"Uploading {local_file_path} ({file_size} bytes) to s3://{bucket_name}/{s3_key}")

            try:
                # Check if file already exists (optional - for incremental uploads)
                try:
                    s3_client.head_object(Bucket=bucket_name, Key=s3_key)
                    logger.info(f"File already exists, skipping: {s3_key}")
                    stats["files_skipped"] += 1
                    continue
                except Exception as head_error:
                    # Only log if it's not a "not found" error
                    if '404' not in str(head_error) and 'NoSuchKey' not in str(head_error):
                        logger.debug(f"Head object check failed (expected for new files): {head_error}")
                    pass  # File doesn't exist, proceed with upload

                # Upload with metadata
                s3_client.upload_file(
                    str(local_file_path),
                    bucket_name,
                    s3_key,
                    ExtraArgs={
                        'Metadata': {
                            'source': 'github',
                            'original_path': str(relative_path),
                            'upload_timestamp': str(int(time.time())),
                            'file_size': str(file_size)
                        }
                    }
                )

                # Verify upload
                s3_client.head_object(Bucket=bucket_name, Key=s3_key)

                stats["files_uploaded"] += 1
                stats["total_size_bytes"] += file_size
                logger.info(f"✅ Successfully uploaded: {s3_key}")

            except Exception as e:
                error_msg = f"❌ Failed to upload {local_file_path}: {e}"
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    error_msg += f" (HTTP {e.response.status_code})"
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    error_msg += f" - Response: {e.response.text[:200]}"
                logger.error(error_msg)
                stats["errors"] += 1

    if not files_found:
        logger.warning(f"No files found in {local_dir} to upload.")
    else:
        logger.info(f"Upload completed. Stats: {stats}")

    return stats


def cleanup_local_files(local_dir: Path) -> None:
    """Clean up local downloaded files."""
    try:
        if local_dir.exists():
            import shutil
            shutil.rmtree(local_dir)
            logger.info(f"Cleaned up local directory: {local_dir}")
    except Exception as e:
        logger.warning(f"Failed to cleanup {local_dir}: {e}")


def calculate_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def validate_upload(local_dir: Path, bucket_name: str, s3_prefix: str, s3_client) -> bool:
    """Validate that all local files were uploaded correctly."""
    logger.info("Validating upload...")

    validation_errors = 0

    for root, _, files in os.walk(local_dir):
        for file in files:
            local_file_path = Path(root) / file
            relative_path = local_file_path.relative_to(local_dir)
            s3_key = f"{s3_prefix}/{relative_path.as_posix()}"

            try:
                # Check if file exists in S3
                s3_response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)

                # Compare file sizes
                local_size = local_file_path.stat().st_size
                s3_size = s3_response['ContentLength']

                if local_size != s3_size:
                    logger.error(f"Size mismatch for {file}: local={local_size}, s3={s3_size}")
                    validation_errors += 1
                else:
                    logger.info(f"✅ Validated: {file}")

            except Exception as e:
                logger.error(f"Validation failed for {file}: {e}")
                validation_errors += 1

    if validation_errors == 0:
        logger.info("✅ All files validated successfully")
        return True
    else:
        logger.error(f"❌ Validation failed with {validation_errors} errors")
        return False