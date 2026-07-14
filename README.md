# Job Application Tracker - Deployed on Kubernetes

A 3-tier web application (React/TypeScript frontend, FastAPI backend, PostgreSQL database) built from scratch, containerized with Docker, and deployed on a local Kubernetes cluster using Kind — with full manual manifest authoring, failure debugging, and deployment automation.

## What it does

Tracks job applications - company, role, status, and applied date - through a simple web UI backed by a real database.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript, served via nginx |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (via Kind — Kubernetes in Docker) |

## Architecture

```
Browser → Frontend (nginx, 2 replicas) → Backend (FastAPI, 2 replicas) → PostgreSQL (1 replica, persistent volume)
```

Each tier runs as its own Kubernetes Deployment with a Service in front of it for stable networking. Configuration is split between ConfigMaps (non-secret) and Secrets (credentials). Database data is preserved across pod restarts using a PersistentVolumeClaim.

## What this project demonstrates

- **Docker fundamentals** — writing Dockerfiles for 3 different tiers, multi-stage builds, Docker Compose orchestration
- **Core Kubernetes concepts** — Pods, Deployments, Services, Namespaces, ConfigMaps, Secrets, PersistentVolumeClaims — each learned hands-on before touching the real app
- **Manifest authoring** — 10 hand-written YAML manifests covering the full application stack
- **Production-style debugging** — deliberately broke the deployment three different ways and diagnosed each using `kubectl logs` and `kubectl describe`:
  - Wrong database password → `CrashLoopBackOff`, exit code 3 (application-level failure)
  - Wrong image tag → `ImagePullBackOff` (container never started)
  - Undersized memory limit → `CrashLoopBackOff`, exit code 137 (OOM kill)
- **Deployment automation** — a single PowerShell script (`deploy.ps1`) that builds images, loads them into the Kind cluster, applies all manifests, and waits for a healthy rollout

## Project structure

```
job-tracker/
├── backend/              # FastAPI app + Dockerfile
├── frontend/              # React/TS app + Dockerfile
├── k8s/                   # Kubernetes manifests
│   ├── namespace.yaml
│   ├── postgres-secret.yaml
│   ├── postgres-pvc.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── backend-configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
├── docker-compose.yml     # Local dev without Kubernetes
└── deploy.ps1              # One-command build + deploy to Kind
```

## Running it

**Prerequisites:** Docker Desktop, `kubectl`, `kind`

```powershell
# Create the cluster (first time only)
kind create cluster --name job-tracker-cluster

# Build, load, and deploy everything
.\deploy.ps1

# Access the app
kubectl port-forward svc/frontend -n job-tracker 5173:80
kubectl port-forward svc/backend -n job-tracker 8000:8000
```

Then open `http://localhost:5173`.

## What's next

- Add an Ingress controller instead of relying on `port-forward`
- Add resource requests/limits tuning based on real load testing
- Automate with ArgoCD (GitOps) once manual deployment is fully solid
