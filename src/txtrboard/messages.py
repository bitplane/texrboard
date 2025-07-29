"""Message classes for TensorBoard update events.

This module contains Textual message classes used to communicate
updates between the background poller and UI components.
"""

from textual.message import Message
from typing import List


class RunsListUpdated(Message):
    """Dispatched when the TensorBoard runs list changes.

    This message is sent when the background poller detects
    that new runs have been added or existing runs removed.
    """

    def __init__(self, runs: List[str]) -> None:
        """Initialize the runs list update message.

        Args:
            runs: Current list of run names from TensorBoard
        """
        self.runs = runs
        super().__init__()


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
