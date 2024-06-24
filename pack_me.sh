#!/bin/zsh

image=$1
what_to_pack=$2
export_location="/usr/local/mywork"

function ce_version_from_clas12tags_docker_version {
	if [ "$2" = "gemc" ]; then
		echo $(find ./ -name clas12Tags)
		#		echo $(find ./ -name clas12Tags) $(find ./ -name ccdb | grep -v bin | grep -v lib | grep -v ceInstall | grep -v python)
	elif [ "$2" = "sim" ]; then
		echo $(find ./ -name clhep | head -1) $(find ./ -name geant4 | head -1) $(find ./ -name qt | head -1) $(find ./ -name xercesc | head -1)
	else
		case $1 in
			prod1) echo "1.0" ;;
			dev) echo "1.1" ;;
		esac
	fi
}

# complementary of the above
function ce_version_from_g4v_docker_version {
	if [[ "$2" = "gemc"  || "$what_to_pack" = "all" ]]; then
		echo $(find ./ -name clas12Tags)
	else
		case $1 in
			g4v11.2.2) echo "1.2" ;;
		esac
	fi
}

docker_tag=$(echo "$image" | cut -d'-' -f1)
tar_file="$export_location/$image.tar.gz"
echo
echo
echo "Image: $image"
echo "Docker Tag: $docker_tag"
echo "Tar file: $tar_file"
if  [ "$what_to_pack" = "gemc" ]; then
	echo "Packing Gemc Only"
elif  [ "$what_to_pack" = "sim" ]; then
	echo "Packing Sim Only"
else
	echo "Packing All"
fi

# this conditions will go away when gemc will catch up to g4v versions
if [ "$docker_tag" = "prod1" ] || [ "$docker_tag" = "dev" ]; then
	os_tag=$(echo "$image" | cut -d'-' -f3)
	to_tar="$(ce_version_from_clas12tags_docker_version "$docker_tag" "$what_to_pack")"
else
	os_tag=$(echo "$image" | cut -d'-' -f2)
	to_tar="$(ce_version_from_g4v_docker_version "$docker_tag" "$what_to_pack")"
fi

echo "Os Tag: $os_tag"
echo "To Tar: $to_tar"

cd "$SIM_HOME" || exit
# copying links to the actual files - this to address docker bug
echo
echo Preserving links
echo
find ./ -type l -name "*.so*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type l -name "*.a*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type d -name ".git" -exec rm -rf {} +
echo
echo Done, now tarring...

echo "tar cvfz $tar_file $=to_tar"
tar cvfz "$tar_file" "$=to_tar"

# if docker_tag is dev, tar noarch as well
if [ "$docker_tag" = "dev" ]; then
	tar cvfz noarch.tar.gz noarch
fi
