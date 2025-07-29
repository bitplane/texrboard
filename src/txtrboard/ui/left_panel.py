"""
TextBoard left panel component.

Contains context-specific controls and runs selection.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Checkbox, Label
from textual import log

from txtrboard.client import TensorBoardClient


class LeftPanel(Container):
    """Left panel containing runs and context-specific controls."""

    def __init__(self):
        super().__init__()
        self.runs_data = []
        self._client = None

    def compose(self) -> ComposeResult:
        with Vertical():
            with Container(id="context-controls"):
                yield Label("Scalars Controls")
                yield Static("• Smoothing: 0.6")
                yield Static("• Y-axis: Auto")
            with Container(id="runs-section"):
                yield Label("Runs")
                yield Static("Loading...", id="runs-loading")

    def on_mount(self) -> None:
        """When panel is mounted, check if we have a client and load runs."""
        if self._client:
            self.update_runs(self._client)

    def set_client(self, client: TensorBoardClient) -> None:
        """Set the TensorBoard client and trigger an update."""
        self._client = client
        if self.is_mounted:
            self.update_runs(client)

    def update_runs(self, client: TensorBoardClient):
        """Update the runs section with data from TensorBoard."""
        try:
            runs = client.get_runs()
            self.runs_data = runs.runs
            log.info(f"Got runs: {runs.runs}")

            # Remove loading message if it exists
            try:
                loading = self.query_one("#runs-loading")
                loading.remove()
            except Exception:
                pass  # Already removed

            # Add run checkboxes
            runs_container = self.query_one("#runs-section")
            for run in runs.runs:
                checkbox = Checkbox(run, value=True)
                checkbox.id = f"run-{run}"
                runs_container.mount(checkbox)
                log.info(f"Added checkbox for run: {run}")

        except Exception as e:
            log.error(f"Error loading runs: {e}")
            try:
                loading = self.query_one("#runs-loading")
                loading.update(f"Error: {e}")
            except Exception:
                pass  # Loading element might not exist
