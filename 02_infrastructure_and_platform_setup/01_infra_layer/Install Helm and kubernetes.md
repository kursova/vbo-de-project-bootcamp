brew install helm
helm version

brew install kubectl
kubectl version --client
Client Version: v1.33.1
Kustomize Version: v5.6.0
kubectl get nodes
NAME             STATUS   ROLES           AGE     VERSION
docker-desktop   Ready    control-plane   3d23h   v1.32.2

kubectl get ns
NAME              STATUS   AGE
default           Active   3d23h
kube-node-lease   Active   3d23h
kube-public       Active   3d23h
kube-system       Active   3d23h


