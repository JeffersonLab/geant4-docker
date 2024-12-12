# geant4-docker

Docker files for geant4 installation

## Base images OS:

- [Almalinux93](https://hub.docker.com/_/almalinux)
- [Fedora36](https://hub.docker.com/_/fedora)
- [Ubuntu](https://hub.docker.com/_/ubuntu)

## Naming and Tags Conventions

- **ostype**: fedora36, ubuntu24, almalinux9
- **geant4_version**: examples: 10.6.2, 10.7.4, 11.3.0
- **gemc_version**: examples: 4.4.2, 5.7, dev
- **install_dir**: software installation directory label. 
  It corresponds to the following paths: 
  - **local**: /usr/local
  - **cvmfs**: /cvmfs/oasis.opensciencegrid.org/jlab/geant4

<br/>

### Base containers:

**jeffersonlab/base:**[cvmfs-]'ostype'


### Geant4 containers:

**jeffersonlab/sim:g4v**'geant4_version'**-**'ostype'**-**'install_dir' 


### Gemc containers: 

**jeffersonlab/gemc:**'gemc_version'**-g4v**'geant4_version'**-**'ostype'**-**'install_dir'

<br/>

Examples:

- jeffersonlab/base:fedora36
- jeffersonlab/sim:g4v10.6.2-fedora36-local
- jeffersonlab/sim:g4v10.7.4-ubuntu24-cvmfs
- jeffersonlab/sim:g4v11.3.0-almalinux9-cvmfs
- jeffersonlab/gemc:prod1-fedora36-local
- jeffersonlab/gemc:dev-ubuntu24-cvmfs


## Automated builds from docker hub

- source: JeffersonLab/geant4-docker
- source type: branch, main
- You can specify the Dockerfile location as a path relative to the build context. 
- The build context is the path to the files needed for the build, 
  relative to the root of the repository. 
  Enter the path to these files in the Build context field. 
  Enter / to set the build context as the root of the source code repository.

---

## Copy images to cvmfs

## Linux OSes:

Use the pack_all.sh script to copy the images to cvmfs. 
The option 'gemc' will only pack the clas12Tag directory as opposed 
to all the libraries.

- **pack_all.sh**
- **pack_all.sh gemc**




## MacOS:

Manually tar the files. Make sure tar is an alias to gtar or use gtar directly.
```
cd /opt/jlab_software
gtar  cvfz 1.1-macos.tar.gz 1.1
mv 1.1-macos.tar.gz ~/mywork
scp *.tar.gz ifarm:/work/clas12/ungaro/images  
```


## Container for clas12-validation and clas12Tags actions

- Currently used: `jeffersonlab/gemc:dev-fedora36` which is an autobuild based on
`jeffersonlab/gemc:dev-g4v10.7.4-fedora36-cvmfs`



---

## Release for OSG:

First make a tag of the current version:
```
docker pull  jeffersonlab/clas12software:production
docker tag jeffersonlab/clas12software:production jeffersonlab/clas12software:tag_sept_24
docker push jeffersonlab/clas12software:tag_sept_24
```

Then make a new tag for the new version:

Almalinux:

```
docker pull jeffersonlab/base:cvmfs-almalinux93  
docker tag jeffersonlab/base:cvmfs-almalinux93   jeffersonlab/clas12software:devel
docker push jeffersonlab/clas12software:devel
docker tag jeffersonlab/base:cvmfs-almalinux93   jeffersonlab/clas12software:production
docker push jeffersonlab/clas12software:production
```

Fedora:

```
docker pull jeffersonlab/base:cvmfs-fedora36  
docker tag jeffersonlab/base:cvmfs-fedora36   jeffersonlab/clas12software:devel
docker push jeffersonlab/clas12software:devel
docker tag jeffersonlab/base:cvmfs-fedora36   jeffersonlab/clas12software:production
docker push jeffersonlab/clas12software:production
```


After testing, can use the tag `production`.

## Testing with docker container:

```
docker_run_image jeffersonlab/clas12software:devel cvmfs
```

### Test script:

```
source /etc/profile.d/modules.csh
set cvmfsPath = /cvmfs/oasis.opensciencegrid.org/jlab/hallb/clas12/sw/
set cvmfsSetupFile = $cvmfsPath/setup.csh
source $cvmfsSetupFile $cvmfsPath
module load sqlite/5.7
setenv SIM_HOME /cvmfs/oasis.opensciencegrid.org/jlab/geant4
source /cvmfs/oasis.opensciencegrid.org/jlab/geant4/ceInstall/setup.csh
module load gemc/5.9
setenv RCDB_CONNECTION mysql://null

module avail
module load coatjava/10.0.2
module load jdk/17.0.2
module load mcgen/3.02

generate-seeds.py generate
set seed = `generate-seeds.py read --row 1`
clasdis --trig 100 --docker --t 20 25 --seed $seed
gemc -USE_GUI=0 -N=100 /cvmfs/oasis.opensciencegrid.org/jlab/hallb/clas12/sw/noarch/clas12-config/dev/gemc/5.7/rga_fall2018_target_at_m3.5.gcard  -INPUT_GEN_FILE='lund, clasdis.dat'   -RANDOMIZE_LUND_VZ='-3.0*cm, 2.5*cm, reset '  -BEAM_SPOT='0.0*mm, 0.0*mm, 0.0*mm, 0.0*mm, 0*deg, reset '          -RASTER_VERTEX='0.0*cm, 0.0*cm, reset '       -SCALE_FIELD='binary_torus,    +1.00'   -SCALE_FIELD='binary_solenoid, -1.00'   -OUTPUT='hipo, gemc.hipo'   -INTEGRATEDRAW='*'   | sed '/G4Exception-START/,/G4Exception-END/d'  
$DRIFTCHAMBERS/install/bin/denoise2.exe  -i gemc.hipo -o gemc_denoised.hipo -t 1 -n $DRIFTCHAMBERS/denoising/code/network/cnn_autoenc_0f_112.json 
recon-util -y /cvmfs/oasis.opensciencegrid.org/jlab/hallb/clas12/sw/noarch/clas12-config/dev/coatjava/10.0.2/rga_fall2018_target_at_m3.5.yaml -i gemc_denoised.hipo -o recon.hipo
echo
ls -l
```

## Testing with apptainer

```
module load singularity
singularity shell  --bind /cvmfs --contain --ipc --pid --cleanenv /cvmfs/singularity.opensciencegrid.org/jeffersonlab/clas12software:devel
singularity shell --home ${PWD}:/srv --pwd /srv --bind /cvmfs --contain --ipc --pid --cleanenv /cvmfs/singularity.opensciencegrid.org/jeffersonlab/clas12software:devel
```