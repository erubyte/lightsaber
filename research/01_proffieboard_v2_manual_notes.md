# Notes: ProffieBoard v2 User Manual (rev 07, updated 2021-06-26)

Source: https://www.fett263.com/ProffieBoard_v2_User_Manual_07.pdf (local copy: `sources/fett263_ProffieBoard_v2_User_Manual_07.pdf`, text in `sources/fett263_manual.txt`).

It's hosted on fett263.com, but the authors are **Dmitry Shtok (ShtokCustomWorx) and Fredrik Hübinette (Profezzorn)**. It's a 2020–2021 document written for **installers** (people wiring a board into an empty hilt), not for owners of a finished saber. Some of it is dated (Arduino-only workflow, ProffieOS 3.x/4.x era defines, ForceSync "in development"). Current ProffieOS is 7.x/8.x (verify in later notes).

## Origin story (Fredrik's intro, 2016)
- Disneyland toy sabers disappointed him; he bought an FX "black series" Luke, and the sound and interactivity were still weak.
- He wanted **sound that reacts fluidly to motion**. NEC and Plecter boards (the commercial boards of the time) gave no way to change how sounds were produced.
- He started with a Teensy 3.2 + PJRC prop shield + SD reader + booster + FETs, crammed into a Graflex 2.1.
- Implemented Plecter and NEC font support so existing fonts would play.
- TeensySaber V2: his own PCB, sized for a Korbanth OWK (7/8 in inner diameter). V3 added a digital 3 W amp.
- **Thexter** posted videos of a better swing-sound algorithm and described it; Fredrik implemented it. Thexter's later improved version = **SmoothSwing V2**.
- TeensySaber V3 was two stacked boards. For a single board he based the design on the open-source **Butterfly** (STM32L4) board, which already had an Arduino core and was 100% open source (Teensy is only mostly open). Designed over a Christmas vacation; prototype took a couple more months.
- Interview: SaberSourcing, "Proffieboard lightsaber controller developer Fredrik Hubinette interview".

## Hardware features (V2.2)
- 17.8 × 33.2 × 4 mm (+3.2 mm with micro-USB and SD).
- GPLv3, "you may add any feature you like".
- Supply 2.6–4.5 V. **Up to 10 A per LED output** (6 MOSFET channels, low-side, rated to 30 V).
- Idle sleep drain about 1.3 mA, about 3.5–4 months shelf time.
- Speaker 4 or 8 Ω, 2–5 W recommended. Amp: 3 W, 5 V, 16-bit digital (I²S).
- Unlimited fonts. Plecter, NEC and SmoothSwing fonts.
- 44 kHz default; 22 kHz and 11 kHz are upsampled automatically.
- **Gapless playback, 2.5 ms cross-fade** when one sample interrupts another.
- **Polyphonic, up to 5 simultaneous samples**.
- **4 data outputs** for Neopixel (WS2812B, SK6812 RGB/RGBW/WWA, PL9823).
- In-hilt LED stars (Tri-Cree, quad RGBW), segmented string blades (6 segments + flash-on-clash string).
- Multi-blade (dual, crossguard). Accent LEDs are just extra "blades" and can run any blade style.
- **Blade ID** (resistor value tells the board which blade is in) and **Blade Detect** (a pin acts like a latching button when a blade is inserted). bladein.wav / bladeout.wav.
- OLED display support (power-level, font name, animations).
- IR receive, POV (persistence of vision) mode, spoken error and low-battery messages.
- 3.3 V pad, about 250 mA, for Bluetooth or OLED. "SD power" pad is FET-switched 3.3 V so add-ons power down in standby.
- USB Mass Storage: the SD card shows up as a drive over the board's USB.
- **SWDCLK / SWDIO pads: hook up an ST-LINK and debug programs running on the board.** (Important for a CS/ECE person: real hardware debugging.)
- BOOT and RESET buttons for bootloader (DFU) mode.

## Pinout (Arduino pin numbers in parentheses)
Activation button 1 (21), Aux button 2 (23), Aux2 button 3 (22); LED 1–6 = (13), (19), (18), (10), (5), (6); Data 1 / Blade ID (16) with an on-board 470 Ω series resistor; Data 2 (1), Data 3 (17), Data 4 / DAC (0); SDA (7), SCL (25); TX (9), RX (8); SD power (11). BATT− for LED negatives, GND for electronics (internally connected, but battery negative must go to BATT−).

## Config file anatomy (this is the core concept)
A ProffieOS config is a C++ header with four `#ifdef` sections:
- `CONFIG_TOP`: board include (`proffieboard_v2_config.h`), `NUM_BLADES`, `NUM_BUTTONS`, `VOLUME` (0–3000), `maxLedsPerStrip`, `CLASH_THRESHOLD_G`, `ENABLE_AUDIO/MOTION/WS2811/SD`, plus feature defines.
- `CONFIG_PROP`: which prop file (button logic) to include, e.g. `../props/saber_fett263_buttons.h`.
- `CONFIG_PRESETS`: `Preset presets[]` (font folder, music track, one blade style per blade, display name) and `BladeConfig blades[]` (Blade ID value → hardware blade definitions → which preset array).
- `CONFIG_BUTTONS`: `Button PowerButton(BUTTON_POWER, powerButtonPin, "pow");` etc.

Hardware definitions are C++ templates: `WS281XBladePtr<144, bladePin, Color8::GRB, PowerPINS<bladePowerPin2, bladePowerPin3> >()` (144 pixels, data pin, color byte order, which MOSFETs switch the strip's power). `SimpleBladePtr<CreeXPE2RedTemplate<1000>, ...>` for in-hilt LEDs (resistor in milliohms). `StringBladePtr<Blue3mmLED, BladePin, White3mmLED>` for segmented strings.

Blade styles are templates too: `StyleNormalPtr<CYAN, WHITE, 300, 800>()` (base color, clash color, ignition ms, retraction ms), `StylePtr<InOutSparkTip<EASYBLADE(BLUE, WHITE), 300, 800> >()`, `StyleFirePtr<RED, YELLOW>()`, `StyleRainbowPtr<300, 800>()`, `IgnitionDelay<300, ...>`.

The whole saber behavior is resolved at **compile time** from templates. This is the key nerd point: blade styles are a C++ template DSL that compiles into per-pixel color functions.

## Useful defines listed (3.x/4.x era; check against current docs)
- `ENABLE_DEVELOPER_COMMANDS`, `DISABLE_DIAGNOSTIC_COMMANDS` (removes `monitor`, `top`, `sdtest`).
- `BLADE_ID_CLASS BridgedPullupBladeID<...>` / `ExternalPullupBladeID<...>`.
- `IDLE_OFF_TIME 60 * 10 * 1000` (ms) to turn off accent LEDs after 10 min.
- `BLADE_DETECT_PIN`. Without a blade, NO_BLADE (one billion) is added to the Blade ID.
- `DISABLE_COLOR_CHANGE`, `SAVE_COLOR_CHANGE`, `SAVE_PRESET`, `SAVE_VOLUME`, `SAVE_STATE`.
- `KEEP_SAVEFILES_WHEN_PROGRAMMING` (from OS 4.7, uploading deletes .ini save files unless this is set).
- `ORIENTATION ORIENTATION_USB_TOWARDS_BLADE` for boards mounted backwards.
- `ENABLE_SERIAL` for a Bluetooth/serial module on RX/TX.

## Serial monitor commands (USB serial, 115200)
`battery_voltage`, `get_volume`, `set_volume <0-3000>`, `pow`, `on`, `off`, `play`, `play_track tracks/x.wav`, `stop_track`, `force`, `drag`, `blast`, `lock`, `clash`, `reset`, `n`, `p`, `list_presets`, `sdtest` (SD read speed), `scanid` (prints Blade ID resistance). Diagnostics like `monitor` and `top` exist too.

This is a big hook for an engineer: the saber has a **command shell over USB serial**.

## Prop files
Button behavior lives in `props/`. Bundled alternatives: `saber_sa22c_buttons.h`, `saber_shtok_buttons.h`, `saber_fett263_buttons.h` (ours). Select in `CONFIG_PROP`. You can write your own prop file.

## Firmware workflow (Arduino)
1. Install Arduino IDE (not beta). Install the Proffieboard Arduino plugin (board package) and, on Windows, Zadig for drivers.
2. Tools → Board: Proffieboard V2. USB Type: Serial + Mass Storage (or + WebUSB). CPU 80 MHz. Optimize: Smallest Code. DOSFS: SDCARD (SPI).
3. Download ProffieOS and the SD card content. Put a config in `ProffieOS/config/`, set `#define CONFIG_FILE "config/your_config.h"` in `ProffieOS.ino`.
4. Upload over a data-capable micro-USB cable. Boot sound plays on success.
5. If it only shows as "STM32 BOOTLOADER": hold BOOT, press RESET, then upload.

## SD card
- FAT32, 4–32 GB, SanDisk recommended, speed over about 900 kB/s (`sdtest`).
- Font folders and track names: Latin characters, no special characters.
- Each font folder should have `config.ini` and `smoothsw.ini`.

## Bluetooth (optional add-on, not in our saber)
- Feasycom FSC-BT630 (nRF52832, BLE only, tiny) or FSC-BT909 (CSR8811, SPP + BLE). Wired to RX/TX + 3.3 V. `ENABLE_SERIAL`.
- Apps: ForceSync (ShtokCustomWorx), FeasyBlue for setting name/PIN.
- "No switch" wiring powers the module from a LED channel so it shuts down in standby (`IDLE_OFF_TIME`).

## Troubleshooting entries
- "Font directory not found" → folder names must match presets exactly; reformat FAT32.
- Board not seen by the computer → cable, drivers, BOOT+RESET.
- Compile errors like "cannot convert StyleFactory*" → wrong number of styles per preset vs NUM_BLADES.
- Stutter → slow SD card, weak battery, bad speaker.

## Relevance to this saber
Our saber is a finished pogo core (NexusSabers LGT A.294-1, Proffie V2.2, Fett263 prop). Most wiring content doesn't apply unless he builds his own hilt. What does apply: config anatomy, serial commands, Blade ID/Detect concepts, SWD debug pads, the Arduino workflow, SD rules.
