#!/bin/zsh

# this scripts loads the dev containers and packs the package specified by the argument.

# settings
images=(fedora36 almalinux94 ubuntu24)
local_install_dir=/Users/ungaro/mywork
container_install_dir=/usr/local/mywork
remote_images_location=/work/clas12/ungaro/images
cvmfs_dir="/scigroup/cvmfs/geant4"
tar_script=tar_package.sh
possible_packages=(geant4 clas12 clas12Tag gemc noarch)
what_to_pack=$1
image_prefix="dev"  # image to pull.
latest_geant4_version="" # latest geant4 version

printUsage() {
	echo
	echo "Usage: $0 <package>"
	echo
	echo "Possible packages: $possible_packages"
	echo
	echo " - geant4: latest geant4, clhep, xercesc, qt"
	echo " - clas12: ccdb, hipo, clas12_cmag, mlibrary, clas12Tags"
	echo " - clas12Tag: latest clas12Tags only (not dev)"
	echo " - gemc: latest gemc tag only (not dev)"
	echo " - noarch: noarch directory"
	echo
}

higher_version() {

    # if one of the tag is empty, return the other
    if [[ -z $1 ]]; then
		print -r -- "$2"
		return 0
	elif [[ -z $2 ]]; then
		print -r -- "$1"
		return 0
	fi

    # Ensure exactly two arguments are provided
    if (( $# != 2 )); then
        print -u2 "Usage: higher_version <tag1> <tag2>" # Print error to stderr
        return 1 # Indicate failure
    fi

    local tag1=$1
    local tag2=$2
    local tag1_parts tag2_parts
    local i max_parts part1 part2 len1 len2

    # Split tags into parts based on the dot delimiter
    # `${(@s:.:)var}` splits $var on '.' into an array (Zsh specific).
    tag1_parts=( "${(@s:.:)tag1}" )
    tag2_parts=( "${(@s:.:)tag2}" )

    # Determine the number of parts in each tag
    len1=${#tag1_parts[@]}
    len2=${#tag2_parts[@]}

    # Find the maximum number of parts to iterate through
    # This handles cases like comparing "1.2" and "1.2.3"
    # Using Zsh's arithmetic conditional expression
    (( max_parts = len1 > len2 ? len1 : len2 ))

    # Compare parts numerically from left to right (MAJOR.MINOR.PATCH...)
    i=1
    while (( i <= max_parts )); do
        # Get corresponding parts, default to 0 if a tag has fewer parts
        # Example: comparing 1.2 (parts: 1 2) vs 1.2.3 (parts: 1 2 3)
        # When i=3, part1 becomes 0 (from ${tag1_parts[3]:-0}), part2 becomes 3.
        part1=${tag1_parts[i]:-0}
        part2=${tag2_parts[i]:-0}

        # Perform numerical comparison using Zsh's arithmetic evaluation `((...))`
        if (( part1 > part2 )); then
            print -r -- "$tag1" # Use print -r -- for safety with potential weird tag strings
            return 0 # tag1 is higher
        elif (( part2 > part1 )); then
            print -r -- "$tag2"
            return 0 # tag2 is higher
        fi
        # If parts are equal, continue to the next part
        (( i++ ))
    done

    # If the loop completes, all comparable parts were equal.
    # This means the tags are effectively identical (e.g., 1.2 vs 1.2.0)
    # or exactly the same (e.g., 1.2.3 vs 1.2.3).
    # Return the first tag (or second, it doesn't matter in case of equality).
    print -r -- "$tag1"
    return 0
}


# -h option
if [[ $1 = "-h" || $1 == "--h" || $# -lt 1 ]]; then
	printUsage
	exit 0
fi


# if it's geant4, extract the geant4 version from the dockerfule name, after 'g4v' and before '-'
# for example: Dockerfile-g4v11.3.0-fedora36 is 11.3.0, Dockerfile-g4v11.3.1-fedora36 is 11.3.1 (latest
if [[ $what_to_pack = "geant4" ]]; then
	# get the geant4 version from the dockerfile name
	dockerfiles=$(ls dockerfiles/Dockerfile-g4v*-*)
	for dockerfile in $=dockerfiles; do
		# get the version from the dockerfile name
		version=$(echo $dockerfile | sed 's/.*g4v\([0-9]*\.[0-9]*\.[0-9]*\).*/\1/')
		latest_geant4_version=$(higher_version $latest_geant4_version $version)
	done
fi

# if the package is not in the list, exit
if [[ $what_to_pack = "all" ]]; then
	echo "Packing all software"
	what_to_pack=${possible_packages[@]}
elif [[ ! " ${possible_packages[@]} " =~ " ${what_to_pack} " ]]; then
	printUsage
	exit 1
else
	if [[ $what_to_pack != "geant4" ]]; then
		echo "Packing $what_to_pack"
	else
		echo "Packing geant4 $latest_geant4_version"
	fi
fi

cp $tar_script $local_install_dir

# notice image name has 'dev'
for image in $images; do
	package_file_name="$container_install_dir/$image-$what_to_pack.tar.gz"
	rm -f $package_file_name
	docker_image="jeffersonlab/gemc:$image_prefix-$image"
	if [[ $what_to_pack = "geant4" ]]; then
		docker_image="jeffersonlab/geant4:g4v$latest_geant4_version-$image"
	fi
	echo
	echo "------------------------------------"
	echo
	echo "Package: $what_to_pack"
	echo "Using Docker Image: $docker_image"
	echo "Package file name: $package_file_name"
	if [[ $what_to_pack == "geant4" ]]; then
		echo "Geant4 Version: $latest_geant4_version"
	fi

	echo
	docker pull "$docker_image"
	docker run --platform linux/amd64 -it --rm \
		-v $local_install_dir:$container_install_dir \
		"$docker_image" \
		$container_install_dir/$tar_script "$what_to_pack" "$package_file_name"
done

echo
echo "------------------------------------"
echo
echo "To copy the tar file to the host, may have to remove ~/.tcshrc from the cue home then run:"
echo "scp $local_install_dir/*.tar.gz ifarm:$remote_images_location"
echo
echo "To unpack the tar files on ifarm, run:"
echo
echo "cd $cvmfs_dir"
for image in $images; do
	package_file_name="$image-$what_to_pack.tar.gz"
	echo "tar -zxpf $remote_images_location/$package_file_name"
done
echo "\n\n"
