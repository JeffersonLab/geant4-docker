#!/usr/bin/env python3

import argparse
from conventions import from_image, modules_path, modules_path_base_dir, g4_version_from_image, localSetupFilename, \
	gemc_tags_from_docker_image, is_sim_image, is_base_container, is_fedora_line, is_alma_line, is_ubuntu_line, is_cvmfs_image

# Purposes:
# Return commands to satisfy container prerequisites

def copy_files(image):
	copy_string = ''
	if is_base_container(image):
		copy_string += 'COPY bgMerginFilename.sh /bin/bgMerginFilename.sh\n'
		copy_string += 'COPY localSetupBase.sh /app/localSetup.sh\n\n'
	elif is_sim_image():
		copy_string += 'COPY localSetupSimTemplate.sh /app/localSetup.sh\n\n'
	return copy_string

def load_jlab_certificate(image):
	certificate_string = ''
	if is_base_container(image):
		if is_fedora_line(image):
			certificate_string += '# JLab certificate\n'
			certificate_string += 'ADD https://pki.jlab.org/JLabCA.crt /etc/pki/ca-trust/source/anchors/JLabCA.crt\n'
			certificate_string += 'RUN update-ca-trust \n\n'
			if is_alma_line(image):
				certificate_string += '# alma specific:\n'
				certificate_string += '# crb: for mysql-devel\n'
				certificate_string += '# synergy: root, scons, vnc\n'
				certificate_string += 'RUN    dnf install -y  \'dnf-command(config-manager)\' \\\n'
				certificate_string += '    && dnf config-manager --set-enabled crb \\\n'
				certificate_string += '    && dnf install -y almalinux-release-synergy \n\n'
		elif is_ubuntu_line(image):
			certificate_string += '# Update needed at beginning to use the right package repos\n'
			certificate_string += 'RUN  apt update\n'
			certificate_string += '\n'
			certificate_string += '# Install ca-certificates tools\n'
			certificate_string += 'RUN apt-get install -y ca-certificates\n'
			certificate_string += '\n'
			certificate_string += '# JLab certificate\n'
			certificate_string += 'ADD https://pki.jlab.org/JLabCA.crt /etc/pki/ca-trust/source/anchors/JLabCA.crt\n'
			certificate_string += 'RUN update-ca-certificates \n\n'
	return  certificate_string

def main():
	desc_str = 'Header for dockerfile'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='Docker header based on image to build')
	args = parser.parse_args()

	image = args.i

	if image:
		header = create_dockerfile_header(image)
		print(header)

def create_dockerfile_header(image):
	from_label = from_image(image)
	localSetup = localSetupFilename()
	header = f'FROM {from_label} \n'
	header += 'LABEL maintainer="Maurizio Ungaro <ungaro@jlab.org>"\n\n'
	header += '# run shell instead of sh\n'
	header += 'SHELL ["/bin/bash", "-c"]\n'
	header += 'ENV AUTOBUILD 1\n\n'
	header += copy_files(image)
	header += load_jlab_certificate(image)
	modulespath = modules_path()
	if is_cvmfs_image(image) or is_sim_image(image):
		header += f'RUN echo "module use {modules_path}" >> {localSetup} \n'
	if is_sim_image(image):
		modules_path_base = modules_path_base_dir(image)
		header += f'RUN sed  -i -e "s|install_dir_module_path_template|{modules_path_base}|g" {localSetup} \\\n'
		g4_version = g4_version_from_image(image)
		header += f'    && echo "module load geant4/{g4_version}" >> {localSetup} \\\n'
	header += '\n'

	return header


if __name__ == "__main__":
	main()
