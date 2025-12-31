$ErrorActionPreference = "Stop"

Write-Host "Building Docker images..." -ForegroundColor Green

# Frontend
Write-Host "Building Frontend..."
docker build -t frontend:latest "$PSScriptRoot/../apps/frontend"

# BFF
Write-Host "Building BFF..."
docker build -t bff:latest "$PSScriptRoot/../apps/bff"

# Weather Service
Write-Host "Building Weather Service..."
docker build -t weather-service:latest "$PSScriptRoot/../apps/weather-service"

# Hockey Service
Write-Host "Building Hockey Service..."
docker build -t hockey-service:latest "$PSScriptRoot/../apps/hockey-service"

# News Service
Write-Host "Building News Service..."
docker build -t news-service:latest "$PSScriptRoot/../apps/news-service"

Write-Host "All images built successfully!" -ForegroundColor Green
