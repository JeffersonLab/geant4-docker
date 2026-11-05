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




Base packages:


Below is a concise explanation of each AlmaLinux package, including its primary purpose. Most packages ending in `-devel` provide header files and libraries needed to compile software, rather than just run it.

| Package                        | Description                                                                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gcc-gfortran`                 | GNU Fortran compiler. Used to compile Fortran programs, particularly scientific and numerical applications.                                                               |
| `pcre-devel`                   | Development files for Perl Compatible Regular Expressions (PCRE). Used for pattern matching and text processing.                                                          |
| `mesa-libGL-devel`             | Development files for Mesa's OpenGL library. Used to compile applications requiring 2D/3D graphics rendering.                                                             |
| `mesa-libGLU-devel`            | Development files for the OpenGL Utility Library (GLU). Provides higher-level graphics functions built on OpenGL.                                                         |
| `glew-devel`                   | OpenGL Extension Wrangler Library. Simplifies accessing modern OpenGL functions and extensions.                                                                           |
| `ftgl-devel`                   | Font rendering library using FreeType and OpenGL. Enables rendering TrueType and OpenType fonts in OpenGL applications.                                                   |
| `mariadb-devel`                | Development headers and libraries for MariaDB/MySQL database connectivity. Used to compile database clients.                                                              |
| `sqlite-devel`                 | Development files for SQLite, a lightweight, embedded SQL database engine.                                                                                                |
| `fftw-devel`                   | Fastest Fourier Transform in the West. Optimized library for computing discrete Fourier transforms, commonly used in scientific computing.                                |
| `cfitsio-devel`                | Development files for CFITSIO. Library for reading and writing FITS (Flexible Image Transport System) files, widely used in astronomy.                                    |
| `graphviz-devel`               | Development libraries for Graphviz. Used to generate and manipulate graph and network visualizations.                                                                     |
| `libuuid-devel`                | Development files for generating and manipulating Universally Unique Identifiers (UUIDs).                                                                                 |
| `avahi-compat-libdns_sd-devel` | Compatibility library implementing Apple's DNS Service Discovery API through Avahi. Used for discovering network services via mDNS/DNS-SD.                                |
| `openldap-devel`               | Development files for LDAP client libraries. Used to build software that communicates with directory services, including authentication systems.                          |
| `python-devel`                 | Development headers and libraries for compiling native Python extensions. Python version depends on the AlmaLinux release.                                                |
| `python3-numpy`                | NumPy numerical computing library for Python 3. Provides efficient multidimensional arrays and mathematical operations.                                                   |
| `libxml2-devel`                | Development files for libxml2. Used for parsing, validating, and manipulating XML documents.                                                                              |
| `gsl-devel`                    | GNU Scientific Library development files. Provides numerical algorithms for statistics, optimization, integration, linear algebra, and more.                              |
| `readline-devel`               | Development files for GNU Readline. Provides command-line editing, history, and interactive input functionality.                                                          |
| `qt5-qtwebengine-devel`        | Development files for Qt WebEngine. Allows Qt applications to embed Chromium-based web browsing functionality.                                                            |
| `R-devel`                      | Development files for the R statistical computing language. Used to compile R extensions and packages containing native code.                                             |
| `R-Rcpp-devel`                 | Development files for Rcpp. Enables integration of C++ code with R and simplifies writing R extensions in C++.                                                            |
| `R-RInside-devel`              | Development files for RInside. Allows C++ applications to embed and execute an R interpreter.                                                                             |
| `xxhash-devel`                 | Development files for xxHash. Extremely fast, noncryptographic hashing library, useful for checksums and data integrity verification.                                     |
| `tbb-devel`                    | Intel oneTBB (Threading Building Blocks) development files. Provides C++ libraries for task-based parallelism and multithreaded applications.                             |
| `gcc`                          | GNU Compiler Collection, primarily providing the C compiler. Essential for building C applications and native libraries.                                                  |
| `binutils`                     | GNU binary utilities, including the assembler (`as`), linker (`ld`), and tools such as `nm`, `objdump`, and `readelf`.                                                    |
| `xrootd-client`                | Client tools for XRootD, a high-performance distributed data access system commonly used in high-energy physics. Includes utilities for remote file access and transfers. |
| `lsof`                         | Lists open files, sockets, and other resources held by running processes. Useful for debugging and system administration.                                                 |
| `liburing`                     | Userspace library for Linux `io_uring`, enabling efficient asynchronous I/O operations with reduced system-call overhead.                                                 |
| `flexiblas-devel`              | Development files for FlexiBLAS. Provides a flexible interface to BLAS/LAPACK numerical libraries, allowing the underlying implementation to be selected or switched.     |

## Grouped by functionality

For an AlmaLinux container, these packages fall into several categories:

| Category                           | Packages                                                                                                                 |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Compilers and build tools          | `gcc`, `gcc-gfortran`, `binutils`, `python-devel`                                                                        |
| Scientific and numerical computing | `fftw-devel`, `gsl-devel`, `flexiblas-devel`, `tbb-devel`, `R-devel`, `R-Rcpp-devel`, `R-RInside-devel`, `python3-numpy` |
| Graphics and visualization         | `mesa-libGL-devel`, `mesa-libGLU-devel`, `glew-devel`, `ftgl-devel`, `graphviz-devel`, `qt5-qtwebengine-devel`           |
| Database connectivity              | `mariadb-devel`, `sqlite-devel`                                                                                          |
| Data formats and processing        | `cfitsio-devel`, `libxml2-devel`, `pcre-devel`, `xxhash-devel`, `libuuid-devel`                                          |
| Networking and distributed data    | `avahi-compat-libdns_sd-devel`, `openldap-devel`, `xrootd-client`                                                        |
| System utilities and I/O           | `lsof`, `liburing`, `readline-devel`                                                                                     |


## Considerations for AlmaLinux containers

A few points are particularly relevant if you're building a scientific computing container:

- Build-time vs. runtime dependencies: Most `-devel` packages are only necessary when compiling applications. You can often omit them from a final runtime image using a multistage container build.
- Repository availability: Some packages, particularly `R-RInside-devel`, `ftgl-devel`, `qt5-qtwebengine-devel`, and `xrootd-client`, may require EPEL or other additional repositories, depending on your AlmaLinux version.
- Headless environments: OpenGL and Qt development packages do not necessarily require an X server during compilation. However, running GUI applications or rendering graphics may require additional runtime libraries or a virtual display.
- BLAS performance: `flexiblas-devel` allows software to use different BLAS backends, such as OpenBLAS, which can significantly affect numerical performance.
- Python version: Check what `python-devel` resolves to in your AlmaLinux release. If your application requires a particular Python version, use the corresponding version-specific development package where available.

Practical recommendation: If your container is intended to compile a scientific software stack (for example, ROOT or other high-energy physics applications), most of these dependencies are reasonable. If it will only execute precompiled applications, the package list can likely be reduced substantially.