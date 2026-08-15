# NEXT_RELOAD.md — the run sheet for the NEXT game load

_A cold load costs **~23–30 minutes**. It is the scarcest resource in this project.
This file exists so a load is never spent on one question._

**Read top to bottom. It is ordered.** Down-window → call #1 → batches → release.
**Every item names the CALL that produces its evidence.** If a check has no call it
is in §7 (cannot be collected) and you do not attempt it.

Assembled by DECIDE from `infrastructure/state/queue/<SEAT>.md`. Harvest and clear
afterwards — a closed item becomes ONE line in `CLOSED.md`. How to spend a load:
`skills/rimworld-load-round/SKILL.md`. What v1 is:
`infrastructure/state/V1_CHAIN.md`.

🔴 **Worldgen is the owner's and it is done by hand.** He builds a world, saves it,
and we ship it as a fixed resource. **No seat runs campaign worldgen, and nothing
in this file schedules it.**

⛔ **Do not add art-fix work.** Standing owner directive: art *fixing* is stopped
until the owner personally verifies art is broken. Art *observation* is welcome —
§5's eyes-on rows are observation, and nothing here schedules a fix.

---

## 1. 🔻 WHILE THE GAME IS DOWN — the only window for a deploy

Everything in this section is inert or refused while RimWorld runs. If the game is
already up, skip to §2.

### 1a. Arm the def dump — OPTIONAL, gates nothing

```bash
echo all > "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/dump_request.txt"
```

**Read at STARTUP only**, so it is armed before launch or not at all. It clears the
offline dump's staleness and blocks nothing.

### 1b. `ModsConfig.xml` — BUILD's alone

**RimWorld does not rewrite it on exit** — measured twice. Only we and the owner
(in RimSort) write it, so there is no window to miss.

🔴 **The hazard is a LIVE collision.** The owner reorders in RimSort with the game
down; a seat writing over that clobbers the ordering and neither party is warned.

> **Do not write `ModsConfig.xml` unless you have just read its mtime.** Announce
> mod-list edits like a bridge take. If in doubt, ask the owner whether RimSort is
> open — they are the only reader who knows.

A mod-list change takes effect **only at startup**. Editing while the game runs is
inert, not destructive — reading the running game as evidence the edit "failed" is
the trap.

Standing changes when a list edit is next made: **mechanoids OFF** (owner's
ruling), and **disable `com.yayo.yayoAni.continued`** `[v2]` — the lightsaber flies
up-and-behind on draft and Yayo's is the suspect.

Then `python.exe src/RimMandrake/Utils/refresh.py` — **Windows** interpreter; WSL's
`python3` fails on the Windows paths with a bare `cannot read ModsConfig`.

### 1c. 🔴 The five deploy traps. Each has cost a load or nearly did.

| trap | what it does |
|---|---|
| **`--apply` bare** | overwrites the game copy from the repo **including a peer's half-finished work**. Always scope it: `deploy_custom_mods.py --mod <name> --apply` |
| **companion built without `--gm`** | silently **strips `jawa/fire_incident` and `jawa/send_letter`** off the game copy. The build refusing by default is the guard working. A low tool count looks identical to a stale build — check which you passed before concluding anything |
| **`strings -a`** | scans 7-bit ASCII, so a method-body literal (UTF-16LE, `#US` heap) reads as **ABSENT**. It proves a tool **name** and nothing about its body. **Use `strings -a -el`** |
| **deploying after launch** | RimWorld reads defs **once, at startup**. A def written after the process started is invisible to it while looking perfectly deployed on disk. Check with `find "<Steam>/Mods" -newermt "<process StartTime>"` before believing any no-show |
| **a new assembly in a mixed batch** | poisons attribution for everything beside it. Deploy an assembly **solo**. ⚠️ The write fails `OSError 22` while the game runs — loaded and locked; the refusal is safe, it cannot truncate |

📐 **If the window gets tight, rank by what the window does to the item's VALUE,
not by severity.** Ships first: value is *destroyed* by the event this window
precedes. Drops first: value is *already being collected* and the change would
merely improve it — a severe bug whose fix is already live is not a claim on a
scarce window.

---

## 2. 🔴 THE MOMENT THE GAME IS UP — harvest the startup log FIRST

**Before any bridge call that mutates anything.**

```bash
python.exe src/RimMandrake/Utils/harvest_log.py
```

**Why the order matters:** the open `GeneratePawnRelations` NRE cluster landed
mostly on pawns a seat had **spawned itself**. The question is whether it is an
artefact of debug spawning or a real defect in relation generation — which runs for
faction leaders and fails silently. **The moment anyone calls `jawa/spawn_pawn`,
that cluster becomes unattributable again and the question cannot be answered.**

Harvest first. Then spawn.

---

## 3. 🔴 CALL #1 — the tool-surface census. Nothing below is interpretable until it passes.

```
rimbridge/list_tools          -> count the jawa/* names
```

🔴 **DO NOT COMPARE AGAINST A NUMBER WRITTEN IN A DOC. DERIVE IT.** Three files
once carried three different expected counts while the artifact defined a fourth
⇒ **a CORRECT deploy would have FAILED the gate.**

**Derive the expectation at census time, from the artifact you just deployed:**

```bash
grep -rhoE --include='*.cs' '"jawa/[a-z_]+"' src/RimMandrake/bridgetools/ | sort -u | wc -l
```

🔴 **`--include='*.cs'` IS LOAD-BEARING. Without it the count is one too high** —
it picks up a `[Tool("jawa/...")]` string inside a comment in
`prove_new_tools.py:112`, and fails a correct build.

| you deployed | expect |
|---|---|
| the artifact **with `--gm`** | that count |
| the artifact **without `--gm`** | that count **minus 2** — `fire_incident` and `send_letter` are stripped |
| anything else | **STOP.** The deployed companion is not the one you measured, and every result below is evidence of nothing |

📌 **Gates compare measurements to measurements, never to prose.** A hardcoded
count in a gate document goes stale on every deploy, silently, and then fails the
correct build.

### Two traps that govern every call after this one

🔴 **THE GAME IS NOT REACTIVE FOR ~40 s AFTER THE BRIDGE FIRST ANSWERS**, whatever
`currentMapReady` and `longEventPending` report. Owner-observed; baked into
`load_session.py` as a settle before any mutation. **Read-only calls are fine
inside that window; only mutation waits.** ⚠️ This is a signal saying the TOOL is
ready being read as the GAME being ready.

🔴 **`jawa/*` tools need a GAME, not just a running process.** Every tool ends
`Find.TickManager?.TicksGame ?? -1`, and `Find.TickManager` dereferences
`Current.Game` — **`?.` guards the RESULT, not the CALL.** At the main menu the
getter throws and *every* tool returns a bare `Object reference not set to an
instance of an object`, naming nothing. A quicktest is enough. ⚠️ `TicksGameSafe()`
is queued at BUILD B1 to fix this; until it is deployed, do not conclude a branch
is broken from a menu call.

🔴 **A def dump is DISK, not RUNTIME.** A dump answers *what the XML says after
patching*; a live `get_def` answers *what the game resolved*. **Where they
disagree, the live read is the one that counts.** This is doctrine, not
convenience — it nearly cost v1 row 5 its correct ruling.

---

## 4. 🌉 BATCH A — the three never-run pawn tools, ~2 minutes, no per-item gate

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
  inheritable, so its genes land as endogenes and survive a later conversion —
  pass `clearEndogenes` deliberately or expect residue.

---

## 5. ⭐ BATCH B — the open live items. None needs a world; a quicktest is enough.

```
rimworld/start_debug_game_ready       -> a fresh map in ~30 s
```

⚠️ That call **exceeds the 30 s timeout and succeeds anyway** — do not retry, or
you get a second map. Reconnect and poll `list_pawns`.

| # | call | seat | why it is worth a line |
|---|---|---|---|
| L1 | **`rimworld/spawn_thing def=SmallThruster x=45 z=131`**, then `jawa/inspect_string` on it — read for `WarningThrusterInside`. ⚠️ **`jawa/spawn_thing` DOES NOT EXIST**; the prefix is vanilla `rimworld/`, or `jawa/spawn_batch` for more than one | BUILD | **Cheapest launch gate we own.** Outdoor-required ⇒ the exported hull needs its stern cut back, a whole deck re-lay. Substructure-free-only ⇒ nothing to change. One paused call decides a large piece of rework. **Blocked until `jawa/inspect_string` deploys (BUILD B1)** |
| L3 | Fire ONE Galactic Empire raid and screenshot it — 🔴 **procedure below the table, do not improvise it** | DECIDE | The biggest open design question DECIDE owns: **before we repair the antagonist, someone must see whether it reads as one.** ~5 min. Needs `jawa/set_faction_relation` (BUILD B1) if the Empire is not already hostile |
| L4 | Spawn `KotORDroidGood_3C` **twice** — the 2nd must NRE | BUILD | 30 s, any map. The whole causal chain (`isOrganic=false` ⇒ no `Pawn_RelationsTracker` ⇒ HAR NRE on the 2nd same-def pawn) rests on this. **If the 2nd does not throw, the chain is wrong and the item re-opens.** An owner decision is queued behind it |

#### 🔴 L3's procedure — IL-confirmed. Follow it verbatim.

**The faction you pass is not the faction that raids.**
`IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps your faction **only if**
non-null AND `FactionUtility::HostileTo(Faction.OfPlayer)` AND (`!deactivated` OR
`parms.forced`). Otherwise `ldflda IncidentParms::faction` goes **by reference**
into `PawnGroupMakerUtility::TryGetRandomFactionForCombatPawnGroupWeighted`,
**which overwrites it.** ⇒ if `OuterRim_GalacticEmpire` is not hostile, the raid
fires, reports `success:true`, and you photograph **a different antagonist**.
Nothing in the reply flags it.

1. `jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true` — **abort on `canFireNow:false`.**
2. Fire, then **read the `faction` field in the REPLY, not the one you sent.** The tool reports `parms.faction` *after* the worker ran; the read-back is the only evidence of which faction actually came.
3. **Pass `points` explicitly.** `points<=0` takes the storyteller default — tens of points on a fresh quicktest, i.e. one trivial attacker, which cannot answer *"does the Empire read as an antagonist"*.

📌 **Generalises: a parameter you pass is not a parameter that survives.** Engine
workers take `IncidentParms` **by ref** and rewrite it. **Assert on the value read
back, never the value sent.** Same shape as `jawa/set_terrain`, where the bridge
**silently drops** an unknown parameter name — `def=` instead of `terrainDef=`
paints nothing and reports no error.

#### 👁️ EYES-ON, observation only — open the xenotype picker and LOOK

Two `iconPath` warnings that **cannot** be settled offline: vanilla textures live
in asset bundles, so a right path and a wrong one look identical from outside.

| look at | path |
|---|---|
| xenotype **`Jawa_Xeno_Gamorrean`** | `UI/Icons/Xenotypes/Pigskin` |
| gene **`Jawa_Head_Plain`** | `UI/Icons/Genes/Gene_Hair` |

**A pink or blank square is the defect. Both drawing closes them permanently.**
One screen, no map required.

---

## 6. BATCH C — the cheapest launch gate we own

### `NoPathToPilotConsole` — one call, no walk, game stays PAUSED

```
jawa/order_pawn   pawnId=<colonist>   targetId=<consoleThingId>   waitTicks=0   unpause=false
```

Returns `canReach` on a paused game. **No movement, no time passes, nothing on the
map changes.** Needs a map with the gravship on it.

🔴 **`pathEndMode` must stay `interactioncell`** — it is the default when
`targetId` is set, so do not override it. The vanilla gate is `PawnCanFillRole` →
`CanReach(…, InteractionCell, …)`, and the cell *beside* a console is a
**different verdict**. **A door is not a path**: doors are in the export, and that
is exactly what this call tests. Reference:
`design/Jawa/worldbuilding/gravship_flight_invariants.md`.

---

## 7. 🚫 GATES THAT CANNOT BE COLLECTED — do not attempt these

Filed so nobody spends a load discovering it. Each is here because **the call that
would produce the evidence does not exist or is measured broken.**

| item | why it cannot be collected |
|---|---|
| **ToolBeltFix** | Needs the apparel **WORN**, and **no `PawnKindDef` spawns `VAEA_Apparel_ToolBelt` anywhere** — every reference on disk is loot. ⇒ held for a **force-equip tool**, not for a load. ⛔ `[v2]` |
| **The float-menu route** | `rimworld/right_click_cell` reports *"Dispatched a live right-click…"* and does nothing — `skills/rimbridge/references/traps.md:294`. Anything whose only route is a context menu is uncollectable |
| **The fix mods, by log** | ⚠️ **None can ever produce a log line.** `Failed to find any textures at` fires only when **every** direction of a `Graphic_Multi` is missing, so a single absent or zero-alpha facing is a silent south-fallback. They settle by eyeballing a pawn, never by `harvest_log.py` |

🔴 **A pawnkind spawn alone tests NONE of the art fixes.** They are
`HairDef`/apparel **`texPath`s**, not pawnkind art. Spawn the pawn without setting
the style and you photograph a default and record it as passed. **Spawn, THEN set
style, THEN set rotation.** Only ONE rotation is broken in each, so a shot from the
wrong side is a false pass. Which facing per mod:
`infrastructure/state/CREATE_TEST_PLAN.md` Part 5.
📌 Generalises: *the call existing is not the same as the call being sufficient* —
name the call **and** the state it must be in.

---

## 8. 🔓 BEFORE RELEASING THE BRIDGE — unlock every pawn you touched

```
jawa/set_pawn_rotation   pawnId=<each pawn from §4>   dir=unlock
```

🔴 **`debugRotLocked` is serialised by `Thing.ExposeData`.** A pawn left locked
stays locked across **every future load**. This is litter that outlives the
session, and it is invisible until someone wonders why a pawn will not turn.

Then stamp `infrastructure/state/status/game.json` **and** broadcast one line
with `src/RimMandrake/Utils/say.py`, naming **what you left on the map** — spawned pawns, painted
terrain, the quicktest map itself. A release that only writes a state file goes
unnoticed; the owner ruled the broadcast mandatory.

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

The offline dump lags the live stack — it describes the mods it was **built from**,
`ModsConfig.xml`'s `<activeMods>` is what is **loaded now**. That gap is the reason
to re-run `refresh.py`, not an error to fix. (A naive `grep -c "<li>"` overcounts;
the `<knownExpansions>` block is the difference.)

**One carry-in, not blocking:** pin the six User Rules that carry both `loadBottom`
and `loadAfter` — `jawa.patches`, `jawa.armoury`, `jawa.doctrine`, `jawavoice`,
`jawaionweapons`, `rimdefdump`. `loadBottom` wins and `loadAfter` is ignored.
✅ The order is CORRECT anyway (0 violations across all 13, tested) — ⚠️ **but it is
riding the topological tie-break rather than being pinned**, so it is right by
luck. BUILD's, post-load.

Afterwards: triage anything new into `vendor/wisdom/benign_log_errors.md`, append
anything that surprised you to the matching
`skills/rimworld-modding/references/traps-*.md`, and file the rest into the
per-seat queues.
