"""
TextBoard left panel component.

Contains context-specific controls and runs selection.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Checkbox, Label
from textual import log
from textual.reactive import reactive
from typing import List, Tuple


class LeftPanel(Container):
    """Left panel containing runs and context-specific controls."""

    # Local copy of runs data to watch for changes
    runs_data: Tuple[str, ...] = reactive(tuple)

    def __init__(self):
        super().__init__()

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
        """Set up reactive watching when mounted."""
        # Initial sync with app data
        if hasattr(self.app, "runs_data"):
            self.runs_data = self.app.runs_data

        # Set up interval to check for changes from app
        self.set_interval(0.5, self._sync_with_app)

    def _sync_with_app(self) -> None:
        """Periodically sync with app's runs_data."""
        if hasattr(self.app, "runs_data") and self.app.runs_data != self.runs_data:
            self.runs_data = self.app.runs_data

    def watch_runs_data(self, old_value: Tuple[str, ...], new_value: Tuple[str, ...]) -> None:
        """Called when runs_data reactive changes."""
        log.info(f"LeftPanel reactive update: {old_value} -> {new_value}")
        self.update_runs_display(list(new_value))

    def update_runs_display(self, runs: List[str]) -> None:
        """Update the runs section display with new data."""
        try:
            self.runs_data = runs.copy()

            # Remove loading message if it exists
            try:
                loading = self.query_one("#runs-loading")
                loading.remove()
            except Exception:
                pass  # Already removed

            # Clear existing run checkboxes
            runs_container = self.query_one("#runs-section")
            for child in runs_container.children:
                if isinstance(child, Checkbox):
                    child.remove()

            # Add new run checkboxes
            for run in runs:
                checkbox = Checkbox(run, value=True)
                checkbox.id = f"run-{run}"
                runs_container.mount(checkbox)
                log.info(f"Added checkbox for run: {run}")

        except Exception as e:
            log.error(f"Error updating runs display: {e}")
            try:
                loading = self.query_one("#runs-loading")
                loading.update(f"Error: {e}")
            except Exception:
                pass  # Loading element might not exist
