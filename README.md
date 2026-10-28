# Maya Voice Studio

A local web interface for [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) text-to-speech, with 12 languages, built-in voices, editable demos, streaming, playback controls, emotion cues, and light and dark themes.

## Platforms

- **Apple Silicon macOS:** Run the MLX speech engine natively on the Mac, with a Docker frontend proxy. Docker Desktop's Linux container does not provide this app direct access to the Apple GPU.
- **Linux AMD64:** Run the app and CUDA speech engine in Docker on a host with a compatible NVIDIA GPU. The image built successfully, but inference on an NVIDIA host has not been verified.
- **Linux ARM64:** Not supported yet. The upstream engine pins PyTorch 2.8.0, torchaudio 2.8.0, and Triton 3.4.0; a compatible CUDA ARM64 runtime needs investigation and testing. Do not use the Mac proxy tag as an ARM Linux inference image.

See the [setup guide](https://github.com/USANJAY05/maya-voice-studio/blob/master/maya_studio/README.md) for requirements and commands. Model files download on first use and can take several gigabytes. The app has no authentication; run it only on a trusted network.

## Build

```bash
./build.sh mac    # Apple Silicon frontend proxy
./build.sh linux  # Linux AMD64 NVIDIA CUDA image
```

## Run from Docker Hub

Replace `<username>` with the Docker Hub namespace used by the publisher. Images appear after the publishing workflow succeeds.

### Linux AMD64 with an NVIDIA GPU

Install Docker, the NVIDIA driver and NVIDIA Container Toolkit first. Then run:

```bash
docker pull <username>/maya-voice-studio:latest-linux-amd64
docker run --rm --gpus all -p 127.0.0.1:8765:8765 \
  -v maya-models:/data/huggingface \
  <username>/maya-voice-studio:latest-linux-amd64
```

Open [localhost:8765](http://localhost:8765). The model downloads into the named volume on first generation. Press Ctrl+C to stop the container; the volume retains the model files.

### Apple Silicon Mac

The Mac image is a frontend proxy. Start the native MLX engine first; Docker alone cannot run this app's Apple GPU backend. Clone this repository, open a terminal in its folder, then run:

```bash
python3 -m venv .venv
.venv/bin/pip install 'mlx-audio[tts] @ git+https://github.com/Blaizzy/mlx-audio.git@6ce7283be6f15f0cba37e839e73bfa4a08bbf040'
MAYA_HOST=0.0.0.0 MAYA_PORT=8766 HF_HOME="$PWD/.maya-cache" .venv/bin/python maya_studio/server.py
```

Leave that terminal running. In a second terminal:

```bash
docker pull <username>/maya-voice-studio:latest-mac-arm64
docker run --rm -p 127.0.0.1:8765:8765 \
  <username>/maya-voice-studio:latest-mac-arm64
```

Open [localhost:8765](http://localhost:8765). Stop each process with Ctrl+C. The native engine listens on all network interfaces and has no authentication, so use a trusted network.

## Docker Hub publishing

Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as GitHub Actions repository secrets. The token must have permission to push `<username>/maya-voice-studio`. Synchronizing the Docker Hub description also requires a personal access token with read, write, and delete scope; for an organization, the user needs Admin access to the repository. On each branch push, CI builds both variants into that one repository with commit-specific tags. On `master`, it also publishes:

- `<username>/maya-voice-studio:latest-mac-arm64` — Mac frontend proxy; requires the native Mac MLX engine.
- `<username>/maya-voice-studio:latest-linux-amd64` — Linux AMD64 NVIDIA CUDA application.

Separate tags are necessary because both Docker Desktop on Apple Silicon and native ARM Linux use the `linux/arm64` platform identifier, even though their GPU backends differ. There is no supported Linux ARM64 image yet. CI builds do not verify GPU inference. After successful builds on `master`, the workflow also synchronizes this README to the Docker Hub repository description.

## Credits

Uses [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) and [MLX Audio](https://github.com/Blaizzy/mlx-audio). See upstream projects for licenses and attribution, including Kyutai Mimi.
