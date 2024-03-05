#!/usr/bin/env python3

import argparse
from image_name import from_container_image

# Purposes:
# Write a dockerfile


def main():
	parser = argparse.ArgumentParser(description="Dpckerfile creator", epilog="Example: -df fedora36")

	parser.add_argument('-df', action='store', help='docker image requested')

	args = parser.parse_args()

	requested_image = args.df
	from_image = from_container_image(requested_image)
	if requested_image.count('-') == 0:
		# calling this will make sure the requested image is supported
		dockerfile = 'dockerfiles/Dockerfile-' + requested_image
	else:
		dockerfile = 'dockerfiles/Dockerfile-' + from_image

	print(f'Creating Dockerfile: {dockerfile}')

	write_dockerfile(dockerfile, from_image)


def write_dockerfile(dockerfile, from_image):
	# write the dockerfile
	with open(dockerfile, 'w') as f:
		f.write(f'FROM {from_image} \n')
		f.write('LABEL maintainer="Maurizio Ungaro <ungaro@jlab.org>"\n\n')
		f.write('# run shell instead of sh\n')
		f.write('SHELL ["/bin/bash", "-c"]\n')
		f.close()


if __name__ == "__main__":
	main()



