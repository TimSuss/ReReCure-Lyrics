#!/usr/bin/env python3
"""Basic functionality test without curses."""
import sys
from pathlib import Path
from src.playlist import Playlist
from src.paginator import Paginator, PageNavigator

# Ensure UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_basic_functionality():
    """Test the core functionality without the UI."""
    print("Testing Footswitch Lyrics Application...")
    print("-" * 50)

    # Test 1: Load playlist
    print("\n1. Loading playlist...")
    playlist = Playlist.from_config(Path('config/playlist.json'))
    print(f"   ✓ Loaded {len(playlist.songs)} songs")

    # Test 2: Load first song
    print("\n2. Loading first song...")
    song = playlist.get_current_song()
    print(f"   ✓ Current song: \"{song.title}\"")

    # Test 3: Get lyrics
    print("\n3. Reading lyrics...")
    lyrics = song.get_lyrics()
    print(f"   ✓ Loaded {len(lyrics)} characters")

    # Test 4: Paginate
    print("\n4. Creating pages...")
    paginator = Paginator(lines_per_page=20)
    pages = paginator.paginate(lyrics)
    print(f"   ✓ Created {len(pages)} pages")

    # Test 5: Navigation
    print("\n5. Testing page navigation...")
    navigator = PageNavigator(pages)
    left, right = navigator.get_current_pages()
    print(f"   ✓ Showing pages {left.page_number} and {right.page_number if right else 'None'}")

    # Test forward
    if navigator.next_page():
        left, right = navigator.get_current_pages()
        print(f"   ✓ After forward: pages {left.page_number} and {right.page_number if right else 'None'}")

    # Test backward
    if navigator.previous_page():
        left, right = navigator.get_current_pages()
        print(f"   ✓ After backward: pages {left.page_number} and {right.page_number if right else 'None'}")

    # Test 6: Song navigation
    print("\n6. Testing song navigation...")
    playlist.next_song()
    song = playlist.get_current_song()
    print(f"   ✓ Next song: \"{song.title}\"")

    playlist.previous_song()
    song = playlist.get_current_song()
    print(f"   ✓ Previous song: \"{song.title}\"")

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
    print("\nTo run the full application:")
    print("  python main.py")
    print("\nControls:")
    print("  Right Arrow / Space - Forward")
    print("  Left Arrow - Backward")
    print("  Q - Quit")

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
