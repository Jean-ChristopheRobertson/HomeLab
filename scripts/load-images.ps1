$ErrorActionPreference = "Stop"

Write-Host "Importing images into k3d cluster 'sre-dashboard-cluster'..." -ForegroundColor Green

$images = @(
    "frontend:latest",
    "bff:latest",
    "weather-service:latest",
    "hockey-service:latest",
    "news-service:latest"
)

foreach ($img in $images) {
    Write-Host "Importing $img..."
    k3d image import $img -c sre-dashboard-cluster
}

Write-Host "All images imported successfully!" -ForegroundColor Green
