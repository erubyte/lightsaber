# Saber basics from scratch: the market, blades, boards

What a new owner should know before anything about Proffie. Sources are listed per section. Vendor blogs are marketing; I note where they're wrong.

## 1. The three layers of any saber
1. **Hilt**: the metal handle (aluminum, sometimes brass/copper parts). Screen-accurate replica vs "inspired" design. Ours: Quinlan Vos design, 31 cm, exposed crystal chamber.
2. **Core / electronics**: sound board + battery + speaker + LEDs. Either **wired into a chassis** (custom installs) or a **removable "core"** that slides into the hilt (factory sabers: LGT/Nexus "Eco pogo core" system, DamienSaber, Padawan Outpost). Ours: removable pogo core, NexusSabers LGT A.294-1, Proffie V2.2.
3. **Blade**: polycarbonate tube. Either hollow (lit from the hilt) or containing LED strips.

## 2. Blade technologies
Sources: ccsabers.com RGB vs Neopixel (2026-09), wegeektogether, thesaberfactory, r/lightsabers threads, Proffie V2 manual.

| Type | How it works | Look | Durability | Notes |
|---|---|---|---|---|
| **Static / single color** | One LED in the hilt | One color | Best | Cheapest |
| **Baselit RGB (in-hilt, "Tri-Cree", "RGB", "XRGB")** | 3–4 high-power LED dies in the hilt shine into a hollow blade with diffusion film | Whole blade one color at once, color-change, flash on clash = whole blade brightens; "ignition" is a fade or flicker, not a scroll | Best for dueling, cheap blade replacement | Brighter at the base. XRGB is LGT's marketing name for an improved baselit; also used loosely |
| **Neopixel ("pixel", "Neo", "SN-Pixel", "Xenopixel" blade)** | Two (sometimes three) strips of addressable RGB LEDs back to back inside the blade, connected by gold rings/pogo pins to the hilt | Scrolling ignition and retraction, local clash flashes, blast marks, fire, unstable, gradients, animations. Brighter and more even | Good with heavy-grade blades; strips can be damaged by hard hits; blades cost more | "NeoPixel" is Adafruit's brand name for WS2812-family LEDs. Our blade is SK6812/WS2812-class |
| **Segmented / "string" blades** | Rows of discrete LEDs on a strip switched in segments | Scroll in 6 steps | Old tech | Proffie supports it (StringBladePtr) |
| **"Pixel" in-hilt / "PixelStick"** | Small Neopixel matrices in the emitter or ultra-thin LED sticks | Varies | | Niche |

**Blade sizes and grades**
- Outer diameter **1 in (25.4 mm)** or **7/8 in (22.2 mm)**. Neopixel blades are almost always 1 in, because a 7/8 in neopixel tube is thin-walled (no room for strips with a thick wall). A 1 in thick-wall blade has the same inner diameter as a regular 7/8 in blade.
- Wall: **thin wall / mid grade ~1.5 mm** vs **thick wall / heavy grade ~3 mm**. Heavy grade survives impacts far better. Ours is 1 in OD, 3 mm wall = heavy grade.
- Weight: heavy-grade neopixel blades are heavy (up to ~300 g for 1 in). A thin-wall neopixel is about as heavy as a heavy-grade baselit blade.
- Lengths: 24–36 in common. Ours is 32 in (81 cm).
- Tips: bullet/rounded, pointed (ours), flat. Inside: foam sleeve and diffusion film; the tip has a reflector.
- Connection: **pogo pins in the emitter** press on **gold rings or a PCB** at the blade base. Standards differ (NPXL by ShtokCustomWorx, LGT/Nexus pogo, KR). Ours: gold rings, any rotation.
- Dueling advice that recurs everywhere: heavy-grade blades, polycarbonate vs polycarbonate only, no hitting hard objects, avoid tip stabs, don't swing a midgrade blade into a heavy grade.

## 3. Sound board families (2026)
Sources: xpecialify buyer's guide, isabers technical comparison (2026-08), solosabers "The Eternal Debate" (2023), plecterlabs.com, sabertec.net, thesaberarmory.com, crucible.hubbe.net.

| Board | Maker | Open? | Config | Notes |
|---|---|---|---|---|
| **Proffieboard** (V1.5, **V2.2**, V3.9) | Fredrik Hübinette (Profezzorn), open hardware, made by multiple fabricators (TheSaberArmory/KR, Electronics123, Artekit, ShtokCustomWorx, Korbanth...) | **Fully open source** (GPLv3 software, open hardware) | Config file compiled with Arduino or web tools; on-saber Edit Mode; ProffieOS Workbench (WebUSB) | 4 data pads, 6 MOSFETs, 3 W amp, 1.66 kHz IMU. Smallest footprint (0.70 in wide). The "most customizable" board. |
| **CFX** (Crystal Focus X / Crystal Focus Saber Core v10) | Erv Plecter, Plecter Labs (Belgium) | Closed | Text config files + on-saber menu; RICE software over USB; crystalfocus.net (Tristan Cam) extends it | Premium, deep, the long-time Proffie rival. Wider (0.82 in). |
| **Golden Harvest (GHv3, GHv4)** | Sabertec (with Saberforge historically) | Closed | SD-card text + on-saber menu; **GHv4 has built-in Wi-Fi and Bluetooth**, apps ForceSync (BT) and GH Commander (web) | GHv4 launched late 2024, dual-core, 4 W amp, 10 LED channels, OLED. Strong dueling tuning. |
| **Verso** | KR Sabers (Khal) | Closed | Simple | Entry-level board for DIY installers. |
| **Asteria** (1.5, 2.5) | Ultimate Works / The Pach Store | Closed | | Smaller market. |
| **Xenopixel (V2, V3 "Xeno3")** | LGT (the factory group behind Nexus Sabers) | Closed, specs unpublished | Bluetooth app (XenoConfigurator), SD files | Mass-market neopixel board in most factory sabers. 34 fonts preinstalled, 11 blade modes, 7 ignition styles, fixed. One button only. |
| **SN-Pixel V4 / SNV4 Pro** | TXQ Sabers | Closed | App | Xenopixel rival in budget factory sabers. Two-button support, character voices. |
| **XRGB** | LGT | Closed | | LGT's baselit line. |
| "Jiahe" V3, D3, Sabneo V8 and others | Chinese factories | Closed | | Budget. |

### What vendors get wrong about Proffie (useful for the manual)
- "Proffie requires recompiling to change a font or color." Not true when Edit Mode and the INI-based style arguments are enabled, which is the norm on preconfigured sabers. You can add a font folder to the SD card and pick it in Edit Mode, change colors and timings, copy presets, all on the saber. Recompiling is only for structural changes (new style code, new prop, new defines).
- "Proffie has no app." True for phones, but **ProffieOS Workbench** runs in a desktop browser over WebUSB, and Fredrik's **Web Programmer** flashes firmware from the browser. Bluetooth is an add-on module.
- "Proffie is just a more complex Xenopixel." The LEDs, battery and speaker are the same class; the difference is the platform: open hardware, open firmware, a style language, a prop language, debugging hooks.
- "Proffie v3.0" doesn't exist. Versions are V1.5, V2.2, V3.9 (the number reflects design iterations).

## 4. Proffieboard V2.2 vs V3.9
Sources: isabers (2026-08), thesaberarmory product page, Sabertrio post, Crucible thread 5527, Artekit V2.2 guide.
- **V2.2**: STM32L433CC, 80 MHz Cortex-M4F, 256 KB flash, 64 KB RAM, 48-pin, SD over SPI. **Discontinued** (Artekit: "discontinued in favor of the new Proffieboard V3.9"), still fully supported by ProffieOS 8.
- **V3.9**: STM32L452RE, same speed, **512 KB flash, 160 KB RAM**, 64-pin, SD over **SDIO** (faster, more simultaneous audio streams), more pads (Free 1–3, extra UART/I²C/SPI), **on-board charging** over the board's USB.
- Same footprint. For a single-blade saber V2.2 is fine; the main V2.2 limit is **flash size** (big configs with many complex styles hit 256 KB). Memory-saving defines exist for this reason (`DISABLE_BASIC_PARSER_STYLES`, `DISABLE_DIAGNOSTIC_COMMANDS`, `DISABLE_TALKIE`).

## 5. Price positioning (2026)
- Baselit RGB sabers: about $80–$200. Xenopixel/SN-Pixel neopixel: about $180–$350. Proffie neopixel factory sabers: typically **$70–$150 more** than the same hilt with Xenopixel (isabers). Custom installs from known installers cost much more.
- The premium "buys the platform, not better LEDs" (isabers' framing is accurate).

## 6. Factory saber ecosystem (relevant to ours)
- **LGT / Nexus Sabers**: Chinese factory group making Xenopixel, XRGB and Proffie cores. Their "Eco pogo core" system lets cores swap between compatible hilts. Proffie LGT cores reportedly ship with 32 GB SD, about 28 fonts, 12 default colors (allsabers.com).
- **DamienSaber**: brand that sells hilts with baselit, Xenopixel 3 and Proffie cores. Mixed reputation on Reddit for pricing (2026-07 thread "Is Damiensaber High?"), positive reviews from sandcrawlernews, myshinytoyrobots. Our saber: DamienSaber NO184-PF, product code 184-PF.
- Other names he'll see: 89sabers, Padawan Outpost, Vader's Vault, Saberforge, Sabertrio, KR Sabers/TheSaberArmory, CCSabers, Neosabers, Ultrasabers, Saber Bay.

## 7. Communities (where the knowledge lives)
- **The Crucible** (crucible.hubbe.net): Fredrik's Discourse forum, the official ProffieOS support forum. Fett263 Corner is a subforum.
- **POD** (pod.hubbe.net): ProffieOS Documentation, moved from the GitHub wiki in Dec 2022.
- **Fett263 site** (fett263.com): prop docs, Style Library, Config Helper, OS7 feature pages.
- Facebook: "Open Source Sabers" group (opensourcesabers), "Custom Lightsaber Owners".
- Reddit r/lightsabers (buyer's guide wiki; blocks automated readers).
- Older: The Rebel Armory (TRA), FX-Sabers forum (Profezzorn's Lab threads).

## 8. Gift context: Quinlan Vos
- Kiffar Jedi Master, maverick, from Kiffu; originally a Dark Horse Comics character (amnesiac Jedi struggling with the dark side), brought into canon in The Clone Wars ("Hunt for Ziro") and the novel **Dark Disciple** (Christie Golden, 2015, adapted from unproduced Clone Wars scripts) with Asajj Ventress. Psychometry (reads memories by touching objects). Green blade.
- CCSabers (2026-10): his hilt has an exposed crystal chamber design. Our hilt matches that (lit crystal chamber).
- A 2025 Black Series figure exists (official images Oct 2025).
