# LIVE — what the running game tells us. CHECK writes. DECIDE and BUILD read.

## 🔴 THE SHIP IS INERT BECAUSE THE GRAV ENGINE WAS NEVER INSPECTED

First real use of `jawa/inspect_string`, 2026-08-15, on the "ship" save. One root
cause explains every gravship symptom we have been chasing separately:

```
GravEngine (126,149)     Send a colonist to inspect this.
                         Power output: 1152 W   Grid excess: 682 W
                         Connected substructure: 4034 / 4680
SmallThruster x4         Not functional: Not connected to grav engine
PilotConsole (129,149)   Not connected to grav engine.
                         Must be placed within range of a grav engine.
                         Gravship range: 0
```

The console is **3 cells from the engine** and still reads "must be placed within
range". That is not a placement fault — an **uninspected** grav engine is inert, so
nothing binds to it: not the console, not a single thruster, and `Gravship range`
stays 0. ⇒ **Before judging any gravship geometry, check that the engine has been
inspected by a colonist.** Every "not connected" reading upstream of that is a
symptom, not a cause.

- ⇒ **The thruster bank is VINDICATED as placed.** The four at (166,147/148/150/151)
  `rot 3` are not faulted for position, rotation or blocked exhaust — the only
  complaint is the engine link, which every thruster on the ship would share
  wherever it sat. Their second requirement is **astrofuel**, and the net reads
  `0 l/d / 0 l` stored, so they would still not fire once the engine is inspected.
- ⚠️ **D-CHK1 needs re-reading in this light.** A colonist could not path to the
  console; a colonist is also what the engine needs. Whether these are one problem
  or two is not yet established.

### What `inspect_string` changes

It answers in one call what geometry could only ever suggest. Every claim above is
a sentence the game wrote, not an inference. **This is now the first tool to reach
for on any "is it working" question** — `get_cell_info` returns a className and
stops. `1196 examined` per call on the full stack, no timeout, no throw.

### ⚠️ Which map is which — the "ship" save is a MIDPOINT

`ship` contains the moved thruster bank (4 at x166 `rot 3`) but **301 conduit and 1
pawn** — so it predates the power rewire (493 conduit) and the 20-species crew. The
engine reads `Grid excess: 682 W` while a smelter on the same map reads `0 W`,
which is the pre-rewire 10-island state showing up as two different PowerNets.
**Do not read power conclusions off this save**; the rewired map was the disposable
one and is gone.

## 🔴 THIS LOAD'S DEF STATE PREDATES B56 — five factions absent BY DESIGN

Process **PID 13644 started 2026-08-15 00:43:34**. The five faction XMLs were
deployed to the game copy at **01:03:42**, and `fe6b460` was committed 01:06:35 —
both ~20 minutes AFTER launch. **RimWorld parses defs once, at launch**, so this
process read the broken files and no amount of redeploying reaches it.

Measured live on this load, not assumed: `jawa/get_defs` returns **0 of 5 resolved**
for `JawaAscendantHelix`, `JawaHuttCartel`, `JawaJunkers`, `JawaDeepwaterCompact`,
`JawaWildsteamClan`. Control `Jawa_IndigenousTribes` resolves `found=True` in the
same call, so the bridge and the query are fine — the five are genuinely not in this
process's def database.

⇒ **A null result for those five on THIS load is the OLD bug, not a new one.** Do
not chase it, and do not report B56's fix as failed. They are correctly shaped on
disk (0 `<xenotype>` tags, dictionary-keyed `<BTD_Nikto>` form) and should be live
on the NEXT cold load.

🔑 **The general trap, now hit twice in two days:** a deploy that lands after the
process launched is invisible to it, and the symptom is a def that is *perfect on
disk* and *absent in game*. C33 was void the first time for exactly this — the mod
deployed ~10 min after that process started. **Before calling any def missing,
compare the game copy's mtime against the process start time**
(`(Get-Process -Id <pid>).StartTime`). Disk evidence is not evidence about the
running game.

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

### Pawn spawning — 2026-08-14, 20 species placed in the ship

- 🔴 **`jawa/spawn_pawn` defaults `faction` to `hostile`.** Pass it explicitly. Twenty
  unrequested hostiles inside a sealed hull is one omitted parameter away.
- 🔴 **`spawn_pawn` reports `Spawned 1/1 <kind>` while generating something else.**
  4 of 20 (`Jawa_Spawn_Muun`, `Jawa_Gamorrean_Guard`, `OuterRim_Bothan`,
  `OuterRim_Cerean`) arrived as `kindDef Colonist` / `xenotype Baseliner`. The message
  echoes the REQUESTED name, so it is not evidence. **Read `kindDef` and `xenotype`
  back off `jawa/list_pawns`.** All four defs resolve fine under `jawa/get_defs`, so
  this is a generation-path fallback, not a missing def.
- 🔑 **`OuterRim_*` and `Jawa_Spawn_*` "species" are `race: Human` + a `BTD_*`
  XENOTYPE**, not separate races. Species identity lives in `xenotype`; a census that
  reads `def` alone reports 16 humans. True separate races on this stack:
  `ABAlien_Yautja`, `guy762_DroidRace_*`, `Dryad_*`, animals.
- ✅ **`jawa/set_pawn_xenotype` fixes it in place** — converted the 4 Baseliners to
  `BTD_Muun`/`BTD_Gamorrean`/`BTD_Bothan`/`BTD_Cerean`, read back correct. `kindDef`
  stays `Colonist`; only the xenotype changes, which is what renders.
- 🔑 **Roster of pawn kinds without `search_debug_actions`:** walk
  `list_debug_action_children` on `Actions\Spawn Pawn...` — **1,723 kinds**, one
  bounded level, ~1 s on the full stack. `jawa/get_defs` CANNOT enumerate (it needs
  explicit `DefType/defName` pairs) but is the right read-only resolve check.
- **C1 progress:** `jawa/get_defs`, `jawa/set_pawn_xenotype`, `jawa/list_things`,
  `jawa/clear_ui` have now RUN live. Still never called: `jawa/fire_quest`, the roof
  pair, the `spawn_batch` vehicle route, and `world_stats` needs its re-run.

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
- ⚠️ **The yellow bolt overlay is UNRESOLVED — do not cite it either way.** Two
  observations that do not yet reconcile, both measured 2026-08-14:
  1. A `VFEFactory_Heatsink` in open desert with **no conduit anywhere near it** renders
     with **no power icon at all**.
  2. The harness's blast doors at (106,120)/(112,120)/(118,120) **do** render the bolt —
     and (112,120) has a `PowerConduit` in its own cell.
  Faction is NOT the discriminator: all of them are `faction=None`. If reading 2 is the
  honest one, the bolt is a real "unpowered" mark and the ship's net is **connected but
  not SUPPLYING** — which would fit the engine being the only generator. **An earlier
  version of this line claimed the overlay was uninformative; that was one control
  over-generalised, and it is withdrawn.** Settle it with `jawa/inspect_string` (S8),
  not with more screenshots. Until then the CONNECTIVITY claim above stands on the graph,
  and SUPPLY remains unmeasured.
- The overlay is toggled by selecting a power designator —
  `rimworld/select_architect_designator architect-designator:power:build-powerconduit`.
  ⚠️ `jawa/clear_ui` does not clear it, but call `clear_ui` **before** selecting, or the
  debug log covers the shot.
