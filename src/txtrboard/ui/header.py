"""
TextBoard header component.

Custom header with app title on the left and control buttons on the right.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Button


class RightControls(Container):
    """Right side controls - refresh, settings, help."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("30s", id="refresh-interval")  # Will become dropdown
            yield Button("⟳", id="refresh-btn", variant="primary")
            yield Button("⚙", id="settings-btn", variant="default")
            yield Button("?", id="help-btn", variant="default")


class TextBoardHeader(Container):
    """Custom header with TextBoard title and right controls."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("TextBoard", id="app-title")
            yield RightControls()
