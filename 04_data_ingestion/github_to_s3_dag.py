from airflow.decorators import dag
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dag(
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingestion", "github", "s3"],
    description="Download data from GitHub repository and upload to S3/MinIO",
    doc_md="""
    ## GitHub to S3 Data Ingestion DAG

    This DAG downloads data from a GitHub repository and uploads it to S3-compatible storage (MinIO).

    ### Prerequisites
    - GitHub token with repository access
    - MinIO/S3 credentials configured
    - Airflow variables set up

    ### Variables Required
    - `GITHUB_TOKEN`: GitHub personal access token
    - `REPO_OWNER`: GitHub repository owner
    - `REPO_NAME`: GitHub repository name
    - `DATA_PATH`: Data path within the repository
    - `BRANCH`: Branch to download from
    - `LOCAL_DOWNLOADED_PATH`: Local path for downloaded files
    - `BUCKET`: S3 bucket name
    - `AWS_ACCESS_KEY_ID`: S3 access key
    - `AWS_SECRET_ACCESS_KEY`: S3 secret key
    - `REGION_NAME`: AWS region
    - `S3_ENDPOINT`: S3 endpoint URL
    """
)
def github_to_s3_dag():
    def validate_variables():
        """Validate that all required Airflow variables are set."""
        required_vars = [
            'GITHUB_TOKEN', 'REPO_OWNER', 'REPO_NAME', 'DATA_PATH', 'BRANCH',
            'LOCAL_DOWNLOADED_PATH', 'BUCKET',
            'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'REGION_NAME', 'S3_ENDPOINT'
        ]

        # Optional variables (will use defaults if not set)
        optional_vars = ['CLEANUP_LOCAL_FILES']

        missing_vars = []
        for var_name in required_vars:
            try:
                Variable.get(var_name)
            except KeyError:
                missing_vars.append(var_name)

        if missing_vars:
            raise ValueError(f"Missing required Airflow variables: {missing_vars}")

        # Check optional variables and set defaults if missing
        for var_name in optional_vars:
            try:
                Variable.get(var_name)
            except KeyError:
                logger.info(f"Optional variable {var_name} not set, will use default value")

        logger.info("All required variables are configured")
        return True

    # Validation task
    validate_task = PythonOperator(
        task_id="validate_variables",
        python_callable=validate_variables,
        doc="Validate that all required Airflow variables are configured"
    )

    # Main ingestion task
    ingest_task = KubernetesPodOperator(
        task_id="run_ingestion_container",
        name="github-to-s3-ingester",
        namespace="airflow",
        image="github-ingester:latest",
        image_pull_policy="IfNotPresent",  # Check local images first
        cmds=["python", "/app/src/main.py"],
        get_logs=True,
        env_vars={
            # GitHub download config
            "GITHUB_TOKEN": "{{ var.value.GITHUB_TOKEN }}",
            "REPO_OWNER": "{{ var.value.REPO_OWNER }}",
            "REPO_NAME": "{{ var.value.REPO_NAME }}",
            "DATA_PATH": "{{ var.value.DATA_PATH }}",
            "BRANCH": "{{ var.value.BRANCH }}",

            # Local save path
            "LOCAL_DOWNLOADED_PATH": "{{ var.value.LOCAL_DOWNLOADED_PATH }}",

            # S3 upload config
            "BUCKET": "{{ var.value.BUCKET }}",
            "AWS_ACCESS_KEY_ID": "{{ var.value.AWS_ACCESS_KEY_ID }}",
            "AWS_SECRET_ACCESS_KEY": "{{ var.value.AWS_SECRET_ACCESS_KEY }}",
            "REGION_NAME": "{{ var.value.REGION_NAME }}",
            "S3_ENDPOINT": "{{ var.value.S3_ENDPOINT }}",

            # Optional configuration
            "CLEANUP_LOCAL_FILES": "{{ var.value.CLEANUP_LOCAL_FILES }}",
        },
        # Resource limits for production
        container_resources={
            "requests": {
                "cpu": "200m",
                "memory": "512Mi"
            },
            "limits": {
                "cpu": "500m",
                "memory": "1Gi"
            }
        },
        # Pod configuration
        is_delete_operator_pod=True,
        in_cluster=True,
        # Retry configuration
        retries=3,
        retry_delay=timedelta(minutes=2),
        retry_exponential_backoff=True,
        max_retry_delay=timedelta(minutes=10),
        # Timeout configuration
        startup_timeout_seconds=300,
        # Security context
        security_context={
            "run_as_user": 1000,
            "run_as_group": 1000,
            "fs_group": 1000
        },
        doc="""
        ## Data Ingestion Task

        Downloads data from GitHub repository and uploads to S3/MinIO.

        ### Process:
        1. Authenticate with GitHub API
        2. Download repository contents
        3. Upload files to S3/MinIO
        4. Clean up temporary files

        ### Error Handling:
        - Retries on network failures
        - Exponential backoff
        - Resource limits enforced
        """
    )

    # Define task dependencies
    validate_task >> ingest_task

    return ingest_task


# Create DAG instance
dag_instance = github_to_s3_dag()