#!/usr/bin/env python3

import argparse
from conventions import dockerfile_name
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

	# fluxbox
	with open(dockerfile, 'a') as f:
		f.write(ifluxbox)


if __name__ == "__main__":
	main()
