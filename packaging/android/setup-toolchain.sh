#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ANDROID_ROOT="$ROOT/.tools/android"
WSL_STORAGE_ROOT="${ANDROID_WSL_STORAGE_ROOT:-$HOME/.cache/pvz/android}"
SDK_DIR="$WSL_STORAGE_ROOT/sdk"
PYTHON="${ANDROID_PYTHON:-python3}"
SDK_TOOLS_VERSION="15859902"
NDK_VERSION="28.2.13676358"
ANDROID_API="35"
BUILD_TOOLS_VERSION="35.0.0"
SDK_TOOLS_SHA256="4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583"
SDK_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-${SDK_TOOLS_VERSION}_latest.zip"

for tool in curl sha256sum unzip tar java; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "Missing Android host prerequisite: $tool" >&2
    echo "Install python-for-android's Ubuntu prerequisites first; see its official quickstart." >&2
    exit 2
  }
done
if ! java -version 2>&1 | grep -Eq 'version "(1\.)?(17|[2-9][0-9])'; then
  echo "Java 17 or newer is required." >&2
  java -version >&2
  exit 2
fi

mkdir -p "$ANDROID_ROOT" "$WSL_STORAGE_ROOT"
link_android_path() {
  local project_path="$1" storage_path="$2"
  mkdir -p "$(dirname "$storage_path")"
  if [[ -L "$project_path" ]]; then
    [[ "$(realpath -m "$project_path")" == "$(realpath -m "$storage_path")" ]] || {
      echo "Android path points to a different target: $project_path" >&2
      exit 2
    }
    return
  fi
  if [[ -e "$project_path" ]]; then
    echo "Refusing to replace existing Android-owned path: $project_path" >&2
    exit 2
  fi
  ln -s "$storage_path" "$project_path"
}
for item in sdk venv pip-cache p4a-storage gradle; do
  link_android_path "$ANDROID_ROOT/$item" "$WSL_STORAGE_ROOT/$item"
done
link_android_path "$ROOT/build/android" "$WSL_STORAGE_ROOT/build"
printf '%s\n' "$WSL_STORAGE_ROOT" > "$ANDROID_ROOT/storage-path"

TEMP_DIR="$(mktemp -d "$WSL_STORAGE_ROOT/.setup-XXXXXX")"
case "$TEMP_DIR" in
  "$WSL_STORAGE_ROOT"/.setup-*) ;;
  *) echo "Unsafe temporary directory: $TEMP_DIR" >&2; exit 2 ;;
esac
trap 'rm -rf "$TEMP_DIR"' EXIT

SDKMANAGER="$SDK_DIR/cmdline-tools/latest/bin/sdkmanager"
if [[ ! -x "$SDKMANAGER" ]]; then
  ARCHIVE="$TEMP_DIR/commandlinetools.zip"
  curl --fail --location --retry 3 "$SDK_TOOLS_URL" --output "$ARCHIVE"
  echo "$SDK_TOOLS_SHA256  $ARCHIVE" | sha256sum --check --status || {
    echo "Android command-line tools checksum mismatch." >&2
    exit 1
  }
  mkdir -p "$TEMP_DIR/sdk" "$SDK_DIR/cmdline-tools"
  unzip -q "$ARCHIVE" -d "$TEMP_DIR/sdk"
  if [[ -e "$SDK_DIR/cmdline-tools/latest" ]]; then
    echo "Refusing to overwrite existing Android command-line tools." >&2
    exit 2
  fi
  mv "$TEMP_DIR/sdk/cmdline-tools" "$SDK_DIR/cmdline-tools/latest"
fi

export ANDROID_HOME="$SDK_DIR"
export ANDROID_SDK_ROOT="$SDK_DIR"
export GRADLE_USER_HOME="$WSL_STORAGE_ROOT/gradle"
export JAVA_HOME="${JAVA_HOME:-$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")}"
export PATH="$SDK_DIR/cmdline-tools/latest/bin:$SDK_DIR/platform-tools:$JAVA_HOME/bin:$PATH"

set +o pipefail
yes | "$SDKMANAGER" --sdk_root="$SDK_DIR" --licenses >/dev/null
set -o pipefail
"$SDKMANAGER" --sdk_root="$SDK_DIR" \
  "platform-tools" \
  "platforms;android-${ANDROID_API}" \
  "build-tools;${BUILD_TOOLS_VERSION}" \
  "ndk;${NDK_VERSION}"

VENV="$WSL_STORAGE_ROOT/venv"
if [[ ! -x "$VENV/bin/p4a" ]]; then
  "$PYTHON" -m venv "$VENV"
  PIP_CACHE_DIR="$WSL_STORAGE_ROOT/pip-cache" \
    "$VENV/bin/python" -m pip install --upgrade pip
  PIP_CACHE_DIR="$WSL_STORAGE_ROOT/pip-cache" \
    "$VENV/bin/python" -m pip install -r "$ROOT/packaging/android/requirements-build.txt"
fi

"$VENV/bin/python" -m pythonforandroid.toolchain --version
java -version
"$SDKMANAGER" --sdk_root="$SDK_DIR" --list_installed
