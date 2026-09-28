import contextlib
import io
import json
import runpy
import socket
import subprocess
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

TOKEN = "test-installation-token"
SCRIPT = Path(__file__).with_name("github_token.py")


class GithubTokenTests(unittest.TestCase):
    def run_helper(self, backend="pbcopy", copy_error=None, discover=False):
        argv = [str(SCRIPT), "--private-key", "test.pem", "--client-id", "test-app"]
        if not discover:
            argv += ["--installation-id", "123"]
        payloads = (
            ([{"id": 123}], {"token": TOKEN}) if discover else ({"token": TOKEN},)
        )
        responses = []
        for payload in payloads:
            response = Mock()
            response.__enter__ = Mock(return_value=io.StringIO(json.dumps(payload)))
            response.__exit__ = Mock(return_value=False)
            responses.append(response)
        stdout, stderr = io.StringIO(), io.StringIO()
        fake_jwt = types.SimpleNamespace(encode=Mock(return_value="test-app-jwt"))
        with (
            patch("sys.argv", argv),
            patch("builtins.open", mock_open(read_data=b"test-private-key")),
            patch(
                "shutil.which",
                side_effect=lambda name: name if name == backend else None,
            ),
            patch("urllib.request.urlopen", side_effect=responses) as request,
            patch("subprocess.run", side_effect=copy_error) as copy,
            patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("Network forbidden"),
            ),
            patch.dict("sys.modules", {"jwt": fake_jwt}),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            status = 0
            try:
                runpy.run_path(str(SCRIPT), run_name="__main__")
            except SystemExit as exc:
                status = exc.code
        self.assertEqual(stdout.getvalue(), "")
        self.assertNotIn(TOKEN, stderr.getvalue())
        return status, stderr.getvalue(), request, copy

    def test_clipboard_receives_token_only_through_stdin(self):
        for command in (["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"]):
            with self.subTest(backend=command[0]):
                status, stderr, request, copy = self.run_helper(command[0])
                self.assertEqual(status, 0)
                self.assertIn("copied to clipboard", stderr)
                request.assert_called_once()
                copy.assert_called_once_with(
                    command,
                    input=TOKEN,
                    text=True,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
                self.assertNotIn(TOKEN, copy.call_args.args[0])

    def test_missing_clipboard_stops_before_token_request(self):
        status, stderr, request, copy = self.run_helper(backend=None)
        self.assertEqual(status, 2)
        self.assertIn("Clipboard access requires", stderr)
        request.assert_not_called()
        copy.assert_not_called()

    def test_clipboard_errors_never_print_token(self):
        for error in (
            OSError("clipboard unavailable"),
            subprocess.CalledProcessError(1, ["pbcopy"], stderr=TOKEN),
            subprocess.TimeoutExpired(["pbcopy"], 10, stderr=TOKEN),
        ):
            with self.subTest(error=type(error).__name__):
                status, stderr, _, _ = self.run_helper(copy_error=error)
                self.assertEqual(status, 1)
                self.assertIn("Could not copy", stderr)
                self.assertNotIn("copied to clipboard", stderr)

    def test_single_installation_is_still_discovered(self):
        status, _, request, copy = self.run_helper(discover=True)
        self.assertEqual(status, 0)
        self.assertEqual(request.call_count, 2)
        self.assertTrue(
            request.call_args.args[0].full_url.endswith("/123/access_tokens")
        )
        copy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
