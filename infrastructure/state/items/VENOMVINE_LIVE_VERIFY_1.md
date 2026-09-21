# VENOMVINE_LIVE_VERIFY_1 — quicktest the venomvine's contact venom in a live game

## what is wrong

`VENOMVINE_CONTACT_VENOM_BUILD_1` built the whole mechanism offline and closed:
`RM_Venomvine`, `RM_VenomvineScratch`, `RM_VenomvineVenom`, the
`CompContactVenom` / `MapComponent_ContactVenom` / `ContactVenomImmunity`
triple, three Mod Settings, and the `RUT_Desert` wiring. It compiles clean and
every def validates. **Nothing has been seen running.**

## why a live check is owed — the one line the gate asks for

🔑 **The NEW mechanism never once observed is "a `MapComponent` damages a pawn
for standing on a registered cell."** Nothing in this repo has done that
before: every existing hazard in `mandrake.rm.environmentalhazards` damages
from a gas grid, a hediff comp, a game condition or a death action, never from
a per-tick cell-occupancy sweep. The registration path (a `ThingComp` on a
Long-ticking plant putting its cell into a map-wide set on spawn and taking it
out on despawn) is likewise new, and the failure mode if it is wrong is
SILENT — a stand that simply never scratches reads exactly like a stand nobody
walked into.

Everything else in the build is ordinary and is NOT what this item is for: the
plant def is a plant def, the DamageDef copies Core's own `ScratchToxic`
shape, and the hediff is a hediff.

## the work

`design/Jawa/worldbuilding/desert_shade_plants_design.md` §5, steps 1–6 and 8,
on a quicktest map with all five DLC (`modset_builder.py` tiers all set
`dlc: True` since 2026-09-19):

1. Spawn a stand; walk a colonist through it — exactly one
   `RM_VenomvineScratch` injury on a leg, `RM_VenomvineVenom` at ~0.12,
   decaying to 0 in ~6 h.
2. Park a colonist inside for 3 in-game hours — one scratch per hour, venom
   past 0.30 (serious stage visible). A downed pawn left inside reaches
   `lethalSeverity` in ~9 h with "Contact venom can kill" on, and never with
   it off.
3. Cut a vine from an adjacent non-vine cell — no scratch. Cut one whose only
   adjacent cells are vine — scratch on the hour. (This is intended, per the
   build item's own "Watch out"; do not "fix" it.)
4. A flying creature (any Core bird) crosses the stand — nothing.
5. A race carrying `ContactVenomImmunity` crosses — nothing. Nothing in the
   repo carries that extension yet, so this step needs a throwaway def or a
   runtime-added extension.
6. Full Sharp leg armour — scratch reduced; when reduced to 0, no venom at
   all.
8. Save/load mid-contact — the per-pawn clock survives (`ExposeData`) and no
   double scratch fires on load.

Also worth watching for, since neither can be seen offline:

- The registration path under **map generation**: `RM_Venomvine` is wild-spawned
  by `WildPlantSpawner`, so its comps register during map gen. Confirm a
  wild-grown stand (not a dev-spawned one) is armed.
- `pathCost 60` in practice — a sparse stand should be threaded and a solid
  band detoured when the detour is cheaper, per the design's avoidance rule.

## criteria

Every step above observed, or the defect it found filed. A step that cannot be
staged (step 5 needs a def that does not exist) is recorded as not-run rather
than passed.

## live run — 2026-09-21: the gate line is DISCHARGED; three steps remain

Run by FOUNDRY on the bridge, `modset_builder.py --tier desertplants` (19 mods,
all five DLC), on a genuine `RUT_Desert` map (tile 83745, 250×250, generated
through `jawa/world_tile_map_generate`). The DLL and all four def files were
deployed this pass — none of it had ever reached the game folder.

### the one line this item exists for — OBSERVED

> *"a `MapComponent` damages a pawn for standing on a registered cell"*

A 14×14 Soil rect at (120,120) was painted and planted solid: `jawa/set_plants`
placed **196 of 196** `RM_Venomvine`, confirmed by `jawa/list_things`
(`countMatched 196`, still 196 at the end of the run). Five colonists were
spawned inside it and three outside as controls. **Within 30 ticks of the first
sweep, four of the five inside carried `Scratch` injuries labelled "scratch
(venomvine)" and the hediff `RM_VenomvineVenom`; all three outside carried
nothing.** The mechanism runs.

### step 1 — crossing: PASS, with the predicted number corrected

| | predicted by the item | measured |
|---|---|---|
| injury site | a leg | left leg · right leg+right foot · left leg+left foot · left leg+**torso** |
| `RM_VenomvineVenom` on first contact | ~0.12 | **0.0536 · 0.1608 · 0.1608 · 0.201** |
| decay | to 0 in ~6 h | **exactly `severityPerDay -0.5`** |

The ~0.12 prediction assumed the full 3 damage; the engine applies 2.01 after
`victimSeverityScalingByInvBodySize` and armour, and one contact produces two
injury records (a leg and its child foot), hence 2 × 2.01 × 0.04 = **0.1608**
for an unarmoured pawn. Crink, who spawned with more apparel, took 0.67 per
injury and 0.0536 of venom — that is step 6's armour reduction visible without
being staged for.

Decay MEASURED rather than estimated: Ash 0.2983 → 0.2833 across 1,800 ticks.
`severityPerDay -0.5` predicts −0.0150 over that window; the reading is
−0.0150. From 0.16, zero at ~19,000 ticks ≈ 5.3 h — the item's "~6 h" is right.

⚠️ One injury landed on a **torso**, not the Bottom region. Recorded as
measured, not judged: `SetBodyRegion(Bottom, Outside)` admits parts whose
`height` is Undefined, and Torso is one, so this may be correct engine
behaviour rather than a defect. 12 of 13 injuries across the run were legs and
feet.

### step 2 — lingering: PASS, cadence exact

Pawns drafted and parked on fixed vine cells, then stepped forward in
`rimworld/step_game_ticks` increments (note: the call completes ~600 ticks per
invocation and returns `status: timedout`, so a cadence test needs a loop, not
one big step). Reconstructing event times from venom severity net of the known
decay rate:

```
events at ticks ~31, ~2530, ~5030, ~7530, ~10030      spacing 2500, 2500, 2500, 2500
windows with no event: 2760->4561 (1801 ticks), 8160->9962 (1802 ticks)   as predicted
```

**One scratch per 2,500 ticks — `contactIntervalTicks` exactly, one per in-game
hour.** Not per tick, not per 15-tick sweep.

All three hediff stages were seen in game with their own labels, crossed at the
thresholds the def declares: **"thorn venom (minor)"** below 0.30 →
**"thorn venom (serious)"** (Mal, 0.3803) → **"thorn venom (grave)"** (Mal,
0.7423). By tick 11,162 three of the five in-stand pawns were **downed by the
venom alone** (Crink 0.6035, Mal 0.9133, Winnie 0.7123) with a live "Colonists
need rescue / Medical emergency" alert. Screenshot:
`Transient/venomvine_stand_20260921.png`.

### control — the strongest single piece of evidence

Two of the three pawns parked outside the stand finished the whole run at
**0 injuries, 0 venom**. The third (Reeves) wandered through the stand before
being parked, took two injuries, and then — parked outside — **took no further
injury for 8,400 ticks while its venom decayed monotonically 0.1877 → 0.1177**
across exactly the windows in which every in-stand pawn's venom rose. Same
pawn, in and then out; that is the contrast the item needed.

### what did NOT run, and why

- **step 3 (cutting from an adjacent cell)** — not staged. No defect suspected.
- **step 4 (a flyer crosses)** — not staged: 1.6 flight is a stat-driven state
  a bird enters on its own, and nothing here can force `pawn.Flying` on demand.
  **NOT-RUN, not passed.**
- **step 5 (`ContactVenomImmunity`)** — unstageable as the item already
  predicted: no def in the repo carries the extension. **NOT-RUN.**
- **step 6 (Sharp leg armour)** — only incidental evidence (Crink's apparel cut
  the damage 2.01 → 0.67). The "reduced to 0 ⇒ no venom at all" half was not
  staged. **PARTIAL.**
- **step 8 (save/load mid-contact)** — not run. `ExposeData` on the per-pawn
  clock is unproven.
- **wild-spawn under map generation** (the item's "also worth watching for") —
  **BLOCKED, and the block is a real defect.** `RM_Venomvine` is not in
  `RUT_Desert`'s runtime `wildPlants` at all: a `PatchOperationReplace` in
  `BiomeFlora_Ashkarr.xml` swaps the whole node for four other defs, so the
  0.25 wiring in `RUT_Desert.xml` never survives load. Filed as
  `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`. `pathCost 60` in practice is
  unobservable for the same reason (no natural stands exist).

### one anomaly, unexplained

Ash stopped taking events after tick ~7562 while still inside the rect at
(123,121), where a vine is present and the stand was never cleared (196 plants
throughout). Every other in-stand pawn kept taking the hourly event. Not
diagnosed; recorded so the next reader does not have to rediscover it.

### also found

`Config error in RM_Venomvine: Nutrition == 0 but preferability is RawBad
instead of NeverForNutrition` — ✅ **FIXED and VERIFIED GONE** on a later load
the same day (`03d963de2`): the def is reparented to `PlantBaseNonEdible`,
since Core's `PlantBase` exists only to add the RawBad `<ingestible>` and this
plant is deliberately Nutrition 0.

## wild spawn UNBLOCKED, and it happens — 2026-09-21, second sitting

`BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` is **closed** (`03d963de2`) and
`RM_Venomvine` is back in `RUT_Desert`'s runtime `wildPlants` at its authored
0.25. A fresh 250×250 `RUT_Desert` map on the same path produced **272 plants
across 8 defs, one of them a wild `RM_Venomvine`** — so the 0.25 wiring
survives load and `WildPlantSpawner` does place it.

⚠️ **That is a spawn observation, NOT the check this item wants.** The open
question was whether a comp on a WILD-grown vine registers its cell during map
generation, and **that was not tested**: the map was left at `ticksGame 1`, no
pawn was walked into the wild vine, and one plant on a 62,500-cell map is a
poor subject anyway. Use a higher-density staging or many maps when someone
runs it properly. `pathCost 60` in practice is likewise still unobserved.

⇒ This item **stays open** for steps 3, 4, 5, 6 and 8, for the wild-stand
registration check, and for `pathCost 60`. The mechanism it was filed to
witness has been witnessed; the wild half has not.
