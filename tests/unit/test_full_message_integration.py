import pytest
from unittest.mock import AsyncMock, Mock, patch
from textual.widgets import Button, Select
from txtrboard.ui.app import TextBoardApp
from txtrboard.messages import ConnectionStatusChanged


@pytest.mark.asyncio
async def test_full_message_flow_refresh_button():
    """Test complete message flow from refresh button to backend polling."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Simulate user clicking refresh button
            refresh_btn = app.query_one("#refresh-btn", Button)
            refresh_btn.press()

            # Allow message processing
            await pilot.pause()

            # Verify the complete flow:
            # 1. Header dispatched RefreshRequested message
            # 2. App received and handled the message
            # 3. App called backend.poll_updates()
            mock_backend.poll_updates.assert_called_once()


@pytest.mark.asyncio
async def test_full_message_flow_interval_change():
    """Test complete message flow from interval dropdown to timer setup."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Simulate user changing interval from INACTIVE to 5s
            select = app.query_one("#refresh-interval", Select)
            select.value = "5s"

            # Allow message processing
            await pilot.pause()

            # Verify the complete flow:
            # 1. Header dispatched RefreshIntervalChanged message with interval=5.0
            # 2. App received and handled the message
            # 3. App updated polling_interval and started timer
            assert app.polling_interval == 5.0
            assert app.polling_timer is not None


@pytest.mark.asyncio
async def test_backend_reactive_data_flow():
    """Test that backend data flows through reactive system."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend.get_current_runs_tuple = Mock(return_value=("train", "eval", "test"))
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Simulate backend data change callback
            app.on_data_changed()

            # Allow processing
            await pilot.pause()

            # Verify app's reactive data was updated
            assert app.runs_data == ("train", "eval", "test")


@pytest.mark.asyncio
async def test_connection_status_updates_title():
    """Test that connection status messages update app title."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Test connected status
            app.post_message(ConnectionStatusChanged(connected=True))
            await pilot.pause()
            assert "Connected" in app.title

            # Test disconnected status
            app.post_message(ConnectionStatusChanged(connected=False, error="Connection lost"))
            await pilot.pause()
            assert "Disconnected" in app.title


@pytest.mark.asyncio
async def test_inactive_to_active_interval_flow():
    """Test changing from INACTIVE to active interval creates timer."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Initially INACTIVE (no timer)
            select = app.query_one("#refresh-interval", Select)
            assert select.value == "INACTIVE"
            assert app.polling_timer is None

            # Change to active interval
            select.value = "30s"
            await pilot.pause()

            # Timer should now be running
            assert app.polling_interval == 30.0
            assert app.polling_timer is not None

            # Change back to INACTIVE (header won't send message)
            select.value = "INACTIVE"
            await pilot.pause()

            # Timer should still be there since no message was sent
            assert app.polling_timer is not None
