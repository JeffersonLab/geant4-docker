#!/bin/zsh

# script to be run inside the container and tar the desired files

source /etc/profile.d/localSetup.sh

package_filename=$2
osrelease=$(basename $SIM_HOME)

if [[ $1 != "all" ]]; then
	what_to_pack=$osrelease/$1
else
	what_to_pack=$osrelease
fi

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
rm -f $package_filename
echo "  >> Docker Done, now tarring $what_to_pack to $package_filename..."
tar cfz $package_filename "$what_to_pack"
echo
echo "  >> Docker Done!"

