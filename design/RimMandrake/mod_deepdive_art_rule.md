# Deep dive: how far does "no donor art kept" reach? (mod audit card C17)

*FOUNDRY, 2026-10-10. Owner order, by card ("Study first"): work out what each reading of the rule costs
before deciding how far it reaches. Offline only: no bridge, no game, no game-code edits, no mod removed.
Owner question C17 is in `design/RimMandrake/mod_audit/GPT_PACKAGE.md` and `OWNER_CARDS.md`.*

## 1. The ruling being scoped

- **2026-10-05, owner, typed** (memory note `no-donor-art-kept`; quoted in `mod_audit/SCENARIO_BRIEF.md` §2):
  *"any remaining MLIE, donor, alpha animals, alpha biomes, etc. art MUST be regenerated at least once for me
  tonight and wired into the sheets, ok? I don't want to review donor art. We're not keeping any."* Same day:
  *"I DO want to see donor art in "past art" so I can see where something came from though, please. I just
  don't want it to be all there is."*
- **Same night, by question card:** vanilla Core/DLC art counts as donor too ("Replace vanilla too"). Every
  vanilla-only **row on a review sheet** also gets a render of ours.
- **2026-10-03, owner, typed** (`design/RimMandrake/sound_sourcing_options_2026-10-02.md` line 3): *vanilla
  sounds ship as final for now, no retuning; sound work has not started.*

Both art rulings were made **about biome review sheets** (creature, plant and terrain rows from the donor mods
being ported). C17 asks whether the rule also covers sound, interface art, and the apparel and furniture of mods
we keep because of what they do.

## 2. Method and instruments

All counts below are MEASURED by parsing. The scripts are in `/home/mandrake/.seat-tmp/artrule/`, which is
throwaway; ticket `DONOR_ART_BUILD_REFS_INSTRUMENT` (§9) moves them into the repo.

1. **Asset index** (`scan_assets.py`). For each of the **551** mods on
   `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`, it lists every image under `Textures/` and every
   clip under `Sounds/`, in each resolved content folder, with its size on disk and its PNG/DDS header size.
   It found **47,202** distinct texture paths and **2,007** distinct sound paths.
2. **Reference scan** (`scan_refs.py`). It builds `def_inventory`'s DefSet over the same list, with inheritance
   resolved: **55,882** def records. It skips abstract defs and the **1,253** defs that the live Cherry Picker
   list cuts. It then walks every resolved def for texture-path fields (`texPath`, `*TexPath`, `*IconPath`,
   `*GraphicPath`, and `<li>` items under them) and for SoundDef `clipPath`/`clipFolderPath`. It also reads path
   values out of every `Patches/` XML.
3. **Resolution follows the engine** (RimSage, `ContentFinder<T>.Get`): mods are searched from the **last loaded
   to the first**, the first loose file found wins, then the base game's own `resources`, and only then any
   mod's AssetBundles. A referenced path matches a file exactly, as a `Graphic_Multi`/apparel facing
   (`_north/_south/_east/_west`, body-type infixes, the `m` mask suffix), or as a folder (`Graphic_Random`,
   `StackCount`). The **owner** of an asset is the mod whose file wins.
4. **Unit.** An *asset* is one referenced graphic path, which is what one review row and one redraw subject are.
   A *file* is one image (one facing or one mask) and is roughly one artpipe job.
5. **Category** comes from the referencing def and the field: any `*Icon*` field or `UI/` path counts as
   **interface**; otherwise the def decides. Race → creatures; `<apparel>` → apparel; `Plant`, `Building` and
   `Item` → plants, buildings_furniture and items_weapons; `ThingStyleDef` → ideology_styles; genes,
   facial-animation and render-tree defs → pawn_looks; motes, flecks, weather and projectiles → effects; terrain;
   vehicle and ship sprites. **Patched_in** is a path that only a patch names.
6. **Decision** is the owning mod's `final_decision` in `mod_audit/MASTER_REGISTRY.csv`. When several donor mods
   own one asset's files, the most durable decision wins (KEEP before PHASE-OUT before ELIMINATE).
7. **Decoded MB** is a labelled ESTIMATE: w × h × 4 × 1.33 for mips, the same proxy `diskfacts.py` uses. It is
   upper-ish, because the game compresses some textures.

**Sanity probes (all pass):**

- `Things/Item/Resource/Chemfuel` resolves to no mod file, so it counts as vanilla.
- Alpha Animals' `AA_Eyeling` resolves to `sarg.alphaanimals` (3 files).
- `AA_Atispec` resolves to **ours**: `mandrake.rsw.patches` loads after Alpha Animals and overrides the file by
  path.
- Space Base Furniture measures **477 MB** decoded, matching the "~500 MB" in the brief.
- Ambience's 23 clips resolve through its `AR_Waves` SoundDef.

**Instrument defect found on the way (ticket `LOADSET_FIX_OLDER_VERSION_FALLBACK`).** For a mod with no
`LoadFolders.xml` and no `1.6/` folder, the engine (`ModContentPack.InitLoadFolders`, RimSage) loads the newest
**older** version folder. `rimworld_loadset.resolve_load_folders` does not, although its own comment says the
engine does. Four mods on the list are invisible to `def_inventory` and `defscan` because of it:
`adaptive.simplestorage`, `adaptive.primitivestorage`, `adaptive.ideology.storage` and `mewn.medievalsigns`. The
mod audit therefore records **def_total 0** for the three Adaptive Storage model packs, which is wrong: they
declare their models in `1.5/Defs`. This study patches the resolver at runtime (`fixload.py`). The shared tool
is unchanged.

**Limits.**

- Paths that C# code loads (through `ContentFinder` or `[StaticConstructorOnStartup]`) are not def-referenced.
  They are reported separately as "not referenced by any def".
- Art inside AssetBundles cannot be resolved per path, and **a path that matches no loose file is counted under
  "vanilla"**. That column therefore also absorbs donor bundle art and some non-texture paths (review §10, F1).
  Donor bundles total about 150 MB across 13 mods. Outland Genetics is KEEP; the rest (Outer Rim, Star Wars
  Animal Collection, Horrors) are mostly PHASE-OUT.
- Single-graphic masks named `_m` (`Graphic_Single.MaskSuffix`) are not matched, so **391** donor mask files are
  uncounted: KEEP 187, PHASE-OUT 196, ELIMINATE 8.
- Paths are lowercased, but the engine's lookup is case-sensitive. A mis-cased texPath that the game fails on
  counts here as resolved. The effect is unmeasured.
- An asset is counted when its def is loaded and not cut. Whether a player actually meets every such def is not
  measured, so "reachable" here is an upper bound.

## 3. Measured: donor assets referenced by defs on the 551 list, by category

**Donor texture assets, split by the decision on the mod that owns the file.** The ours and vanilla columns
count assets of every kind for comparison.

| category | KEEP | PHASE-OUT | ELIMINATE | donor total | files | disk MB | decoded MB (est) | resolves to a file in our mod | no loose file (vanilla, bundle or non-texture; §10 F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **interface** (icons, UI) | 1,130 | 1,471 | 164 | 2,765 | 2,829 | 83 | 872 | 309 | 1,642 |
| apparel | 98 | 66 | 3 | 167 | 893 | 13 | 249 | 264 | 170 |
| buildings_furniture | 988 | 1,730 | 307 | 3,025 | 7,610 | 218 | 5,862 | 325 | 1,092 |
| creatures | 98 | 867 | 26 | 991 | 2,494 | 34 | 928 | 884 | 677 |
| effects | 185 | 329 | 20 | 534 | 922 | 24 | 480 | 147 | 483 |
| ideology_styles | 16 | 1,564 | 1 | 1,581 | 3,582 | 29 | 962 | 25 | 123 |
| items_weapons | 463 | 379 | 41 | 883 | 1,517 | 19 | 384 | 693 | 361 |
| pawn_looks | 308 | 443 | 11 | 762 | 3,032 | 23 | 2,720 | 198 | 456 |
| plants | 41 | 287 | 0 | 328 | 963 | 17 | 125 | 345 | 244 |
| terrain | 28 | 407 | 0 | 435 | 435 | 451 | 1,846 | 25 | 181 |
| vehicles_ships | 57 | 3 | 0 | 60 | 60 | 6 | 61 | 0 | 15 |
| other | 5 | 11 | 0 | 16 | 95 | 14 | 782 | 0 | 3 |
| patched_in | 95 | 230 | 13 | 338 | 844 | 13 | 409 | 108 | 159 |
| **total** | **3,512** | **7,787** | **586** | **11,885** | **25,276** | **945** | **15,682** | **3,323** | **5,607** |

**Corrected vanilla figure (§10, F1).** Of the 5,607 paths with no loose file:

- About **1,295** are donor AssetBundle art (`outerrim/`, `outland/`, `swanimals/`, …). **390** of those are on
  KEEP mods, mostly `neronix17.outland.genetics`: 268 world-visible and 122 interface.
- **280** are not textures at all: RulePack name files and shader paths.
- **Firm vanilla**, meaning a Core/DLC def references the path, is **3,259**: world 2,345, interface 914, biome
  look 611.

The true vanilla count is between **3,259 and ~4,030**. Every vanilla figure below uses that corrected range.

**Grouped the way C17 asks** (KEEP world-visible and interface are loose-file counts; add ~268 and ~122 for KEEP
bundle art):

| bucket | KEEP | PHASE-OUT | ELIMINATE |
|---|---|---|---|
| world-visible art (every row above except interface) | **2,382 assets / 5,537 files / ~3.5 GB est** | 6,316 / 15,837 / ~10.3 GB | 422 / 1,073 / ~1.0 GB |
| interface art | **1,130 / 1,178 / ~0.36 GB** | 1,471 / 1,485 / ~0.48 GB | 164 / 166 / ~0.04 GB |
| "biome look" (creatures + plants + terrain) | 167 / 416 / ~0.38 GB | 1,561 / 3,391 / ~2.5 GB | 26 / 85 |

**Sound.** Donor clip files that resolve through SoundDefs or patches:

| decision | files | MB | of which another def or patch references the SoundDef |
|---|---:|---:|---:|
| KEEP | 250 | 36.1 | 149 |
| PHASE-OUT | 443 | 94.6 | 345 |
| ELIMINATE | 122 | 7.1 | 97 |

- The remaining clips are played from C#.
- Donor clips that no SoundDef names (code-played or dead): KEEP 32, PHASE-OUT 41, ELIMINATE 43.
- **1,330** clip references across 1,443 SoundDefs match no loose clip. They are mostly vanilla, but bundle clips
  such as Realistic Human Sounds land here too.
- The largest KEEP sound mods: Lightsabers 36, Vanilla Vehicles Expanded 35, VFE Pirates 20, Alpha Mechs 16,
  Dubs Bad Hygiene Lite 13, Darkest Dungeon incident sounds 11, VFE Factory 11, VE Gravship 11, Spaceports 11,
  Melee Animation 11.
- Realistic Human Sounds (`mlie.realistichumansounds`, KEEP) ships its 10 MB in an AssetBundle, so it is not in
  the clip counts.

**Donor files on disk that no def references** (code-loaded or dead):

| | KEEP | PHASE-OUT | ELIMINATE |
|---|---:|---:|---:|
| non-UI textures | 2,898 | 7,953 | 601 |
| `UI/` textures | 767 | 859 | 55 |

`vesper.egihologramsandprojectors` alone holds 2,487 of the non-UI files.

**The C17 mods by name:**

| mod | decision | what the player sees | measured |
|---|---|---|---|
| Ambience `swablu.ambience` | PHASE-OUT | wave and wind beds | 23 clips via `AR_Waves` (2.0 MB) + 14 code-played; no art |
| Metal Pipe `flangopink.metalpipe` (+ Horseshoe) | ELIMINATE | the clang; pipe items | 2 clips; 4 item textures |
| meme tantrum sounds `kshtantrumsounds.mod` | ELIMINATE | sounds | 13 clips |
| Monty Python melee sounds `bonible.medievalmeleesounds` | ELIMINATE | melee sounds | 48 clips (all patched onto existing SoundDefs) + 17 unreferenced |
| Rust Chrome `mandrake.rm.rustchrome` (ours) | not on the 551 list (`OURS_ABSENT_INSTALLED`) | a recolour of vanilla UI | 14 PNGs under `Textures/UI/Widgets/` that override vanilla UI paths by load order |
| Slave Outfits `usgiyi.slaveoutfits` | KEEP | worn apparel | 9 apparel assets / 108 files / ~33 MB |
| Space Base Furniture `mingtuwuxiang.spacebasedecorative` | KEEP | furniture, decor, 3 floors | 102 assets (82 furniture, 17 icons, 3 terrain) / 435 files / ~477 MB |
| Adaptive Storage model packs `adaptive.simplestorage`, `.primitivestorage`, `.ideology.storage` | PHASE-OUT | shelves and crates that fill as they stock | 42 + 42 + 146 assets (168 storage models + 62 icons) / 374 files / ~246 MB; the framework itself has none |
| Roots of RimWorld `ghost.rootsofrimworld` | PHASE-OUT | tribal decor | 33 assets / 79 files / ~53 MB |

## 4. Already replaced by ours

- **Path overrides.** 27 referenced assets resolve to our file while a donor mod also ships that path: 22
  furniture, 3 creatures, 1 effect, 1 item. Example: `mandrake.rsw.patches` overriding Alpha Animals sprites.
- **Assets whose winning file sits in one of our mods:** 3,323, against 11,885 donor assets. Creatures 884,
  plants 345, items 693, furniture 325. **This is not "our art".** In at least **337** of the 3,323, every file
  matches a donor file on byte size and dimensions: a port that copied the donor image (creatures 86, items 92,
  interface 76, apparel 36).
- **Art ledger** (`art.py index`, 2026-10-10): 5,322 texture slots of ours.
  - **720** slots hold both a donor variant and a repo copy. **661** of those copies are the donor image itself:
    649 are sha-identical and 12 are phash-identical. **Only 59 differ.** None of the 720 has an artpipe
    variant.
  - **374** slots have only a donor variant.
  - So ports have mostly **moved** donor art into our mods, not replaced it.
  - The ledger records 6,061 artpipe renders.
- **Our defs that borrow other people's art:** 54 assets point at donor art (terrain 14, pawn looks 12,
  creatures 9) and **~460** at vanilla, mostly interface icons (213). Ticket `BORROWED_ART_CENSUS_OUR_DEFS`
  lists them.

## 5. Cost per asset type

**The pipeline, measured from `D:\ClaudeWork\rimmandrake\artpipe\throughput.jsonl`.**

- A job's median is **99 s**, with a p90 of 130 s.
- 5,856 of 7,994 jobs came back ok (73%), so it takes about **1.37 jobs per accepted image**.
- The last 7.5 days produced **3,220 ok images on 8 Codex workers, about 430 a day**. The daily peak is 665.
- A job uses about **0.24%** of its worker's weekly Codex meter. The meters were at 99% and "grumpy" today.
- Owner redos after review are not measured here. A **×1.25** allowance is an ASSUMPTION.

So one image costs about 1.7 jobs, and one asset costs files-per-asset × 1.7 jobs.

**Files per asset, measured from §3:**

- interface 1.0
- terrain 1.0
- effects 1.7
- items 1.7
- buildings and furniture 2.5
- creatures 2.5
- plants 2.9
- pawn looks 4.0
- apparel 5.3 (every body type × 3 facings)

**What the machine cannot do yet:**

- **Sound.** There is no sound pipeline. Sound work has not started (the 2026-10-03 ruling).
  `D:\Luke\dev\MandrakeAudio\` holds 23.5 GB of Sonniss GDC2024 audio, not yet extracted. Every clip would be
  sourced and edited by hand.
- **The binding constraint is the owner's review time, not the pipeline.** Under the 2026-10-05 ruling every
  replaced asset is a sheet row he looks at, and biome sittings are one biome at a time.

**Memory, which the rule does not save.** RimWorld loads **every** texture under every active mod's
`Textures/` at startup, referenced or not (`ModContentHolder.ReloadAll`, RimSage). So:

1. Redrawing a kept mod's art by **overriding its paths from a later mod leaves the donor's files loaded too**.
   Memory rises by the size of our renders. Our renders are often 512 px or more against donor art of 128 to
   256 px.
2. Memory falls only when the donor's files leave the folder: the mod is cut, forked, or its textures are
   replaced in a copy we ship ourselves. A fork needs a licence or the author's permission, which is a separate
   question.
3. The real VRAM cost is still a header proxy. `HEAVY_TEXTURES_MEASURE_REAL_VRAM` (already filed in
   `mod_audit/ACTIONS_NOW.md`) is the measurement.

## 6. Dependencies: donor art on mods we keep for what they do

There are **102 KEEP mods** with donor art that defs reference. Ranked by estimated decoded MB, the top 20 are:

- `mingtuwuxiang.spacebasedecorative` 435 files / ~477 MB
- `biomesteam.biomesfossils` 254 / ~462
- `redmattis.bigsmall.core` 627 / ~312 (genes, heads and icons)
- `vanillaexpanded.gravship` 384 / ~309
- `oskarpotocki.vanillavehiclesexpanded` 223 / ~273
- `sarg.alphamechs` 521 / ~180
- `vanillaexpanded.vfefactory` 154 / ~163
- `cp.uncle.boris.used.furniture` 157 / ~152
- `lee.theforce.lightsaber` 180 / ~121
- `lazyfridaystudio.genesexpandedeyes` 456 / ~108
- `sbz.neatstoragefridge` 83 / ~108
- `oskarpotocki.vfe.pirates` 286 / ~102
- `sbz.gravshipstorage` 99 / ~98
- `xmb.ancientminingindustry.mo` 93 / ~95
- `gmmp.dungeon` 143 / ~82
- `dubwise.rimefeller` 50 / ~65
- `aoba.fortress.industrial` 90 / ~61
- `redmattis.betterprerequisites` 44 / ~53
- `co.uk.epicguru.meleeanimation` 4 / ~45
- `meathax.showmeyourtools` 119 / ~43

These are what any reading wider than "the biome look" lands on. Redrawing their art works only by path override
(§5: it adds memory and breaks when the author moves a path) or by a fork. And the mods are kept for code that
we are not replacing.

**PHASE-OUT art (6,316 world-visible assets) is owed under every reading, and it is not paid.** It is not an
*extra* cost of a wider reading, because it leaves or is ported whatever is decided (C01 "port everything").
But ports have so far copied donor bytes (§4: 661 of 720 slots), and the 2026-10-05 ruling still requires them
redrawn. For the biome look alone that is 1,561 assets / 3,391 files, about **5,800 jobs or ~10 pipeline days**.
ELIMINATE art (586 assets) leaves with the cut.

## 7. Candidate readings

The jobs figure is files × 1.37 × 1.25. Days are files × 1.25 ÷ ~430 accepted images a day, with no other art
queued. Owner review is in assets, one row each. All readings sit **on top of** the ~10 days of PHASE-OUT
biome-look redraws that every reading owes (§6).

| | Reading | extra donor art to replace (KEEP mods) | + vanilla, if it counts | jobs / pipeline days | owner review rows | what the player sees |
|---|---|---|---|---|---|---|
| **1** | **Biome look only**: creatures, plants and terrain, which is what the 2026-10-05 words were about | 167 assets / 416 images | ~611 firm-vanilla biome-look paths, only as rows on our biome sheets (already ruled) | ~710 / ~1.2 d | 167 | every animal, plant and floor of the world in our register; kept mods' furniture, apparel, mechs, icons and sounds as their authors made them |
| **2** | **Everything the player sees in the world** (C17 option A): reading 1 + furniture, apparel, items, effects, pawn looks, vehicles and ideology styles | 2,382 assets / 5,537 images (+~268 bundle assets, Outland Genetics) | 2,345 to ~2,900 vanilla world paths (~5,900 to 7,300 images, est. at 2.5 per path) | ~9,500 / ~16 d (+~10,000 to 12,500 / ~17 to 21 d with vanilla) | ~2,650 (+2,345 or more) | a world wholly in our register; vanilla-standard menus and sounds |
| **3** | **2 + interface art** | +1,130 assets / 1,178 images + 767 code-loaded UI files (+~122 bundle icons) | +914 to ~1,130 vanilla interface paths | +~3,300 / +~5.7 d | +~1,250 | the same, plus our icons (the vanilla widget frame needs Rust Chrome back on the list; it is not on it today) |
| **4** | **Everything, sound included** (C17 option B) | 3 + 250 kept-mod clips (+32 code-played) | +1,330 vanilla clip references | art as in 3; sound has **no pipeline**, so every clip is hand-sourced | +250 listens | it contradicts the 2026-10-03 "vanilla sounds ship as final" ruling |

**Risks, by reading.**

- **Reading 1.** Almost nothing new: the port programme already pays for it. Its risk is that kept-mod furniture
  sits beside our painterly creatures in a visibly different style.
- **Readings 2 and 3.**
  1. They pay to redraw art inside mods we keep for function. A path override keeps the donor's files loaded, so
     **memory rises** (§5), and it breaks silently when an author renames a path. A patch that matches nothing
     logs nothing.
  2. They add 2,400 to 3,500 review rows to a review queue that is already the bottleneck.
  3. Space Base Furniture alone is 102 rows and ~477 MB.
- **The vanilla clause** adds about as much again as reading 2's donor art. It was ruled by card for **sheet rows**, not for the
  game at large, and widening it is the owner's call (`VANILLA_ART_DECIDE_REACH`).
- **Reading 4.** No sound tooling exists, and it reverses a standing typed ruling.

## 8. Recommendation

**Reading 1 now, and Reading 2 as an ordered backlog, not a gate. Interface and sound stay out. Vanilla stays
limited to sheet rows.** This is **narrower than C17's option A**, which would redraw kept mods' apparel and
furniture "as for any donor", meaning reading 2 in full. The narrowing is deliberate, for the reasons below.

- The rule's purpose, in the owner's own words, is that he never again reviews donor art as the final look of
  **our** content. Reading 1 covers every row he will ever see on a biome sheet, and it costs only 167 more
  assets (~1.2 pipeline days). The other 1,561 biome-look assets on PHASE-OUT mods are owed anyway, about 10
  days (§6). Ports have so far mostly copied donor images, so that debt is real, and it comes first.
- World-visible art on kept mods (2,382 assets) is real but expensive. It also brings no memory gain and has a
  silent-breakage mode. Take it **mod by mod, in decoded-MB and visibility order**, starting with Space Base
  Furniture, Biomes Fossils, VE Gravship and Vanilla Vehicles Expanded. When a mod comes up, decide whether to
  redraw it by override, fork it, or cut it, rather than redrawing all 2,382 by sweep. The Adaptive Storage packs
  and Roots of RimWorld are PHASE-OUT, so they follow the port programme. Slave Outfits (9 assets) is cheap enough
  to redraw in the first apparel wave.
- **Interface (1,130 assets plus 767 code-loaded files) and sound (250 clips plus code-played) stay out.**
  Leaving interface out leaves vanilla's own frame unless Rust Chrome (`OURS_ABSENT_INSTALLED`) is put back on the
  list. That is a separate one-mod decision costing nothing new. Sound is under a standing "vanilla ships as final" ruling,
  with no pipeline behind it.
- The **off-tone** sound mods (Metal Pipe, meme tantrums, Monty Python melee) are already ELIMINATE under C19,
  so they leave without any reading of this rule.

This is a recommendation. The owner decides by card (`ART_RULE_DECIDE_REACH`).

## 9. Tickets (names pass `rimflow namecheck`; not filed)

| name | what |
|---|---|
| `ART_RULE_DECIDE_REACH` | owner card: readings 1 to 4 of §7, recommendation §8; record the answer in `mod_audit/OWNER_RULINGS.md` and the memory note |
| `VANILLA_ART_DECIDE_REACH` | owner card: does "vanilla counts as donor" stay limited to sheet rows (as ruled), or reach the 3,964 world and 1,643 interface vanilla paths in play? |
| `LOADSET_FIX_OLDER_VERSION_FALLBACK` | `rimworld_loadset.resolve_load_folders`: add the engine's newest-older-version-folder fallback (`ModContentPack.InitLoadFolders`) for mods with no `LoadFolders.xml` and no exact folder; then re-run `defscan.py` and `assemble.py`; the 3 Adaptive Storage packs and Medieval Signs read **def_total 0** today |
| `KEPT_MODS_REDRAW_WORLD_ART` | reading 2's backlog: per KEEP mod, in §6 order, choose override, fork or cut, then queue its world-visible art; opens with Space Base Furniture (102 assets) and Slave Outfits (9) |
| `BORROWED_ART_CENSUS_OUR_DEFS` | list the 54 donor-art and ~460 vanilla-art assets our own defs point at, **plus the 661 ledger slots and ≥337 assets whose "ours" file is a byte copy of donor art**, by mod, as input to the sheets |
| `DONOR_ART_BUILD_REFS_INSTRUMENT` | move `scan_assets.py`, `scan_refs.py` and `tables.py` into `src/RimMandrake/Utils/modaudit/` with a selftest and the sanity probes of §2, so these counts can be regenerated; while doing it, fix the review's method defects: match `_m` masks; drop RulePack and shader paths; classify unmatched paths as vanilla only when a Core/DLC def names them, otherwise as bundle; resolve case-sensitively; keep the first duplicate within a mod |

Memory is not a new ticket: `HEAVY_TEXTURES_MEASURE_REAL_VRAM` already exists.

## 10. Review disposition

A fresh-context Opus reviewer (2026-10-10) re-derived nine headline figures. Six matched exactly: the §3 totals;
KEEP world-visible and interface; Space Base Furniture; Slave Outfits and Roots; sound KEEP 250; Biomes Fossils
and the 102 KEEP mods. It found eight defects. All applied:

| # | finding | disposition |
|---|---|---|
| F1 | The "vanilla" column counted any path with no loose file. That included ~1,295 donor bundle paths (390 on KEEP mods) and 280 non-texture paths. Firm vanilla is 3,259. | **Applied.** Column relabelled; corrected range in §3 and §7. The instrument fix goes in `DONOR_ART_BUILD_REFS_INSTRUMENT`. |
| F2 | "719 slots superseded" was false: 661 of 720 "ours" copies are the donor image, and 59 differ | **Applied** (§4); it changes §6 and §8 |
| F3 | "ours" means "the winning file is in our mod", not our art; at least 337 are byte copies | **Applied** (§3 header, §4) |
| F4 | The Adaptive Storage breakdown said 68 storage models; the measured figure is 168 | **Applied** |
| F5 | §7 divided jobs by images per day; days were overstated by ~1.37× | **Applied** (§7, §8) |
| F6 | `_m` single-graphic masks were missed (391 donor files) | **Applied** as a stated limit in §2; scanner fix ticketed |
| F7 | The recommendation leaned on Rust Chrome, which is not on the list | **Applied** (§7 reading 3, §8) |
| F8 | "PHASE-OUT art is already paid by porting" was false given F2 | **Applied**: ~10 days owed under every reading (§6, §8) |
| N9 | The recommendation is narrower than C17 option A | **Applied**: §8 now says so |
| N10 | Case sensitivity, first-duplicate-wins within a mod, 169 double-counted file keys (25,276 references are 25,106 distinct files), decision precedence (1 mixed asset) | **Accepted as limits.** Case sensitivity is stated in §2. The others are below 1%. Instrument fix ticketed. |

The reviewer also checked and confirmed the memory claim: `ReloadAll` loads every file, and `ContentFinder`
searches last-loaded first, so an override leaves the donor's files loaded.
