"""
Command palette commands for txtrboard.

Defines custom commands that can be invoked via the command palette (Ctrl+P).
"""

from textual.command import Command, Hit, Provider


class DevToolsCommand(Command):
    """Command to toggle developer tools."""

    def __init__(self) -> None:
        super().__init__(
            name="Toggle Developer Tools",
            title="Toggle Developer Tools",
            help_text="Open/close the Textual developer tools overlay",
        )

    def run(self) -> None:
        """Toggle the developer tools."""
        self.app.toggle_developer_tools()


class RefreshDataCommand(Command):
    """Command to refresh TensorBoard data."""

    def __init__(self) -> None:
        super().__init__(
            name="Refresh Data",
            title="Refresh TensorBoard Data",
            help_text="Reload runs and metrics from TensorBoard server",
        )

    def run(self) -> None:
        """Refresh the data."""
        # This will trigger the same logic as the refresh button
        from txtrboard.ui.left_panel import LeftPanel

        if hasattr(self.app, "client") and self.app.client:
            try:
                left_panel = self.app.query_one(LeftPanel)
                left_panel.update_runs(self.app.client)
            except Exception:
                pass


class TxtrboardCommandProvider(Provider):
    """Command provider for txtrboard-specific commands."""

    async def search(self, query: str) -> list[Hit]:
        """Search for matching commands."""
        commands = [
            DevToolsCommand(),
            RefreshDataCommand(),
        ]

        # For now, always show all commands for debugging
        hits = []
        for command in commands:
            hits.append(
                Hit(
                    score=1.0,
                    match_display=command.name,
                    command=command,
                )
            )

        return hits
