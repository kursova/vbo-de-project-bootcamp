## Add Spark operator helm repo
```commandline
helm repo add \
spark-operator \
https://kubeflow.github.io/spark-operator


helm repo update
```

## Create namespace for spark operator
```commandline
kubectl create ns spark-operator
```

## Install operator with helm
```commandline
helm install \
my-spark-operator \
spark-operator/spark-operator \
--namespace spark-operator \
--set webhook.enable=true
```

## Check resources
```commandline
kubectl get all -n spark-operator
NAME                                                READY   STATUS    RESTARTS   AGE
pod/my-spark-operator-controller-68658b59c7-sv6r2   1/1     Running   0          63s
pod/my-spark-operator-webhook-786d69bbd5-rm6qd      1/1     Running   0          63s

NAME                                    TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
service/my-spark-operator-webhook-svc   ClusterIP   10.97.95.52   <none>        9443/TCP   63s

NAME                                           READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-spark-operator-controller   1/1     1            1           63s
deployment.apps/my-spark-operator-webhook      1/1     1            1           63s

NAME                                                      DESIRED   CURRENT   READY   AGE
replicaset.apps/my-spark-operator-controller-68658b59c7   1         1         1       63s
replicaset.apps/my-spark-operator-webhook-786d69bbd5      1         1         1       63s

```

## Create service account
```commandline
kubectl create serviceaccount spark

kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
```