#!/usr/bin/env python3

import argparse
from base_packages import packages_to_be_installed
from cvmfs_packages import packages_to_be_installed as cvmfs_packages_to_be_installed
from conventions import *


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
	if is_base_container(image):
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

		commands += '\n'
		commands += install_meson()

	# geant4 image
	elif is_geant4_image(image):
		commands += install_ceInstall()
		commands += f'RUN source {localSetupFile} \\\n'
		commands += f'    && module use {modules_path()} \\\n'
		commands += f'    && module load sim_system \\\n'
		g4version = g4_version_from_image(image)
		# if g4version is 11.*, uninstall qt5-qtbase-devel qt5-linguist and install the qt6 versions
		if g4version.startswith('11.'):
			if is_fedora_line(image):
				commands += '    && dnf remove -y qt5-qtbase-devel qt5-linguist \\\n'
				commands += '    && dnf install -y qt6-qtbase-devel qt6-linguist \\\n'
			elif is_ubuntu_line(image):
				commands += '    && apt-get remove -y libqt5widgets5 libqt5opengl5-dev libqt5printsupport5 \\\n'
				commands += '    && apt-get install -y qt6-base-dev libqt6opengl6t64 libqt6openglwidgets6t64 \\\n'
		commands += f'    && install_geant4 {g4version} \n\n'

	# gemc image
	elif is_gemc_image(image):
		#additional_packages='maven jq perl-DBI assimp-devel tetgen-devel'
		additional_packages='maven jq perl-DBI perl-DBD-SQLite perl-XML-LibXML'
		if is_ubuntu_line(image):
			additional_packages = 'maven jq libdbi-perl unzip libdbd-sqlite3-perl libxml-libxml-simple-perl'
		#additional_packages = 'maven jq perl-DBI assimp-dev libtetgen-dev'
		gemc_tags = gemc_tags_from_docker_image(image)
		commands += update_ceInstall()
		if 'dev' in gemc_tags:
			commands += install_coatjava_dependencies(additional_packages, image)
		commands += f'RUN source {localSetupFile} \\\n'
		commands += f'    && module use {modules_path()} \\\n'
		commands += f'    && module load sim_system \\\n'
		for tag in gemc_tags:
			commands += f'    && install_gemc {tag} '
			# if not the last item in clas12_tags, add \n
			if tag != gemc_tags[-1]:
				commands += '\\\n'
			else:
				commands += '\n'

	commands += '\n'
	return commands

def install_root_from_ubuntu_tarball(localSetupFile):
	root_version     = '6.32.02'
	ubuntu_os_name   = 'ubuntu24.04-x86_64-gcc13.2'
	root_file        = f'root_v{root_version}.Linux-{ubuntu_os_name}.tar.gz'
	root_remote_file = f'https://root.cern/download/{root_file}'
	root_install_dir = '/usr/local'
	commands = '\n'
	commands += '# root installation using tarball\n'
	commands += f'RUN cd {root_install_dir} \\\n'
	commands += f'    && {curl_command({root_remote_file})}  \\\n'
	commands += f'    && tar -xzvf {root_file} \\\n'
	commands += f'    && rm {root_file} \\\n'
	commands += f'    && echo "cd {root_install_dir}/root/bin ; source thisroot.sh ; cd -" >> {localSetupFile}\n'
	return commands

def install_meson():
	meson_version = '1.9.0'
	meson_location	= f'https://github.com/mesonbuild/meson/releases/download/{meson_version}'
	meson_file	= f'meson-{meson_version}.tar.gz'
	meson_remote_file = f'{meson_location}/{meson_file}'
	meson_install_dir = '/usr/local'
	commands = '\n'
	commands += '# meson installation using tarball\n'
	commands += f'RUN cd {meson_install_dir} \\\n'
	commands += f'    && {curl_command({meson_remote_file})}  \\\n'
	commands += f'    && tar -xzvf {meson_file} \\\n'
	commands += f'    && rm {meson_file} \\\n'
	commands += f'    && ln -s {meson_install_dir}/meson-{meson_version}/meson.py /usr/bin/meson\n'
	return commands

def install_ceInstall():
	modulebasepath=modules_path_base_dir()
	modulesubdir='geant4'
	commands = '# ceInstall installation  \n'
	commands += f'RUN mkdir -p {modulebasepath} \\\n'
	commands += f'    && cd {modulebasepath} \\\n'
	commands += f'    && git clone https://github.com/JeffersonLab/ceInstall {modulesubdir}  \n\n'
	return commands

def update_ceInstall():
	modulepath=modules_path()
	commands = '# ceInstall update  \n'
	commands += f'RUN cd {modulepath} \\\n'
	commands += f'    &&  git pull  \n\n'
	return commands


# install maven, jq, perl-DBI, and install groovy from
# https://groovy.jfrog.io/artifactory/dist-release-local/groovy-zips/
# Version 4.0.26
# For example: https://groovy.jfrog.io/artifactory/dist-release-local/groovy-zips/apache-groovy-binary-4.0.26.zip
def install_coatjava_dependencies(additional_packages, image):
	commands = '\n'
	commands += '# coatjava dependencies installation using tarball\n'
	if is_fedora_line(image):
		commands += f'RUN dnf install -y --allowerasing {additional_packages} \\\n'

	elif is_ubuntu_line(image):
		commands += 'RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \\\n'
		commands += f'    && DEBIAN_FRONTEND=noninteractive apt-get  install -y --no-install-recommends tzdata {additional_packages} \\\n'
	commands += '    && curl -L -O https://groovy.jfrog.io/artifactory/dist-release-local/groovy-zips/apache-groovy-binary-4.0.26.zip \\\n'
	commands += '    && unzip apache-groovy-binary-4.0.26.zip \\\n'
	commands += '    && rm apache-groovy-binary-4.0.26.zip \\\n'
	commands += '    && mv groovy-4.0.26 /usr/local/groovy \\\n'
	commands += '    && ln -s /usr/local/groovy/bin/groovy /usr/bin/groovy \n\n'
	return commands


if __name__ == "__main__":
	main()
