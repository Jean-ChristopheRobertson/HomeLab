.PHONY: build cluster-up cluster-down up down restart

build:
	pwsh ./scripts/build-images.ps1

cluster-up:
	k3d cluster create --config deploy/cluster/k3d.yaml

cluster-down:
	k3d cluster delete --config deploy/cluster/k3d.yaml

up:
	pwsh ./manage.ps1 -Up

down:
	pwsh ./manage.ps1 -Down

restart:
	pwsh ./manage.ps1 -Restart

