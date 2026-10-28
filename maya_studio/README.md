# Maya Voice Studio

The web interface supports Maya speech on Apple Silicon through MLX or on a Windows NVIDIA GPU through the CUDA engine. These use different inference backends; there is no universal GPU-enabled container.

## Mac: Docker frontend + native MLX engine

Docker Desktop's Linux container does not provide the Apple Metal GPU to the MLX engine. The frontend proxy runs in Docker and connects to a separate native macOS process for speech. Docker Desktop, Apple Silicon, Python 3.10+ and MLX Audio with Maya2 support are required.

From the project root, create a durable native environment if needed:

```sh
python3 -m venv .venv
.venv/bin/pip install 'mlx-audio[tts] @ git+https://github.com/Blaizzy/mlx-audio.git@6ce7283be6f15f0cba37e839e73bfa4a08bbf040'
```

In one terminal start the native engine (this downloads the model on first use):

```sh
MAYA_HOST=0.0.0.0 MAYA_PORT=8766 HF_HOME="$PWD/.maya-cache" .venv/bin/python maya_studio/server.py
```

In another terminal, start the Docker frontend:

```sh
cd maya_studio
docker compose -f compose.mac.yml up --build
```

Open http://localhost:8765. Stop any existing service on that port first. The native service listens on port 8766 on all interfaces to make it reachable from Docker Desktop; it has no authentication. Use a trusted network, and stop it when finished. The existing .venv on this Mac uses Python under /private/tmp; reinstall it with a permanent Python if that temporary runtime is removed.

## Windows: NVIDIA GPU container

Requires Windows x86-64, an NVIDIA GPU (12 GB VRAM recommended), a current NVIDIA driver supporting CUDA 12.8, Docker Desktop configured with WSL 2, and working Docker GPU access. AMD and Intel GPUs and CPU-only Windows are not supported by this CUDA configuration. In PowerShell, from this folder:

```powershell
docker compose -f compose.windows.yml up --build
```

Open http://localhost:8765. The first speech request downloads model weights and supporting models into the `maya-models` Docker volume. The image build is large and may take significant time. Stop with Ctrl+C and `docker compose -f compose.windows.yml down`; this retains the model volume. The CUDA image and integration have not been tested on a Windows NVIDIA machine.

## Security and operation

Compose publishes the frontend to localhost only. The app has no authentication and is intended for trusted local use. Do not expose it to an untrusted network. The model handles one request at a time. Stream and non-stream audio use 24 kHz mono. The original model server and the MLX implementation can differ in voice output and emotion handling. Voice training labels come from Maya's model card; cross-language results can carry a different accent.

## Build scripts

From the project root, run `./build.sh mac` to build the Mac frontend image or `./build.sh windows` to build the Windows NVIDIA image. In Windows PowerShell, run `./build.ps1` (or `./build.ps1 -Target windows`). These commands build images; use the platform-specific startup instructions above to run them.

## Docker Hub CI/CD

The GitHub Actions workflow builds and publishes both images whenever a branch is pushed, and can be started manually from the Actions tab. Add these **repository secrets** under Settings → Secrets and variables → Actions:

- `DOCKERHUB_USERNAME`: Docker Hub account or organization namespace that owns the image repositories.
- `DOCKERHUB_TOKEN`: Docker Hub access token with permission to push both repositories. Use an organization access token or suitable credentials if publishing under an organization.

The workflow publishes `<username>/maya-voice-studio-mac` and `<username>/maya-voice-studio-windows`. Every push gets a `sha-<full-commit-sha>` tag; pushes to `master` also update `latest`. The Mac frontend is built for Linux ARM64 and AMD64; the Windows NVIDIA image is Linux AMD64 and needs an NVIDIA GPU with WSL 2. The Mac image still needs its native MLX backend. A successful image build does not test speech generation on either GPU. Configure secrets before pushing this workflow, or rerun the failed workflow once they are present.
