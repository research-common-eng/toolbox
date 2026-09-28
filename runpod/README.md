# Runpod workflow

Generate a temporary GitHub token on a trusted local machine, copy it directly to the clipboard, and paste it into Git's password prompt on Runpod. Keep the GitHub App's private key on your local machine.

## Generate a token locally

On your trusted local machine, run the following from the repository root. Replace the example key path and IDs with your own values; omit `--installation-id` if the app has exactly one installation.

```sh
cd runpod

uv run github_token.py \
  --private-key "/path/to/github-app.private-key.pem" \
  --client-id Iv23liXXXXXXXXXXXXXX \
  --installation-id 12345678  # Not strictly required.
```

| Input | Required? | What to provide |
| --- | --- | --- |
| `--private-key` | Yes | Local path to the app's `.pem` signing key. Download it from the app's settings under **Private keys**; see [GitHub's private-key guide](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps). |
| `--client-id` | Yes | The **Client ID** from the same app's settings page. See [GitHub's JWT guide](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app). |
| `--installation-id` | When multiple installations exist | The numeric ID of the installation to use. With exactly one installation, the helper can select it automatically. |

If the app has no installations, install it first. GitHub's [installation authentication guide](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation#generating-an-installation-access-token) describes API endpoints for finding installation IDs.


The helper sends the token to the clipboard through stdin and prints only a confirmation. It does not put the token in terminal output, process arguments, or a shell variable. Run it on a local desktop with `pbcopy` (macOS), `wl-copy` (Linux/Wayland), or `xclip` (Linux/X11); clipboard failures stop the script without printing the token.

The clipboard contains the token, and clipboard-history tools may retain it. The helper does not clear existing shell history or previously saved credentials.

GitHub sets the token's lifetime to **one hour**. Rerun the helper when you need a fresh token. See [GitHub's token documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app).

## Clone a repository on Runpod

Run this command in the Runpod terminal, replacing the repository path as needed:

```sh
git -c credential.helper= clone https://x-access-token@github.com/my-org/my-repo.git
```

Paste the copied token when Git asks for a password. Password input is hidden and is not entered as a shell command. The URL contains only the username, and `-c credential.helper=` disables credential helpers for this invocation so they do not save the token. See [Git's credential documentation](https://git-scm.com/docs/gitcredentials).

## Set up the pod

From the cloned repository root:

```sh
bash runpod/startup.sh
```

The startup script installs the development tools, tmux, and screen, then calls [the shared Zsh installer](../zsh/set_up_zsh.sh). Keep the `runpod/` and `zsh/` folders together; the script resolves the installer path relative to itself.

It also adds a guarded block to `~/.bashrc` so new interactive Bash sessions start Zsh automatically. Rerunning setup does not duplicate the block, and non-interactive Bash scripts keep using Bash. Open a new terminal after setup; use `bash --norc` when you explicitly need an interactive Bash shell.

## Use agentsview

`startup.sh` installs [agentsview](https://github.com/kenn-io/agentsview), configures `~/.agentsview/config.toml`, and starts the agentsview daemon on the Runpod pod. The configuration sets `public_url = "http://127.0.0.1:9000"` and `daemon_idle_timeout = "0s"` before starting the daemon.

From your local computer, open an SSH tunnel using the `runpod` SSH host configured below:

```sh
ssh -N \
  -p 11945 \
  -L 127.0.0.1:9000:127.0.0.1:8080 \
  -o ExitOnForwardFailure=yes \
  runpod
```

Replace `11945` if your pod uses a different public SSH port. Keep this command running, then open <http://127.0.0.1:9000> in your local browser. The tunnel forwards local port **9000** to port **8080** on the pod.

## Use Eternal Terminal

`startup.sh` installs Eternal Terminal (ET) and starts its server on the pod. Install ET on your local machine too, following the [installation instructions](https://eternalterminal.dev/download/).

Expose the pod's TCP ports **22** (SSH) and **2022** (ET), and note the public port mapped to each. ET uses SSH to establish the session, then connects through its own TCP port; see the [ET user manual](https://eternalterminal.dev/usermanual/).

In the Runpod console, go to **Pods → select your pod → Connect → Direct TCP Ports** (also called **TCP Port Mapping**). Find the entries ending in `:22` and `:2022`; the port beside the public IP is the external port to use. For example, `203.0.113.10:13007 → :22` means SSH uses public port `13007`. Use the corresponding external port from the `:2022` entry for ET. See [Runpod's connection guide](https://docs.runpod.io/pods/configuration/connect-to-ide).

On your local machine, add the following entry to `~/.ssh/config`. Replace the IP address and SSH port placeholders with the pod's connection details, and set `IdentityFile` to the private key you use to SSH into the pod.

```sshconfig
Host runpod
    HostName <runpod-ip>
    User root
    Port <public-port-that-maps-to-22>
    IdentityFile ~/.ssh/id_ed25519
```

First, verify that `ssh runpod` works. Then connect from your local machine, replacing `ET_PUBLIC_PORT` with the public port mapped to the pod's port **2022**:

```sh
et runpod:ET_PUBLIC_PORT
```
