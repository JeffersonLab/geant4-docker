#!/usr/bin/env python3

import argparse
from base_packages import packages_to_be_installed

# Purposes:
# Return installation commands


def main():
	desc_str = 'Install Packages for dockerfile'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='Docker header based on image to build')
	args = parser.parse_args()

	image = args.i

	if image:
		icommands = install_commands(image)
		print(icommands)


def install_commands(image):

	commands = '\n'
	packages = packages_to_be_installed(image)

	if 'fedora36' == image:
		commands += 'RUN dnf install -y '
		commands += packages
		commands += '\\\n'
		commands += '   && dnf -y update \\\n'
		commands += '   && dnf -y check-update \\\n'
		commands += '   && dnf clean packages \\\n'
		commands += '   && dnf clean all \\\n'
		commands += '   && rm -rf /var/cache/yum \\\n'
		commands += '   && ln -s /usr/bin/cmake3 /usr/local/bin/cmake\n'


	elif 'almalinux93' == image:
		commands += 'RUN dnf install -y --allowerasing '
		commands += packages
		commands += '\\\n'
		commands += '   && dnf -y update \\\n'
		commands += '   && dnf -y check-update \\\n'
		commands += '   && dnf clean packages \\\n'
		commands += '   && dnf clean all \\\n'
		commands += '   && rm -rf /var/cache/yum \\\n'
		commands += '   && ln -s /usr/bin/cmake3 /usr/local/bin/cmake\n'

	elif 'ubuntu22' == image:
		commands += 'RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \\\n'
		commands += '    && DEBIAN_FRONTEND=noninteractive apt-get  install -y --no-install-recommends tzdata '
		commands += packages
		commands += '\\\n'
		commands += '   && apt-get -y update \\\n'
		commands += '   && apt-get -y autoclean\n'
		commands += install_root_from_ubuntu_tarball()


	commands += '\n'
	return commands


def install_root_from_ubuntu_tarball():
	commands = '\n'
	commands += '# root installed using tarball\n'
	commands += 'ENV ROOT_RELEASE=6.30.04\n'
	commands += 'ENV ROOT_FILE=root_v${ROOT_RELEASE}.Linux-ubuntu22.04-x86_64-gcc11.4.tar.gz\n'
	commands += 'ENV ROOT_INSTALL_DIR=/usr/local\n'
	commands += 'RUN cd ${ROOT_INSTALL_DIR} \\\n'
	commands += '    && wget https://root.cern/download/${ROOT_FILE} \\\n'
	commands += '    && tar -xzvf ${ROOT_FILE} \\\n'
	commands += '    && rm ${ROOT_FILE} \\\n'
	commands += '    && echo "cd ${ROOT_INSTALL_DIR}/root ; source bin/thisroot.sh ; cd -" >> /etc/profile.d/root.sh\n'
	return commands


if __name__ == "__main__":
	main()
