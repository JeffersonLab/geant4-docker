#!/usr/bin/env python3
import argparse

# Purposes:
# Functions containing naming conventions for images, dockerfiles, tags

def supported_osnames():
	return ['fedora36', 'almalinux93', 'ubuntu24']

def supported_cvmfs_osnames():
	return [f'cvmfs-{osname}' for osname in supported_osnames()]

def supported_geant4_versions():
	return ['10.6.2', '10.7.4', '11.2.2']

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
	if image.count('-') == 3:
		return True
	return False

def from_image(requested_image):
	if requested_image.count('-') == 0 or 'cvmfs' in requested_image:
		return os_base_image_from_imagename(requested_image)
	# sim image, requesting base image
	elif requested_image.count('-') == 1:
		return base_imagename_from_sim(requested_image)
	# gemc image, requesting sim image
	elif requested_image.count('-') == 2:
		return base_imagename_from_sim(requested_image)

def os_base_image_from_imagename(requested_image):
	if 'fedora36' in requested_image:
		return 'fedora:36'
	elif 'almalinux93' in requested_image:
		return 'almalinux:9.3'
	elif 'ubuntu24' in requested_image:
		return 'ubuntu:24.04'
	else:
		# not supported
		print(f'Error: platform {requested_image} not supported')
		exit(1)

def base_imagename_from_sim(requested_image):
	for osname in supported_osnames():
		if osname in requested_image:
			from_image = 'jeffersonlab/base:' + osname
	return from_image

def sim_imagename_from_gemc(requested_image):
	# strip everything before first '-'
	from_image = 'jeffersonlab/sim:' + requested_image.split('-', 1)[1]
	return from_image

def osname_from_image(requested_image):
	if requested_image.count('-') == 0:
		osname = requested_image
	elif requested_image.count('-') == 1:
		osname = requested_image.split('-')[1]
	elif requested_image.count('-') == 2:
		osname = requested_image.split('-')[1]
	else:
		osname = requested_image.split('-')[2]
	if osname not in supported_osnames():
		print(f'Error: osname {osname} not supported')
		exit(1)
	return osname

def g4_version_from_image(requested_image):
	# return the string between 'g4v' and '-'
	if 'g4v' in requested_image:
		return requested_image.split('g4v')[1].split('-')[0]
	else:
		print(f'Error: geant4 version not found in {requested_image}')
		exit(1)

# as of july 2024:
# prod1: gemc versions 4.4.2
# dev:   gemc versions 5.10, dev
def gemc_tags_from_docker_image(image):
	if image.count('-') == 3:
		tag = image.split('-')[0]
		if tag == 'prod1':
			return ['4.4.2']
		elif tag == 'dev':
			return ['5.10', 'dev']
		else:
			print(f'Error: tag {tag} not supported')
			exit(1)
	else:
		return []



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
