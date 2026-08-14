# NEXT_RELOAD.md — the run sheet for the NEXT game load

_A cold load costs **~23–30 minutes**. It is the scarcest resource in this project.
This file exists so a load is never spent on one question._

**Read top to bottom. It is ordered.** Before-launch → call #1 → batches. **Every
item names the CALL that produces its evidence.** If a check has no call, it is in
§7 (cannot be collected) and you do not attempt it.

Assembled by PROJECT from `infrastructure/state/queue/<SEAT>.md`. Harvest and clear
afterwards — a closed item becomes ONE line in `CLOSED.md` (`DOC_BUDGET.md` §3).
How to spend a load: `skills/rimworld-load-round/SKILL.md`.

---

## 🔴 SCOPE OF THIS SESSION — WORLDGEN IS HELD

**The owner has HELD worldgen. v1 rows 2 and 7 do NOT happen this session.**

Reason: the owner's sea spec — a quarter ocean in three oddly-shaped bodies, a few
mountain-fed rivers, the rest badlands / desert / deep desert / alien — is
contradicted by the generator, which produces **43–55% scattered ocean**. Ocean is
an **elevation rule written at worldgen step 0**; no slider touches it. The owner
chose to solve the sea before spending the irreversible click.

> **The Configure Factions page is seen ONCE.** It is not on this session's path.
> `WORLDGEN_FACTION_CHECKLIST.md` stays ratified and waiting. **Do not open it.**

**So this session is: prove the tooling, then verify everything that does NOT need
a fresh campaign world.**

**v1 rows and where they stand — do not spend a call on a closed one:**

| row | state | this session |
|---|---|---|
| 1 Empire reskin | ✅ CLOSED | — |
| 2 Faction exclusion | 🔴 needs worldgen | **HELD** |
| 3 *The Claim* quest | built + deployed, never seen | §7 — the fire mechanism is uncollectable |
| 4 Three terrain overrides | 1 of 3 seen | ⭐ **§5, the session's real target** |
| 5 Jawa xenotype | ✅ CLOSED checked-and-fine (`V1_SCOPE.md:608-633`) | — |
| 6 Weapons / gear | ✅ CLOSED `ad3e9b0` | — |
| 7 Ordinary worldgen | 🔴 needs worldgen | **HELD** |
| 8 ⭐ Gravship | ✅ CLOSED — built + exported `6909ecb` | — |

⚠️ `V1_SCOPE.md`'s burn-down table still shows row 5 as 🟨 while its own §608-633
closes it. **The prose ruling is later and wins.** Row 5's only residual ask — see
it on a naturally-spawned campaign Jawa — needs the held worldgen anyway.

---

## 1. 🔻 BEFORE LAUNCH — the game is DOWN right now, so this window is LIVE

_(This section used to be headed "MOOT FOR THIS LOAD". That was inverted.)_

### 1a. Arm the def dump — OPTIONAL, gates nothing

```bash
echo all > "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/dump_request.txt"
```

**Read at STARTUP only**, so it is armed before launch or not at all. Worth doing
to clear the offline dump's staleness — **but it blocks nothing.** An older note
here made it row 4's sole route; that is dead, see §5c.

### 1b. Mod list — OPS's alone (rule 7)

**`ModsConfig.xml` is written only by us or by the owner in RimSort.** RimWorld
does not rewrite it on exit — measured twice (exit at 10:04:55, file mtime 10:01;
and a 16:41:39 write with no game alive). **So there is no window to miss.**

🔴 **The real hazard is a LIVE collision.** The file changed twice in twenty
minutes while the game was down (22,328 B @16:21 → 22,406 B @16:41). The owner
reorders in RimSort with the game down; a seat writing over that clobbers the
ordering and neither party is warned.

> **Do not write `ModsConfig.xml` unless you have just read its mtime.** Announce
> mod-list edits like the live bridge. If in doubt, ask the owner whether RimSort
> is open — they are the only reader who knows.

A mod-list change takes effect **only at startup**. Editing while the game runs is
inert, not destructive — reading the running game as evidence the edit "failed" is
the trap.

| # | change | why |
|---|---|---|
| 1 | **Turn mechanoids OFF** | owner's ruling |
| 2 | **Disable `com.yayo.yayoAni.continued`** `[v2]` | lightsaber flies up-and-behind on draft; Yayo's is the suspect. Everything it was held back for is closed |

Then `python.exe src/RimMandrake/Utils/refresh.py` — **Windows** interpreter; WSL's
`python3` fails on the Windows paths with a bare `cannot read ModsConfig`.

### 1c. Companion — nothing owed

**Deployed `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`
— 21 tools, 235,008 B, byte-verified by `strings` on the DEPLOYED copy, not
trusted from the build's own report.** Any earlier "20 tools" line here is dead.
This copy carries BRIDGE's `BiomeDef` branch (`9f58702`) — see §3b.

⚠️ **Three tools have never executed** — `jawa/set_pawn_rotation`,
`jawa/set_pawn_style`, `jawa/set_pawn_xenotype`. They compile and self-verify on
paper only; first execution is this load.
⚠️ **Any future companion deploy must pass `--gm`** or it strips
`jawa/fire_incident` and `jawa/send_letter` off the game copy. The build refusing
by default is the guard working.

### 1d. No deploy is owed

**Measured on the game copy: rows 3 and 4 are deployed and byte-identical**, and
the ground hulk was deployed tonight. `Mods/Jawa_Patches/Defs/` holds
`MapGeneration`, `PrefabDefs`, `QuestScriptDefs`, `TerrainDefs`, `ThingDefs_Items`;
`Patches/` holds `JawaGroundHulk_Register.xml`, `JawaResource_Scrapfields.xml`,
`JawaTerrain_DuneSeas.xml`, `JawaTerrain_SaltPans.xml`. **The old "A DEPLOY IS OWED
BEFORE ROW 3 OR ROW 4" block was false and is deleted.**

---

## 2. 🔴 THE MOMENT THE GAME IS UP — harvest the startup log FIRST

**Before any bridge call that mutates anything.**

```bash
python.exe src/RimMandrake/Utils/harvest_log.py
```

**Why the order matters:** OPS's O12 is a cluster of 9
`GeneratePawnRelations` NREs, 8 of which landed on a pawn OPS had **spawned
itself** in the ion test. The open question is whether they are an artefact of
debug spawning or a real defect in relation generation — which runs for faction
leaders and fails silently. **The moment anyone calls `jawa/spawn_pawn`, that
cluster becomes unattributable again and the question cannot be answered.**

Harvest first. Then spawn.

---

## 3. 🔴 CALL #1 — the tool-surface census. Nothing below is interpretable until it passes.

```
rimbridge/list_tools          -> expect 21 jawa/* names
```

**21.** 20 or fewer means the deployed companion is not the one we measured, and
every result below it is evidence of nothing. One call, costs nothing, gates
everything.

The 21: `damage`, `destroy_batch`, `drain_log`, `fire_incident`, `get_def`,
`get_roof_batch`, `get_terrain_batch`, `list_factions`, `list_pawns`,
`order_pawn`, `refresh_rect`, `send_letter`, `set_pawn_rotation`,
`set_pawn_style`, `set_pawn_xenotype`, `set_plants`, `set_roof_batch`,
`set_terrain`, `set_terrain_batch`, `spawn_batch`, `spawn_pawn`.

### 3b. ⭐ CALL #2 — v1 row 4's dune-seas gate. **No map needed. Do it here.**

**Defs load before any map exists, so this runs ahead of the quicktest** — it is
the cheapest v1 evidence in the file.

```
jawa/get_def   defName=Desert         defType=BiomeDef
jawa/get_def   defName=ExtremeDesert  defType=BiomeDef
```

BRIDGE added a `BiomeDef` branch to the companion (`9f58702`, deployed and
byte-verified). `get_def` now returns `terrainPatchMakers` — each with
`perlinFrequency`, fertility band, `minSize` and its ordered `thresholds`
(terrain, min, max) — plus `terrainsByFertility` and `patchMakerCount`.

| BiomeDef | SoftSand threshold `min` | vanilla | PASS |
|---|---|---|---|
| `Desert` | read it | 0.65 | **0.55** |
| `ExtremeDesert` | read it | 0.65 | **0.50** |
| `AridShrubland` | patch **adds** a whole `terrainPatchMakers` block | — | block present |

Already automated as item **A5** in
`src/RimMandrake/BridgeTools/load_session.py`. **It FAILs loudly if the companion
returns no `terrainPatchMakers`**, rather than reporting a silent pass — so an
empty reply is a result, not a shrug.

🔴 **Why live, and not the dump: a def dump is DISK, not RUNTIME.** A dump answers
*what the XML says after patching*; `get_def` answers *what the game resolved*.
**Where they disagree, the live read is the one that counts.** This is doctrine,
not convenience — it is what nearly cost row 5 its correct ruling.

---

## 4. 🌉 BATCH A — the three never-run tools, ~2 minutes, no per-item gate

Order is free after call #1. **Assert on read-back fields, never on `success`.**

```
1. jawa/list_pawns                                   -> ids for everything below
2. jawa/spawn_pawn        kindDef=<jawa kind>  faction=player  xenotype=BTD_Jawa
3. jawa/set_pawn_xenotype pawnId=<id from 2>   xenotype=BTD_Jawa
4. jawa/set_pawn_rotation pawnId=<id>          dir=east      then dir=unlock
5. jawa/set_pawn_style    pawnId=<id>          hair=…  beard=…
```

- **`set_pawn_rotation`** returns `applied`, `posture`, `visible`. 🔴 **`visible:
  false` means the pawn is laying or downed and the renderer ignores the turn** —
  a real no-op wearing a success. Stand it up and repeat.
- **`set_pawn_style`** returns per-field `was`/`now`/`ok`. Tattoos silently no-op
  without Ideology; the tool **refuses** rather than lying, so a refusal there is
  correct behaviour.
- **`set_pawn_xenotype`** clears xenogenes but **not** endogenes. `BTD_Jawa` is
  inheritable, so its 24 genes land as endogenes and survive a later conversion —
  pass `clearEndogenes` deliberately or expect residue.

---

## 5. ⭐ BATCH B — v1 ROW 4, on a ~30-second quicktest map

```
rimworld/start_debug_game_ready       -> a fresh map in ~30 s
```

🔴 **Row 4's on-map items are map-generation-time.** A `terrainPatchMaker` and a
`GenStepDef` both run during map gen; **nothing appears on an existing map,
however long you look.** Checking them on a standing map is a guaranteed false
negative. *(Dune seas is the exception — it closed on a def read in §3b.)*

### 5a. Ground hulk + scrapfields — **NOT biome-gated, any fresh map shows them**

Both patch `Base_Player`'s `genSteps` with **no biome filter**:

| item | GenStep order | file |
|---|---|---|
| scrapfields (`ChunkSlagSteel` scatter) | **960** | `src/Jawa/Jawa_Patches/Defs/MapGeneration/JawaScrapfields.xml` |
| ground hulk (the rider on row 4) | **940** | `src/Jawa/Jawa_Patches/Defs/MapGeneration/JawaGroundHulk.xml` |

**Evidence to collect — screenshots, two of them:**
- **the hulk, wide shot** — the wreck reads as a downed ship, not as rubble
- **one casket bank, close** — the ancient cryptosleep caskets standing in rows.
  *(The starboard bank is deliberately short; that is design, not a defect.)*
- **scrapfields** — steel slag strewn in the open with machine-bit filth around it

### 5b. Salt pans — ✅ **ALREADY PASSED LIVE, 144 cells. Do not re-spend.**

⚠️ If you do repaint for any reason, the parameter is **`terrainDef`**, NOT `def`:

```
jawa/set_terrain   terrainDef=Jawa_SaltCrust   x=… z=… width=… height=…   layer=top
```

🔴 **The bridge silently drops unknown parameter names before the tool runs.**
Written as `def=`, it paints nothing and reports no error. Read the cell back with
`rimworld/get_cell_info` → `terrainDefName`.

### 5c. Dune seas — ✅ **already collected in §3b. Do not look at sand.**

🔴 **It is a DENSITY change, 0.65 → 0.55. Nobody can eyeball a 15% difference
without a control map** — a seat could stare at a correct result and call it
failed. `V1_SCOPE.md:484-498` corrected this gate; do not revert it to a look.
The evidence is the §3b `get_def` read, and it needs no map.

### 5d. The biome constraint applies to §5b only

A Desert / ExtremeDesert / AridShrubland quicktest tile is needed for **salt pans**
alone — dune seas moved to a live def read, and **the hulk and scrapfields are not
biome-gated at all.** Any fresh map shows those two.

---

## 6. BATCH C — the cheapest launch gate we own

### `NoPathToPilotConsole` — one call, no walk, game stays PAUSED

```
jawa/order_pawn   pawnId=<colonist>   targetId=<consoleThingId>   waitTicks=0   unpause=false
```

Returns `canReach` on a paused game (BRIDGE, `bee5da9`). **No movement, no time
passes, nothing on the map changes.**

🔴 **`pathEndMode` must be `interactioncell`** — it is the default when `targetId`
is set, so do not override it. The vanilla gate is `PawnCanFillRole` →
`CanReach(…, InteractionCell, …)`, and the cell *beside* a console is a
**different verdict**. **A door is not a path**: doors are in the export, and that
is exactly what this call tests. Reference:
`design/Jawa/worldbuilding/gravship_flight_invariants.md`.

⚠️ Row 8 is closed and this does not reopen it — flight was ruled out of row 8's
bar. This is a **launch-gate fact**, collected because it costs one paused call.

---

## 7. 🚫 GATES THAT CANNOT BE COLLECTED — do not attempt these

Filed so nobody spends a load discovering it. Each is here because **the call that
would produce the evidence does not exist or is measured broken.**

| item | why it cannot be collected |
|---|---|
| **v1 row 3 — fire *The Claim*** | The rumour item needs a **right-click float menu** ("Read the rumour") on a colonist. `rimworld/right_click_cell` is **measured broken** — it reports *"Dispatched a live right-click…"* and nothing happens (`skills/rimbridge/references/traps.md:294`; `queue/BRIDGE.md:535`). No bridge route to a float menu exists. **Row 3 waits for the owner at the keyboard.** ⚠️ Do NOT wait for the storyteller either — the quest is root-selected |
| **ToolBeltFix** | Needs the apparel **WORN**. There is no equip tool in the 21 |
| **CereanManeFix / SauridFrillFix** | Neither names a pawnkind defName, so there is no `spawn_pawn` that reliably produces the pawn to look at |
| **The seven fix mods generally** | ⚠️ **None can ever produce a log line.** `Failed to find any textures at` fires only when **every** direction of a `Graphic_Multi` is missing, so a single absent or zero-alpha facing is a silent south-fallback. They settle by eyeballing a pawn, never by `harvest_log.py` |

🔴 **DO NOT ADD ART-FIX WORK.** Standing directive from the owner: **CREATE stops
fixing art until the owner personally verifies art is broken.** Art *observation*
is fine and welcome; art *fixing* is stopped. Nothing in this file schedules an
art fix, and nothing should be added that does.

---

## 8. 🔓 BEFORE RELEASING THE BRIDGE — unlock every pawn you touched

```
jawa/set_pawn_rotation   pawnId=<each pawn from §4>   dir=unlock
```

🔴 **`debugRotLocked` is serialised by `Thing.ExposeData`.** A pawn left locked
stays locked across **every future load**. This is litter that outlives the
session, and it is invisible until someone wonders why a pawn will not turn.

Then the release announcement, naming **what you left on the map** — spawned pawns,
painted terrain, the quicktest map itself:

```
LIVE BRIDGE RELEASED — <seat>, <what changed, and anything left on the map>
```

---

## 9. 📋 AFTER THE LOAD — harvest, then refresh

```bash
python.exe src/RimMandrake/Utils/harvest_log.py                  # every standing check, with baselines
python.exe src/RimMandrake/Utils/harvest_log.py --show crossref  # read the actual lines
python.exe src/RimMandrake/Utils/refresh.py                      # rebuild the offline dump
```

Exit code 1 means something is above baseline. Procedure:
`skills/rimworld-load-round/SKILL.md` §8.

⚠️ **Exit 0 means the LOG is clean. It does not mean the load passed.** Every item
above that says *look* or *screenshot* is settled on screen only.
- **A patch that silently no-ops logs NOTHING.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return `true` when they match nothing.
- **Art items have no log strings at all.** A present-but-empty PNG is a
  successful load by every measure the engine has.

**The offline dump describes 580 mods** — `observed/2026-08-13/dumps/defnames.580.2026-08-13.json`.
Re-run `refresh.py` after the load before trusting any offline def lookup, and
remember: **a def dump is DISK, not RUNTIME.** Any mod that mutates defs at load —
dedup, remap, implied-def generation — makes a disk-derived conclusion unsafe.
That is what nearly cost row 5 its correct ruling.

### Two carry-ins, neither blocking

**1. Pin the six User Rules — durability, not correctness.** `loadBottom` and
`loadAfter` in the same rule means `loadBottom` wins and `loadAfter` is ignored.
Six of thirteen carry both: `jawa.patches`, `jawa.armoury`, `jawa.doctrine`,
`jawavoice`, `jawaionweapons`, `rimdefdump`. ✅ **Today's order is CORRECT anyway**
— 0 violations across all 13, tested rather than reasoned. ⚠️ **But it is riding
the topological tie-break, not being pinned**, so it is right by luck. OPS's,
post-load.

**2. Retiring `mandrake.missingartfixes`** has an order and one dependency — the
blast-door brief still lives inside its `Source/`. **Do not re-derive the sequence;
it is written up in `infrastructure/state/queue/CREATE.md` under C11.**

Afterwards: triage anything new into `vendor/wisdom/benign_log_errors.md`, append
anything that surprised you to the matching
`skills/rimworld-modding/references/traps-*.md`, and file the rest into the
per-seat queues.
