# /// script
# requires-python = ">=3.11"
# dependencies = ["tomlkit==0.15.1"]
# ///
import sys
from pathlib import Path

import tomlkit


def configure(path):
    document = tomlkit.parse(path.read_text()) if path.exists() else tomlkit.document()
    document["public_url"] = "http://127.0.0.1:9000"
    document["daemon_idle_timeout"] = "0s"
    content = tomlkit.dumps(document)
    tomlkit.parse(content)
    path.write_text(content)


if __name__ == "__main__":
    configure(Path(sys.argv[1]))
