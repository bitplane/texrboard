import pytest
from unittest.mock import AsyncMock, patch
from txtrboard.backend import Backend
from txtrboard.client import TensorBoardConnectionError, TensorBoardAPIError
from txtrboard.messages import ConnectionStatusChanged
from txtrboard.models.tensorboard import RunsResponse


class MockMessagePump:
    """Mock message pump for testing."""

    def __init__(self):
        self.messages = []
        self.data_changed_calls = 0

    def post_message(self, message) -> None:
        self.messages.append(message)

    def on_data_changed(self) -> None:
        self.data_changed_calls += 1


def test_backend_initialization():
    """Test Backend initializes with correct defaults."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    assert backend.message_pump is message_pump
    assert backend.base_url == "http://localhost:6006"
    assert backend.cached_runs is None
    assert backend.is_connected is False
    assert backend.last_error == ""


def test_backend_custom_initialization():
    """Test Backend with custom parameters."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump, base_url="http://example.com:8080")

    assert backend.base_url == "http://example.com:8080"


@pytest.mark.asyncio
async def test_successful_polling():
    """Test successful polling updates runs list."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    # Mock the client response
    mock_runs = ["train", "eval", "test"]
    mock_response = RunsResponse(runs=mock_runs)

    with patch.object(backend.client, "get_runs", return_value=mock_response):
        await backend.poll_updates()

    # Check cached data
    assert backend.cached_runs == mock_runs
    assert backend.is_connected is True
    assert backend.last_error == ""

    # Check data changed callback was called
    assert message_pump.data_changed_calls == 1

    # Check only connection status message sent (no more data messages)
    assert len(message_pump.messages) == 1
    conn_msg = message_pump.messages[0]
    assert isinstance(conn_msg, ConnectionStatusChanged)
    assert conn_msg.connected is True
    assert conn_msg.error == ""


@pytest.mark.asyncio
async def test_runs_list_change_detection():
    """Test that only changed runs lists trigger messages."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    # First poll with initial runs
    initial_runs = ["train", "eval"]
    mock_response1 = RunsResponse(runs=initial_runs)

    with patch.object(backend.client, "get_runs", return_value=mock_response1):
        await backend.poll_updates()

    # Clear messages and reset callback counter
    message_pump.messages.clear()
    initial_callback_calls = message_pump.data_changed_calls

    # Second poll with same runs - should not trigger runs update
    with patch.object(backend.client, "get_runs", return_value=mock_response1):
        await backend.poll_updates()

    # Should have no messages and no additional callbacks since nothing changed
    assert len(message_pump.messages) == 0
    assert message_pump.data_changed_calls == initial_callback_calls

    # Third poll with different runs - should trigger update
    new_runs = ["train", "eval", "test"]
    mock_response2 = RunsResponse(runs=new_runs)

    with patch.object(backend.client, "get_runs", return_value=mock_response2):
        await backend.poll_updates()

    # Should have one additional data changed callback
    assert message_pump.data_changed_calls == initial_callback_calls + 1

    # No messages should be sent for data changes
    assert len(message_pump.messages) == 0


@pytest.mark.asyncio
async def test_connection_error_handling():
    """Test handling of connection errors."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    # Set initial connected state
    backend._connected = True

    # Mock connection error
    error_msg = "Connection refused"
    mock_error = TensorBoardConnectionError(error_msg)

    with patch.object(backend.client, "get_runs", side_effect=mock_error):
        await backend.poll_updates()

    # Check cached data
    assert backend.cached_runs is None  # Should remain None
    assert backend.is_connected is False
    assert backend.last_error == error_msg

    # Check connection status message
    assert len(message_pump.messages) == 1
    conn_msg = message_pump.messages[0]
    assert isinstance(conn_msg, ConnectionStatusChanged)
    assert conn_msg.connected is False
    assert conn_msg.error == error_msg


@pytest.mark.asyncio
async def test_api_error_handling():
    """Test handling of API errors."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    # Mock API error
    error_msg = "404 Not Found"
    mock_error = TensorBoardAPIError(error_msg)

    with patch.object(backend.client, "get_runs", side_effect=mock_error):
        await backend.poll_updates()

    # Check error handling
    assert backend.is_connected is False
    assert backend.last_error == error_msg

    # Check connection status message
    assert len(message_pump.messages) == 1
    conn_msg = message_pump.messages[0]
    assert isinstance(conn_msg, ConnectionStatusChanged)
    assert conn_msg.connected is False
    assert conn_msg.error == error_msg


@pytest.mark.asyncio
async def test_cleanup():
    """Test cleanup functionality."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    with patch.object(backend.client, "close", new_callable=AsyncMock) as mock_close:
        await backend.cleanup()

        # Should close client
        mock_close.assert_called_once()


def test_cached_runs_property():
    """Test cached_runs property returns copy."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    # Test None case
    assert backend.cached_runs is None

    # Test with data
    original_runs = ["train", "eval"]
    backend._cached_runs = original_runs

    cached = backend.cached_runs
    assert cached == original_runs
    assert cached is not original_runs  # Should be a copy


@pytest.mark.asyncio
async def test_multiple_polls_same_data():
    """Test that multiple polls with same data don't spam messages."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    mock_runs = ["stable_run"]
    mock_response = RunsResponse(runs=mock_runs)

    with patch.object(backend.client, "get_runs", return_value=mock_response):
        # First poll - should generate connection message and data callback
        await backend.poll_updates()
        assert len(message_pump.messages) == 1  # connection only
        assert message_pump.data_changed_calls == 1  # data callback

        # Clear messages (but keep callback count)
        message_pump.messages.clear()
        initial_callback_calls = message_pump.data_changed_calls

        # Second poll - should not generate messages or callbacks (no changes)
        await backend.poll_updates()
        assert len(message_pump.messages) == 0
        assert message_pump.data_changed_calls == initial_callback_calls

        # Third poll - should not generate messages or callbacks (no changes)
        await backend.poll_updates()
        assert len(message_pump.messages) == 0
        assert message_pump.data_changed_calls == initial_callback_calls


@pytest.mark.asyncio
async def test_connection_recovery():
    """Test connection recovery after error."""
    message_pump = MockMessagePump()
    backend = Backend(message_pump)

    # First poll fails
    error_msg = "Connection failed"
    mock_error = TensorBoardConnectionError(error_msg)

    with patch.object(backend.client, "get_runs", side_effect=mock_error):
        await backend.poll_updates()

    # Should be disconnected
    assert backend.is_connected is False
    assert backend.last_error == error_msg
    assert len(message_pump.messages) == 1  # connection failed message

    # Clear messages
    message_pump.messages.clear()

    # Second poll succeeds
    mock_runs = ["recovered_run"]
    mock_response = RunsResponse(runs=mock_runs)

    with patch.object(backend.client, "get_runs", return_value=mock_response):
        await backend.poll_updates()

    # Should be connected again
    assert backend.is_connected is True
    assert backend.last_error == ""
    assert len(message_pump.messages) == 1  # connection recovered only
    assert message_pump.data_changed_calls == 1  # data callback
