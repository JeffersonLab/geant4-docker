#!/usr/bin/env python3

import argparse

# Purposes:
# Return from_image, dockerfile, image name, tag


def main():
	desc_str = 'Naming for images, dockerfile, tags'
	example = 'Example: -f fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)

	parser.add_argument('-f', action='store', help='FROM container image based on what to build')

	# optional -a argument
	# parser.add_argument('-a', action='store', help='additional packages')

	parser.add_argument('-d', action='store', help='installation directory')

	args = parser.parse_args()

	# FROM
	if args.f:
		from_label = from_container_image(args.f)
		print(f'FROM Label: {from_label}')


def from_container_image(requested_image, install_dir=None):
	from_image = ''
	if requested_image.count('-') == 0:
		from_image = os_image_from_base_requested(requested_image)
	# sim image, requesting base image
	elif requested_image.count('-') == 2:
		if install_dir:
			from_image = base_image_from_sim_requested(requested_image, install_dir)
		else:
			print('Error: installation directory required')
			exit(1)
	return from_image


def os_image_from_base_requested(requested_image):
	if requested_image == 'fedora36':
		return 'fedora:36'
	elif 'almalinux93' == requested_image:
		return 'almalinux:9.3'
	elif 'ubuntu22' == requested_image:
		return 'ubuntu:22.04'
	else:
		# not supported
		print(f'Error: platform {requested_image} not supported')
		exit(1)


def base_image_from_sim_requested(requested_image, install_dir):
	from_image = 'jeffersonlab/base:'


if __name__ == "__main__":
	main()



