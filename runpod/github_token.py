import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

import jwt


def github_request(method, path, app_jwt):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {app_jwt}",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        print(f"GitHub API error ({exc.code}): {body}", file=sys.stderr)
        sys.exit(1)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--private-key", help="Path to GitHub App private .pem key", required=True
)
parser.add_argument("--client-id", required=True)
parser.add_argument("--installation-id")
args = parser.parse_args()

clipboard_commands = (
    ["pbcopy"],
    ["wl-copy"],
    ["xclip", "-selection", "clipboard"],
)
clipboard_command = next(
    (command for command in clipboard_commands if shutil.which(command[0])),
    None,
)
if clipboard_command is None:
    parser.error("Clipboard access requires pbcopy (macOS), wl-copy, or xclip (Linux).")


with open(args.private_key, "rb") as f:
    private_key = f.read()


now = int(time.time())

app_jwt = jwt.encode(
    {
        "iat": now - 60,
        "exp": now + 600,
        "iss": args.client_id,
    },
    private_key,
    algorithm="RS256",
)


installation_id = args.installation_id

if not installation_id:
    installations = github_request(
        "GET",
        "/app/installations",
        app_jwt,
    )

    if len(installations) != 1:
        print(
            f"Found {len(installations)} installations. Pass --installation-id.",
            file=sys.stderr,
        )
        sys.exit(1)

    installation_id = installations[0]["id"]


result = github_request(
    "POST",
    f"/app/installations/{installation_id}/access_tokens",
    app_jwt,
)

# Send the token through stdin, never command arguments or terminal output.
try:
    subprocess.run(
        clipboard_command,
        input=result["token"],
        text=True,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10,
    )
except (OSError, subprocess.SubprocessError):
    print(
        "Could not copy the token. Check clipboard access and rerun.", file=sys.stderr
    )
    sys.exit(1)

print("GitHub token copied to clipboard.", file=sys.stderr)
