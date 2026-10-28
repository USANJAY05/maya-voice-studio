#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${1:-}" in
  mac) docker build -f "$root/maya_studio/Dockerfile.mac" -t maya-voice-studio-mac "$root/maya_studio" ;;
  windows) docker build --platform linux/amd64 -f "$root/maya_studio/Dockerfile.cuda" -t maya-voice-studio-windows "$root/maya_studio" ;;
  *) printf 'Usage: %s {mac|windows}\n' "$0" >&2; exit 2 ;;
esac
