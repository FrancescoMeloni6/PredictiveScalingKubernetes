## Ambiente di esecuzione

Il progetto è stato sviluppato e testato su **Windows 11** con la seguente stack tecnologica:

| Componente        | Versione / Note                                  |
|------------------|--------------------------------------------------|
| Docker Desktop   | Motore container locale                          |
| Minikube         | Cluster Kubernetes single-node                   |
| Helm             | Package manager per chart Kubernetes             |
| Prometheus       | Helm chart `prometheus-community`                |
| KEDA             | Helm chart `kedacore/keda`                       |
| Ingress NGINX    | Addon Minikube                                  |
| Python           | 3.11                                             |

---
# Configurazione

```bash
# Punta Docker al daemon di Minikube
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build delle immagini
docker build -t random-service   ./random-service
docker build -t hash-service     ./hash-service
docker build -t forecast-service ./forecast-service
docker build -t load-generator   ./load-generator

# Installazione e Deployment di Prometheus e KEDA
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install prometheus prometheus-community/prometheus
helm install keda kedacore/keda --namespace keda --create-namespace

# Deploy dei manifest Kubernetes
kubectl apply -f k8s/random-deployment.yaml
kubectl apply -f k8s/random-service.yaml
kubectl apply -f k8s/hash-deployment.yaml
kubectl apply -f k8s/hash-service.yaml
kubectl apply -f k8s/forecast-deployment.yaml
kubectl apply -f k8s/forecast-service.yaml
kubectl apply -f k8s/load-generator.yaml

# Scaler KEDA (da applicare dopo che i servizi sono Running)
kubectl apply -f k8s/random-scaler.yaml
kubectl apply -f k8s/hash-scaler.yaml
```

# Accesso locale

[https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns](https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns)

```bash
# Su powershell come amministratore
Add-DnsClientNrptRule -Namespace ".test" -NameServers "$(minikube ip)"

# Aggiunta di Ingress e Ingress DNS
minikube addons enable ingress
minikube addons enable ingress-dns

# Attivazione Ingress
kubectl apply -f k8s/ingress-service.yaml
minikube tunnel
```