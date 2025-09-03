#!/usr/bin/env python3
import argparse

DISTROS = ["fedora", "ubuntu", "arch", "almalinux", "debian", "rhel"]

# ------------------------------------------------------------------------------
# Package groups by purpose
pkg_sections = {
    "cxx_essentials": {
        "fedora": ["git", "make", "cmake", "gcc-c++", "gdb", "valgrind"],
        "ubuntu": ["git", "make", "cmake", "g++", "gdb", "valgrind"],
        "arch":   ["git", "make", "cmake", "gcc", "gdb", "valgrind"],
        # debian uses same as ubuntu (handled by mapping below)
    },
    "expat": {
        "fedora": ["expat-devel"],
        "ubuntu": ["libexpat1-dev"],
        "arch":   ["expat"],
    },
    "sql": {
        "fedora": ["mariadb-devel", "sqlite-devel"],
        "ubuntu": ["libmysqlclient-dev", "libsqlite3-dev"],
        # On Arch, dev headers are included in the main pkgs; no -devel splits
        "arch":   ["mariadb", "mariadb-libs", "sqlite"],
    },
    "python_ninja": {
        "fedora": ["python3-devel", "ninja-build"],
        "ubuntu": ["python3-dev", "ninja-build"],
        "arch":   ["python", "python-pip", "ninja"],
    },
    "x11_1": {
        "fedora": ["mesa-libGLU-devel", "libX11-devel", "libXpm-devel", "libXft-devel"],
        "ubuntu": ["libglu1-mesa-dev", "libx11-dev", "libxpm-dev", "libxft-dev"],
        "arch":   ["mesa", "glu", "libx11", "libxpm", "libxft"],
    },
    "x11_2": {
        "fedora": ["libXt-devel", "libXmu-devel", "libXrender-devel",
                   "xorg-x11-server-Xvfb", "xrandr"],
        # Ubuntu/Debian: xrandr is in x11-xserver-utils (not a pkg called 'xrandr')
        "ubuntu": ["libxt-dev", "libxmu-dev", "libxrender-dev",
                   "xvfb", "x11-xserver-utils"],
        # Arch: xrandr is xorg-xrandr; xvfb via xorg-server-xvfb
        "arch":   ["libxt", "libxmu", "libxrender",
                   "xorg-server-xvfb", "xorg-xrandr"],
    },
    "utilities_1": {
        "fedora": ["bzip2", "wget", "curl", "nano", "bash", "tcsh", "zsh",
                   "hostname", "gedit", "environment-modules", "pv", "which"],
        # Ubuntu/Debian: 'which' is 'which' (not gnu-which)
        "ubuntu": ["bzip2", "wget", "curl", "nano", "bash", "tcsh", "zsh",
                   "hostname", "gedit", "environment-modules", "pv", "which", "ca-certificates"],
        "arch":   ["bzip2", "wget", "curl", "nano", "bash", "tcsh", "zsh",
                   "hostname", "gedit", "environment-modules", "pv", "which"],
    },
    "utilities_2": {
        "fedora": ["psmisc", "procps", "mailcap", "net-tools", "rsync", "patch"],
        "ubuntu": ["psmisc", "procps", "mailcap", "net-tools", "rsync", "patch"],
        "arch":   ["psmisc", "procps", "mailcap", "net-tools", "rsync", "patch"],
    },
    "vnc": {
        "fedora": ["xterm", "x11vnc", "novnc"],
        "ubuntu": ["xterm", "x11vnc", "novnc"],
        "arch":   ["xterm", "x11vnc", "novnc"],
    },
    "qt6": {
        "fedora": ["qt6-qtbase-devel"],
        "ubuntu": ["qt6-base-dev", "libqt6opengl6t64", "libqt6openglwidgets6t64"],
        "arch":   ["qt6-base", "qt6-base-devel"],
    },
    "root": {
        "fedora": ["root"],
        "ubuntu": [],
        "arch":   ["root"],
    },
    "sanitizers": {
        "fedora": ["liblsan", "libasan", "libubsan", "libtsan", "tbb"],
        "ubuntu": ["liblsan0", "libasan8", "libubsan1", "libtsan2", "libtbb12"],
        "arch":   ["gcc-libs", "tbb"],
    },
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
    "arch": (
        " \\\n && pacman -Syu --noconfirm"
        " \\\n && pacman -Scc --noconfirm"
        " \\\n && rm -rf /var/cache/pacman/pkg/* \n"
    ),
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
    image = image.lower()
    for d in ["fedora", "almalinux", "rhel", "ubuntu", "debian", "arch"]:
        if d in image:
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

def _map_family(platform: str) -> str:
    p = platform.lower()
    if "almalinux" in p or "rhel" in p or "centos" in p:  # treat RHEL family as fedora pkgs
        return "fedora"
    if "debian" in p:                                     # treat Debian like Ubuntu pkgs
        return "ubuntu"
    return p

def packages_to_be_installed(platform: str) -> str:
    plat = _map_family(platform)
    pkgs = []
    for section in pkg_sections.values():
        pkgs.extend(section.get(plat, []))
    # remove duplicates, keep stable output
    return ' '.join(sorted(set(pkgs)))

def install_root_from_ubuntu_tarball(local_setup_file: str) -> str:
    root_version = '6.32.02'
    ubuntu_os_name = 'ubuntu24.04-x86_64-gcc13.2'
    root_file = f'root_v{root_version}.Linux-{ubuntu_os_name}.tar.gz'
    root_remote_file = f'https://root.cern/download/{root_file}'
    root_install_dir = '/usr/local'
    commands = '\n\n'
    commands += '# root installation using tarball\n'
    commands += f'RUN cd {root_install_dir} \\\n'
    commands += f'    && {curl_command(root_remote_file)}  \\\n'
    commands += f'    && tar -xzf {root_file} \\\n'
    commands += f'    && rm {root_file} \\\n'
    commands += f'    && echo "cd {root_install_dir}/root/bin ; source thisroot.sh ; cd -" >> {local_setup_file}\n'
    return commands

def install_meson() -> str:
    meson_version = '1.9.0'
    meson_location = f'https://github.com/mesonbuild/meson/releases/download/{meson_version}'
    meson_file = f'meson-{meson_version}.tar.gz'
    meson_remote_file = f'{meson_location}/{meson_file}'
    meson_install_dir = '/usr/local'
    commands = '\n'
    commands += '# meson installation using tarball\n'
    commands += f'RUN cd {meson_install_dir} \\\n'
    commands += f'    && {curl_command(meson_remote_file)}  \\\n'
    commands += f'    && tar -xzf {meson_file} \\\n'
    commands += f'    && rm {meson_file} \\\n'
    commands += f'    && ln -s {meson_install_dir}/meson-{meson_version}/meson.py /usr/bin/meson\n'
    return commands

def jlab_certificate() -> str:
    return "/etc/pki/ca-trust/source/anchors/JLabCA.crt"

def curl_command(url: str) -> str:
    """
    Build a portable curl command string.
    We attempt to use a site-specific CA if present; otherwise rely on system CAs.
    -k is kept for resilience, but you can remove it once CAs are squared away.
    """
    ca = jlab_certificate()
    return f"bash -lc 'CA=\"{ca}\"; EXTRA=\"\"; [ -f \"$CA\" ] && EXTRA=\"--cacert $CA\"; curl -S --location-trusted --progress-bar --retry 4 $EXTRA -k -O {url}'"

def packages_install_commands(image: str) -> str:
    distro = distro_name_from_image(image)
    family = _map_family(distro)
    packages = packages_to_be_installed(image)
    cleanup = cleanup_string_by_distro.get(family, "")
    local_setup_file = local_setup_filename()
    commands = ""
    commands += docker_header(image)

    is_alma = "almalinux" in image.lower()
    is_rhel = "rhel" in image.lower()

    if family == "fedora":
        commands += "RUN update-ca-trust\n\n"
        if is_alma or is_rhel:
            commands += (
                "RUN dnf install -y 'dnf-command(config-manager)' \\\n"
                "    && dnf config-manager --set-enabled crb \\\n"
                "    && dnf install -y almalinux-release-synergy \n\n"
            )
        commands += f"RUN dnf install -y --allowerasing {packages}{cleanup}"

    elif family == "ubuntu":
        commands += "RUN apt-get update\n\n"
        commands += "# Install CA tools\n"
        commands += "RUN apt-get install -y ca-certificates\n"
        commands += "RUN update-ca-certificates\n\n"
        commands += (
            "RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \\\n"
            "    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata "
            + packages + cleanup
        )
        commands += install_root_from_ubuntu_tarball(local_setup_file)

    elif family == "arch":
        commands += f"RUN pacman -Syu --noconfirm {packages}{cleanup}"

    commands += install_meson()
    commands += novnc_launch_commands()
    return commands

# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Return list of packages or install commands for Geant4 + novnc environments",
        epilog="Example: ./g4pkglist.py -p fedora:40 --install"
    )
    parser.add_argument(
        "-p", "--platform", required=True,
        help="Target base image (e.g., fedora:40 / almalinux:9 / rhel:9 / ubuntu:24.04 / debian:13 / archlinux:latest)"
    )
    parser.add_argument(
        "--install", action="store_true",
        help="Print full Dockerfile (header + install commands)"
    )

    args = parser.parse_args()
    if args.install:
        print(packages_install_commands(args.platform))
    else:
        print(packages_to_be_installed(args.platform))

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
