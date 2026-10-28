# Maya Voice Studio

A local web interface for [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) text-to-speech. Choose a language and voice, use or edit a demo passage, and listen to generated speech. The app supports 12 languages, voice selection, streaming playback, pause and stop, emotion cues, playback speed, and light and dark themes.

Maya is a text-to-speech model: it turns text into audio. Regional demo wording and emotion cues are best-effort prompts, not guaranteed accent or emotion controls. Speed changes browser playback; downloaded audio retains its original speed.

## Choose your platform

| Platform | Setup | Requirements |
| --- | --- | --- |
| Apple Silicon Mac | Docker frontend with a native MLX speech engine | Docker Desktop, Apple Silicon, Python 3.10+, MLX Audio |
| Windows with NVIDIA GPU | CUDA speech engine and app in Docker | Windows x86-64, Docker Desktop with WSL 2, NVIDIA driver with CUDA 12.8 support; 12 GB VRAM recommended |

The Mac frontend image does **not** run the model inside Docker: the model runs natively to access the Apple GPU. The Windows image requires an NVIDIA GPU; CPU-only Windows and AMD or Intel GPUs are not supported by this configuration. See the [detailed setup guide](maya_studio/README.md) for installation and first-run instructions.

### Build the images

From the project root:

```bash
# Mac frontend image
./build.sh mac

# Windows NVIDIA image (Linux AMD64)
./build.sh windows
```

On Windows PowerShell:

```powershell
./build.ps1
```

Building an image does not start the app. Follow the [setup guide](maya_studio/README.md) to run the native Mac engine and frontend, or the Windows Docker Compose service. Model files download on first use and can take several gigabytes.

### Run the published image

After CI has published an image, Docker can select the variant for the machine:

```bash
docker pull <username>/maya-voice-studio:latest
```

On an Apple Silicon Mac, first start the native MLX backend on port 8766 as described in the [setup guide](maya_studio/README.md), then run:

```bash
docker run --rm -p 127.0.0.1:8765:8765 <username>/maya-voice-studio:latest
```

On an NVIDIA-equipped Windows PC using Docker Desktop and WSL 2, run in PowerShell:

```powershell
docker run --rm --gpus all -p 127.0.0.1:8765:8765 -v maya-models:/data/huggingface <username>/maya-voice-studio:latest
```

Architecture selects the image variant, not the host operating system: ARM64 contains the Mac frontend proxy, while AMD64 contains the NVIDIA CUDA engine. Other combinations, such as ARM Windows, Intel Macs, or non-NVIDIA Windows PCs, are not supported by this image.

## Docker Hub CI/CD

The GitHub Actions workflow builds both platform variants and publishes them to one Docker Hub repository on branch pushes. Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `DOCKERHUB_USERNAME` — the Docker Hub account or organization namespace.
- `DOCKERHUB_TOKEN` — an access token permitted to push the image repository.

Both variants are published to `<username>/maya-voice-studio`. Docker selects the ARM64 Mac frontend or AMD64 Windows NVIDIA variant automatically. Every branch push receives a `sha-<full-commit-sha>` tag, and pushes to `master` also update `latest`. The workflow can also be run manually. A successful build does not verify GPU speech generation.

## Security and limitations

The app has no authentication. The supplied Docker Compose files publish the frontend only to localhost. The Mac native engine must listen on a network interface for Docker Desktop to reach it; run it on a trusted network and stop it when not in use. The app processes one generation at a time.

The Mac container frontend and streaming were tested with the native MLX engine. The Windows image was built and its web server was tested, but speech generation on an NVIDIA-equipped Windows machine has not yet been verified.

## Credits

This project uses [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) and [MLX Audio](https://github.com/Blaizzy/mlx-audio). See the model card and upstream projects for their licenses and component attribution, including Kyutai Mimi.
