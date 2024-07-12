#!/bin/sh

# on fedora and ubuntu installation dir is different for modules
[[ -f /usr/share/Modules/init/sh ]] && source /usr/share/Modules/init/sh
[[ -f /usr/share/modules/init/sh ]] && source /usr/share/modules/init/sh

export TERM=xterm-256color
alias l='ls -l'
alias lt='ls -lhrt'
alias ll='ls -lah'
alias gist='git status -s | grep -v \?'
alias gista='git status -s'

# temp installation of meson, as the one in the container is too old
meson_version=1.5.0
if [ ! -d "/root/meson-$meson_version" ]; then
	cd /root
	wget https://github.com/mesonbuild/meson/releases/download/$meson_version/meson-$meson_version.tar.gz
	tar -zxpf meson-$meson_version.tar.gz
	ln -s /root/meson-$meson_version/meson.py /usr/bin/meson
fi


