# Wi-Fi Desk Buddy - NTP Clock & Pomodoro Timer

MicroPython-based productivity tool for Raspberry Pi Pico 2 W with Wi-Fi time sync and focus timer.

## Features

- **🕐 Wi-Fi Synced Clock**: Automatically syncs with NTP servers for accurate time
- **⏱️ Pomodoro Timer**: 25-minute work sessions with 5-minute breaks
- **🎨 RGB Customization**: Adjustable LED colors for personalized display
- **⚙️ On-Device Settings**: Configure everything without a computer
- **🌈 Visual Alerts**: LED animations for timer completion
- **🔔 Audio Alerts**: Optional buzzer notifications (optional)

## Hardware Components

### Required Parts
- **Raspberry Pi Pico 2 W** (RP2350 with Wi-Fi)
- **WS2812B LED Strip** (NeoPixel) - 30 LEDs recommended
- **3x Push Buttons** (tactile switches)
- **3x 10kΩ Resistors** (for pull-up, if not using internal)
- **Breadboard** and jumper wires
- **USB Cable** (for power and programming)

### Optional Parts
- **Passive Buzzer** (for audio alerts)
- **3D Printed Enclosure**
- **Diffuser** (for LED strip)

## Pin Connections

```
Raspberry Pi Pico 2 W
┌─────────────────────┐
│                     │
│  GP16 ──────────────┼──→ WS2812B Data In
│                     │
│  GP14 ──────────────┼──→ Button MODE (to GND)
│  GP15 ──────────────┼──→ Button UP (to GND)
│  GP13 ──────────────┼──→ Button DOWN (to GND)
│                     │
│  GP12 ──────────────┼──→ Buzzer + (optional)
│                     │
│  VBUS ──────────────┼──→ LED Strip 5V
│  GND ───────────────┼──→ LED Strip GND, Buttons, Buzzer -
│                     │
└─────────────────────┘

Button Wiring:
Each button connects between GPIO pin and GND
(Internal pull-up resistors are used)

WS2812B LED Strip:
- 5V  → Pico VBUS (or external 5V supply for >10 LEDs)
- GND → Pico GND
- DIN → GP16 (with 330Ω resistor recommended)
```

### Wiring Notes:
1. **Power**: For LED strips >10 LEDs, use external 5V power supply
2. **Data Line**: Add 330Ω resistor between GP16 and LED data in
3. **Capacitor**: 1000µF capacitor across LED power recommended
4. **Common Ground**: Ensure Pico GND and LED power GND are connected

## Software Setup

### 1. Install MicroPython on Pico 2 W

**Download Firmware:**
1. Visit [MicroPython Downloads](https://micropython.org/download/RPI_PICO2_W/)
2. Download latest `.uf2` file for Pico 2 W

**Flash Firmware:**
1. Hold BOOTSEL button on Pico while connecting USB
2. Pico appears as USB drive
3. Drag `.uf2` file to the drive
4. Pico will reboot with MicroPython installed

### 2. Install Required Libraries

MicroPython on Pico 2 W includes all necessary libraries:
- ✅ `network` - Wi-Fi connectivity
- ✅ `ntptime` - NTP time synchronization
- ✅ `neopixel` - WS2812B control
- ✅ `machine` - Hardware access
- ✅ `time` - Time functions

**No additional libraries needed!**

### 3. Upload Code to Pico

**Using Thonny IDE (Recommended):**
1. Install [Thonny](https://thonny.org/)
2. Open Thonny → Tools → Options → Interpreter
3. Select "MicroPython (Raspberry Pi Pico)"
4. Connect Pico via USB
5. Open `wifi_desk_buddy.py`
6. Update Wi-Fi credentials:
   ```python
   WIFI_SSID = "YourNetworkName"
   WIFI_PASSWORD = "YourPassword"
   ```
7. Click File → Save As → Raspberry Pi Pico
8. Save as `main.py` (runs automatically on boot)

**Using rshell (Command Line):**
```bash
pip install rshell
rshell -p /dev/ttyACM0  # or COM port on Windows
cp wifi_desk_buddy.py /pyboard/main.py
```

**Using ampy:**
```bash
pip install adafruit-ampy
ampy --port /dev/ttyACM0 put wifi_desk_buddy.py /main.py
```

## Configuration

### Wi-Fi Settings
Edit these lines in the code:
```python
WIFI_SSID = "YOUR_WIFI_SSID"      # Your Wi-Fi network name
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"  # Your Wi-Fi password
```

### Timezone
College Station, Texas = UTC-6 (CST)
```python
UTC_OFFSET = -6 * 3600  # -6 hours in seconds
```

**Other timezones:**
- UTC-5 (EST): `-5 * 3600`
- UTC-7 (MST): `-7 * 3600`
- UTC-8 (PST): `-8 * 3600`
- UTC+0 (GMT): `0`

### LED Configuration
```python
NUM_LEDS = 30          # Number of LEDs in your strip
BRIGHTNESS = 0.4       # 0.0 to 1.0 (40% brightness)
```

### Pomodoro Duration
```python
POMODORO_WORK_MINUTES = 25   # Work session length
POMODORO_BREAK_MINUTES = 5   # Break session length
```

## Usage

### Button Controls

| Button | Clock Mode | Pomodoro Mode | Settings Mode |
|--------|------------|---------------|---------------|
| **MODE** | Switch to Pomodoro | Switch to Settings | Switch to Clock |
| **UP** | No function | Start/Resume Timer | Increase Value |
| **DOWN** | No function | Stop/Pause Timer | Next Setting |

### Modes

#### 🕐 Clock Mode
- Displays current time on LED strip
- Automatically syncs with NTP every hour
- Time format (12/24-hour) configurable in settings
- LED colors customizable in settings

#### ⏱️ Pomodoro Mode
- **Press UP**: Start work session (25 min default)
- **Press DOWN**: Stop/pause timer
- **Progress Bar**: LEDs fill to show time elapsed
  - Green LEDs = Work session
  - Blue LEDs = Break session
- **Completion**: Flashing red/yellow alert + buzzer beeps
- **Auto-Switch**: After work → break, after break → work

#### ⚙️ Settings Mode
- **DOWN**: Cycle through settings
- **UP**: Increase current setting value

**Available Settings:**
1. **Time Format**: Toggle 12/24-hour
2. **Color - Red**: Adjust red component (0-255)
3. **Color - Green**: Adjust green component (0-255)
4. **Color - Blue**: Adjust blue component (0-255)
5. **Brightness**: Adjust LED brightness (0.1-1.0)
6. **Work Duration**: Adjust work session (minutes)
7. **Break Duration**: Adjust break session (minutes)

### LED Display Patterns

**Clock Mode:**
- Time displayed as digit bars (6 LEDs per digit pair)
- Format: HH:MM:SS
- Separator dots blink every second

**Pomodoro Mode:**
- Progress bar fills from left to right
- Green = Work session in progress
- Blue = Break session in progress
- Flashing red/yellow = Session complete!

**Settings Mode:**
- Single white LED indicates selected setting position

## Serial Monitor Output

Connect to Pico's serial port to see debug output:

**Using Thonny:**
- View → Shell (see output in bottom panel)

**Using screen (Linux/Mac):**
```bash
screen /dev/ttyACM0 115200
```

**Example Output:**
```
Wi-Fi Desk Buddy Starting...
Connecting to Wi-Fi: MyNetwork
.........
Wi-Fi Connected!
IP Address: 192.168.1.100
NTP time synchronized
System ready!
Mode: CLOCK
Press MODE button to cycle modes
UP/DOWN buttons control current mode
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **LEDs not lighting** | Check power supply, verify GP16 connection, confirm NUM_LEDS setting |
| **Wi-Fi won't connect** | Verify SSID/password, check 2.4GHz network (Pico doesn't support 5GHz) |
| **Time is wrong** | Adjust UTC_OFFSET for your timezone |
| **Buttons not responding** | Check GPIO connections, verify pull-up configuration |
| **Code won't upload** | Ensure Pico is in bootloader mode, try different USB cable/port |
| **NTP sync fails** | Check internet connection, firewall may block NTP (port 123) |

### Common Issues

**LEDs are too bright:**
```python
BRIGHTNESS = 0.2  # Reduce to 20%
```

**Not enough LEDs lighting:**
```python
NUM_LEDS = 60  # Increase if you have more LEDs
```

**Time off by one hour (DST):**
```python
# Adjust UTC_OFFSET for Daylight Saving Time
UTC_OFFSET = -5 * 3600  # CDT instead of CST
```

## File Structure

```
wifi-desk-buddy/
├── wifi_desk_buddy.py    # Main MicroPython code
├── README.md             # This file
└── boot.py               # Optional: Auto-start configuration
```

### Optional `boot.py` for Auto-Start

Create `boot.py` on Pico to run code automatically on power-up:
```python
# boot.py
import time
time.sleep(2)  # Wait for USB serial
import main    # Runs main.py automatically
```

## Performance

- **Startup Time**: ~5-10 seconds (Wi-Fi + NTP sync)
- **Power Consumption**: 
  - Idle: ~50mA (Pico + LEDs off)
  - Active: ~200-500mA (depends on LED count and brightness)
- **NTP Sync Accuracy**: ±100ms
- **Button Response**: <200ms
- **LED Update Rate**: 20 FPS

## Customization Ideas

### Color Themes
Add preset color schemes:
```python
COLOR_PRESETS = {
    "warm": (255, 100, 0),    # Orange
    "cool": (0, 100, 255),    # Blue
    "nature": (0, 255, 50),   # Green
    "sunset": (255, 50, 100)  # Pink
}
```

### Extended Pomodoro
Implement 4-session cycle:
```python
# 4 work sessions, then long break
LONG_BREAK_MINUTES = 15
session_count = 0
```

### Display Modes
- Show date on button press
- Display room temperature (with sensor)
- Show upcoming calendar events

## Technical Details

### NTP Synchronization
- Uses `pool.ntp.org` server
- Syncs on startup and every 60 minutes
- Applies timezone offset after sync
- Handles network failures gracefully

### LED Control
- WS2812B protocol (NeoPixel)
- 800kHz data rate
- 24-bit RGB color per LED
- Software-based brightness control

### Pomodoro Algorithm
```python
elapsed = current_time - start_time
remaining = duration - elapsed
progress = elapsed / duration
num_leds_lit = progress * NUM_LEDS
```

## License

MIT License - Free to use and modify

## Acknowledgments

Built for improving productivity during study sessions at Texas A&M University, College Station.

---

**Project Duration**: December 2024 - February 2025  
**Location**: College Station, Texas  
**Type**: Personal Project
