#!/usr/bin/env python3

import argparse

# Purposes:
# Return fluxbox installation commands


def main():
	desc_str = 'fluxbox installation commands'
	example = 'Example: -i fedora36'
	parser = argparse.ArgumentParser(description=desc_str, epilog=example)
	parser.add_argument('-i', action='store', help='fluxbox installation commands based on image to build')
	args = parser.parse_args()

	image = args.i

	if image:
		icommands = fluxbox_install_commands(image)
		print(icommands)

# notice copy directory conf.d needs destination /app/conf.d
def fluxbox_install_commands(image):
	commands = '\n'
	commands += '# Setup demo environment variables'
	commands += '\n'
	commands += 'ENV HOME=/root'
	commands += ' LANG=en_US.UTF-8'
	commands += ' LANGUAGE=en_US.UTF-8'
	commands += '  LC_ALL=C.UTF-8 '
	commands += ' DISPLAY=:0.0'
	commands += ' DISPLAY_WIDTH=1400'
	commands += ' DISPLAY_HEIGHT=1000'
	commands += ' RUN_XTERM=yes'
	commands += ' RUN_FLUXBOX=yes\n'
	commands += '\n'
	commands += 'COPY fluxbox/conf.d /app/conf.d\n'
	commands += 'COPY fluxbox/supervisord.conf fluxbox/entrypoint.sh  /app/\n'
	commands += '\n'
	commands += 'CMD ["/app/entrypoint.sh"]\n'
	commands += 'EXPOSE 8080\n'
	commands += '\n'


	commands += '\n'
	return commands


if __name__ == "__main__":
	main()
