.PHONY: build cluster-up cluster-down

build:
	@echo "Building..."

cluster-up:
	k3d cluster create --config deploy/cluster/k3d.yaml

cluster-down:
	k3d cluster delete --config deploy/cluster/k3d.yaml
