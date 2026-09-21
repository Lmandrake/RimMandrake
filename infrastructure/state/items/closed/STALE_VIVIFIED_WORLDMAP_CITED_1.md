# STALE_VIVIFIED_WORLDMAP_CITED_1 — live design docs are written against a pre-rename worldmap

## what is wrong

`world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv` is a **superseded** worldmap export.
`world/ASHKARR_WORLDMAP_tiles.csv` is the canonical one — the artifact
`WORLD_REMAKE_FINAL_STEP_1` names as surviving the world remake.

They cover the **same 21,872 tiles** and disagree about what those tiles are called.
MEASURED 2026-09-20, both files parsed with `csv.DictReader`, joined on `tile`:

| | disagreement |
|---|---:|
| **biome key** differs on | **21,660 of 21,872 tiles** |
| **region name** differs on | **1,136 of 21,872 tiles** |

The biome disagreement is the `RUT_` rename: the vivified CSV still says
`ExtremeDesert`, `Desert`, `AB_MycoticJungle`, `Wasteland` where the canonical says
`RUT_ExtremeDesert`, `RUT_Desert`, `RUT_TheRot`, `RUT_Wasteland`. It therefore
predates `NAMING_SCHEME_EXECUTION_1` (closed 2026-08-31) entirely.

## the case that found it

`design/Jawa/worldbuilding/biomes/fall_line.md` is written against the vivified CSV
and calls the colony's home region **`Fall Line Barrens`**. The canonical worldmap
calls those same 153 tiles **`The Breaks`**.

Caught 2026-09-20 while reviewing `FALL_LINE_ARRIVAL_MECHANISM_1`'s spec, which had
inherited the stale name and was about to gate a `TileMutatorDef` on it. ⛔ **A gate
built on `Fall Line Barrens` matches nothing on the canonical world.** The correction
is recorded at the foot of
`design/RimUtinni/fall_line_arrival_mechanism_spec.md`.

🔑 The *geography* in that spec was right and is unaffected — tile 17007 really is in
the 153-tile region abutting the 155-tile `Fall Line`, and 155 + 153 = the 308 tiles
it cites. Only the **name to build against** was wrong. That is the dangerous shape:
every number checked out, so nothing looked wrong.

## who else cites it

9 files reference `ASHKARR_VIVIFIED` (MEASURED 2026-09-20). Two are closed items and
one is a generated queue view — leave those, they are provenance. The live ones:

- `design/Jawa/worldbuilding/biomes/fall_line.md` — **the reason this item exists**
- `design/RimUtinni/fall_line_arrival_mechanism_spec.md` — already corrected
- `infrastructure/state/evidence/world_port_survives_2026-08-26_CHECK.md` — evidence, check before editing
- `src/RimMandrake/Utils/vivify_world.py` and `src/RimMandrake/Utils/README.md` — the generator; decide whether it still has a job

## spec

1. Establish, in one line in the repo, **which worldmap CSV is canonical** and say so
   where a reader will hit it first. Right now nothing states it.
2. Reconcile `fall_line.md` to the canonical names — region names and biome keys both.
   Per the deletion rule, **correct the text, do not annotate it**.
3. Decide `vivify_world.py`'s fate: if it can regenerate a current export, say how it
   is run and what fingerprint proves the output current; if it is dead, remove it and
   its README entry rather than leaving a generator that emits stale names.
4. Sweep the other biome sheets under `design/Jawa/worldbuilding/biomes/` for region
   or biome names that exist only in the vivified CSV. ⚠️ This is the same defect class
   as `FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1` — check that item first; they may merge.

## verify

Join both CSVs on `tile` and confirm every region/biome name used by a live design doc
appears in `ASHKARR_WORLDMAP_tiles.csv`. The join is the instrument — ⛔ do not grep
either file; `.claude/hooks/block_blind_scan.py` refuses a scan on a worldcsv and names
`measure csv <path> --where col=value` instead.

## criteria

No live design doc names a region or biome that the canonical worldmap does not have.
