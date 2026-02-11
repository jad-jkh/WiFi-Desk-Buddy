"""
Wi-Fi Desk Buddy - NTP Clock & Pomodoro Timer
Raspberry Pi Pico 2 W (RP2350) - MicroPython

Features:
- Wi-Fi synced clock using NTP (Network Time Protocol)
- 12/24-hour time format switching
- RGB LED color customization
- Pomodoro focus timer (25 min work / 5 min break)
- Visual alerts for timer completion
- On-device settings via buttons

Hardware:
- Raspberry Pi Pico 2 W
- WS2812B RGB LED strip (NeoPixel)
- 3x Push buttons (Mode, Up, Down)
- Optional: Buzzer for audio alerts

Required Libraries:
- network (built-in)
- ntptime (built-in)
- neopixel (built-in for Pico W)
- machine (built-in)
- time (built-in)
"""

import network
import ntptime
import time
import machine
from neopixel import NeoPixel
from machine import Pin, PWM

# WIFI SETUP
WIFI_SSID = "YOUR_WIFI_SSID"            # LOL NOT PUTTING MY SSID HERE
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"    # OR MY PASSWORD!!!!!!

# PINS
LED_PIN = 16
BUTTON_MODE = 14
BUTTON_UP = 15
BUTTON_DOWN = 13
BUZZER_PIN = 12

# LED STUFF
NUM_LEDS = 30
BRIGHTNESS = 0.4

# TIMEZONE (DALLAS TX = UTC-6)
UTC_OFFSET = -6 * 3600

# POMODORO DEFAULTS
POMODORO_WORK_MINUTES = 25
POMODORO_BREAK_MINUTES = 5

# INIT HARDWARE
strip = NeoPixel(Pin(LED_PIN), NUM_LEDS)
button_mode = Pin(BUTTON_MODE, Pin.IN, Pin.PULL_UP)
button_up = Pin(BUTTON_UP, Pin.IN, Pin.PULL_UP)
button_down = Pin(BUTTON_DOWN, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty_u16(0)

# STATE MANAGEMENT
class SystemState:
    def __init__(self):
        self.mode = "clock"
        self.use_24_hour = False
        self.clock_color = (255, 100, 0) # type: ignore
        self.brightness = BRIGHTNESS
        
        self.pomodoro_active = False
        self.pomodoro_is_work = True
        self.pomodoro_start_time = 0
        self.pomodoro_work_duration = POMODORO_WORK_MINUTES * 60
        self.pomodoro_break_duration = POMODORO_BREAK_MINUTES * 60
        self.pomodoro_alert = False
        
        self.settings_index = 0
        self.settings_options = [
            "Time Format (12/24)",
            "Color - Red",
            "Color - Green", 
            "Color - Blue",
            "Brightness",
            "Work Duration",
            "Break Duration"
        ]
        
        self.last_mode_press = 0
        self.last_up_press = 0
        self.last_down_press = 0
        self.debounce_ms = 200
        self.last_ntp_sync = 0

state = SystemState()

# WIFI CONNECTION
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to Wi-Fi: {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # CONNECTING ANIMATION
        led_index = 0
        while not wlan.isconnected():
            strip.fill((0, 0, 0))
            strip[led_index % NUM_LEDS] = (0, 0, 255)
            strip.write()
            led_index += 1
            time.sleep(0.1)
            print(".", end="")
    
    print(f"\nWi-Fi Connected!")
    print(f"IP: {wlan.ifconfig()[0]}")
    
    # SUCCESS FLASH
    for _ in range(3):
        strip.fill((0, 255, 0))
        strip.write()
        time.sleep(0.2)
        strip.fill((0, 0, 0))
        strip.write()
        time.sleep(0.2)
    
    return wlan

# NTP SYNC
def sync_time():
    try:
        ntptime.settime()
        state.last_ntp_sync = time.time()
        print("NTP synced")
        return True
    except Exception as e:
        print(f"NTP failed: {e}")
        return False

def get_local_time():
    utc_time = time.time()
    local_time = utc_time + UTC_OFFSET
    return time.localtime(local_time)

# LED HELPERS
def clear_strip():
    strip.fill((0, 0, 0))
    strip.write()

def apply_brightness(color):
    r, g, b = color
    return (
        int(r * state.brightness),
        int(g * state.brightness),
        int(b * state.brightness)
    )

def display_digit(digit, start_pos, color):
    # EACH DIGIT GETS 3 LEDS, HEIGHT = VALUE
    num_leds_on = min(int((digit / 9.0) * 3), 3)
    
    for i in range(3):
        if i < num_leds_on:
            strip[start_pos + i] = apply_brightness(color)
        else:
            strip[start_pos + i] = (0, 0, 0)

def display_time_digits(hours, minutes, seconds):
    clear_strip()
    color = state.clock_color
    
    # HOURS
    h1 = hours // 10
    h2 = hours % 10
    display_digit(h1, 0, color)
    display_digit(h2, 3, color)
    
    # MINUTES
    m1 = minutes // 10
    m2 = minutes % 10
    display_digit(m1, 7, color)
    display_digit(m2, 10, color)
    
    # SECONDS
    s1 = seconds // 10
    s2 = seconds % 10
    display_digit(s1, 14, color)
    display_digit(s2, 17, color)
    
    # SEPARATOR DOTS (BLINK)
    if seconds % 2 == 0:
        strip[6] = apply_brightness(color)
        strip[13] = apply_brightness(color)
    
    strip.write()

def display_clock():
    current_time = get_local_time()
    hours = current_time[3]
    minutes = current_time[4]
    seconds = current_time[5]
    
    # 12HR FORMAT IF NEEDED
    if not state.use_24_hour:
        if hours == 0:
            hours = 12
        elif hours > 12:
            hours -= 12
    
    display_time_digits(hours, minutes, seconds)

# POMODORO FUNCTIONS
def start_pomodoro():
    state.pomodoro_active = True
    state.pomodoro_start_time = time.time()
    state.pomodoro_alert = False
    
    session_type = "WORK" if state.pomodoro_is_work else "BREAK"
    duration = state.pomodoro_work_duration if state.pomodoro_is_work else state.pomodoro_break_duration
    print(f"Pomodoro {session_type} started - {duration // 60} min")

def stop_pomodoro():
    state.pomodoro_active = False
    print("Pomodoro stopped")

def pomodoro_elapsed_seconds():
    if not state.pomodoro_active:
        return 0
    return int(time.time() - state.pomodoro_start_time)

def pomodoro_remaining_seconds():
    duration = state.pomodoro_work_duration if state.pomodoro_is_work else state.pomodoro_break_duration
    elapsed = pomodoro_elapsed_seconds()
    return max(0, duration - elapsed)

def check_pomodoro_completion():
    if not state.pomodoro_active:
        return
    
    remaining = pomodoro_remaining_seconds()
    
    if remaining == 0 and not state.pomodoro_alert:
        state.pomodoro_alert = True
        state.pomodoro_active = False
        play_alert()
        
        # FLIP SESSION TYPE
        state.pomodoro_is_work = not state.pomodoro_is_work
        session_type = "BREAK" if state.pomodoro_is_work else "WORK"
        print(f"Session done! Time for {session_type}")

def display_pomodoro():
    if state.pomodoro_alert:
        alert_animation()
        return
    
    if not state.pomodoro_active:
        # READY TO START PATTERN
        strip.fill((0, 0, 0))
        for i in range(0, NUM_LEDS, 3):
            strip[i] = apply_brightness((100, 100, 100))
        strip.write()
        return
    
    # PROGRESS BAR
    duration = state.pomodoro_work_duration if state.pomodoro_is_work else state.pomodoro_break_duration
    elapsed = pomodoro_elapsed_seconds()
    progress = elapsed / duration
    
    # GREEN FOR WORK, BLUE FOR BREAK
    color = (0, 255, 0) if state.pomodoro_is_work else (0, 100, 255)
    
    num_lit = int(progress * NUM_LEDS)
    
    clear_strip()
    for i in range(num_lit):
        strip[i] = apply_brightness(color)
    strip.write()

def alert_animation():
    # FLASH RED/YELLOW
    current_ms = time.ticks_ms()
    if (current_ms // 500) % 2 == 0:
        strip.fill(apply_brightness((255, 0, 0)))
    else:
        strip.fill(apply_brightness((255, 255, 0)))
    strip.write()

def play_alert():
    # 3 BEEPS
    for _ in range(3):
        buzzer.freq(1000)
        buzzer.duty_u16(32768)
        time.sleep(0.2)
        buzzer.duty_u16(0)
        time.sleep(0.2)

# SETTINGS MENU
def display_settings():
    clear_strip()
    
    # SHOW CURRENT SETTING POSITION
    setting_led = int((state.settings_index / len(state.settings_options)) * NUM_LEDS)
    
    for i in range(NUM_LEDS):
        if abs(i - setting_led) < 2:
            strip[i] = apply_brightness((255, 255, 255))
        else:
            strip[i] = (0, 0, 0)
    
    strip.write()
    print(f"Setting: {state.settings_options[state.settings_index]}")

def adjust_setting(increment):
    idx = state.settings_index
    
    if idx == 0:  # TIME FORMAT
        state.use_24_hour = not state.use_24_hour
        print(f"Time format: {'24-hour' if state.use_24_hour else '12-hour'}")
    
    elif idx == 1:  # RED
        r, g, b = state.clock_color
        r = max(0, min(255, r + (increment * 10)))
        state.clock_color = (r, g, b)
        print(f"Red: {r}")
    
    elif idx == 2:  # GREEN
        r, g, b = state.clock_color
        g = max(0, min(255, g + (increment * 10)))
        state.clock_color = (r, g, b)
        print(f"Green: {g}")
    
    elif idx == 3:  # BLUE
        r, g, b = state.clock_color
        b = max(0, min(255, b + (increment * 10)))
        state.clock_color = (r, g, b)
        print(f"Blue: {b}")
    
    elif idx == 4:  # BRIGHTNESS
        state.brightness = max(0.1, min(1.0, state.brightness + (increment * 0.1)))
        print(f"Brightness: {state.brightness:.1f}")
    
    elif idx == 5:  # WORK TIME
        state.pomodoro_work_duration = max(60, state.pomodoro_work_duration + (increment * 60))
        print(f"Work: {state.pomodoro_work_duration // 60} min")
    
    elif idx == 6:  # BREAK TIME
        state.pomodoro_break_duration = max(60, state.pomodoro_break_duration + (increment * 60))
        print(f"Break: {state.pomodoro_break_duration // 60} min")

# BUTTON HANDLING
def handle_buttons():
    current_ms = time.ticks_ms()
    
    # MODE BUTTON
    if button_mode.value() == 0:
        if time.ticks_diff(current_ms, state.last_mode_press) > state.debounce_ms:
            state.last_mode_press = current_ms
            
            modes = ["clock", "pomodoro", "settings"]
            current_idx = modes.index(state.mode)
            state.mode = modes[(current_idx + 1) % len(modes)]
            
            print(f"Mode: {state.mode.upper()}")
            mode_change_animation()
    
    # UP BUTTON
    if button_up.value() == 0:
        if time.ticks_diff(current_ms, state.last_up_press) > state.debounce_ms:
            state.last_up_press = current_ms
            handle_up_button()
    
    # DOWN BUTTON
    if button_down.value() == 0:
        if time.ticks_diff(current_ms, state.last_down_press) > state.debounce_ms:
            state.last_down_press = current_ms
            handle_down_button()

def handle_up_button():
    if state.mode == "clock":
        pass
    
    elif state.mode == "pomodoro":
        if state.pomodoro_alert:
            state.pomodoro_alert = False
        elif not state.pomodoro_active:
            start_pomodoro()
    
    elif state.mode == "settings":
        adjust_setting(1)

def handle_down_button():
    if state.mode == "clock":
        pass
    
    elif state.mode == "pomodoro":
        if state.pomodoro_active:
            stop_pomodoro()
        elif state.pomodoro_alert:
            state.pomodoro_alert = False
    
    elif state.mode == "settings":
        state.settings_index = (state.settings_index + 1) % len(state.settings_options)
        print(f"Selected: {state.settings_options[state.settings_index]}")

# ANIMATIONS
def startup_animation():
    print("Starting up...")
    for i in range(NUM_LEDS):
        hue = int((i / NUM_LEDS) * 255)
        strip[i] = apply_brightness(hsv_to_rgb(hue, 255, 255))
        strip.write()
        time.sleep(0.05)
    
    time.sleep(0.5)
    clear_strip()

def mode_change_animation():
    strip.fill(apply_brightness((255, 255, 255)))
    strip.write()
    time.sleep(0.1)
    clear_strip()

def hsv_to_rgb(h, s, v):
    if s == 0:
        return (v, v, v)
    
    h = h / 255.0 * 6.0
    i = int(h)
    f = h - i
    
    p = int(v * (1.0 - s / 255.0))
    q = int(v * (1.0 - s / 255.0 * f))
    t = int(v * (1.0 - s / 255.0 * (1.0 - f)))
    v = int(v)
    
    i = i % 6
    
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    return (v, p, q)

# MAIN LOOP
def main():
    print("Wi-Fi Desk Buddy Starting...")
    
    startup_animation()
    wlan = connect_wifi()
    sync_time()
    
    print("Ready!")
    print(f"Mode: {state.mode.upper()}")
    print("MODE button cycles modes")
    print("UP/DOWN control current mode")
    
    while True:
        try:
            handle_buttons()
            
            # RESYNC EVERY HOUR
            if time.time() - state.last_ntp_sync > 3600:
                sync_time()
            
            # RUN CURRENT MODE
            if state.mode == "clock":
                display_clock()
            elif state.mode == "pomodoro":
                check_pomodoro_completion()
                display_pomodoro()
            elif state.mode == "settings":
                display_settings()
            
            time.sleep(0.05)
        
        except KeyboardInterrupt:
            print("\nShutting down...")
            clear_strip()
            buzzer.duty_u16(0)
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()