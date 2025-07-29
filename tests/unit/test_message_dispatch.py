import pytest
from textual.app import App
from textual.widget import Widget
from txtrboard.messages import RunsListUpdated, ConnectionStatusChanged


class TestMessageDispatch:
    """Test suite for verifying message dispatch works with Textual."""

    @pytest.mark.asyncio
    async def test_runs_list_updated_dispatch(self):
        """Test that RunsListUpdated message can be dispatched and handled."""
        received_message = None

        class TestWidget(Widget):
            def on_runs_list_updated(self, message: RunsListUpdated) -> None:
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
            runs = ["train", "eval", "test"]
            message = RunsListUpdated(runs)
            widget.post_message(message)

            # Give the message time to be processed
            await pilot.pause()

            # Verify the message was received
            assert received_message is not None
            assert received_message.runs == runs

    @pytest.mark.asyncio
    async def test_connection_status_changed_dispatch(self):
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
    async def test_message_bubbling(self):
        """Test that messages bubble up through the widget hierarchy."""
        received_at_app = None
        received_at_widget = None

        class TestWidget(Widget):
            def on_runs_list_updated(self, message: RunsListUpdated) -> None:
                nonlocal received_at_widget
                received_at_widget = message
                # Don't prevent bubbling

        class TestApp(App):
            def compose(self):
                yield TestWidget()

            def on_runs_list_updated(self, message: RunsListUpdated) -> None:
                nonlocal received_at_app
                received_at_app = message

        app = TestApp()
        async with app.run_test() as pilot:
            # Get the widget
            widget = app.query_one(TestWidget)

            # Dispatch the message
            runs = ["single_run"]
            message = RunsListUpdated(runs)
            widget.post_message(message)

            # Give the message time to be processed
            await pilot.pause()

            # Verify the message was received at both levels
            assert received_at_widget is not None
            assert received_at_widget.runs == runs
            assert received_at_app is not None
            assert received_at_app.runs == runs
