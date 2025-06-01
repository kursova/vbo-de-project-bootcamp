from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

start_date = datetime(2023, 10, 11)

default_args = {
    'owner': 'airflow',
    'start_date': start_date,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

with DAG('my_dag', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    t0 = BashOperator(task_id='task0', bash_command='echo "Hello! I am task0"', retries=2, retry_delay=timedelta(seconds=15))

    t1 = BashOperator(task_id='task1',
                      bash_command='echo "Hello! I am task1"',
                      retries=2, retry_delay=timedelta(seconds=15))

    t2 = BashOperator(task_id='task2', bash_command='echo "Hello! I am task3"',
                      retries=2, retry_delay=timedelta(seconds=15))

    t0 >> t1 >> t2