## 1. Create database, user and privileges on postgresql for superset
Superset is application that need a database. Let's create a db, user and necessary grants.
Since we already have postgresql instance on out Kubernetes cluster it is reasonable to use it rather than create new instance.

### 1.1. Access PostgreSQL:
```bash
kubectl exec -it cnpg-cluster-1 -n cnpg-database -- psql -U postgres
```

### 1.2. Create a Database for Superset:
```bash
CREATE DATABASE superset;
\c superset;
CREATE USER superset WITH PASSWORD 'superset';
GRANT ALL PRIVILEGES ON DATABASE superset TO superset;
GRANT ALL PRIVILEGES ON schema public TO superset;

\q
```

## 2. Configure
### 2.1. Generate secret_key
```commandline
openssl rand -base64 42

oTiQw735K+2ySvdGQH4qTqM0mVN+V4ynt++kyvs7nEkOsSk7I9Mdd5c3
```

### 2.2. custom yaml file

## 3. Namespace
```commandline
kubectl create namespace superset
```

## 4. Helm install
```commandline
helm repo add superset http://apache.github.io/superset/

helm repo update

helm install superset superset/superset -n superset -f custom-values.yaml
```

## 5. Check resources
```commandline
 kubectl get all -n superset
NAME                                  READY   STATUS      RESTARTS   AGE
pod/superset-5fcdf8f659-lx9hr         1/1     Running     0          2m4s
pod/superset-init-db-ssp8g            0/1     Completed   0          2m4s
pod/superset-redis-master-0           1/1     Running     0          2m4s
pod/superset-worker-bd5746f64-rcgnz   1/1     Running     0          2m4s

NAME                              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
service/superset                  NodePort    10.97.206.99    <none>        8088:30088/TCP   2m4s
service/superset-redis-headless   ClusterIP   None            <none>        6379/TCP         2m4s
service/superset-redis-master     ClusterIP   10.109.172.46   <none>        6379/TCP         2m4s

NAME                              READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/superset          1/1     1            1           2m4s
deployment.apps/superset-worker   1/1     1            1           2m4s

NAME                                        DESIRED   CURRENT   READY   AGE
replicaset.apps/superset-5fcdf8f659         1         1         1       2m4s
replicaset.apps/superset-worker-bd5746f64   1         1         1       2m4s

NAME                                     READY   AGE
statefulset.apps/superset-redis-master   1/1     2m4s

NAME                         STATUS     COMPLETIONS   DURATION   AGE
job.batch/superset-init-db   Complete   1/1           73s        2m4s

```

## 6. Web UI
http://localhost:30088/
admin admin

## 7. Updates of values e.g. installing new pip package
```
helm upgrade --install superset superset/superset -n superset -f custom-values.yaml
```

## 8. Add connection
### 8.1. Trino connection
- Settings -> Database Connections


+Database -> Supported Databased Trino

![img.png](images/01_trino_connection.png)![img.png](images/01_superset_add_connection_02.png)

---
Name: Trino
SQLAlchemy URI: trino://admin@trino.trino.svc.cluster.local:8080
Test connection

### 8.2. Postgresql traindb
- +Database -> PostgreSQL
- SQLAlchemy URI: postgresql+psycopg2://train:Ankara06@cnpg-cluster-rw.cnpg-database.svc.cluster.local/traindb
- Name: Postgresql-traindb

## 9. Example Charts
### 9.1. Schema of trino tpch data

![img.png](images/02_tpch_schema.png)

---

### 9.2. Create dataset
- Superset UI -> SQL -> SQL Lab
- Query
```sql
SELECT 
    l.orderkey,
    l.partkey,
    l.suppkey,
    l.linenumber,
    l.quantity,
    l.extendedprice,
    l.discount,
    l.tax,
    l.returnflag,
    l.linestatus,
    l.shipdate,
    l.commitdate,
    l.receiptdate,
    l.shipinstruct,
    l.shipmode,
    l.comment AS lineitem_comment,
    o.custkey,
    o.orderstatus,
    o.totalprice,
    o.orderdate,
    o.orderpriority,
    o.clerk,
    o.shippriority,
    o.comment AS order_comment,
    ps.availqty,
    ps.supplycost,
    ps.comment AS partsupp_comment,
    s.name AS supplier_name,
    s.address AS supplier_address,
    s.phone AS supplier_phone,
    s.acctbal AS supplier_acctbal,
    s.comment AS supplier_comment,
    pt.name AS part_name,
    pt.mfgr,
    pt.brand,
    pt.type,
    pt.size,
    pt.container,
    pt.retailprice,
    pt.comment AS part_comment,
    cus.name AS customer_name,
    cus.address AS customer_address,
    cus.phone AS customer_phone,
    cus.acctbal AS customer_acctbal,
    cus.mktsegment,
    cus.comment AS customer_comment,
    n.name AS country,
    n.regionkey,
    n.comment AS nation_comment
FROM tpch.sf1.lineitem l 
JOIN tpch.sf1.orders o ON l.orderkey = o.orderkey
JOIN tpch.sf1.partsupp ps ON l.partkey = ps.partkey
JOIN tpch.sf1.supplier s ON ps.suppkey = s.suppkey
JOIN tpch.sf1.part pt ON ps.partkey = pt.partkey
JOIN tpch.sf1.customer cus ON o.custkey = cus.custkey
JOIN tpch.sf1.nation n ON cus.nationkey = n.nationkey 
```

Open sqllab on superset ui
Paste query and save as dataset

![img.png](images/03_sqllab_query.png)

---

![img_1.png](images/03_sqllab_quer_save.png)

---

### 9.3. Create a dashboard
### 9.4. Create Charts