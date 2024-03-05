# geant4-docker

Docker files for geant4 installation

## Base images:

- [Almalinux](https://hub.docker.com/_/almalinux)
- [Fedora](https://hub.docker.com/_/fedora)
- [Ubuntu](https://hub.docker.com/_/ubuntu)

## Naming and Tags Conventions

- **ostype**: fedora36, ubuntu22, almalinux9
- **geant4_version**: examples: 10.6.2, 10.7.4, 11.2.1
- **gemc_version**: examples: 5.4, 5.7
- **install_dir**: software installation directory.  
  - local: /usr/local
  - cvmfs: /cvmfs/oasis.opensciencegrid.org/jlab/geant4


- The base containers are named **jeffersonlab/base:ostype**


- The geant4 containers are named **jeffersonlab/sim:geant4_version-ostype-install_dir** 


- The gemc containers are named **jeffersonlab/gemc:gemc_version-geant4_version-ostype-install_dir**



# Build base images:

```
./create_dockerfile.py fedora36
```
