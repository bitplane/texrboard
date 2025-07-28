import pytest
import tarfile
import subprocess
import time
import socket
from pathlib import Path


@pytest.fixture
def logdir(tmpdir_factory):
    """Fixture that provides access to extracted TensorBoard log directories.

    Usage:
        def test_something(logdir):
            path = logdir('tacotron2-melvyn-bragg')
            # do stuff with the path

    The fixture extracts ./tests/data/{name}.tar.gz into a temporary directory
    and returns the path. Cleanup is handled automatically by pytest.
    """

    def _load_logdir(name: str) -> str:
        # Path to the archive file
        archive_path = Path(__file__).parent / "data" / f"{name}.tar.gz"

        if not archive_path.exists():
            available_files = []
            data_dir = Path(__file__).parent / "data"
            if data_dir.exists():
                available_files = [f.stem.replace(".tar", "") for f in data_dir.glob("*.tar.gz")]

            raise FileNotFoundError(
                f"Archive {name}.tar.gz not found in tests/data/. " f"Available archives: {available_files}"
            )

        # Create temporary directory
        tmpdir = tmpdir_factory.mktemp(f"logdir_{name}")

        # Extract archive with filter for Python 3.14 compatibility
        with tarfile.open(archive_path, "r:gz") as tar:
            # Use 'data' filter to safely extract (available in Python 3.12+)
            try:
                tar.extractall(path=tmpdir, filter="data")
            except TypeError:
                # Fallback for older Python versions
                tar.extractall(path=tmpdir)

        # If there's only one directory in the extraction, return that directory
        contents = list(tmpdir.listdir())
        if len(contents) == 1 and contents[0].isdir():
            return str(contents[0])

        return str(tmpdir)

    return _load_logdir


def _find_free_port():
    """Find a free port to use for TensorBoard server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture
def tensorboard_server(logdir):
    """Fixture that starts a TensorBoard server with extracted log data.

    Usage:
        def test_something(tensorboard_server):
            url = tensorboard_server('tacotron2-melvyn-bragg')
            # test with TensorBoard server at url

    The fixture starts TensorBoard with the specified log directory,
    waits for it to be ready, yields the server URL, then cleans up.
    """

    def _start_server(dataset_name: str) -> str:
        # Get the log directory using the logdir fixture
        log_path = logdir(dataset_name)

        # Find a free port
        port = _find_free_port()

        # Start TensorBoard server
        cmd = [
            "tensorboard",
            "--logdir",
            log_path,
            "--port",
            str(port),
            "--host",
            "localhost",
            "--reload_interval",
            "1",
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait for server to start (check if port is open)
        server_url = f"http://localhost:{port}"
        max_wait = 30  # seconds
        wait_time = 0.1

        for _ in range(int(max_wait / wait_time)):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(("localhost", port))
                    if result == 0:
                        # Give it a moment more to fully initialize
                        time.sleep(0.5)
                        break
            except Exception:
                pass
            time.sleep(wait_time)
        else:
            # If we get here, server didn't start
            process.terminate()
            stdout, stderr = process.communicate()
            raise RuntimeError(
                f"TensorBoard server failed to start within {max_wait}s.\n" f"stdout: {stdout}\nstderr: {stderr}"
            )

        # Store process reference for cleanup
        _start_server._process = process
        return server_url

    yield _start_server

    # Cleanup: terminate the server if it was started
    if hasattr(_start_server, "_process"):
        _start_server._process.terminate()
        _start_server._process.wait(timeout=5)
