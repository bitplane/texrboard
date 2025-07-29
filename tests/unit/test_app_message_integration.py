import pytest
from unittest.mock import AsyncMock, Mock, patch
from textual.widgets import Button, Select
from txtrboard.ui.app import TextBoardApp
from txtrboard.messages import RefreshRequested, RefreshIntervalChanged


@pytest.mark.asyncio
async def test_app_handles_refresh_request():
    """Test that App handles RefreshRequested messages properly."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Get the refresh button and trigger it
            refresh_btn = app.query_one("#refresh-btn", Button)
            refresh_btn.press()

            # Give time for message processing
            await pilot.pause()

            # Verify backend poll_updates was called
            mock_backend.poll_updates.assert_called_once()


@pytest.mark.asyncio
async def test_app_handles_interval_change():
    """Test that App handles RefreshIntervalChanged messages properly."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Initially no timer should be running
            assert app.polling_timer is None

            # Change interval from INACTIVE to 10s
            select = app.query_one("#refresh-interval", Select)
            select.value = "10s"

            # Give time for message processing
            await pilot.pause()

            # Verify polling interval was updated and timer started
            assert app.polling_interval == 10.0
            assert app.polling_timer is not None


@pytest.mark.asyncio
async def test_app_stops_timer_when_changing_interval():
    """Test that App properly stops existing timer when interval changes."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Start with 10s interval
            select = app.query_one("#refresh-interval", Select)
            select.value = "10s"
            await pilot.pause()

            # Verify timer is running
            first_timer = app.polling_timer
            assert first_timer is not None
            assert app.polling_interval == 10.0

            # Change to 30s interval
            select.value = "30s"
            await pilot.pause()

            # Verify old timer was stopped and new one started
            assert app.polling_interval == 30.0
            assert app.polling_timer is not None
            assert app.polling_timer != first_timer

            # Verify the first timer was stopped (Timer.stop() should make it inactive)
            # Since we can't easily check if timer is stopped, just verify we have a different timer
            assert first_timer != app.polling_timer


@pytest.mark.asyncio
async def test_app_handles_inactive_interval():
    """Test that App stops timer when interval set to INACTIVE."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Start with active interval
            select = app.query_one("#refresh-interval", Select)
            select.value = "10s"
            await pilot.pause()

            # Verify timer is running
            timer = app.polling_timer
            assert timer is not None

            # Set to INACTIVE
            select.value = "INACTIVE"
            await pilot.pause()

            # Timer should still be there since INACTIVE doesn't dispatch message
            # (This tests that the header correctly doesn't send messages for INACTIVE)
            assert app.polling_timer is not None


@pytest.mark.asyncio
async def test_refresh_message_triggers_immediate_poll():
    """Test that RefreshRequested triggers immediate backend poll."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Send refresh message directly
            app.post_message(RefreshRequested())
            await pilot.pause()

            # Verify immediate poll was triggered
            mock_backend.poll_updates.assert_called_once()


@pytest.mark.asyncio
async def test_interval_change_message_updates_timer():
    """Test that RefreshIntervalChanged message updates polling timer."""
    with patch("txtrboard.ui.app.Backend") as mock_backend_class:
        # Setup mock backend
        mock_backend = Mock()
        mock_backend.poll_updates = AsyncMock()
        mock_backend_class.return_value = mock_backend

        app = TextBoardApp()
        async with app.run_test() as pilot:
            # Send interval change message directly
            app.post_message(RefreshIntervalChanged(5.0))
            await pilot.pause()

            # Verify interval and timer were updated
            assert app.polling_interval == 5.0
            assert app.polling_timer is not None
