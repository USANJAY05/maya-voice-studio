#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command="${1:-}"

case "$command" in
  mac)
    docker build -f "$root/maya_studio/Dockerfile.mac" -t maya-voice-studio-mac "$root/maya_studio"
    ;;
  linux)
    docker build --platform linux/amd64 -f "$root/maya_studio/Dockerfile.linux" -t maya-voice-studio-linux "$root/maya_studio"
    ;;
  run-mac)
    if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
      echo "run-mac requires an Apple Silicon Mac." >&2
      exit 1
    fi
    if [[ ! -x "$root/.venv/bin/python" ]]; then
      echo "Missing $root/.venv/bin/python. Follow the Mac setup instructions in README.md first." >&2
      exit 1
    fi
    if ! docker info >/dev/null 2>&1; then
      echo "Docker is not running. Start Docker Desktop and try again." >&2
      exit 1
    fi

    log_file="$root/.maya-engine.log"
    echo "Starting native Maya MLX server on port 8766..."
    (
      cd "$root"
      MAYA_HOST=0.0.0.0 MAYA_PORT=8766 HF_HOME="$root/.maya-cache" \
        "$root/.venv/bin/python" "$root/maya_studio/server.py"
    ) >"$log_file" 2>&1 &
    engine_pid=$!

    cleanup() {
      echo "Stopping native Maya MLX server..."
      kill "$engine_pid" 2>/dev/null || true
      wait "$engine_pid" 2>/dev/null || true
    }
    trap cleanup EXIT INT TERM

    sleep 2
    if ! kill -0 "$engine_pid" 2>/dev/null; then
      echo "Native MLX server failed to start. See $log_file" >&2
      cat "$log_file" >&2
      exit 1
    fi

    echo "Starting Docker frontend. Open http://localhost:8765"
    docker compose -f "$root/maya_studio/compose.mac.yml" up --build
    ;;
  *)
    printf 'Usage: %s {mac|linux|run-mac}\n' "$0" >&2
    printf '  mac      Build the Apple Silicon Docker frontend proxy image\n' >&2
    printf '  linux    Build the Linux AMD64 NVIDIA CUDA image\n' >&2
    printf '  run-mac  Start the native MLX engine and Docker frontend on Apple Silicon\n' >&2
    exit 2
    ;;
esac
