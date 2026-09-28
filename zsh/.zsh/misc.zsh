# --------------------
# History
# --------------------
# avoids saving consecutive duplicate commands in history
setopt HIST_IGNORE_DUPS

# shares command history between multiple open Zsh terminals
# setopt SHARE_HISTORY

# enter a directory name without typing cd
setopt AUTO_CD


# --------------------
# Completion
# --------------------
autoload -Uz compinit
compinit

zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# --------------------
# Useful tools
# --------------------
# The Linux installer puts Starship in this directory.
path=("$HOME/.local/bin" $path)

command -v zoxide >/dev/null && eval "$(zoxide init zsh)"

if [[ -r /usr/share/doc/fzf/examples/key-bindings.zsh ]]; then
  source /usr/share/doc/fzf/examples/key-bindings.zsh
  [[ -r /usr/share/doc/fzf/examples/completion.zsh ]] &&
    source /usr/share/doc/fzf/examples/completion.zsh
elif command -v fzf >/dev/null && fzf --zsh >/dev/null 2>&1; then
  source <(fzf --zsh)
fi

# Starship prompt
eval "$(starship init zsh)"

# Autosuggestions
if [[ "$OSTYPE" == darwin* ]]; then
  zsh_plugin_prefix="$(brew --prefix)"
else
  zsh_plugin_prefix="/usr"
fi
source "$zsh_plugin_prefix/share/zsh-autosuggestions/zsh-autosuggestions.zsh"

# Keep highlighting near the end
source "$zsh_plugin_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
