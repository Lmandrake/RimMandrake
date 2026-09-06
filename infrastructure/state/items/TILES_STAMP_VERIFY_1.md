# TILES_STAMP_VERIFY_1

FOUNDRY investigation, 2026-09-06 (autonomous, owner AFK). Scope limit applied per
`frozen-artifacts` skill and CLAUDE.md: **only the owner re-freezes.** This is
investigation + read-only tooling. The stamp itself was NOT rewritten and the CSV's
tile data was NOT touched.

## 1. The "~1650-tile shrubland->Desert repaint" is NOT on disk — the filing's headline claim is wrong

Measured directly (git blob at the stamped commit vs current disk, per-tile join, not
aggregate counts):

- `world/ASHKARR_WORLDMAP_tiles.csv` currently: `AridShrubland` 748 rows, `Desert` 4151 rows.
- The exact snapshot the stamp (`sha256 65c7be19…`) describes is commit `0ccf44fe`
  (2026-08-23, *"HorrorWastes was two places 20C apart"* — confirmed by re-hashing
  `git show 0ccf44fe:world/ASHKARR_WORLDMAP_tiles.csv"`): `AridShrubland` 709,
  `Desert` 4648.
- Net change since the stamp: `AridShrubland` **+39**, `Desert` **-497** — the opposite
  direction from "shrubland repainted to Desert".
- Per-row transition count (tile-by-tile join, 4,264 rows changed biome in total):
  **`AridShrubland -> Desert` occurs on ZERO rows.** The only transition between the
  two is `Desert -> AridShrubland`, on **142** rows — again, backwards from the claim.

**Where the "~1650" and "shrubland->Desert" language actually comes from:**
`infrastructure/state/items/WORLDMAP_DESERT_BAND_REPAIR_1.md`, filed 2026-09-05, same
session as the recent biome-grammar/sun-angle-ladder work. It is a **ratified but
NOT YET EXECUTED** owner-approved plan ("AridShrubland folds in… net 1,590 tiles
retyped, 7.3% of the planet") to be applied in a *future bridge session*, and its
numbers are measured against `world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv` — a
`vivify_world.py` snapshot pulled from a live game load, **not** the frozen authored
CSV. Confirmed by direct comparison: that VIVIFIED snapshot's biome census
(AridShrubland 748 / Desert 4151) is byte-identical in counts to today's
`ASHKARR_WORLDMAP_tiles.csv` — i.e. it was captured from the *current, unrepainted*
world, one day after the CSV's last edit (2026-08-23 -> vivified 2026-08-24). The
retype `WORLDMAP_DESERT_BAND_REPAIR_1` describes has not landed anywhere yet.

⇒ **Whoever filed this item conflated two unrelated things**: a real, separate stamp
staleness on the frozen tiles CSV (explained in §2 below), and the pending
`WORLDMAP_DESERT_BAND_REPAIR_1` proposal's biome-count language, which describes a
change that has not happened to this file. There is no unexplained shrubland->Desert
repaint to account for.

## 2. What actually IS stale: 14 legitimate surgical-edit commits, never restamped

The freeze (`world/ASHKARR_WORLDMAP_tiles.csv.frozen.json`) was last correctly stamped
by commit `0ccf44fe` (2026-08-23, restamps CSV + marker together, 4-line diff to the
marker). Fourteen further commits touched the CSV that same day and none restamped:

```
e3eb2882 The nightside becomes layers: mycoid, then horror wastes, then alien chemistry
2e7f4377 Ocean depth is -350, not -30: vanilla's own constant, read out of a vanilla save
b4ded4f5 Damp becomes a hypersaline desiccated swamp, which is what its name always said
0e563f51 The Kiln pan: the great river now dies into a Danakil-style evaporite basin
0cbc3634 Jungle peters out to stormy savanna at the Kiln; 100 more stagnant rivulets
b5135747 The rot rule, keyed on distance from water: cypre banks, feralisk cores
12eae828 Fever Wood becomes the wet place: swamps, fester, and 11 islands in the Twilight
0572c6ef Dew Belt / Dew Horn: the stranded feralisk cluster goes, the savanna skirt thins
5b73a31e Dew Horn becomes badlands: the trapped savanna strip is gone
9f3f25dc Mistfoot gets a reason to exist: 13 tiles, not 500
a46bd851 The Sink: Damp's rectangle becomes a rift on the terminator
8ca0895e The pools cluster instead of ticking: stdev/mean 0.19 -> 1.33
4f9a5743 Speckle cleared: 49 lone hexes become 9 islands, ice fragments dissolved
9d3d8fae Grey Sea coastline smoothed: the gear teeth are gone, water budget untouched
609d2ea5 The Anvil becomes the flat-topped plateau its own design doc says it is
```

Every one is exactly the class of change the freeze's own `whatFreezingCosts` field
names as staying free ("SURGICAL edit, not... regeneration" via
`ashkarr_clamp_rain.py`-style scripts) — each commit message cites a specific ruling
or measured defect it fixes. This is legitimate authored work, not accidental drift;
it was simply never restamped after the last of these 14 landed. Net biome deltas
between the stamp and disk (largest movers): `AB_RockyCrags` -2591, `HorrorWastes`
+1243, `AB_PropaneLakes` +1035, `ZBiome_Badlands` +541, `BMT_CrystalCaverns` +451,
`AB_FeraliskInfestedJungle` -362, `Desert` -497, `AridShrubland` +39.

## 3. Tooling built: the hash check is now a real, callable, wired-in command

`src/RimMandrake/Utils/verify_frozen.py` **already existed** (built during an earlier
restamp, per its own docstring) as the CLI hash-check/`--restamp` command for any
`*.frozen.json` marker in the repo. What it did NOT have: a library entry point other
scripts could call on every read, and none of the actual reader scripts called it —
which is exactly how this staleness went unnoticed for 14 commits.

Added `warn_if_stale(artifact_path)` to `verify_frozen.py` — non-fatal (fails open,
never raises, never blocks the caller), prints a one-line stderr warning naming the
exact CLI command to run for details when the stamp disagrees with disk. Wired it into
every reader script under `src/RimMandrake/Utils/` that opens
`world/ASHKARR_WORLDMAP_tiles.csv` directly and isn't itself a writer that already
reminds to restamp (`ashkarr_horror_is_one_place.py` and `ashkarr_warm_crags_to_horror.py`
already print a restamp reminder on write — untouched):

- `src/RimMandrake/Utils/ashkarr_populate.py` (`load_tiles()`)
- `src/RimMandrake/Utils/lint_links.py` (`main()`, before the tiles read)
- `src/RimMandrake/Utils/reload_check.py` (the live-tiles read block)

Verified live: importing `warn_if_stale` directly against the current stale stamp
prints the warning and returns `False`; running
`python3 src/RimMandrake/Utils/lint_links.py` end-to-end shows the warning fire before
its normal report. `python3 -m py_compile` clean on all four touched files.

`first_light.py` and `w9_run.py` also reference the `TILES` path but don't open it
directly in-process (they drive it through the bridge / other modules) — not wired;
say so here rather than guessing a hook point that might not fire.

## 4. Left for the owner: the actual restamp

Not run, per scope limit — restamping a frozen artifact is the owner's action alone.
Verified working (dry-run reports STALE correctly; `--restamp` code path is the
existing, previously-used mechanism, unchanged):

```
python3 src/RimMandrake/Utils/verify_frozen.py --restamp world/ASHKARR_WORLDMAP_tiles.csv
```

This updates only `sha256`/`bytes`/`rows` in the `.frozen.json` sidecar to match the
14 already-committed surgical edits above. It does **not** touch `frozenMeaning`,
`whyItPassesTheThreeTests`, `whatFreezingCosts`, `toUnfreeze` or `notFrozen*` — those
still read true. It does **not** apply `WORLDMAP_DESERT_BAND_REPAIR_1` (§1) — that is
a separate, still-pending, ratified-but-unexecuted item for a future bridge session
and should not be conflated with this restamp.

Left `doing`, not closed — the actual restamp command above is the one action the
owner should run to close this out.
