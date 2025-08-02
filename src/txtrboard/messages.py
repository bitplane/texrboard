"""Message classes for TensorBoard events and UI interactions.

This module contains Textual message classes used to communicate
between UI components, the backend, and the app for both data updates
and user interactions.
"""

from textual.message import Message


# Backend data update messages
class ConnectionStatusChanged(Message):
    """Dispatched when TensorBoard connection status changes.

    This message is sent when the connection to TensorBoard
    server is established, lost, or encounters an error.
    """

    def __init__(self, connected: bool, error: str = "") -> None:
        """Initialize the connection status change message.

        Args:
            connected: True if connected to TensorBoard, False if disconnected
            error: Error message if connection failed (empty string if no error)
        """
        self.connected = connected
        self.error = error
        super().__init__()


# UI interaction messages
class RefreshRequested(Message):
    """Dispatched when the user clicks the refresh button.

    This message bubbles up to the App which triggers an immediate
    backend poll for fresh data.
    """

    def __init__(self) -> None:
        """Initialize the refresh request message."""
        super().__init__()


class RefreshIntervalChanged(Message):
    """Dispatched when the user changes the refresh interval setting.

    This message bubbles up to the App which adjusts the polling
    timer interval accordingly.
    """

    def __init__(self, interval: float) -> None:
        """Initialize the refresh interval change message.

        Args:
            interval: New refresh interval in seconds
        """
        self.interval = interval
        super().__init__()
