# Gravship layouts: red herrings and the validation plan

The full text behind `SKILL.md` "Red herrings" and "Validation plan". SKILL.md states each rule once; the measurements and the
per-gate predictions are here.

### Red herrings, so nobody spends the hours again

- **Substructure connectivity was intact the whole time.** 4,037 cells, 4,034
  linked to the engine — matching the engine's own `Connected substructure: 4034`
  exactly. All eight thruster cells were substructure AND connected. Verify this
  cheaply with a 4-way flood fill from the engine over the `foundation` layer and
  compare to the engine's own number; if they agree, substructure is not your bug.
- **Distance is not the gate.** Thrusters 40 tiles out work once claimed and fed.
- **`onlyRequiresLooseConnection`** differs between parts (`GravFieldExtender`
  true, `SmallThruster` false) and is a genuine def difference — but it is not
  what was blocking, and reading it as the cause sends you to geometry again.
- **A colonist must INSPECT the grav engine** before anything binds to it, and an
  uninspected engine makes every part report the same "not connected" line. That
  is a real gate, and it is upstream of all four above. Reaching the engine needs
  a door: on the measured hull the engine chamber had **none**, and the whole ship
  has 2 doors for an 86x133 hull.


## Validation plan — what you owe whoever holds the game

`validate()` returning `[]` and `--roundtrip` passing prove the file agrees with
itself. Neither is the game accepting the ship. So an authored layout ships with
a validation plan **in the same commit** — because a load costs 23–30 minutes,
and without one the seat holding the game invents a check that carries none of
your predictions.

**1. The observable — what a player SEES when it works.**
🔴 **A positive observation, never "no error".** A ship that fails placement
mostly fails *silently* — nothing red, nothing logged. Name the thing on screen:
the layout's label on the choose-gravship page, `Connected substructure: 49 /
4500` on the engine panel, a floor tile that is `MetalTile` and not dirt.

**2. The route — the exact call, click path or spawn that produces it.**
The filename in `Config\GravshipExport`, the scenario, the cell to `click_cell`,
the gizmo. ⚠️ **If the route needs a tool that does not exist yet, say so and
file it as blocked on the tool** — mid-game import is queued as **B-v2** and does
not exist, so any item routed through a Sketch spawn is blocked, not queued.

**3. The prediction — written BEFORE the look.**
A number or a specific string: `49 / 4500`, two thrusters with no warning, 4,057
`terrainDef` cells back. A layout is all counts; predict them.

**4. The threshold — what CLOSES it, and what is explicitly out of scope.**
⭐ **Usually one observation, not a battery.** Name the minutia you are skipping
— the fog in unoccupied rooms, the missing preview PNG, the open questions in
`gravship_flight_invariants.md` §9.

**5. Batch or solo.**
A layout file rides with anything else on the same new game — it enters at world
creation and costs nothing extra. **A new assembly goes solo** (the B-v2 importer
when it lands), because if the load comes up wrong nobody can separate the DLL
from the ship beside it.

**6. What a FALSE PASS looks like.**
The way this particular check lies. Four measured here:
- **Geometrically valid, still unplaceable.** A thruster must **STAND on
  substructure while its exclusion zone contains NO substructure** — 1×5 behind a
  `SmallThruster`, 2×7 behind a `LargeThruster`. `validate()` checks foundations
  and engine coordinates and never looks at that rectangle, so a clean validator
  run is not a clearance check (`gravship_flight_invariants.md` §5). 🔴 The zone
  rotates to the side **OPPOSITE** the facing — offset `(0,0,-5)·rot` for the
  `GravshipThruster`'s 1×5 — so a **rot-South thruster's zone lands NORTH**,
  across the pad it stands on, and reads `Blocked by substructure` forever. Face
  each thruster **away from the ship edge**, not toward open space as intuition
  suggests (measured 2026-08-29).
- **Floors that survive export and vanish on a Sketch spawn.** Terrain is
  re-applied by the arrival Postfix (`HarmonyPatch_DoGravship.cs:~157`), *not* by
  `BuildFromLayout` — so a mid-game import lands the structure bare and **nothing
  errors**. Export→import passing says nothing about the Sketch path (§"One real
  catch"; invariants §9 q9).
- **The surplus was silently disconnected.** `maxSimultaneous` (ours: 20 small,
  10 large, read live) **drops the excess with no warning**. Counting thrusters in
  the XML is not counting connected thrusters; read the engine panel (§5, §6).
- **Under capacity read as flight-ready.** Completeness is a separate check from
  capacity: the engine panel's red `Requires: Thruster, fuel tank, controls`, and
  pathing (`NoPathToPilotConsole`, `PilotConsoleInaccessible`) — a sealed hull
  connects fine and refuses to launch (invariants §1, §2).

### The shape to hand over

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

Three lines. If it does not fit, the item is really two items.

Worked, for a hand-authored sled's first import:

```
PROVE    Drop JawaTestSled.xml in Config\GravshipExport -> new game, gravship- arrival scenario -> choose page -> pick "Jawa test sled" -> click_cell each thruster, then the GravEngine
EXPECT   Both SmallThrusters show a plain inspect panel with NO red "will be blocked by gravship substructure" warning · 0 blocked warnings; engine panel reads "Connected substructure: 49 / 4500"
LIES     validate() returns [] for this file: it checks foundation and engine coords, never the 1x5 exclusion rectangle. A clean validator is not a check.
```
