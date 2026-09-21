# VENOMVINE_PATHCOST_AND_FLYER_1 — both venomvine properties, MEASURED

## what this was

`VENOMVINE_LIVE_VERIFY_1` closed with every step of
`design/Jawa/worldbuilding/desert_shade_plants_design.md` §5 observed except two
things: `pathCost 60` in practice, and `MapComponent_ContactVenom.Sample`'s
`if (pawn.Flying) continue` — the flyer exemption copied from `Building_Trap.Tick`.
**Both are now measured, 2026-09-21.**

## step 4 — a flyer crosses a stand and is untouched — OBSERVED 2026-09-21

**A flyer takes nothing. A grounded pawn on the identical cells takes a scratch
on the first sample pass. The skip is keyed on `Pawn.Flying` and on nothing else.**

| window | arm | `Pawn.Flying` | newly envenomed |
|---|---|---|---|
| 1 (202 ticks) | **Goose ×15** | **true, 15/15 at every poll** | **0 / 15** |
| 1 (same ticks, same stand) | Turkey ×15 | false | **15 / 15** |
| 2 (200 ticks) | **the SAME 15 geese, landed** | false | **15 / 15** |
| 3 (200 ticks) | **Hare ×15, forced airborne** | **true, 15/15 at every poll** | **0 / 15** |
| 4 (200 ticks) | the SAME 15 hares, landed | false | **15 / 15** |

Windows 2 and 4 are the within-subject control the earlier attempt could not
have: the identical pawns, on the identical cells, differing only in `Flying`.
Windows 3–4 rule out species — a Hare has `MaxFlightTime 0` and the engine's own
`StartFlying()` **refuses** it, yet forcing its `flightState` alone exempts it.

Staging: a 30×30 arena, `jawa/clear_area` then 900 of 900 cells carrying
`RM_Venomvine` via `jawa/spawn_batch`, all 45 animals confirmed inside the arena
at every read. Script: `src/RimMandrake/bridgetools/prove_venomvine_flyer.py`;
run log `Transient/venomvine_flyer_run.txt`.

🔑 **The window is ~200 ticks, not thousands, and that is the design.** `Sample`
scratches on FIRST contact immediately (`index < 0` → `Scratch` on that same pass)
and runs every 15 ticks, so the per-pawn outcome is BINARY inside a few hundred
ticks. The earlier 7,220-tick rate comparison was the wrong instrument for a
skip-or-not question, and a 57,000-tick attempt before it killed all 60 animals
(`victimSeverityScalingByInvBodySize`) and returned nothing.

### the tool this needed, and what it does

`jawa/pawn_flight` (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlightTools.cs`)
— nothing on the bridge could read `Pawn.Flying`, let alone set it. It reports the
whole `Pawn_FlightTracker` for one pawn or every spawned pawn of a kind, and drives
it four ways: `report` · `start` (the engine's own `StartFlying()`, with its refusal
named) · `hold` (writes the private `flightState`, so it works on a species that can
never fly) · `land` (writes `Grounded` — `ForceLand()` alone is **not** enough).

Four engine facts it exists to encode, each read from 1.6 source:

- **`Flying` is a STAT switch, not a race flag.** `CanEverFly` ends in
  `GetStatValue(MaxFlightTime) > 0f`. MEASURED here: Goose 30 s, Hare and Turkey 0 s.
- **`TakingOff` and `Landing` both read as `Flying`** (`flightState != Grounded`),
  so a pawn is airborne for the venom component right up to the tick its landing
  lerp completes.
- 🔴 **Flight does not persist by itself.** `Notify_JobStarted` force-lands on every
  job start whose `JobDef` lacks `tryStartFlying`, and `FlightTick` lands the pawn
  once `flyingTicks >= MaxFlightTicks`. Hence `maintainTicks`, which re-asserts every
  poll and reports **`flyingLowWater`** — the fewest pawns seen airborne at any poll.
  Both flight windows above ran `flyingLowWater 15/15` with **0 reasserts needed**,
  which is what makes the zeros attributable rather than merely null.
- 🔴 **`MaxFlightTicks` is 0 for a non-flyer, so `hold` writes a large NEGATIVE
  `flyingTicks`.** With 0 the hare arm landed on the very next tick and only
  accidentally missed the sample passes (`flyingLowWater 0`, first run of the day).

### 🔴 the instrument bug that nearly produced a false "the mechanism is broken"

`jawa/list_pawns` puts the hediff list at **`row["health"]["hediffs"]`**, not
`row["hediffs"]`. Reading the wrong key returns `[]` for every pawn, so the first
run reported **0 of 15 for every arm including the grounded controls** — a clean,
confident, entirely wrong zero that reads as "the venom stand is inert". The stand
was working the whole time. ⛔ Never read a per-pawn health field without first
confirming that a pawn which IS damaged reads as damaged.

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

Both halves are measured against a live game with grounded controls. Done.
