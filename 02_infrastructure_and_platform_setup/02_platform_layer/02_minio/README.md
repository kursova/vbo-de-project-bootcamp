## Create namespace
```commandline
kubectl create ns minio
```

## Add helm repo
```
helm repo add minio https://charts.min.io/

helm repo update
```
## Create credentials
```commandline
kubectl create secret generic minio-credentials -n minio \
  --from-literal=rootUser=minioadmin \
  --from-literal=rootPassword=minioadmin123
```


## Install with custom options
```commandline
helm install minio minio/minio \
--version 5.4.0 \
--namespace minio \
--set mode=standalone \
--set existingSecret=minio-credentials \
--set persistence.storageClass=hostpath \
--set persistence.size=20Gi \
--set resources.requests.memory=512Mi \
--set resources.requests.cpu=250m \
--set resources.limits.memory=1Gi \
--set resources.limits.cpu=500m \
--set securityContext.runAsUser=1000 \
--set securityContext.runAsGroup=1000 \
--set securityContext.fsGroup=1000 \
--set service.type=NodePort \
--set service.nodePort=30900 \
--set consoleService.type=NodePort \
--set consoleService.nodePort=30901
```
## Check resources
```commandline
 kubectl get all -n minio
NAME                         READY   STATUS    RESTARTS   AGE
pod/minio-8495545468-lnws2   1/1     Running   0          39s

NAME                    TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
service/minio           NodePort   10.102.78.75   <none>        9000:30900/TCP   39s
service/minio-console   NodePort   10.99.127.69   <none>        9001:30901/TCP   39s

NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/minio   1/1     1            1           39s

NAME                               DESIRED   CURRENT   READY   AGE
replicaset.apps/minio-8495545468   1         1         1       39s
```

## Web UI
http://127.0.0.1:30901/

## Create bucket 
- warehouse