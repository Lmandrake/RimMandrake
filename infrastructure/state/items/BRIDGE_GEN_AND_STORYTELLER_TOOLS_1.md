# BRIDGE_GEN_AND_STORYTELLER_TOOLS_1 — 14 more bridge tools, owner said "keep building" while the game loads

Filed 2026-08-29, FOUNDRY. Sibling to `BRIDGE_LORDS_AND_GAPS_TOOLS_1` (the first 10).
Written and BUILT during the game's own LOADING window — deploy needs the game closed,
which loading is not, so this batch is source+build only until the next down-window.

## Spec

New file `JawaBenchGenTools2.cs` (4 tools, ungated — map-generation/roof-repair
primitives, same tier as `jawa/prefab_place`/`build_batch`, not incidents):
- `jawa/scatter_at` / `jawa/run_genstep` — `GenStepDef.genStep` (the already-constructed
  instance the XML loader builds — there is no `genStepClass` field to reflect on, a
  guess corrected mid-build by the compiler) `.ForceScatterAt`/`.Generate` on a live map.
- `jawa/run_basegen_symbol` — `BaseGen.globalSettings.map`/`symbolStack.Push`/`Generate()`.
  ⚠️ HIGH RISK, can spawn a full populated settlement per the roster's own `settlement`
  symbol example.
- `jawa/fix_floating_roofs` — `RoofCollapseCellsFinder.CheckAndRemoveCollpsingRoofs`.

New file `JawaBenchStorytellerTools2.cs` (7 tools):
- `jawa/spawn_mech_cluster` (GATED) — `MechClusterGenerator.GenerateClusterSketch` +
  `MechClusterUtility.SpawnCluster`, the exact utility `Verb_MechCluster` calls.
- `jawa/incident_queue_clear` (GATED) — `IncidentQueue.Clear()`; it is the WHOLE
  capability, the backing list has no per-item Remove.
- `jawa/set_game_speed` (ungated, same tier as `time_set_ticks`) — `TickManager.CurTimeSpeed`.
- `jawa/letter_list` (ungated) / `jawa/letter_send_delayed` (GATED, same tier as
  `send_letter`) — `LetterStack.LettersListForReading` / `.ReceiveLetter(..., delayTicks)`.
- `jawa/av_effect` (ungated, cosmetic only) — song/shake/fleck bundled: `ForcePlaySong`,
  `CameraShaker.DoShake`, `FleckMaker.ThrowMetaIcon`.
- `jawa/set_thing_props` (ungated) — retroactive quality/HP/faction/style on an
  ALREADY-SPAWNED thing; `build_batch`/`spawn_batch` only ever set these at spawn time.
- `jawa/pawn_set_guest_status` (ungated, same tier as `set_pawn_faction`) —
  `Pawn_GuestTracker.SetGuestStatus(Faction, GuestStatus)`, the last unbuilt row in the
  roster's §0. Self-contained — the engine call already runs every notify/refresh, none
  of the usual pawn-edit refresh traps apply.

New file `JawaBenchMiscTools2.cs` (2 tools, ungated — added after cross-checking the
OWNER-CULLED 185-row roster, `design/Jawa/bridge/capability_roster_data.py`
+ `dll_capability_roster.decisions.json` (posture DEFAULT INCLUDE, 5 struck), against
the live tool surface by name-token match, then hand-verified with a grep. Only 3 of
185 rows came back uncovered; 2 were solid, 1 (`Find.UIRoot`, HARD, no named mechanism)
was skipped as too vague):
- `jawa/take_screenshot` — `ScreenshotTaker.TakeNonSteamShot(fileName)`. ⚠️ Writes to
  RimWorld's OWN Screenshots folder, NOT the owner's F10/Steam screenshot location
  ([[rimworld-screenshot-location]]) — said loudly in the tool's own Description.
- `jawa/rebuild_dirty_regions` — `RegionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms()`,
  a lighter alternative to `map_commit`'s always-full `RebuildAllRegionsAndRooms()`.

## Verify

Built clean: `build.py --gm` → 0 errors, 0 warnings, second pass after fixing two source
mistakes the FIRST build caught (`GenStepDef.genStepClass` doesn't exist — the real field
is `genStep`, an instance, not a Type; and a doubled `BaseGen.BaseGen.` reference). 274
unique `jawa/…` names total, no collisions. **Not deployed — game was LOADING, not down,
when this batch was written; `--apply` needs the process closed.** Deploy at the next
down-window, then prove each live (none of the 11 has ever been observed running):
`run_basegen_symbol` and `spawn_mech_cluster` are the two most worth a careful first call
(irreversible / spawns a hostile threat respectively).

## Live-verify 2026-08-30, FOUNDRY — 9 of 11 PASS, `letter_list` BROKEN. Not closed.

Full 585-mod list, fresh quicktest map. The two HIGH-RISK calls were fired on the
owner's explicit go-ahead, at map corners, game paused, and **both were cleaned up
immediately afterwards** — final state: zero mechs, zero hostile pawns, only the
map's own pre-existing `LordJob_FleshbeastAssault` remains, game paused.

### 🔴 `jawa/letter_list` — BROKEN. NREs on any letter with no look targets.

Worked at `count: 0` on an empty stack. The moment a real letter arrived:
```
jawa/letter_list {} -> success false
  "Object reference not set to an instance of an object"
  System.NullReferenceException
```
Cause, exactly: `JawaBenchStorytellerTools2.cs:245` builds each row with
```csharp
lookTargets = l.lookTargets.IsValid ? l.lookTargets.ToString() : null
```
`Verse/LookTargets.cs:7` declares **`public class LookTargets`** — a *class*, not a
struct — so `Letter.lookTargets` is null for any letter sent without targets, and
`.IsValid` throws. Most letters have no look targets, so this tool fails on the
normal case and only worked because the stack happened to be empty.
**Fix is one guard**: `l.lookTargets != null && l.lookTargets.IsValid`.

### ✅ `jawa/letter_send_delayed` — PASS, with a picture
`{label: "FOUNDRY probe", delayTicks: 300}` → `arriveAtTick: 5922`. Not on the
stack immediately (`letter_list` → 0); after `step_game_ticks 400` a screenshot
shows **"FOUNDRY probe" sitting in the letter pane** on screen. The delay queue
works. (Its arrival is also what exposed the `letter_list` bug above.)

### ✅ `jawa/set_game_speed` — PASS, and it FIXES a documented silent failure
`silent-failures.md` records `rimworld/set_time_speed` reporting the speed it set
while the game stayed paused and `ticksGame` never moved. This one does not:
```
Paused -> Normal   state.paused false, timeSpeed "Normal",  ticks 5443 -> 5620 over 3 real s (+177)
Normal -> Paused   state.paused true,  timeSpeed "Paused",  ticks 5622 -> 5622 over 3 real s (   0)
```
Verified by tick delta across wall-clock, not by the return value. ⇒ **this is the
working route for time speed on this bridge.**

### ✅ `jawa/scatter_at` — PASS, placed real content AT the named cell
Four `GenStep_Scatterer` defs forced at `170,100`. Read-back of the region:
`SteamGeyser` **at exactly 170,100**, plus `Wall` x33, `AncientFence` x11,
`Door` x4, `Column` x3, `AncientGenerator` x1 from the ruins/shrine scatterers.

### ✅ `jawa/run_genstep` — PASS, measured map-wide
`{genStepDef: "SteamGeysers"}` → resolved `genStepType:
RimWorld.GenStep_ScatterGeysers`, `threw: null`; whole-map `SteamGeyser` count
**13 → 18**. `ScatterRuinsSimple` likewise raised `AncientFence` map-wide.
⚠️ **Instrument note that nearly produced a false negative**: counting geysers by
walking 125x125 rects with `limit: 4000` returned **0 before and 0 after** — the
documented `jawa/list_things` truncation trap, where truncation reads as absence.
The `defName` filter with `countMatched` is the correct instrument.

### ✅ `jawa/run_basegen_symbol` — PASS (HIGH RISK, fired on go-ahead, then removed)
`{symbol: "settlement", rect: "40,40,26,26"}` into a rect cleared to **0 things**:
```
things   0 -> 340   Wall x162, Sandbags x55, StandingLamp x12, Door x12, Battery x6,
                    FermentingBarrel x6, Bed x4, Turret_MiniTurret x4, meals, weapons
pawns   38 ->  51   (+13)
lords            ->  LordJob_DefendBase, faction AG_XenohumanPirates, 13 members
```
Exactly the documented behaviour: buildings + inhabitants + a DefendBase Lord.
**Removed immediately** — `lord_destroy` (13 members) then `clear_area` (474
things); pawns back to 38, hostile pawns `[]`.

### ✅ `jawa/spawn_mech_cluster` — PASS (GATED, fired on go-ahead, then removed)
`{at: "28,228", points: 500, startDormant: true, canAssaultColony: false}` — map
corner, ~130 cells from the colony, game paused:
```
spawnedThingCount 35: Wall x28, PsychicDroner, ActivatorProximity,
                      UnstablePowerCell, Gloomlight, Turret_AutoChargeBlaster
pawns +2:  Mech_Cyclops48001, AM_Daggersnout48003  (faction "Kilyoth Mechhive")
lord:      LordJob_SleepThenMechanoidsDefend, 2 members  <- the dormant defend lord
```
Every component the description promised. **Removed immediately** — `lord_destroy`
then `clear_area` (881 things); mechs `[]`, hostile pawns `[]`.

### ✅ `jawa/fix_floating_roofs` — PASS, proven by a purpose-built floating roof
First attempt proved nothing: stripping a room with `clear_area` removes the roof
too (it strips roof over its rect), so there was nothing unsupported and
`cellsCleared: 0` was correct but uninformative. Rebuilt the test to leave a real
floating roof — a 9x9 room, then `clear_area` on **only the four perimeter
strips**:
```
walls remaining in room: 0
interior cell 184,184 -> roofDefName "RoofConstructed"   (roof still there)
fix_floating_roofs -> roofedCellsBefore 1598, roofedCellsAfter 1549, cellsCleared 49
interior cell 184,184 -> roofDefName None
```
49 = exactly the 7x7 unsupported interior. Whole-map scan, as documented.

### ✅ `jawa/set_thing_props` — PASS on quality/hitPoints/faction-on-buildings
`Gun_Revolver` (Normal, 100 HP) → `{quality: Legendary, hitPoints: 42}` →
`changed: [quality, hitPoints, faction]`, label became
*"Revolver (legendary 42%)"*; **independent** `jawa/list_things` read-back:
`quality Legendary, hitPoints 42`.
⚠️ **One honest defect found**: `faction` was listed in `changed[]` while
`factionAfter` was `null` — the revolver is an item the engine will not give a
faction. Cross-checked against a building: `GravEngine` → `factionAfter: "New
Arrivals"`, then cleared → `null`, both correct. ⇒ the faction path works where
the engine allows it, but the tool reports `changed` **without confirming the
write took**, which is the exact "report the write, not the effect" pattern this
project treats as a defect. Small fix: read `thing.Faction` back and only list it
in `changed[]` if it actually moved.

### ⚠️ `jawa/incident_queue_clear` — ran clean, destructive path UNMEASURED
`{}` → `success: true, clearedCount: 0, cleared: []`. The queue was genuinely
empty on a fresh quicktest map, and nothing on the bridge populates
`IncidentQueue` on demand (it fills from quests and delayed incidents). The tool
resolved the queue and returned an honest empty result; **that it actually clears
a populated queue is not proven** and is recorded as unmeasured rather than passed.

### ⚠️ `jawa/av_effect` — ran on all three modes; cosmetic, largely unverifiable
`shake` → `success`, but **`curShakeMagAfter: 0.0`** — the shaker does not
accumulate while the game is paused, so this neither confirms nor refutes.
`fleck` (Heart at 120,120) and `song` (EntrySong) both returned success with their
resolved defs echoed. All three are cosmetic with no game state to read back;
treated as **ran without error**, not as proven visible.

## Criteria
- [x] 11 tools written, every signature read from 1.6 source via rimsage — including the
      one wrong guess (`genStepClass`) the compiler itself caught and forced a correction on.
- [x] Builds clean (0 errors, 0 warnings), four passes (11, +1 `pawn_set_guest_status`,
      +2 `take_screenshot`/`rebuild_dirty_regions` from the owner-culled 185-row cross-check).
- [x] No name collision with the existing 263 (253 + the first 10) — 277 confirmed.
- [x] Deployed — all 11 registered on the live bridge (301 `jawa/` tools).
- [ ] Each proven live. **PASS (8):** `scatter_at`, `run_genstep`,
      `run_basegen_symbol`, `fix_floating_roofs`, `spawn_mech_cluster`,
      `set_game_speed`, `letter_send_delayed`, `set_thing_props`.
      **Also PASS, the three later additions:** `take_screenshot` (used throughout
      this pass), `pawn_set_guest_status` (Guest->Prisoner->Guest->Slave, each
      call's `Before` matching the previous `After`; Prisoner initialised
      `resistance 16.0`/`will 0.0`), `rebuild_dirty_regions` (ran clean; a cache
      rebuild with no external observable).
      🔴 **`letter_list` is BROKEN**: `l.lookTargets.IsValid` with no null guard,
      and `Verse.LookTargets` is a CLASS, so any letter without look targets NREs
      the whole call. One-line fix, needs a game-down rebuild.
      ⚠️ **UNMEASURED, not passed:** `incident_queue_clear` (queue genuinely empty;
      nothing populates it on demand) and `av_effect` (cosmetic; `shake` read back
      `curShakeMagAfter 0.0` because the shaker does not accumulate while paused).

--- history ---
