# Geant4 Containers for JLAB

This repository publish docker containers with Geant4 installations

## Base images 

 - fedora
 - ubuntu
 - arch
 - almalinux
 - debian
 - rhel

<br/>

## Geant4 Tags

 - 11.3.2


## Examples:

Pull:
```bash
docker pull ghcr.io/jeffersonlab/geant4-docker:11.3.2-ubuntu:24.04
```

Run:
```bash
docker run --rm -it ghcr.io/jeffersonlab/geant4-docker:11.3.2-ubuntu:24.04 bash```
```

Run (Apple Silicon Mac):
```bash
docker run --rm -it --platform=linux/amd64 ghcr.io/jeffersonlab/geant4-docker:11.3.2-ubuntu:24.04 bash
```