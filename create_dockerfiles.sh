#!/bin/zsh

osnames=(fedora36 almalinux94 ubuntu24)
g4_versions=(10.6.2 10.7.4 11.3.1)
gemc_docker_tags=(prod1 dev)

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
			echo "  > Creating dockerfile for $image_name"
			./create_dockerfile.py -i "$image_name"
	done
done

# gemc images
echo "\n\n > GEMC images:\n"
for osname in $osnames; do
	for gdocker_tag in $gemc_docker_tags; do
			image_name="gemc-$gdocker_tag-$osname"
			echo "  > Creating dockerfile for $image_name"
			./create_dockerfile.py -i "$image_name"
	done
done

echo "\n\n"
