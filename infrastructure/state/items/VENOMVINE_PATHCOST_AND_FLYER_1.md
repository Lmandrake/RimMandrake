# VENOMVINE_PATHCOST_AND_FLYER_1 — the flyer exemption, the one venomvine property still unobserved

## what is wrong

`VENOMVINE_LIVE_VERIFY_1` closed with every step of
`design/Jawa/worldbuilding/desert_shade_plants_design.md` §5 observed except two
things. **One of the two is now measured** (`pathCost 60`, see below, 2026-09-21).
This item is what is left: `MapComponent_ContactVenom.Sample` skips a pawn when
`pawn.Flying`, copied from `Building_Trap.Tick`, and that one line has still never
been seen doing anything.

## step 4 — a flyer crosses a stand and is untouched — STILL OPEN

🔴 **It cannot be forced, and as of 2026-09-21 it cannot be READ either.** Both
halves are measured, not assumed:

- **No debug action.** Re-enumerated live on the 19-mod `shrublandfauna` tier,
  2026-09-21: 3 debug roots, **766** first-level children, and the only node whose
  leaf name contains fly/flight/flee is `Actions\Force Enemy Flee`, which is
  unrelated. This reproduces the 2026-09-21 enumeration on a different mod list.
- **No bridge tool writes `Pawn.Flying`** — unchanged.
- **NEW: no bridge tool READS it either, and the scripting tools are not a way
  round.** `rimbridge/run_lua` / `run_lua_file` / `run_script` are, by their own
  descriptions, a *lowered subset* that sequences existing capability calls — not
  arbitrary C# against the running game. So there is no route to `Pawn.Flying`
  in either direction.

### the observational run that was made, and why it does not settle it

Staged exactly as this item prescribes — a solid stand, many flyers, a grounded
control on the same stand, sized for a rate difference rather than a zero:

- `MaxFlightTime` MEASURED per species with `jawa/pawn_stats` on a live pawn:
  **Duck 30 s · Goose 30 s · Sparrow 30 s · `RSW_ScrapNestBird` 30 s · Chicken 3 s**;
  **Turkey · Emu · Cassowary · Hare · Boomrat · Squirrel · Rat all 0 s.**
  (So `Pawn_FlightTracker.CanEverFly` is true for the first group and false for
  the second — the arms are correctly constituted.)
- Pen: a walled 20×20 box (84 Steel walls), interior x 22–41 / z 126–145, with
  **400 of 400 interior cells** carrying `RM_Venomvine`. Nobody can stand off a
  vine, so `contactIntervalTicks` 2500 is the only thing setting the scratch rate
  and it is species-independent.
- Arms, matched on body size so the confound runs *against* the hypothesis:
  **Goose (flyer, bodySize 0.65)** vs **Cassowary (ground, 0.70)** and
  **Turkey (ground, 0.60)**, 20 each.

**Result at dt = 7,220 ticks, all 20 of each still alive and inside the pen:**

| arm | `MaxFlightTime` | Scratch injuries | `RM_VenomvineVenom` severity sum |
|---|---|---|---|
| Goose | 30 s | 121 | 14.89 |
| Cassowary | 0 s | 120 | 14.88 |
| Turkey | 0 s | 122 | 14.88 |

**No rate difference at all.** Duck (0.4) died out earlier than the rest, which
tracks `victimSeverityScalingByInvBodySize`, not flight.

⚠️ **That null does NOT mean the exemption is broken, and it must not be recorded
as if it did.** With `Pawn.Flying` unreadable there is no way to separate *"the
geese never left the ground inside a 20×20 pen"* from *"the `pawn.Flying` skip
never fires"*. The run bounds the effect (≤ ~1% over 7,220 ticks in that pen); it
does not attribute it.

⚠️ **And sizing the window is a trap of its own.** `victimSeverityScalingByInvBodySize`
makes a 100%-vine pen lethal to small animals within ~2–3 in-game hours: a first
attempt run to ~57,000 ticks killed all 60 test animals and returned nothing.
Keep any repeat under ~8,000 ticks, or thin the stand.

## what would actually close it

A JawaBench `[Tool]` that reports `Pawn.Flying` for a named pawn — and, better,
one that starts a flight through `Pawn_FlightTracker` so the crossing can be
staged instead of waited for. That is a one-minute edit-build-deploy-test cycle
on a minimal list (`rimbridge-companion` skill). Until it exists, this step is
**UNMEASURABLE with the existing tool surface**, and that is the honest state —
not "observed" and not "failing".

## `pathCost 60` in practice — MEASURED 2026-09-21, both modes

`RM_Venomvine` carries `pathCost 60` so a sparse stand is threaded and a solid
band is detoured when the detour is cheaper. Staged on a flat arena:
`jawa/clear_area 18,98,74,49` (1,932 things destroyed), 3,626 cells set to `Sand`,
0 of 35 sampled cells roofed. One drafted, unarmed colonist, ordered with
`jawa/ordered_job Goto` from **(25,120) to (85,120)**, position sampled every 13
ticks to recover the actual route.

| run | stand | route | cells inside the stand's footprint | cells standing on a vine |
|---|---|---|---|---|
| **control** | none | 61 cells, **dead straight, z = 120 throughout** | — | — |
| **detour** | x 50–60 × z 110–130, **231 vines, 100 %** | 61 cells, z 109–120: peels off the straight line at x = 40, runs the stand's whole width along **z = 109 — one cell outside its edge** — and climbs back to z = 120 at x = 71 | **0** | 0 |
| **thread** | same rect, **104 of 231 cells (45 %)** | 61 cells, z 119–120: goes straight through the footprint, weaving one cell up and down | **11** | **0** |

Solid ⇒ goes round. Sparse ⇒ goes through, and still never sets foot on a vine.
That is the design's avoidance rule, observed. Cell lists are in the run log.

⚠️ **Tool note for whoever stages venomvine again:** `jawa/set_plants` REFUSES
`RM_Venomvine` on `Sand` — "terrain or conditions cannot support RM_Venomvine",
231 of 231 rejected. `jawa/spawn_batch` (plain `GenSpawn`) places them fine and
they register with `MapComponent_ContactVenom` normally, which is how both runs
above were staged.

## criteria

The pathCost half is done. The item stays open on the flyer half alone, and the
standard is unchanged: a measured rate difference for flyers over a stand with a
grounded control — or the NOT-RUN reason measured rather than asserted, which is
what the section above now records.
