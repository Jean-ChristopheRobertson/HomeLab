param (
    [Parameter(Mandatory = $false)]
    [switch]$Up,

    [Parameter(Mandatory = $false)]
    [switch]$Down,

    [Parameter(Mandatory = $false)]
    [switch]$Restart
)
$ErrorActionPreference = "Stop"
# Ensure we are running from the script's directory
Set-Location $PSScriptRoot

$ClusterConfig = "deploy/cluster/k3d.yaml"

function Remove-Cluster {
    Write-Host "💥 Destroying Cluster..." -ForegroundColor Red
    k3d cluster delete --config $ClusterConfig
}

function Create-Cluster {
    Write-Host "🌱 Creating Cluster..." -ForegroundColor Green
    # Check if cluster exists to avoid error if running -Up on existing cluster
    $clusters = k3d cluster list -o json | ConvertFrom-Json
    if ($clusters.name -contains "sre-dashboard-cluster") {
        Write-Host "   Cluster already exists." -ForegroundColor Yellow
    }
    else {
        k3d cluster create --config $ClusterConfig
    }
    
    # Ensure we have the kubeconfig and context
    Write-Host "   Refreshing kubeconfig..."
    
    # Aggressively clean up potential stale config to prevent GKE conflicts
    # Use cmd /c to avoid PowerShell NativeCommandError on stderr output
    cmd /c "kubectl config delete-context k3d-sre-dashboard-cluster 2>&1" | Out-Null
    cmd /c "kubectl config delete-cluster k3d-sre-dashboard-cluster 2>&1" | Out-Null
    cmd /c "kubectl config delete-user k3d-sre-dashboard-cluster 2>&1" | Out-Null

    k3d kubeconfig merge sre-dashboard-cluster --kubeconfig-switch-context
    
    # Patch kubeconfig to use 127.0.0.1 if host.docker.internal is used (common issue on Windows)
    $clusterName = "k3d-sre-dashboard-cluster"
    try {
        # Use correct quoting for JSONPath on Windows
        $serverUrl = kubectl config view -o jsonpath="{.clusters[?(@.name=='$clusterName')].cluster.server}"
        if ($serverUrl -match "host.docker.internal") {
            Write-Host "   Patching kubeconfig to use 127.0.0.1..." -ForegroundColor Yellow
            $newUrl = $serverUrl -replace "host.docker.internal", "127.0.0.1"
            kubectl config set-cluster $clusterName --server=$newUrl
        }
    }
    catch {
        Write-Warning "Failed to patch kubeconfig: $_"
    }
    
    # Verify context
    $currentContext = kubectl config current-context
    if ($currentContext -ne "k3d-sre-dashboard-cluster") {
        Write-Error "Failed to switch context. Current context is '$currentContext'. Expected 'k3d-sre-dashboard-cluster'."
    }
    
    # Verify connectivity
    Write-Host "   Verifying connectivity..."
    try {
        $info = kubectl cluster-info
        Write-Host "   Connected to: $info" -ForegroundColor Gray
    }
    catch {
        Write-Error "   Could not connect to the cluster. It might be starting up or the config is invalid."
    }

    Write-Host "   Context set to $currentContext" -ForegroundColor Green
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
