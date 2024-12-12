#!/bin/zsh

#osreleases=(fedora36-gcc12 almalinux94-gcc11 ubuntu24-gcc13)
osreleases=(almalinux94-gcc11)
tags=(prod1 dev)
tags=(dev)
g4versions=(11.3.0)

local_install_dir=/Users/ungaro/mywork
container_install_dir=/usr/local/mywork/

remote_images_location=/work/clas12/ungaro/images

what_to_pack=$1


function do_the_deed {
	osrelease=$1
	osname=$(echo $osreleases | cut -d'-' -f1)
	what_to_pack=$2
	tag=$3

	# if it's gemc tag:
	if [[ $what_to_pack = "gemc" ]]; then
		image_tag="gemc-$tag-$osname"
		remote_image_name="jeffersonlab/gemc:$image_tag"
	elif [[ $what_to_pack = "geant4" ]]; then
		image_tag="g4v$tag-$osname"
		remote_image_name="jeffersonlab/geant4:$image_tag"
	fi

	echo " > Osrelease: $osrelease"
	echo " > Image tag: $image_tag"
	echo " > Remote image: $remote_image_name"
	docker pull "$remote_image_name"
	cp ./pack_me.sh unpack_me.sh $local_install_dir
	docker run --platform linux/amd64 -it --rm -v $local_install_dir:$container_install_dir "$remote_image_name" $container_install_dir/pack_me.sh "$osrelease" "$what_to_pack" "$remote_image_name"
}

if [[ $what_to_pack = "gemc" ]]; then
	echo "\n gemc docker images:\n"
	for osrelease in $=osreleases; do
		for tag in $=tags; do
			do_the_deed "$osrelease" gemc "$tag"
		done
	done
elif [[ $what_to_pack = "geant4" ]]; then
	echo "\n geant4 docker images:\n"
	for osrelease in $=osreleases; do
		for g4version in $=g4versions; do
			do_the_deed "$osrelease" geant4 "$g4version"
		done
	done
fi

echo
echo "------------------------------------"
echo
echo "To copy the tar file to the host, may have to remove .tcshrc from jlab then run:"
echo "rm ~/.tcshrc"
echo "cd $local_install_dir"
echo "scp *.tar.gz unpack_me.sh ifarm:/work/clas12/ungaro/images"
echo
echo "Also, copy noarch when needed:"
echo "scp -r /opt/jlab_software/noarch ifarm:/work/clas12/ungaro/images"
echo
echo "To unpack the tar files on ifarm, run:"
echo "$remote_images_location/unpack_me.sh"
echo "\n\n"
