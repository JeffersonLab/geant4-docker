#!/bin/zsh

#osnames=(almalinux93 )
osnames=(fedora36 almalinux93 ubuntu24)
osnames=(fedora36 almalinux93)
osnames=(ubuntu24)
g4_versions_not_in_clas12=()
g4_versions_not_in_clas12=(11.2.2)
clas12tags_docker_tags=(dev) # see conventions.py for details
clas12tags_docker_tags=(prod1 dev) # see conventions.py for details
local_install_dir=/Users/ungaro/mywork
container_install_dir=/usr/local/mywork/
remote_images_location=/work/clas12/ungaro/images

install_dirs=(cvmfs)

what_to_pack="all"
if [ $1 = "gemc" ]; then
	what_to_pack="gemc"
elif  [ $1 = "sim" ]; then
	what_to_pack="sim"
fi

function g4_version_from_clas12tags_version {
	case $1 in
		4.4.2) echo "10.6.2" ;;
		5.9) echo "10.6.2" ;;
		5.10) echo "10.7.4" ;;
	esac
}

function g4_version_from_clas12tags_docker_version {
	case $1 in
		prod1) echo "10.6.2" ;;
		dev) echo "10.7.4" ;;
	esac
}

function do_the_deed {
	image_name=$1
	gemc_or_sim=$2
	remote_image_name="jeffersonlab/$gemc_or_sim:$image_name"
	echo "$image_name  remote: $remote_image_name"
	# docker pull "$remote_image_name"
	cp ./pack_me.sh unpack_me.sh $local_install_dir
	docker run --platform linux/amd64 -it --rm -v $local_install_dir:$container_install_dir "$remote_image_name" $container_install_dir/pack_me.sh "$image_name" "$what_to_pack"
}

# clas12tags images
if [[ "$what_to_pack" = "gemc" || "$what_to_pack" = "all" ]]; then
	echo "\n\nClas12Tags images:\n"
	for osname in $=osnames; do
		for cdocker_tag in $clas12tags_docker_tags; do
			for install_dir in $install_dirs; do
				g4_version=$(g4_version_from_clas12tags_docker_version "$cdocker_tag")
				image_name="$cdocker_tag-g4v$g4_version-$osname-$install_dir"
				# if image_name contains ubuntu, skip it
				if [[ $image_name == *"ubuntu"* ]]; then
					echo "Skipping $image_name"
					continue
				fi
				do_the_deed "$image_name" "gemc"
			done
		done
	done
fi

# remaining g4 versions - only if NOT gemc only
if [[ "$what_to_pack" = "sim" || "$what_to_pack" = "all" ]]; then
	echo "\n\nRemaining g4 versions:\n"
	for osname in $=osnames; do
		for g4_version in $=g4_versions_not_in_clas12; do
			for install_dir in $=install_dirs; do
				image_name="g4v$g4_version-$osname-$install_dir"
				do_the_deed "$image_name" "sim"
			done
		done
	done
fi

echo
echo "To copy the tar file to the host, may have to remove .tcshrc from jlab then run:"
echo "rm ~/.tcshrc"
echo "cd $local_install_dir"
echo "scp *.tar.gz unpack_me.sh ifarm:/work/clas12/ungaro/images"
echo
echo "To unpack the tar files on ifarm, run:"
echo "$remote_images_location/unpack_me.sh"
echo "\n\n"
