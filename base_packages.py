#!/usr/bin/env python3

import argparse

# Purposes:
# return a list of RPM packages for fedora / ubuntu flavors

fedora = ''
ubuntu = ''

# c++ essentials
fedora += ' git make cmake gcc-c++'
ubuntu += ' git make cmake g++'

# expat
fedora += ' expat-devel'
ubuntu += ' expat libexpat1-dev'

# sql
fedora += ' mariadb-devel sqlite-devel'        # mariadb-devel provides mysql_config and libmysqlclient
ubuntu += ' libmysqlclient-dev libsqlite3-dev' # in ubuntu line mysq_config is not given by mariadb.

# python
fedora += ' python3-devel python3-scons ninja-build'
ubuntu += ' python3-dev scons ninja-build'

# x11
fedora += ' mesa-libGLU-devel libX11-devel libXpm-devel libXft-devel '
ubuntu += ' libglu1-mesa-dev  libx11-dev   libxpm-dev   libxft-dev   '
fedora += ' libXt-devel libXmu-devel libXrender-devel  xorg-x11-server-Xvfb xrandr '
ubuntu += ' libxt-dev   libxmu-dev   libxrender-dev    xvfb                 x11-xserver-utils'

# utilities. No 'which' in ubuntu?
fedora += ' bzip2 wget curl nano bash tcsh zsh hostname gedit environment-modules pv which'
ubuntu += ' bzip2 wget curl nano bash tcsh zsh hostname gedit environment-modules pv'

# more utilities
fedora += ' psmisc procps mailcap net-tools rsync patch'
ubuntu += ' psmisc procps mailcap net-tools rsync patch'

# even more utilities
fedora += ' perl-CPAN glibc-langpack-en'
ubuntu += ' libcpandb-perl'

# xterm
fedora += ' xterm'
ubuntu += ' xterm'

# vnc
fedora += ' x11vnc novnc'
ubuntu += ' x11vnc novnc'

# fluxbox
fedora += ' fluxbox supervisor'
ubuntu += ' fluxbox supervisor'

# qt5
fedora += ' qt5-qtbase-devel qt5-linguist'
ubuntu += ' libqt5widgets5 libqt5opengl5-dev libqt5printsupport5'

# meson comes installed from source.  ninja
fedora += ' ninja-build'
ubuntu += ' ninja-build'

# root not on ubuntu
fedora += ' root'

# AddressSanitizer: libasan; UndefinedBehaviorSanitizer: libubsan; MemorySanitizer: libmsan; ThreadSanitizer: libtsan
fedora += ' liblsan  libasan  libubsan  libtsan  tbb'
ubuntu += ' liblsan0 libasan8 libubsan1 libtsan2 libtbb12'

# doxygen. This is quite big, perhaps we need a dedicated container w/o all the previous stuff
fedora += ' doxygen'
ubuntu += ' doxygen'

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
	# if platform contain fedora, return fedora
	# if platform contain ubuntu, return ubuntu
	# if platform contain almalinux, return almalinux
	# else return error
	if 'fedora' in platform:
		return fedora
	elif 'ubuntu' in platform:
		return ubuntu
	elif 'almalinux' in platform:
		# remove fluxbox supervisor
		almalinux = fedora.replace('fluxbox supervisor', '')
		return almalinux
	else:
		return 'Error: platform not supported'
		exit(1)

if __name__ == "__main__":
	main()
