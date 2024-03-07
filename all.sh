#!/bin/zsh

osnames=(fedora36 almalinux93 ubuntu22)
g4_versions=(10.6.2 10.7.4 11.2.1)
clas12tags_versions=(4.4.2 5.7 5.8)
install_dirs=(cvmfs local)

function g4_version_from_clas12tags_version {
	case $1 in
		4.4.2) echo "10.6.2" ;;
		5.7) echo "10.6.2" ;;
		5.8) echo "10.7.4" ;;
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
			echo "g4v$g4_version-$osname-$install_dir"
			./create_dockerfile.py -i "g4v$g4_version-$osname-$install_dir"
		done
	done
done

# clas12tags images
echo "\n\nClas12Tags images:\n"
for osname in $osnames; do
	for clas12tags_version in $clas12tags_versions; do
		for install_dir in $install_dirs; do
			g4_version=$(g4_version_from_clas12tags_version $clas12tags_version)
			echo "$clas12tags_version-g4v$g4_version-$osname-$install_dir"
			# ./create_dockerfile.py -i "clas12tags$clas12tags_version-$osname-$install_dir"
		done
	done
done

echo "\n\n"
