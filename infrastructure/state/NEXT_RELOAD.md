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
| 3 *The Claim* quest | built + deployed, never seen | 🔓 **UNBLOCKED 2026-08-14** — `jawa/fire_quest`, §1c. No longer in §7 |
| 4 Three terrain overrides | **2 of 3 seen** — dune seas closed live | ⭐ **§5.** Scrapfields is an OPEN defect (11 vs ≥75), not a blank |
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

### 1c. Companion — ✅ **NOTHING OWED. The build landed 2026-08-14 12:25.**

🔴 **Re-measured by PROJECT 2026-08-14 against the game copy, not relayed:**
`md5 55b2362985bcf5a2dc4a1140ef39eb7a`, **292,864 B @ 12:25**, **26 `jawa/` names**,
`get_defs` and `fire_quest` both PRESENT. **The "UNDEPLOYED" table below was true
when written and is now false** — everything it lists is on the game copy. Do not
rebuild, do not redeploy, and do not spend the shutdown window on the companion.

🔴 **Corrected 2026-08-14 by BRIDGE, byte-measured against the game copy.** The old
NEED-DOWN batch listed three items and **two of them were already deployed**:
`jawa/order_pawn` and the `jawa/damage` refusal fix are both on the game copy.

| tool | state |
|---|---|
| `jawa/order_pawn` | ✅ deployed — do not re-deploy |
| `jawa/damage` refusal fix | ✅ deployed — do not re-deploy |
| **`jawa/get_defs` (`f4ecb68`)** | ✅ **DEPLOYED 12:25** — measured, see above |
| **`jawa/fire_quest`** | ✅ **DEPLOYED 12:25** — measured. Unblocks v1 row 3, which §7 had filed as uncollectable. `QuestUtility::GenerateQuestAndMakeAvailable(QuestScriptDef, float)`, IL-confirmed to reach `QuestManager::Add` — it registers, it does not merely generate. The tool reads the quest back out of `QuestManager` and reports its id/name/State, because a method returning is not evidence |

⚠️ **The method that made the stale entry look verified:** `strings -a` scans
7-bit ASCII, so a method-body literal (UTF-16LE, in the `#US` heap) reads as
**ABSENT**. Plain `strings` proves a tool **name** and nothing about its body.
**Use `strings -a -el`.** This retroactively weakens the "byte-verified by
`strings`" claim immediately below — that check still proves the 22 names are
present; it never proved any behaviour inside them.



**Deployed `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`
— 26 tools, 292,864 B @ 12:25, md5 `55b2362`, verified on the DEPLOYED copy, not
trusted from the build's own report.** Any earlier "20", "21", "22" or "24 tools"
line is dead. This copy carries BRIDGE's `BiomeDef` branch (`9f58702`, §3b) and
`jawa/world_stats` (`5768a10`).

⚠️ **Three tools have never executed** — `jawa/set_pawn_rotation`,
`jawa/set_pawn_style`, `jawa/set_pawn_xenotype`. They compile and self-verify on
paper only; first execution is this load.
⚠️ **Any future companion deploy must pass `--gm`** or it strips
`jawa/fire_incident` and `jawa/send_letter` off the game copy. The build refusing
by default is the guard working.

### 1d. ✅ **THE DEPLOY LANDED — `da7118e`. NOTHING IS OWED. Do not spend the window here.**

**OPS ran `--mod Jawa_Patches --apply` → `VERIFIED in sync`, 4 files.** Rows 2, 3,
4 and 5 below are **SHIPPED** — including 🔴 **`BuzzerApostrophe_Fix.xml`, the one
with the deadline. It made the window.** Row 1 was already deployed (§1c) and is
dropped. **Row 6 shipped on 08-13 and re-measured identical (md5 `d68bea3f`).**

⭐ **Why row 6 looked owed and was not:** a `--mod`-scoped `--apply` that ends
`VERIFIED in sync` is a positive statement about **every file in that mod**, not
only the ones it rewrote. Read the verdict, not the write count.

⚠️ **`--plan` lists one mod this table does not: `StrandedQuest`** — 3 files, not
deployed, **not enabled in `ModsConfig.xml`**. OPS left it inert, correctly. It is
an enable + deploy and it must land **pre-worldgen** — but **worldgen is HELD this
session**, so it has **no deadline tonight**. Owner ruling wanted before the
worldgen load, not before this one. Filed, not blocking.

_Table below is the pre-deploy state, kept because it records what was ranked and why._

**This section read "No deploy is owed" until 2026-08-14. That is now FALSE.**
⚠️ **The count and the table must agree. They did not, for one revision** — the
header said four and the table listed three, omitting two genuinely drifted files.
**Read the row count, not the adjective.** OPS's `--plan` run is the authority;
if it lists a file this table does not, this table is the stale one.

| # | item | ship? | why |
|---|---|---|---|
| ~~1~~ | ~~companion DLL~~ | ⛔ **DROPPED — ALREADY DEPLOYED** | Game copy md5 `55b2362`, 26 tools @ 12:25, `--gm` pair present. Measured independently by BRIDGE and by PROJECT 2026-08-14, and identical to the repo build. **Do not rebuild minutes before launch.** §1c |
| 6 | `BTDGravshipQuest_GrammarFix.xml` (`57b6f69`) | ✅ **ALREADY DEPLOYED — nothing owed** | Repo and game copy both md5 `d68bea3f`, verified by OPS and re-measured by PROJECT. It shipped with the 08-13 deploy. ⭐ **Generalises:** a `--mod`-scoped `--apply` ending `VERIFIED in sync` is a positive statement about **every** file in that mod, not only the ones it wrote — so no second `Jawa_Patches` deploy can be owed tonight. OPS O13, `queue/OPS.md:127`. Authored, validated, committed, **never deployed**; xpath confirmed against the installed defs, exactly 1 match. Success is a POSITIVE observation — the Downed Gravship quest showing description text — **not** the disappearance of `Grammar unresolvable`, which proves nothing if the quest never fired |
| 2 | `JawaScrapfields.xml` — `isJunk` off (`de1018b`) | ✅ | repo-only; game copy still 2026-08-13 16:42 **with `isJunk` present** |
| 3 | `JawaGroundHulk.xml` — `isJunk` off (`de1018b`) | ✅ | same defect class, same commit |
| 4 | ⏳ **`BuzzerApostrophe_Fix.xml`** (`3822ef9`) | ✅ **AND IT EXPIRES** | 🔴 **The ONLY item here with a deadline. Buzzer names bake into the save as STRINGS**, so it is worth shipping **only while worldgen is still ahead of us.** Ship it now and it works forever; miss this window and it is worth nothing the moment the world is made. Validator clean, both namer sites |
| 5 | `AnimalBiomeDuplicates_Fix.xml` (`9acddd3`) | ✅ **vouched by OPS — and this is the row to DROP if the window gets tight** | `validate_patch.py` OK, 0/0. ⭐ **Already deployed** (game copy 08-10 15:46) — what drifted is the *content*, not its presence, and the live log carries **0** hits for `same key has already been added`, so the deployed version is doing its job right now. The drift is a refinement from a closed investigation, not a fix for anything currently broken |
| — | **`JawaSeaShaper.dll` — SOLO, its own load** | ⚠️ **not in the batch** | repo md5 `b7730027`, deployed `82b48e53` @ 08-13 23:57, **older than the launch.** A new assembly poisons attribution for everything beside it. ⚠️ **The write FAILS `OSError 22` while the game runs** — loaded and locked. The refusal is safe; it cannot truncate |
| — | Armoury × 2 | ⛔ **HELD on scope** | v1 row 6 is closed; weapon balance is not v1 and ships in any later window |

🔴 **`--apply` overwrites the game copy with whatever is in the repo at that
moment, including a peer's half-finished work. Scope it with `--mod`; never run it
bare.** Deploy list and drift plan: OPS's queue.

### 📐 How to rank this list if the window gets tight

**Not by severity. By what the window does to the item's value.**

| | |
|---|---|
| 🔴 **ships first** | **value is DESTROYED by the event this window precedes** — deferring is not deferring, it is discarding. *Buzzer: names bake into the save as strings the moment the world is made* |
| ⬇️ **drops first** | **value is already being collected and would merely improve** — *AnimalBiomeDuplicates: deployed since 08-10, zero live errors, the drift is a refinement* |

⚠️ **Severity ranks these two the wrong way round.** The duplicate-key bug is by far
the nastier failure — an uncontained `ArgumentException` in
`BiomeDef.CommonalityOfAnimal()` killing every consumer of `AllWildAnimals` at
startup — and it is still the correct thing to drop, **because it is already fixed
in the running game.** *A severe bug you have already shipped the fix for is not a
claim on a scarce window; a trivial one whose window closes tonight is.*

⛔ **Do not let this list grow.** The Armoury patches are HELD on scope — v1 row 6
is closed, weapon balance is not v1, and it ships in any later window.

**Still true from before:** rows 3 and 4's defs are deployed and byte-identical,
and the ground hulk was deployed tonight. `Mods/Jawa_Patches/Defs/` holds
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
rimbridge/list_tools          -> count the jawa/* names
```

🔴 **DO NOT COMPARE AGAINST A NUMBER WRITTEN IN A DOC. DERIVE IT.** Three files
carried three different expected counts on 2026-08-14 — **21** in
`EXPECTED_FAILURES_next_load.md`, **22** here, **24** in `queue/BRIDGE.md` — while
the source artifact defined **24**. ⇒ **a CORRECT deploy would have FAILED the
gate on the irreversible worldgen run.**

**Derive the expectation at census time, from the artifact you just deployed:**

```bash
grep -rhoE --include='*.cs' '"jawa/[a-z_]+"' src/RimMandrake/bridgetools/ | sort -u | wc -l   # = 26 on 2026-08-14
```

🔴 **`--include='*.cs'` IS LOAD-BEARING. Without it this command returns 27** and
fails a correct build — it picks up a `[Tool("jawa/...")]` string inside a comment
in `prove_new_tools.py`. Found by BRIDGE, re-measured by PROJECT 2026-08-14
(27 bare / 26 scoped). **Fourth instance of the exact failure this section exists
to prevent — and this time it was in the fix itself.**

| you deployed | expect |
|---|---|
| the current artifact **with `--gm`** | that count — **26** today, `get_defs` + `fire_quest` included |
| the current artifact **without `--gm`** | that count **minus 2** — `fire_incident` and `send_letter` are stripped |
| anything else | **STOP.** The deployed companion is not the one you measured, and every result below is evidence of nothing |

⚠️ **A low read does not by itself mean a stale build** — the `--gm` strip looks
identical to one. Check which you passed before concluding anything.

📌 **Why this keeps happening: a hardcoded count in a gate document goes stale on
every single deploy, silently, and the gate then fails the correct build.** Third
instance in one night of *a number in a document that nobody re-derives*. **Gates
compare measurements to measurements — never to prose.**

**Measured on the DEPLOYED copy 2026-08-14 12:25: 26 names, `--gm` pair present.**
That is a measurement of the artifact the game will load, not a doc number — but
**it goes stale the instant anyone redeploys.** Re-derive with the `grep` above and
compare measurement to measurement. The four names added since the "22" list:
`get_defs`, `fire_quest`, `list_things`, `clear_ui`.

🔴 **THE GAME IS NOT REACTIVE FOR ~40 s AFTER THE BRIDGE FIRST ANSWERS**, whatever
`currentMapReady` and `longEventPending` report. Owner-observed; baked into
`load_session.py` as a settle before any mutation.
**Read-only calls are fine inside that window** — this census, the §3b dune-seas
`get_def`, and the `LIVE BRIDGE TAKEN` announcement all land immediately. **Only
mutation waits.** ⚠️ This is a signal saying the TOOL is ready being read as the
GAME being ready, which is the shape of half of `traps.md`.

⭐ **`jawa/world_stats` is read-only and needs a WORLD, not a map** — `waterPct`,
the **connected-water-body list**, `seedString` and `planetCoverage`. The body list
is the half that matters: a percentage alone cannot tell *three oddly-shaped bodies*
from *the same water smeared into forty blobs*, and those two worlds report an
identical `waterPct`. **It turns the owner's sea spec into a number.**

### 3b. ⭐ CALL #2 — v1 row 4's dune-seas gate. **No MAP needed — but a GAME is.**

🔴 **Measured 2026-08-14: this does NOT run at the main menu.** Every `jawa/*` tool
ends `Find.TickManager?.TicksGame ?? -1`, and `Find.TickManager` compiles to a
getter that dereferences `Current.Game` — **`?.` guards the RESULT, not the CALL.**
With no game the getter throws and *every* tool returns a bare
`Object reference not set to an instance of an object`, naming nothing.
⇒ **Run it once a game exists (a quicktest is enough); do not run it at the menu and
conclude the branch is broken.**

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

✅ **THE HULK LOAD IS WORTH SPENDING — a hold was raised and then cleared, both on
2026-08-14, and the clearing is recorded so nobody re-raises it.**

I held this check on the theory that `isJunk` × `Dunes` (`junkDensityFactor` 0) had
zeroed the hulk exactly as it appeared to zero scrapfields. **OPS settled it from
IL in minutes and the hold is WRONG:**
- `GenStep_ScatterGroupPrefabs : GenStep_Scatterer`, overriding neither
  `CalculateFinalCount` nor `GetPlacementFactor` — so the hulk **is** subject to the
  junk factor. That half held.
- **But the hulk emitted a could-not-find-cell warning (`Player.log:6759`), and a
  zero count never enters the placement loop, so it cannot warn.** ⇒ count ≥ 1 ⇒
  the factor was not 0 on that tile.
⇒ **`c74baa9` (minSpacing 85 → 0) did NOT fix the wrong thing.** The
minSpacing/roofed hypothesis is live and this is the load that tests it.

🔴 **What survives, and it is a CAMPAIGN risk, not a quicktest one:** the mutator
table is real — of 337 mutators, **`Dunes`, `Iceberg`, `VEE_DetachedIceberg`,
`VEE_IceAndFire` and `VEE_QuicksandDunes` have `junkDensityFactor` 0**, and both
`JawaScrapfields.xml:93` and `JawaGroundHulk.xml:99` set `isJunk`. **If the campaign
landing tile carries `Dunes`, both place NOTHING, silently, with no warning.** The
Jawa clan is a scavenger clan on a desert world. **Check the tile's mutators before
the campaign worldgen, not after.**

🔴 **The hulk needs a COLD LOAD, and the map must be generated AFTER it.** A
save-load of an existing map does not re-run GenSteps. Do not test it on a map
the running process already made.

> **Why, measured 2026-08-14:** the `minSpacing 85 -> 0` fix (`c74baa9`) was
> deployed at **01:33:48**; `RimWorldWin64` PID 16112 started at **01:03:26**, and
> RimWorld reads defs **once, at startup**. That process therefore held
> `minSpacing 85` — the exact def that found no cell on 2 of 2 maps — so a no-show
> on it would have read as a **third failure of a def that was already fixed**.
> `jawa/get_def Jawa_StampGroundHulk` does **not** expose `minSpacing`
> (`extra: null`), so the file mtime is the evidence, not the bridge.
>
> ⚠️ **Generalises past the hulk:** `find "<Steam>/Mods" -newermt "<process
> StartTime>"` is the check. Any def deployed after launch is invisible to the
> running game while looking perfectly deployed on disk.

✅ **Scrapfields is unaffected** — `JawaScrapfields.xml` is 2026-08-13 16:42, well
before any recent launch, so it is testable on a map the current process made.

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

## 5e. ⭐ BATCH B2 — LATE ADDITIONS, assembled by PROJECT 2026-08-14 from all four
seat queues. **Every one is scratch-map or paused. None needs a world.**

_The run sheet was 1.5 h behind the queues when the restart was called. These are
the items that sweep surfaced; each is confirmed by its owning seat this window._

| # | call | owner | why it is worth a line |
|---|---|---|---|
| L1 | **`rimworld/spawn_thing def=SmallThruster x=45 z=131`** — read the returned/inspect string for `WarningThrusterInside`. ⚠️ **`jawa/spawn_thing` DOES NOT EXIST** — not among the 26 names; the prefix is vanilla `rimworld/`, or `jawa/spawn_batch` for more than one (BRIDGE, offline) | CREATE | **Cheapest launch gate we own.** Outdoor-required ⇒ the exported hull needs its stern cut back, a whole deck re-lay. Substructure-free-only ⇒ nothing to change. One paused call decides a large piece of rework |
| L2 | `jawa/order_pawn targetId=<pilot console thingId> waitTicks=0 unpause=false` — read `canReach` | CREATE | 🔴 `pathEndMode` must stay `interactioncell` (the default when `targetId` is set). **The cell beside a console is a different verdict from the vanilla `PawnCanFillRole` gate** — do not substitute one for the other |
| L3 | Fire ONE Galactic Empire raid and screenshot it — 🔴 **three-step procedure below the table, do not improvise it** | VISION | VISION's own words: *the biggest open design question I own.* V6/V7/V25 have three layers of analysis and **nobody has looked at it on screen.** ~5 min. **Before we repair the antagonist, someone must see whether it reads as one** |
| L4 | Spawn `KotORDroidGood_3C` **twice** — the 2nd must NRE | OPS | 30 s, any map. O12's whole causal chain (`isOrganic=false` ⇒ no `Pawn_RelationsTracker` ⇒ HAR NRE on the 2nd same-def pawn) rests on this. **If the 2nd does not throw, the chain is wrong and O12 re-opens.** An owner decision is queued behind it |
| L5 | Full-map `listerThings` count of `ChunkSlagSteel` — **NO sampling** — plus `TileInfo.Mutators` and map size. 🔴 **ONLY ON A MAP GENERATED THIS SESSION — see the block below** | OPS | v1 row 4's open defect. ⚠️ **Match the band to the def the map was BUILT with: 75–125 pre-`de1018b`, 44–56 after.** ≥75 closes it as a MEASUREMENT defect, not a content one. The standing "11" was never a count — it was 8,100 sampled cells extrapolated, and where those rects sat is recorded nowhere |
| L6 | `jawa/list_things`, `jawa/clear_ui`, `set_roof_batch`/`get_roof_batch` | BRIDGE | Never-run tools with no batch anywhere. `clear_ui` **gates the art re-shoot** — the old 12 screenshots are non-evidence because the dev log covers frame centre |
| L7 | Re-run P1 `AV_DogSled` | BRIDGE | `spawn_batch` now routes `VehicleDef` through `VehicleSpawner` **by reflection**. Unproven, and the reflection is what keeps the companion loading without Vehicle Framework |

#### 🔴 L5 IS NOT MEASURABLE ON AN OLD SAVE — OPS, 2026-08-14, verified by PROJECT against the def

**`Jawa_ScatterScrapfields` is a `GenStepDef`** wrapping `GenStep_ScatterThings`,
order 960 (`src/Jawa/Jawa_Patches/Defs/MapGeneration/JawaScrapfields.xml:103-107`).
**A GenStep runs at MAP GENERATION and never again** ⇒ a map's `ChunkSlagSteel`
count is **frozen with whatever def was deployed the moment that map was made.**

The game copy carried `isJunk` until the 13:40 deploy tonight. `isJunk` makes
`GenStep_Scatterer.CalculateFinalCount` multiply by `GetPlacementFactor`, which is
the **product of `TileMutatorDef.junkDensityFactor` over every mutator on the
tile** — and **`Dunes` is one of five live mutators whose factor is ZERO.** ⇒ every
pre-existing map was generated with the step silently zeroed.

| you ran L5 on | verdict |
|---|---|
| a map generated **this session** | ✅ real. **44–56 in 4–6 clumps** closes v1 row 4 |
| the existing colony save | ⛔ **"not measurable here" — NOT "44–56 missed".** You measured the OLD def |

⚠️ **The 75–125 figure is not a measured pre-state and is not a comparison band
for anything.** Per the def's own header it came from an arithmetic that omitted
`GetPlacementFactor` entirely. **L5 must state which map it ran on.**

📌 **Generalises: a one-shot generator's output dates the DEF THAT BUILT IT, not
the def on disk.** Before counting anything a GenStep placed, ask when the map was
made. Same shape as *artifact right, consumer stale* — the consumer here is the map.

#### 🔴 L3's procedure — BRIDGE, IL-confirmed 2026-08-14. Follow it verbatim.

**The faction you pass is not the faction that raids.**
`IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps your faction **only if**
non-null AND `FactionUtility::HostileTo(Faction.OfPlayer)` AND (`!deactivated` OR
`parms.forced`). IL_001f/0036/0055 all branch to IL_0059, where
`ldflda IncidentParms::faction` goes **by reference** into
`PawnGroupMakerUtility::TryGetRandomFactionForCombatPawnGroupWeighted`, **which
overwrites it.** ⇒ if `OuterRim_GalacticEmpire` is not hostile, the raid fires,
reports `success:true`, and VISION photographs **a different antagonist**. Nothing
in the reply flags it.

1. `jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true` — **abort on `canFireNow:false`.**
2. Fire, then **read the `faction` field in the REPLY, not the one you sent.** The tool reports `parms.faction` *after* the worker ran; the read-back is the only evidence of which faction actually came.
3. **Pass `points` explicitly.** `points<=0` takes the storyteller default — tens of points on a fresh quicktest, i.e. one trivial attacker, which cannot answer *"does the Empire read as an antagonist"*.

📌 **Generalises: a parameter you pass is not a parameter that survives.** Engine
workers take `IncidentParms` **by ref** and rewrite it. **Assert on the value read
back, never the value sent.** Same shape as `set_terrain`'s dropped `def=`.

#### 👁️ EYES-ON, no bridge call possible — open the xenotype picker and LOOK

**OPS, from the O18 scoped sweep (`cbe6f1c`). Two `iconPath` warnings that cannot
be settled offline** — vanilla textures live in asset bundles, so a right path and
a wrong one look identical from outside the game.

| look at | path |
|---|---|
| xenotype **`Jawa_Xeno_Gamorrean`** | `UI/Icons/Xenotypes/Pigskin` |
| gene **`Jawa_Head_Plain`** | `UI/Icons/Genes/Gene_Hair` |

**A pink or blank square is the defect. Both drawing closes them permanently.**
Cheapest eyes-on item on the sheet — one screen, no map required.

⛔ **NOT in any batch, deliberately:** the ten art-fix mods. The standing directive
makes **the owner's own eyes** the gate, so it is an owner-look item and no seat
can close it with a bridge call. CREATE's ruling, and it is right.

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
| ~~**v1 row 3 — fire *The Claim***~~ | 🔓 **NO LONGER TRUE — moved out of this section 2026-08-14.** The float-menu route is still dead (`rimworld/right_click_cell` reports *"Dispatched a live right-click…"* and does nothing — `skills/rimbridge/references/traps.md:294`), but the menu was never the only route. **BRIDGE is building `jawa/fire_quest`**, deploying in the same shutdown window as `jawa/get_defs`. See §1c |
| **ToolBeltFix** | Needs the apparel **WORN**, and the reason is now PROVEN rather than assumed: **no `PawnKindDef` spawns `VAEA_Apparel_ToolBelt` anywhere** in the workshop tree, `Mods/` or `Data/` — every reference is loot. ⇒ held for a **force-equip tool**, not for a load. ⛔ **`[v2]`** — the equip primitive is not v1 and must not take window space |
| ~~**CereanManeFix / SauridFrillFix**~~ | 🔓 **NO LONGER TRUE — collectable on ANY standing map, 2026-08-14.** Both DO name a pawnkind: `OuterRim_Cerean` (hair `OuterRim_CereanMane`, face **SOUTH**) and `VRESaurids_Villager_Saurid` (hair `VRESaurids_Littlefoot`, face **NORTH** — the donor ships `CenterFrill8_north-.png` with a trailing hyphen while `CenterFrill7_north.png` beside it is correct, so north is the only broken rotation). `jawa/spawn_pawn` + `jawa/set_pawn_style` + `jawa/set_pawn_rotation` are all live. **No load, no fresh map.** ⛔ **`[v2]` — observation only, and it does NOT compete with the three v1 window items** |
| **The seven fix mods generally** | ⚠️ **None can ever produce a log line.** `Failed to find any textures at` fires only when **every** direction of a `Graphic_Multi` is missing, so a single absent or zero-alpha facing is a silent south-fallback. They settle by eyeballing a pawn, never by `harvest_log.py` |

🔴 **THE TRAP THAT WOULD HAVE WASTED THE TWO ITEMS ABOVE — a pawnkind spawn alone
tests NONE of them.** All three fixes are `HairDef`/apparel **`texPath`s**, not
pawnkind art. Spawn the pawn without setting the style and you photograph a
default and record it as passed. **Spawn, THEN set style, THEN set rotation.**
📌 Generalises: *the call existing is not the same as the call being sufficient* —
name the call **and** the state it must be in.

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

## 8b. 🔻 THE NEXT SHUTDOWN WINDOW — already booked. Do not rediscover this.

**Three things need the game DOWN and none of them can be done while it runs.**
Assembled 2026-08-14 during this load; the load itself is the build time.

| # | item | owner | why it waits for a shutdown |
|---|---|---|---|
| S1 | 🔴 **`JawaSeaShaper.dll` — DEPLOYS SOLO** | CREATE builds · OPS deploys | Repo `b7730027` vs deployed `82b48e53` @ 08-13 23:57 — **the sea fix is NOT live.** The write **fails `OSError 22` while the game runs** (loaded and locked; the refusal is safe, it cannot truncate). A new assembly poisons attribution for anything beside it ⇒ **solo, and it is the gate on any worldgen load** |
| S2 | `jawa/ideo_of` | BRIDGE | Built offline during this load. Companion work needs a **shutdown**, not a startup |
| S3 | `jawa/biome_probe` | BRIDGE | Same. Unblocks 28 of 29 biome removals currently judged from def fields alone |

⚠️ **S2 and S3 were deliberately kept OUT of the pre-launch build** — rushing two
unproven tools into the one artifact that is currently proven-good, minutes before
launch, risks 26 working tools to add 2. **That was the right call and it is not to
be re-litigated;** it is why they are here.

🔴 **Consequence to state plainly: worldgen is at minimum one shutdown away.**
S1 must land first, and it cannot land while the game is up.

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

**The offline dump describes 580 mods** — `observed/2026-08-13/dumps/defnames.580.2026-08-13.json`
— while **the live stack is 585** (`<activeMods>` in `ModsConfig.xml`, measured by
OPS and agreed independently by the O18 sweep header). ⚠️ **Both numbers are
correct and they are about different things:** 580 is what the dump *was built
from* on 08-13, 585 is what is loaded now. **That five-mod gap IS the reason to
re-run `refresh.py`** — it is not an error to fix. (A naive `grep -c "<li>"` says
590; the `<knownExpansions>` block is the difference, and is the likely origin of
any stray count.)
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
