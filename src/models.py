"""Data models for the lyrics display application."""
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Song:
    """Represents a song with its lyrics file."""
    title: str
    lyrics_file: Path

    def get_lyrics(self) -> str:
        """Read and return the lyrics content."""
        if not self.lyrics_file.exists():
            raise FileNotFoundError(f"Lyrics file not found: {self.lyrics_file}")
        return self.lyrics_file.read_text(encoding='utf-8')


@dataclass
class Page:
    """Represents a single page of lyrics."""
    content: str
    page_number: int
