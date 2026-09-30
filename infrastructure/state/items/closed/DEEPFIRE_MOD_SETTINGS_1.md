## Spec row (verbatim, deepfire_luminous_pigment_spec.md §10 step 12)

| # | build | proof |
|---|---|---|
| 12 | Mod Settings screen, every key in §7 wired; About.xml, `.csproj` with every `.cs` in `<Compile Include>` (the `EnableDefaultCompileItems false` trap); art wired; `validation.py` | build clean; all-off quicktest: nothing spawns, nothing paints, no errors; **cold load on the full list** (`COLD_LOAD_RUN_SHEET_*`) with the Player.log strings for each def written before launch (`rimworld-load-round`) |

## What already exists to build on

- `LuminousPigmentSettings`/`LuminousPigmentMod` (`LuminousPigmentMod.cs`)
  already ships a real Mod Settings screen for Phase 1 (the chain) + Cuisine
  + gods (partial) + status — this item ADDS the painting-family keys, it
  does not build the screen from scratch.
- Step 5's own `DeepfirePaintDefaults` (`DeepfirePaintUtility.cs`) is
  DELIBERATELY plain constants, not settings, with a header comment saying
  so explicitly — this item is where `coatRadius[]`, `coatIntensity[]`,
  `glowMinValue`, the per-target Deepfire costs, and every other painting
  number named "not yet Mod Settings" across the DEEPFIRE_* follow-on items
  move into `LuminousPigmentSettings` and get wired the same
  `ApplySettings()`-reapply-at-startup way the Phase 1 numbers already are.
- `RM_LuminousPigment.csproj` sets `EnableDefaultCompileItems false` — every
  `.cs` file step 5 and its follow-ons add needs its own explicit
  `<Compile Include>` line (step 5's own commit already did this correctly
  for its 8 new files — verify every later DEEPFIRE_* item's new `.cs` files
  did too before this item runs, since a missing line compiles into nothing
  with no error, the exact trap CLAUDE.md names for this csproj).

## Build

Wire every painting/worn-glow number named across
`DEEPFIRE_FLOOR_PAINT_1`/`DEEPFIRE_FIRSTCOAT_BONUS_1`/`DEEPFIRE_WORN_GLOW_1`/
`DEEPFIRE_STATUS_THOUGHTS_1`/`DEEPFIRE_GOD_BRIDGE_DELTAS_1` into Mod
Settings (should run LAST among the DEEPFIRE_* follow-ons — it depends on
all of them existing to have numbers to wire). Art (a real texture for
`RM_DeepfireLightProxy`? — it is `drawerType None`, deliberately invisible,
so likely nothing to wire there; check whether "art wired" in this row
refers to something else, e.g. the designator icons, which currently reuse
vanilla `UI/Designators/Paint_Bottom`/`Cancel` placeholders per
`Designator_Deepfire.cs`'s own header comment). `validation.py` (the
north-star system, `NORTH_STAR_PIT_PILOT_1` family — check current state
before assuming a `shows=` bar needs authoring here; CLAUDE.md's own
"north-star validation state" section says the system cannot GREEN
anything project-wide as of its last measurement). Finally the cold load on
the full list.

## Needs

`game-up` — the cold-load proof is the item's own closing bar; everything
before it can run on a quicktest tier.
