#!/usr/bin/env python3

import argparse
from conventions import from_image, dockerfile_name
from header import container_header
from packages import install_commands

# Purposes:
# Write a dockerfile


def main():
	desc_str = 'Dockerfile creator'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='image to build')
	args = parser.parse_args()

	image = args.i
	from_label = from_image(image) # calling this will make sure the requested image is supported
	dname = dockerfile_name(image)

	create_dockerfile(dname, from_label, image)


def create_dockerfile(dockerfile, from_label, image):

	header = container_header(from_label, image)
	ipackages = install_commands(image)

	# pre-requisites
	with open(dockerfile, 'w') as f:
		f.write(header)
		f.close()

	# packages install
	with open(dockerfile, 'a') as f:
		f.write(ipackages)
		f.close()

if __name__ == "__main__":
	main()



