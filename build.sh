#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${1:-}" in
  mac) docker build -f "$root/maya_studio/Dockerfile.mac" -t maya-voice-studio-mac "$root/maya_studio" ;;
  linux) docker build --platform linux/amd64 -f "$root/maya_studio/Dockerfile.linux" -t maya-voice-studio-linux "$root/maya_studio" ;;
  *) printf 'Usage: %s {mac|linux}\n' "$0" >&2; exit 2 ;;
esac
