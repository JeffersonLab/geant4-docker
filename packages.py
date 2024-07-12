#!/usr/bin/env python3

import argparse
from base_packages import packages_to_be_installed
from cvmfs_packages import packages_to_be_installed as cvmfs_packages_to_be_installed
from conventions import gemc_tags_from_docker_image, is_cvmfs_image, is_fedora_line, is_ubuntu_line, \
	is_sim_image, g4_version_from_image, is_gemc_image, localSetupFilename

# Purposes:
# Return installation commands

cleanup_string_fedora = ' \\\n && dnf -y update \\\n && dnf -y check-update \\\n && dnf clean packages \\\n && dnf clean all \\\n && rm -rf /var/cache/dnf \n'
cleanup_string_ubuntu = ' \\\n && apt-get -y update \\\n && apt-get -y autoclean \n'

def main():
	desc_str = 'Install Packages for dockerfile'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='Docker header based on image to build')
	args = parser.parse_args()

	image = args.i

	if image:
		icommands = packages_install_commands(image)
		print(icommands)


def packages_install_commands(image):
	commands = ''
	packages = packages_to_be_installed(image)
	localSetupFile = localSetupFilename()
	if is_cvmfs_image(image):
		packages = cvmfs_packages_to_be_installed(image)

	if is_fedora_line(image):
		commands += 'RUN dnf install -y --allowerasing '
		commands += packages
		commands += cleanup_string_fedora

	elif is_ubuntu_line(image):
		commands += 'RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \\\n'
		commands += '    && DEBIAN_FRONTEND=noninteractive apt-get  install -y --no-install-recommends tzdata '
		commands += packages
		commands += install_root_from_ubuntu_tarball(localSetupFile)

	# sim image
	elif is_sim_image(image):
		g4_version = g4_version_from_image(image)
		commands += f'RUN source {localSetupFile} \\\n'
		commands += f'           && module load sim_system \\\n'
		commands += f'           && install_geant4 {g4_version} \\\n'
		commands += '            && strip --remove-section=.note.ABI-tag $QTDIR/lib/libQt5Core.so.5\n'

	# gemc image
	elif is_gemc_image(image):
		gemc_tags = gemc_tags_from_docker_image(image)
		commands += f'RUN source {localSetupFile} \\\n'
		for tag in gemc_tags:
			commands += f'           && module load sim_system \\\n'
			commands += f'           && install_gemc {tag} '
			# if not the last item in clas12_tags, add \n
			if tag != gemc_tags[-1]:
				commands += '\\\n'
			else:
				commands += '\n'

	commands += '\n'
	commands += install_meson()
	commands += '\n'
	return commands

def install_root_from_ubuntu_tarball(localSetupFile):
	root_version     = '6.30.04'
	root_file        = f'root_v{root_version}.Linux-ubuntu22.04-x86_64-gcc11.4.tar.gz'
	root_install_dir = '/usr/local'
	commands = '\n'
	commands += '# root installed using tarball\n'
	commands += f'RUN cd {root_install_dir} \\\n'
	commands += f'    && wget https://root.cern/download/{root_file} \\\n'
	commands += f'    && tar -xzvf {root_file} \\\n'
	commands += f'    && rm {root_file} \\\n'
	commands += f'    && echo "cd {root_install_dir}/root/bin ; source thisroot.sh ; cd -" >> {localSetupFile}\n'
	return commands

def install_meson():
	meson_version = '1.5.0'
	meson_location	= f'https://github.com/mesonbuild/meson/releases/download/{meson_version}'
	meson_file	= f'meson-{meson_version}.tar.gz'
	meson_install_dir = '/usr/local'
	commands = '\n'
	commands += '# meson installed using tarball\n'
	commands += f'RUN cd {meson_install_dir} \\\n'
	commands += f'    && wget {meson_location}/{meson_file} \\\n'
	commands += f'    && tar -xzvf {meson_file} \\\n'
	commands += f'    && rm {meson_file} \\\n'
	commands += f'    && ln -s {meson_install_dir}/meson-{meson_version}/meson.py /usr/bin/meson\n'
	return commands


if __name__ == "__main__":
	main()
