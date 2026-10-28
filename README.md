# Maya Voice Studio

A local web interface for [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) text-to-speech, with 12 languages, built-in voices, editable demos, streaming, playback controls, emotion cues, and light and dark themes.

## Platforms

- **Apple Silicon macOS:** Run the MLX speech engine natively on the Mac, with a Docker frontend proxy. Docker Desktop's Linux container does not provide this app direct access to the Apple GPU.
- **Linux AMD64:** Run the app and CUDA speech engine in Docker on a host with a compatible NVIDIA GPU. The image built successfully, but inference on an NVIDIA host has not been verified.
- **Linux ARM64:** Not supported yet. The upstream engine pins PyTorch 2.8.0, torchaudio 2.8.0, and Triton 3.4.0; a compatible CUDA ARM64 runtime needs investigation and testing. Do not use the Mac proxy tag as an ARM Linux inference image.

See the [setup guide](maya_studio/README.md) for requirements and commands. Model files download on first use and can take several gigabytes. The app has no authentication; run it only on a trusted network.

## Build

```bash
./build.sh mac    # Apple Silicon frontend proxy
./build.sh linux  # Linux AMD64 NVIDIA CUDA image
```

## Docker Hub publishing

Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as GitHub Actions repository secrets. The token must have permission to push `<username>/maya-voice-studio`. On each branch push, CI builds both variants into that one repository with commit-specific tags. On `master`, it also publishes:

- `<username>/maya-voice-studio:latest-mac-arm64` — Mac frontend proxy; requires the native Mac MLX engine.
- `<username>/maya-voice-studio:latest-linux-amd64` — Linux AMD64 NVIDIA CUDA application.

Separate tags are necessary because both Docker Desktop on Apple Silicon and native ARM Linux use the `linux/arm64` platform identifier, even though their GPU backends differ. There is no supported Linux ARM64 image yet. CI builds do not verify GPU inference.

## Credits

Uses [Maya 2 Native](https://huggingface.co/maya-research/maya2-native) and [MLX Audio](https://github.com/Blaizzy/mlx-audio). See upstream projects for licenses and attribution, including Kyutai Mimi.
