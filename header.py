#!/usr/bin/env python3

import argparse
from conventions import from_image, install_dir_from_image, sim_version_from_image

# Purposes:
# Return commands to satisfy container prerequisites


def main():
	desc_str = 'Header for dockerfile'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='Docker header based on image to build')
	args = parser.parse_args()

	image = args.i

	if image:
		header = container_header(image)
		print(header)


def container_header(image):
	from_label = from_image(image)
	header = f'FROM {from_label} \n'
	header += 'LABEL maintainer="Maurizio Ungaro <ungaro@jlab.org>"\n\n'
	header += '# run shell instead of sh\n'
	header += 'SHELL ["/bin/bash", "-c"]\n\n'

	if 'fedora36' == image:
		header += 'COPY localSetupBase.sh /app/localSetup.sh\n\n'
		header += '# JLab certificate\n'
		header += 'ADD https://pki.jlab.org/JLabCA.crt /etc/pki/ca-trust/source/anchors/JLabCA.crt\n'
		header += 'RUN update-ca-trust\n'

	elif 'almalinux93' == image:
		header += 'COPY localSetupBase.sh /app/localSetup.sh\n\n'
		header += '# JLab certificate\n'
		header += 'ADD https://pki.jlab.org/JLabCA.crt /etc/pki/ca-trust/source/anchors/JLabCA.crt\n'
		header += 'RUN update-ca-trust\n'
		header += '\n'
		header += '# alma specific:\n'
		header += '# crb: for mysql-devel\n'
		header += '# synergy: root, scons, vnc\n'
		header += 'RUN    dnf install -y  \'dnf-command(config-manager)\' \\\n'
		header += '    && dnf config-manager --set-enabled crb \\\n'
		header += '    && dnf install -y almalinux-release-synergy\n'

	elif 'ubuntu22' == image:
		header += 'COPY localSetupBase.sh /app/localSetup.sh\n\n'
		header += '# Update needed at beginning to use the right package repos\n'
		header += 'RUN  apt update\n'
		header += '\n'
		header += '# Install ca-certificates tools\n'
		header += 'RUN apt-get install -y ca-certificates\n'
		header += '\n'
		header += '# JLab certificate\n'
		header += 'ADD https://pki.jlab.org/JLabCA.crt /etc/pki/ca-trust/source/anchors/JLabCA.crt\n'
		header += 'RUN update-ca-certificates\n'

	# sim image
	elif image.startswith('g4v'):
		install_dir = install_dir_from_image(image)
		sim_version = sim_version_from_image(image)
		header += f'ENV SIM_HOME {install_dir}\n'
		header += 'WORKDIR $SIM_HOME\n\n'
		header += 'COPY localSetupSimTemplate.sh $SIM_HOME/localSetup.sh\n'
		header += '\n'
		header += 'RUN sed  -i -e "s|templateSim|$SIM_HOME|g"    $SIM_HOME/localSetup.sh \\\n'
		header += f'    && echo "module load sim/{sim_version}" >> $SIM_HOME/localSetup.sh \\\n'
		header += '    && cp $SIM_HOME/localSetup.sh /app/localSetup.sh \\\n'
		header += '    && cp $SIM_HOME/localSetup.sh /etc/profile.d/localSetup.sh\n'

	header += '\n'

	return header


if __name__ == "__main__":
	main()
