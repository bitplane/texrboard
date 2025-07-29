"""
TensorBoard server management.

Handles starting, stopping, and managing embedded TensorBoard server instances.
"""

import subprocess
import socket
import time
import tempfile
import tarfile
from pathlib import Path
from typing import Optional

from textual import log


def find_free_port() -> int:
    """Find a free port to use for TensorBoard server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def extract_log_archive(archive_path: str) -> str:
    """Extract a .tar.gz log archive to temporary directory."""
    archive_path = Path(archive_path)

    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    # Create temporary directory
    tmpdir = Path(tempfile.mkdtemp(prefix="textboard_logs_"))

    # Extract archive
    with tarfile.open(archive_path, "r:gz") as tar:
        try:
            tar.extractall(path=tmpdir, filter="data")
        except TypeError:
            # Fallback for older Python versions
            tar.extractall(path=tmpdir)

    # If there's only one directory in extraction, return that directory
    contents = list(tmpdir.iterdir())
    if len(contents) == 1 and contents[0].is_dir():
        return str(contents[0])

    return str(tmpdir)


class TensorBoardManager:
    """Manages an embedded TensorBoard server process."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.server_url: Optional[str] = None

    def start_server(self, logdir: str) -> str:
        """Start TensorBoard server with given logdir."""
        port = find_free_port()

        cmd = ["tensorboard", "--logdir", logdir, "--port", str(port), "--host", "localhost", "--reload_interval", "1"]

        log.info(f"Starting TensorBoard: {' '.join(cmd)}")
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait for server to start
        server_url = f"http://localhost:{port}"
        max_wait = 30
        wait_time = 0.1

        for _ in range(int(max_wait / wait_time)):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(("localhost", port))
                    if result == 0:
                        time.sleep(0.5)  # Give it a moment to fully initialize
                        break
            except Exception:
                pass
            time.sleep(wait_time)
        else:
            stdout, stderr = self.process.communicate()
            raise RuntimeError(
                f"TensorBoard server failed to start within {max_wait}s.\n" f"stdout: {stdout}\nstderr: {stderr}"
            )

        self.server_url = server_url
        log.info(f"TensorBoard started at: {server_url}")
        return server_url

    def stop_server(self):
        """Stop the TensorBoard server."""
        if self.process:
            log.info("Stopping TensorBoard server")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            self.server_url = None
