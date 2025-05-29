## Upload source data to MinIO
- bronze/Churn_Modelling.csv

## Spark Code
- iceberg_nessie.py

## requirements.txt

## Dockerfile

## Build Image
```commandline
docker build -t spark-iceberg-nessie:1.0 .
```

## sparkApplication.yaml
- write_to_iceberg_sparkApplication.yaml

## Apply
```commandline
kubectl apply -f write_to_iceberg_sparkApplication.yaml
```

## Watch
### Operator logs
```commandline
 kubectl logs -f pod/my-spark-operator-controller-68658b59c7-vqpq8 -n spark-operator
```
### Driver logs
```commandline
kubectl logs -f iceberg-nessie-driver
```

## Delete application
```commandline
kubectl delete -f write_to_iceberg_sparkApplication.yaml
```