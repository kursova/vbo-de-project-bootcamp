#!/usr/bin/env python3
"""
GitHub to S3 Data Ingestion Pipeline

This script downloads data from a GitHub repository and uploads it to S3-compatible storage.
It includes comprehensive error handling, validation, and statistics reporting.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from highway_ingester.github_downloader import (
    download_github_dir,
    upload_to_s3,
    get_boto3_client,
    cleanup_local_files,
    validate_upload,
    test_s3_connection
)


def main():
    """Main execution function with comprehensive error handling."""
    start_time = time.time()

    # Load environment variables
    load_dotenv()

    # Configuration validation
    required_env_vars = [
        'GITHUB_TOKEN', 'REPO_OWNER', 'REPO_NAME', 'DATA_PATH',
        'LOCAL_DOWNLOADED_PATH', 'BUCKET',
        'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'REGION_NAME', 'S3_ENDPOINT'
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)

    # Get configuration
    config = {
        'github_token': os.getenv('GITHUB_TOKEN'),
        'repo_owner': os.getenv('REPO_OWNER'),
        'repo_name': os.getenv('REPO_NAME'),
        'data_path': os.getenv('DATA_PATH'),  # Single path for both GitHub and S3
        'local_downloaded_path': Path(os.getenv('LOCAL_DOWNLOADED_PATH') or '/tmp/downloaded_data'),
        'bucket': os.getenv('BUCKET'),
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'region_name': os.getenv('REGION_NAME'),
        's3_endpoint': os.getenv('S3_ENDPOINT'),
        'branch': os.getenv('BRANCH', 'main')  # Default to 'main' if not specified
    }

    # Debug AWS credentials (masked for security)
    print(f"🔐 AWS Access Key ID: {config['aws_access_key_id'][:8] if config['aws_access_key_id'] else 'None'}...")
    print(f"🔐 AWS Secret Key: {'***' if config['aws_secret_access_key'] else 'None'}")
    print(f"🔐 S3 Endpoint: {config['s3_endpoint']}")

    print("🚀 Starting GitHub to S3 Data Ingestion Pipeline")
    print(f"📁 Repository: {config['repo_owner']}/{config['repo_name']}")
    print(f"📂 Data Path: {config['data_path']}")
    print(f"🪣 Destination: s3://{config['bucket']}/{config['data_path']}")

    try:
        # Step 1: Download from GitHub
        print("\n📥 Step 1: Downloading from GitHub...")
        download_stats = download_github_dir(
            repo_owner=config['repo_owner'],
            repo_name=config['repo_name'],
            dir_path=config['data_path'],  # Use same path for GitHub
            branch=config['branch'],
            local_dir=str(config['local_downloaded_path']),
            token=config['github_token']
        )

        print(f"✅ Download completed:")
        print(f"   - Files downloaded: {download_stats['files_downloaded']}")
        print(f"   - Directories processed: {download_stats['directories_processed']}")
        print(f"   - Total size: {download_stats['total_size_bytes'] / (1024 * 1024):.2f} MB")
        print(f"   - Errors: {download_stats['errors']}")

        if download_stats['errors'] > 0:
            print("⚠️  Some files failed to download")

        # Step 2: Upload to S3
        print("\n📤 Step 2: Uploading to S3...")
        s3_client = get_boto3_client(
            service_name="s3",
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
            region_name=config['region_name'],
            endpoint_url=config['s3_endpoint']
        )

        # Test S3 connection before uploading
        print("🔍 Testing S3 connection...")
        if not test_s3_connection(s3_client):
            print("❌ S3 connection test failed")
            sys.exit(1)
        print("✅ S3 connection test successful")

        upload_stats = upload_to_s3(
            local_dir=config['local_downloaded_path'],
            bucket_name=config['bucket'],
            s3_prefix=config['data_path'],
            s3_client=s3_client
        )

        print(f"✅ Upload completed:")
        print(f"   - Files uploaded: {upload_stats['files_uploaded']}")
        print(f"   - Files skipped: {upload_stats['files_skipped']}")
        print(f"   - Total size: {upload_stats['total_size_bytes'] / (1024 * 1024):.2f} MB")
        print(f"   - Errors: {upload_stats['errors']}")

        if upload_stats['errors'] > 0:
            print("⚠️  Some files failed to upload")

        # Step 3: Validate upload
        print("\n🔍 Step 3: Validating upload...")
        validation_success = validate_upload(
            local_dir=config['local_downloaded_path'],
            bucket_name=config['bucket'],
            s3_prefix=config['data_path'],
            s3_client=s3_client
        )

        if validation_success:
            print("✅ Upload validation successful")
        else:
            print("❌ Upload validation failed")
            sys.exit(1)

        # Step 4: Cleanup (optional)
        cleanup_enabled = os.getenv('CLEANUP_LOCAL_FILES', 'true').lower() == 'true'
        if cleanup_enabled:
            print("\n🧹 Step 4: Cleaning up local files...")
            cleanup_local_files(config['local_downloaded_path'])
            print("✅ Local files cleaned up")
        else:
            print("\n💾 Step 4: Skipping cleanup (CLEANUP_LOCAL_FILES=false)")

        # Final summary
        total_time = time.time() - start_time
        print(f"\n🎉 Pipeline completed successfully in {total_time:.2f} seconds")
        print(f"📊 Summary:")
        print(f"   - Download: {download_stats['files_downloaded']} files")
        print(f"   - Upload: {upload_stats['files_uploaded']} files")
        print(f"   - Total data: {upload_stats['total_size_bytes'] / (1024 * 1024):.2f} MB")
        print(f"   - Processing time: {total_time:.2f} seconds")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()