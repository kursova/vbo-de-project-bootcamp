## Prepare PostgreSQL for Airflow DB
### Access PostgreSQL:
```commandline
kubectl exec -it cnpg-cluster-1 -n cnpg-database -- psql -U postgres
```
### Create a Database for Airflow:
```commandline
CREATE DATABASE airflow;
\c airflow;
CREATE USER airflow WITH PASSWORD 'Ankara06';
GRANT ALL PRIVILEGES ON database airflow TO airflow;
GRANT ALL PRIVILEGES ON SCHEMA public TO airflow;

\q
```
## Create namespace
```commandline
kubectl create namespace airflow
```

## Add Helm Repo
```commandline
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```
### Custom values
- custom-values.yaml

## Web UI
- admin admin

## GitSync
### Create secret for github authentication
- Go github greate a token (classic) give repo permission
```commandline
kubectl create secret generic git-credentials -n airflow \
  --from-literal=GITSYNC_USERNAME=<username> \
  --from-literal=GITSYNC_PASSWORD=<your-github-token> \
  --from-literal=GIT_SYNC_USERNAME=<username> \
  --from-literal=GIT_SYNC_PASSWORD=<your-github-token>
```
### Create airflow/dags
- In the project root directory

### Create example dag
- my_dag.py inside airflow/dags


## Install Airflow with Helm
```commandline
helm install airflow apache-airflow/airflow -f custom-values.yaml --namespace airflow
```

## Check resources
```commandline
kubectl get all -n airflow


NAME                                     READY   STATUS    RESTARTS   AGE
pod/airflow-scheduler-79cfc779cd-s9l5n   3/3     Running   0          2m47s
pod/airflow-webserver-744585d79d-bkr7p   1/1     Running   0          2m47s

NAME                        TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
service/airflow-webserver   NodePort   10.105.42.84   <none>        8080:31880/TCP   2m47s

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/airflow-scheduler   1/1     1            1           2m47s
deployment.apps/airflow-webserver   1/1     1            1           2m47s

NAME                                           DESIRED   CURRENT   READY   AGE
replicaset.apps/airflow-scheduler-79cfc779cd   1         1         1       2m47s
replicaset.apps/airflow-webserver-744585d79d   1         1         1       2m47s
```

### Airflow Web UI
- http://localhost:31880
- admin admin

### Create database
```commandline
CREATE DATABASE traindb;
\c traindb;
CREATE USER train WITH PASSWORD 'Ankara06';
GRANT ALL PRIVILEGES ON database traindb TO train;
GRANT ALL PRIVILEGES ON SCHEMA public TO train;
```
### Create postgresql connection
- Connection Id: `postgresql_traindb_conn`
- Host: cnpg-cluster-rw.cnpg-database.svc.cluster.local
- Database: traindb
- Login: train
- Password: Ankara06
- Port: 5432

## Create second dag for simple sql operation
- airflow/dags/execute_sql_dag.py