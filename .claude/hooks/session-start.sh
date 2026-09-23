#!/bin/bash
# Installiert yt-dlp und ffmpeg, um YouTube-Tonspuren herunterzuladen.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg >/dev/null
fi

pip install -q -U yt-dlp 2>&1 | grep -v "Running pip as the 'root' user" || true

yt-dlp --version
ffmpeg -version | head -1
