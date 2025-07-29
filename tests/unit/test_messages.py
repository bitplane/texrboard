from textual.message import Message
from txtrboard.messages import RunsListUpdated, ConnectionStatusChanged


class TestRunsListUpdated:
    """Test suite for RunsListUpdated message."""

    def test_message_creation(self):
        """Test creating RunsListUpdated message with runs list."""
        runs = ["train", "eval", "test"]
        message = RunsListUpdated(runs)

        assert isinstance(message, Message)
        assert message.runs == runs
        assert message.runs is runs  # Should store the exact list reference

    def test_empty_runs_list(self):
        """Test creating message with empty runs list."""
        message = RunsListUpdated([])

        assert message.runs == []
        assert len(message.runs) == 0

    def test_single_run(self):
        """Test creating message with single run."""
        runs = ["single_run"]
        message = RunsListUpdated(runs)

        assert message.runs == ["single_run"]
        assert len(message.runs) == 1


class TestConnectionStatusChanged:
    """Test suite for ConnectionStatusChanged message."""

    def test_connection_established(self):
        """Test creating message for successful connection."""
        message = ConnectionStatusChanged(connected=True)

        assert isinstance(message, Message)
        assert message.connected is True
        assert message.error == ""

    def test_connection_lost(self):
        """Test creating message for lost connection."""
        message = ConnectionStatusChanged(connected=False)

        assert message.connected is False
        assert message.error == ""

    def test_connection_error(self):
        """Test creating message for connection error."""
        error_msg = "Connection refused"
        message = ConnectionStatusChanged(connected=False, error=error_msg)

        assert message.connected is False
        assert message.error == error_msg

    def test_connected_with_error_string(self):
        """Test creating message with connected=True but error string."""
        # This might be an edge case, but the API allows it
        message = ConnectionStatusChanged(connected=True, error="Warning: slow connection")

        assert message.connected is True
        assert message.error == "Warning: slow connection"

    def test_default_error_parameter(self):
        """Test that error parameter defaults to empty string."""
        message_connected = ConnectionStatusChanged(True)
        message_disconnected = ConnectionStatusChanged(False)

        assert message_connected.error == ""
        assert message_disconnected.error == ""
