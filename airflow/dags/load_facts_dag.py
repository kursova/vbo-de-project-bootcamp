from airflow.decorators import dag
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from datetime import datetime, timedelta
from airflow.models import Param


@dag(
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["fact"],
    template_searchpath='/opt/airflow/dags/repo/airflow/dags/spark_on_k8s',
    params={
        "start_date": Param(
            default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            description="Start date for fact table processing (YYYY-MM-DD)",
            type="string"
        ),
        "end_date": Param(
            default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            description="End date for fact table processing (YYYY-MM-DD)",
            type="string"
        ),
        "data_year_offset": Param(
            default="1",
            description="Year offset for data processing (default: 1 for previous year)",
            type="string"
        )
    }
)
def load_facts_dag():
    ingest_task = SparkKubernetesOperator(
        task_id="load-facts",
        image="spark-load_facts:1.0",
        namespace="default",
        name="load_facts",
        application_file="load_facts_sparkApplication.yaml",
        # Valid parameters for SparkKubernetesOperator
        delete_on_termination=True,
        get_logs=True,
        startup_timeout_seconds=600,
        reattach_on_restart=True,
        log_events_on_failure=True
    )

    # Do NOT call ingest_task(), just let it be registered in the DAG
    # If you had more tasks, you'd define dependencies like: task1 >> task2


dag_instance = load_facts_dag()