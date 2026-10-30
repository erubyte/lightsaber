# Synthesis: what should go in the manual (mostly section 3)

Research notes behind this: files 01–07 in this folder. Status 2026-10-29: all proposed pages are now in the manual (pages 25–40, with "Get started with Proffie" on pages 30–33). The seven on-saber checks below are still open.

## The answer to "why did I pay extra for Proffie?"
Short version for the manual: **a Xenopixel saber is a finished product; a Proffie saber is a platform.** The LEDs, battery and speaker are the same class of parts. The extra money buys:

1. **Open everything.** The firmware is GPLv3 C++ (about 80,000 lines on GitHub), and the board is open hardware: KiCad files, schematic and BOM are published under the TAPR Open Hardware License. Closed boards (Xenopixel, SN-Pixel, CFX, Golden Harvest) publish none of this.
2. **Behavior is code.** Button and gesture logic is a "prop file", a C++ state machine he can read, copy and rewrite. ProffieOS ships 11 props.
3. **Visuals are code.** A blade style is a C++ template expression evaluated for every LED on every frame. Anything the language can express, the blade can show. Closed boards offer a fixed menu (Xenopixel V3: 11 blade modes, 7 ignitions).
4. **Sound can be driven by code.** Since OS 7, styles can switch whole sound sets live (alt fonts), trigger sounds at points in an animation, and chain conditional effects. That's how people built a training-remote mini game, light-to-dark corruption, and interactive blaster deflection that only happens if you actually move the blade in time.
5. **It keeps getting better for free.** The same 2019 V2.2 board runs ProffieOS 8.10 (Feb 2026), which added a new menu system, color displays, SD-card corruption protection and dual-blade control.
6. **It's hackable at every level**: a USB serial shell, a browser editor (Workbench), a live style simulator, SWD debug pads, host-side unit tests, spare GPIO, I²C and UART.

For him specifically (CS + ECE): it's an STM32 Cortex-M4 embedded system with a 6-axis IMU at 1.66 kHz, I²S audio, DMA-driven LED output, cooperative coroutines, an event bus and a template DSL, all documented and modifiable.

## Facts to verify on the actual saber before writing version-specific pages
These decide what the manual can promise. Each takes a minute with the saber on USB:
1. **ProffieOS version**: serial command `version`. If it's 6.x/7.x, OS 8 menu features don't apply until he upgrades.
2. **Is the factory config on the SD card?** Look for a `.h` file or a ProffieOS zip. DamienSaber has sent wrong configs before (Crucible thread 6175, Dec 2024). If it's missing, ask DamienSaber for it. Without it, a new config has to be rebuilt from the wiring, `presets.ini` and the font list (Fredrik's 7-step recipe in note 05/06).
3. **WebUSB and Mass Storage enabled?** Decides whether Workbench and drag-and-drop fonts work without opening the core.
4. **Which Edit Mode variant**: full Edit Mode (`FETT263_EDIT_MODE_MENU`), Edit Settings only, or OS 8 menus. The manual's Edit Mode page already hedges with a `{TODO}`.
5. **Rehearsal vs Special Abilities**: `FETT263_SAVE_CHOREOGRAPHY` (our Rehearsal page) can't be combined with `FETT263_SPECIAL_ABILITIES`. Confirm the Rehearsal page applies.
6. **Pixel count** of the blade (`WS281XBladePtr<N, ...>` in the config, or the `LengthFinder` style). 32 in blades are usually around 114–117 pixels per strip.
7. **Can BOOT/RESET be reached** in the LGT core? Fett263 says installers should make them accessible. `RebootDFU` over serial avoids needing them while the firmware runs.

## Checks against the current manual
- One-button controls (Quick reference, Control pages, Color, Rehearsal, Edit Mode): **checked against `props/saber_fett263_buttons.h` and they match**, including Click + Long Click for a muted ignition, Double Click + Long Click for battery level, 4 clicks for color change, Double Click and Hold for Edit Mode, and Triple Click and Hold for Rehearsal.
- Two small additions the source supports:
  - Hold + Clash does two different things depending on angle: parallel or up opens the volume menu, pointing down toggles gesture sleep. The Quick reference lists only "Volume".
  - Double Click with the blade off depends on angle: pointing straight up starts or stops the track, parallel or down opens the Track Player.
- "Proffie font folders work as they are" (Sound fonts page): true for Proffie-format fonts. Fonts in Xenopixel or CFX format need renaming first. A free cross-board converter exists (Mormegil / NoSloppy SoundFontNamingConverter).
- "A motion sensor reads 1,600 times a second": correct (LSM6DS3H at 1.66 kHz, ProffieOS default `PROFFIEOS_MOTION_FREQUENCY 1600`).
- "Up to five sounds at once": matches the official manual's default.
- Glossary "Neopixel" and "Xenopixel" entries are accurate.

## Proposed section 3 (Customization), in priority order
The current section 3 is: What is Proffie · Glossary · Edit Mode · Rehearsal · Sound fonts and SD card · Quick reference. Pages are 85 × 130 mm, so each idea below is one page with one diagram or table. Recommended set marked ★.

### ★ 1. Why Proffie (rewrite of "What is Proffie")
- Keep the origin line (Fredrik Hübinette, Profezzorn).
- Replace the feature list with a **two-column comparison: Xenopixel vs Proffie** (who controls the code, blade effects, sounds, buttons, updates, hardware access). One sentence: same LEDs, different relationship with the hardware.
- Optional one-line history: built because NEC and Plecter boards wouldn't let him change how sound reacted to motion; SmoothSwing came from Thexter.

### ★ 2. Saber types (new; could replace the glossary's "Other saber types")
- One table: Baselit/RGB vs Neopixel (how lit, ignition look, clash look, dueling durability).
- One row of boards: Xenopixel, SN-Pixel, Golden Harvest, CFX, Verso, Proffie, each with "open or closed" and "how you configure it".
- Blade facts: 1 in vs 7/8 in, thin vs heavy wall; ours is 1 in heavy-grade 32 in. (Section 2's "The blade" page has some of this; keep it brief here.)

### ★ 3. Before you change anything (new)
Numbered steps:
1. Copy the whole SD card to a computer.
2. Find the config file (a `.h` on the card or in a zip). If it's missing, ask DamienSaber for it.
3. Back up the firmware: profezzorn.github.io/webdfu/dfu-util/ → `RebootDFU` → Connect → Read → save the `.bin`.
4. To undo on-saber edits: delete `presets.ini` and `presets.tmp`.
- Tip: the STM32's ROM bootloader can't be overwritten, so a bad upload is always recoverable.

### ★ 4. Connect to a computer (new)
- Data-capable micro-USB on the board, never for charging.
- Three things show up: a **serial port**, a **WebUSB** device and possibly a **drive** (the SD card).
- Small table of serial commands: `version`, `list_presets`, `battery_voltage`, `sdtest`, `on`, `off`, `clash`, `n`/`p`, `set_volume`, `RebootDFU`.
- **ProffieOS Workbench** (browser, Chrome or Edge): volume, presets, tracks, trigger effects, edit presets.

### ★ 5. The config file (new)
- One annotated snippet with the four sections: `CONFIG_TOP` (defines), `CONFIG_PROP` (Fett263 prop), `CONFIG_PRESETS` (font, track, style, name; blade definition with pixel count, data pin, power FETs), `CONFIG_BUTTONS`.
- One line on the toolchain: Arduino IDE with the Proffieboard plugin, or ProffieConfig, or JMT Studio, or Fett263 Config Helper with the Web Programmer.
- What needs a recompile and what doesn't: fonts, colors, timings and preset order don't (Edit Mode / Workbench); new styles, defines and props do.

### ★ 6. Blade styles (new)
- Concept: every pixel's color is a function of position, time and events; even `Red` is a style.
- A tiny example, e.g. `StylePtr<Layers<AudioFlicker<Green, DarkGreen>, ResponsiveClashL<White>, InOutTrL<TrWipe<300>, TrWipeIn<500>>>>()`, with three labels (base, clash layer, ignition and retraction).
- Tools: Style Editor (live simulator), Fett263 Style Library, plus a QR code for each.
- Style arguments: why copies of one style cost no extra memory and can be edited in Edit Mode.

### ★ 7. Under the hood (new; the page he'll love)
- One diagram: IMU (accel ±16 g, gyro ±2000 dps, 1.66 kHz, I²C) → fusion (down vector, swing speed, twist) → event bus (`SaberBase`: clash, blast, lockup, on, off) → two consumers: **sound** (polyphonic WAV mixer → I²S → 3 W amp) and **blade style** (per-LED function → DMA timer → WS2812 strips). Buttons → prop file → event bus.
- SmoothSwing in three lines: two looping swing sounds play silently under the hum; swing speed sets volume, and accumulated rotation crossfades between the low and high loops; the hum ducks as you swing.
- Clash detection in one line: `|accel − down|/2 + |Δgyro|/2 > threshold`, and why speaker vibration made this hard.
- Specs line: STM32L433, 80 MHz Cortex-M4F, 256 KB flash, 64 KB RAM, no RTOS (cooperative "loopers" and line-number coroutines).

### 8. Modding ideas (new; for the CS/ECE reader)
A short list, each item one line and one link:
- Upgrade to ProffieOS 8.10 (menus, SD protection).
- Write your own prop: change one `EVENTID(...)` case.
- Write a style or function and test it on the host (`make test` in `styles/`).
- Debug on hardware with an ST-LINK on the SWDIO/SWCLK pads.
- Add a BLE module (FSC-BT630) for Workbench over Bluetooth.
- Alt fonts: light/dark versions of one font (a fit for Quinlan Vos and Dark Disciple).
- Fett263 interactive styles: mini game, interactive preon, Kyber Select.
- Board files: KiCad at fredrik.hubbe.net/lightsaber/v5/board22.html.

### Keep: Edit Mode, Rehearsal (once items 4 and 5 of the checklist above are verified)

### Expand: Sound fonts and SD card
- Font folder anatomy (hum, swingl/swingh, clsh, out/in, font.wav, config.ini, smoothsw.ini).
- 44.1 kHz 16-bit mono WAV.
- Where to get fonts: Kyberphonic, Greyscale Fonts (free section), KSith, JayDalorian, Saberfont.com. Licenses are per person for their own collection.
- Format converter for non-Proffie fonts.

### Glossary additions
Alt font · Bootloader (DFU) · Config file · Edit Mode · Prop file (exists) · Serial monitor · Style argument · Workbench · SD card save files (presets.ini).

### ★ Resources page (new, with QR codes like the rest of the manual)
POD docs (pod.hubbe.net) · The Crucible forum · Fett263 (fett263.com) · Style Editor · Workbench · ProffieOS on GitHub · A video list once you've reviewed `07_videos_to_review.md`.

## Section 2 tie-ins (small)
- The Electronics page could add the pixel count and power figures once confirmed (2 strips × N pixels; up to about 60 mA per pixel at full white, so a full-white 32 in blade can draw 13 A or more; that's why the blade uses two MOSFET channels and needs a high-drain cell).
- The Proffieboard V2.2 is discontinued in favor of V3.9 (more flash and RAM, SDIO, on-board charging). One line in the Electronics page, so he isn't surprised when reading current docs.

## Decisions for you
1. Which of pages 1–8 to build (★ = my recommended set: 1–7 plus Resources; 8 if there's room).
2. Whether to verify the seven facts on the saber before writing (recommended), or write pages with hedges.
3. Whether to ask DamienSaber for the factory config now (it's the one thing he'll most want, and the vendor is the only source).
