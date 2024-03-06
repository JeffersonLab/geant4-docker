#!/bin/zsh


osnames=(fedora36 almalinux93 ubuntu22)

for osname in $osnames; do
  echo "$osname"
   ./create_dockerfile.py -i $osname
done