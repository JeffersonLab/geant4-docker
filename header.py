#!/usr/bin/env python3

import argparse
from image_name import from_container_image

# Purposes:
# Return from_image, dockerfile, image name, tag


def main():
	desc_str = 'Header for dockerfile'
	example = 'Example: -p fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)

	parser.add_argument('-i', action='store', help='Docker header based on image to build')

	args = parser.parse_args()
	image = args.i
	from_container_image(image)

	if image:
		header = container_header(image)
		print(header)


def container_header(image):

	header = '\n'
	if image == 'fedora36':
		header += '# JLab certificate\n'

	elif image == 'almalinux93':
		header += '# JLab certificate\n'

	elif image == 'ubuntu22':
		header += '# Update needed at beginning to use the right package repos\n'
		header += 'RUN apt-get install -y ca-certificates\n'

	return header


if __name__ == "__main__":
	main()
