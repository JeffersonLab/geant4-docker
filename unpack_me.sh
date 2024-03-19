#!/bin/zsh

sources_dir="/work/clas12/ungaro"
cvmfs_dir="/scigroup/cvmfs/geant4"

cd $cvmfs_dir

for tar_file in $sources_dir/*.tar.gz; do
	echo "Unpacking $tar_file"
	tar -xzf $tar_file
done