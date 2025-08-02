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
from textual.timer import Timer
from textual.reactive import reactive

from txtrboard.client import TensorBoardClient
from txtrboard.server import TensorBoardManager
from txtrboard.backend import Backend
from txtrboard.messages import RefreshRequested, RefreshIntervalChanged, ConnectionStatusChanged
from txtrboard.logging_config import get_logger
from txtrboard.ui.theme import register_themes, get_default_theme
from txtrboard.ui.left_panel import LeftPanel
from txtrboard.ui.header import TextBoardHeader


class TextBoardApp(App):
    """Main TextBoard TUI application."""

    # Load CSS from external file
    CSS_PATH = Path(__file__).parent / "app.tcss"

    # Reactive data that components can watch
    runs_data = reactive(tuple())

    def get_theme_variable_defaults(self) -> dict[str, str]:
        """Define custom theme variables."""
        return {
            "header-text": "#FFFFFF",
            "header-bg": "#FF6F00",
            "panel-light": "#FFFFFF",
            "panel-dark": "#F5F5F5",
            "panel-text": "#212121",
            "panel-text-bright": "#FFFFFF",
        }

    def __init__(self, server_url: Optional[str] = None):
        super().__init__()

        # Get logger (logging setup handled by CLI)
        self.logger = get_logger(__name__)
        self.logger.info("TextBoardApp starting up")

        self.server_url = server_url
        self.client: Optional[TensorBoardClient] = None
        self.tb_manager = TensorBoardManager()

        # Backend and polling
        self.backend: Optional[Backend] = None
        self.polling_timer: Optional[Timer] = None
        self.polling_interval: float = 30.0  # Default 30 seconds

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
        """Initialize the app with themes and backend."""
        # Register and apply theme
        register_themes(self)
        self.theme = get_default_theme().name

        # Initialize backend
        server_url = self.server_url or "http://localhost:6006"
        self.backend = Backend(message_pump=self, base_url=server_url)

        # Keep client reference for legacy code
        self.client = self.backend.client

        # Start polling timer (INACTIVE by default - user will set interval)
        # Timer will be started when user changes from INACTIVE

        # Initial title
        self.title = "TextBoard"

    def on_data_changed(self) -> None:
        """Callback from Backend when data changes."""
        if self.backend:
            self.logger.debug("Data changed callback - updating reactive")
            self.runs_data = self.backend.get_current_runs_tuple()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "theme-btn":
            # Toggle between light and dark themes
            if self.theme == "tensorboard_dark":
                self.theme = "tensorboard_light"
            else:
                self.theme = "tensorboard_dark"

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

    def on_refresh_requested(self, message: RefreshRequested) -> None:
        """Handle refresh button clicks."""
        self.logger.info("Refresh requested - triggering immediate poll")
        if self.backend:
            # Trigger immediate polling update - call_later properly handles coroutines
            self.call_later(self.backend.poll_updates)
        else:
            self.logger.warning("Refresh requested but backend is None")

    def on_refresh_interval_changed(self, message: RefreshIntervalChanged) -> None:
        """Handle refresh interval changes."""
        self.logger.info(f"Refresh interval changed to {message.interval} seconds")
        self.polling_interval = message.interval

        # Stop existing timer if running
        if self.polling_timer:
            self.logger.debug("Stopping existing polling timer")
            self.polling_timer.stop()
            self.polling_timer = None

        # Start new timer with updated interval
        if self.backend:
            self.logger.info(f"Starting new polling timer with {self.polling_interval}s interval")
            self.polling_timer = self.set_interval(self.polling_interval, self.backend.poll_updates)
        else:
            self.logger.warning("Interval changed but backend is None")

    # RunsListUpdated message handler removed - now using callback + reactive pattern

    def on_connection_status_changed(self, message: ConnectionStatusChanged) -> None:
        """Handle connection status changes."""
        if message.connected:
            self.title = "TextBoard - Connected"
            self.logger.info("Connected to TensorBoard")
            log.info("Connected to TensorBoard")
        else:
            self.title = "TextBoard - Disconnected"
            self.logger.error(f"TensorBoard connection lost: {message.error}")
            log.error(f"TensorBoard connection lost: {message.error}")

    def cleanup(self):
        """Clean up resources."""
        # Reset mouse cursor to fix terminal state
        import os

        os.system('printf "\\033[?25h\\033[0m"')  # Show cursor and reset colors

        # Stop polling timer
        if self.polling_timer:
            self.polling_timer.stop()
            self.polling_timer = None

        # Clean up backend (which will close the client)
        if self.backend:
            self.call_later(self.backend.cleanup)
        elif self.client:
            self.client.close()

        self.tb_manager.stop_server()
