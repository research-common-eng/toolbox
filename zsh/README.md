# Zsh setup

Shell configuration with aliases, history and completion settings, a Starship prompt, fzf, zoxide, autosuggestions, and syntax highlighting.

## Setup

- **macOS:** Requires Bash, Zsh, and Homebrew, with `brew` on your `PATH`.
- **Linux:** Supports Debian/Ubuntu with Bash, `apt-get`, and root or `sudo` access. Downloads require network access; on Ubuntu, the Universe repository must be enabled for the shell-tool packages.

From the repository root:

```sh
bash zsh/set_up_zsh.sh
```

From this folder:

```sh
bash set_up_zsh.sh
```

You can also run the script from elsewhere using its absolute path. It locates the configuration files relative to itself.

Start a new Zsh session after installation to load the configuration.

## What gets installed

The [setup script](set_up_zsh.sh) installs Starship, fzf, zoxide, autosuggestions, and syntax highlighting:

- **macOS:** Uses Homebrew.
- **Linux:** Uses `apt-get` for Zsh, fzf, zoxide, and the Zsh plugins. Installs Starship into `~/.local/bin` using its [official installer](https://starship.rs/guide/#step-1-install-starship), which also works on older releases without a Starship package.

It copies `.zsh/` into your home directory, appends configuration-loading commands to `~/.zshrc`, and copies the Starship configuration to `~/.config/starship.toml`. The shell configuration adds `~/.local/bin` to `PATH` and loads plugins from their installation directory.

Running it again overwrites matching configuration files and appends another set of loading commands to `~/.zshrc`.
