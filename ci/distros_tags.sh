#!/usr/bin/env bash
# -e — Exit on error
# -u — Treat unset variables as an error
# -o pipefail — Prevent errors in a pipeline from being masked
set -euo pipefail

get_ubuntu_lts()      { echo "24.04"; }
get_fedora_latest()   { echo "40"; }
get_arch_latest()     { echo "latest"; }
get_almalinux_latest(){ echo "9.4"; }
get_debian_latest()   { echo "13"; }
get_rhel_latest()     { echo "9.4"; }
get_geant4_tag()      { echo "11.3.2"; }

build_matrix() {
  local geant4_tag
  geant4_tag="$(get_geant4_tag)"

  cat <<EOF
{
  "include": [
    {
      "distro": "ubuntu",
      "docker_from": "ubuntu:$(get_ubuntu_lts)",
      "geant4_tag": "${geant4_tag}"
    },
    {
      "distro": "fedora",
      "docker_from": "fedora:$(get_fedora_latest)",
      "geant4_tag": "${geant4_tag}"
    },
    {
      "distro": "arch",
      "docker_from": "archlinux:$(get_arch_latest)",
      "geant4_tag": "${geant4_tag}"
    },
    {
      "distro": "almalinux",
      "docker_from": "almalinux:$(get_almalinux_latest)",
      "geant4_tag": "${geant4_tag}"
    },
    {
      "distro": "debian",
      "docker_from": "debian:$(get_debian_latest)",
      "geant4_tag": "${geant4_tag}"
    },
    {
      "distro": "rhel",
      "docker_from": "redhat/ubi9:$(get_rhel_latest)",
      "geant4_tag": "${geant4_tag}"
    }
  ]
}
EOF
}

main() {
  # Compute image namespace (works on Actions; falls back locally)
  local owner image
  owner="${GITHUB_REPOSITORY_OWNER:-JeffersonLab}"
  image="ghcr.io/${owner}/geant4"

  # If GITHUB_OUTPUT is set (GitHub Actions), write multi-line outputs there.
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    # Use a unique delimiter to avoid accidental collisions
    local DELIM="MATRIX_$(date +%s%N)"
    {
      echo "matrix<<${DELIM}"
      build_matrix
      echo "${DELIM}"
      echo "image=${image}"
    } >> "$GITHUB_OUTPUT"
  else
    # Local run: just print the JSON
    build_matrix
  fi
}

main "$@"
