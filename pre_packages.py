#!/usr/bin/env python3

import argparse

# Purposes:
# Return from_image, dockerfile, image name, tag


def main():
	# Provides the -h, --help message
	desc_str = "   Naming for images, dockerfile, tags\n"
	parser = argparse.ArgumentParser(description=desc_str)

	parser.add_argument('-f', action='store', help='FROM container image based on what to build')
	parser.add_argument('-d', action='store', help='installation directory')

	args = parser.parse_args()

	# FROM
	if args.f:
		from_image = from_container_image(args.f)
		print(f'FROM: {from_container_image(args.f, args.d)}')



def from_container_image(requested_image, install_dir):

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
	elif requested_image == 'almalinux93':
		return 'almalinux:9.3'
	elif requested_image == 'ubuntu22':
		return 'ubuntu:22.04'
	else:
		# not supported
		print(f'Error: platform {requested_image} not supported')
		exit(1)


def base_image_from_sim_requested(requested_image, install_dir):
	from_image = 'jeffersonlab/base:'



if __name__ == "__main__":
	main()



