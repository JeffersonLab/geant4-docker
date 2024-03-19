#!/bin/zsh

image=$1
export_location="/usr/local/mywork"

function ce_version_from_clas12tags_docker_version {
	case $1 in
		prod1) echo "1.0" ;;
		dev) echo "1.1" ;;
	esac
}

# complementary of the above
function ce_version_from_g4v_docker_version {
	case $1 in
		g4v11.2.1) echo "1.2" ;;
	esac
}

docker_tag=$(echo "$image" | cut -d'-' -f1)
tar_file="$export_location/$image.tar.gz"
echo "Image: $image"
echo "Docker Tag: $docker_tag"
echo "Tar file: $tar_file"

# this conditions will go away when gemc will catch up to g4v versions
if [ "$docker_tag" = "prod1" ] || [ "$docker_tag" = "dev" ]; then
	os_tag=$(echo "$image" | cut -d'-' -f3)
	to_tar="$(ce_version_from_clas12tags_docker_version "$docker_tag")"
else
	os_tag=$(echo "$image" | cut -d'-' -f2)
	to_tar="$(ce_version_from_g4v_docker_version "$docker_tag")"
fi

echo "Os Tag: $os_tag"
echo "To Tar: $to_tar"

cd "$SIM_HOME" || exit
find ./ -type l -name "*.so*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type l -name "*.a*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type d -name ".git" -exec rm -rf {} +

tar cvfz "$tar_file" "$to_tar"

# if docker_tag is dev, tar noarch as well
if [ "$docker_tag" = "dev" ]; then
	tar cvfz noarch.tar.gz noarch
fi

echo
echo "To copy the tar file to the host, run:"
echo "cd $export_location"
echo "scp *.tar.gz unpack_me.sh ifarm:/work/clas12/ungaro "
