# Maya Voice Studio

A local web interface for [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) text-to-speech, with 12 languages, built-in voices, editable demos, streaming, playback controls, emotion cues, and light and dark themes.

## Platforms

- **Apple Silicon macOS:** Run the MLX speech engine natively on the Mac, with the web frontend in Docker. Docker Desktop's Linux container cannot directly use the Mac's Apple GPU through this project's MLX backend.
- **Linux AMD64:** Run the app and CUDA speech engine in Docker on a host with a compatible NVIDIA GPU. The image builds, but inference on an NVIDIA host has not been verified.
- **Linux ARM64:** Not supported yet. The upstream CUDA dependencies need an ARM64-compatible solution and testing. Do not use the Mac proxy image as a Linux ARM inference image.

See the [setup guide](https://github.com/USANJAY05/maya-voice-studio/blob/master/maya_studio/README.md) for requirements and commands. Model files download on first use and can take several gigabytes.

## Apple Silicon Mac: Docker frontend + native MLX engine

This is a two-part setup: a small Docker container serves the web UI and forwards API requests to the MLX server running on macOS. The MLX server uses Apple Silicon acceleration. **Docker alone does not run the speech model on the Mac GPU.**

### 1. Clone and install the native engine

Install Docker Desktop and Python 3.10+ first. Then run from the repository root:

```bash
git clone https://github.com/USANJAY05/maya-voice-studio.git
cd maya-voice-studio

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install 'mlx-audio[tts] @ git+https://github.com/Blaizzy/mlx-audio.git@6ce7283be6f15f0cba37e839e73bfa4a08bbf040'
.venv/bin/pip install soundfile
```

### 2. Start both services

The helper script starts the native MLX server in the background, builds the Mac proxy image, and runs Docker Compose in the foreground:

```bash
./build.sh run-mac
```

Open [http://localhost:8765](http://localhost:8765). Press Ctrl+C to stop the Docker service; the helper script also stops the native MLX process it started.

The native engine log is written to `.maya-engine.log`. If startup fails, inspect that file. Stop any existing process already using port 8766 or 8765 before starting.

### 3. Run the two parts manually (alternative)

Terminal 1, from the repository root:

```bash
MAYA_HOST=0.0.0.0 MAYA_PORT=8766 HF_HOME="$PWD/.maya-cache" .venv/bin/python maya_studio/server.py
```

Terminal 2, from the repository root:

```bash
docker compose -f maya_studio/compose.mac.yml up --build
```

Open [http://localhost:8765](http://localhost:8765). Stop each process with Ctrl+C.

The native server binds to all interfaces so Docker Desktop can reach it. It has no authentication: use this only on a trusted network and stop it when finished. The helper script manages the native process lifecycle for local use.

## Linux AMD64 with an NVIDIA GPU

Requires Docker, an NVIDIA driver compatible with CUDA 12.8, and the NVIDIA Container Toolkit. An NVIDIA GPU with around 12 GB VRAM is recommended.

From the repository root:

```bash
docker compose -f maya_studio/compose.linux.yml up --build
```

Open [http://localhost:8765](http://localhost:8765). Model weights are stored in the `maya-models` Docker volume. The image build and web startup have been checked; NVIDIA inference has not been verified.

To build the Linux image without starting it:

```bash
./build.sh linux
```

## Build the Mac proxy image only

If you only want to build the Mac frontend proxy image:

```bash
./build.sh mac
```

This does not start the native MLX engine or the container. Use `./build.sh run-mac` to start the complete Mac setup.

## Docker Hub images

Replace `<username>` with the Docker Hub namespace used by the publisher. Images are available after the publishing workflow succeeds.

### Linux AMD64 with NVIDIA GPU

```bash
docker pull <username>/maya-voice-studio:latest-linux-amd64
docker run --rm --gpus all -p 127.0.0.1:8765:8765 \
  -v maya-models:/data/huggingface \
  <username>/maya-voice-studio:latest-linux-amd64
```

Open [http://localhost:8765](http://localhost:8765). The named volume retains downloaded model files after the container stops.

### Apple Silicon Mac

First install the native MLX dependencies and start the engine as described above. Then, in another terminal, run the published proxy image:

```bash
docker pull <username>/maya-voice-studio:latest-mac-arm64
docker run --rm -p 127.0.0.1:8765:8765 \
  <username>/maya-voice-studio:latest-mac-arm64
```

The published Mac image is a frontend proxy only; it still requires the native MLX engine listening on port 8766.

## Docker Hub publishing

Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as GitHub Actions repository secrets. The token must have permission to push `<username>/maya-voice-studio`. On branch pushes, CI builds both variants with commit-specific tags, except when all changed files are HTML, JavaScript, CSS, TXT, or Markdown. Run the image workflow manually to include frontend-only changes; otherwise published images retain the previous frontend. On `master`, it also publishes:

- `<username>/maya-voice-studio:latest-mac-arm64` — Mac frontend proxy; requires the native Mac MLX engine.
- `<username>/maya-voice-studio:latest-linux-amd64` — Linux AMD64 NVIDIA CUDA application.

CI builds do not verify GPU inference. To update the Docker Hub overview, manually run the **Update Docker Hub overview** workflow from GitHub Actions.

## Security and limitations

- The app has no authentication. Keep it on a trusted network.
- The native Mac server binds to `0.0.0.0:8766` for Docker Desktop connectivity.
- The server processes one generation at a time.
- Model files download on first use and can take several gigabytes.
- Regional wording and emotion cues are best effort; playback speed changes browser playback, not the generated audio file.

## Credits

Uses [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) and [MLX Audio](https://github.com/Blaizzy/mlx-audio). See upstream projects for licenses and attribution, including Kyutai Mimi.
