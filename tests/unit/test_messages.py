from textual.message import Message
from txtrboard.messages import ConnectionStatusChanged, RefreshRequested, RefreshIntervalChanged


def test_connection_status_changed_connection_established():
    """Test creating message for successful connection."""
    message = ConnectionStatusChanged(connected=True)

    assert isinstance(message, Message)
    assert message.connected is True
    assert message.error == ""


def test_connection_status_changed_connection_lost():
    """Test creating message for lost connection."""
    message = ConnectionStatusChanged(connected=False)

    assert message.connected is False
    assert message.error == ""


def test_connection_status_changed_connection_error():
    """Test creating message for connection error."""
    error_msg = "Connection refused"
    message = ConnectionStatusChanged(connected=False, error=error_msg)

    assert message.connected is False
    assert message.error == error_msg


def test_connection_status_changed_connected_with_error_string():
    """Test creating message with connected=True but error string."""
    # This might be an edge case, but the API allows it
    message = ConnectionStatusChanged(connected=True, error="Warning: slow connection")

    assert message.connected is True
    assert message.error == "Warning: slow connection"


def test_connection_status_changed_default_error_parameter():
    """Test that error parameter defaults to empty string."""
    message_connected = ConnectionStatusChanged(True)
    message_disconnected = ConnectionStatusChanged(False)

    assert message_connected.error == ""
    assert message_disconnected.error == ""


def test_refresh_requested_message_creation():
    """Test creating RefreshRequested message."""
    message = RefreshRequested()

    assert isinstance(message, Message)
    # RefreshRequested has no additional properties to test


def test_refresh_interval_changed_message_creation():
    """Test creating RefreshIntervalChanged message."""
    interval = 3.5
    message = RefreshIntervalChanged(interval)

    assert isinstance(message, Message)
    assert message.interval == interval


def test_refresh_interval_changed_with_different_intervals():
    """Test RefreshIntervalChanged with various interval values."""
    # Test integer interval
    message1 = RefreshIntervalChanged(5)
    assert message1.interval == 5

    # Test float interval
    message2 = RefreshIntervalChanged(2.5)
    assert message2.interval == 2.5

    # Test small interval
    message3 = RefreshIntervalChanged(0.1)
    assert message3.interval == 0.1
