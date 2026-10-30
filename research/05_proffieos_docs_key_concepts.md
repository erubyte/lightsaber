# Key concepts from POD (ProffieOS Documentation)

Source: https://pod.hubbe.net/ (GitHub: profezzorn/ProffieOSDocs, cloned at commit d1c3a79, 2026-10-28; local copy `sources/ProffieOSDocs/`). About 73k words, 230+ pages. A single-page version for searching or printing: https://pod.hubbe.net/POD.html

## Mental model
- **Proffieboard** = hardware. **ProffieOS** = firmware. **Prop file** = the app logic (buttons, gestures, menus). **Config file** = his saber's definition (hardware, presets, styles). **Sound font** = folder of WAVs + `config.ini` + `smoothsw.ini`. **Blade style** = code describing every pixel over time. **Preset** = font + track + one style per blade + name.
- Three independent version numbers: ProffieOS (e.g. 8.10), Proffieboard (1.5/2.2/3.9), Arduino-Proffieboard plugin (e.g. 4.6). They mix and match; a V3 board doesn't need plugin V3 or OS 3. Minor version bumps are bug fixes only ("after 2.9 comes 2.10"). (explainers/version-numbers.md)

## Three ways to change things, from least to most power
1. **On the saber**: Edit Mode / OS 8 menus (spoken, navigated by turning the hilt). Changes go to INI files on the SD card.
2. **ProffieOS Workbench** (https://profezzorn.github.io/lightsaber-web-bluetooth/app.html): a web app over **WebUSB** (Chrome/Edge) or Web Bluetooth (needs a BT module). Volume slider, battery voltage, select presets, play tracks, trigger effects, and an editing view to reorder/add/delete presets and change font, track, style, variation. Saves immediately. Requires firmware built with USB Type including WebUSB, and the SD card not mounted at the same time.
3. **Recompile and flash**: edit the config, build with Arduino (or Fett263 Config Helper + Fredrik's Web Programmer), upload over USB. Needed for new style code, prop changes, defines.

## Before touching anything: back up
- **Firmware backup**: https://profezzorn.github.io/webdfu/dfu-util/ . Put the board in bootloader mode (serial command `RebootDFU`, or hold BOOT, tap RESET, release BOOT), click Connect ("STM32 BOOTLOADER"), click **Read** to save a `.bin`. Restore with **Write**. The .bin is not a config; you can't recover the config from it. (howto/how-to-back-up-a-proffieboard.md)
- **SD card backup**: copy the whole card, including `*.ini` and `*.tmp` save files.
- **Find the factory config**: vendors often leave the config `.h` (or a whole ProffieOS zip) on the SD card. Look in the root; inside a zip, open `ProffieOS.ino` and find the uncommented `#define CONFIG_FILE` line. (config/get-from-sd-card.md). This is the single most important file he'll want. If the vendor didn't include it, ask the vendor (DamienSaber) for it; under GPLv3 there's a reasonable case for asking, and many vendors share configs on request.
- **Factory reset of edits**: delete `presets.ini` and `presets.tmp` from the SD card, then reboot. (tools/workbench.md)

## Save files (explainers/save-file-format.md)
- Up to OS 6: plain INI. Problem: creating/deleting files during a power cut can corrupt the FAT directory.
- OS 7+: each save file is preallocated and **never resized or recreated**; two copies (`.ini` and `.tmp`) are written alternately (A/B), each with a header: magic `0xFF1E5AFE`, checksum, iteration counter, length, plus an install-time string. The newest valid copy wins; plain-INI fallback for compatibility. Save files with a different install time than the running firmware are ignored unless `KEEP_SAVEFILES_WHEN_PROGRAMMING`.
- To hand-edit: delete the first 512-byte block, then it's a plain INI.
- `KEEP_SAVEFILES_WHEN_PROGRAMMING` caveats: config changes to volume, clash threshold, fonts, colors won't take effect over existing INI values; style numbers are positional (`style=builtin 14 1`), so **never remove presets from the config** or the board can lock up.

## USB explained (explainers/understanding-usb.md)
- USB descriptors depend on the uploaded program. Usual choice: **Serial + WebUSB + Mass Storage** (three endpoints: serial port, WebUSB, drive).
- If the firmware is broken, the board may not enumerate. Fallback is the STM32's **ROM bootloader** (can't be overwritten), which shows up as "STM32 BOOTLOADER", a DFU device. Windows needs Zadig for it. Arduino uploads by sending a magic sequence to the serial port that reboots into DFU, then flashing.
- This means **he can't brick it** in the usual sense: the ROM DFU bootloader always works if he can reach the BOOT/RESET buttons (core must be opened) or the serial port still runs.

## Clash detection history (explainers/history-of-clash.md)
A good engineering story for him:
1. Original: `|a_now − a_last| > CLASH_THRESHOLD_G`. Sample-rate dependent.
2. Then against a slow average. Then OS 3 added the **Fusor** (accel + gyro → down vector): `|a − down| > threshold`.
3. Range was ±4 g and effective rate about 800 Hz; people tuned to about 3.9 by accident of clipping. Fredrik added interrupt-driven I²C to get a reliable **1600 Hz** and raised the range to **±16 g**. Result: more false clashes, because at high sample rates **the speaker's sound vibrations** show up in the accelerometer.
4. Fixes: `ACCEL_MEASUREMENTS_PER_SECOND 800` (box filter), `AUDIO_CLASH_SUPPRESSION_LEVEL` (raise the threshold with current volume), `PROFFIEOS_ACCELEROMETER_RANGE`, `PROFFIEOS_MOTION_FREQUENCY`.
5. Fett263 used the **gyro** to detect clashes in blade styles. Fredrik found gyro spikes on impact and combined both: `|a − down|/2 + |Δgyro|/2 > threshold`. There's a define to revert to the old formula.
6. `scripts/clash_recorder.h` records IMU traces for tuning.

## Sound fonts (sound/sound-font-configuration.md, alt_sounds.md, sub-sub-sounds.md, faster-fonts.md)
- Format: **44.1 kHz, 16-bit, mono PCM WAV** recommended (11/22/44 kHz mono or stereo supported; `.raw`/`.usl` 44 kHz mono).
- Naming: `font/clash001.wav`, or `font/clsh/01.wav`. Numbers must be consistent with no gaps; random pick among numbered files. Loops (hum) re-pick randomly each loop.
- **Monophonic (Plecter-style) vs polyphonic (NEC/Naigon-style)** is decided **per sound by filename**: e.g. `clash` (mono) vs `clsh` (poly), `blaster` vs `blst`, `swing` vs `swng`, `lockup` vs `lock`, `poweron` vs `out`, `poweroff` vs `in`. Mono effects interrupt and rejoin the hum; poly ones overlay it.
- **Font search paths**: `"font1;common"` searches several folders (under 127 chars total). Lets fonts share `common` voice prompts or quote packs.
- **Alt fonts (OS 7)**: `alt000/`, `alt001/`... each with the identical file set; styles (`SyncAltToVarianceL/F`, `AltF`) or props choose which is live. Light/dark versions of a font, frozen blade, etc.
- **Sub-sub sounds (OS 7)**: `swng/01/000.wav...`, so strength-selected sounds still have random variety.
- **FAT32 performance**: 16 directory entries per block; put multi-file effects in subfolders, singletons (hum.wav) in the root. Reduces audio underflows (pops, gaps).
- OS 8 sounds: `chhum` (alt change with no gap), `fastout`, `quote`, `mclick` (menu click), `idle`.
- Monophonic name list includes `bgndrag`, `bgnlock`, `bgnmelt`, `bgnlb`, `boot`, `ccbegin/ccchange/ccend`, `drag/enddrag`, `endlb`, `font`, `force`, `hum`, `in/out`, `preon`, `pstoff`, `quote`, `stab`, `swingl/swingh`...

## Style arguments (config/styles/style_arguments.md)
- `RgbArg<BASE_COLOR_ARG, Red>` and `IntArg<IGNITION_TIME_ARG, 300>` turn style constants into runtime-editable slots. Copies of the same style with different arguments **cost no extra flash**.
- OS 7: default args in the config, e.g. `StylePtr<...>("65535,0,0")` (Rgb16).
- Standard slots: 1 BASE_COLOR, 2 ALT_COLOR, 3 STYLE_OPTION, 4 IGNITION_OPTION, 5 IGNITION_TIME, 6 IGNITION_DELAY, 7 IGNITION_COLOR, 8 IGNITION_POWER_UP, 9 BLAST_COLOR, 10 CLASH_COLOR, 11 LOCKUP_COLOR, 12 LOCKUP_POSITION, then drag, emitter, off options, retraction, preon, swing options...
- Trick: configure with Edit Mode, then read the arg strings out of `presets.ini` and paste them into the config.

## Menus (OS 8, howto/menus.md)
- `#define MENU_SPEC_TEMPLATE DefaultMenuSpec` (or `FETT263_MENU_SPEC` with the Fett263 prop).
- Needs a **ProffieOS V2 voicepack** `common` folder on the SD card and in each preset's search path (fredrik.hubbe.net/lightsaber/sound/; BC custom voicepacks on the Crucible).
- Top menu → Edit Presets (select font/track, edit blade style per blade, move, select/insert, delete) and Settings (volume, SD access, blade length, clash threshold, blade dimming).
- Navigation can also be driven from the serial monitor: `left`, `right`, `select`, `cancel`.

## Serial monitor (tools/serial-monitor-commands.md and additional commands)
Arduino Serial Monitor or any terminal at the board's CDC port. Basics: `version`, `reset`, `RebootDFU`, `get_volume`, `set_volume`, `n`, `p`, `on`, `off`, `clash`, `force`, `blast`, `stab`, `lock`, `lblock`, `drag`, `melt`, `ccmode`, `cd`, `pwd`, `dir`, `play`, `play_track`, `stop_track`, `list_presets`, `battery_voltage`, `sdtest` (normal cards give 10–11 parallel streams; under 9, replace the card), `scanid`, `top`, `monitor`. OS 8: `sd`, `quote`, `swing`, `slash`, `spin`, `get_variation`, `|`.

## Writing a prop (howto/making-your-own-prop-file.md)
- Props are a big `switch` over `EVENTID(BUTTON_X, EVENT_Y, MODE_Z)` (e.g. `EVENT_CLICK_SHORT`, `EVENT_CLICK_LONG`, `EVENT_DOUBLE_CLICK`, `EVENT_HELD`, `EVENT_TWIST`, `EVENT_SWING`, `EVENT_STAB`, `EVENT_CLASH`; `MODE_ON`/`MODE_OFF`) returning true when handled. Actions call `On()`, `Off()`, `SaberBase::DoForce()`, etc.
- Timings: double click within 500 ms; long click over 500 ms (`BUTTON_LONG_CLICK_TIMEOUT` in OS 8).
- Copy a prop, include it in `CONFIG_PROP`. OS ships: saber.h (default), saber_fett263_buttons.h, saber_sa22c_buttons.h, saber_shtok_buttons.h, saber_BC_buttons.h, saber_caiwyn_buttons.h, saber_sabersense_buttons.h, blaster.h, blaster_BC_buttons.h, detonator.h, hev.h (Half-Life HEV suit), micom.h, audiofx.h, dual_prop.h.

## SD cards (hardware/sd-cards.md)
Proffieboard V2.2 reads the card in SPI mode, so regular benchmarks don't predict performance; `sdtest` is the real test.
