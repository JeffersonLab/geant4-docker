#!/usr/bin/env python3

import argparse


# Purposes:
# Functions containing naming conventions for images, dockerfiles, tags


def supported_images():
	return ['fedora36', 'almalinux93', 'ubuntu22']


def supported_geant4_versions():
	return ['10.6.2', '10.7.4', '11.2.1']


def supported_gemc_versions():
	return ['4.4.2', '5.7', '5.8']


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
		print(f'Supported images:\t\t {supported_images()}')
		print(f'Supported geant4 versions:\t {supported_geant4_versions()}')
		print(f'Supported gemc versions:\t {supported_gemc_versions()}')
		print()
		print(f'OS Name: {osname}')
		print(f'Install Directory: {install_dir}')
		print(f'FROM Label: {from_label}')
		print(f'Dockerfile: {dockerfile}')
		print()


def from_image(requested_image):
	if requested_image.count('-') == 0:
		return os_imagename_from_base(requested_image)
	# sim image, requesting base image
	elif requested_image.count('-') == 2:
		return base_imagename_from_sim(requested_image)
	# gemc image, requesting sim image
	elif requested_image.count('-') == 3:
		return sim_imagename_from_gemc(requested_image)


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
	osname = osname_from_image(requested_image)
	from_image = 'jeffersonlab/base:' + osname
	return from_image


def sim_imagename_from_gemc(requested_image):
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
	else:
		osname = requested_image.split('-')[2]

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


def g4_version_from_image(requested_image):
	g4_version = ''
	if requested_image.count('-') == 2:
		g4_version = requested_image.split('-')[0]
	elif requested_image.count('-') == 3:
		g4_version = requested_image.split('-')[1]
	else:
		print(f'Error: osname {requested_image}\'s geant4 not supported')
		exit(1)

	# make sure requested geant4 version is supported
	g4_version = g4_version[3:]
	if g4_version not in supported_geant4_versions():
		print(f'Error: geant4 version {g4_version} not supported')
		exit(1)

	return g4_version


def sim_version_from_g4_version(g4_version):
	if g4_version == '10.6.2':
		return '1.0'
	elif g4_version == '10.7.4':
		return '1.1'
	elif g4_version == '11.2.1':
		return '1.2'


if __name__ == "__main__":
	main()
