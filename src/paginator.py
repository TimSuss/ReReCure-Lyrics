"""Pagination logic for splitting lyrics into displayable pages."""
from typing import List
from .models import Page


class Paginator:
    """Handles pagination of song lyrics."""

    def __init__(self, lines_per_page: int = 20):
        """
        Initialize the paginator.

        Args:
            lines_per_page: Number of lines to display per page
        """
        self.lines_per_page = lines_per_page

    def paginate(self, lyrics: str) -> List[Page]:
        """
        Split lyrics into pages.

        Args:
            lyrics: The full lyrics text

        Returns:
            List of Page objects
        """
        lines = lyrics.split('\n')
        pages = []
        page_number = 1

        for i in range(0, len(lines), self.lines_per_page):
            page_lines = lines[i:i + self.lines_per_page]
            page_content = '\n'.join(page_lines)
            pages.append(Page(content=page_content, page_number=page_number))
            page_number += 1

        # Ensure at least one page exists
        if not pages:
            pages.append(Page(content="", page_number=1))

        return pages


class PageNavigator:
    """Manages navigation through pages and songs."""

    def __init__(self, pages: List[Page], current_page_index: int = 0):
        """
        Initialize the page navigator.

        Args:
            pages: List of pages for the current song
            current_page_index: Starting page index (0-based)
        """
        self.pages = pages
        self.current_page_index = max(0, min(current_page_index, len(pages) - 1))

    def get_current_pages(self) -> tuple[Page, Page | None]:
        """
        Get the current two pages to display side-by-side.

        Returns:
            Tuple of (left_page, right_page). right_page may be None if at the end.
        """
        left_page = self.pages[self.current_page_index]
        right_page = None

        if self.current_page_index + 1 < len(self.pages):
            right_page = self.pages[self.current_page_index + 1]

        return left_page, right_page

    def can_go_forward(self) -> bool:
        """Check if we can move forward within the current song."""
        # We can go forward if we're not showing the last page on the right side
        return self.current_page_index + 1 < len(self.pages)

    def can_go_backward(self) -> bool:
        """Check if we can move backward within the current song."""
        return self.current_page_index > 0

    def next_page(self) -> bool:
        """
        Move to the next page.

        Returns:
            True if moved successfully, False if at the end
        """
        if self.can_go_forward():
            self.current_page_index += 1
            return True
        return False

    def previous_page(self) -> bool:
        """
        Move to the previous page.

        Returns:
            True if moved successfully, False if at the beginning
        """
        if self.can_go_backward():
            self.current_page_index -= 1
            return True
        return False

    def reset(self):
        """Reset to the first page."""
        self.current_page_index = 0

    def get_total_pages(self) -> int:
        """Get the total number of pages."""
        return len(self.pages)
