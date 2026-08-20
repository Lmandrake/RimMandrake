# Stale-file audit — `observed/` and `world/`

**Date:** 2026-08-20 · **Scope:** `D:\Luke\dev\Rimworld\observed\` (1.1 GB) and
`D:\Luke\dev\Rimworld\world\` (92 MB) · **AUDIT ONLY — nothing was moved or deleted.**

---

## Totals

| | bytes | human |
|---|---:|---|
| **DELETE — pure cache, untracked, regenerable offline** | **1,026,665,073** | **~979 MiB** |
| **QUARANTINE — superseded, needs a 7-day dwell** | **75,007,336** | **~72 MiB** |
| **TOTAL working-tree reclaim** | **1,101,672,409** | **~1.03 GiB** |
| *of which reclaimed from `.git` history* | **0** | — |

🔑 **The headline finding is that the repo is not the problem — the disk is.**
Every byte in the DELETE column is already `.gitignore`d and was never committed;
`.git` is 287 MB and none of it comes from the 979 MiB pile. The project's own
"do not commit derived artifacts" rule has been **followed**, and `.gitignore`
lines 98–195 document each cache and name its generator. This audit mostly
confirms that policy and proposes collecting on it.

🔴 **One real committed-bulk finding, and it cannot be undone:** three savegames
totalling **39,510,182 bytes** are tracked in `world/` despite the blanket `*.rws`
rule — they predate it, and `.gitignore` never un-tracks. Removing them frees disk
only. Do not add another `.rws`.

---

## Table, ranked by bytes reclaimed

| path | size | tracked? | regenerable by | referenced by | verdict | why |
|---|---:|---|---|---|---|---|
| `D:\Luke\dev\Rimworld\observed\inventory\bundle_textures\` *(payload only — 20,394 PNGs, excludes `index.csv` + `manifest.json`)* | 505,428,739 | **no** (ignored, `.gitignore:187`) | `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\extract_bundle_textures.py` — offline, needs the UnityPy venv, slow | generator; `skills\reading-rimworld-graphics\SKILL.md` | **DELETE** | Extracted copies of textures that already exist in the game install; the generator does incremental re-extract from `manifest.json`. |
| `D:\Luke\dev\Rimworld\observed\genome\art_cache\` *(14,150 PNGs)* | 339,917,285 | **no** (ignored, `.gitignore:193`) | `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\genome_art_cache.py` — offline, UnityPy venv | `genome_matrix_build.py`, `gen_xenotype_contact_sheet.py` | **DELETE** | Same class as above: re-extractable gene/xenotype icons. `.gitignore` calls it out by name and by size. |
| `D:\Luke\dev\Rimworld\observed\inventory\sheets_buildings\` | 64,663,693 | **no** | `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\thing_contact_sheet.py` | `cherrypick_review.py` | **DELETE** | Contact sheets exist to be **looked at once**; the outcome is already captured in `decisions_buildings.json`, which is tracked. |
| `D:\Luke\dev\Rimworld\observed\inventory\sheets_items\` | 25,164,348 | **no** | `thing_contact_sheet.py` | `cherrypick_review.py` | **DELETE** | Distilled into `decisions_items.json`. |
| `D:\Luke\dev\Rimworld\observed\2026-08-13\inventory\` | 21,922,428 | **no** (ignored, `.gitignore:189`) | `animal_inventory.py` + `animal_contact_sheet.py` | *(nothing — `STRUCTURE.md:136` names the sibling `dumps\`, not this)* | **DELETE** | **Superseded duplicate run.** `GENERATED_FROM.json` says 575 mods / 1,178 animal rows; the live `observed\inventory\` copy has 1,240. Older census, same tool, no citation. |
| `D:\Luke\dev\Rimworld\observed\inventory\sheets_animals\` | 18,755,022 | **no** | `animal_contact_sheet.py` | `cherrypick_review.py` | **DELETE** | **Also a near-duplicate:** byte-for-byte within a few bytes of the loose `animal_sheet_*.png` one directory up, generated 43 minutes apart on 2026-08-15. |
| `D:\Luke\dev\Rimworld\observed\inventory\animal_sheet_01..10.png` + `animal_sheet_index.csv` | 18,351,216 | **no** | `animal_contact_sheet.py` | `Utils\README.md` | **DELETE** | The newer of the duplicate pair above. Both copies are cache; keep neither. |
| `D:\Luke\dev\Rimworld\world\WORLDMAP_source.rws` | 14,207,047 | **YES** | none — a captured savegame | `design\Jawa\worldbuilding\worldgen_interactive_def.md`; `skills\rimworld-world-editing\references\generating-a-world.md` | **QUARANTINE** | Superseded: the Ash'karr memory and `ASHKARR_WORLD_DEFINITION.md` state the `.rws` files are "the old automated-worldgen mess and are NOT sources". Tracked ⇒ frees disk only. |
| `D:\Luke\dev\Rimworld\world\WORLDMAP_gen.rws` | 14,178,821 | **YES** | none | `worldgen_interactive_def.md:21,715` cites it as **the measured artifact** (21,872 tiles, "verified by loading it") | **QUARANTINE** | ⚠️ Not a DELETE. A design doc cites this file as the evidence behind a measurement. Quarantine only, and fix the citation before the dwell expires. |
| `D:\Luke\dev\Rimworld\world\WORLDMAP_gen.rws.bak` | 14,175,759 | **no** | none | *(nothing)* | **QUARANTINE** | Ad-hoc backup taken 8 minutes before the `.rws` it shadows (08:07 vs 08:15, 2026-08-18). Unreferenced, untracked. **The only entry here that is genuinely new bytes off the disk.** |
| `D:\Luke\dev\Rimworld\world\WORLDMAP_sub7b_source.rws` | 11,124,314 | **YES** | none | `Utils\worldview.py`, queue `BUILD.md`, `CHECK_CLOSED.md` | **QUARANTINE** | Superseded world. It is the provenance of `world_tiles_sub7b.csv`, which is KEPT and is what actually matters. |
| `D:\Luke\dev\Rimworld\observed\inventory\sheets_apparel\` | 10,016,785 | **no** | `thing_contact_sheet.py` | `cherrypick_review.py`; `queue\DECIDE_ARCHIVE.md` | **DELETE** | Distilled into `decisions_apparel.json`. |
| `D:\Luke\dev\Rimworld\world\view\WORLDMAP_ashkarr_v2.*` *(6 files)* | 8,829,270 | **YES** | `Utils\worldview.py` | `the_one_map.md`, `ASHKARR_WORLD_DEFINITION.md` reference `world\view` generally, not these names | **QUARANTINE** | Renders of a superseded intermediate world. The current render set is `ASHKARR_WORLDMAP.*`. Tracked ⇒ disk only. |
| `D:\Luke\dev\Rimworld\observed\inventory\sheets_weapons\` | 9,061,767 | **no** | `thing_contact_sheet.py` | `cherrypick_review.py`; `queue\DECIDE_ARCHIVE.md` | **DELETE** | Distilled into `decisions_weapons.json`. |
| `D:\Luke\dev\Rimworld\observed\inventory\sheets_plants\` | 6,724,902 | **no** | `thing_contact_sheet.py` | `cherrypick_review.py` | **DELETE** | Distilled into `decisions_plants.json`. |
| `D:\Luke\dev\Rimworld\world\view\WORLDMAP_ashkarr.*` *(6 files)* | 6,367,460 | **YES** | `worldview.py` | as above | **QUARANTINE** | v1 renders, superseded twice over. |
| `D:\Luke\dev\Rimworld\world\view\WORLDMAP_sub7b_source.*` *(3 files)* | 6,124,665 | **YES** | `worldview.py` | as above | **QUARANTINE** | Renders of a superseded savegame. |
| `D:\Luke\dev\Rimworld\observed\inventory\*.csv` *(animals, biome_animals, patch_watch, animal_attacks, animal_lifestages, conflicts)* | 4,562,172 | **no** | `Utils\animal_inventory.py` — offline, seconds | `skills\rimworld-content-moderation\SKILL.md`, `def_inventory.py`, `Utils\README.md` | **DELETE** | Referenced **by name in tooling**, but as an output path, not as cited evidence. `refresh.py --offline` rebuilds them in seconds. |
| `D:\Luke\dev\Rimworld\observed\2026-08-15\Player.log.pre-worldgen` | 1,225,436 | **no** (ignored, `.gitignore:164`) | **none — unreproducible** | *(nothing)* | **DELETE** | `.gitignore`'s own doctrine: a harvested log's "value expires once the findings are extracted". 5 days old, zero citations. ⚠️ Genuinely unrecoverable — see Ambiguous #3. |
| `D:\Luke\dev\Rimworld\world\{biomes,hydro,relief,settle,discmap_520}.npz` | 871,280 | **no** | `world_relief.py` → `world_hydro.py` → `world_biomes.py` → `world_settle.py`, a strict offline chain | only the next stage of that chain | **DELETE** | Textbook intermediate cache. `ashkarr_paint.py` recomputes its own relief rather than loading these. `discmap_520.npz` has no reader at all. |

### KEEP — and why

| path | size | tracked? | why it stays |
|---|---:|---|---|
| `D:\Luke\dev\Rimworld\observed\w3\` *(10 PNGs)* | 46,274,798 | **YES** | 🔴 **Freshest evidence in the repo — written 2026-08-19, 20:43–22:22, hours before this audit.** Bridge screenshots from `prove_prefabs.py`, `prove_buildings.py`, `prove_map_grids.py` etc., seven of them cited as evidence in `infrastructure\state\queue\CHECK.md`. Not stale by any measure. |
| `D:\Luke\dev\Rimworld\world\view\ASHKARR_WORLDMAP.*` *(5 files)* | 11,637,917 | **YES** | The render of **the one map**. `the_one_map.md` says to judge the world by looking at this. |
| `D:\Luke\dev\Rimworld\observed\resource_watch\` | 5,570,017 | no (ignored) | 🔴 **LIVE.** `.watcher.lock` present; both `watch_*.csv` were appended to at **2026-08-20 00:04**. A running process owns these files. Do not touch. |
| `D:\Luke\dev\Rimworld\observed\2026-08-13\dumps\` | 5,296,262 | **YES** | `infrastructure\STRUCTURE.md:136` calls it *"the current generated-data home, not a snapshot"*. The date in the path is misleading — this is live. |
| `D:\Luke\dev\Rimworld\world\world_tiles_sub7b.csv` · `world_neighbors_sub7b.csv` · `world_tiles_lada.csv` | 3,897,285 | **YES** | ⚠️ **Requires a running game on the bridge to reproduce** (`jawa/world_tile_export`, `JawaBenchTerrainTools.cs`). `ASHKARR_WORLD_DEFINITION.md:20` and `the_one_map.md:171` name them as the tile-geometry engine truth. Expensive and load-bearing. |
| `D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv` + `_settlements` `_links` `_meta` | 1,819,682 | **YES** | ⭐ **THE MAP.** `ASHKARR_WORLD_DEFINITION.md:284`. |
| `D:\Luke\dev\Rimworld\world\live_tiles_check.csv` | 1,342,873 | **no** | ⚠️ **Kept precisely because it is cited evidence of a measurement.** `queue\DECIDE_ARCHIVE.md:496` cites it for "reads back 21,872 tiles, zero blank biome cells". It is a bridge read-back — **regenerating it needs the game up**, so this is not a cheap cache. Untracked, so it is also the only copy. **Recommend tracking it** rather than removing it. |
| `D:\Luke\dev\Rimworld\observed\inventory\bundle_textures\index.csv` + `manifest.json` | 8,306,005 | no (ignored) | ⚠️ **Kept as cited evidence.** `design\Jawa\worldbuilding\ANCIENTS_AS_RAKATA_SPEC.md:403` cites `index.csv` as the extracted-bundle index. `manifest.json` is what makes re-extraction incremental. This is the *provenance* the project's rule says to keep when the *bulk* goes. |
| `D:\Luke\dev\Rimworld\observed\genome\scan_manifest.json` | 178 | **no** ⚠️ | Provenance for the whole genome scan (576 mods, 1,857 genes, 42,963 textures). See Finding A. |
| `D:\Luke\dev\Rimworld\observed\inventory\decisions_*.json` *(7)* | 154,089 | **YES** | The owner's hand-made keep/cut calls. Not regenerable by any machine. See Finding B. |
| `D:\Luke\dev\Rimworld\world\world_graph.npz` | 472,291 | **YES** | Tracked cache, cited as evidence in `queue\CHECK.md`. Removing it saves nothing in git; leave it. |

---

## Findings that are not about bytes

**A. `.gitignore` claims `scan_manifest.json` is tracked. It is not.**
Line 127 says *"scan_manifest.json IS tracked: it is the provenance … for the register
the scan produces."* But line 193's `observed/genome/` swallows the whole directory,
and `git check-ignore` confirms the manifest is ignored. `git ls-files observed/genome/`
returns **zero** files. ⇒ **Deleting `art_cache/` today destroys the only record of what
mod set produced it.** The intended negation was never written. Fix before any cleanup:

```
observed/genome/*
!observed/genome/scan_manifest.json
```

The same gap exists for `observed/2026-08-13/inventory/GENERATED_FROM.json` (the 575-mod
provenance stamp), swallowed by line 189 — which is how I could tell that directory was a
superseded run, and it would have gone with it.

**B. The seven `decisions_*.json` exist twice, byte-identical.**
`D:\Luke\dev\Rimworld\observed\inventory\` and `D:\Luke\dev\Rimworld\deployed\decisions\`
hold identical copies of all seven (155 KB total — trivial size, real hazard). These are
the one thing here **no machine can regenerate**. Two copies with no stated primary will
drift. Not a delete candidate; flagged for someone to name the authoritative one.

**C. `observed/` has no README, but `.gitignore` cites one.**
Lines 101 and 143 both refer readers to `observed/README.md` for the full policy
statement. `find` shows no `.md` at any depth in `observed/`. The doctrine those rules
lean on is not written down anywhere the reader is sent.

---

## What I could NOT determine

1. **Whether `worldview.py` can still re-render the quarantined worlds.** It needs a def
   dump from the *same mod set* as the `.rws`; a stale dump makes the picture lie. I did
   not verify a matching dump still exists, so I have treated those renders as
   **not cheaply regenerable** and recommended quarantine rather than deletion.
2. **Which of the duplicate animal-sheet pairs is authoritative** — `sheets_animals\` (06:20)
   vs the loose PNGs (07:03), both 2026-08-15, differing by a handful of bytes. Both are
   cache, so the answer does not change the verdict, but if only one is to go, it is a
   coin-flip on this evidence.
3. **Whether `Player.log.pre-worldgen` still holds an unextracted finding.** It is
   unreferenced and unreproducible — a genuinely irreversible delete. The project's own
   rule says a harvested log's value expires, but that assumes someone harvested it. I
   could not confirm anyone did. **Treat as QUARANTINE if that assumption is not solid.**
4. **Whether the `worldgen_interactive_def.md` citation of `WORLDMAP_gen.rws` is still
   live doctrine or archived history.** The Ash'karr memory says the `.rws` files are not
   sources; the design doc cites one as measured evidence. These disagree, and the
   disagreement is why that file is QUARANTINE and not DELETE.

---

## Suggested order of operations

1. Fix the two `.gitignore` provenance negations (Finding A) — **before** anything moves.
2. Delete the cache tier: `bundle_textures/` payload, `genome/art_cache/`, the six
   `sheets_*/`, the loose sheets and CSVs, the `2026-08-13/inventory/` duplicate run, the
   five `.npz`. ≈ **979 MiB**, all untracked, all named by a generator in `.gitignore`.
3. `git mv` the QUARANTINE tier into `D:\Luke\dev\Rimworld\infrastructure\disposing\`
   for the 7-day dwell. Note the `.bak` is untracked, so it needs a plain move.
4. Track `world/live_tiles_check.csv` — it is cited evidence that costs a game load to
   remake and currently exists in exactly one untracked copy.
5. Leave `observed/w3/` and `observed/resource_watch/` alone.
