# deploy.ps1 - Automates build, load into kind, and apply/rollout for the job-tracker app
# Usage: .\deploy.ps1

$ErrorActionPreference = "Stop"
$ClusterName = "job-tracker-cluster"
$Namespace = "job-tracker"

Write-Host "==> Building Docker images" -ForegroundColor Cyan
docker compose build

Write-Host "==> Loading images into Kind cluster" -ForegroundColor Cyan
kind load docker-image job-tracker-backend:latest --name $ClusterName
kind load docker-image job-tracker-frontend:latest --name $ClusterName

Write-Host "==> Applying manifests" -ForegroundColor Cyan
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

Write-Host "==> Restarting deployments to pick up new images" -ForegroundColor Cyan
kubectl rollout restart deployment backend -n $Namespace
kubectl rollout restart deployment frontend -n $Namespace

Write-Host "==> Waiting for rollout to complete" -ForegroundColor Cyan
kubectl rollout status deployment backend -n $Namespace
kubectl rollout status deployment frontend -n $Namespace

Write-Host "==> Current pod status" -ForegroundColor Cyan
kubectl get pods -n $Namespace

Write-Host "==> Done. Run this to access the app:" -ForegroundColor Green
Write-Host "    kubectl port-forward svc/frontend -n $Namespace 5173:80"
Write-Host "    kubectl port-forward svc/backend -n $Namespace 8000:8000"
