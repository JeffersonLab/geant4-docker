## TODO:

- create repos for geant4 and clas12 containers, use hub autobuild on those
- test file with reconstruction using osg container

## Base images OSes (ostype)

- [Almalinux94](https://hub.docker.com/_/almalinux)
- [Fedora36](https://hub.docker.com/_/fedora)
- [Ubuntu24](https://hub.docker.com/_/ubuntu)


<br/>

## Base JLAB containers:

**jeffersonlab/base:**[cvmfs-]-**'ostype'**

All base containers have the install directory `/cvmfs/oasis.opensciencegrid.org/jlab/geant4/`.
The 'cvmfs' based container do not have root or other packages needed to compile software 
in order to make them leaner.

TODO: rename the cvmfs container to 'osg'


Examples:

- jeffersonlab/base:fedora36
- jeffersonlab/base:cvmfs-fedora36



### Geant4 JLAB containers:

**jeffersonlab/geant4:g4v'geant4_version'-'ostype'**

where geant4 version is one of the following:

- 10.6.2
- 10.7.4
- 11.3.0
- 11.3.1
- 11.3.2

Examples:

- jeffersonlab/geant4:g4v10.7.4-ubuntu24
- jeffersonlab/geant4:g4v11.3.2-fedora40
- jeffersonlab/geant4:g4v11.3.2-almalinux94

### GEMC JLAB containers: 

**jeffersonlab/gemc:'gemc_version'-'ostype'**

where gemc version is one of the following:

- prod1 (contains 4.4.2)
- dev (contains 5.10, 5.11 and dev)

TODO: once gemc uses meson / geant4, add prod2

---

## Automated builds from docker hub

- source: JeffersonLab/geant4-docker
- source type: branch, main
- You can specify the Dockerfile location as a path relative to the build context. 
- The build context is the path to the files needed for the build, 
  relative to the root of the repository. 
  Enter the path to these files in the Build context field. 
  Enter / to set the build context as the root of the source code repository.

---

## Manual Local Build
```
docker buildx build --platform linux/amd64  --no-cache --progress=plain \
-t jeffersonlab/base:cvmfs-almalinux94 -f dockerfiles/Dockerfile-gemc-dev-almalinux94 .
```

---

# Copy Software to cvmfs

## Linux OSes:

Use the pack.sh script to create a gzipped tarfile with specific software to be copied to cvmfs. 


```
Usage: pack.sh <package>

Possible packages: geant4 clas12 clas12Tag gemc noarch

 - geant4: latest geant4, clhep, xercesc, qt
 - clas12: ccdb, hipo, clas12_cmag, mlibrary, clas12Tags
 - clas12Tag: latest clas12Tags only (not dev)
 - gemc: latest gemc tag only (not dev)
 - noarch: noarch directory
 ```


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
`jeffersonlab/gemc:dev-g4v10.7.4-fedora36`


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
docker pull jeffersonlab/base:cvmfs-almalinux94  
docker tag jeffersonlab/base:cvmfs-almalinux94   jeffersonlab/clas12software:devel
docker push jeffersonlab/clas12software:devel
docker tag jeffersonlab/base:cvmfs-almalinux94   jeffersonlab/clas12software:production
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