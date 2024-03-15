#!/bin/zsh

image=$1

available_c12_docker_tags=("prod1" "dev")

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

cd "$SIM_HOME" || exit

docker_tag=$(echo "$image" | cut -d'-' -f1)
echo "Docker Tag: $docker_tag"

# if docker_tag is in available_c12_docker_tags, then os_tag is the third field, otherwise it is the second field
for c12_docker_tag in $available_c12_docker_tags; do
	if [ "$docker_tag" = "$c12_docker_tag" ]; then
		os_tag=$(echo "$image" | cut -d'-' -f3)
		to_tar="$(ce_version_from_clas12tags_docker_version "$docker_tag")"
		# exit loop, found the tag
		break
	else
		os_tag=$(echo "$image" | cut -d'-' -f2)
		to_tar="$(ce_version_from_g4v_docker_version "$docker_tag")"
		# exit loop, found the tag
		break
	fi
done

tar_file="/usr/local/mywork/$image.tar.gz"

echo "Image: $image"
echo "Os Tag: $os_tag"
echo "Tar file: $tar_file"
echo "To Tar: $to_tar"

find ./ -type l -name "*.so*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type l -name "*.a*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type d -name ".git" -exec rm -rf {} +

tar cvfz "$tar_file" "$to_tar"

# if docker_tag is dev, tar noarch as well
if [ "$docker_tag" = "dev" ]; then
	tar cvfz noarch.tar.gz noarch
fi
