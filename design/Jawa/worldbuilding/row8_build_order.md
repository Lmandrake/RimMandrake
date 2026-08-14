# row8_build_order.md — the gravship build, step by step

_Written offline 2026-08-13 by CREATE, during the worldgen load window, for CREATE
to read **line by line while driving the bridge**. It is an execution sheet, not a
design. Every number carries the file it was read from; nothing here is
remembered._

**Row 8 of `D:\Luke\dev\Rimworld\infrastructure\state\V1_SCOPE.md`** — the one
item that ships DEEP. Gate (`V1_SCOPE.md:40-42`): **seen working in-game once.**
For this row that means **the hull exists on the map, the grav engine reports it
connected, and a screenshot shows it** — not "the log is clean".

⚠️ **This runs AFTER worldgen.** `V1_SCOPE.md:280-290`: the anchor moved to
worldgen; rows 2 and 7 are one event and come first, and the ship is built on the
world that event creates.

---

## 🔴 D1–D5 ARE RULED — owner, 2026-08-13. Read this before step 1.

The plan below was written with five decisions open. **They are closed. Where the
text downstream still reads as a choice, this section wins.**

| # | question | **owner's ruling** | what it changes below |
|---|---|---|---|
| **D1** | the design describes a **wreck**; the plan builds the finished ship | **BUILD IT FINISHED** | the damage pass is not in scope. `ship_deck_plan.md:274-277` calls placing a pre-broken ship *"the one true blocker"* — it stays blocked, and stays **v2**. Do not partially break anything "for flavour". |
| **D2** | which map, given step 9 destroys everything in 11,438 cells and the hull lands on a fresh colony's arrival site | **A SCRATCH QUICKTEST MAP**, then export and bring the export to the campaign | step 9 is now **free** — nothing on that map is worth keeping. The campaign map is **not touched** this session. |
| **D3** | two of eight heatsinks conflict with the hull footprint | **BUILD WITH SIX** | do **not** regenerate the sheet, so BRIDGE's `SHEET_SHA256` pin stands untouched. Ship runs hotter than designed; one-line fix later. |
| **D4** | east or west for the four `needsManualRotation` machines | **spawn at `rot=1`** rather than rotating afterwards — my recommendation, unopposed | one call per machine instead of two; no reliance on a manual rotation step |
| **D5** | does the export happen this session | **YES — it is the point.** D2 makes the build worthless without it | step 20 is now load-bearing, not optional. See the fallback note on its gizmo route. |

⇒ **Two consequences worth stating plainly.** The riskiest step in the plan
(step 9, the destroy) is now the *cheapest*, because the map is disposable. And
the riskiest step is now **step 20, the export** — it is the only thing that
carries the work off the scratch map, and its gizmo route
(`list_selected_gizmos` → `execute_gizmo` → `click_ui_target`) is the one
unproven dependency in the whole sheet. **Fallback: the owner clicks Export on
the grav engine — three clicks.** Confirm the export file exists before the
scratch map is discarded.

✅ **Two questions this sheet had booked for the live session are already answered
offline**, from Gravship Exporter's own shipped C# source: **floors survive the
round trip** (`GravshipExporter.cs:183-184` captures non-substructure terrain;
`HarmonyPatch_DoGravship.cs:125-158` restores it via `SetTerrain` — the README's
"you can't save floors" is stale), and **extenders export** (the exclusion list
at `GravshipExporter.cs:190-196` is engine, pawns, items only). The 5-minute
small-ship test is **dropped**.

⚠️ **Still unbuildable as written, and NOT fixed by D1–D5** — these are gaps in
the design, not in the plan: no doors anywhere (782 continuous hull tiles = a
sealed interior), no `PilotConsole`, no thrusters, no fuel, no power source, no
water tank; and `SWC_CarboniteRack`, "scanner", "gravlite panels", "astrofuel",
the Spirit Shrine and the oculus floor are **labels with no def behind them**.
`ship_build.md:311` files all of that under "interior detail", which is doing
heavy lifting for a door. **Named for VISION, not invented here.**

---

## 0. What this session is buying, and what it is not

| buys | does not buy |
|---|---|
| 4,057 substructure cells, 4 floors, 1,053 things on the map | any interior furniture — no beds, doors, lamps, tables (`ship_build.md:311-313`) |
| the engine + 8 extenders chained, hull reported liftable | the wrecked-at-t=0 starting state the design actually describes (§6.1) |
| a screenshot that closes the v1 gate | a playable colony aboard it |
| an exported `ShipLayoutDefV2` XML — the reusable artifact | a verified re-import; that needs a **new game start**, i.e. the next load |

---

## 1. Preconditions — check each, one line each

| # | must be true | how you know |
|---|---|---|
| P1 | The world has been generated and a colony map is loaded | `jawa/list_pawns` answers instead of `{"success": false, "message": "No current map. Load a game first."}` (`skills/rimbridge/references/traps.md`, timeout entry) |
| P2 | The owner has given the traffic light | you asked; `agents_def.md` rule 1 — only they see every window |
| P3 | `LIVE BRIDGE TAKEN — CREATE, row 8 gravship build` sent to every peer | `CLAUDE.md` §"The Live Bridge"; the RELEASED half is owed at the end whatever happens |
| P4 | Bigger Gravships' four settings are still 34 / 30 / 12 / 85 | read the FILE, not the panel: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3522759531_GravshipSizeSettings.xml` — see §2 |
| P5 | The companion reports **20** `jawa/` tools | step 2 below. Every later check is uninformative until this reads 20 (`skills/rimbridge/SKILL.md:266-275`) |
| P6 | `runInBackground` is on, or the game window has focus | otherwise every main-thread call times out at 30 s while `ping` answers in 0.5 ms (`traps.md`, `runInBackground` entry) |

🔴 **P4 is the one that silently voids the whole build.** At Bigger Gravships'
own defaults the hull needs a reach of 74.46 and gets 51.80, no layout can rescue
it, and **nothing logs it** (`src/RimMandrake/mapsynth/ship_designs.py:56-60`).

---

## 2. The numbers, with provenance

Every constant the build depends on. **Do not re-derive these live; verify P4 and
go.**

| quantity | value | read from |
|---|---|---|
| grav engine connection radius | **34** | `Config\Mod_3522759531_GravshipSizeSettings.xml` → `BG_gravEngineMaxDistance`; mirrored `src/RimMandrake/mapsynth/ship_designs.py:64` |
| field extender radius | **30** | same file, `BG_gravExtenderMaxDistance`; `ship_designs.py:65` |
| max field extenders | **12** | same file, `BG_gravExtenderMax`; `ship_designs.py:66` |
| max extender distance from engine | **85** | same file, `BG_gravExtenderMaxDistanceFromEngine`; `ship_designs.py:67` |
| engine substructure support | **632.8** | same file, `BG_gravEngineSupport` = 632.79541 (`ship_designs.py:72`, `:80`) |
| extender substructure support | **500** | 🔴 **NOT in that file. There is no `BG_gravExtenderSupport` key.** 500 is Bigger Gravships' *compiled mod default* (`ship_designs.py:73-74`, queue `CREATE.md` C4) |
| capacity cap | **6,632** = 632.8 + 500×12 | `ship_designs.py:82` |
| hull tiles | **4,057** | `ship_bridge.json` → `foundation.cells`; matches `ship_build.md:20` |
| extenders needed | **8** of 12 | `ship_bridge.json` → spawn call 1, 8 ops; `ship_build.md:84` |
| worst-case extender distance | **84.72** against the 85 cap | `AGENT_CREATE_state.md:85` — **0.28 of a cell of margin** |
| origin offset | **+81, +57** | `ship_bridge.json` → `origin`, `"centred on a 250x250 map"` |
| hull extent | **86 × 133**, map cells **x 82–167, z 58–190** | `ship_bridge.json` → `hullExtent`, `mapCells` |
| batch guards | **4,096 ops / 70,000 cells** per call | `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs:2821-2822` |

🔴 **Carry C4's warning forward.** `EXT_SUPPORT = 500` was documented as coming
from the settings file and does not. It is the right value believed for the wrong
reason, and the reason matters: at Vanilla Gravship Expanded's **100** the cap
would be 1,832.8 and at vanilla's **250** it would be 3,632.8 — **both below the
4,057-tile hull.** The build would then fail on *capacity* while every radius in
this table was correct, and you would spend the session looking for a radius bug.
**If the ship refuses to lift, check the cap before you check the radii.**

Largest call in the plan is 782 ops / 3,328 cells — comfortable against both
guards.

---

## 3. Decisions owed BEFORE the session — put these to the owner in ONE message

**D1 and D2 are blocking. D3–D5 want an answer but have a stated default.**

| # | question | my recommendation |
|---|---|---|
| **D1** 🔴 | **Where does the ship go?** The plan centres an 86×133 hull on a 250×250 map at x 82–167 / z 58–190. On a fresh colony the player's own arrival gravship and starting pawns are at the map centre — i.e. **inside this footprint**. | **Survey first (step 5), then choose.** If the arrival ship is in the rect, offset the build clear of it and regenerate: `python3 src/RimMandrake/Utils/rimbench/shipbuild.py --origin X,Z`. Do not build over the colony. |
| **D2** 🔴 | **Is this map disposable?** `jawa/destroy_batch categories=All` over 11,438 cells destroys every building, item and plant in the rect, and the terrain reset destroys plants. On the *shipping* colony that is not reversible by restore — `capture()/restore()` puts the TerrainDef back and does not bring the plants back (`skills/rimbridge/SKILL.md:315-320`). | **Say out loud which map this is.** If it is the shipping colony, take the save at step 6 and treat it as the only undo. If it is a dev quicktest map, skip step 6 and go fast. |
| **D3** | **Two heatsinks are held back** as footprint conflicts — (26,126) inside Mincer, (66,126) inside Neutro Synth (`ship_bridge.json` → `footprintConflicts`). Fixing regenerates `build_sheet_15.json`, trips BRIDGE's `SHEET_SHA256` pin and moves five machines. | **Build with 6 of 8 and file the other two `[v2]`.** The ship does not need them to fly and the regeneration cost lands on another seat mid-session. |
| **D4** | **Four machines have an undetermined facing** — `Autofarmer`, `Autoloom`, `ConveyorOven`, `AutomatedCannery` are emitted `rot=0` with `needsManualRotation` because a footprint cannot tell east from west (`ship_bridge.json`; `NEXT_RELOAD.md:279-281`). | **Spawn each at `rot=1` (East), screenshot, flip to 3 if it reads wrong.** Each is its own single-op call, so the facing is a call parameter — there is no "rotate by hand" step, and no reason to leave four machines facing north. |
| **D5** | **Does the export happen this session?** The exporter's button is a gizmo on the grav engine; it writes to the *Config* folder, not the repo. | **Yes, and copy the output into the repo the same hour** (step 21). An export left in `Config\GravshipExport\` is one reinstall from gone. |

⚠️ **Note what is NOT on this list.** The engine position is settled — the deck
plan's shrine-heart at grid (45,92) = map **(126,149)**, costing one extra
extender, is already stamped into `ship_bridge.json` (`ship_build.md:76-95`).
Do not reopen it.

---

## 4. The ordered build sequence — 21 steps in six phases

**Grouped so a failure at step N does not invalidate 1..N-1.** Phase A mutates
nothing. Phase B is a reversible probe. Phase C is the only destructive phase.
Phase D is the build and is resumable per call. Phases E and F are evidence and
delivery.

### Driving it

There is **no committed runner** for `ship_bridge.json` — the 2026-08-13 rehearsal
was driven ad hoc. Drive it as a library, never `--json` on the command line
(`skills/rimbridge/SKILL.md:38-49`):

```python
import sys, json
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
P = json.load(open("/mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/ship_build/ship_bridge.json"))
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token); rb.connect()
```

Keep **one** connection open across the whole build. `resolve_endpoint()` scrapes
the token out of `Player.log`, so it is never last launch's value.

---

### Phase A — establish. No mutation. Abort here costs nothing.

**Step 1 — connect and confirm the bridge is awake.**
```python
rb.call("rimbridge/get_bridge_status", {})
```
✅ **Passes when:** fields are populated. **All-null fields with a ~5 s delay is
`runInBackground` off, not a hung game** (`traps.md`).

**Step 2 — tool census. 🔴 Nothing below is informative until this reads 20.**
```python
names = [t["name"] for t in rb.list_tools()]
print(sum(1 for n in names if n.startswith("jawa/")))
```
✅ **Passes when: exactly 20.** 18 = the deploy lost `--gm`; 17 = the
pre-appearance build; 7 = an older companion; 0 = the bundle did not load
(`skills/rimbridge/SKILL.md:266-275`). **A stale companion is also how
`layer='foundation'` comes back as `layer must be 'top' or 'under'`**
(`traps.md`, "Fixed in the companion").

**Step 3 — read the map size off the game, not off a note.**
```python
r = rb.call("jawa/get_terrain_batch", {"rects": "1,1,1,1"})
print(r["mapSize"])
```
✅ **Passes when:** `mapSize == {"x":250,"z":250}`. Anything else → **regenerate
before firing anything**: `python3 src/RimMandrake/Utils/rimbench/shipbuild.py --center <x>,<z>`.
⚠️ `NEXT_RELOAD.md:235-243` records the file contradicting itself on whether 250×250
is the colony map or a debug map. **This step settles it; do not settle it from a
document.**
⚠️ `jawa/spawn_batch` does **not** return `mapSize` — only `jawa/set_terrain`,
`set_terrain_batch` and `get_terrain_batch` do
(`JawaBenchTerrainTools.cs:187`, `:370`, `:483`). `shipbuild.py:1010-1011` says all
three including spawn_batch; that line is wrong. Use `get_terrain_batch`.

**Step 4 — confirm the four settings (offline, no bridge call).**
```bash
grep -E "gravEngineMaxDistance|gravExtenderMaxDistance|gravExtenderMax|gravEngineSupport" \
  "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/Mod_3522759531_GravshipSizeSettings.xml"
```
✅ **Passes when:** 34 / 30 / 12 / 85 as in §2. ⚠️ **An absent key means DEFAULT,
not zero** — only non-default values are written.

**Step 5 — site survey. This answers D1.**
```python
rb.call("jawa/get_terrain_batch", {"rects": "82,58,86,133", "layer": "foundation"})
rb.call("jawa/list_pawns", {"rect": "82,58,86,133"})
```
✅ **Passes when:** `distinctTerrains` contains **no `Substructure`** and
`list_pawns` returns **nobody you care about**. 🔴 A `Substructure` hit means the
player's arrival gravship is inside the footprint — **stop and take D1 to the
owner.** Building over it destroys the colony's own ship.

**Step 6 — baseline save. This is the abort anchor (see §8).**
```python
rb.call("rimworld/save_game", {"saveName": "pre_row8_gravship"})
```
✅ **Passes when:** it returns a path. ⚠️ `save_game` **ignores the name you give
it** and writes `rimbridge_save_<timestamp>.rws` (`skills/rimbridge/SKILL.md:66-67`)
— read the returned path and write it down; you cannot find this save by name.

---

### Phase B — probe. Two small reversible calls that catch every class of failure the big build can hit.

⚠️ **`NEXT_RELOAD.md:245-246`: do not discover the placement by watching 4,057
tiles land.**

**Step 7 — corner probe. Proves the coordinate frame.**
```python
rb.call("jawa/set_terrain_batch",
        {"ops": "Sand:82,58,3,3;Sand:165,58,3,3;Sand:82,188,3,3;Sand:165,188,3,3"})
rb.call("rimworld/screenshot_cell_rect",
        {"x": 82, "z": 58, "width": 86, "height": 133, "paddingCells": 6})
```
✅ **Passes when:** `cellsOutOfBounds == 0`, `cellsFailedVerify == 0`, and the
screenshot shows **four sand squares bounding the intended footprint** — not one
square in a corner of the map.

**Step 8 — foundation probe. Proves the layer works on THIS companion build.**
```python
rb.call("jawa/set_terrain_batch",
        {"ops": "Substructure:82,58,5,5", "layer": "foundation"})
```
✅ **Passes when:** `cellsChanged == 25`, `cellsFailedVerify == 0`.
🔴 **`cellsFailedVerify > 0` here means a floor is present and `SetFoundation` is
refusing — silently, at the write.** Measured 25/0/25 on bare ground against
**0/25** with `MetalTile` laid first (`traps.md:225-229`). **Do not proceed to
step 11 until this reads 0.** `cellsChanged` is true and useless on its own.
🔴 `layer must be 'top' or 'under'` here = stale companion → back to step 2.

---

### Phase C — clear the site. 🔴 The only destructive phase. D2 must be answered first.

**Step 9 — destroy things in the footprint.**
```python
rb.call("jawa/destroy_batch", {"rects": "82,58,86,133", "categories": "All"})
```
⚠️ **`categories` is PLURAL.** The singular key is dropped by the binder without
an error and you silently get the `Plant` default
(`JawaBenchTerrainTools.cs:703-714`; `NEXT_RELOAD.md:251`). Pawns are never
destroyed by this tool whatever you pass.
✅ **Passes when:** per-category counts come back and the rect is visibly clear.

**Step 10 — reset terrain to bare ground. 🔴 `destroy_batch` removes THINGS, never TERRAIN.**
```python
sand = P["foundation"]["ops"].replace("Substructure:", "Sand:")
rb.call("jawa/set_terrain_batch", {"ops": sand, "layer": "top"})
```
✅ **Passes when:** `cellsFailedVerify == 0` over 4,057 cells.
⚠️ **This step is why the rehearsal went from 103 refused foundation cells to 0**
(`NEXT_RELOAD.md:258-262`). Reusing the foundation ops with the def swapped gives
an exact hull-shaped cover — do not paint the bounding box instead, it sands
7,381 cells of map that are not the ship.
⚠️ Painting Sand destroys plants and they do not come back
(`skills/rimbridge/SKILL.md:315-320`).

---

### Phase D — the build. Each step is one or more independent calls; a failure resumes at the failed call.

🔴 **The order below is the only order that works: foundation → floors → things.**
A floor is a one-way door — substructure cannot be retrofitted, and the refusal is
silent (`traps.md:225-229`).

**Step 11 — foundation. ONE call, 4,057 cells, 132 rects.**
```python
rb.call("jawa/set_terrain_batch", {"ops": P["foundation"]["ops"], "layer": "foundation"})
```
✅ **Passes when:** `cellsFailedVerify == 0` **and**
`cellsChanged + cellsAlreadyCorrect == 4057` **and** `cellsOutOfBounds == 0`.
🔴 Any non-zero `cellsFailedVerify` — **stop.** Go back to step 10 for those cells;
do not lay floors over them, that makes it permanent.

**Step 12 — floors. FOUR calls.**
```python
for name, t in P["terrain"].items():
    rb.call("jawa/set_terrain_batch", {"ops": t["ops"], "layer": "top"})
```
✅ **Passes when:** each returns `cellsFailedVerify == 0`; totals are MetalTile
3,328 · SterileTile 507 · WoodPlankFloor 197 · CarpetMarine 25 = 4,057
(`ship_bridge.json` → `terrain`).

**Step 13 — the grav engine, then the eight extenders. Order is load-bearing.**
```python
rb.call("jawa/spawn_batch", {"ops": "GravEngine:126,149"})
rb.call("jawa/spawn_batch", {"ops": P["spawn"][1]["ops"]})   # 8 GravFieldExtender, in chain order
```
✅ **Passes when:** `spawned == 1` then `spawned == 8`, `failed == 0`.
⚠️ **`GravEngine:126,149` is a CENTRE, not a corner** — a 3×3 occupies 125–127 ×
148–150 (`traps.md`, "Multi-cell things spawn CENTRED").
⚠️ **The 8 ops are already in the chain order `ship_build.md:92-99` requires**
(verified against the ops string), and `spawn_batch` applies ops in order. If the
engine's connected-substructure readout at step 18 comes up short, the fallback is
eight separate calls in that same order.

**Step 14 — hull walls. 782 things, one call.**
```python
c = P["spawn"][2]   # GravshipHull, stuff Steel
rb.call("jawa/spawn_batch", {"ops": c["ops"], "stuff": c["stuff"], "rot": c["rot"]})
```
✅ **Passes when:** `spawned == 782`, `failed == 0`, `perDef` shows GravshipHull.
🔴 **`stuff` is a call-level parameter and it is Steel.** Dropping it does not
fail — it builds the hull out of the def's default material.

**Step 15 — conduit. Two calls: PowerConduit ×184, HiddenConduit ×1.**
✅ **Passes when:** 184 and 1, `failed == 0`. ⚠️ The single `HiddenConduit` is not
cosmetic — it sits where a keel tile also carries a node, and an exposed
`PowerConduit` there would have wiped or refused an extender with nothing in the
log (`ship_build.md:101-106`).

**Step 16 — machines and factory fittings. The remaining 21 calls.**
```python
for c in P["spawn"][5:]:
    if c["needsManualRotation"]: continue      # step 17 owns these four
    a = {"ops": c["ops"]}
    if c["stuff"]: a["stuff"] = c["stuff"]
    if c["rot"]:   a["rot"]   = c["rot"]
    rb.call("jawa/spawn_batch", a)
```
✅ **Passes when:** every call returns `failed == 0`. Expect
`VFEFactory_FactoryHopper` 51, `VFEFactory_Heatsink` **6** (not 8 — D3),
`VFEFactory_Booster` 2, and one each of the 18 machines.
⚠️ **These defNames are RESOLVED, not live-verified** (`ship_build.md:256-258`).
**Fallback when one fails:** `jawa/get_def {"defName": "<name>"}` and read the
supplying mod back; a failure here is one machine, not the build.

**Step 17 — the four undetermined facings (D4).**
```python
for c in P["spawn"]:
    if c["needsManualRotation"]:
        rb.call("jawa/spawn_batch", {"ops": c["ops"], "rot": 1})   # 1 = East
```
✅ **Passes when:** all four spawn, then a screenshot of each reads right-way-round.
Wrong → destroy that one cell and re-spawn at `rot: 3`. **`rot` is 0=N 1=E 2=S
3=W** (`JawaBenchTerrainTools.cs:520-524`); out-of-range is range-checked at entry
rather than silently normalised into a different valid facing.

---

### Phase E — prove it. This is what closes the gate.

**Step 18 — ask the engine whether it has a ship.**
```python
rb.call("rimworld/click_cell", {"x": 126, "z": 149})       # selects the GravEngine
rb.call("rimworld/list_selected_gizmos", {})
rb.call("rimworld/take_screenshot", {})                     # the inspect pane
```
✅ **Passes when:** the engine's readout shows the substructure **connected**
(not red) and the tile count reads at or near 4,057 against a 6,632 cap.
🔴 **This is the real test of the whole design.** `GravshipHull` spawns happily on
bare ground because `GenSpawn` checks no affordance — **a substructure-less ship
is buildable and is not a gravship, which is worse because everything looks
right** (`traps.md:229`). Red substructure here with everything else green means
the settings check at step 4 lied, or the cap (§2) is the constraint that bound.

**Step 19 — the photograph. This is the gate's evidence.**
```python
rb.call("rimworld/screenshot_cell_rect",
        {"x": 82, "z": 58, "width": 86, "height": 133, "paddingCells": 8,
         "fileName": "row8_gravship_built"})
```
✅ **Passes when:** you can see a ship. Save the returned path; **the gate is
"seen", and a path to the image is what "seen" means in a report**
(`V1_SCOPE.md:40-42`).

---

### Phase F — deliver the artifact.

**Step 20 — export.** The button is a `Command_Action` gizmo on the grav engine,
labelled **"Export Gravship Layout"**
(`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3576790938\1.6\Source\GravshipExport\Exporter\Patch_GravEngine_GetGizmos.cs:21`).
It opens `Dialog_NameShip`.
```python
rb.call("rimworld/click_cell", {"x": 126, "z": 149})
g = rb.call("rimworld/list_selected_gizmos", {})            # find "Export Gravship Layout"
rb.call("rimworld/execute_gizmo", {"gizmoId": "<id from above>"})
rb.call("rimworld/get_screen_targets", {})                  # the name dialog
rb.call("rimworld/click_ui_target", {"targetId": "<the accept control>"})
```
✅ **Passes when:** `Config\GravshipExport\<defName>.xml` exists.
⚠️ **This gizmo path has never been driven from the bridge.** Fallback: **ask the
owner to click it** — select the engine, click Export, type the name. That is
three clicks and it is not worth losing the artifact over.
🔴 **The export captures `engine.AllConnectedSubstructure` only**
(`GravshipExporter.cs:133`). Anything not in the connected field is silently
absent from the XML — so **step 18 must have passed before this is meaningful**,
and the exported row count should be checked against 4,057.

**Step 21 — get the artifact into the repo. It is a work product, not a cache.**
```
C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport\<defName>.xml
                                                                                                  \<defName>.png
```
(path from `GravshipExporter.cs:73`, `:83-84`.) Copy both into the repo under
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_build\export\` and commit with
an explicit pathspec, same hour. `CLAUDE.md` §"Commit AND PUSH": unreproducible +
value persists = **commit it**.

---

## 5. What genuinely cannot be decided offline — the justification for the session

Short, and shorter than it was this morning (see §7).

1. **The map size and the map's contents.** Whether it is 250×250, and whether the
   arrival gravship and the colonists are standing in the footprint. Steps 3 and 5.
2. **Whether the hull actually reports connected and liftable** at the owner's
   settings, with the extender chain as laid. Step 18. Every offline check says
   yes at 100% coverage and 0.28 of a cell of margin; nothing offline can show the
   engine's own readout.
3. **Whether the 26 resolved VFE defNames registered.** Declared in XML ≠ present
   in `DefDatabase` on a 580-mod stack (`ship_build.md:256-258`). Step 16.
4. **East or west for the four rotated machines.** A footprint cannot express it
   and neither can a def. Step 17 — it is a look, not a calculation.
5. **Whether the exporter's gizmo can be driven from the bridge.** Step 20.

**Everything else on the old list was answerable from files, and has been
answered.** That is §7, and it is the lesson `V1_SCOPE.md:140-144` already
recorded once: *before booking the scarcest resource we have, check whether the
question is answerable offline.*

---

## 6. 🔴 Not buildable as written — every gap is a decision someone should make deliberately

CREATE's standing question is *does this exist as a real thing the game can load,
and is the spec complete enough to build from without guessing?* Here it is not,
in four different ways. **None of these block the 21 steps above** — the plan
builds what it builds — but a reader of the design will not recognise what lands.

### 6.1 🔴 The design describes a WRECK. The plan builds a finished ship.

`ship_deck_plan.md:70-77` is explicit: substructure **40–55% disconnected and
showing red**, hull walls **missing in large sections**, factory machines present
as **broken scrap** under the owner's "SACRED SCRAP" ruling — inviolate until
repaired. `ship_designs.md:18-20` names a render of *"the stripped structural
wreck the campaign begins from"*.

The plan lays 4,057 fully-connected cells, a complete 782-tile wall ring and 18
**working** machines. **The t=0 state the campaign's premise rests on is not
expressed anywhere in `ship_bridge.json`, and there is no damaged-machine def.**
`ship_deck_plan.md:274-277` names this itself: *"how to place a large pre-broken
ship as the start save … **this is the one true blocker between design and
execution**"* — and it is still open.

⇒ **Recommendation: build the intact ship anyway, this session.** It closes the
gate, it is the export artifact, and damage is subtractive — a later pass deletes
walls and swaps machines for wrecks. But **say plainly in the report that the ship
on the map is the repaired end-state, not the campaign's opening ship**, or the
owner will see the screenshot and think row 8 is finished.

### 6.2 The ship has no systems, and no way in.

Present in the design, absent from all 26 spawn calls (checked against
`ship_bridge.json`, not against a summary):

| missing | design says | consequence |
|---|---|---|
| **Doors — every one** | `ship_build.md:176-177` lists `Autodoor`/`Door` in the vocabulary | 782 continuous hull tiles: **the interior is sealed and unreachable** |
| **`PilotConsole`** | `ship_deck_plan.md:93`; `ship_build.md:129` names it as zone M's content | 113 tiles of SterileTile and no console |
| **Thrusters** | `ship_deck_plan.md:110`; `ship_build.md:148` | **the ship cannot fly** |
| **Chemfuel tanks** | `ship_deck_plan.md:253`; zone U, 90 tiles | no fuel |
| **Water tanks** | `ship_build.md:150`, zone W | 90 tiles of floor colour, no tank |
| **Power generation, batteries, switches** | `ship_deck_plan.md:110`, `:122` | 184 conduits carrying nothing from nowhere |
| **Shuttle pads** | `ship_designs.md:461-462`; zone H, 420 tiles | bare floor at the prong tips |
| **Vac-barrier / radiator bay** | `ship_deck_plan.md:164-169`, RESOLVED as a dedicated wing | **no such zone exists in the 16-zone map at all** |
| **Turrets, firefoam, shield** | in the vocabulary at `ship_build.md:180-181` | undefended |
| **The shrine's contents** | `ship_designs.md:86` scrap-totem shrine | T is 25 tiles of CarpetMarine and the engine — **there is no totem** |

`ship_build.md:311-313` owns this honestly — *"interior detail is not placed"* —
but "interior detail" is doing heavy lifting for *doors, thrusters, the pilot
console and the power supply*. **Furniture is v2; a door is not furniture.**

## 🔴 STEP 19b — CUT A DOOR. PROMOTED FROM "IF TIME REMAINS" TO A GATE STEP.

**PROJECT named the open criterion for row 8 as BOARDABLE, 2026-08-13. A sealed
hull is not boardable, so this stopped being optional the moment that was said.**
782 continuous hull tiles means no colonist can ever get inside; the ship would
pass every flight check and fail the only criterion left.

⚠️ **Do not skip this if the session is running short.** A ship with a door and
no pilot console still clears the gate. A ship with a console and no door does
not. **If exactly one thing gets placed after step 19, it is a door.**

**Defs verified in Core, not remembered:** `Door` and `Autodoor` —
`Data/Core/Defs/ThingDefs_Buildings/Buildings_Structure.xml:66` and `:89`. Use
**`Autodoor`** if power reaches it; plain `Door` otherwise, and plain `Door` is
the safe pick because the ship has no power source (§6.2).

**Procedure — mechanical, no judgement needed mid-build:**
1. After the hull walls exist, query the wall ring on the **south face** of the
   hull rect (`x82-167, z58-190`) at roughly the x-midpoint, `x≈124`.
2. Pick one wall cell there. **Destroy that one wall thing**, then spawn `Door`
   at the same cell.
3. Cut a **second** door on a different face. One door is a single point of
   failure — if it lands on an interior partition rather than the exterior
   wall, the ship is still sealed and the screenshot will not show it.

🔴 **The gate test is NOT "a door exists".** Order a colonist to walk to an
interior cell and confirm they **arrive**. Pathing is the only thing that proves
boardable — a door in an interior wall, a door blocked by substructure edge, or
a door with no reachable route all look correct in a screenshot. **Shoot the
colonist standing inside.**

⇒ **After the door, if time remains:** a `PilotConsole`, then everything else in
the table above. Those are vanilla defs already named in `ship_build.md:176-179`.
Everything beyond them is a genuine v2 authoring pass and should be filed, not
improvised.

### 6.3 Named by label, or not a def at all

Things CREATE would have to guess. Each needs a decision, not a guess:

- `ship_deck_plan.md:93` **"scanner"** — no candidate def named anywhere.
- `ship_deck_plan.md:221` **"gravlite panels"** — a material label.
- `ship_deck_plan.md:224` **"VGE astrofuel"**, `:180`/`:222` **`VFE_BasicFactories`
  → `VFE_ComplexFactories`** written as research defNames — unverified.
- `ship_distinctive_features.md:27`, `:32` **`SWC_CarboniteRack`** — 🔴 **this def
  does not exist.** It belongs to a custom mod spec (`carbonite_trophy_mod.md`)
  that has not been built. The carbonite reliquary is unbuildable today, full stop.
- `ship_distinctive_features.md:566` **"Spirit Shrine"** — from Afterlife, a mod
  that is only *ADOPT-leaning* (`:593`), not adopted.
- `ship_distinctive_features.md:194` **"oculus floor — a single transparent tile"**
  — no such terrain exists.
- `ship_distinctive_features.md:97` **"one small altar/shrine décor object per
  pod"** ×7 — no def, no source mod.

### 6.4 Numbers in the design that contradict the build

If CREATE reads the design docs mid-session instead of this sheet, these are the
lines that will mislead:

| stale | says | truth |
|---|---|---|
| `ship_deck_plan.md:5`, `:29`, `:36`, `:302` | **2,000-tile cap**, ~150 headroom | 4,057 / 4,800, **743 headroom** (`ship_build.md:20`) |
| `ship_deck_plan.md:44-46` | engine reaches **19**, 6 extenders reach **16** | **34 / 30 / 12** (§2) |
| `ship_deck_plan.md:50-51`, `:56-60`, `:62` | a **1,732-tile** layout, ≤15 tiles off the keel, 6 extenders | a different ship entirely |
| `ship_designs.md:15`, `:90`, `ship_deck_plan.md:136` | **7 extenders** | **8** — 7 is only valid with the engine at (55,34), which the build rejects for the shrine-heart (`ship_build.md:80-95`) |
| `ship_designs.md:101` vs `:113` | cap **6,632** vs cap **4,800**, in one file | 6,632 is the live figure; 4,800 is what every per-design check was run against |
| `ship_deck_plan.md:122` vs `ship_build.md:254` vs `ship_bridge.json` | **4** heatsinks vs **8** vs **6** | **6 are spawned** (D3) |

⇒ **Recommendation: this sheet is authoritative during the session.** VISION owns
`design/Jawa/worldbuilding/` now (`AGENT_CREATE_state.md:92-93`) — file the stale
lines at VISION rather than editing them, and note the extender count and the tile
cap as the two that would actually change a decision.

---

## 7. ⭐ Two questions this plan was supposed to leave open — both are ANSWERED, offline

`V1_SCOPE.md:145-148` calls the export round trip *"the residual live test"* and
`NEXT_RELOAD.md:304-321` books five minutes of the session for it. **It does not
need the game. Gravship Exporter ships its complete C# source**, at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3576790938\1.6\Source\`.

**Q1 — do floors survive the round trip? YES.**
- Export: `GravshipExport\Exporter\GravshipExporter.cs:183-184` —
  `if (terrain != null && !terrain.IsSubstructure) shipCell.terrainDef = terrain.defName;`
  Every non-substructure terrain in every hull cell is captured.
- Import: `GravshipExport\HarmonyPatch_DoGravship.cs:12` patches
  `ScenPart_PlayerPawnsArriveMethod.DoGravship`, and its Postfix at `:125-158`
  resolves each `cell.terrainDef` and calls `terrainGrid.SetTerrain(world, terrainDef)`.

So the README's *"You can't save floors"* is **stale**, and the shipped example's
204 non-null `terrainDef` cells were never a contradiction — they were the answer.
⚠️ One real caveat from the same code: `:150` skips a cell when
`!terrainDef.layerable && current != terrainDef`. Our four floors are all layerable
floors, so they apply; a *natural* terrain would not.

**Q2 — do the engine and the extenders survive? Engine NO by design, extenders YES.**
`GravshipExporter.cs:190-196` is the entire exclusion list:
`if (thing.def == engine.def) continue;` · `if (thing is Pawn) continue;` ·
`ThingCategory.Item` skipped. **The engine is excluded because it is the anchor of
the capture** — the new game re-creates it (`ship_build.md:38-60`).
**`GravFieldExtender` is an ordinary Building and matches no exclusion, so it
exports.** `ship_build.md:61-66` flags this as inference *"[Extender] appears
nowhere in the assembly"*; the source settles it.

⇒ **Recommendation: DROP the 5-minute small-ship test.** Reading the code is
strictly stronger evidence than a small ship would have been, and the only thing
the small test could add — that the *import* works end to end — needs a **new game
start**, which this session does not have. Export the real ship (step 20), commit
it (step 21), and validate the import on the next start.

---

## 8. Unproven tools, and the fallback for each

| tool | state | fallback if it fails |
|---|---|---|
| `jawa/set_pawn_rotation`, `jawa/set_pawn_style`, `jawa/set_pawn_xenotype` | 🆕 **never executed** (`skills/rimbridge/SKILL.md:266-275`) | **Not used by this plan at all.** No step depends on them. |
| `jawa/list_factions` | 🆕 never executed | not used here; it is row 5/row 1's tool |
| `jawa/set_roof_batch` / `get_roof_batch` | 🆕 never executed | not used — **the ship is roofless as built**, and that is a v2 gap, not a step |
| `rimworld/list_selected_gizmos` + `execute_gizmo` + `click_ui_target` | proven to exist in the tool reference (`docs/tool-reference.md:801-812`, `:631`); **this gizmo path never driven** | **step 20**: ask the owner to click Export on the engine. Three clicks. |
| `rimworld/click_cell` to select a *building* | documented (`:1045`), reports before/after selection; not proven on a GravEngine | select by clicking a hull cell instead and walk the selection, or fall back to the owner |
| `jawa/spawn_batch` `rot` parameter | deployed `2f74209`, **live from the next game start** (`ship_build.md:234`) | if every thing lands facing north, `rot` did not take: the deploy is stale → step 2's census will already have told you |

🔑 **The three brand-new pawn tools are not on this plan's critical path.** If a
peer wants them proven, that is a separate errand on the same bridge session — it
does not belong inside the build.

---

## 9. Abort and resume

**What is on the map after each phase, and where the next attempt starts.**

| aborted after | left on the map | resume at |
|---|---|---|
| Phase A (1–6) | **nothing changed** | step 1 |
| step 7 | four 3×3 sand patches at the hull corners | step 7 (idempotent) |
| step 8 | a 5×5 patch of Substructure at (82,58) | step 8 — re-running is a no-op, `cellsAlreadyCorrect` absorbs it |
| step 9–10 | 🔴 **a cleared, sanded 86×133 rect and nothing else.** Irreversible for plants | step 9. **This is the point of no return; D2 must have been answered.** |
| step 11 | 4,057 substructure cells on bare sand — invisible from above, real in the grid | step 12. **Do not re-run step 10** — sanding over foundation is untested and pointless |
| step 12 | a floor plan, no walls: a ship-shaped floor | step 13 |
| step 13 | engine + 8 extenders standing alone on the floor | step 14 |
| step 14–17 | a progressively more complete ship | **the failed call only.** Every spawn call is independent; re-running a completed one duplicates things, so track which calls returned `failed == 0` |
| step 18–19 | the finished hull | step 18 — read-only, re-run freely |
| step 20 | the finished hull, no artifact | step 20, or the owner clicks it |

🔴 **The undo is the save from step 6, not a terrain restore.**
`capture()/restore()` returns the TerrainDef exactly — 2,601 cells, 0 wrong — and
**does not bring back the plants the paint destroyed**
(`skills/rimbridge/SKILL.md:315-320`). On a map that matters, the save is the undo.

🔴 **Whatever happens, send the release.** A `TAKEN` with no `RELEASED` marks the
bridge occupied forever:

```
LIVE BRIDGE RELEASED — CREATE, <what got built, which step it stopped at,
                       and that an 86x133 sanded rect / hull is left at x82-167 z58-190>
```

**Say what you left behind.** The next seat inherits this map.
