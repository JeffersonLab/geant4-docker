#!/bin/bash

# Returns a random background hipo file in the selected configuration
# example of command line:
# bg_merge_bk_file.sh rgk_fall2018_FTOff tor+1.00_sol-1.00 60nA_6535MeV get
# this script can be tested on cue machines
# exit codes defined in Submit documentation repo

# pelican usage:

# ls: pelican object ls osdf:///jlab-osdf/clas12/osgpool/backgroundfiles/rga_fall2018/tor+1.00_sol-1.00/40nA_10604MeV/10k/00095.hipo



configuration=$1
fields=$2
bkmerging=$3
getit=$4

pelican_path="osdf:///jlab-osdf/clas12/osgpool/"
xdir="$pelican_path/backgroundfiles/"$configuration"/"$fields"/"$bkmerging"/10k"


NFILES=$(pelican object ls $xdir | wc | awk '{print $1}')
if [[ $NFILES -eq 0 ]]; then
    echo "wrong NFILES: " $NFILES " not found. exiting"
    exit 221
fi


# works only if > 100 files
nzeros="00"

R=$(( $RANDOM % $NFILES + 1))
if [[ ! $? -eq 0 ]]; then
        echo "bg_merge_bk_file.sh: RANDOM Number not valid: " $R
        exit 223
fi

if (($R < 10))
then
	nzeros="0000"
elif (($R < 100))
then
	nzeros="000"
fi

bgfile="$xdir/"$nzeros$R".hipo"
if [[ ! $? -eq 0 ]]; then
        echo "bg_merge_bk_file.sh: " $bgfile does not exist
        exit 223
fi

echo $bgfile

if [ "$#" == 4 ]; then
	if [ $getit == "get" ]; then
		pelican object get "$bgfile" . 
		exit $?
	fi
fi


exit 0

