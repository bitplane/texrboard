#!/usr/bin/env python3
"""
TextBoard CLI entry point.

Command-line interface for launching the TextBoard TUI application.
"""

import argparse
import sys

from textual_board.server import TensorBoardManager, extract_log_archive
from textual_board.ui.app import TextBoardApp


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="TextBoard - TUI replacement for TensorBoard")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--logdir", help="Path to TensorBoard logs directory (starts embedded server)")
    group.add_argument("--log-file", help="Path to .tar.gz log archive (extracts and starts embedded server)")
    group.add_argument("--host", default="localhost", help="TensorBoard server host (default: localhost)")

    parser.add_argument("--port", type=int, default=6006, help="TensorBoard server port (default: 6006)")

    args = parser.parse_args()

    tb_manager = TensorBoardManager()
    server_url = None

    try:
        if args.logdir:
            # Start embedded server with logdir
            server_url = tb_manager.start_server(args.logdir)
        elif args.log_file:
            # Extract archive and start embedded server
            logdir = extract_log_archive(args.log_file)
            server_url = tb_manager.start_server(logdir)
        else:
            # Connect to existing server
            server_url = f"http://{args.host}:{args.port}"

        # Start the TUI
        app = TextBoardApp(server_url)
        app.tb_manager = tb_manager  # Pass manager for cleanup
        app.run()

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        tb_manager.stop_server()


if __name__ == "__main__":
    main()
