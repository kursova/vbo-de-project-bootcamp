## Prepare PostgreSQL for Nessie
- DBeaver
- kubectl
```commandline
kubectl exec -it cnpg-cluster-1 -n cnpg-database -- psql -U postgres
```

### Create a Database for nessie
```commandline
CREATE DATABASE nessie;
\c nessie;
CREATE USER nessie_user WITH PASSWORD 'Ankara06';
GRANT ALL PRIVILEGES ON database nessie TO nessie_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO nessie_user;
```

## Install Nessie
### Add Helm Repo
```commandline
helm repo add nessie https://charts.projectnessie.org

helm repo update
```
## Create namespace
```commandline
kubectl create namespace nessie
```

## Create secret for postgresql and minio access
```commandline
kubectl create secret generic nessie-postgres-minio-creds -n nessie \
  --from-literal=username=nessie_user \
  --from-literal=password=Ankara06 \
  --from-literal=NESSIE_CATALOG_SERVICE_S3_ACCESS_KEY_NAME=minioadmin \
  --from-literal=NESSIE_CATALOG_SERVICE_S3_ACCESS_KEY_SECRET=minioadmin123
```
## Custom values

## Install nessie with helm
```commandline
helm install nessie nessie/nessie -n nessie -f custom-values.yaml
```

## Nodeport (expose outside)
```commandline
kubectl apply -f nessie-service-nodeport.yaml
```
 
Check http://127.0.0.1:31920/tree/main