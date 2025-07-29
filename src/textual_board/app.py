#!/usr/bin/env python3
"""
TextBoard - TUI replacement for TensorBoard

A terminal-based interface for viewing TensorBoard logs and metrics.
"""

import argparse
import sys
import tempfile
import tarfile
import subprocess
import socket
import time
import atexit
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, TabbedContent, TabPane, Static, Button, Checkbox, Label
from textual import log

from src.textual_board.tensorboard_client import TensorBoardClient, TensorBoardConnectionError


def find_free_port() -> int:
    """Find a free port to use for TensorBoard server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


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


class LeftPanel(Container):
    """Left panel containing runs and context-specific controls."""

    def __init__(self):
        super().__init__()
        self.runs_data = []

    def compose(self) -> ComposeResult:
        with Vertical():
            with Container(id="context-controls"):
                yield Label("Scalars Controls")
                yield Static("• Smoothing: 0.6")
                yield Static("• Y-axis: Auto")
            with Container(id="runs-section"):
                yield Label("Runs")
                yield Static("Loading...", id="runs-loading")

    def update_runs(self, client: TensorBoardClient):
        """Update the runs section with data from TensorBoard."""
        try:
            runs = client.get_runs()
            self.runs_data = runs.runs

            # Remove loading message
            loading = self.query_one("#runs-loading")
            loading.remove()

            # Add run checkboxes
            runs_container = self.query_one("#runs-section")
            for run in runs.runs:
                checkbox = Checkbox(run, value=True)
                checkbox.id = f"run-{run}"
                runs_container.mount(checkbox)

        except Exception as e:
            loading = self.query_one("#runs-loading")
            loading.update(f"Error: {e}")


class RightControls(Container):
    """Right side controls - refresh, settings, help."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("30s", id="refresh-interval")  # Will become dropdown
            yield Button("⟳", id="refresh-btn", variant="primary")
            yield Button("⚙", id="settings-btn", variant="default")
            yield Button("?", id="help-btn", variant="default")


class CustomHeader(Container):
    """Custom header with TextBoard title and right controls."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("TextBoard", id="app-title")
            yield RightControls()


class TextBoardApp(App):
    """Main TextBoard TUI application."""

    CSS = """
    CustomHeader {
        dock: top;
        height: 3;
        background: $surface;
        border-bottom: solid $primary;
    }

    CustomHeader Horizontal {
        height: 3;
        align: center middle;
    }

    #app-title {
        padding: 0 2;
        text-style: bold;
        color: $primary;
        content-align: center middle;
    }

    RightControls {
        dock: right;
        width: auto;
    }

    RightControls Horizontal {
        height: 3;
        align: center middle;
    }

    RightControls Button {
        margin: 0 1;
        min-width: 3;
    }

    LeftPanel {
        dock: left;
        width: 25%;
        border-right: solid $primary;
    }

    #context-controls {
        height: 50%;
        border-bottom: solid $primary;
        padding: 1;
    }

    #runs-section {
        height: 50%;
        padding: 1;
    }

    TabbedContent {
        margin: 1;
    }
    """

    def __init__(self, server_url: Optional[str] = None):
        super().__init__()
        self.server_url = server_url
        self.client: Optional[TensorBoardClient] = None
        self.tb_manager = TensorBoardManager()

        # Register cleanup
        atexit.register(self.cleanup)

    def compose(self) -> ComposeResult:
        yield CustomHeader()
        yield LeftPanel()

        with TabbedContent():
            with TabPane("Scalars", id="scalars-tab"):
                yield Static("Scalar plots will go here", id="scalars-content")

            with TabPane("Images", id="images-tab"):
                yield Static("Image displays will go here", id="images-content")

            with TabPane("Histograms", id="histograms-tab"):
                yield Static("Histogram plots will go here", id="histograms-content")

            with TabPane("Graphs", id="graphs-tab"):
                yield Static("Graph visualization will go here", id="graphs-content")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the TensorBoard client connection."""
        try:
            self.client = TensorBoardClient(self.server_url or "http://localhost:6006")
            # Test connection
            env = self.client.get_environment()
            log.info(f"Connected to TensorBoard {env.version}")
            self.title = f"TextBoard - {env.version}"

            # Update the left panel with runs data
            left_panel = self.query_one(LeftPanel)
            left_panel.update_runs(self.client)

        except TensorBoardConnectionError as e:
            log.error(f"Failed to connect to TensorBoard: {e}")
            self.title = "TextBoard - Connection Failed"

    def cleanup(self):
        """Clean up resources."""
        if self.client:
            self.client.close()
        self.tb_manager.stop_server()


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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="TextBoard - TUI replacement for TensorBoard")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--logdir", help="Path to TensorBoard logs directory (starts embedded server)")
    group.add_argument("--log-file", help="Path to .tar.gz log archive (extracts and starts embedded server)")
    group.add_argument("--host", default="localhost", help="TensorBoard server host (default: localhost)")

    parser.add_argument("--port", type=int, default=6006, help="TensorBoard server port (default: 6006)")

    args = parser.parse_args()

    tb_manager = TensorBoardManager()
    server_url = None

    try:
        if args.logdir:
            # Start embedded server with logdir
            server_url = tb_manager.start_server(args.logdir)
        elif args.log_file:
            # Extract archive and start embedded server
            logdir = extract_log_archive(args.log_file)
            server_url = tb_manager.start_server(logdir)
        else:
            # Connect to existing server
            server_url = f"http://{args.host}:{args.port}"

        # Start the TUI
        app = TextBoardApp(server_url)
        app.tb_manager = tb_manager  # Pass manager for cleanup
        app.run()

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        tb_manager.stop_server()


if __name__ == "__main__":
    main()
