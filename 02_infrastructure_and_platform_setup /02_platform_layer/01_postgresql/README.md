## Installing operator
- Delete all helm repos
```commandline
 for repo in $(helm repo list | awk 'NR>1 {print $1}'); do helm repo remove "$repo"; done
```

- Add helm repo
```commandline
helm repo add cnpg https://cloudnative-pg.github.io/charts

helm repo update
```
- Install operator
```commandline
helm install cnpg \
--namespace cnpg-system \
--create-namespace \
--version 0.22.1 \
cnpg/cloudnative-pg
```
- Check operator pod is up
```commandline
kubectl get pod -n cnpg-system
 
 
NAME                                   READY   STATUS    RESTARTS   AGE
cnpg-cloudnative-pg-5fbbcc8844-b8c5f   1/1     Running   0          2m3s
```
## Installing Cluster
- 
```commandline
helm install cnpg \
--namespace cnpg-database \
--create-namespace \
--values custom-values.yaml \
cnpg/cluster
```

## Expose db to outside
```commandline
 kubectl apply -f cnpg-service-nodeport.yaml
```

## Get superuser(postgres) password
```commandline
 kubectl get secret -n cnpg-database cnpg-cluster-superuser -o jsonpath='{.data.password}' | base64 -d
```

## Connect to psql on db pod
```commandline
kubectl exec -it cnpg-cluster-1 -n cnpg-database -- psql -U postgres
```
