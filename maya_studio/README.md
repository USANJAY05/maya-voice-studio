# Maya Voice Studio setup

## Apple Silicon Mac

The Docker frontend connects to a native MLX engine. From the project root, using a permanent Python 3.10+ installation:

```sh
python3 -m venv .venv
.venv/bin/pip install 'mlx-audio[tts] @ git+https://github.com/Blaizzy/mlx-audio.git@6ce7283be6f15f0cba37e839e73bfa4a08bbf040'
MAYA_HOST=0.0.0.0 MAYA_PORT=8766 HF_HOME="$PWD/.maya-cache" .venv/bin/python maya_studio/server.py
```

In another terminal:

```sh
cd maya_studio
docker compose -f compose.mac.yml up --build
```

Open http://localhost:8765. Stop any existing service on that port first. The native engine listens on all interfaces so Docker Desktop can reach it; it has no authentication. Use a trusted network and stop it when finished. The existing project `.venv` may reference Python in `/private/tmp`, so recreate it if that runtime is removed.

## Linux AMD64 with NVIDIA GPU

Requires Docker and the NVIDIA Container Toolkit, a compatible driver with CUDA 12.8 support, and an NVIDIA GPU (12 GB VRAM recommended):

```sh
cd maya_studio
docker compose -f compose.linux.yml up --build
```

Open http://localhost:8765. Model weights download to the `maya-models` volume on first use. The image build and web startup have been checked; NVIDIA inference has not been tested.

## Linux ARM64

Not supported yet. Upstream's pinned PyTorch 2.8.0 and Triton 3.4.0 CUDA dependencies require an ARM64-compatible solution and testing. The `latest-mac-arm64` Docker tag is a Mac frontend proxy and does not provide Linux ARM inference.

## Docker Hub CI/CD

Add repository secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` with permission to push `<username>/maya-voice-studio`. CI publishes commit-specific tags for both variants and, for pushes to master, `latest-mac-arm64` and `latest-linux-amd64`. Run the workflow manually from GitHub Actions if secrets were added after the push.

Published image examples, replacing `<username>`:

```sh
# Mac: first start the native MLX engine above
docker run --rm -p 127.0.0.1:8765:8765 <username>/maya-voice-studio:latest-mac-arm64

# Linux AMD64 with NVIDIA GPU
docker run --rm --gpus all -p 127.0.0.1:8765:8765 -v maya-models:/data/huggingface <username>/maya-voice-studio:latest-linux-amd64
```

The app has no authentication and processes one generation at a time. Regional wording and emotion cues are best effort; playback speed only affects browser playback.
