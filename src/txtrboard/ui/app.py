"""
TextBoard main application.

The main TUI application class that coordinates all components.
"""

import atexit
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Button, Tabs
from textual.containers import Horizontal, Container
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

        with Horizontal(id="main-content"):
            yield LeftPanel()
            with Container(id="content-area"):
                yield Static("Scalar plots will go here", id="scalars-content")
            with Container(id="content-area-images", classes="hidden"):
                yield Static("Image displays will go here", id="images-content")
            with Container(id="content-area-histograms", classes="hidden"):
                yield Static("Histogram plots will go here", id="histograms-content")
            with Container(id="content-area-graphs", classes="hidden"):
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

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab switching."""
        # Hide all content area containers
        content_containers = ["content-area", "content-area-images", "content-area-histograms", "content-area-graphs"]
        for container_id in content_containers:
            try:
                container = self.query_one(f"#{container_id}")
                container.add_class("hidden")
            except Exception:
                pass

        # Show the selected content area container based on tab label
        tab_label = str(event.tab.label).upper()
        label_to_container = {
            "SCALARS": "content-area",
            "IMAGES": "content-area-images",
            "HISTOGRAMS": "content-area-histograms",
            "GRAPHS": "content-area-graphs",
        }

        if tab_label in label_to_container:
            try:
                container = self.query_one(f"#{label_to_container[tab_label]}")
                container.remove_class("hidden")
            except Exception:
                pass

    def cleanup(self):
        """Clean up resources."""
        # Reset mouse cursor to fix terminal state
        import os

        os.system('printf "\\033[?25h\\033[0m"')  # Show cursor and reset colors

        if self.client:
            self.client.close()
        self.tb_manager.stop_server()
