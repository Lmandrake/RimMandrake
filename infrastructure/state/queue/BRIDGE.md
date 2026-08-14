# infrastructure/state/queue/BRIDGE.md

_BRIDGE's queue. **You own it — write freely, nobody blocks on it.** Others file at
you by appending. Doctrine in `agents_def.md`; the v1/v2 line in `V1_SCOPE.md`;
finished items in `infrastructure/state/CLOSED.md`._
🔴 **Newest at the TOP — read the head, never `tail` this file.** On 2026-08-14 a
fresh seat tailed it and carried three closed items into a report as open.

## ⭐ v1 — YOUR ROWS

**`V1_SCOPE.md` rows 5 (Jawa xenotype on the map), 6 (gear from the 6 live mods seen
in use — partly done) and 7 (ordinary desert worldgen) are yours, all *verify only***
— the live observation IS the task. ⛔ **Do not book a load for these**: rows 2–4 are
authored offline by OPS/CREATE and all of it verifies in ONE session.

## Open

### 🔴 PRE-LAUNCH 2026-08-14 — CENSUS EXPECTS **26**, and the documented derivation says 27
Measured on the game copy at the open window: md5 `55b2362985bcf5a2dc4a1140ef39eb7a`,
292,864 B @ 12:25, **26/26 `jawa/` names**, md5-identical to the repo build
`src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`,
no `.cs` newer than it. **No companion deploy is owed** — `NEXT_RELOAD.md` §1c/§1d
row 1 were stale and PROJECT has been corrected.

🔴 **`NEXT_RELOAD.md` §3's derivation command over-counts by one and would FAIL a
correct build.** `grep -rhoE '"jawa/[a-z_]+"' src/RimMandrake/bridgetools/` → **27**;
it matches `[Tool("jawa/x")]` inside a *comment* in `prove_new_tools.py:112`. Add
`--include='*.cs'` → 26. **Generalises: a derivation is only as good as its corpus —
scoping a gate's grep to "the source tree" swept in prose about the source tree.**

✅ **VISION's sea-gate ask is ALREADY SHIPPED, not owed.** `perimeter`,
`centroidLat` and `raggedness` (perimeter²/tiles) are in the DEPLOYED binary —
`strings -a -el` returns the anonymous-type template
`{ tiles = {0}, pct = {1}, perimeter = {2}, raggedness = {3}, centroidLat = {4} }`.
Sea gate is **5-of-5** collectable. (`JawaBenchTerrainTools.cs:3164-3178`.)

⏳ **Deferred to the NEXT shutdown window, deliberately: `jawa/ideo_of`,
`jawa/biome_probe`** (VISION.md:508, 515). Both are new tools needing IL-verified
engine routes; rushing them into the one artifact that is currently proven-good,
minutes before launch, risks 26 working tools to add 2. **Build them offline during
the load** — that is dead time already.

### 🔴 THE 12 ART SCREENSHOTS ARE NON-EVIDENCE — re-shoot them, do not judge them
Found by opening the pictures. The Debug log window covers the CENTRE of the
screen, which is exactly where `look()` puts the subject; in `p5_004.png` and
`p13_012.png` the subject is not in frame at all. Twelve rows filed `NEEDS EYES`
— collected, and empty. `jawa/clear_ui` fixes it forward (closes every
`Window_Dev`, drops the selection) and `rimbench.core.look()`/`.frame()` call it
automatically. ⚠️ Closing the log by hand does not hold — auto-open-on-error.
Banner is at the top of `observed/2026-08-14_load_session.md`; trap filed.

### ✅ AV_DogSled's NullReference was MINE, not the art's
`Vehicles.VehicleDef` cannot go through `ThingMaker` — `VehiclePawn::.ctor` leaves
`vehiclePather`/`ignition`/`drawTracker`/`kindDef` null and `SpawnSetup` callvirts
all three. `spawn_batch` now routes vehicles through
`Vehicles.VehicleSpawner.SpawnVehicleRandomized` **by reflection**, so the
companion still loads without Vehicle Framework. P1 is re-runnable.

### ✅ DONE 2026-08-14 — the window was spent: 22 → **26 tools deployed**
Game copy md5 **`55b2362`**, 26 `jawa/` names, GM pair present. Third tool is
`jawa/list_things` (`3adedbc`) — a ThingID for a NON-PAWN, which nothing on the
bridge could produce; the only source was a human clicking the object, and that
is precisely why A2 `NoPathToPilotConsole` was SKIPPED in the live session.
`load_session.py` now looks the console up itself (defName `PilotConsole`, read
from `Odyssey/Defs/ThingDefs_Buildings/Buildings_Gravship.xml`).
⛔ **No bulletin to peers yet — none of the three has been CALLED.** A capability
is announced when it has run, not when it has compiled.

### ✅ DONE 2026-08-14 — `jawa/get_defs` + `jawa/fire_quest` are DEPLOYED
Window taken with the game confirmed down. Game copy
`…\BridgeTools\JawaBench\JawaBench.BridgeTools.dll` md5 **`ea5952e2`**, **24**
`jawa/` names, both new ones in it, GM pair present. Gate raised in the same
commit — and it is no longer a literal: `census()` derives from `EXPECTED_TOOLS`
and `prove_new_tools.ALL_TOOLS` reads the deployed DLL, so the number cannot go
stale in two files again.
⛔ **This is a DEPLOY, not a proof.** Neither tool has been called. RimBridgeServer
registers companions only at startup, so nothing changes until the next launch.

**`jawa/fire_quest` closes v1 row 3**, which was filed UNCOLLECTABLE only because
its route (read an in-world item → float menu) needs `rimworld/right_click_cell`,
measured broken. `jawa/fire_quest questDef=Jawa_TheClaim points=<n> [accept]
[dryRun]` bypasses it. Engine route read with ilprobe, not recalled: `QuestUtility
.GenerateQuestAndMakeAvailable(QuestScriptDef, float)` is public static and its IL
is `QuestGen::Generate` → `Find::get_QuestManager` → `QuestManager::Add` ⇒ it
**registers**, not merely generates. 🔴 **The returned Quest is not the evidence** —
every field is read back off `QuestManager` after the call and `success` means
*found in the manager*. The rumour hands out `Jawa_TheClaim`
(`Jawa_ClaimRumour.xml:89-91`), `rootMinPoints 0`.

**Why `get_defs` outranks one tool.** Five v1 gates had no collectable evidence
because `get_def`'s rich block was **ThingDef-only**, each fix adding another
hardcoded branch. `get_defs` reads a `fields` list reflectively off **any** def type
⇒ a new question needs **no new build**, and a build needs the game closed.

### 🟡 BUILT AND DEPLOYED, NEVER RUN — awaiting one live session
**Deployed copy measured 2026-08-14 after the window:** md5 `55b2362`, **26 tools**.
Compiles clean; the rows below have **never been driven live** — do not let another
seat treat them as working tooling.

| tool | commit | what closes it |
|---|---|---|
| `jawa/set_pawn_rotation` | `7b8d5b7` | `prove_new_tools.py --pawns` |
| `jawa/set_pawn_style` | `7b8d5b7` | ″ |
| `jawa/set_pawn_xenotype` + `xenotype` on `spawn_pawn` | `e60197a` | ″ |
| `jawa/get_defs` | 2026-08-14 | any def-type question that is not a ThingDef |
| `jawa/fire_quest` | 2026-08-14 | v1 row 3 — `questDef=Jawa_TheClaim` |
| `jawa/list_things` | `3adedbc` | A2 now finds its own console; the item IS the proof |
| `jawa/clear_ui` | `9a5b6fe` | any screenshot whose subject is actually visible |
| vehicle route in `spawn_batch` | `9a5b6fe` | P1 `AV_DogSled` spawning at all |
| roof pair | — | `set_roof_batch` / `get_roof_batch` |

✅ **Off this list, live-proven 2026-08-14:** `jawa/order_pawn` (Paige walked
111→117 and back, `ticksElapsed=240`, left undrafted) and `jawa/list_factions`
(54 factions, A1/A1b both PASS). ⚠️ `jawa/world_stats` was CALLED and its answer
was **discarded by a harness NameError** — unproven for a different reason, and
the harness bug is fixed (`3e17731`).

🔴 **The finding that shaped `order_pawn`: `TryTakeOrderedJob` returns TRUE for a
job it merely ENQUEUED** (IL_013f/01ac/01fa each `ldc.i4.1; ret` after
`EnqueueFirst`/`EnqueueLast`) **and never consults reachability** — textbook silent
success. So the tool polls real ticks and returns the position read back off the
map; `success` is *arrival*, false whenever `ticksElapsed` is 0. ⚠️ **It can
unpause** (default) — hence the real walk sits behind `--walk`. ⚠️ **The walk proof
drives a COLONIST**: a hostile has no drafter, its Lord duty overrides the Goto, and
a working tool reads as FAIL.

**`NoPathToPilotConsole` needs no movement** — the gate is `ReachabilityUtility
.CanReach(pawn, console, PathEndMode.InteractionCell, …)`, and a pawn can reach the
cell *beside* a console and still fail `InteractionCell` ⇒ target the THING.
Nothing left on the map; CREATE's item 6.
`jawa/order_pawn pawnId=colonists targetId=<consoleThingId> waitTicks=0 unpause=false`

### 🟢 RUN THIS, DO NOT COMPOSE CALLS — `src/RimMandrake/bridgetools/load_session.py`
```bash
python.exe src/RimMandrake/bridgetools/load_session.py --phase any     # BEFORE worldgen
python.exe src/RimMandrake/bridgetools/load_session.py --phase fresh   # after it
python3     src/RimMandrake/bridgetools/load_session.py --selftest     # no game
```

**A load is wasted by COMPOSING calls while the game is up** — looking up a defName,
guessing a parameter, discovering something was never deployed: offline work bought
at live prices. Writes one ledger to `observed\<date>_load_session.md`, one line per
item, and tracks **LITTER** — the release message is written from that list, not
from memory. 🔴 **It does not adjudicate art**: visual items end in `NEEDS EYES`
plus a screenshot path.

### ⭐ THE NEXT LOAD'S SCRIPT IS ALREADY WRITTEN
`D:\Luke\dev\Rimworld\infrastructure\state\CREATE_TEST_PLAN.md` — CREATE wrote it, I
execute it. Eight art-fix mods, v1 row 3's `Jawa_ClaimRumour`, row 4's terrain plus the
619-cell ground hulk. Part 3 needs a **freshly generated** Desert/ExtremeDesert/
AridShrubland map; a quicktest counts. **A screenshot is the evidence, a def query is
not** — every failure mode in it is silent.

🔴 **Nine pre-flight corrections to that plan live in
`infrastructure/state/AGENT_BRIDGE_state.md` — read them before you type at a live
console.** Two are wrong parameters, one is a diagnostic string with no basis, and
`ToolBelt` does not exist under that name.

### 🟡 Confirmatory, not load-bearing — `get_def GravFieldExtender`
CREATE settled offline that the Bigger Gravships settings reach the live defs
(`GravshipSize.dll` stamps radii during implied-def generation, after all XML patching)
⇒ **do not spend a live session's first call on this**; worth one when convenient.
⚠️ On disk the def is 16.9/12.9 and is *meant* to disagree.

### 🟡 B-v1 — live terrain edit: put the salt back in the dry lake bed
**Owner's ruling, overriding both me and VISION.** Geological Landforms hard-codes
`SoftSand` on its dry-lake landform and the mod-side fix means editing a serialised
NodeCanvas ⇒ fix it **live, on arrival**. Target defName, verified: `Jawa_SaltCrust`,
`src/Jawa/Jawa_Patches/Defs/TerrainDefs/JawaSaltCrust.xml:100`.
⚠️ **Bound by BOTH a rect and a source-terrain match, never terrain alone** — a
map-wide SoftSand→salt repaint erases the desert.
**The deliverable is the CAPABILITY, not the pan:** (a) can the bridge detect or be told
a landform footprint, (b) set terrain over that region, (c) does it survive save/reload.
First live evidence for tile-augmentation-on-approach, which has none
(`design/Jawa/worldbuilding/tile_augmentation_catalogue.md`). Same session as worldgen,
after rows 2 and 7. Not a blocker.

### 🟢 Observe at the next worldgen — `OuterRim_RebelAlliance`
🔴 **ABSENT is the DESIRED outcome** (VISION R2; `RebelAlliance_Suppress.xml` does it
deliberately) ⇒ **PRESENT is the failure.** Control is `OuterRim_GalacticEmpire`, which
must be present; one `jawa/list_factions` answers both and closes EXPECTED_FAILURES A3.
⚠️ **Nothing in `Player.log` reports a faction that never generates** — the only
detection is looking on purpose. Observe, do not fix.

### `[v2]` backlog
- **`jawa/import_gravship`** — mid-game layout import. `ShipSketchBuilder.BuildFromLayout`
  is `public static` and pure (no `Find.`/`Current.`/`Map`) and a `Sketch` spawns onto a
  live map ⇒ one method call, not a mod fork; licence permits it. Closes the design loop:
  author XML → import → look → iterate, no worldgen, no 25-min load per turn.
  ⚠️ **Floors will NOT come with it** — terrain is re-applied by a Harmony patch that does
  not run for a mid-game Sketch spawn; replay the cells through `jawa/set_terrain_batch`
  (`src/RimMandrake/Utils/gravship_layout.py` emits them). Needs game DOWN.
- **Biome-aware terrain palettes, and a `destroy_at` verb** — idea only.

## 🔴 Live state you must not rediscover

- **`BG_gravEngineSupport` is 4500** (was 632.79541) in
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3522759531_GravshipSizeSettings.xml`.
  Set live via `rimworld/update_mod_settings` **plus the mod's own "Apply Settings
  Now!" button** — the write alone does not reach the defs, the button does, no
  restart needed. The 4,057-cell hull went `4057/633` → `4057/4500`.
  ⚠️ **Any capacity reading starts from 4500.** (Compiled default is 500.0, so
  632.79541 was neither vanilla nor a mod default.)
- **A def deployed AFTER the game launched is invisible to the running process** and
  looks perfectly deployed on disk. `find "<Steam>/Mods" -newermt "<PID StartTime>"`.
  (`traps-mods-and-managers.md`, `7d8a4a6`.)
- **`strings -a` only proves a tool NAME.** Method-body literals are UTF-16LE in the
  #US heap ⇒ `strings -a -el` to prove a *message* shipped. Plain `strings` reported
  a present fix as ABSENT and it was carried as fact for a day.
