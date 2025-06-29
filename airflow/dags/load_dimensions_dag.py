from airflow.decorators import dag
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from datetime import datetime


@dag(
    schedule_interval="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["dimension"],
    template_searchpath='/opt/airflow/dags/repo/airflow/dags/spark_on_k8s'
)
def load_dimensions_dag():
    ingest_task = SparkKubernetesOperator(task_id="load-dimensions",
        image="spark-load_dimensions:1.0",
        namespace="default",
        name="load_dimensions",
        application_file="load_dimensions_sparkApplication.yaml",

    )

    # Do NOT call ingest_task(), just let it be registered in the DAG
    # If you had more tasks, you'd define dependencies like: task1 >> task2


dag_instance = load_dimensions_dag()