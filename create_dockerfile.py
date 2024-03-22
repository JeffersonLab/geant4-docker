#!/usr/bin/env python3

import argparse
from conventions import dockerfile_name, supported_osnames, supported_cvmfs_osnames
from header import container_header
from packages import install_commands
from fluxbox import fluxbox_install_commands


# Purposes:
# Write a dockerfile


def main():
	desc_str = 'Dockerfile creator'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='image to build')
	args = parser.parse_args()

	image = args.i
	create_dockerfile(image)


def create_dockerfile(image):
	dockerfile = dockerfile_name(image)
	header = container_header(image)
	ipackages = install_commands(image)
	ifluxbox = fluxbox_install_commands(image)

	# pre-requisites
	with open(dockerfile, 'w') as f:
		f.write(header)
		f.close()

	# packages install
	with open(dockerfile, 'a') as f:
		f.write(ipackages)
		f.close()

	# fluxbox - only if image is in supported_images
	if image in supported_osnames() or image in supported_cvmfs_osnames():
		with open(dockerfile, 'a') as f:
			f.write(ifluxbox)
			f.close()



if __name__ == "__main__":
	main()
