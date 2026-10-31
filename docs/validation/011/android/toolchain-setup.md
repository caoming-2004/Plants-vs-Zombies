# Android build toolchain

**Status: configured; release APK built 2026-10-30.**

- Build host: Ubuntu 24.04.3 under WSL2.
- Android SDK: command-line tools 15859902, platform API 35, Build Tools 35.0.0, platform-tools 37.0.1.
- Android NDK: 28.2.13676358 (28c); NDK minimum API 24.
- Java: OpenJDK JDK 17 selected by the build script (the system Java 21 runtime is not used for Gradle).
- Python-for-Android: 2026.5.9, isolated Android virtual environment; pygame-ce 2.5.8 recipe.
- ABI: arm64-v8a; landscape orientation; target/compile API 35, minimum API 24.
- Android-only p4a, Gradle, SDK/NDK, and staging/cache live in WSL ext4 at `/home/caoming/.cache/pvz/android`; Windows `build/windows/` and `dist/windows/` were not used by this Android build.
- To keep dependency setup reproducible without pip network access during p4a, required Cython and setuptools wheels are kept under `.tools/android/wheels` and referenced through an Android-only wheelhouse.

Build entry point: `bash packaging/android/build.sh release`. The script writes the arm64 APK to `dist/android/PvzMiniGame-meizu20-arm64.apk` and rejects an existing output rather than overwriting it.
