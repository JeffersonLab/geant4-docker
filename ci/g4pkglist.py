#!/usr/bin/env python3
import argparse

DISTROS = ["fedora", "ubuntu", "arch", "almalinux", "debian", "rhel"]

# ------------------------------------------------------------------------------
# Package groups by purpose
pkg_sections = {
	"cxx_essentials": {
		"fedora": ["git", "make", "cmake", "gcc-c++", "gdb", "valgrind"],
		"ubuntu": ["git", "make", "cmake", "g++", "gdb", "valgrind"],
		"arch":   ["git", "make", "cmake", "gcc", "gdb", "valgrind"]
	},
	"expat":          {
		"fedora": ["expat-devel"],
		"ubuntu": ["libexpat1-dev"],
		"arch":   ["expat"]
	},
	"sql":            {
		"fedora": ["mariadb-devel", "sqlite-devel"],
		"ubuntu": ["libmysqlclient-dev", "libsqlite3-dev"],
		"arch":   ["mariadb-libs", "mariadb-devel", "sqlite", "sqlite-devel"]
	},
	"python_ninja":   {
		"fedora": ["python3-devel", "ninja-build"],
		"ubuntu": ["python3-dev", "ninja-build"],
		"arch":   ["python", "python-pip", "ninja"]
	},
	"x11_1":          {
		"fedora": ["mesa-libGLU-devel", "libX11-devel", "libXpm-devel", "libXft-devel"],
		"ubuntu": ["libglu1-mesa-dev", "libx11-dev", "libxpm-dev", "libxft-dev"],
		"arch":   ["mesa", "glu", "libx11", "libxpm", "libxft"]
	},
	"x11_2":          {
		"fedora": ["libXt-devel", "libXmu-devel", "libXrender-devel", "xorg-x11-server-Xvfb",
		           "xrandr"],
		"ubuntu": ["libxt-dev", "libxmu-dev", "libxrender-dev", "xvfb", "xrandr",
		           "x11-xserver-utils"],
		"arch":   ["libxt", "libxmu", "libxrender", "xorg-server-xvfb", "xorg-xrandr"]
	},
	"utilities_1":    {
		"fedora": ["bzip2", "wget", "curl", "nano", "bash", "tcsh", "zsh", "hostname", "gedit",
		           "environment-modules", "pv", "which"],
		"ubuntu": ["bzip2", "wget", "curl", "nano", "bash", "tcsh", "zsh", "hostname", "gedit",
		           "environment-modules", "pv", "gnu-which"],
		"arch":   ["bzip2", "wget", "curl", "nano", "bash", "tcsh", "zsh", "hostname", "gedit",
		           "environment-modules", "pv", "which"]
	},
	"utilities_2":    {
		"fedora": ["psmisc", "procps", "mailcap", "net-tools", "rsync", "patch"],
		"ubuntu": ["psmisc", "procps", "mailcap", "net-tools", "rsync", "patch"],
		"arch":   ["psmisc", "procps", "mailcap", "net-tools", "rsync", "patch"]
	},
	"vnc":            {
		"fedora": ["xterm", "x11vnc", "novnc"],
		"ubuntu": ["xterm", "x11vnc", "novnc"],
		"arch":   ["xterm", "x11vnc", "novnc"]
	},
	"qt6":            {
		"fedora": ["qt6-qtbase-devel"],
		"ubuntu": ["qt6-base-dev", "libqt6opengl6t64", "libqt6openglwidgets6t64"],
		"arch":   ["qt6-base", "qt6-base-devel"]
	},
	"root":           {
		"fedora": ["root"],
		"ubuntu": [],
		"arch":   ["root"]
	},
	"sanitizers":     {
		"fedora": ["liblsan", "libasan", "libubsan", "libtsan", "tbb"],
		"ubuntu": ["liblsan0", "libasan8", "libubsan1", "libtsan2", "libtbb12"],
		"arch":   ["gcc-libs", "tbb"]
	}
}

# ------------------------------------------------------------------------------
# Cleanup strings per base distro family
cleanup_string_by_distro = {
	"fedora": (
		" \\\n && dnf -y update"
		" \\\n && dnf -y check-update"
		" \\\n && dnf clean packages"
		" \\\n && dnf clean all"
		" \\\n && rm -rf /var/cache/dnf \n"
	),
	"ubuntu": (
		" \\\n && apt-get -y update"
		" \\\n && apt-get -y autoclean"
		" \\\n && rm -rf /var/lib/apt/lists/* \n"
	),
	"arch":   (
		" \\\n && pacman -Syu --noconfirm"
		" \\\n && pacman -Scc --noconfirm"
		" \\\n && rm -rf /var/cache/pacman/pkg/* \n"
	)
}


# ------------------------------------------------------------------------------
# Helpers

def novnc_launch_commands() -> str:
    return """
# Setup environment and launch noVNC + x11vnc + Xvfb
ENV DISPLAY=:1
ENV GEOMETRY=1280x800

CMD ["/bin/bash", "-c", "\
Xvfb :1 -screen 0 ${GEOMETRY}x24 & \\
x11vnc -display :1 -nopw -forever -bg -quiet && \\
/usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080"]
"""


def distro_name_from_image(image: str) -> str:
	for d in ["fedora", "almalinux", "rhel", "ubuntu", "debian", "arch"]:
		if d in image.lower():
			return d
	return "unknown"


def local_setup_filename():
	return '/etc/profile.d/localSetup.sh'


def docker_header(image: str) -> str:
	return f"""FROM {image}
LABEL maintainer="Maurizio Ungaro <ungaro@jlab.org>"

# run shell instead of sh
SHELL ["/bin/bash", "-c"]
ENV AUTOBUILD=1
"""


def packages_to_be_installed(platform: str) -> str:
	platform = platform.lower()
	pkgs = []
	for section in pkg_sections.values():
		# Treat almalinux and rhel as fedora clones
		if "almalinux" in platform or "rhel" in platform:
			platform = "fedora"
		for key in [k for k in DISTROS if k in platform]:
			pkgs.extend(section.get(key, []))
			break
	return ' '.join(sorted(set(pkgs)))  # remove duplicates


def packages_install_commands(image: str) -> str:
	distro = distro_name_from_image(image)
	packages = packages_to_be_installed(image)
	cleanup = cleanup_string_by_distro.get(distro, "")
	local_setup_file = local_setup_filename()
	commands = ""
	commands += docker_header(image)

	is_alma = "almalinux" in image.lower()
	is_rhel = "rhel" in image.lower()

	if distro == "fedora":
		commands += "RUN update-ca-trust\n\n"
		# Special handling for AlmaLinux
		if is_alma or is_rhel:
			commands += (
				"RUN dnf install -y 'dnf-command(config-manager)' \\\n"
				"    && dnf config-manager --set-enabled crb \\\n"
				"    && dnf install -y almalinux-release-synergy \n\n"
			)
		commands += f"RUN dnf install -y --allowerasing {packages}{cleanup}"
	elif distro == "ubuntu":
		commands += "RUN apt update\n\n"
		commands += "# Install ca-certificates tools\n"
		commands += "RUN apt-get install -y ca-certificates\n"
		commands += "RUN update-ca-certificates\n\n"
		commands += (
				"RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \\\n"
				"    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata "
				+ packages + cleanup)
		commands += install_root_from_ubuntu_tarball(local_setup_file)


	elif distro == "arch":
		commands += f"RUN pacman -Syu --noconfirm {packages}{cleanup}"

	commands += install_meson()
	commands += novnc_launch_commands()

	return commands


def install_root_from_ubuntu_tarball(local_setup_file):
	root_version = '6.32.02'
	ubuntu_os_name = 'ubuntu24.04-x86_64-gcc13.2'
	root_file = f'root_v{root_version}.Linux-{ubuntu_os_name}.tar.gz'
	root_remote_file = f'https://root.cern/download/{root_file}'
	root_install_dir = '/usr/local'
	commands = '\n\n'
	commands += '# root installation using tarball\n'
	commands += f'RUN cd {root_install_dir} \\\n'
	commands += f'    && {curl_command({root_remote_file})}  \\\n'
	commands += f'    && tar -xzf {root_file} \\\n'
	commands += f'    && rm {root_file} \\\n'
	commands += f'    && echo "cd {root_install_dir}/root/bin ; source thisroot.sh ; cd -" >> {local_setup_file}\n'
	return commands


def install_meson():
	meson_version = '1.9.0'
	meson_location = f'https://github.com/mesonbuild/meson/releases/download/{meson_version}'
	meson_file = f'meson-{meson_version}.tar.gz'
	meson_remote_file = f'{meson_location}/{meson_file}'
	meson_install_dir = '/usr/local'
	commands = '\n'
	commands += '# meson installation using tarball\n'
	commands += f'RUN cd {meson_install_dir} \\\n'
	commands += f'    && {curl_command({meson_remote_file})}  \\\n'
	commands += f'    && tar -xzf {meson_file} \\\n'
	commands += f'    && rm {meson_file} \\\n'
	commands += f'    && ln -s {meson_install_dir}/meson-{meson_version}/meson.py /usr/bin/meson\n'
	return commands


def jlab_certificate():
	return "/etc/pki/ca-trust/source/anchors/JLabCA.crt"


# execute system curl command to download file
# notice: both the cacert and the -k option are given here. For some reason the cacert option
# was not enough on fedora line OSes
# see also https://curl.se/docs/sslcerts.html
def curl_command(filename):
	return f'curl -S --location-trusted --progress-bar --retry 4 --cacert {jlab_certificate()} {filename} -k -O'


def main():
	parser = argparse.ArgumentParser(
		description="Return list of packages or install commands for Geant4 + novnc environments",
		epilog="Example: ./g4pkglist.py -p fedora40"
	)
	parser.add_argument("-p", "--platform", required=True,
	                    help="Target platform: fedora / almalinux / rhel / ubuntu / debian / arch")
	parser.add_argument("--install", action="store_true",
	                    help="Print full Docker install RUN command")

	args = parser.parse_args()
	if args.install:
		print(packages_install_commands(args.platform))
	else:
		print(packages_to_be_installed(args.platform))


# ------------------------------------------------------------------------------
if __name__ == "__main__":
	main()
