import pytest
from textual.app import App
from textual.widgets import Button, Select
from txtrboard.ui.header import TextBoardHeader
from txtrboard.messages import RefreshRequested, RefreshIntervalChanged


@pytest.mark.asyncio
async def test_refresh_button_dispatches_message():
    """Test that clicking refresh button dispatches RefreshRequested message."""
    received_message = None

    class TestApp(App):
        def compose(self):
            yield TextBoardHeader()

        def on_refresh_requested(self, message: RefreshRequested) -> None:
            nonlocal received_message
            received_message = message

    app = TestApp()
    async with app.run_test() as pilot:
        # Find the refresh button and trigger press event directly
        refresh_btn = app.query_one("#refresh-btn", Button)
        refresh_btn.press()

        # Give time for the message to be processed
        await pilot.pause()

        # Verify the message was received
        assert received_message is not None
        assert isinstance(received_message, RefreshRequested)


@pytest.mark.asyncio
async def test_interval_select_dispatches_message():
    """Test that changing refresh interval dispatches RefreshIntervalChanged message."""
    received_message = None

    class TestApp(App):
        def compose(self):
            yield TextBoardHeader()

        def on_refresh_interval_changed(self, message: RefreshIntervalChanged) -> None:
            nonlocal received_message
            received_message = message

    app = TestApp()
    async with app.run_test() as pilot:
        # Find the select widget and change its value
        select = app.query_one("#refresh-interval", Select)
        select.value = "10s"

        # Give time for the message to be processed
        await pilot.pause()

        # Verify the message was received with correct interval
        assert received_message is not None
        assert isinstance(received_message, RefreshIntervalChanged)
        assert received_message.interval == 10.0


@pytest.mark.asyncio
async def test_interval_mapping():
    """Test that all interval values map correctly."""
    received_messages = []

    class TestApp(App):
        def compose(self):
            yield TextBoardHeader()

        def on_refresh_interval_changed(self, message: RefreshIntervalChanged) -> None:
            received_messages.append(message)

    app = TestApp()
    async with app.run_test() as pilot:
        select = app.query_one("#refresh-interval", Select)

        # Test all interval mappings
        test_cases = [
            ("5s", 5.0),
            ("10s", 10.0),
            ("30s", 30.0),
            ("1m", 60.0),
            ("5m", 300.0),
        ]

        for value, expected_interval in test_cases:
            received_messages.clear()
            select.value = value
            await pilot.pause()

            assert len(received_messages) == 1
            assert received_messages[0].interval == expected_interval


@pytest.mark.asyncio
async def test_inactive_interval_no_message():
    """Test that INACTIVE interval doesn't dispatch a message."""
    received_message = None

    class TestApp(App):
        def compose(self):
            yield TextBoardHeader()

        def on_refresh_interval_changed(self, message: RefreshIntervalChanged) -> None:
            nonlocal received_message
            received_message = message

    app = TestApp()
    async with app.run_test() as pilot:
        select = app.query_one("#refresh-interval", Select)

        # Set to active value first
        select.value = "10s"
        await pilot.pause()

        # Clear the received message
        received_message = None

        # Set to INACTIVE
        select.value = "INACTIVE"
        await pilot.pause()

        # Should not receive a message for INACTIVE
        assert received_message is None
