# geant4-docker

Docker files for geant4 installation

## Base images:

- [Almalinux](https://hub.docker.com/_/almalinux)
- [Fedora](https://hub.docker.com/_/fedora)
- [Ubuntu](https://hub.docker.com/_/ubuntu)

## Naming and Tags Conventions

- **ostype**: fedora36, ubuntu22, almalinux9
- **geant4_version**: examples: 10.6.2, 10.7.4, 11.2.1
- **gemc_version**: examples: 5.4, 5.7, dev
- **install_dir**: software installation directory.  
  - **local**: /usr/local
  - **cvmfs**: /cvmfs/oasis.opensciencegrid.org/jlab/geant4

<br/>

### Base containers:

**jeffersonlab/base:'ostype'**


### Geant4 containers:

**jeffersonlab/sim:g4v**'geant4_version'**-**'ostype'**-**'install_dir' 


### Gemc containers: 

**jeffersonlab/gemc:**'gemc_version'**-g4v**'geant4_version'**-**'ostype'**-**'install_dir'

<br/>

Examples:

- jeffersonlab/base:fedora36
- jeffersonlab/sim:g4v10.6.2-fedora36-local
- jeffersonlab/gemc:5.4-g4v10.6.2-fedora36-local
- jeffersonlab/sim:g4v10.7.4-ubuntu22-cvmfs
- jeffersonlab/gemc:5.7-g4v10.7.4-ubuntu22-cvmfs
- jeffersonlab/sim:g4v11.2.1-almalinux9-cvmfs


# Build base images:

```
./create_dockerfile.py fedora36
```
