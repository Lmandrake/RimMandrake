# Memory footprint audit — mechanical legwork (2026-09-07)

Feeds `infrastructure/state/items/RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1.md`. This is
RAW MEASUREMENT ONLY — no synthesis, no recommendations. A deeper Opus-tier pass
happens on top of this. Read-only task; nothing else in the repo was touched.

## 1. Crash evidence (read, not grep-listed)

**`crash_report_20260905_225503_DELIBERATE_RESTART_not_a_crash.md`** — filename is
accurate: this is a deliberate restart at 2026-09-06T05:54:55Z for
`GRAVSHIP_LANDING_CRUSH_1` verification, not a crash. RSS steady at ~7.32GB for the
40 samples before the restart. NOT evidence of a memory crash.

**`crash_report_20260906_055852.md`** — a real, unplanned process disappearance,
detected 2026-09-06T12:58:52Z. RSS in the last 40 samples: 8.70GB, declining
smoothly (not spiking) to 8.06GB right up to the last sample before the process
vanished. No sudden jump, no OOM-shaped spike at time of death.

**No `OutOfMemoryException`, no .NET-catchable OOM text, no "low memory"/GC-pressure
warning string anywhere** in either crash report's Player.log excerpt, nor in
`Player_log_ninefold_crash_598mod_2026-09-07.log`, `Player_log_quicktest_crash_2026-09-05.log`,
or `Player_log_stale_ninefold_session_2026-09-05.log` (all three crash/quicktest-named
Player_logs were checked for `outofmemory|out of memory|low memory|Allocat.*fail` —
zero hits). All three of those Player_logs cut off mid-stream at the exact same
in-game moment (mid-research-completion burst, "ComplexClothing" research line) with
no trailing exception text — consistent with an abrupt native-level crash (no managed
exception was thrown/caught before death), not a graceful OOM.

**Windows Event Viewer caveat — important**: both crash reports' embedded
Application-log excerpts show the IDENTICAL three APPCRASH/Application-Error event
pairs (`RimWorldWin64.exe` vs `ntdll.dll`, exception code `0xc0000005`
STATUS_ACCESS_VIOLATION, same fault bucket `1625590480408144550`, same fault offset
`0x70f32`), timestamped 2026-09-05 15:18 / 20:02 / 20:20 — i.e. those events PREDATE
both report-detection timestamps (05:55:03 and 12:58:52 the next day). The capture
script is pulling stale/cached WER history, not a fresh event tied to each specific
death. So: there IS a recurring `ntdll.dll` access-violation signature in the
system's crash history, but it cannot be confidently attributed to either of these
two specific measured death moments from this data alone — flag as suggestive, not
proven, for the synthesis pass.

**Peak RSS measured across the whole watched session** (`rimworld_mem_watch_2026-09-05.log`,
5,713 samples, PID 24480 then 27680 across a restart):
- **max: 21,152,072 KB ≈ 20.17 GB**, at 2026-09-06T06:10:26Z — well after the
  deliberate restart (05:55) and ~7 hours before the real crash (12:58).
- min: 1,129,764 KB ≈ 1.08 GB (near a fresh launch, before mods finish loading).
- **The real crash did NOT happen at the peak.** RSS climbed to 21GB, came back down
  into the 17-20GB band for a while, and the eventual death happened much later at a
  comparatively modest 8.7GB → 8.06GB, declining. This argues against "hit a hard
  ceiling and died" as the crash mechanism — the access-violation signature (if it's
  really the same event) is more consistent with heap corruption / use-after-free
  than a simple allocation-exhaustion OOM. Confirms the owner's "18GB+" figure is a
  real measured peak (20.17GB), not an exaggeration — but peak size and crash-time
  size are two different numbers and should not be conflated in the synthesis.
- `free -h` inside both crash reports is the **WSL/Linux side** (35Gi total, mostly
  free) — this does NOT measure the Windows host's physical RAM or commit charge at
  the time of the Windows-side crash. No Windows-side system memory pressure reading
  exists in the captured data. UNKNOWN whether the Windows host was itself under
  memory/commit pressure at either death.

## 2. Real on-disk size census (proxy signal, NOT memory usage — see caveat below)

599 active mods per `ModsConfig.xml` (re-read fresh 2026-09-07, confirmed 599 — an
earlier intermediate scratch copy of the active list was found silently truncated to
11 lines mid-task and was regenerated and re-verified at 599 before producing this
table). Of these: 543 resolved to a Steam Workshop folder (mapped packageId →
Workshop folder via each folder's top-level `<packageId>` in `About/About.xml`,
NOT via any `<packageId>` inside a nested `<modDependencies>` block — an early
attempt using a naive regex mis-matched on dependency packageIds and produced 56
false "missing" entries before this was caught and fixed with proper XML parsing).
The other 56 are: 5 base-game/DLC (Core/Royalty/Ideology/Biotech/Anomaly/Odyssey —
1 is `ludeon.rimworld.loadtracer`-style dev shim, rest are official) and 51 of our
own custom mods (`mandrake.*`), which live in the game's local `Mods/` folder, not
Steam Workshop.

**Measured with `du -sk` per folder** (real disk usage, one subprocess call per
folder, 543 workshop calls + 78 local-Mods calls, all succeeded, zero errors):

- Sum of all 543 measured active Workshop mod folders: **5.98 GB**
- Our own deployed custom mods (`.../RimWorld/Mods/`, 78 folders, actual GAME-LOADED
  copy, not the repo source): **245 MB total**, largest single one is
  `Armoury` (`mandrake.rsw.armoury`, "Jawa Armoury Rebalance") at 84 MB — big enough
  to land at rank 16 of the top 30 below.
  (For comparison only, NOT part of the ranking: the *repo* `src/` copies are much
  bigger than what's deployed — `src/RimStarWars` 227 MB, `src/RimMandrake` 222 MB,
  `src/RimUtinni` 169 MB — because the repo carries dev-only files, docs, and
  pre-deploy art that never reaches the game's `Mods/` folder. Never cite the repo
  size as the game's footprint.)
- Base game install (`.../RimWorld`, Core + all 6 official DLC under `Data/`):
  **1.2 GB**
- **Total on-disk content across everything the game actually loads:
  ~7.4 GB** (5.98 + 0.245 + 1.2), against a **measured peak RSS of 20.17 GB**. The
  peak in-memory footprint is roughly **2.7x the total compressed on-disk asset
  weight of every active mod plus the base game combined.** This is the single most
  important number for the synthesis pass: it means the memory bloat is NOT simply
  "loose files loaded 1:1 into RAM" — Unity/RimWorld decompress textures into
  uncompressed GPU-ready buffers at load (a compressed PNG on disk can expand several-
  fold in VRAM/RAM), and/or a large share of the 20GB is engine/game-state overhead
  (def graphs, pawn/pathing caches, GC heap fragmentation, save-game state) that has
  nothing to do with any single mod's asset folder. Disk size is a real, measured
  number — it is not memory usage, and this gap is exactly why.

### TOP 30 ACTIVE MODS BY ON-DISK FOLDER SIZE

| # | Size | Mod name | packageId |
|---|------|----------|-----------|
| 1 | 328 MB | Biomes! Caverns | biomesteam.biomescaverns |
| 2 | 288 MB | RimThemes | arandomkiwi.rimthemes |
| 3 | 254 MB | GRiNDTerra Biomes | grimterra.biomesmod |
| 4 | 228 MB | Minerals Rock | zacharyfoster.mineralsrock |
| 5 | 186 MB | RW - Planet Atmosphere | rwnodetree.rwplanetatmosphere |
| 6 | 142 MB | [RH2] Uncle Boris' - Used Furniture | cp.uncle.boris.used.furniture |
| 7 | 142 MB | Vanilla Backgrounds Expanded | vanillaexpanded.backgrounds |
| 8 | 141 MB | WallStuff | arcjc007.wallstuff |
| 9 | 136 MB | Minerals Framework | zacharyfoster.mineralsframework |
| 10 | 121 MB | Outer Rim - Core | neronix17.outerrim.core |
| 11 | 120 MB | ReGrowth 2 | regrowth.botr.core |
| 12 | 119 MB | Star Wars KotOR Resources and Materials | guy762.mm.kotorcore |
| 13 | 109 MB | Alpha Biomes | sarg.alphabiomes |
| 14 | 99 MB | GRiNDTerra Terrain Retexture | grimterra.terrainretexturemod |
| 15 | 88 MB | Outland - Genetics | neronix17.outland.genetics |
| 16 | 84 MB | Jawa Armoury Rebalance (OUR mod) | mandrake.rsw.armoury |
| 17 | 80 MB | Jurassic Rimworld - Dinosaurs Only (Continued) | mlie.jurassicrimworlddinosaursonly |
| 18 | 80 MB | Tech Level Enforcement | summersausages2ttv.techlevelenforcement |
| 19 | 76 MB | Ancient urban ruins | xmb.ancienturbanruins.mo |
| 20 | 72 MB | Gravship Exporter | arcjc007.gravshipexporter |
| 21 | 69 MB | Face Addon Framework | eoralmilk.faceaddonframework |
| 22 | 68 MB | Outer Rim - Droid Depot | neronix17.outerrim.droiddepot |
| 23 | 68 MB | Alpha Animals Retextured | ks.aaretextured |
| 24 | 68 MB | Biomes! Polluted Lands | biomesteam.biomespollutedlands |
| 25 | 59 MB | GravTide | gravtide.mod |
| 26 | 58 MB | Vanilla Landmarks Expanded | vanillaexpanded.vexploratione |
| 27 | 57 MB | Outer Rim - Galactic Empire | neronix17.outerrim.galacticempire |
| 28 | 56 MB | Worldbuilder | ferny.worldbuilder |
| 29 | 56 MB | Melee Animation | co.uk.epicguru.meleeanimation |
| 30 | 55 MB | Laser Cannon | arcjc007.lasercannon |

## 3. Texture format check, top 5 by disk size

1. **Biomes! Caverns (328 MB)** — no `AssetBundles/` folder anywhere. `Textures/` has
   1,225 files, 1,194 of them `.png` (rest are per-thing `readme.txt`/notes sitting
   next to the art). **All loose PNG — fully re-encodable/compressible.**

2. **RimThemes (288 MB)** — no `Textures/` folder at all at top level. The bulk
   (260 MB of the 288 MB) is in `Themes/`, one subfolder per UI theme (Scyther,
   Singularity, Thrumbo, USFM, Cyberpunk, Muffalo, etc.), and it is NOT primarily
   texture content: 286 `.png`, but also 226 `.wav`, 86 `.jpg`, 26 `.webm` (video),
   18 `.ogg`, 4 `.ogv`. **Mixed loose assets (images + audio + video), no
   AssetBundle.** Re-encoding textures alone would only address part of this mod's
   footprint; whether RimWorld loads every theme's assets into memory regardless of
   which one is active in Mod Settings is UNMEASURED here (needs a profiler, not a
   disk read).

3. **GRiNDTerra Biomes (254 MB total, 241 MB of it is `1.6/Textures/`)** — 950
   files, all 950 are `.png`. No `AssetBundles/`. **All loose PNG.**

4. **Minerals Rock (228 MB total, 148 MB is `1.6/Textures/`)** — 829 files, 629
   `.png` (200 non-PNG, likely material/support files, not individually itemized).
   No `AssetBundles/`. **Loose PNG.** Notable disk-only (NOT memory-relevant) waste:
   this mod ships a **60 MB `.git/` folder** and an `.aider.tags.cache` file bundled
   straight into the Workshop upload — dev artifacts the game never reads, inflating
   the on-disk number without inflating RAM at all. A good example of why disk size
   over-reports what actually loads.

5. **RW - Planet Atmosphere (186 MB)** — has a genuine `AssetBundles/` folder, but
   it's tiny (176 KB: Linux/macOS/Windows shader bundles only). The real texture
   weight is small and loose: only 4 files under `Textures/`, one of which is a
   **single uncompressed 45 MB 8K PNG** (`8k_earth_clouds.png`) — a very concrete,
   individually re-encodable/downscalable offender. The other 141 MB of this mod's
   186 MB is a `src/` folder — a full bundled Unity dev project (`.idea`, `.vscode`,
   `ProjectSettings`, `UserSettings`, `.cs`/`.shader`/`.unity`/`.asset` files) that
   RimWorld's mod loader has no reason to read at all (it only loads
   `Textures/`, `Assemblies/`, `Defs/`, etc. under the versioned folder). **Likely
   pure disk waste, not memory** — flagging as a strong candidate for that
   "trim dead content from an absorbed mod" angle the ticket asks about, but this
   is disk-only; it says nothing about this mod's actual RAM contribution.

## UNKNOWN / not measured here

- **No live RSS profiling was done in this task** — no cold-load-vs-after-play-session
  RSS comparison, no per-mod RAM attribution. That needs the game running with a
  profiler attached (e.g. Unity Memory Profiler or ETW), which is explicitly the
  deeper Opus-tier pass's job, not this legwork.
- Whether the two captured crash deaths (05:55 restart is NOT a crash; 12:58:52 IS)
  share the actual `ntdll.dll` c0000005 signature shown in the stale WER excerpts is
  UNPROVEN from this data — the timestamps in those Application-log blocks predate
  both detections.
- Windows host-level physical memory/commit pressure at either death: UNKNOWN (only
  WSL-side `free -h` was captured, which is a different memory pool entirely).
- Whether RimWorld keeps all of RimThemes' per-theme assets resident regardless of
  the selected theme: UNKNOWN without a profiler.
- AssetBundle-shipped content elsewhere in the top 30 beyond the top 5 was not
  checked (out of task scope as specified).
