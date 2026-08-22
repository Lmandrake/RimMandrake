## spec
✅ **OWNER RULING, 2026-08-22, verbatim:** *"That world, upon examination, really isn't very
bad at all... we're thinking of trying to adopt it."* — said after looking at
`world/view/ASHKARR_GLOBES.html`, the four-globe sheet.

🔴 **This SUPERSEDES `WORLD_FROZEN_RETHINK_PLANET_1`** (2026-08-21) wherever the two disagree.
That freeze lasted one evening. It was not wasted — it stopped a wholesale redraft — but its
premise, that the owner was dissatisfied enough to discard the map, is now false.

## What it decides
1. ✅ **Ash'karr AS IT STANDS is the v1 planet.** Adopted, not merely current.
2. ✅ **Authoring on it is OPEN**, and means editing **the map that exists, DIRECTLY and in
   place**: river and road continuity, landmarks, named places, settlements, terrain detail.
3. ⛔ **Three things did NOT come back, and no reading of this item reopens them:**
   - regenerating the bundle with `ashkarr_paint.py` — the artifact is hand-held now;
   - `refmatch.py` and the reference-match harness — cancelled, and moot twice over: the
     owner accepted the map **by looking**, which is the judgement the harness wanted to make;
   - **worldgen, in any version.** CLAUDE.md's standing ruling is untouched and always was.
4. 🔮 `design/V2_DREAMS.md > PLANET_METHOD_RETHINK_1` **stands as history, not as a plan.**

## Five items stay dropped, deliberately
Reopening the freeze does not reopen these, and each has its own reason:

| item | why it stays dropped |
|---|---|
| `REFMATCH_THRESHOLDS_CALIBRATE_1` | the harness is still dead — see (3) |
| `SCALD_RELIEF_RENDER_LOOK_1` | the owner HAS looked; the globes were that look |
| `RIVERS_BEGIN_FROM_NOTHING_1` | its substance was delivered by direct edit (`9d14d16`), not by re-running the painter, which is what the item actually asked for |
| `W9` · `LOAD2_TARGET_IS_SUB7B_1` | both are live-game paint runs; they belong with `FINAL_WORLD_PREP_1` when the owner is ready to bake |

## What was done under it, 2026-08-22
- **Seven river mouths joined to the Scald** (`9d14d16`). Every mouth stopped exactly one hex
  short, the richest carrying 28,936 units of accumulation into a jungle tile with no river.
  14 links, mouth-first. Networks reaching the sea: **1 of 10 → 4 of 10**.
- **Roads measured and found clean** — one network, 837 links, all 72 settlements on it, and
  all nine dead-ends are settlement spurs. No repair needed.
- **The freeze unwound in 14 docs plus `canon.yml`, `queue/HUMAN.md` and §17 of the plan.**
  Banners are REPLACED, never deleted, so the reversal is visible where the freeze was.

## Owner rulings taken in the same conversation
- **Tall sunlit massifs get rivers — the WET ones only.** `The Dew Horn` (144 tiles, 1936 m,
  1668 mm), `The Ashfall Range` (18 tiles, 2190 m, 1657 mm) and its 6-tile southern cluster,
  and `The Anvil` (7 tiles, 1574 m, 545 mm). ⛔ **`The Rust Cathedral` (61 °C, substellar,
  ~0 mm) and `The Ammonia Flats` (606 tiles, −30 °C, 19 mm) stay dry** — liquid water is not
  possible at either, and the Flats' own name says the liquid there is not water.
- **System #0 is an INLAND DELTA and stays endorheic.** 11,206 units dying on a flat jungle
  plain at 12 m, 17 hexes from any sea behind a 2,106 m lava ridge. Water does not climb
  1,839 m; routing it would mean editing elevation. The work there is presentational — a
  salt-pan or marsh terminus and a landmark at the fan.
- **Build-out priority, all four accepted:** landmarks first (16 on 21,872 tiles, six of them
  the same Oasis), then named places (23 regions; the Dune Sea alone is 1,692 tiles under one
  name), then settlement and faction spread, then a terrain-detail pass.

## verify
- No open item's purpose is to freeze or discard the planet.
- `canon.yml > ORTHO_GLOBE_MAP_ACCEPTED_1` carries the adoption, with the freeze struck in
  place rather than deleted.
- `grep -rln "THE PLANET IS FROZEN" design infrastructure` returns nothing.
- The five items above are still `dropped`.

## criteria
A seat arriving cold at any world doc learns, from the top of that doc, that the map is
adopted and that direct edits to it are the work — without needing this item.
