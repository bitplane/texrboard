"""
TextBoard main application.

The main TUI application class that coordinates all components.
"""

import atexit
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Footer, TabbedContent, TabPane, Static, Button
from textual import log

from txtrboard.client import TensorBoardClient, TensorBoardConnectionError
from txtrboard.server import TensorBoardManager
from txtrboard.ui.theme import register_themes, get_default_theme
from txtrboard.ui.left_panel import LeftPanel
from txtrboard.ui.header import TextBoardHeader


class TextBoardApp(App):
    """Main TextBoard TUI application."""

    # Load CSS from external file
    CSS_PATH = Path(__file__).parent / "app.tcss"

    def __init__(self, server_url: Optional[str] = None):
        super().__init__()
        self.server_url = server_url
        self.client: Optional[TensorBoardClient] = None
        self.tb_manager = TensorBoardManager()

        # Register cleanup
        atexit.register(self.cleanup)

    def compose(self) -> ComposeResult:
        yield TextBoardHeader()
        yield LeftPanel()

        with TabbedContent():
            with TabPane("SCALARS", id="scalars-tab"):
                yield Static("Scalar plots will go here", id="scalars-content")

            with TabPane("IMAGES", id="images-tab"):
                yield Static("Image displays will go here", id="images-content")

            with TabPane("HISTOGRAMS", id="histograms-tab"):
                yield Static("Histogram plots will go here", id="histograms-content")

            with TabPane("GRAPHS", id="graphs-tab"):
                yield Static("Graph visualization will go here", id="graphs-content")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app with themes and TensorBoard connection."""
        # Register and apply theme
        register_themes(self)
        self.theme = get_default_theme().name

        # Initialize TensorBoard client connection
        try:
            self.client = TensorBoardClient(self.server_url or "http://localhost:6006")
            # Test connection
            env = self.client.get_environment()
            log.info(f"Connected to TensorBoard {env.version}")
            self.title = f"TextBoard - {env.version}"

            # Set the client on the left panel, which will trigger loading
            left_panel = self.query_one(LeftPanel)
            left_panel.set_client(self.client)

        except TensorBoardConnectionError as e:
            log.error(f"Failed to connect to TensorBoard: {e}")
            self.title = "TextBoard - Connection Failed"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "refresh-btn":
            # Refresh runs data
            if self.client:
                left_panel = self.query_one(LeftPanel)
                left_panel.update_runs(self.client)

    def cleanup(self):
        """Clean up resources."""
        # Reset mouse cursor to fix terminal state
        import os

        os.system('printf "\\033[?25h\\033[0m"')  # Show cursor and reset colors

        if self.client:
            self.client.close()
        self.tb_manager.stop_server()
