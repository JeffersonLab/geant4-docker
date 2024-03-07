#!/bin/zsh


osnames=(fedora36 almalinux93 ubuntu22)
g4_versions=(10.6.2 10.7.4 11.2.1)
install_dirs=(cvmfs local)

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
	#  ./create_dockerfile.py -i $osname -g $g4_version -d $install_dir
	done
  done
done

echo "\n\n"
