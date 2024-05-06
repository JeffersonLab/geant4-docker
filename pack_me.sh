#!/bin/zsh

image=$1
gemc_only=$2
export_location="/usr/local/mywork"

function ce_version_from_clas12tags_docker_version {
	if [ "$2" = "yes" ]; then
		echo $(find ./ -name clas12Tags)
	else
		case $1 in
			prod1) echo "1.0" ;;
			dev) echo "1.1" ;;
		esac
	fi
}

# complementary of the above
function ce_version_from_g4v_docker_version {
	if [ "$2" = "yes" ]; then
		echo $(find ./ -name clas12Tags)
	else
		case $1 in
			g4v11.2.1) echo "1.2" ;;
		esac
	fi
}

docker_tag=$(echo "$image" | cut -d'-' -f1)
tar_file="$export_location/$image.tar.gz"
echo "Image: $image"
echo "Docker Tag: $docker_tag"
echo "Tar file: $tar_file"
if  [ "$gemc_only" = "yes" ]; then
	echo "Packing Gemc Only"
fi

# this conditions will go away when gemc will catch up to g4v versions
if [ "$docker_tag" = "prod1" ] || [ "$docker_tag" = "dev" ]; then
	os_tag=$(echo "$image" | cut -d'-' -f3)
	to_tar="$(ce_version_from_clas12tags_docker_version "$docker_tag" "$gemc_only")"
else
	os_tag=$(echo "$image" | cut -d'-' -f2)
	to_tar="$(ce_version_from_g4v_docker_version "$docker_tag" "$gemc_only")"
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
echo Done, now tarring.

tar cvfz "$tar_file" "$to_tar"

# if docker_tag is dev, tar noarch as well
if [ "$docker_tag" = "dev" ]; then
	tar cvfz noarch.tar.gz noarch
fi

