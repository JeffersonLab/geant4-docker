#!/bin/zsh

osnames=(fedora36 almalinux93 ubuntu24)
g4_versions=(10.6.2 10.7.4 11.2.1)
clas12tags_docker_tags=(prod1 dev) # see conventions.py for details
install_dirs=(cvmfs local)

function g4_version_from_clas12tags_version {
	case $1 in
		4.4.2) echo "10.6.2" ;;
		5.7) echo "10.6.2" ;;
		5.8) echo "10.7.4" ;;
	esac
}

function g4_version_from_clas12tags_docker_version {
	case $1 in
		prod1) echo "10.6.2" ;;
		dev) echo "10.7.4" ;;
	esac
}

# base images
echo "\nBase images:\n"
for osname in $osnames; do
	echo "$osname"
	./create_dockerfile.py -i $osname
done

# sim images
echo "\n\nSim images:\n"
for osname in $osnames; do
	for g4_version in $g4_versions; do
		for install_dir in $install_dirs; do
			image_name="g4v$g4_version-$osname-$install_dir"
			echo $image_name
			./create_dockerfile.py -i "$image_name"
		done
	done
done

# clas12tags images
echo "\n\nClas12Tags images:\n"
for osname in $osnames; do
	for cdocker_tag in $clas12tags_docker_tags; do
		for install_dir in $install_dirs; do
			g4_version=$(g4_version_from_clas12tags_docker_version $cdocker_tag)
			image_name="$cdocker_tag-g4v$g4_version-$osname-$install_dir"
			echo "$image_name"
			./create_dockerfile.py -i "$image_name"
		done
	done
done

# base cvmfs images
echo "\n\nBase cvmfs images:\n"
for osname in $osnames; do
		image_name="cvmfs-$osname"
		echo $image_name
		./create_dockerfile.py -i "$image_name"
done

echo "\n\n"
