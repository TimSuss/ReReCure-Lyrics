#!/usr/bin/env python3
"""Entry point for the lyrics display application."""
import argparse
from pathlib import Path
from src.app import LyricsApp


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Footswitch-controlled lyrics display application"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/playlist.json"),
        help="Path to the playlist configuration file (default: config/playlist.json)"
    )
    parser.add_argument(
        "--lines-per-page",
        type=int,
        default=20,
        help="Number of lines per page (default: 20)"
    )
    parser.add_argument(
        "--footswitch-device",
        type=str,
        default=None,
        help="Path to footswitch device (e.g., /dev/input/event0). Auto-detected if not specified."
    )
    parser.add_argument(
        "--gpio",
        action="store_true",
        help="Use GPIO pedal board (Raspberry Pi only, pins 17/27 for buttons, 22/23 for LEDs)"
    )

    args = parser.parse_args()

    # Validate config file exists
    if not args.config.exists():
        print(f"Error: Configuration file not found: {args.config}")
        print(f"Please create a configuration file or specify a different path with --config")
        return 1

    # Create and run the application
    try:
        app = LyricsApp(
            config_path=args.config,
            lines_per_page=args.lines_per_page
        )
        app.run(footswitch_device=args.footswitch_device, use_gpio=args.gpio)
        return 0
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
