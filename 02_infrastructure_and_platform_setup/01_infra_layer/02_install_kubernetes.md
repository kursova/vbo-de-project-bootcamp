## Install Kubernetes 
### Open Docker desktop
- From settings enable kubernetes

![img.png](images/08_enable_kubernetes.png)

- Apply & Restart
---

- after start

![img.png](images/09_after_k8s_start.png)

---

## Install Helm
- Open Oracle Linux terminal
```commandline
 sudo yum install openssl
 
 curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
 
 chmod 700 get_helm.sh
 
 ./get_helm.sh
 
 helm version
```