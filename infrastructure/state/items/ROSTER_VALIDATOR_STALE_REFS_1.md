# ROSTER_VALIDATOR_STALE_REFS_1 — the validator's remaining errors are all its own

## what is wrong

After `_validate.py`'s `PAINTED_DEFS` was fixed to derive from the world CSV
(`bd69008f6`), 48 red errors remain. MEASURED 2026-09-20:

| class | count | verdict |
|---|---:|---|
| `flora def X not in plant_pool.csv` | 32 lines / **27 unique defs** | **ALL FALSE** |
| `fauna def X not in the creature register` | **11** | **ALL FALSE** |
| `defNames entry X is not a painted biome def` | **5** | **REAL** |

**Every one of the 38 flagged flora and fauna defs resolves in the live def dump**
(618 mods, `a48bc71544df1a7e`, captured 2026-09-20T17:44:19Z). Checked one query per
defName. Genuinely absent: **0 of 38.**

The rosters are right. The two reference artifacts are behind:

- `design/Jawa/mods/plant_pool.csv` — last written **2026-08-23**
- `design/Jawa/worldbuilding/review/creature_register_rows.json` — **2026-09-05**

Anything authored since is flagged. The flora misses are our own newer plants
(`RUT_Arpeau`, `RUT_Dewshrooms`, `RUT_FireLavender`, `RUT_Skulltop`,
`RUT_Wrinklecap`, `RUT_TreeMartyr`, the Twisting Thorn family…); the fauna misses
are seven `*Juv` juvenile forms plus `RUT_CathedralRoach`, `RUT_FireHawk`,
`RUT_FurnaceBeast`, `RUT_ScarRoach`.

⇒ **~90% of this validator's red output is noise**, and it is the noise that makes
the 5 real errors easy to miss.

## the 5 REAL errors — pre-repaint donor defNames in roster `defNames`

- `fall_line.json`: `ExtremeDesert`, `Desert`, `AridShrubland`
- `the_blue_desert.json`: `BiomeGRimond`
- `the_lantern_deeps.json`: `AB_PropaneLakes`

🔑 `fall_line.json`'s three are **already covered** by
`FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1` — and note the owner's 2026-09-20 ruling
there: those rows leave the biome tables entirely, so ⛔ **do not rekey them to
`RUT_*`**. The other two are plain renames.

## ⛔ why nothing was fixed here

**Both stale artifacts are read by work that is in flight right now.**

- `plant_pool.csv` is read by `design/Jawa/mods/biome_flora.py`, which **FOUNDRY is
  mid-edit on** (`BMT_FLORA_ABSORPTION_1`). Regenerating the pool underneath a live
  edit is how two windows corrupt each other.
- `creature_register_rows.json` is read by `rosters_to_cast.py`,
  `gen_stat_adjustments.py` and `_consolidate.py` — a rebuild is cross-cutting, not
  local.

🔴 **And neither may be safe to simply regenerate.** A generated file in this repo
can accumulate hand-made entries the generator can no longer rebuild — a count is
not a roster, and regenerating deletes them for good. **Check for curated rows
before running any generator over either file** (`frozen-artifacts` skill).

## the work

1. Establish, for each artifact, whether it is purely generated or carries curated
   rows. Do not run a generator until that is answered.
2. Refresh both, **after** `BMT_FLORA_ABSORPTION_1` lands — not during.
3. Re-run `_validate.py`; the flora and fauna classes should go to zero. If they do
   not, what remains is a real finding for the first time.
4. Fix the 2 plain biome renames; leave `fall_line.json` to its own item.

## Watch out

- ⚠️ **A batched SQL `IN`-list query gave the wrong answer here.** A first pass using
  one query with all 32 names reported 12 defs as absent from the dump; checking each
  name individually showed **0** absent. The per-name check is the one to trust.
  🔑 An instrument that is cheap and slow beats one that is fast and silently partial.
- ⚠️ **`ModsConfig.xml` is not evidence about the owner's stack while a test tier is
  live.** Read `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` instead.
  A check run during FOUNDRY's 14-mod flight test read `rotsporekit` as INACTIVE; it
  is active in the real 618.

## verify

`_validate.py` reports zero `not in plant_pool.csv` and zero `not in the creature
register` errors, with no roster edited to achieve it.

## criteria

A red line from the roster validator means something is actually wrong.
