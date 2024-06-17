#!/usr/bin/env python3

import argparse
from base_packages import packages_to_be_installed
from cvmfs_packages import packages_to_be_installed as cvmfs_packages_to_be_installed
from conventions import sim_version_from_image, clas12_tags_from_docker_tag

# Purposes:
# Return installation commands

cleanup_string_fedora = ' \\\n  && dnf -y update \\\n  && dnf -y check-update \\\n  && dnf clean packages \\\n  && dnf clean all \\\n  && rm -rf /var/cache/dnf \n'
cleanup_string_ubuntu = ' \\\n  && apt-get -y update \\\n  && apt-get -y autoclean \n'

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
	if 'cvmfs-fedora36' == image:
		packages = cvmfs_packages_to_be_installed('fedora36')
	elif 'cvmfs-almalinux93' == image:
		packages = cvmfs_packages_to_be_installed('almalinux93')
	elif 'cvmfs-ubuntu24' == image:
		packages = cvmfs_packages_to_be_installed('ubuntu24')

	if 'fedora36' == image or 'cvmfs-fedora36' == image:
		commands += 'RUN dnf install -y '
		commands += packages
		commands += cleanup_string_fedora

	elif 'almalinux93' == image or 'cvmfs-almalinux93' == image:
		commands += 'RUN dnf install -y --allowerasing '
		commands += packages
		commands += cleanup_string_fedora

	elif 'ubuntu24' == image or 'cvmfs-ubuntu24' == image:
		commands += 'RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \\\n'
		commands += '    && DEBIAN_FRONTEND=noninteractive apt-get  install -y --no-install-recommends tzdata '
		commands += cleanup_string_ubuntu
		commands += install_root_from_ubuntu_tarball()

	# sim image
	elif image.startswith('g4v'):
		sim_version = sim_version_from_image(image)
		commands += 'RUN source /app/localSetup.sh \\\n'
		commands += f'           && install_sim {sim_version} \\\n'
		commands += '            && strip --remove-section=.note.ABI-tag $QTDIR/lib/libQt5Core.so.5\n'

	# gemc3 image
	elif image.startswith('g3v'):
		g3_tag = image.split('-')[0].split('g3v')[1]
		commands += 'RUN source /app/localSetup.sh \\\n'
		commands += f'           && module switch gemc3/{g3_tag} \\\n'
		commands += f'           && install_gemc3 {g3_tag} '
		commands += '\n'

	# gemc image containing clas12_tags
	elif image.count('-') == 3:
		clas12_tags = clas12_tags_from_docker_tag(image)
		commands += 'RUN source /app/localSetup.sh \\\n'
		for tag in clas12_tags:
			commands += f'           && module switch gemc/{tag} \\\n'
			commands += f'           && install_gemc {tag} '
			# if not the last item in clas12_tags, add \n
			if tag != clas12_tags[-1]:
				commands += '\\\n'
			else:
				commands += '\n'

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
