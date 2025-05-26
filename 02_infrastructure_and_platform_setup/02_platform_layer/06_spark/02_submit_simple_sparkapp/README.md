- Dockerfile
- spark_on_k8s_app.py
- requirements.txt
- Build image
```commandline
docker build -t spark-k8s-app:2.0 .
```
- sparkApplication.yaml
- Submit application
```commandline
kubectl apply -f sparkApplication.yaml
```
- Driver logs
```commandline
kubectl logs -f pyspark-on-k8s-driver
```