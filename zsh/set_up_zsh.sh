#!/usr/bin/env bash
set -euo pipefail

zsh_setup_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

case "$(uname -s)" in
Darwin)
  brew install starship fzf zoxide zsh-autosuggestions zsh-syntax-highlighting
  ;;
Linux)
  # Debian/Ubuntu, including Runpod images. Use sudo only when needed.
  zsh_apt=(apt-get)
  if [[ "$(id -u)" -ne 0 ]]; then
    zsh_apt=(sudo apt-get)
  fi
  "${zsh_apt[@]}" update
  "${zsh_apt[@]}" install -y zsh fzf zoxide zsh-autosuggestions \
    zsh-syntax-highlighting curl ca-certificates tar gzip

  # Starship is unavailable in older Ubuntu/Debian package repositories.
  mkdir -p "$HOME/.local/bin"
  curl -fsSL https://starship.rs/install.sh | sh -s -- -y -b "$HOME/.local/bin"
  ;;
*)
  echo "Supported operating systems: macOS and Debian/Ubuntu Linux." >&2
  exit 1
  ;;
esac

echo "Setting up zsh"
cp -r "$zsh_setup_dir/.zsh" "$HOME/"
cat >>"$HOME/.zshrc" <<'EOF'

# zsh
source $HOME/.zsh/aliases.zsh
source $HOME/.zsh/exports.zsh
source $HOME/.zsh/functions.zsh
source $HOME/.zsh/misc.zsh
source $HOME/.zsh/prompt.zsh
EOF

mkdir -p "$HOME/.config"
cp "$zsh_setup_dir/.config/starship.toml" "$HOME/.config/"
