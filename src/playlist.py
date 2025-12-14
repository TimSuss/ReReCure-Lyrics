"""Playlist management for the lyrics display application."""
from typing import List, Optional
from pathlib import Path
import json
from .models import Song


class Playlist:
    """Manages the collection of songs and current position."""

    def __init__(self, songs: List[Song]):
        if not songs:
            raise ValueError("Playlist must contain at least one song")
        self.songs = songs
        self.current_song_index = 0

    @classmethod
    def from_config(cls, config_path: Path) -> 'Playlist':
        """Load playlist from a JSON configuration file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        songs = []
        # Base path is the parent of the config directory (project root)
        base_path = config_path.parent.parent

        for song_data in config.get('songs', []):
            lyrics_path = base_path / song_data['lyrics_file']
            songs.append(Song(
                title=song_data['title'],
                lyrics_file=lyrics_path
            ))

        return cls(songs)

    def get_current_song(self) -> Song:
        """Get the currently selected song."""
        return self.songs[self.current_song_index]

    def next_song(self) -> Song:
        """Move to the next song in the playlist."""
        self.current_song_index = (self.current_song_index + 1) % len(self.songs)
        return self.get_current_song()

    def previous_song(self) -> Song:
        """Move to the previous song in the playlist."""
        self.current_song_index = (self.current_song_index - 1) % len(self.songs)
        return self.get_current_song()

    def has_next_song(self) -> bool:
        """Check if there's a next song available."""
        return self.current_song_index < len(self.songs) - 1

    def has_previous_song(self) -> bool:
        """Check if there's a previous song available."""
        return self.current_song_index > 0
