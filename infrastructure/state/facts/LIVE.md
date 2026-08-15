# LIVE — what the running game tells us. CHECK writes. DECIDE and BUILD read.

- A **quicktest builds a FULL world**, not a stub: 119,904 tiles, `waterPct 25.0`,
  2 water bodies, `seedString "green"`, `planetCoverage 0.3`, `previewOnly:false`.
  ⇒ the sea can be measured on disposable worlds without opening the planet page
  or the once-only Configure Factions screen.
- `waterPct 25.0` is a **mode, not a constant** — seed `sickle` read 16.74.
- `start_debug_game_ready` **times out at the client (30 s) and still works**;
  `hasCurrentGame` flips false→true after. Budget ~90 s. Do not retry a timeout.
- After a map exists the game is **not reactive for ~40 s**, whatever
  `currentMapReady` reports. Read-only calls are fine inside it; mutations are not.
- **A GenStep runs at map generation and never again.** Anything it scattered is
  frozen with the def that was deployed when that map was made — counting it on an
  older map measures the older def.
- `IncidentWorker_RaidEnemy` takes `IncidentParms` **by reference** and
  `PawnGroupMakerUtility` **overwrites `parms.faction`** if your faction is not
  hostile. The raid reports success and a different faction arrives. **Read the
  faction back out of the reply**, and pass `points` explicitly or the storyteller
  default gives one trivial attacker.
- Spawning the **second** pawn of a race whose flesh type we set `isOrganic=false`
  throws: no `Pawn_RelationsTracker`, and HAR dereferences it. First spawn of each
  def always succeeds. Confirmed live.
- **Vanilla art lives in asset bundles**, so a wrong `iconPath` and a right one look
  identical offline. Icon paths can only be settled by looking in-game.
- Live mod count is **585 active**; the last offline def dump was built from 580.
  Both are correct about different things — re-run `refresh.py` before trusting a
  disk-derived lookup.
- Companion DLL: **30 tools built (md5 `d7e7c6c1`), 26 deployed.** A companion
  deploy needs the game DOWN and **must pass `--gm`** or it strips
  `fire_incident` and `send_letter`.

## 🔴 The authored ship on the CURRENT map — 2026-08-14, owner is mid-build on it

`Gravship_v1` stamped at origin **(81,57)**, footprint x81–168 z57–191, on a wiped
"Tall Shrooms" quicktest. **4,057/4,057 substructure, every floor type complete,
1,052/1,052 things.** Map is otherwise bare: 30,276 things destroyed, 1,759 roofs
removed, 4,544 rock floors repainted, 597 stray substructure cells removed,
**0 pawns**, god mode **OFF**, paused.

| part | where | note |
|---|---|---|
| `GravEngine` | **(126,149)** | the export contained NO engine; its header records `gravEngineX/Z 45,92` and that maps exactly here, at the centre of the ship's only 5×5 `CarpetMarine` block |
| `PilotConsole` | **(129,149)** | |
| `ChemfuelTank` | **(126,151)** | owner filled it by hand in god mode |
| `SmallThruster` ×4 | **(166,147) (166,148) (166,150) (166,151)** | moved 2026-08-14 on the owner's ruling. EAST transom, `rot 3` (West) — the ship now flies **west**. Was the west hull line at `rot 1` (flew east), scattered over 128 tiles of flank |
| `PowerConduit` | 300 total | 184 from the export + **116 routed by BFS** to every component |

- 🔴 **The grav engine IS the ship's power plant.** Live def:
  `CompProperties_Power`, `compClass CompPowerPlantGravEngine`,
  `transmitsPower true`, `idlePowerDraw -1.0` (negative = generation). ⚠️ **The
  DISK def has no power comp at all** — a mod restamps it at load, so a grep of
  `Buildings_Gravship.xml` returns a well-formed and WRONG answer. Read live.
- ⚠️ **Buildings from `spawn_batch` arrive FACTIONLESS.** The `GravEngine` offers
  **no Launch gizmo** and `Claim` is *disabled* until a colonist exists to claim
  it. Flyability and `NoPathToPilotConsole` are both untestable on a pawnless map.
- ⏳ **"Not enough fuel" on a paused fresh build is a tick-0 artefact**, not a
  defect — the thrusters have not ticked. Let time run, then re-read.
- ✅ **RESOLVED — the red diagonal overlay is NOT a placement fault.** A/B, 2026-08-14:
  a control thruster spawned in the *exact* known-good config the owner says flew the
  ship east (west hull line, `rot 1`, at (86,149)) renders with the **same** red slash
  and purple bars as the new east bank. The overlay does not discriminate between a
  working and a suspect thruster, so it is a ship-wide condition (unfuelled/unticked,
  see the tick-0 bullet above) — **never read it as evidence about placement.**
  The still-missing thing is a real status read: `jawa/inspect_string` (S8).
- 🔑 **A thruster's exhaust strip runs OPPOSITE its facing**, and the thruster
  **replaces a hull-wall segment** rather than standing behind one. Measured, not
  inferred: all 4 original thrusters were the **westmost cell of their row** at
  `rot 1`, each in a gap in the west wall with 5 empty cells beyond. Mirror for
  `rot 3`: outer cell on the east wall, lane running east. The in-game ▶ arrow
  points along the exhaust, i.e. away from travel — a west-flying ship shows ▶ east.
- 🔑 **`Position` is the LOW-x cell at `rot 1` but the HIGH-x cell at `rot 3`.**
  A 1×2 thruster spawned at x=166 `rot 3` occupies **165–166**; at x=108 `rot 1` it
  occupies 108–109. Read `cellRect` off `rimworld/get_map_target_info` (needs the
  **`Thing_` prefix**) rather than assuming — a guess here mounts the bank one cell
  inboard and buries the exhaust lane in substructure.
- 🔑 **The hull's east wall has a 9-cell flat transom at x=166, z145–153, centred on
  z=149 — the GravEngine's own row.** It is the only long flat facet on the ship and
  is plainly the designed engine mount. Flat-facet profile of the east wall is
  reproducible with `jawa/list_things defName=GravshipHull` + per-row max-x.
- 🔴 **`apply_architect_designator` `dryRun` is NOT a placement validator under god
  mode.** It returned `ok=true` for 25/25 cells including a cell **already occupied by
  a thruster**. Do not use it to confirm anything; it answers "did the call run".
- ⚠️ **The ship still has no power SOURCE for its VFE factory block** beyond the
  engine itself, and no `LargeThruster`, `SignalJammer` or shield.

### 🔴 Power — the 300 conduits were wired to NOTHING. Rewired 2026-08-14

**Before:** 310 transmitter cells in **10 disconnected islands**; the engine's own net
was 63 cells; **0 of 23** powered machines had a transmitter touching them (3 sat on a
dead island, 20 had no conduit adjacent at all). The grid looked plausible on screen and
carried no power anywhere. ⇒ **a conduit census is not a wiring check.** 300 conduits and
zero connections render almost identically to 300 conduits and full coverage.

**After:** 201 conduits added → **1 net, 502 cells, 23/23 machines connected.**

- **The connection rule, as used for the audit:** transmitters join **orthogonally only**
  (diagonal conduit does NOT connect); a `CompPowerTrader` connects if a transmitter cell
  lies inside its footprint **or in the 8-way ring around it**. Transmitters here are
  `PowerConduit`, `HiddenConduit` and `GravEngine` (`transmitsPower true`, all 9 cells of
  its 3×3 at (125,148)–(127,150)).
- **Not power consumers, despite looking like it:** `GravFieldExtender`, `PilotConsole`,
  `VFEFactory_Booster`, `VFEFactory_FactoryHopper`, `Door` — none has a power comp. Only
  the 21 `VFEFactory_*` machines and 5 `VFEFactory_Heatsink` draw. Read the comps; do not
  assume from the name.
- **Route conduit on SUBSTRUCTURE only** or it does not fly with the ship. Conduit may
  share a cell with a hull wall (not an edifice clash) but not with a machine — the
  router treats machine footprints as non-routable and reaches them via the 8-way ring.
- 🔴 **`jawa/get_def` does NOT serialize `basePowerConsumption`** — the one number power
  work needs. The comp fields stop at `transmitsPower / idlePowerDraw / shortCircuitInRain
  / showPowerNeededIfOff / alwaysDisplayAsUsingPower`. **Ship power BUDGET is currently
  unmeasurable from the bridge**; only topology is. Wants `inspect_string` (S8).
- ⚠️ **The power overlay is NOT a connection oracle.** A/B: a `VFEFactory_Heatsink`
  spawned in open desert with **no conduit on the map near it** renders with **no power
  icon at all**, while wired machines on the ship show yellow bolts and magenta dots. So
  icon-presence does not mean "unpowered" — those marks are machine art / VFE facility
  status. **Read the graph, not the pixels.** The overlay is only good for *seeing* where
  conduit runs, which is what it was turned on for.
- The overlay is toggled by selecting a power designator —
  `rimworld/select_architect_designator architect-designator:power:build-powerconduit`.
  ⚠️ `jawa/clear_ui` does not clear it, but call `clear_ui` **before** selecting, or the
  debug log covers the shot.
