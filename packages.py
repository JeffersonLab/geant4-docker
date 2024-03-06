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
		commands += '    && dnf -y update \\\n'
		commands += '	&& dnf -y check-update \\\n'
		commands += '	&& dnf clean packages \\\n'
		commands += '	&& dnf clean all \\\n'
		commands += '	&& rm -rf /var/cache/yum \\\n'
		commands += '	&& ln -s /usr/bin/cmake3 /usr/local/bin/cmake\n'


	elif 'almalinux93' == image:
		commands += 'RUN dnf install -y --allowerasing '
		commands += packages
		commands += '\\\n'
		commands += '	&& apt  update \\\n'
		commands += '	&& dnf -y check-update \\\n'
		commands += '	&& dnf clean packages \\\n'
		commands += '	&& dnf clean all \\\n'
		commands += '	&& rm -rf /var/cache/yum \\\n'
		commands += '	&& ln -s /usr/bin/cmake3 /usr/local/bin/cmake\n'

	elif 'ubuntu22' == image:
		commands += 'RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \\\n'
		commands += '    && DEBIAN_FRONTEND=noninteractive apt  install -y --no-install-recommends tzdata '
		commands += packages
		commands += '\\\n'
		commands += '	&& apt  update \\\n'
		commands += '	&& apt  autoclean\n'


	commands += '\n'
	return commands


if __name__ == "__main__":
	main()
