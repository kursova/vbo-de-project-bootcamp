from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

start_date = datetime(2024, 5, 20)

default_args = {
    'owner': 'airflow',
    'start_date': start_date,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

with DAG('sql_operator_dag', default_args=default_args, schedule_interval='@once', catchup=False) as dag:
    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id='postgresql_traindb_conn',
        sql="""create table if not exists 
        public.books(id SERIAL PRIMARY KEY, 
        name varchar(255));"""
    )

    insert_books = SQLExecuteQueryOperator(
        task_id="insert_books",
        conn_id='postgresql_traindb_conn',
        sql="""insert into public.books(name) 
            VALUES ('Çalı Kuşu'), ('Great Expectations'), ('Idiot'), ('Father Goriot');"""
    )

    fetch_books = SQLExecuteQueryOperator(
        task_id="fetch_books",
        conn_id='postgresql_traindb_conn',
        sql="SELECT * FROM public.books;",
        return_last=True,
    )

    create_table >> insert_books >> fetch_books