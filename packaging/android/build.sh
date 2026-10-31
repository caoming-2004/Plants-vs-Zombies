#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-release}"
if [[ "$MODE" != "smoke" && "$MODE" != "release" ]]; then
  echo "usage: $0 [smoke|release]" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ANDROID_ROOT="$ROOT/.tools/android"
ANDROID_STORAGE_ROOT="$ANDROID_ROOT"
if [[ -f "$ANDROID_ROOT/storage-path" ]]; then
  IFS= read -r ANDROID_STORAGE_ROOT < "$ANDROID_ROOT/storage-path"
fi
ANDROID_STORAGE_ROOT="$(realpath -m "$ANDROID_STORAGE_ROOT")"
ANDROID_BUILD="$(realpath -m "$ROOT/build/android")"
SDK_DIR="$ANDROID_STORAGE_ROOT/sdk"
NDK_DIR="$SDK_DIR/ndk/28.2.13676358"
P4A="$ANDROID_STORAGE_ROOT/venv/bin/p4a"
P4A_STORAGE="$ANDROID_STORAGE_ROOT/p4a-storage"
GRADLE_HOME="$ANDROID_STORAGE_ROOT/gradle"
APP_VERSION="0.6.1"

for required in "$P4A" "$SDK_DIR/platforms/android-35" "$SDK_DIR/build-tools" "$NDK_DIR/source.properties"; do
  if [[ ! -e "$required" ]]; then
    echo "Android toolchain component is missing: $required" >&2
    echo "Install the Android-only toolchain under .tools/android and install packaging/android/requirements-build.txt there." >&2
    exit 2
  fi
done
if ! command -v java >/dev/null 2>&1 || ! command -v javac >/dev/null 2>&1; then
  echo "A full JDK is unavailable in this Linux/WSL environment." >&2
  exit 2
fi
if [[ -z "${JAVA_HOME:-}" || ! -x "$JAVA_HOME/bin/javac" ]]; then
  JAVAC_PATH="$(readlink -f "$(command -v javac)")"
  JAVA_HOME="$(dirname "$(dirname "$JAVAC_PATH")")"
fi
if ! "$JAVA_HOME/bin/java" -version 2>&1 | grep -Eq 'version "(1\.)?(17|[2-9][0-9])'; then
  echo "Java 17 or newer is required; current Java is:" >&2
  "$JAVA_HOME/bin/java" -version >&2
  exit 2
fi

mkdir -p "$ANDROID_BUILD" "$P4A_STORAGE" "$GRADLE_HOME" "$ROOT/docs/validation/011/android"
RUN_DIR="$(mktemp -d "$ANDROID_BUILD/staging-${MODE}-XXXXXX")"
PRIVATE_DIR="$RUN_DIR/private"
mkdir -p "$PRIVATE_DIR" "$RUN_DIR/p4a-recipes"
cp "$ROOT/packaging/android/app-config/.p4a" "$RUN_DIR/.p4a"
cp -a "$ROOT/packaging/android/p4a-recipes/." "$RUN_DIR/p4a-recipes/"

if [[ "$MODE" == "smoke" ]]; then
  cp "$ROOT/packaging/android/smoke/main.py" "$PRIVATE_DIR/main.py"
  cp -a "$ROOT/packaging/android/smoke/assets" "$PRIVATE_DIR/assets"
  APP_NAME="PVZ Android Check"
  PACKAGE_ID="com.pvzmini.androidcheck"
else
  APP_SOURCE="$ROOT/packaging/android/app"
  if [[ ! -f "$APP_SOURCE/main.py" ]]; then
    echo "Android app entry point is missing: $APP_SOURCE/main.py" >&2
    exit 2
  fi
  cp "$APP_SOURCE/main.py" "$PRIVATE_DIR/main.py"
  cp -a "$ROOT/src" "$PRIVATE_DIR/src"
  python3 "$ROOT/packaging/android/copy_runtime_assets.py" "$ROOT/assets" "$PRIVATE_DIR/assets"
  APP_NAME="狗狗植物大战"
  PACKAGE_ID="com.pvzmini.doggame"
fi

export ANDROID_HOME="$SDK_DIR"
export ANDROID_SDK_ROOT="$SDK_DIR"
export ANDROID_NDK_HOME="$NDK_DIR"
export GRADLE_USER_HOME="$GRADLE_HOME"
export JAVA_HOME
export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$ROOT/.tools/android/wheels"
export PIP_CACHE_DIR="$ANDROID_STORAGE_ROOT/pip-cache"
export PATH="$SDK_DIR/cmdline-tools/latest/bin:$SDK_DIR/platform-tools:$JAVA_HOME/bin:$PATH"

LOG="$(date -u +%Y%m%dT%H%M%SZ)-${MODE}.log"
(
  cd "$RUN_DIR"
  "$P4A" apk \
    --private "$PRIVATE_DIR" \
    --package "$PACKAGE_ID" \
    --name "$APP_NAME" \
    --version "$APP_VERSION" \
    --storage-dir "$P4A_STORAGE" \
    --local-recipes "$RUN_DIR/p4a-recipes" \
    --sdk-dir "$SDK_DIR" \
    --ndk-dir "$NDK_DIR" \
    --debug
) 2>&1 | tee "$ROOT/docs/validation/011/android/$LOG"

shopt -s nullglob
PACKAGES=("$RUN_DIR"/*.apk)
if [[ "${#PACKAGES[@]}" -ne 1 ]]; then
  echo "Expected exactly one APK in the Android staging folder, found ${#PACKAGES[@]}" >&2
  exit 1
fi
if [[ "$MODE" == "release" ]]; then
  OUTPUT="$ROOT/dist/android/PvzMiniGame-meizu20-arm64.apk"
  if [[ -e "$OUTPUT" ]]; then
    echo "Refusing to overwrite existing Android deliverable: $OUTPUT" >&2
    exit 2
  fi
  mkdir -p "$(dirname "$OUTPUT")"
  cp "${PACKAGES[0]}" "$OUTPUT"
  echo "APK written to $OUTPUT"
else
  echo "Smoke APK retained only under $RUN_DIR"
fi
