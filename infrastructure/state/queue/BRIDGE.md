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

### 🔴 OWED AT THE NEXT SHUTDOWN WINDOW — `jawa/get_defs` + `jawa/fire_quest`
**Two tools, one window.** `f4ecb68` and `jawa/fire_quest` (2026-08-14), both
compile 0/0. Deployed copy is 22; the artifact is **24**.

```bash
python.exe src/RimMandrake/bridgetools/build.py --gm --apply   # game CLOSED
```
Then bump to **24** in the same commit: `EXPECTED_TOOLS` (`load_session.py`),
`ALL_TOOLS` (`prove_new_tools.py`), `census(expect=)`, `skills/rimbridge/SKILL.md`.
Non-GM is 22. **Do not raise the gate early** — it fails a correct deploy.

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

### 🟡 BUILT AND DEPLOYED, NEVER RUN — five tools awaiting one live session
**Deployed copy measured 2026-08-14:** `…\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`,
md5 `45fe3874…`, **22 tools**. Compiles clean; **not one has been driven live** —
do not let another seat treat these as working tooling.

| tool | commit | what closes it |
|---|---|---|
| `jawa/set_pawn_rotation` | `7b8d5b7` | `prove_new_tools.py --pawns` |
| `jawa/set_pawn_style` | `7b8d5b7` | ″ |
| `jawa/set_pawn_xenotype` + `xenotype` on `spawn_pawn` | `e60197a` | ″ |
| `jawa/order_pawn` | `bee5da9` | `prove_new_tools.py --pawns --walk`, live paused map |

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
