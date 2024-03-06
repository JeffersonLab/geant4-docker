#!/usr/bin/env python3

import argparse

# Purposes:
# Functions containing naming conventions for images, dockerfiles, tags


def main():
	desc_str = 'Naming for images, dockerfile, tags'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='FROM container image based on what to build')
	args = parser.parse_args()

	image = args.i
	if image:
		osname = osname_from_image(image)
		install_dir = install_dir_from_image(image)
		from_label = from_image(image)
		dockerfile = dockerfile_name(image)
		print()
		print(f'Supported images: {supported_images()}')
		print()
		print(f'OS Name: {osname}')
		print(f'Install Directory: {install_dir}')
		print(f'FROM Label: {from_label}')
		print(f'Dockerfile: {dockerfile}')
		print()

def supported_images():
	return ['fedora36', 'almalinux93', 'ubuntu22']

def from_image(requested_image):
	if requested_image.count('-') == 0:
		return os_imagename_from_base(requested_image)
	# sim image, requesting base image
	elif requested_image.count('-') == 2:
		return base_imagename_from_sim(requested_image)
	# gemc image, requesting sim image
	elif requested_image.count('-') == 3:
		return sim_imagename_from_sim(requested_image)


def os_imagename_from_base(requested_image):
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


def base_imagename_from_sim(requested_image):
	install_dir = install_dir_from_image(requested_image)
	from_image = 'jeffersonlab/base:'
	return from_image


def sim_imagename_from_sim(requested_image):
	install_dir = install_dir_from_image(requested_image)
	from_image = 'jeffersonlab/sim:'
	return from_image


def dockerfile_name(image):
	from_label = from_image(image)
	if image.count('-') == 0:
		return 'dockerfiles/Dockerfile-' + image
	else:
		return 'dockerfiles/Dockerfile-' + from_label


def osname_from_image(requested_image):

	if requested_image.count('-') == 0:
		osname = requested_image
	elif requested_image.count('-') == 2:
		osname = requested_image.split('-')[1]

	# make sure requested image is supported
	if osname not in supported_images():
		print(f'Error: osname {osname} not supported')
		exit(1)

	return osname

def install_dir_from_image(requested_image):
	if requested_image.count('-') == 0:
		return 'system'
	else:
		return requested_image.split('-')[-1]



if __name__ == "__main__":
	main()
