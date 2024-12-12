#!/bin/zsh

# not automatic on all OSes
source /etc/profile.d/localSetup.sh

osrelease=$1
what_to_pack=$2
remote_image_name=$3
osname=$(echo $osrelease | cut -d'-' -f1)
image_tag=$(echo $remote_image_name | cut -d':' -f2)

export_location="/usr/local/mywork"
work_dir="/cvmfs/oasis.opensciencegrid.org/jlab/geant4/"

function dirs_to_tar {
	cd "$work_dir" || exit
	if [ "$what_to_pack" = "gemc" ]; then
		echo $(find ./ -name clas12Tags | grep -v bin) $(find ./ -name gemc | grep -v modules | grep -v bin)
		# echo $(find ./ -name clas12Tags) $(find ./ -name ccdb | grep -v bin | grep -v lib | grep -v ceInstall | grep -v python)
	else
		echo $(modules/util/osrelease.py)
	fi
}


tar_file="$export_location/$image_tag.tar.gz"
to_tar="$(dirs_to_tar)"
echo
echo
echo " > osrelease: $osrelease"
echo " > osname: $osname"
echo " > Tar destination: $tar_file"
echo " > To Tar (from osrelease.py: $to_tar"
echo " > Work dir: $work_dir"


# copying links to the actual files - this to address docker bug
cd "$work_dir" || exit
echo
echo " > Preserving links"
find ./ -type l -name "*.so*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i";  done' sh {} +
find ./ -type l -name "*.a*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i";   done' sh {} +
find ./ -type d -name ".git" -exec rm -rf {} +
SIZE=$(du -sk $=to_tar | cut -f 1)
echo " > Done, now tarring with: tar cfz $tar_file $=to_tar from $(pwd), size: $SIZE k"
tar cfz "$tar_file" "$=to_tar"
echo
echo " > done with osrelease: $osrelease"

# once pv is installed:
#tar cfz - "$=to_tar" | pv -p -s ${SIZE}k > $tar_file
