# ProffieOS versions and Fett263 feature catalog

## Version history (from GitHub releases and The Crucible)
Sources: https://github.com/profezzorn/ProffieOS/releases, https://crucible.hubbe.net/t/proffieos-8-is-now-live/7698

- **ProffieOS 8.10** is current. Released **2026-02-22** after more than a year of beta. Download: fredrik.hubbe.net/lightsaber/proffieos.html or GitHub.
- 7.15 was the last 7.x (bug fixes for Fett263 Special Abilities, MultiTransitionEffect, TrWave).
- 7.7 was the big 7.x feature drop (since 6.9). ProffieOS 7 runs on Teensy V3, Proffieboard V1.5, V2.2, V3.7/V3.9.
- Our saber's installed version is unknown. Factory cores often ship 6.x or 7.x. The serial command `version` (or the boot log) shows it. Check before writing anything version-specific.

### OS 8 headline features
- **Menu system** decoupled from the prop file. `MENU_SPEC_TEMPLATE` picks the menu. Supported by saber, BC and Fett263 props. Menus: Edit Settings (volume, SD access, dimming, clash threshold, blade length), Edit Preset (font, track, move, insert, delete), Edit Style (select style, apply colors/settings, reset), Style Settings (colors, numbers, times), Color Edit (hue, brightness, RGB, named colors, copy/paste).
- **Sound Library V2**: more spoken menu prompts, configurable color list.
- **Color display support** (16-bit). Layered compositing. New animation format **PQF** (about 50% compression, fast decode, loops, labels, conditions that react to saber events).
- **SD card corruption protection** (`MOUNT_SD_SETTING`): the card doesn't auto-mount over USB; you enable access from the menu or serial (`sd` command), then turn it off again.
- **Dual-blade support**: per-blade on/off state (Maul-style).
- Servo support, FastButton, LeftRightRotaryReceiver, SubBladeWithList, blaster OLED controller.
- New defines include `PROFFIEOS_LOG_LEVEL`, `FONT_PATTERN`, `ENABLE_IDLE_SOUND`, `BUTTON_LONG_CLICK_TIMEOUT`, `CLASH_THRESHOLD_GAMMA`, `DISABLE_AUDIO/WS2811/MOTION/SD`, `BLADE_ID_SCAN_TIMEOUT`.
- New styles: `DisplayStyle`, `Pixelate`, `HardStripes`, `TransitionLoopWhile`. New functions: `ReadPinF`, `AnalogReadPinF` (read a GPIO from a blade style), `IntSelectX`, blaster functions.
- New serial commands: `sd`, `quote`, `swing`, `slash`, `spin`, `get_variation`, `|` (tag).
- About 40 new named colors (ElectricLime, MasterSwordBlue, ZeusBolt, ...).
- New sounds: `fastout`, `quote`, `chhum`, `mclick`, `idle`.
- New props: `sabersense_buttons.h` (simpler harmonized 1/2-button), `blaster_BC_buttons.h`. BC prop gets dual-blade staff control and 8 user effects.
- Fett263 prop in OS 8: `MENU_SPEC_TEMPLATE`, `MOUNT_SD_SETTING` in Edit Mode, `FONT_PATTERN`, `FETT263_MANUAL_BLADE_ID`, `FETT263_MANUAL_BLADE_ARRAY`, `FETT263_REPLACE_CC_COLOR_LIST` (hue rotation instead of color list), `FETT263_SIMPLIFIED_PROP`, `FETT263_SWING_CLASH_DELAY`, `FETT263_SS_BUTTON_CLICKER`, circular volume and dim menus.
- Testers credited: BlackDragonN001, Bruinrogue, Farnsworth9qc, Fett263, hkwwinger, kersskerner, LyleStyle, NoSloppy, olivierflying747-8, orntar, SaberSense, Triin.

### OS 7.7 highlights (since 6.9)
- New INI read/write code, much less SD corruption.
- **Alt fonts** (`altNNN/` folders): style code can switch the whole sound set live.
- Sub-sub sound directories (`hum/001/001.wav`).
- Updated clash detection.
- **Bendable time** in transitions (accelerating/decelerating ignitions).
- New config section **CONFIG_STYLES** (define styles once, reference by name).
- All `config.ini` files in the font search path are read.
- New prop `saber_caiwyn_buttons.h`.
- Experimental **ESP32-S3** support.
- Pairable sound transitions: lock/endlock, drag/enddrag, melt/endmelt, lb/endlb, armhum/endarm.
- New transitions: `TrBlink`, `TrDoEffect`, `TrDoEffectAlways`, `TrLoop`, `TrLoopN`, `TrLoopUntil`. New functions: `TwistAcceleration`, `AltF`, `SyncAltToVarianceF`, `VolumeLevel`, `ModF`, `IsBetween`...
- Styles: `StylePOV`, `ContinuousPOV`, `ChargingStylePtr`, `LockupTrL`.
- Fett263 prop: force/quote while off, quick select, circular volume/dimming, special abilities, spin mode, edit settings menu, quick select on boot, quiet track player.

## Fett263 (Fernando da Rosa) feature catalog
Source: https://www.fett263.com/proffieOS7-intro.html

Fett263 is the most prolific ProffieOS contributor: the prop file our saber uses, the Style Library, the Config Helper, Edit Mode, and a long YouTube series of proof-of-concept videos. Paid Patreon "Early Access" library for the newest styles; the main library is free.

### OS6 features (now standard)
- **Edit Mode** and **ProffieOS Workbench** (WebUSB browser UI) to edit presets, colors, styles on the saber.
- **Battle Mode 2.0**: lockup, drag, melt triggered by motion alone, no buttons.
- **Real Clash**: clash sound and flash scale with how hard the blade is hit.
- Acceleration-based accent swings (swing sounds layered on top of SmoothSwing).
- Track player, quote player, voice prompts.
- **Gesture ignitions/retractions** (swing on, thrust on, twist on, stab on) and **Gesture Sleep** to disable them.
- **Rehearsal / Choreography Mode** (record and replay clash/lockup sequences).
- Dual Mode effects and sounds (different sound/visual for pointing up vs down).
- **Style Options** (one style with selectable variants) and **Interactive "Kyber Select"** (Fallen Order-style crystal selection).
- Intensity Lockup, Lightning Block, Melt.
- "Deep sleep": V2.2 has no true deep sleep; standby is about 6 months with good wiring; use a kill switch or remove the battery for indefinite storage.

### OS7 features
- **Style ↔ sound synergy**: styles can trigger and change sounds (before, styles only followed sounds via `WavLen`, `WavNum`, `NoisySoundLevel`).
- **Alt fonts** controlled by styles: Pull to the Darkness (light→dark side corruption), Cortosis Clash, Interactive Ice Blade (frozen sounds), Kinetic build-up, Infinity Gauntlet stones.
- **Transition sounds**: sounds attached to visual transitions.
- **Special Abilities**: per-preset custom controls; each preset behaves like its own "video game". Demo: Last Airbender (Air, Fire, Water, Earth in one preset).
- **Blade States**: on-demand rain blade with looped rain sound.
- Quote controls: random or sequential, grouped by mood/character, scripted conversations.
- Up to 5 on-demand ignition effects.
- **Chained and conditional effects**: e.g. interactive blast deflection where a blaster shot sound plays and you must actually move the saber in time to deflect; random-length chains of shots.
- **Interactive preons**: a faulty sputtering ignition you can "smack" to start, or a "security" gesture that must be performed to unlock ignition.
- **Style-based mini games**: ANH training remote game (sound-only, react to blast sounds, 3 strikes, win to unlock a new blade style). Built with KyberPhonic's "ANH Training" font.
- Staff/dual-blade on one board with conditional secondary ignition.
- Accelerating/decelerating ignitions with a "bend" value.
- **Quick Select**: rotate the hilt like a dial through presets, hold to ignite. `FETT263_QUICK_SELECT_ON_BOOT`.
- Circular volume menu; `EFFECT_VOLUME_LEVEL` to show volume on the blade.
- New clash detection settings.
- **Config Helper Tool** compiles configs for Fredrik's **Web Programmer** (flash without Arduino) and generates a custom user manual for your config.

### July 2025: Gesture-Based Special Abilities and Multi-Phase (Early Access)
- Up to 10 "phases" per blade, each a different style + alt font, triggered by gestures: point up and hold, point down and hold, hold parallel, point up then swing, quick 1/4 turn, swing X times, clash X times, blast X times, ignite while pointing up/down/parallel, clash while off, stab up/down, force, quote.
- Incrementing phases (build power by holding up longer), independent revert triggers, per-phase transitions.
- Requires alt fonts and `FETT263_SPECIAL_ABILITIES`. Styles carry setup instructions in their comments.
- Demo: He-Man transformation.

## What this means for the gift
The selling point isn't one feature. It's that the saber is an open platform: behavior is code (prop file), visuals are code (styles), sounds can be driven by code (alt fonts), and the community keeps shipping features for free on the same 2018-era hardware.
