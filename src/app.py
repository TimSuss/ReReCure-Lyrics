"""Main application logic for the lyrics display system."""
import curses
from pathlib import Path
from typing import Optional
from .playlist import Playlist
from .paginator import Paginator, PageNavigator
from .display import Display
from .input_handler import InputHandler, InputAction, FootswitchHandler, GPIOPedalHandler


class LyricsApp:
    """Main application controller."""

    def __init__(self, config_path: Path, lines_per_page: int = 20):
        """
        Initialize the lyrics application.

        Args:
            config_path: Path to the playlist configuration file
            lines_per_page: Number of lines to show per page
        """
        self.playlist = Playlist.from_config(config_path)
        self.paginator = Paginator(lines_per_page=lines_per_page)
        self.page_navigator: Optional[PageNavigator] = None
        self.display: Optional[Display] = None
        self.input_handler = InputHandler()
        self.footswitch_handler: Optional[FootswitchHandler] = None
        self.gpio_pedal_handler: Optional[GPIOPedalHandler] = None
        self.running = False

        # Initialize with the first song
        self._load_current_song()

    def _load_current_song(self):
        """Load and paginate the current song."""
        current_song = self.playlist.get_current_song()
        lyrics = current_song.get_lyrics()
        pages = self.paginator.paginate(lyrics)
        self.page_navigator = PageNavigator(pages)

    def _handle_forward(self):
        """Handle forward navigation."""
        if self.page_navigator.can_go_forward():
            # Move to next page in current song
            self.page_navigator.next_page()
        else:
            # At the end of current song, move to next song
            if self.playlist.has_next_song():
                self.playlist.next_song()
                self._load_current_song()
                if self.display:
                    self.display.show_message("Next Song", duration_ms=500)

    def _handle_backward(self):
        """Handle backward navigation."""
        if self.page_navigator.can_go_backward():
            # Move to previous page in current song
            self.page_navigator.previous_page()
        else:
            # At the beginning of current song, move to previous song
            if self.playlist.has_previous_song():
                self.playlist.previous_song()
                self._load_current_song()
                # Go to the end of the previous song
                while self.page_navigator.can_go_forward():
                    self.page_navigator.next_page()
                if self.display:
                    self.display.show_message("Previous Song", duration_ms=500)

    def _handle_quit(self):
        """Handle quit action."""
        self.running = False

    def _render(self):
        """Render the current state to the display."""
        if not self.display or not self.page_navigator:
            return

        left_page, right_page = self.page_navigator.get_current_pages()
        current_song = self.playlist.get_current_song()

        self.display.render_two_pages(
            left_page=left_page,
            right_page=right_page,
            song_title=current_song.title,
            current_song_num=self.playlist.current_song_index + 1,
            total_songs=len(self.playlist.songs)
        )

    def _process_keyboard_input(self):
        """Process keyboard input."""
        if not self.display:
            return

        key = self.display.get_key()
        if key:
            action = self.input_handler.handle_key(key)
            if action == InputAction.FORWARD:
                self._handle_forward()
            elif action == InputAction.BACKWARD:
                self._handle_backward()
            elif action == InputAction.QUIT:
                self._handle_quit()

    def _process_footswitch_input(self):
        """Process footswitch input."""
        if not self.footswitch_handler or not self.footswitch_handler.device:
            return

        action = self.footswitch_handler.read_event()
        if action == InputAction.FORWARD:
            self._handle_forward()
        elif action == InputAction.BACKWARD:
            self._handle_backward()

    def _process_gpio_pedal_input(self):
        """Process GPIO pedal board input."""
        if not self.gpio_pedal_handler or not self.gpio_pedal_handler.enabled:
            return

        action = self.gpio_pedal_handler.read_event()
        if action == InputAction.FORWARD:
            self._handle_forward()
        elif action == InputAction.BACKWARD:
            self._handle_backward()

    def run_with_curses(self, stdscr):
        """
        Main application loop (called by curses.wrapper).

        Args:
            stdscr: The curses standard screen object
        """
        self.display = Display(stdscr)
        self.running = True

        # Initial render
        self._render()

        # Main loop
        while self.running:
            # Process input
            self._process_keyboard_input()
            self._process_footswitch_input()
            self._process_gpio_pedal_input()

            # Render current state
            self._render()

    def run(self, footswitch_device: Optional[str] = None, use_gpio: bool = False):
        """
        Start the application.

        Args:
            footswitch_device: Optional path to the footswitch device
            use_gpio: Enable GPIO pedal board support (Raspberry Pi only)
        """
        # Set up GPIO pedal board if requested
        if use_gpio:
            self.gpio_pedal_handler = GPIOPedalHandler()
            if not self.gpio_pedal_handler.enabled:
                print("Running without GPIO pedals.")

        # Set up footswitch if on Linux
        import sys
        if sys.platform.startswith('linux') and not use_gpio:
            self.footswitch_handler = FootswitchHandler(footswitch_device)
            if self.footswitch_handler.connect():
                print("Footswitch connected successfully!")
            else:
                print("Running without footswitch. Use keyboard controls.")

        # Run with curses
        try:
            curses.wrapper(self.run_with_curses)
        except KeyboardInterrupt:
            pass
        finally:
            # Clean up GPIO resources
            if self.gpio_pedal_handler:
                self.gpio_pedal_handler.cleanup()
            print("Application closed.")
