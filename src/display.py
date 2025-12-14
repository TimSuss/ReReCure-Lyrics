"""Display module for rendering lyrics on the console."""
import curses
from typing import Optional
from .models import Page


class Display:
    """Handles the terminal display using curses."""

    def __init__(self, stdscr):
        """
        Initialize the display.

        Args:
            stdscr: The curses standard screen object
        """
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()

        # Configure curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(100) # 100ms timeout for getch()

        # Initialize color pairs if terminal supports color
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    def clear(self):
        """Clear the screen."""
        self.stdscr.clear()

    def refresh(self):
        """Refresh the screen to show changes."""
        self.stdscr.refresh()

    def render_two_pages(
        self,
        left_page: Page,
        right_page: Optional[Page],
        song_title: str,
        current_song_num: int,
        total_songs: int
    ):
        """
        Render two pages side-by-side.

        Args:
            left_page: The left page to display
            right_page: The right page to display (may be None)
            song_title: The current song title
            current_song_num: Current song number (1-indexed)
            total_songs: Total number of songs
        """
        self.clear()
        self.height, self.width = self.stdscr.getmaxyx()

        # Calculate layout
        header_height = 3
        footer_height = 2
        content_height = self.height - header_height - footer_height
        page_width = self.width // 2

        # Render header
        self._render_header(song_title, current_song_num, total_songs)

        # Render divider line
        divider_y = header_height - 1
        self.stdscr.hline(divider_y, 0, curses.ACS_HLINE, self.width)

        # Render left page
        self._render_page(
            left_page,
            start_y=header_height,
            start_x=0,
            width=page_width,
            height=content_height
        )

        # Render vertical divider
        for y in range(header_height, self.height - footer_height):
            try:
                self.stdscr.addch(y, page_width, curses.ACS_VLINE)
            except curses.error:
                pass

        # Render right page if available
        if right_page:
            self._render_page(
                right_page,
                start_y=header_height,
                start_x=page_width + 1,
                width=page_width - 1,
                height=content_height
            )

        # Render footer
        self._render_footer(left_page.page_number, right_page.page_number if right_page else None)

        self.refresh()

    def _render_header(self, song_title: str, current_song: int, total_songs: int):
        """Render the header with song information."""
        # Song title (centered, bold if possible)
        title_y = 0
        title_x = max(0, (self.width - len(song_title)) // 2)

        try:
            self.stdscr.addstr(
                title_y,
                title_x,
                song_title,
                curses.A_BOLD | curses.color_pair(2) if curses.has_colors() else curses.A_BOLD
            )
        except curses.error:
            pass

        # Song counter (top right)
        song_info = f"Song {current_song}/{total_songs}"
        info_x = max(0, self.width - len(song_info) - 2)
        try:
            self.stdscr.addstr(
                title_y,
                info_x,
                song_info,
                curses.color_pair(3) if curses.has_colors() else curses.A_NORMAL
            )
        except curses.error:
            pass

    def _render_page(self, page: Page, start_y: int, start_x: int, width: int, height: int):
        """
        Render a single page of lyrics.

        Args:
            page: The page to render
            start_y: Starting Y position
            start_x: Starting X position
            width: Width of the page area
            height: Height of the page area
        """
        lines = page.content.split('\n')

        for i, line in enumerate(lines):
            if i >= height:
                break

            y = start_y + i
            x = start_x + 2  # Add some padding from the edge

            # Truncate line if too long
            display_line = line[:width - 4]

            try:
                self.stdscr.addstr(
                    y,
                    x,
                    display_line,
                    curses.color_pair(1) if curses.has_colors() else curses.A_NORMAL
                )
            except curses.error:
                # Ignore errors when writing to the last cell
                pass

    def _render_footer(self, left_page_num: int, right_page_num: Optional[int]):
        """Render the footer with navigation hints."""
        footer_y = self.height - 2

        # Draw a line above the footer
        try:
            self.stdscr.hline(footer_y, 0, curses.ACS_HLINE, self.width)
        except curses.error:
            pass

        footer_y += 1

        # Page numbers
        if right_page_num:
            page_info = f"Pages {left_page_num}-{right_page_num}"
        else:
            page_info = f"Page {left_page_num}"

        # Navigation hints
        nav_hint = "← BACK | FORWARD → | Q to quit"

        try:
            # Left side: page numbers
            self.stdscr.addstr(footer_y, 2, page_info, curses.A_DIM if curses.has_colors() else curses.A_NORMAL)

            # Right side: navigation hints
            hint_x = max(0, self.width - len(nav_hint) - 2)
            self.stdscr.addstr(footer_y, hint_x, nav_hint, curses.A_DIM if curses.has_colors() else curses.A_NORMAL)
        except curses.error:
            pass

    def show_message(self, message: str, duration_ms: int = 2000):
        """
        Show a temporary message in the center of the screen.

        Args:
            message: The message to display
            duration_ms: How long to display it in milliseconds
        """
        self.height, self.width = self.stdscr.getmaxyx()
        y = self.height // 2
        x = max(0, (self.width - len(message)) // 2)

        try:
            self.stdscr.addstr(
                y,
                x,
                message,
                curses.A_REVERSE | curses.color_pair(3) if curses.has_colors() else curses.A_REVERSE
            )
        except curses.error:
            pass

        self.refresh()
        curses.napms(duration_ms)

    def get_key(self) -> Optional[str]:
        """
        Get a key press from the user.

        Returns:
            The key name or None if no key was pressed
        """
        try:
            key = self.stdscr.getch()
            if key == -1:
                return None

            # Try to get the key name
            try:
                key_name = curses.keyname(key).decode('utf-8')
                return key_name
            except:
                # If that fails, try to convert to char
                try:
                    return chr(key)
                except:
                    return None

        except Exception:
            return None
