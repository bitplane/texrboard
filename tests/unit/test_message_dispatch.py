import pytest
from textual.app import App
from textual.widget import Widget
from txtrboard.messages import ConnectionStatusChanged, RefreshRequested, RefreshIntervalChanged


@pytest.mark.asyncio
async def test_connection_status_changed_dispatch():
    """Test that ConnectionStatusChanged message can be dispatched and handled."""
    received_message = None

    class TestWidget(Widget):
        def on_connection_status_changed(self, message: ConnectionStatusChanged) -> None:
            nonlocal received_message
            received_message = message

    class TestApp(App):
        def compose(self):
            yield TestWidget()

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the widget
        widget = app.query_one(TestWidget)

        # Dispatch the message
        message = ConnectionStatusChanged(connected=False, error="Connection failed")
        widget.post_message(message)

        # Give the message time to be processed
        await pilot.pause()

        # Verify the message was received
        assert received_message is not None
        assert received_message.connected is False
        assert received_message.error == "Connection failed"


@pytest.mark.asyncio
async def test_message_bubbling():
    """Test that messages bubble up through the widget hierarchy."""
    received_at_app = None
    received_at_widget = None

    class TestWidget(Widget):
        def on_connection_status_changed(self, message: ConnectionStatusChanged) -> None:
            nonlocal received_at_widget
            received_at_widget = message
            # Don't prevent bubbling

    class TestApp(App):
        def compose(self):
            yield TestWidget()

        def on_connection_status_changed(self, message: ConnectionStatusChanged) -> None:
            nonlocal received_at_app
            received_at_app = message

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the widget
        widget = app.query_one(TestWidget)

        # Dispatch the message
        message = ConnectionStatusChanged(connected=True)
        widget.post_message(message)

        # Give the message time to be processed
        await pilot.pause()

        # Verify the message was received at both levels
        assert received_at_widget is not None
        assert received_at_widget.connected is True
        assert received_at_app is not None
        assert received_at_app.connected is True


@pytest.mark.asyncio
async def test_refresh_requested_dispatch():
    """Test that RefreshRequested message can be dispatched and handled."""
    received_message = None

    class TestWidget(Widget):
        def on_refresh_requested(self, message: RefreshRequested) -> None:
            nonlocal received_message
            received_message = message

    class TestApp(App):
        def compose(self):
            yield TestWidget()

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the widget
        widget = app.query_one(TestWidget)

        # Dispatch the message
        message = RefreshRequested()
        widget.post_message(message)

        # Give the message time to be processed
        await pilot.pause()

        # Verify the message was received
        assert received_message is not None
        assert isinstance(received_message, RefreshRequested)


@pytest.mark.asyncio
async def test_refresh_interval_changed_dispatch():
    """Test that RefreshIntervalChanged message can be dispatched and handled."""
    received_message = None

    class TestWidget(Widget):
        def on_refresh_interval_changed(self, message: RefreshIntervalChanged) -> None:
            nonlocal received_message
            received_message = message

    class TestApp(App):
        def compose(self):
            yield TestWidget()

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the widget
        widget = app.query_one(TestWidget)

        # Dispatch the message
        interval = 2.5
        message = RefreshIntervalChanged(interval)
        widget.post_message(message)

        # Give the message time to be processed
        await pilot.pause()

        # Verify the message was received
        assert received_message is not None
        assert isinstance(received_message, RefreshIntervalChanged)
        assert received_message.interval == interval
