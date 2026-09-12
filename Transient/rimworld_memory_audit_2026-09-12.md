# RimWorld memory footprint — offline deep pass (2026-09-12)

Feeds `RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1`. Builds on, and **corrects in two places**,
`Transient/memory_audit_legwork_2026-09-07.md` and
`Transient/memory_audit_synthesis_2026-09-08.md` — read this one for the mechanism.

Discipline: every number below is MEASURED with its instrument named, or UNMEASURED.
Modelled figures are labelled MODELLED and carry their formula.

---

## 0. Headline

**Texture RAM is ~13 GB of an 18.8 GB live process, and the single biggest
*un-banked* lever is not compression — it is 1,578 textures whose dimensions are not
divisible by 4, which RimWorld therefore refuses to compress at all.** They cost
2.69 GB instead of 0.67 GB. Fixing them is visually lossless.

The prior synthesis's option A ("texture compression at load, plausibly 5–10 GB")
is **already banked** — compression is on, measured in the owner's live Prefs.

---

## 1. Live measurement

| what | value | instrument |
|---|---|---|
| Live RSS, reading 1 | **19,733,360 KB = 18.82 GB** | MEASURED — `tasklist.exe /FI "IMAGENAME eq RimWorldWin64.exe" /FO CSV`, PID 38076, 2026-09-12 |
| Live RSS, reading 2 (minutes later) | **19,732,220 KB = 18.82 GB** | MEASURED — same instrument, same PID |
| Active mods | **591** | MEASURED — XML parse of live `ModsConfig.xml` (drifted down from 599 on 2026-09-07) |
| Active mods resolved to a folder | 585 of 591 | MEASURED — the 6 unresolved are exactly Core + 5 DLC |
| Prior session peak RSS | 20.17 GB | MEASURED (prior pass, `rimworld_mem_watch_2026-09-05.log`) |

**The owner's "18GB or more" is exactly right and it is not a transient peak** — two
readings minutes apart differ by 1.1 MB. This is steady state on a loaded game, with
a separately-measured excursion to 20.17 GB.

⚠️ This RSS is a full loaded session; whether it is post-cold-load or hours into play
is UNMEASURED (the process was already up when this pass ran). Cold-load-vs-after-play
delta remains owed and needs a deliberate watched load.

---

## 2. The mechanism — read from the game's own source, not inferred

Instrument: RimSage, `./Source/Verse/ModContentLoader.cs`,
`./Source/Verse/StaticTextureAtlas.cs`, `./Source/Verse/PrefsData.cs`,
`./Source/RimWorld/Dialog_Options.cs`. All quotes are from the decompiled 1.6 source.

1. **Texture compression exists, is user-toggleable, and defaults ON.**
   `PrefsData.cs:36` — `public bool textureCompression = true;`
   `Dialog_Options.cs:371` — an in-game Options checkbox, requiring a restart to change.
   → resolves the prior synthesis's "UNVERIFIED — check the options screen first".

2. **It is ON for the owner right now.** MEASURED: live `Prefs.xml` contains
   `<textureCompression>True</textureCompression>`.

3. **Compressed format is DXT5 = 1 byte/pixel** (`StaticTextureAtlas.FastCompressDXT`
   → `GraphicsFormat.RGBA_DXT5_UNorm`), against 4 bytes/pixel for RGBA32.

4. 🔴 **The gate nobody had found** — `ModContentLoader.LoadTextureViaImageConversion`:
   ```csharp
   bool flag = texture2D.width % 4 == 0 && texture2D.height % 4 == 0;
   if (Prefs.TextureCompression && flag) { ...compress to DXT5... }
   else { ...Apply() with no compression... }
   ```
   **A texture whose width or height is not a multiple of 4 is never compressed,
   regardless of the setting.** It lives in RAM at full RGBA32 — 4× cost. Nothing
   warns the user; the only hint is a `Prefs.LogVerbose`-gated warning about
   *mipmaps* for non-power-of-two, which is a different (and milder) penalty.

5. **DDS is natively supported and takes precedence.** `ModContentLoader.LoadAllForMod`
   skips a `.png` outright when a same-named `.dds` exists; `ModDdsLoader.TryLoadDds`
   handles DXT1/DXT5 (`DdsPixelFormat.cs`). MEASURED: **1,645 DDS files already ship
   across 30 active mods.**

---

## 3. Pixel census — the honest offender metric

The prior pass called for this and correctly said disk size over-reports. Done here.

**Instrument**: direct read of each PNG's IHDR header (bytes 16–24), no decode, no
`grep`, no size heuristic. 585 active mod folders walked; `.git`/`.idea`/`.vscode`
excluded; PNGs shadowed by a same-named DDS excluded (they never load — see §2.5).

**MEASURED totals across 591 active mods:**

| | |
|---|---|
| Loaded PNG textures | **56,034** |
| Total pixels | **8.880 Gpx** |
| — DXT-eligible (both dims % 4 == 0) | 54,456 textures, **8.338 Gpx** |
| — **NOT compressible** (a dim not % 4) | **1,578 textures, 0.542 Gpx** |
| On-disk weight of active mod folders | 5.47 GB |

**MODELLED texture RAM** (formula: `DXT-eligible px × 1 B + uncompressible px × 4 B`,
all `× 4/3` for the mip chain):

| scenario | modelled RAM |
|---|---|
| **Compression ON (the live configuration)** | **13.05 GB** — 10.35 GB DXT5 + **2.69 GB RGBA32** |
| Compression OFF (if the owner ever toggles it) | **44.11 GB** |

**This model is corroborated by the live measurement**: 13.05 GB modelled texture RAM
inside an 18.82 GB MEASURED process leaves ~5.8 GB for the engine, def graph, pawn and
path caches, save state and GC heap — a coherent shape. The prior synthesis's implied
45 GB naive RGBA figure *exceeded* the measured peak, which was the tell that the
model was missing compression. It now reconciles.

⚠️ Base game + DLC art is **UNMEASURED by this census** and correctly so: only 7 loose
PNGs exist under `Data/` (MEASURED) — base art ships inside `resources.assets`,
already compressed at build time, and is not a PNG-census target.

### Top 15 active mods by MODELLED texture RAM

Note how different this is from the disk ranking — #1 by disk (Biomes! Caverns, 324 MB)
is #7 here, while the Facial Animation family is tiny on disk and huge in RAM.

| # | mod | modelled RAM | of which UNCOMPRESSIBLE |
|---|---|---|---|
| 1 | Star Wars KotOR Resources and Materials | 497 MB | 4 MB |
| 2 | Vanilla Textures Expanded - [NL] Facial Animation | 445 MB | 1 MB |
| 3 | Big and Small - Genes & More | 431 MB | **204 MB** |
| 4 | [NL] Facial Animation - WIP | 403 MB | 3 MB |
| 5 | EGI Holograms and Projectors | 387 MB | 4 MB |
| 6 | Outland - Genetics | 387 MB | 13 MB |
| 7 | Biomes! Caverns | 374 MB | 77 MB |
| 8 | RW - Planet Atmosphere | 286 MB | 3 MB |
| 9 | Torment Master | 277 MB | **221 MB** |
| 10 | Genetic Mods for Facial Animation | 274 MB | 12 MB |
| 11 | Ancient urban ruins | 267 MB | 90 MB |
| 12 | RimMandrake - Star Wars Races (OURS) | 250 MB | 0 MB |
| 13 | Vanilla Backgrounds Expanded | 249 MB | 82 MB |
| 14 | Jawa Armoury Rebalance (OURS) | 232 MB | 8 MB |
| 15 | Alpha Memes | 221 MB | 16 MB |

### Top 10 by UNCOMPRESSIBLE RAM — the waste list

Every megabyte here is 4× what it needs to be, for a dimension that is off by 1–3 pixels.

| # | mod | wasted-format RAM | textures | worst dimensions |
|---|---|---|---|---|
| 1 | Torment Master | 221 MB | 28 | 1465×1661 |
| 2 | Big and Small - Genes & More | 204 MB | 75 | 1121×630 |
| 3 | **RimStarWars Patches (OURS)** | **181 MB** | 52 | 1254×1254 |
| 4 | Rim of Madness - Bones Unofficial Fix | 120 MB | 4 | 2077×3623 |
| 5 | Ancient urban ruins | 90 MB | 35 | 2274×1281 |
| 6 | Ideology Scavenger Role | 89 MB | 19 | 1875×985 |
| 7 | Vanilla Furniture Expanded - Security | 87 MB | 22 | 853×3808 |
| 8 | Vanilla Backgrounds Expanded | 82 MB | 2 | 5333×3000 |
| 9 | Biomes! Caverns | 77 MB | 15 | 2134×2134 |
| 10 | GravTide | 70 MB | 21 | 2050×1300 |

**Our own mods carry 190 MB of this** (MEASURED across all 69 local mods), 181 MB of
it in `RimStarWars Patches` alone — fixable unilaterally, no Workshop mod touched,
no Steam update to revert it.

---

## 4. Crash correlation

Re-read the captures; **the prior pass's conclusion holds and I did not find reason to
revise it.** Summarised rather than re-derived:

- **No managed OOM anywhere.** Zero `OutOfMemoryException` / low-memory / GC-pressure
  strings in any captured crash log.
- **The one real death happened at 8.70 GB → 8.06 GB, declining** — roughly 12 GB
  *below* the measured peak, and ~7 hours after it. This is not allocation exhaustion.
- **Recurring native `ntdll.dll 0xc0000005` access violation**, same fault bucket
  across three occurrences; one instance already root-caused to concurrent worldgen
  tilegen (`BRIDGE_NTDLL_CRASH_TILEGEN_1`).
- ⚠️ The WER excerpts are stale-cached and predate both detection timestamps, so
  per-death attribution is **suggestive, not proven**.
- Windows host commit pressure at death: **UNKNOWN** — the watch script captured only
  WSL-side `free -h`, a different memory pool entirely.

**Verdict, restated with the new mechanism in hand**: the crash is a *native* fault,
not an OOM. Reducing texture RAM does not directly fix it. But an 18.8 GB steady-state
process on a 32-bit-address-space-free but fragmentation-prone native heap is a
plausible aggravator, and every GB removed lowers that pressure. Treat memory
reduction as hygiene that helps case (b), not as a crash fix.

---

## 5. Reduction options — owner-decidable, with honest expected gain

| # | option | expected saving | basis | trade-off |
|---|---|---|---|---|
| **A** | ~~Turn on texture compression~~ | **0 GB — ALREADY ON** | MEASURED: live `Prefs.xml` `<textureCompression>True</textureCompression>` | — *(this corrects the 2026-09-08 synthesis, which ranked it the biggest lever at 5–10 GB)* |
| **B** | 🥇 **Pad the 1,578 non-multiple-of-4 textures to the next multiple of 4** (transparent pixels; art untouched) | **~2.0 GB** (2.69 → 0.67 GB) | **MEASURED basis** — exact texture list and pixel counts in hand; the 4× factor is read from the game's own `width % 4 == 0` branch | Visually **lossless**. Cost: a script + local copies of Workshop mods (absorption precedent), which Steam updates would revert. Our own 190 MB is permanent and free. |
| **C** | Downscale the pixel-count giants (KotOR, Facial Animation family, EGI Holograms, Outland Genetics — top of §3) | **1–3 GB**, hypothesis | Halving linear resolution cuts RAM 4×; which mods tolerate it visually is a judgement call, UNMEASURED | Visible at max zoom. Same local-copy caveat. Needs the owner to rule per mod. |
| **D** | Drop or trim by RAM rank, not disk rank | up to 0.5 GB per top-15 mod | MEASURED per-mod table in §3 | Content loss — an owner ruling, not a technical one. The table is the input. |
| **E** | Convert PNGs to DDS | **~0 GB RAM** (load-time win only, reportedly 30–40% faster loads) | Source: DDS DXT5 is the *same* 1 B/px the runtime already produces. Only DXT1 (no alpha) would halve it. | ⚠️ **Do not sell this as a memory fix** — it is a load-time fix. Worth it on its own merits given the 15-minute cold load. |
| **F** | Add Windows-side commit capture to the mem-watch script | 0 GB, closes the biggest UNKNOWN | — | Trivial; one `Get-Counter` line. Still owed from the prior pass. |
| **G** | Continue Cherry Picker / absorption def trimming | incremental, compounds | — | The only lever touching the non-texture ~5.8 GB. Already the project pattern. |

⛔ **Not recommended**: chasing the crash as an OOM (evidence says native fault);
ranking mods for removal by disk size (§3 shows the two rankings barely correlate).

---

## 6. What is still UNMEASURED

- **Cold-load vs after-play RSS delta** — needs a deliberate watched load; this pass
  caught the process already up. Still owed, and should ride a load already being paid for.
- **Per-mod RAM attribution by profiler** — the §3 table is a *model*, well-corroborated
  in aggregate but never per-mod-verified. Do not cite a single row as measured RAM.
- **Whether RimThemes keeps all per-theme assets resident** regardless of active theme
  (its bulk is audio/video, invisible to a pixel census) — needs a profiler.
- **Base game / DLC texture RAM** — ships in `resources.assets`, not loose PNGs;
  outside this census by design.
- **Windows host commit pressure at crash time** — see option F.

---

## Provenance

- Pixel census scripts: `/tmp/.../scratchpad/` (throwaway; the numbers above are the
  deliverable). Re-derivable in ~3 minutes from the method in §3.
- Source quotes: RimSage over decompiled RimWorld 1.6.
- Web corroboration for the compression-off cost (500 mods: 17 GB vanilla vs 29 GB with
  compression disabled) — consistent with this report's 13.05 GB / 44.11 GB model:
  [Graphics Settings+ comments](https://steamcommunity.com/sharedfiles/filedetails/comments/1678847247),
  [High quality textures](https://steamcommunity.com/sharedfiles/filedetails/?id=1676969930),
  [Mod Textures — RimWorld Wiki](https://rimworldwiki.com/wiki/Modding_Tutorials/Textures).
