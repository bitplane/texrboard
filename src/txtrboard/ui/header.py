"""
TextBoard header component.

Custom header with app title on the left and control buttons on the right.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Button, Tabs, Tab, Select


class RightControls(Container):
    """Right side controls - refresh, settings, help."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Select(
                [("5s", "5s"), ("10s", "10s"), ("30s", "30s"), ("1m", "1m"), ("5m", "5m")],
                value="30s",
                id="refresh-interval",
                allow_blank=False,
            )
            yield Button("Refresh", id="refresh-btn", variant="primary")
            yield Button("Settings", id="settings-btn", variant="default")
            yield Button("Help", id="help-btn", variant="default")


class HeaderTabs(Container):
    """Tab navigation in header."""

    def compose(self) -> ComposeResult:
        with Tabs():
            yield Tab("SCALARS", id="scalars")
            yield Tab("IMAGES", id="images")
            yield Tab("HISTOGRAMS", id="histograms")
            yield Tab("GRAPHS", id="graphs")


class TextBoardHeader(Container):
    """Custom header with txtrboard title, tabs, and controls."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-content"):
            yield Static("txtrboard", id="app-title")
            with Tabs(id="main-tabs"):
                yield Tab("SCALARS")
                yield Tab("IMAGES")
                yield Tab("HISTOGRAMS")
                yield Tab("GRAPHS")
            with Horizontal(id="right-controls"):
                yield Select(
                    [
                        ("INACTIVE", "INACTIVE"),
                        ("5s", "5s"),
                        ("10s", "10s"),
                        ("30s", "30s"),
                        ("1m", "1m"),
                        ("5m", "5m"),
                    ],
                    value="INACTIVE",
                    id="refresh-interval",
                    allow_blank=False,
                )
                yield Button("☀", id="theme-btn", variant="default")
                yield Button("🗘", id="refresh-btn", variant="primary")
                yield Button("⚙", id="settings-btn", variant="default")
                yield Button("🛈", id="help-btn", variant="default")
