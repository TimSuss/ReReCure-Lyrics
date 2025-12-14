# Footswitch-Controlled Lyrics Display

A console-based lyrics display application designed for live performances. Control your lyrics with a footswitch while singing!

## Features

- **Footswitch Control**: Navigate lyrics hands-free using a USB footswitch
- **Keyboard Fallback**: Works with keyboard if no footswitch is available
- **Side-by-Side Pages**: Shows two pages at once for smooth reading
- **Large Text Display**: Optimized for floor displays visible from standing position
- **Playlist Management**: Organize multiple songs in a simple JSON file
- **Cross-Platform**: Runs on Windows (development) and Linux (Raspberry Pi)

## Installation

### On Windows (Development)

```bash
# Clone or navigate to the project directory
cd ReReCure-Lyrics

# Install dependencies
pip install -r requirements.txt
```

### On Raspberry Pi / Linux

```bash
# Clone or navigate to the project directory
cd ReReCure-Lyrics

# Install dependencies
pip install -r requirements.txt

# For footswitch support, you may need to run with sudo
# or add your user to the input group:
sudo usermod -a -G input $USER
# (log out and back in for this to take effect)
```

## Configuration

### Setting Up Your Playlist

Edit `config/playlist.json` to add your songs:

```json
{
  "songs": [
    {
      "title": "Your Song Title",
      "lyrics_file": "lyrics/your_song.txt"
    },
    {
      "title": "Another Song",
      "lyrics_file": "lyrics/another_song.txt"
    }
  ]
}
```

### Adding Lyrics

Create text files in the `lyrics/` directory. Each file should contain the lyrics for one song:

```
lyrics/
  ├── your_song.txt
  ├── another_song.txt
  └── ...
```

## Usage

### Test First

Before running the full application, you can verify everything works:

```bash
python test_basic.py
```

This will test all core functionality without requiring the full curses interface.

### Basic Usage

```bash
python main.py
```

### Command-Line Options

```bash
# Use a different config file
python main.py --config path/to/your/playlist.json

# Adjust lines per page (default: 20)
python main.py --lines-per-page 25

# Specify footswitch device manually
python main.py --footswitch-device /dev/input/event0

# Use GPIO pedal board (Raspberry Pi)
python main.py --gpio
```

### Controls

#### Keyboard Controls
- **Right Arrow / Space / Enter / N / F**: Move forward (next page/song)
- **Left Arrow / B / P**: Move backward (previous page/song)
- **Q / ESC**: Quit the application

#### Footswitch Controls (USB)
The application automatically detects footswitch devices on Linux. Common footswitches emulate keyboard keys:
- **Forward pedal**: Typically Right Arrow or Page Down
- **Backward pedal**: Typically Left Arrow or Page Up

#### GPIO Pedal Board (Raspberry Pi)
When using `--gpio` flag, the application expects a pedal board wired to GPIO pins:
- **Forward button**: GPIO 17 (with LED on GPIO 22)
- **Backward button**: GPIO 27 (with LED on GPIO 23)
- Buttons should be wired with pull-up resistors (or use internal pull-up)
- LEDs will flash when pedals are pressed

### Navigation Behavior

1. **Within a Song**: Shows pages 1-2, then 2-3, then 3-4, etc.
2. **At End of Song**: Forward button moves to the next song
3. **At Beginning of Song**: Backward button moves to the previous song (at its end)
4. **Song Wrapping**: After the last song, wraps to the first; before the first song, wraps to the last

## Setting Up Input Devices

### USB Footswitch

On Linux, to find your footswitch device:

```bash
# List all input devices
ls -l /dev/input/by-id/

# Or use evtest to identify the correct device
sudo evtest
```

The application will auto-detect devices with "footswitch", "foot", or "pedal" in their name.

### GPIO Pedal Board (Raspberry Pi)

If you have a custom pedal board wired to GPIO pins:

**Default Pin Configuration:**
- GPIO 17: Forward button
- GPIO 27: Backward button
- GPIO 22: Forward LED
- GPIO 23: Backward LED

**Wiring:**
1. Connect buttons between GPIO pin and ground
2. The software uses internal pull-up resistors
3. Connect LEDs with appropriate current-limiting resistors (220Ω-1kΩ)
4. LED positive (long leg) to GPIO pin, negative to ground through resistor

**Running with GPIO:**
```bash
# Run with GPIO support (may need sudo for GPIO access)
python main.py --gpio

# Or add your user to the gpio group to avoid sudo:
sudo usermod -a -G gpio $USER
# Then log out and back in
```

## Project Structure

```
ReReCure-Lyrics/
├── main.py                 # Entry point
├── src/
│   ├── app.py             # Main application logic
│   ├── display.py         # Terminal/curses display
│   ├── input_handler.py   # Keyboard and footswitch input
│   ├── models.py          # Data models (Song, Page)
│   ├── paginator.py       # Pagination logic
│   └── playlist.py        # Playlist management
├── config/
│   └── playlist.json      # Song playlist configuration
├── lyrics/
│   └── *.txt             # Individual song lyrics files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Windows: "No module named '_curses'"
Install windows-curses:
```bash
pip install windows-curses
```

### Linux: Footswitch not detected
1. Make sure the footswitch is plugged in
2. Run with sudo: `sudo python main.py`
3. Or add your user to the input group (see Installation section)
4. Manually specify device: `python main.py --footswitch-device /dev/input/event0`

### Raspberry Pi: GPIO pedals not working
1. Make sure gpiozero is installed: `pip install gpiozero`
2. Run with sudo: `sudo python main.py --gpio`
3. Check your wiring matches the pin configuration (GPIO 17, 27, 22, 23)
4. Test individual pins with a simple script to verify hardware
5. Check that you're using physical buttons that connect to ground when pressed

### Text too small/large
Adjust the terminal font size in your terminal emulator settings, or modify `--lines-per-page` to show fewer lines (larger text per line with word wrap).

**On Raspberry Pi Desktop:**
- Terminal → Edit → Preferences → Appearance → Font → Size 24-32

**On Raspberry Pi Console Mode:**
```bash
sudo dpkg-reconfigure console-setup
# Choose UTF-8, then "Terminus" font at 16x32
```

### Display issues
- Ensure your terminal is maximized or full-screen
- Use a terminal with good Unicode support (e.g., GNOME Terminal, Konsole, Windows Terminal)
- Try a monospace font optimized for reading

## Development

The application follows best practices:
- **Modular design**: Separate concerns (display, input, logic)
- **Type hints**: Clear function signatures
- **Error handling**: Graceful failures with helpful messages
- **Configuration**: External JSON for easy customization
- **Cross-platform**: Platform-specific code is isolated

## License

This project is open source and available for use in live performances.
