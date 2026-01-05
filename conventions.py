#!/usr/bin/env python3
import argparse

# Purposes:
# Functions containing naming conventions for images, dockerfiles, tags

def supported_osnames():
	return ['fedora36', 'almalinux94', 'ubuntu24', 'fedora40']


def supported_cvmfs_osnames():
	return [f'cvmfs-{osname}' for osname in supported_osnames()]


def supported_geant4_versions():
	return ['10.6.2', '10.7.4', '11.3.0']


def modules_path_base_dir():
	return '/cvmfs/oasis.opensciencegrid.org/jlab'


def modules_path():
	return modules_path_base_dir() + '/geant4/modules'


def localSetupFilename():
	return '/etc/profile.d/localSetup.sh'


def dockerfile_name(image):
	return 'dockerfiles/Dockerfile-' + image


def is_base_container(image):
	if image in supported_osnames() or image in supported_cvmfs_osnames():
		return True
	return False


def is_fedora_line(image):
	if 'fedora' in image or 'almalinux' in image:
		return True
	return False


def is_alma_line(image):
	if 'almalinux' in image:
		return True
	return False


def is_ubuntu_line(image):
	if 'ubuntu' in image:
		return True
	return False


def is_cvmfs_image(image):
	if image.startswith('cvmfs'):
		return True
	return False


def is_geant4_image(image):
	if 'g4v' in image:
		return True
	return False


def is_gemc_image(image):
	if 'gemc' in image:
		return True
	return False


def jlab_certificate():
	return "/etc/pki/ca-trust/source/anchors/JLabCA.crt"


# execute system curl command to download file
# notice: both the cacert and the -k option are given here. For some reason the cacert option
# was not enough on fedora line OSes
# see also https://curl.se/docs/sslcerts.html
def curl_command(filename):
	return f'curl -S --location-trusted --progress-bar --retry 4 --cacert {jlab_certificate()} {filename} -k -O'

def from_image(requested_image):
	if requested_image.count('-') == 0 or 'cvmfs' in requested_image:
		return os_base_image_from_imagename(requested_image)
	# sim image, requesting base image
	elif is_geant4_image(requested_image):
		return base_imagename_from_sim(requested_image)
	# gemc image, requesting sim image
	elif is_gemc_image(requested_image):
		return geant4_imagename_from_gemc(requested_image)


def os_base_image_from_imagename(requested_image):
	if 'fedora36' in requested_image:
		return 'fedora:36'
	elif 'fedora40' in requested_image:
		return 'fedora:40'
	elif 'almalinux94' in requested_image:
		return 'almalinux:9.4'
	elif 'ubuntu24' in requested_image:
		return 'ubuntu:24.04'
	else:
		# not supported
		print(f'Error: platform {requested_image} base image not supported')
		exit(1)


import logging

def base_imagename_from_sim(requested_image):
	logger = logging.getLogger(__name__)

	for osname in supported_osnames():
		if osname in requested_image:
			from_image = 'jeffersonlab/base:' + osname
			return from_image

	logger.debug(
		f"No matching OS found in '{requested_image}'. Supported OS names: {supported_osnames()}")
	return None  # or raise an exception, or return a default image


def geant4_imagename_from_gemc(requested_image):
	from_image = 'jeffersonlab/geant4:g4v' + g4_version_from_image(
		requested_image) + '-' + osname_from_image(requested_image)
	return from_image


def osname_from_image(requested_image):
	if is_base_container(requested_image):
		return requested_image
	elif is_cvmfs_image(requested_image):
		return requested_image.split('-')[1]
	elif is_geant4_image(requested_image):
		return requested_image.split('-')[1]
	elif is_gemc_image(requested_image):
		return requested_image.split('-')[2]
	else:
		print(f'Error: osname {requested_image} not supported')
		exit(1)


def g4_version_from_image(requested_image):
	# return the string between 'g4v' and '-'
	if 'g4v' in requested_image:
		return requested_image.split('g4v')[1].split('-')[0]
	elif 'gemc' in requested_image:
		gtag = requested_image.split('-')[1]
		if gtag == 'prod1':
			return '10.6.2'
		elif gtag == 'dev':
			return '10.7.4'
		else:
			print(f'g4_version_from_image error: tag {gtag} not supported for {requested_image}')
			exit(1)
	else:
		print(f'Error: geant4 version not found in {requested_image}')
		exit(1)


# as of july 2024:
# prod1: gemc versions 4.4.2
# dev:   gemc versions 5.10, dev
def gemc_tags_from_docker_image(image):
	gtag = image.split('-')[1]
	if gtag == 'prod1':
		return ['4.4.2']
	elif gtag == 'dev':
		return ['5.11', '5.12', 'dev']
	else:
		print(f'gemc_tags_from_docker_image error: tag {gtag} not supported')
		exit(1)


def main():
	desc_str = 'Naming for images, dockerfile, tags'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='FROM container image based on what to build')
	args = parser.parse_args()

	image = args.i
	if image:
		osname = osname_from_image(image)
		modulespath = modules_path()
		from_label = from_image(image)
		dockerfile = dockerfile_name(image)
		g4_version = g4_version_from_image(image)
		gemc_tags = gemc_tags_from_docker_image(image)
		print()
		print(f'Supported images:\t {supported_osnames()}')
		print(f'Supported cvmfs images:\t {supported_cvmfs_osnames()}')
		if image.split('-')[0] != 'cvmfs':
			print(f'Supported geant4 versions:\t {supported_geant4_versions()}')
		print()
		print(f'OS Name: {osname}')
		print(f'Modules Directory: {modulespath}')
		print(f'FROM Label: {from_label}')
		print(f'Dockerfile: {dockerfile}')
		print()
		if g4_version != 'na':
			print(f'Geant4 Version: {g4_version}')
		if gemc_tags:
			print(f'clas12 tags:\t\t {gemc_tags}')
		print()


if __name__ == "__main__":
	main()
