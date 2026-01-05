#!/usr/bin/env python3

import argparse

# Purposes:
# return a list of RPM packages for fedora / ubuntu flavors

# Added all root mandatory and optional dependencies from the one liners here: https://root.cern/install/dependencies/
# flexiblas-devel added for mcgen support. not found in ubuntu
# xrootd-client for xrootd
# lsof for tcsh modules
# what was liburing for? asynchronous I/O interface for the Linux kernel

fedora = ''
ubuntu = ''

# c++ essentials
fedora += ' gcc-gfortran pcre-devel mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mariadb-devel sqlite-devel fftw-devel cfitsio-devel graphviz-devel libuuid-devel avahi-compat-libdns_sd-devel openldap-devel python-devel python3-numpy libxml2-devel gsl-devel readline-devel qt5-qtwebengine-devel R-devel R-Rcpp-devel R-RInside-devel xxhash-devel'
ubuntu += ' gfortran libpcre3-dev xlibmesa-glu-dev libglew-dev libftgl-dev libmysqlclient-dev libfftw3-dev libcfitsio-dev graphviz-dev libavahi-compat-libdnssd-dev libldap2-dev python3-dev python3-numpy libxml2-dev libkrb5-dev libgsl0-dev qtwebengine5-dev nlohmann-json3-dev'

# utilities
fedora += ' gcc binutils xrootd-client lsof liburing flexiblas-devel '
ubuntu += ' gcc binutils xrootd-client lsof liburing2 '

# utilities. No 'which' in ubuntu?
fedora += ' bzip2 wget curl nano bash tcsh zsh hostname gedit environment-modules rsync patch which '
ubuntu += ' bzip2 wget curl nano bash tcsh zsh hostname gedit environment-modules rsync patch '

# pelican: only for almalinux
pelican_for_alma = ' pelican pelican-osdf-compat pelican-server htgettoken '

def main():
	desc_str = 'Return list of packages for the requested platform'
	example = 'Example: -p fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-p', action='store', help='list of packages for specific platform')
	args = parser.parse_args()

	platform = args.p
	if platform:
		print(packages_to_be_installed(platform))


def packages_to_be_installed(platform):
	if 'fedora' in platform:
		return fedora
	elif 'almalinux' in platform:
		# remove fluxbox supervisor
		almalinux = fedora.replace('fluxbox supervisor', '')
		almalinux += pelican_for_alma
		return almalinux
		# return fedora
	elif 'ubuntu' in platform:
		return ubuntu
	else:
		return 'Error: platform not supported'
		exit(1)

if __name__ == "__main__":
	main()
