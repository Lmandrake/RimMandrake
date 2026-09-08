# RimWorld memory footprint — synthesis (deep pass, 2026-09-08)

Feeds `RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1`. Built ON the mechanical legwork
(`Transient/memory_audit_legwork_2026-09-07.md`) — read that first; every number
below is either from it (MEASURED) or explicitly marked estimate/hypothesis.

## 1. What the numbers actually say

- **The 18GB+ is real: peak RSS 20.17 GB MEASURED** — but it is a *play-session
  peak*, not steady state (min 1.08 GB at launch; ~7.3 GB steady in one watched
  session; peak hit hours into play).
- **The crash is NOT a managed OOM.** Zero OutOfMemory/GC-pressure strings in any
  captured log; the one real death happened at 8.7 GB *declining* — nowhere near
  the peak. The recurring `ntdll.dll 0xc0000005` access-violation signature (same
  fault bucket, three occurrences) is a NATIVE fault — heap corruption /
  use-after-free territory, and FOUNDRY already root-caused one instance to
  concurrent worldgen tilegen (`BRIDGE_NTDLL_CRASH_TILEGEN_1`). ⚠️ The WER
  excerpts are stale-cached, so per-death attribution is suggestive, not proven.
- **The 2.7× gap (7.4 GB on disk → 20.17 GB peak) is the expected shape, not a
  mystery.** RimWorld loads loose PNGs into uncompressed RGBA GPU/RAM buffers:
  a compressed PNG expands to `width × height × 4 bytes (+~33% mipmaps)` —
  file size on disk is nearly irrelevant; **pixel count is the real currency.**
  599 mods of loose PNG art plausibly accounts for the majority of the peak,
  with def graphs, pawn/path caches and GC fragmentation on top.
  - Worked example, MEASURED file: RW Planet Atmosphere's single
    `8k_earth_clouds.png` (8192×4096) ≈ **178 MB of RAM as RGBA+mips** from a
    45 MB file. One texture.

## 2. Why it crashes anyway (working hypothesis, honestly labeled)

A native access violation at modest RSS, hours after a 20 GB peak, fits
**address-space/heap fragmentation or native-heap corruption**, not allocation
exhaustion. Two non-exclusive candidates:
(a) a genuine native bug (the tilegen crash proves at least one exists);
(b) long sessions at very high texture pressure degrade the native heap so a
later ordinary allocation faults. Reducing texture RAM helps (b) and is harmless
to (a). **Windows host commit pressure at death: UNKNOWN — the watch captured
only WSL's memory.** Closing that hole is cheap (see option F).

## 3. Reduction options — owner-decidable, ranked by expected RAM saved

| # | option | expected saving | trade-off / cost |
|---|---|---|---|
| A | **Texture compression at load** — verify whether RimWorld 1.6's graphics/perf settings expose a compress-textures toggle (UNVERIFIED — check the options screen first); if absent, evaluate a load-time DXT-compression mod (Graphics Settings+ lineage / Performance Fish). DXT is 4–8× smaller than RGBA. | **The single biggest lever — plausibly 5–10 GB off peak** if textures dominate as §1 argues | Slight art quality loss; longer first load while encoding; one quicktest + one full load to verify |
| B | **Downscale the loose-PNG giants** (Biomes! Caverns 1,194 PNGs, GRiNDTerra 950, Minerals Rock 629 — all loose, all re-encodable). Halving linear resolution cuts their RAM 4×. | 1–3 GB (est.; needs a pixel census, one script) | Visible on max zoom; must hold local copies (absorption precedent) or Workshop updates revert it |
| C | **The 8K clouds file**: downscale `8k_earth_clouds.png` to 2K | **~170 MB from ONE file** (MEASURED size, computed expansion) | Softer planet clouds in the space view; minutes of work; same local-copy caveat |
| D | **RimThemes diet** — 260 MB of mixed media (images+audio+video for EVERY theme). Whether unused themes stay resident is UNMEASURED (profiler needed); if they do, trimming to the one used theme or dropping the mod is ~0.5–1 GB (est.) | UI cosmetics only; zero gameplay | Profile first, or just drop it and measure the delta on one load |
| E | **Continue absorption/Cherry Picker trimming** — fewer live defs shrinks the def graph and every per-def cache; also the only lever that touches the non-texture share | Incremental per mod; compounds | Already this project's pattern; slow |
| F | **Instrument the host side** — add Windows-side commit/physical-memory capture (one `powershell Get-Counter` line) to the existing mem-watch script, so the next death carries host pressure data | Closes the biggest UNKNOWN for attribution | Trivial; no game cost |

⛔ NOT recommended: chasing the crash as if it were OOM (evidence says native
fault), or ranking mods for removal by disk size (the Minerals Rock `.git` folder
and Planet Atmosphere's bundled Unity project show disk size over-reports; pixel
count is the honest ranking — one script away, rides option B).

## 4. Still owed (live, deliberate — never its own errand per the maturity rules)

Cold-load vs after-play RSS comparison and per-mod RAM attribution need a
profiler on a load we're already paying for; the pixel-census script for
options A/B can run offline any time.
