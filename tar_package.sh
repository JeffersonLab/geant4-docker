#!/bin/zsh

# script to be run inside the container and tar the desired files

source /etc/profile.d/localSetup.sh
osrelease=$(basename $SIM_HOME)

possible_packages=(geant4 clas12 clas12Tag gemc noarch)
geant4_packages=(clhep xercesc geant4)
clas12_packages=(clhep xercesc qt geant4 ccdb hipo clas12_cmag mlibrary clas12Tags)

# what_to_pack is an array of items
what_to_pack=""
if [[ $1 = "geant4" ]]; then
	for i in ${geant4_packages[@]}; do
		what_to_pack="$what_to_pack $osrelease/$i"
	done
elif [[ $1 = "clas12" ]]; then
	for i in ${clas12_packages[@]}; do
		what_to_pack="$what_to_pack $osrelease/$i"
	done
elif [[ $1 = "clas12Tag" ]]; then
	# only pack last clas12Tag, not dev
	latest_clas12Tag=$(ls -1 $SIM_HOME/clas12Tags | grep -v dev | sort -V | tail -n 1)
	what_to_pack="$osrelease/clas12Tags/$latest_clas12Tag"
elif [[ $1 = "gemc" ]]; then
	# only pack last gemc
	latest_gemc=$(ls -1 $SIM_HOME/gemc | sort -V | tail -n 1)
	what_to_pack="$osrelease/gemc/$latest_gemc"
elif [[ $1 = "noarch" ]]; then
	what_to_pack="noarch"
else
	echo "Unknown package: $1"
	echo "Possible packages: $possible_packages"
	exit 1
fi

package_filename=$2

echo
echo "  >> Docker Tar destination: $package_filename"
echo "  >> Docker To pack: $what_to_pack"
echo


echo
echo "  >> Docker Preserving links..."
cd $SIM_HOME/..
find ./ -type l -name "*.so*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i";  done' sh {} +
find ./ -type l -name "*.a*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i";   done' sh {} +
find ./ -type d -name ".git" -exec rm -rf {} +
find ./ -type f -name "*.tgz" -exec rm -rf {} +
find ./ -type f -name "*.tar.gz" -exec rm -rf {} +
rm -f $package_filename
echo "  >> Docker Done, now tarring:\n      - $=what_to_pack\n     to $package_filename..."
echo "  >> Current dir: $(pwd) content:\n$(ls -l)"
tar cfz $package_filename $=what_to_pack
echo
echo "  >> Docker Done!"

