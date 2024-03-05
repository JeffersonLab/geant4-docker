#!/usr/bin/env python3

import argparse

# Purposes:
# Return from_image, dockerfile, image name, tag


def main():
	# Provides the -h, --help message
	desc_str = "   Header for dockerfile\n"
	parser = argparse.ArgumentParser(description=desc_str)

	parser.add_argument('-f', action='store', help='Docker header based on what to build')

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



if __name__ == "__main__":
	main()



