"""TensorBoard backend data management and polling system.

This module contains the Backend class that manages TensorBoard API client
and data caching. The Textual app is responsible for calling poll_updates()
on a timer using set_interval().
"""

from typing import List, Optional, Protocol
from txtrboard.client import TensorBoardClient, TensorBoardConnectionError, TensorBoardAPIError
from txtrboard.messages import RunsListUpdated, ConnectionStatusChanged


class MessagePump(Protocol):
    """Protocol for objects that can receive and dispatch messages.

    This allows the Backend to send messages to any object with a post_message
    method, typically the Textual App instance.
    """

    def post_message(self, message) -> None:
        """Post a message to be dispatched."""
        ...


class Backend:
    """Backend data management system for TensorBoard.

    This class manages the TensorBoard API client and handles data caching.
    It provides a poll_updates() method that the Textual app should call
    periodically using set_interval() to check for changes.

    Future expansion could include:
    - Performance statistics collection
    - Server management (start/stop TensorBoard)
    - Temporary directory management
    - Cleanup on shutdown
    """

    def __init__(self, message_pump: MessagePump, base_url: str = "http://localhost:6006"):
        """Initialize the Backend.

        Args:
            message_pump: Object that can receive messages (typically the App)
            base_url: TensorBoard server URL
        """
        self.message_pump = message_pump
        self.base_url = base_url

        # TensorBoard client
        self.client = TensorBoardClient(base_url)

        # Cached data
        self._cached_runs: Optional[List[str]] = None
        self._connected = False
        self._last_error = ""

    async def poll_updates(self) -> None:
        """Poll TensorBoard for updates and dispatch messages if changes detected.

        This method should be called periodically by the Textual app using
        set_interval(). It checks for changes in runs list and connection status,
        dispatching appropriate messages when changes are detected.
        """
        try:
            # Fetch current runs
            runs_response = await self.client.get_runs()
            current_runs = runs_response.runs

            # Check if runs list changed
            if self._cached_runs != current_runs:
                self._cached_runs = current_runs.copy()

                # Dispatch update message
                message = RunsListUpdated(current_runs)
                self.message_pump.post_message(message)

            # Update connection status if needed
            if not self._connected or self._last_error:
                self._connected = True
                self._last_error = ""

                # Dispatch connection status message
                message = ConnectionStatusChanged(connected=True)
                self.message_pump.post_message(message)

        except (TensorBoardConnectionError, TensorBoardAPIError) as e:
            error_msg = str(e)

            # Update connection status if needed
            if self._connected or self._last_error != error_msg:
                self._connected = False
                self._last_error = error_msg

                # Dispatch connection status message
                message = ConnectionStatusChanged(connected=False, error=error_msg)
                self.message_pump.post_message(message)

    async def cleanup(self) -> None:
        """Clean up resources on shutdown."""
        await self.client.close()

    # Properties for accessing cached data
    @property
    def cached_runs(self) -> Optional[List[str]]:
        """Get the cached runs list."""
        return self._cached_runs.copy() if self._cached_runs else None

    @property
    def is_connected(self) -> bool:
        """Check if currently connected to TensorBoard."""
        return self._connected

    @property
    def last_error(self) -> str:
        """Get the last connection error message."""
        return self._last_error
