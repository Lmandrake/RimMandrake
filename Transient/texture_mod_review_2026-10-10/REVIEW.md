# Texture / resolution / upscaling mod review — 2026-10-10

## 1. Which list (MEASURED)

Parsed with `xml.etree.ElementTree` → `find("activeMods")`, never a `<li>` grep.

| list | active mods (MEASURED) | note |
|---|---|---|
| `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` (live, now) | **68** | shrunk (post-crash/minimal); not the full list |
| `…\Config\ModsConfig.xml.belt_bak_175633` (2026-10-03) | **634** | **largest list on disk — USED as primary** |
| `…\Config\ModsConfig.xml.bak_cauldron_overrides_20261009_085401` (mtime 10-07) | **614** | most recent full list; 5 mods in it are not in the 634 |
| largest in `infrastructure/state/modlists/` | 599 (`ModsConfig.FULL.PRECAPTURE.20260907_215737.xml`) | older; superseded by the two above |

Reviewed set = **union of 634 + 614 + live = 647 packageIds**. Of these, **591 resolve to an installed folder**
(About.xml scan of BOTH roots: 1,377 installed packageIds). Unresolved: 6 `ludeon.*` (DLC, in `Data\`), and
~50 ids that are in the 634 list but have **no installed folder** — 48 of them are our retired
`mandrake.rsw.*artoverride` / `mandrake.rut.*artoverride` mods (retired 2026-09-18), plus `mandrake.rm.messyconduit`,
`mandrake.rm.warscar`, `vlvop.tormentmaster.expansion`. Those cannot load, so they cannot touch textures.
⇒ the 634 list is partly stale; the 614 list is the realistic "full" set.

## 2. Census method and sanity probes

Python only (no shell loops). For each of the 591 resolved mods:

1. **Text**: regex over `<name>` + `<description>` for texture/HD/high-res/upscale/4K/2K/retexture/sprite/graphics/
   resolution/atlas/compress/DDS/mipmap/zoom/camera/reskin.
2. **Textures tree**: every `.png/.dds/.jpg/.psd/.tga` under any `Textures/` folder — count, bytes, DDS count.
   Max-dimension histogram sampled (~80 files/mod) from PNG/DDS headers.
3. **Vanilla overlap**: each texture's path under `Textures/` compared against (a) the vanilla DLC AssetBundle container
   paths and (b) every `texPath`/`graphicPath`/`iconPath` in `RimWorld\Data\*\Defs` (2,933 paths; exact match after
   stripping `_north/_south/_east/_west/m` suffixes = **override**; same folder = **added variant**), and (c) Core
   `resources.assets` names (3,381; Core has no container paths, so a stem match is **weak** evidence — it fires on
   new art with vanilla-like stems, e.g. Astronomy Style Pack's `Column.png`).
4. **Assemblies**: only DLLs a 1.6 load would actually use (skipping `Source/ obj/ bin/ packages/`, bundled
   `Assembly-CSharp`/`UnityEngine`/Harmony copies, and `1.0–1.5` folders) searched for texture-loading and camera API
   names in both UTF-8 (metadata) and UTF-16 (string literals): `LoadImage, ModContentLoader, LoadTexture, mipMapBias,
   anisoLevel, Compress, LoadRawTextureData, DXT, mipmap, filterMode, TextureFormat, maxTextureSize, masterTextureLimit,
   rootSize, ZoomRootSize, sizeRange`.
   ⚠️ The first pass without that filter lit up 7 mods with hundreds of hits each (e.g. Tech Level Enforcement,
   Minerals *, Selectable Sculpture Graphic) — every one was a **bundled copy of Assembly-CSharp / Mono.Cecil in a
   Source/ or packages/ folder**, never loaded. Discarded.

**Sanity probes (the instrument can see):** known texture mods were found — More Vanilla Textures (45 exact vanilla
overrides), Morphs Assorted Biotech Retex (110 exact), Van's Melee Weapons (13 exact), ReGrowth 2 ("HD" in
description), GRiNDTerra Terrain Retexture. Installed-but-INACTIVE texture mods were also found (proves the sweep
reads beyond the active list): `telefonmast.graphicssettings` (Graphics Settings+), `vanillaexpanded.vtexe`
(Vanilla Textures Expanded), `vanillaexpanded.vtexvariations`, `gerrymon.uvt` (Gerrymon's Upscaled Vanilla Textures),
`cf.anomalyupscaled`, `dbh.upscaled`, `bionicicons.hd`, `shira.rgrwthpatch`, `el.biotechmechrt`.

**Hit counts:** 198 of 591 mods tripped at least one weak signal; 63 had a texture/camera API name in a loaded DLL
(almost all are ordinary UI icon loading); after reading name+description+contents, **39 are flagged** below.

Limitations: `LoadFolders.xml` was not resolved per mod (a texture in an unlisted folder was still counted), and a
clean DLL string scan cannot *prove* a negative — read "none detected by this scan", not "none exists".

**Engine facts used (RimSage, decompiled 1.6 `Verse/ModContentLoader.cs`, `Verse/ContentFinder.cs`):**
- `ContentFinder` walks running mods **last → first**: the **last-loaded mod wins** a texture path.
- Within one mod, a `.dds` with the same name **replaces** the `.png` (the PNG is skipped, never loaded).
- Loose PNGs load with a full mip chain, **Trilinear, aniso 2**. If `Prefs.TextureCompression` is on **and** both
  dimensions are multiples of 4, the texture is **DXT-compressed at load** (`FastCompressDXT` on GPUs with compute
  shaders). Non-power-of-two sizes get a **clamped mip count** when compression is on ("will look worse when zoomed out").
- Owner's `Prefs.xml`: **`<textureCompression>True</textureCompression>`** (MEASURED). So OUR generated PNGs are
  being DXT-compressed by vanilla today — no mod is doing it.

## 3. Flagged mods — per-mod findings

Paths are under `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\<id>` (workshop) or
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<Folder>` (ours). "pos" = position in the 614 list
(higher loads later and **wins** a texture path). "res" = sampled max edge in px.

### 3a. Vanilla retexture / "upscale vanilla" mods — the owner's question

| mod | what it measurably does | size | verdict |
|---|---|---|---|
| **More Vanilla Textures** `tidal.morevanilla.textures` (ws 2707120862, pos 223) | "higher resolution and more variety" for vanilla: **45 exact vanilla path overrides + 9 added variants**, plus **30 XML ops that repoint vanilla `texPath`/`graphicClass`** (eggs, tusks…). Res 128–256 — barely above vanilla. We already counter-patch its egg `drawSize` (`src/RimUtinni/UtinniPatches/Patches/StatNorm_MoreVanillaTextures_DrawSizeNeutral.xml`). | 0.9 MB | REMOVE AT ART-REGEN (before its subjects are redrawn) |
| **Morphs Assorted Biotech Retex** `morphsassorted.biotechretex` (2950383797, pos 224) | "High res Textures for Biotech": **110 exact overrides** of Biotech paths (growth vat, baby food…), 512 px, every file shipped as DDS **and** PNG (the PNG is skipped by the engine). | 26.5 MB | REMOVE AT ART-REGEN |
| **Van's Retexture: Melee Weapons** `sirvan.mwretextured` (2922441211) | 13 exact overrides of vanilla melee weapons, 256 px; its own description: *"You are using camera+? … higher, crisper resolution"*. | 0.1 MB | REMOVE AT ART-REGEN |
| **Van's Retexture: Steel** `sirvan.steelretexture` (2955560866) | Steel_a/b/c, 256 px. | 0.1 MB | REMOVE AT ART-REGEN |
| **Simple Cape and Hood Retexture** `stokes.simplehoodcape` (3543386604) | 6 exact apparel overrides + 1 patch replacing `Apparel_Cape/graphicData`, 256 px. | 0.7 MB | REMOVE AT ART-REGEN |
| **Rustic Meal Retexture** `jelheb.rusticmealretexture` (3453364177, pos 529) | No path overrides at all — **213 XML ops repoint meal `texPath`s** (vanilla + VE + others) to `RusticMeal/…`, 128 px. | 2.2 MB | REMOVE AT ART-REGEN — ⚠️ masks any meal art we place at vanilla paths, **regardless of load order** |
| **GRiNDTerra Terrain Retexture** `grimterra.terrainretexturemod` (3543925559, pos 150) | "Earthlike Textures": replaces **~30 Core/Odyssey terrain surfaces** at their exact paths, incl. **Sand, Gravel, PackedDirt, NewAridSoil, Mud, RoughStone** — i.e. the ground of every desert map. **1024 px** (one 4096). | **102.8 MB** | REMOVE AT ART-REGEN (terrain pass); it is the largest vanilla override on the list and defines today's ground look |
| **Better Trees** `chaoticenrico.bettertrees` (3539609975) + **Maal's Djeeshka textures** `maal.bettertreesmod` (3543705507) + **Comigo Better Trees** `qux.comigo.bettertreesmod` (3559784361) | A Harmony framework that **swaps tree graphics at runtime by defName** from `TreeTextureTemplateDef` dictionaries; the two packs map 14–25 vanilla/DLC trees (Oak, Pine, Palm, Teak, Bamboo, Anima, Gauranlen…). 512 px. Our `src/RimUtinni/AshkarrFlora/Patches/BetterTrees_SweetlineTree_Immunity.xml` already guards our own tree. | 53.5 MB | REMOVE AT ART-REGEN (trees pass) — ⚠️ **masks a texPath-level redraw of any mapped tree no matter the load order** |
| **ReGrowth 2** `regrowth.botr.core` (2260097569, pos 439) | Content framework **and** "replace many of the vanilla plant textures with HD ones": **66 XML ops repointing vanilla plant `texPath`s** + added variants in vanilla chunk folders. Res mostly 128–256, some 1024. **Our biome XML depends on it** (12 files in `src/`, e.g. `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Webwork.xml`). | 104.7 MB + 8.5 MB bundles | KEEP (dependency) — when we redraw a vanilla plant, patch its `texPath` *after* ReGrowth rather than drop a PNG at the vanilla path |
| **World Map Enhanced** `zal.worldmapenhanced` (3599967849, pos 393) | Replaces world-map biome textures (229 files, 73 matching Core names), 256–512 px. GRimTerra World Map loads later and overrides 30 of its paths; the rest still shows. | 31.4 MB | REMOVE AT ART-REGEN END (planet paint pass) — *changed after GPT review, see §5* |
| **GRimTerra World Map** `grimterra.worldmap` (3546956014, pos 422) | World-map biome textures, 512 px. | 19.5 MB | REMOVE AT ART-REGEN END (the once-only planet paint pass) |
| **[Dizzy] Candles and Hidden Meditation** `dizzy.candlesandmeditation` (2569910895) | Functional (candles; smaller/invisible meditation & ritual spots) + 14 exact overrides of spot art. | 0.5 MB | KEEP (functional; our later art wins by path) |
| **More Sculpture** `bichang.moresculpture` (1612316880, pos 220) | Adds **574 files (74 variants per sculpture)** *inside vanilla's sculpture folders*. | 18.7 MB | REMOVE AT ART-REGEN — ⚠️ see §4 pooling: these mix into **our** redrawn sculptures at random |

### 3b. Retextures of other (donor) mods

| mod | measured | size | verdict |
|---|---|---|---|
| **Alpha Animals Retextured** `ks.aaretextured` (3536598972) | 243 creatures × (DDS + skipped PNG), 512 px, over Alpha Animals' own paths. | **69.3 MB** | REMOVE AT ART-REGEN END (goes with Alpha Animals' cast as we replace/cut it) |
| **Research Reinvented Retextured** `aw.researchreinvented.retextured` | 21 DDS UI/kit textures, 512 px. | 7.8 MB | REMOVE AT ART-REGEN END (low value) |
| **Character Editor Retextured** `neronix17.retexture.charactereditor` | UI skin for Character Editor (visible whenever that editor is opened). | 1.0 MB | KEEP (out of regen scope by preference, not because nobody sees it) |
| **Ancient urban ruins** `xmb.ancienturbanruins.mo` (3316062206) | Content (urban ruin maps) + 39 exact overrides and **53 added files in vanilla `Things/Building/Ruins/*` folders**, 64–1024 px. | 28.3 MB | KEEP content; at the ruins pass, isolate or counter-patch its pooled/overriding ruin art |
| **Adaptive Storage** trio `adaptive.simplestorage` / `.primitivestorage` / `.ideology.storage` | Content (storage buildings) using "Phaneron's retexture"; DDS+PNG pairs, 256–1136 px. | 71 MB | KEEP — ordinary content; its art is regenerated like any donor's |

### 3c. Facial animation stack (pawn faces) — not upscalers, but heavy texture sets

`nals.facialanimation` (functional, 1,236 files) · `vanillaexpanded.vtexe.facialanims` (1,300 files, + 4 exact vanilla
wound overrides) · `reel.facialanims` · `sd.fa.reelsadjustments` (23.6 MB DDS) · `sd.fa.vteadjustments` ·
`danzinagri.facialanimationcompatabilityproject` (29.5 MB) · `sd.fa.geneticheadsmods`. ~72 MB together, 512 px.
**Verdict: KEEP — UNSURE only on the owner's say.** CLAUDE.md: cosmetic face changes need his permission and can
break animated faces. Any regen of faces is a separate decision (Q3 below).

### 3d. Texture loading / compression / atlas / VRAM

- **No active mod replacing the engine's texture loader or compression was detected by this scan.** The only active loaded DLLs touching
  `LoadImage`/`Compress` do it for their own UI icons or menu art (HugsLib, Camera+, VBE, Worldbuilder, RimThemes…).
  **Graphics Settings+ (`telefonmast.graphicssettings`) is installed but INACTIVE.**
- The compressor that actually touches our art is **vanilla's own `textureCompression=True`** (§2). KEEP it: DXT
  roughly quarters VRAM, which matters at 3.07 GB of loose textures on disk.
- **Vanilla Backgrounds Expanded** `vanillaexpanded.backgrounds` (2775017012): 39 menu backgrounds at
  **1920–5333 px, 147.9 MB**, loaded at startup. **Our `RimUtinni: Menu Shell` depends on it**
  (`src/RimUtinni/MenuShell/Defs/BackgroundImageDefs.xml`). KEEP; its cost is the price of the menu shell.
- **RW – Planet Atmosphere** `rwnodetree.rwplanetatmosphere` (3272330410): a **single 8192×4096 cloud PNG (45 MB)** plus
  a 5000×5000 sun flare, world-map cosmetics only. One 8K RGBA texture is 128 MB uncompressed / ~43 MB DXT5 with mips.
  **UNSURE** — test below.
- **RimThemes** `arandomkiwi.rimthemes` (1668983184, 24.6 MB): a UI theme engine that loads/swaps UI textures itself.
  Our **Rust Chrome** UI skin (`mandrake.rm.rustchrome`, 14 vanilla UI paths) is in the 634 list but **not** in the
  614 list. **UNSURE** — two UI skinning systems at once; decide with the UI pass.

### 3e. Zoom / camera

- **Camera+** `brrainz.cameraplus` (867467808) — in both full lists; extra zoom range, Harmony on `CameraDriver`.
- **SimpleCameraSetting** `ray1203.simplecamerasetting` (3232415388) — in the **live 68-mod list only**, not in either full
  list. Same job ("modify the zoom range"), written as a lighter Camera+.
- **Verdict: KEEP exactly one zoom mod.** It is the only mod here that *sets a target* for our regen: the memory note
  `art-downscale-legibility-and-resolution` records that the 256² knee was measured at **vanilla** zoom tiers only and
  that enhanced zoom makes "the player can't see past 128 px/cell" UNMEASURED. The zoom mod we ship with decides the
  real max px-per-cell.

### 3f. Our own texture-override mods (for completeness)

`mandrake.rm.rustchrome` (UI skin), `mandrake.rsw.desertvehiclereskin` (30 × 512 over Alpha Vehicles Neolithic),
`mandrake.rut.menushell` (2560-px menu art, 35 MB), `mandrake.rsw.kotorbandoliernorthfix`, `mandrake.rsw.msedroidfix`.
KEEP — they *are* the regen. MEASURED: all of our mods load **after** every third-party mod they collide with
(110 shared paths, ours wins in every case).

## 4. Interactions with our art pipeline

**Our art, MEASURED:** 9,110 loose PNGs across our deployed mods, 0.85 GB of the 3.07 GB of loose textures on the full
list. Random sample of 1,500: 45% are 512 px, 38% 256, 9% 128, 2% 1024; **63 (4%) are not power-of-two** and 1 is
not a multiple of 4.

1. **Path overrides cannot beat us; three other mechanisms can.** Load order decides a same-path fight and our mods
   load last (110 collisions, 110 wins). But three mechanisms ignore load order entirely:
   - **XML `texPath` repointing** — Rustic Meal (213 ops), ReGrowth (66), More Vanilla Textures (30). If we drop a PNG
     at the vanilla path, the def no longer asks for that path, so our art never shows.
   - **Runtime swap by defName** — Better Trees (3 mods). Same effect for 14–25 trees.
   - **Folder pooling** — `ContentFinder.GetAllInFolder` (decompiled 1.6) gathers textures **from every mod** under a
     folder, and `Graphic_Collection.Init` keeps every distinct name as a random variant. So More Sculpture's 574 files,
     Ancient Urban Ruins' 53, ReGrowth's chunk variants and More Vanilla Textures' 9 **are mixed in at random beside our
     redrawn art** in the same folders, whatever the load order.
   ⇒ The trap for the regen is not "the upscaler wins"; it is **"our art is silently not used, or diluted among
   donor variants"** (`Graphic_Random` picks a stable variant per thing ID, so it is a share of things, not a flicker).
   A redraw that targets one of those subjects must neutralise the mod before it is accepted.
   **Checked today (MEASURED):** our deployed art has 0 files at vanilla tree paths, 0 graphic patches on vanilla
   meal/tree/sculpture defs, our meals and our one statuary use our own folders, and our EggOval a/b/c share names
   with More Vanilla Textures' a/b (same name → ours wins). So no already-shipped art of ours was found masked.
2. **Cold load.** Every loose PNG is decoded and DXT-compressed at startup; nothing here is lazy. The removal set in
   §7 is **~334 MB** of the 3.07 GB (≈11%) — GRiNDTerra terrain (103 MB), Alpha Animals Retextured (69 MB) and the
   Better Trees trio (54 MB) are most of it; +47 MB if Planet Atmosphere goes too. Without a profiled load this cannot be converted into minutes — **UNMEASURED**. Expect a
   modest share of the ~15-minute load, not a dramatic one.
3. **Do loader/compression mods change how our PNGs look?** No third-party mod does. Vanilla does: with
   `textureCompression=True` our RGBA PNGs become DXT5 (block compression — 4×4 blocks, some banding in smooth
   painterly gradients and soft alpha edges), and the **4% non-power-of-two files get a clamped mip chain** that the
   engine itself warns "will look worse when zoomed out". Our generator should emit **power-of-two canvases**.
4. **Atlas thresholds (decompiled 1.6, `Verse/GlobalTextureAtlasManager.cs`, `Verse/PawnTextureAtlas.cs`,
   `Verse/PawnRenderer.cs`).** `TryInsertStatic` **refuses any texture with a side ≥ 512**, so 512-px building/item
   art is never batched into the static atlas (more draw calls, and it keeps its own mips). Humanlike pawns are drawn
   from a **128-px-per-frame** atlas whenever zoomed out (`ZoomRootSize > 18`); animals never use it. ⇒ 256 vs 512 is a
   real engine boundary for static things, and humanlike detail above 128 px only shows up when zoomed in.
5. **Resolution target.** Donor upscalers sit at 128–512 px (only GRiNDTerra terrain and ReGrowth hit 1024). None of
   them is a better target than our own `drawSize × 128 px/cell` rule (`skills/generating-rimworld-sprites`). The
   zoom mod's maximum zoom is the one external number that should set the ceiling.

## 5. GPT review

`python3 src/RimMandrake/Utils/gpt_consult.py … -m gpt-6.1-sol --effort high`, given this file (draft §1–6).
Summary of its answer:

**Agreed with:** subject-by-subject retirement for Morphs, Van's ×2, Cape/Hood and GRiNDTerra; ReGrowth kept as a
dependency; compression left on provisionally; folder pooling called "a real, serious contamination mechanism".

**Disagreements and what I did with each:**

| GPT's point | My check | Change |
|---|---|---|
| "World Map Enhanced is mostly masked" is unsupported — 30 overridden paths out of 229 files | Correct: I conflated "30 of GRimTerra's 36" with WME's total | **WME: REMOVE NOW → REMOVE AT ART-REGEN END** |
| Check already-regenerated subjects for masking *now*, not later | Ran it: 0 of ours at vanilla tree paths, 0 patches on meal/tree/sculpture defs, our meals/statuary in own folders | No change needed; result recorded in §4 |
| Static atlas rejects textures ≥512; pawn atlas is 128-px frames | **Confirmed** in decompiled 1.6 (and pawn atlas is humanlike + zoomed-out only) | Added §4 item 4; feeds Q-free pipeline note in §6 |
| "~11% of disk bytes ⇒ modest load cost" is not evidence | Correct — PNG bytes ≠ decode/compress/atlas work | §6 now calls it an untested hypothesis and names the A/B |
| Split Better Trees framework from its texture packs | Fair: the framework also does resizing/snow | **Framework → UNSURE; the two packs stay REMOVE AT ART-REGEN** |
| VBE: find out what Menu Shell actually needs before accepting its 148 MB | Fair | Kept KEEP, added follow-up in §6 |
| Planet Atmosphere deserves an A/B now (8192×4096 ≈ 171 MiB RGBA with mips, ~43 MiB BC3) | Agree | Stays UNSURE; promoted to owner question Q2 |
| Character Editor UI *is* player-visible | Correct | Wording fixed |
| Ancient Urban Ruins missing a verdict | Correct | Added: KEEP content, isolate pooled art at ruins pass |
| `Graphic_Random` picks a stable variant per thing; "1 in 75" is not a measured rate | Correct | Wording fixed in §4 |
| Power-of-two improves mips but the GPU compressor still floors the smallest mips (~16 px) | Not re-verified | Kept the POT recommendation; did not claim full mips |
| Missing audit axes: shaders/masks/material colours, graphic-class states, Harmony render patches, AssetBundle direct loads, colour grading/post-processing, stale DDS siblings in OUR folders, VRAM peaks | Agree these are real and not covered by a texture census | Listed in §6 as the per-subject "rendering manifest" check; **not** measured here |
| If BC3 visibly hurts key art, test offline BC7 DDS (engine's DDS loader reads it) — but atlas recompression may undo it for <512 static art | Plausible, unmeasured | Recorded as a fallback, not a plan |

Raw answer: kept out of the repo (scratch); the substance is above.

## 6. Recommended direction

1. **Answer to the owner's instinct: yes, the "upscale vanilla" mods should go — but one subject at a time, not all
   at once.** None of them slows the load dramatically on the evidence we have, and none beats our art on a plain
   path fight (our mods load last: 110 collisions, 110 wins). Pulling them now only puts vanilla art back on screen —
   art that is itself going to be regenerated.
2. **The real risk is masking, not quality.** Rustic Meal (213 repoints), ReGrowth (66), More Vanilla Textures (30),
   Better Trees (defName swaps) and More Sculpture / Ancient Ruins (folder pooling) can hide or dilute our redraws
   **whatever the load order**. So step 0 of every regen batch: list every active mod that repoints, swaps or pools
   that subject; neutralise it (remove the pure-retexture mod, or counter-patch a content mod we keep); then accept
   the art only after an in-game check. Remove a whole pure-retexture mod once none of its remaining coverage is
   wanted.
3. **Keep:** vanilla `textureCompression` on (provisionally — A/B it on painterly art at max zoom), exactly one zoom
   mod (Camera+ on the full list), ReGrowth (dependency), VBE (Menu Shell dependency — but find out whether Menu Shell
   can stop depending on its 148 MB of backgrounds), the facial animation stack (owner's call), Dizzy Candles.
4. **Pipeline changes this review justifies:**
   - Power-of-two canvases (4% of ours are not, and the engine clamps their mips).
   - Treat **512 as a real boundary**: static things at ≥512 px are never atlased; keep 256 the default for small
     static things and go to 512 only with a reason (consistent with the existing `oversize_reason` gate).
   - A per-subject **rendering manifest** before acceptance: final def, graphic class and states, effective
     texture path(s) and which mod supplies each, masks/shader, any Harmony or defName swap — so "our art wins" is
     shown, not assumed. Includes stale same-name `.dds` in our own folders (a DDS silently suppresses a new PNG).
5. **Measurements still owed (not done here):** a load-time A/B of the removal group on the frozen full list; a VRAM
   read with/without Planet Atmosphere; a compression on/off screenshot pair of our art at max Camera+ zoom.

## 7. Verdict table (39 flagged)

Verdict counts: **KEEP 21 · REMOVE NOW 1 · REMOVE AT ART-REGEN (per subject / at end) 14 · UNSURE 3.**

| # | mod (packageId) | what it does to textures | size | verdict | single deciding test (UNSURE only) |
|---|---|---|---|---|---|
| 1 | More Vanilla Textures (`tidal.morevanilla.textures`) | 45 vanilla overrides + 30 texPath repoints, ≤256 px | 0.9 MB | REMOVE AT ART-REGEN (its subjects) | |
| 2 | Morphs Assorted Biotech Retex (`morphsassorted.biotechretex`) | 110 Biotech overrides, 512 px DDS | 26.5 MB | REMOVE AT ART-REGEN | |
| 3 | Van's Retexture: Melee Weapons (`sirvan.mwretextured`) | 13 overrides, 256 px | 0.1 MB | REMOVE AT ART-REGEN | |
| 4 | Van's Retexture: Steel (`sirvan.steelretexture`) | 3 overrides | 0.1 MB | REMOVE AT ART-REGEN | |
| 5 | Simple Cape and Hood Retexture (`stokes.simplehoodcape`) | 6 overrides + graphicData patch | 0.7 MB | REMOVE AT ART-REGEN | |
| 6 | Rustic Meal Retexture (`jelheb.rusticmealretexture`) | 213 meal texPath repoints | 2.2 MB | REMOVE AT ART-REGEN (meals) | |
| 7 | GRiNDTerra Terrain Retexture (`grimterra.terrainretexturemod`) | ~30 Core terrains incl. Sand/Gravel/NewAridSoil, 1024 px | 102.8 MB | REMOVE AT ART-REGEN (terrain) | |
| 8 | Maal's Better Trees textures (`maal.bettertreesmod`) | defName tree swaps, 512 px | 42.2 MB | REMOVE AT ART-REGEN (trees) | |
| 9 | Comigo Better Trees (`qux.comigo.bettertreesmod`) | defName tree swaps, 512 px | 6.0 MB | REMOVE AT ART-REGEN (trees) | |
| 10 | More Sculpture (`bichang.moresculpture`) | 574 variants pooled into vanilla sculpture folders | 18.7 MB | REMOVE AT ART-REGEN (sculptures) | |
| 11 | Alpha Animals Retextured (`ks.aaretextured`) | 243 AA creatures, 512 px DDS | 69.3 MB | REMOVE AT ART-REGEN (AA cast) | |
| 12 | Research Reinvented Retextured (`aw.researchreinvented.retextured`) | RR UI/kits, 512 px DDS | 7.8 MB | REMOVE AT ART-REGEN END | |
| 13 | World Map Enhanced (`zal.worldmapenhanced`) | world biome textures | 31.4 MB | REMOVE AT ART-REGEN END (paint pass) | |
| 14 | GRimTerra World Map (`grimterra.worldmap`) | world biome textures, wins 30 paths over #13 | 19.5 MB | REMOVE AT ART-REGEN END (paint pass) | |
| 15 | SimpleCameraSetting (`ray1203.simplecamerasetting`) | zoom range; duplicate of Camera+ (live 68-list only) | — | REMOVE NOW (from any list that also has Camera+) | |
| 16 | Better Trees framework (`chaoticenrico.bettertrees`) | runtime defName graphic swap + resize/snow | 5.3 MB | UNSURE | after packs 8–9 go: does it still change anything we want? Screenshot a vanilla oak/pine with vs without |
| 17 | RW – Planet Atmosphere (`rwnodetree.rwplanetatmosphere`) | 8192×4096 cloud PNG + 5000² flare | 47.1 MB | UNSURE | VRAM + load-time A/B with/without, and does the owner want the effect (Q2) |
| 18 | RimThemes (`arandomkiwi.rimthemes`) | UI theme engine, loads its own UI textures | 24.6 MB | UNSURE | in the UI pass: load with Rust Chrome — do our slider/button PNGs show? |
| 19 | ReGrowth 2 (`regrowth.botr.core`) | content + 66 vanilla plant repoints, HD | 113 MB | KEEP (dependency; counter-patch per plant) | |
| 20 | Ancient urban ruins (`xmb.ancienturbanruins.mo`) | content + 39 overrides + 53 pooled ruin files | 28.3 MB | KEEP (isolate its art at ruins pass) | |
| 21 | [Dizzy] Candles and Hidden Meditation (`dizzy.candlesandmeditation`) | functional + 14 overrides | 0.5 MB | KEEP | |
| 22 | Vanilla Backgrounds Expanded (`vanillaexpanded.backgrounds`) | 39 menu backgrounds up to 5333 px | 147.9 MB | KEEP (Menu Shell dependency) | |
| 23 | Camera+ (`brrainz.cameraplus`) | extended zoom — sets the real px/cell ceiling | 0.1 MB | KEEP (the one zoom mod) | |
| 24 | Character Editor Retextured (`neronix17.retexture.charactereditor`) | editor UI skin | 1.0 MB | KEEP | |
| 25–27 | Adaptive Simple / Primitive / Ideology Storage (`adaptive.*`) | storage content with retextured art | 71 MB | KEEP (regen as donor content) | |
| 28–34 | Facial animation stack (`nals.facialanimation`, `vanillaexpanded.vtexe.facialanims`, `reel.facialanims`, `sd.fa.reelsadjustments`, `sd.fa.vteadjustments`, `danzinagri.facialanimationcompatabilityproject`, `sd.fa.geneticheadsmods`) | animated face textures, 512 px | ~72 MB | KEEP (owner's call, Q3) | |
| 35–39 | Ours: Rust Chrome, Desert Vehicle Reskin, Menu Shell, Bandolier North Fix, MSE Droid North Fix | our overrides | ~37 MB | KEEP | |

Not flagged but noted: no active texture-loader/compression mod detected; installed-but-inactive upscalers
(Vanilla Textures Expanded, Gerrymon's Upscaled Vanilla Textures, [CF] Anomaly Upscaled, [CF] Dubs Bad Hygiene
Upscaled, Bionic Icons HD, Graphics Settings+) should stay inactive.

## 8. Owner decisions

**Q1. When should the "upscale vanilla textures" mods come out?**
- (a) One at a time, just before we redraw what each one covers *(recommended — no stretch of vanilla art, and it
  catches the mods that would hide our new art)*.
- (b) All the pure retexture packs now (rows 1–14, ~330 MB). Simpler list; the game shows plain vanilla art until our
  redraws land.
- (c) Leave them all until the whole regen is finished, then remove in one go. Least work now; highest risk that a
  redraw is silently hidden in the meantime.

**Q2. The planet-atmosphere mod carries one 8K cloud image (about 43–170 MB of video memory) just for the world
map's look. Keep it?**
- (a) Keep it — the world map look is worth it.
- (b) Remove it now — the world map is frozen and painted once at the end anyway.
- (c) Measure first: we A/B load time and video memory, you look at both, then decide.

**Q3. Pawn faces come from a stack of seven facial-animation mods (~72 MB). Are faces part of "regenerate basically
all game art"?**
- (a) Yes — redraw faces too, inside the same animation system, with you approving each style change.
- (b) No — keep the current animated faces as they are; regen covers everything else.
- (c) Decide later, when the pawn/xenotype art pass comes up.
