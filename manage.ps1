param (
    [Parameter(Mandatory=$false)]
    [switch]$Up,

    [Parameter(Mandatory=$false)]
    [switch]$Down,

    [Parameter(Mandatory=$false)]
    [switch]$Restart
)

$ClusterConfig = "deploy/cluster/k3d.yaml"

function Remove-Cluster {
    Write-Host "💥 Destroying Cluster..." -ForegroundColor Red
    k3d cluster delete --config $ClusterConfig
}

function Create-Cluster {
    Write-Host "🌱 Creating Cluster..." -ForegroundColor Green
    k3d cluster create --config $ClusterConfig
}

function Build-Images {
    Write-Host "🐳 Building Images..." -ForegroundColor Cyan
    & ./scripts/build-images.ps1
}

function Load-Images {
    Write-Host "🚚 Loading Images..." -ForegroundColor Cyan
    & ./scripts/load-images.ps1
}

function Deploy-Resources {
    Write-Host "🚀 Deploying Resources..." -ForegroundColor Magenta
    
    # Base
    Write-Host "  - Base (Namespaces, Redis, Ingress)..."
    kubectl apply -f deploy/base/namespaces.yaml
    kubectl apply -f deploy/base/redis
    kubectl apply -f deploy/base/ingress

    # Observability
    Write-Host "  - Observability (Prometheus, Grafana)..."
    kubectl apply -f deploy/observability

    # Apps
    Write-Host "  - Apps (Microservices)..."
    kubectl apply -f deploy/apps
    
    Write-Host "⏳ Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod --all -n sre-dashboard --timeout=120s
}

if ($Down -or $Restart) {
    Remove-Cluster
}

if ($Up -or $Restart) {
    Create-Cluster
    Build-Images
    Load-Images
    Deploy-Resources
    
    Write-Host "✅ Setup Complete!" -ForegroundColor Green
    Write-Host "  - Dashboard: http://localhost:8080 (via Ingress if configured) or port-forward"
    Write-Host "  - Grafana:   kubectl port-forward svc/grafana 3000:80 -n monitoring"
    Write-Host "  - Prometheus: kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
}

if (-not ($Up -or $Down -or $Restart)) {
    Write-Host "Usage: ./manage.ps1 [-Up] [-Down] [-Restart]"
}
