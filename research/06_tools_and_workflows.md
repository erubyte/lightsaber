# Tools for working on a Proffie saber (2026)

## Official, by Fredrik (profezzorn)
| Tool | URL | What it does |
|---|---|---|
| ProffieOS download | https://fredrik.hubbe.net/lightsaber/proffieos.html , https://github.com/profezzorn/ProffieOS/releases | Firmware source. Current 8.10 (2026-02-22). |
| Arduino-Proffieboard plugin | Arduino Boards Manager URL from the ProffieOS page; GitHub profezzorn/arduino-proffieboard | Board support package (STM32L4 core). Plugin 4.6 beta in late 2025 with an updated compiler. |
| **ProffieOS Workbench** | https://profezzorn.github.io/lightsaber-web-bluetooth/app.html | Web app over **WebUSB** or Web Bluetooth. Volume, battery voltage, preset select, track play, effect triggers; editing view for presets (font, track, style, variation, reorder, add, delete). Chrome/Edge on desktop; Android Chrome works with USB OTG. Firmware must be built with WebUSB in USB Type. |
| **Web DFU programmer / backup** | https://profezzorn.github.io/webdfu/dfu-util/ | Read (back up) or write the firmware `.bin` through the STM32 bootloader, from the browser. |
| **Web Programmer** | linked from Fett263 Config Helper ("Program Board") | Compiles and flashes a pasted config in the cloud/browser, no Arduino install. |
| **ProffieOS Style Editor** | https://fredrik.hubbe.net/ProffieOS-StyleEditor/style_editor.html (source: github.com/profezzorn/ProffieOS-StyleEditor, `npm install` + `npx vite` to run locally) | Live blade simulator: paste or build a style, see the blade animate, trigger clash/blast/lockup, edit arguments. Also the reference for every template's arguments. |
| Configurator / generator | https://fredrik.hubbe.net/lightsaber/v5/ (V2), /v6/ (V3) | Interactive wiring diagram + config generator for builders. |
| Voicepacks | https://fredrik.hubbe.net/lightsaber/sound/ | The `common` folder with spoken menu prompts (needed for Edit Mode / menus). |

## Fett263
| Tool | URL | What it does |
|---|---|---|
| **Style Library** (OS 7/8) | https://www.fett263.com/fett263-proffieOS7-style-library.html | Huge builder: pick base style, ignition, retraction, preon, clash, blast, lockup, interactive effects; produces style code with Edit Mode arguments; live preview and font preview tools. Free public access; Patreon Early Access for newest features. |
| **Config Helper** | https://www.fett263.com/fett263-os7-config-helper.html | Walks through every define and prop option, builds the presets, outputs a config, and produces **custom documentation** (controls, style options, supported sound files) for that config. Hands off to the Web Programmer. |
| Prop docs | https://www.fett263.com/proffieOS7-fett263-prop-file.html | All controls and defines. |
| Updating guide | https://www.fett263.com/updating-your-proffieboard.html | Simplified update steps. |
| Getting started | https://www.fett263.com/proffieboard-getting-started.html | Beginner path. |

## Community desktop apps
| Tool | Who | Platforms | Notes |
|---|---|---|---|
| **ProffieConfig** | Ryan Ogurek (ryryog25), GPL-3.0, github.com/ryancog/ProffieConfig, site proffieconfig.kafrenetrading.com | macOS, Windows | "All-In-One Proffieboard Management Utility". GUI config generation, import an existing config, compile and upload, serial monitor, driver install, sanity checks, without Arduino IDE or Zadig. v1.7.9 announced 2025; V2 restructuring; active (commit 2026-09-04). |
| **JMT Studio** | "jedimaster" on the Crucible | Windows (signed), macOS Apple Silicon and Intel (signed, notarized), Linux .deb/AppImage | v1.7.1 (2026-06-10). IDE-style config editor with syntax highlighting and bracket diagnostics for style expressions, visual preset editor, visual `RgbArg` color editing, built-in serial monitor, compile and flash, DFU recovery guidance (including Apple Silicon dfu-suffix patching), **multiple ProffieOS versions side by side per saber** with rollback. Source on GitHub. |

For a CS/ECE person: plain Arduino IDE + git is still the most transparent path; JMT Studio is the best fit if he wants an IDE and version management; ProffieConfig if he prefers a GUI.

## Hardware he may want
- **Data-capable micro-USB cable** (the board's port is micro-USB on V2.2; charge-only cables are the #1 failure).
- **microSD card reader** (much faster than mass storage over the board).
- For debugging: **ST-LINK V2/V3** probe (or any SWD probe) on the SWDIO/SWCLK pads, plus OpenOCD/GDB or STM32CubeIDE. Requires opening the core and soldering or pogo-clipping to pads. Advanced.
- Optional add-ons: FSC-BT630 BLE module (Workbench over Bluetooth), SSD1306 OLED, extra accent Neopixels.

## Recommended first-session workflow (for the manual's section 3)
1. Charge fully. Open the core only as far as needed to reach the SD card and micro-USB.
2. **Copy the whole SD card** to the computer. Look for the factory config `.h` or a ProffieOS zip.
3. Connect micro-USB with a data cable. Open a serial terminal (Arduino Serial Monitor, `screen`, or JMT Studio) and run `version`, `list_presets`, `battery_voltage`, `sdtest`.
4. **Back up the firmware** with the Web DFU page (`RebootDFU`, then Read).
5. Try ProffieOS Workbench (works only if the factory build enabled WebUSB).
6. Play in the Style Editor with the factory styles from the config.
7. Only then: install a toolchain, build the factory config unchanged, flash, confirm it behaves identically. Then start changing things.
