#!/bin/zsh

osnames=(fedora36 almalinux93 ubuntu24)
g4_versions=(10.6.2 10.7.4 11.2.2)

clas12tags_docker_tags=(prod1 dev) # see conventions.py for details
gemc3_docker_tags=(1.3 dev)

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

# base images
echo "\n > Base images:\n"
for osname in $osnames; do
	echo "  > Creating dockerfile for $osname"
	./create_dockerfile.py -i $osname
done


# base cvmfs images
echo "\n\n > Base cvmfs images:\n"
for osname in $osnames; do
	image_name="cvmfs-$osname"
	echo "  > Creating dockerfile for $image_name"
	./create_dockerfile.py -i "$image_name"
done


# geant4 images
echo "\n\n > Geant4 images:\n"
for osname in $osnames; do
	for g4_version in $g4_versions; do
			image_name="g4v$g4_version-$osname"
			echo $image_name
			./create_dockerfile.py -i "$image_name"
	done
done

exit

# gemc images
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


# gemc3 images
echo "\n\nGemc3 images:\n"
last_g4_version=${g4_versions[-1]}
for cdg3_tags in  $gemc3_docker_tags; do
	for osname in $osnames; do
		for install_dir in $install_dirs; do
			image_name="g3v$cdg3_tags-g4v$last_g4_version-$osname-$install_dir"
			echo $image_name
			./create_dockerfile.py -i "$image_name"
		done
	done
done

echo "\n\n"
