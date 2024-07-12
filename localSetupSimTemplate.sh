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

currentDir=$(pwd)
cd install_dir_module_path_template

# if ceInstall is not there, clone it, otherwise pull
if [ ! -d "geant4" ]; then
	git clone https://github.com/JeffersonLab/ceInstall

	mv ceInstall/* .
	mv ceInstall/.git .
	rm -rf ceInstall

	git checkout nosim
else
	cd geant4
	git pull
	cd ..
fi

cd $currentDir



