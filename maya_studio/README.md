# Maya Voice Studio setup

## Apple Silicon Mac: Docker frontend + native MLX engine

The Mac Docker image is a frontend proxy, not the model runtime. Docker Desktop runs Linux containers and this project's MLX backend needs to run natively on macOS to use Apple Silicon GPU acceleration.

### Requirements

- Apple Silicon Mac (M-series).
- macOS with Python 3.10+.
- Docker Desktop for Mac, running.
- Internet access and several GB of free disk space for model downloads.

### 1. Install the native MLX dependencies

Run these commands from the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install 'mlx-audio[tts] @ git+https://github.com/Blaizzy/mlx-audio.git@6ce7283be6f15f0cba37e839e73bfa4a08bbf040'
.venv/bin/pip install soundfile
```

### 2. Start the complete Mac setup

From the repository root:

```sh
./build.sh run-mac
```

The helper script starts the native MLX server on port 8766, writes its output to `.maya-engine.log`, builds the proxy container, and starts Docker Compose. Open http://localhost:8765. Press Ctrl+C to stop the container and the native server started by the script.

If startup fails, inspect `.maya-engine.log`. Make sure ports 8765 and 8766 are not already in use.

### 3. Manual startup (alternative)

Terminal 1, from the repository root:

```sh
MAYA_HOST=0.0.0.0 MAYA_PORT=8766 HF_HOME="$PWD/.maya-cache" .venv/bin/python maya_studio/server.py
```

Terminal 2, from the repository root:

```sh
docker compose -f maya_studio/compose.mac.yml up --build
```

Open http://localhost:8765. Stop both processes with Ctrl+C.

The native server binds to all interfaces so Docker Desktop can reach it. There is no authentication; use a trusted network and stop the service when finished.

## Linux AMD64 with NVIDIA GPU

Requires Docker, the NVIDIA Container Toolkit, a compatible driver with CUDA 12.8 support, and an NVIDIA GPU (around 12 GB VRAM recommended).

From the repository root:

```sh
docker compose -f maya_studio/compose.linux.yml up --build
```

Open http://localhost:8765. Model weights download to the `maya-models` volume on first use. The image build and web startup have been checked; NVIDIA inference has not been verified.

## Linux ARM64

Not supported yet. The upstream CUDA dependencies need an ARM64-compatible solution and testing. The `latest-mac-arm64` Docker tag is a Mac frontend proxy and does not provide Linux ARM inference.

## Docker Hub images

Add repository secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` with permission to push `<username>/maya-voice-studio`. CI publishes commit-specific tags for both variants and, on pushes to master, `latest-mac-arm64` and `latest-linux-amd64`.

Published image examples, replacing `<username>`:

```sh
# Mac: start the native MLX engine first, then run the proxy image
docker run --rm -p 127.0.0.1:8765:8765 <username>/maya-voice-studio:latest-mac-arm64

# Linux AMD64 with NVIDIA GPU
docker run --rm --gpus all -p 127.0.0.1:8765:8765 -v maya-models:/data/huggingface <username>/maya-voice-studio:latest-linux-amd64
```

## Security and limitations

- The app has no authentication; run it only on a trusted network.
- The Mac native server binds to `0.0.0.0:8766` so Docker Desktop can reach it.
- The app processes one generation at a time.
- Regional wording and emotion cues are best effort; playback speed only affects browser playback.
