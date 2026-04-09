#!/usr/bin/env bash
set -euo pipefail

dest="${1:-$(pwd)/gpumd-tool-sources}"
mkdir -p "$dest"

clone_or_update() {
  local name="$1"
  local url="$2"
  if [ -d "$dest/$name/.git" ]; then
    git -C "$dest/$name" pull --ff-only
  elif [ -d "$dest/$name" ]; then
    echo "skip $name: directory exists but is not a git repo" >&2
  else
    git clone --depth 1 "$url" "$dest/$name"
  fi
}

clone_or_update GPUMD https://github.com/brucefan1983/GPUMD.git
clone_or_update GPUMD-Tutorials https://github.com/brucefan1983/GPUMD-Tutorials.git
clone_or_update GPUMDkit https://github.com/zhyan0603/GPUMDkit.git
clone_or_update NepTrain https://github.com/aboys-cb/NepTrain.git
clone_or_update NepTrainKit https://github.com/aboys-cb/NepTrainKit.git

echo "tool sources available at: $dest"
