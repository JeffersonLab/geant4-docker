#!/usr/bin/env python3

import argparse


# Purposes:
# Functions containing naming conventions for images, dockerfiles, tags


def supported_osnames():
	return ['fedora36', 'almalinux93', 'ubuntu24']

def supported_cvmfs_osnames():
	return ['cvmfs-fedora36', 'cvmfs-almalinux93', 'cvmfs-ubuntu24']


def supported_geant4_versions():
	return ['10.6.2', '10.7.4', '11.2.1']


# as of march 2024:
# prod 1 has gemc versions 4.4.2, 5.7
# dev has gemc versions 5.8, dev
def clas12_tags_from_docker_tag(image):
	if image.count('-') == 3:
		tag = image.split('-')[0]

		if tag == 'prod1':
			return ['4.4.2', '5.7']
		elif tag == 'dev':
			return ['5.8', 'dev']
		else:
			print(f'Error: tag {tag} not supported')
			exit(1)
	else:
		return []


def install_dir_path_from_label(label):
	if label == 'local':
		return '/usr/local'
	elif label == 'cvmfs':
		return '/cvmfs/oasis.opensciencegrid.org/jlab/geant4'
	else:
		print(f'Error: install directory {label} not supported')
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
		install_dir = install_dir_from_image(image)
		from_label = from_image(image)
		dockerfile = dockerfile_name(image)
		g4_version = g4_version_from_image(image)
		sim_version = sim_version_from_image(image)
		clas12_tags = clas12_tags_from_docker_tag(image)
		print()
		print(f'Supported images:\t\t {supported_osnames()}')
		if image.split('-')[0] != 'cvmfs':
			print(f'Supported geant4 versions:\t {supported_geant4_versions()}')
		print()
		print(f'OS Name: {osname}')
		print(f'Install Directory: {install_dir}')
		print(f'FROM Label: {from_label}')
		print(f'Dockerfile: {dockerfile}')
		print()
		if g4_version != 'na':
			print(f'Geant4 Version: {g4_version}')
		if sim_version != 'na':
			print(f'Sim Version: {sim_version}')
		if clas12_tags:
			print(f'clas12 tags:\t\t {clas12_tags}')
		print()


def from_image(requested_image):
	if requested_image.count('-') == 0:
		return os_imagename_from_base(requested_image)
	elif requested_image.count('-') == 1:
		return os_imagename_from_base(requested_image)
	# sim image, requesting base image
	elif requested_image.count('-') == 2:
		return base_imagename_from_sim(requested_image)
	# gemc image, requesting sim image
	elif requested_image.count('-') == 3:
		return sim_imagename_from_gemc(requested_image)


def os_imagename_from_base(requested_image):
	if requested_image == 'fedora36' or 'cvmfs-fedora36' == requested_image:
		return 'fedora:36'
	elif 'almalinux93' == requested_image or 'cvmfs-almalinux93' == requested_image:
		return 'almalinux:9.3'
	elif 'ubuntu24' == requested_image or 'cvmfs-ubuntu24' == requested_image:
		return 'ubuntu:24.04'
	else:
		# not supported
		print(f'Error: platform {requested_image} not supported')
		exit(1)


def base_imagename_from_sim(requested_image):
	osname = osname_from_image(requested_image)
	from_image = 'jeffersonlab/base:' + osname
	return from_image


def sim_imagename_from_gemc(requested_image):
	# strip everything before first '-'
	from_image = 'jeffersonlab/sim:' + requested_image.split('-', 1)[1]
	return from_image


def dockerfile_name(image):
	return 'dockerfiles/Dockerfile-' + image


def osname_from_image(requested_image):
	if requested_image.count('-') == 0:
		osname = requested_image
	elif requested_image.count('-') == 2:
		osname = requested_image.split('-')[1]
	elif requested_image.count('-') == 1:
		osname = requested_image.split('-')[1]
	else:
		osname = requested_image.split('-')[2]

	# make sure requested image is supported
	if osname not in supported_osnames():
		print(f'Error: osname {osname} not supported')
		exit(1)

	return osname


def install_dir_from_image(requested_image):
	if requested_image.count('-') == 0:
		return 'system'
	elif requested_image.split('-')[0] == 'cvmfs':
		return install_dir_path_from_label('cvmfs')
	else:
		install_dir_label = requested_image.split('-')[-1]
		return install_dir_path_from_label(install_dir_label)


def g4_version_from_image(requested_image):
	if requested_image.count('-') == 2:
		g4_version = requested_image.split('-')[0]
	elif requested_image.count('-') == 3:
		g4_version = requested_image.split('-')[1]
	else:
		return 'na'

	# make sure requested geant4 version is supported
	g4_version = g4_version[3:]
	if g4_version not in supported_geant4_versions():
		print(f'Error: geant4 version {g4_version} not supported')
		exit(1)
	else:
		return g4_version



def sim_version_from_image(requested_image):
	g4_version = g4_version_from_image(requested_image)
	if g4_version == '10.6.2':
		return '1.0'
	elif g4_version == '10.7.4':
		return '1.1'
	elif g4_version == '11.2.1':
		return '1.2'
	else:
		return 'na'

if __name__ == "__main__":
	main()
