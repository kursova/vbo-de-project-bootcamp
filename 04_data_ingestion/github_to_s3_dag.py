from airflow.decorators import dag
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime


@dag(
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingestion"]
)
def github_to_s3_dag():
    ingest_task = KubernetesPodOperator(
        task_id="run_ingestion_container",
        name="github-to-s3-ingester",
        namespace="airflow",
        image="ghcr.io/erkansirin78/github-ingester:latest",
        cmds=["python", "/app/src/main.py"],
        get_logs=True,
        env_vars={
            # GitHub download config
            "GITHUB_TOKEN": "{{ var.value.GITHUB_TOKEN }}",
            "REPO_OWNER": "{{ var.value.REPO_OWNER }}",
            "REPO_NAME": "{{ var.value.REPO_NAME }}",
            "DIR_PATH": "{{ var.value.DIR_PATH }}",

            # Local save path
            "LOCAL_DOWNLOADED_PATH": "{{ var.value.LOCAL_DOWNLOADED_PATH }}",

            # S3 upload config
            "BUCKET": "{{ var.value.BUCKET }}",
            "S3_PATH": "{{ var.value.S3_PATH }}",
            "AWS_ACCESS_KEY_ID": "{{ var.value.AWS_ACCESS_KEY_ID }}",
            "AWS_SECRET_ACCESS_KEY": "{{ var.value.AWS_SECRET_ACCESS_KEY }}",
            "REGION_NAME": "{{ var.value.REGION_NAME }}",
            "S3_ENDPOINT": "{{ var.value.S3_ENDPOINT }}",
        },
        is_delete_operator_pod=True,
    )

    # Do NOT call ingest_task(), just let it be registered in the DAG
    # If you had more tasks, you'd define dependencies like: task1 >> task2


dag_instance = github_to_s3_dag()