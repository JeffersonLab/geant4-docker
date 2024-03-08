#!/bin/zsh

file=/usr/local/mywork/$1

function ce_version_from_clas12tags_docker_version {
	case $1 in
		prod1) echo "1.0" ;;
		dev) echo "1.1" ;;
	esac
}

cd $SIM_HOME

docker_tag=$(echo $file | cut -d'-' -f1)
os_tag=$(echo $file | cut -d'-' -f3)
to_tar="$os_tag/$(ce_version_from_clas12tags_docker_version $docker_tag)"

echo "Tar file: $file"
echo "To Tar: $to_tar"

find ./ -type l  -name "*.so*" -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type l  -name "*.a*"  -exec sh -c 'for i in "$@"; do cp --preserve --remove-destination "$(readlink -f "$i")" "$i"; echo $i; done' sh {} +
find ./ -type d -name ".git" -exec rm -rf {} +

tar cvfz $file $to_tar
