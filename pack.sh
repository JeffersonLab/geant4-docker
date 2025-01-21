#!/bin/zsh

# this scripts loads the dev containers and install the package specified by the argument.
# if 'all' is specified, then all packages are installed

containers=(fedora36 almalinux94 ubuntu24)
#containers=(almalinux94)

local_install_dir=/Users/ungaro/mywork
container_install_dir=/usr/local/mywork/
remote_images_location=/work/clas12/ungaro/images
cvmfs_dir="/scigroup/cvmfs/geant4"
pack_file=tar_package.sh

possible_packages=(ccdb clas12Tags clas12_cmag clhep evio geant4 gemc hipo mlibrary qt xercesc)

function printUsage {
	echo
	echo "Usage: $0 <package>"
	echo "Possible packages: $possible_packages"
	echo "To pack all packages, use 'all'"
	echo "If no package is specified, clas12Tags is assumed"
	echo
}

# -h option
if [[ $1 = "-h" || $1 == "--h" ]]; then
	printUsage
	exit 0
fi

# we must have at least one argument, the package to install
# exit if no packages or the package is not in the list
if [[ $# -lt 1 ]]; then
	what_to_pack=clas12Tags
else
	what_to_pack=$1
fi

# if the package is not in the list, exit
if [[ $what_to_pack = "all" ]]; then
	echo "Packing all software"
elif [[ ! " ${possible_packages[@]} " =~ " ${what_to_pack} " ]]; then
	printUsage
	exit 1
fi

cp $pack_file $local_install_dir

for container in $containers; do
	image="dev-$container"
	package_file_name="$container_install_dir/$image-$what_to_pack.tar.gz"
	rm -f $package_file_name
	docker_image="jeffersonlab/gemc:$image"
	echo
	echo "------------------------------------"
	echo
	echo "Package: $what_to_pack"
	echo "Docker Image: $docker_image"
	echo "Package file: $package_file_name"
	echo
	docker pull "$docker_image"
	docker run --platform linux/amd64 -it --rm -v $local_install_dir:$container_install_dir "$docker_image" \
		$container_install_dir/$pack_file "$what_to_pack" "$package_file_name"
done

echo
echo "------------------------------------"
echo
echo "To copy the tar file to the host, may have to remove ~/.tcshrc from the cue home then run:"
echo "scp $local_install_dir/*.tar.gz ifarm:$remote_images_location"
echo
echo "Also, copy noarch when needed:"
echo "scp -r /opt/jlab_software/noarch ifarm:$remote_images_location"
echo
echo "To unpack the tar files on ifarm, run:"
echo "tar -zxpvf $remote_images_location/$package_file_name"
echo
echo " and copy the interested content to $cvmfs_dir"
echo "\n\n"
