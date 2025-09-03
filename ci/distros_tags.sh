#!/usr/bin/env bash
# -e — Exit on error
# -u — Treat unset variables as an error
# -o pipefail — Prevent errors in a pipeline from being masked
set -euo pipefail

get_ubuntu_lts()      { echo "24.04"; }
get_fedora_latest()   { echo "40"; }
get_arch_latest()     { echo "latest"; }
get_almalinux_latest() { echo "9.4"; }
get_debian_latest()   { echo "13"; }
get_rhel_latest()     { echo "9.4"; }
get_geant4_tag()      { echo "11.3.2"; }

#!/usr/bin/env bash
set -euo pipefail

# ... your get_* functions stay the same ...

build_matrix() {
  local geant4_tag
  geant4_tag="$(get_geant4_tag)"
  cat <<EOF
{
  "include": [
    { "distro": "ubuntu",    "docker_from": "ubuntu:$(get_ubuntu_lts)",          "geant4_tag": "${geant4_tag}" },
    { "distro": "fedora",    "docker_from": "fedora:$(get_fedora_latest)",       "geant4_tag": "${geant4_tag}" },
    { "distro": "arch",      "docker_from": "archlinux:$(get_arch_latest)",      "geant4_tag": "${geant4_tag}" },
    { "distro": "almalinux", "docker_from": "almalinux:$(get_almalinux_latest)", "geant4_tag": "${geant4_tag}" },
    { "distro": "debian",    "docker_from": "debian:$(get_debian_latest)",   "geant4_tag": "${geant4_tag}" },
    { "distro": "rhel",      "docker_from": "redhat/ubi9:$(get_rhel_latest)","geant4_tag": "${geant4_tag}" }
  ]
}
EOF
}

main() {
  # Compute image ref (lowercase) for GHCR
  local owner repo owner_lc repo_lc image
  owner="${GITHUB_REPOSITORY_OWNER:-JeffersonLab}"
  repo="${GITHUB_REPOSITORY##*/:-geant4}"
  owner_lc="$(echo "$owner" | tr '[:upper:]' '[:lower:]')"
  repo_lc="$(echo "$repo"  | tr '[:upper:]' '[:lower:]')"
  image="ghcr.io/${owner_lc}/${repo_lc}"

  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    # Running in GitHub Actions: write multi-line outputs
    local DELIM="MATRIX_$(date +%s%N)"
    {
      echo "matrix<<$DELIM"
      build_matrix
      echo "$DELIM"
      echo "image=$image"
    } >> "$GITHUB_OUTPUT"
  else
    # Local run: print JSON to stdout for inspection
    build_matrix
    echo "# image=$image" >&2
  fi
}

main "$@"
