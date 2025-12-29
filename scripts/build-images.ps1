$ErrorActionPreference = "Stop"

Write-Host "Building Docker images..." -ForegroundColor Green

# Frontend
Write-Host "Building Frontend..."
docker build -t frontend:latest ./HomeLab/apps/frontend

# BFF
Write-Host "Building BFF..."
docker build -t bff:latest ./HomeLab/apps/bff

# Weather Service
Write-Host "Building Weather Service..."
docker build -t weather-service:latest ./HomeLab/apps/weather-service

# Hockey Service
Write-Host "Building Hockey Service..."
docker build -t hockey-service:latest ./HomeLab/apps/hockey-service

# News Service
Write-Host "Building News Service..."
docker build -t news-service:latest ./HomeLab/apps/news-service

Write-Host "All images built successfully!" -ForegroundColor Green
