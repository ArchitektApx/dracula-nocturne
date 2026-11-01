#!/bin/sh
# Runs the tests and a full install / undo in Linux containers.
#   tools/linux-test.sh [image...]    default: debian:trixie fedora:latest alpine:latest
set -eu
cd "$(dirname "$0")/.."
[ $# -gt 0 ] || set -- debian:trixie fedora:latest alpine:latest
for image in "$@"; do
  printf '\n=== %s\n' "$image"
  docker run --rm -v "$PWD:/src:ro" -e TERM=xterm-256color "$image" sh -ec '
    if command -v apt-get >/dev/null; then
      apt-get update -qq >/dev/null && apt-get install -y -qq python3 zsh fish tmux lua5.4 neovim bat fzf curl ca-certificates >/dev/null 2>&1
    elif command -v dnf >/dev/null; then
      dnf install -y -q python3 zsh fish tmux lua neovim bat fzf >/dev/null 2>&1
    elif command -v apk >/dev/null; then
      apk add -q python3 zsh fish tmux lua5.4 neovim bat fzf curl bash
    fi
    curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
    export PATH="$HOME/.local/bin:$PATH" UV_LINK_MODE=copy
    cp -r /src /root/nocturne && cd /root/nocturne && rm -rf .venv
    uv run -q pytest -q 2>&1 | tail -2
    uv run -q nocturne check
    touch ~/.bashrc ~/.zshrc && cp ~/.bashrc /tmp/bashrc.before
    uv run -q nocturne install -y --level full >/dev/null
    uv run -q nocturne doctor
    bash -c "source ~/.bashrc; echo \"\$LS_COLORS\" | cut -c1-40; echo \"\$FZF_DEFAULT_OPTS\" | cut -c1-40"
    bat=$(command -v bat || command -v batcat)
    echo "x = 1" > /tmp/x.py && "$bat" --theme="Dracula Nocturne" --color=always -pp /tmp/x.py | grep -q "38;" && echo "bat: themed"
    uv run -q nocturne install --undo >/dev/null
    python3 -c "import filecmp, sys; sys.exit(not filecmp.cmp(sys.argv[1], sys.argv[2], shallow=False))" \
      ~/.bashrc /tmp/bashrc.before && [ ! -e ~/.config/dracula-nocturne ] && echo "undo: clean"
  '
done
