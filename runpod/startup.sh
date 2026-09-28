#!/usr/bin/env bash
set -euo pipefail

startup_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2 || true
}

step() {
  log "==> $1"
}

finish_step() {
  log "<== Finished: $1"
}

on_error() {
  local status="$1"
  local line="$2"
  log "ERROR: setup stopped at line $line (exit $status)"
}

trap 'on_error "$?" "$LINENO"' ERR

step "Starting Pod setup"

# npm & Codex
step "Refresh apt package index"
sudo apt update
finish_step "Refresh apt package index"

step "Install Node.js and npm"
sudo apt install -y nodejs npm tree
finish_step "Install Node.js and npm"

step "Install Codex CLI"
npm install -g @openai/codex
finish_step "Install Codex CLI"

step "Copy Codex configuration"
mkdir -p "$HOME/.codex"
cp "$startup_dir/../codex/config.toml" "$HOME/.codex/config.toml"
finish_step "Copy Codex configuration"

# python
step "Install uv"
log '    + curl -LsSf https://astral.sh/uv/install.sh | sh'
curl -LsSf https://astral.sh/uv/install.sh | sh
finish_step "Install uv"

# Terminal utilities and shared Zsh configuration
step "Install terminal utilities"
sudo apt install -y screen tmux
finish_step "Install terminal utilities"

step "Set up Zsh"
bash "$startup_dir/../zsh/set_up_zsh.sh"
finish_step "Set up Zsh"

step "Use Zsh for interactive Bash sessions"
if ! grep -Fxq '# Start Zsh in interactive Bash sessions.' "$HOME/.bashrc" 2>/dev/null; then
  cat >>"$HOME/.bashrc" <<'EOF'

# Start Zsh in interactive Bash sessions.
if [[ $- == *i* && -z "${ZSH_VERSION:-}" ]] && command -v zsh >/dev/null 2>&1; then
  exec zsh -i
fi
EOF
fi
finish_step "Use Zsh for interactive Bash sessions"

# Eternal Terminal
step "Install Eternal Terminal"
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:jgmath2000/et
sudo apt update
sudo apt install -y et
finish_step "Install Eternal Terminal"

step "Start Eternal Terminal server"
etserver_log="/workspace/logs/${RUNPOD_POD_ID:-default}/etserver.log"
mkdir -p "$(dirname -- "$etserver_log")"
log "Starting etserver; output: $etserver_log"
nohup /usr/bin/etserver --cfgfile=/etc/et.cfg --logtostdout \
  </dev/null >>"$etserver_log" 2>&1 &
etserver_pid=$!
sleep 2
if ! kill -0 "$etserver_pid" 2>/dev/null; then
  log "ERROR: etserver exited during startup. See $etserver_log"
  exit 1
fi
log "Eternal Terminal server started (PID $etserver_pid)."
finish_step "Start Eternal Terminal server"

step "Install agentsview"
curl -fsSL https://agentsview.io/install.sh | bash
finish_step "Install agentsview"

step "Configure agentsview"
mkdir -p "$HOME/.agentsview"
uv_bin="$(command -v uv || printf '%s' "${UV_INSTALL_DIR:-$HOME/.local/bin}/uv")"
"$uv_bin" run --no-project "$startup_dir/configure_agentsview.py" "$HOME/.agentsview/config.toml"
finish_step "Configure agentsview"

step "Start agentsview daemon"
agentsview daemon start
finish_step "Start agentsview daemon"

log "==> Pod setup complete"

# Debug on runpod:
# Check if port 2022 is in use.
# ss -lntp | grep ':2022'
