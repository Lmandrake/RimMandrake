# NEXT_RELOAD.md — the run sheet for the NEXT game load

_A cold load costs **~23–30 minutes**. It is the scarcest resource in this project.
This file exists so a load is never spent on one question._

**Read top to bottom. It is ordered.** Down-window → call #1 → batches → release.
**Every item names the CALL that produces its evidence.** If a check has no call it
is in §7 (cannot be collected) and you do not attempt it.

Assembled by DECIDE from `infrastructure/state/queue/<SEAT>.md`. Harvest and clear
afterwards — a closed item is deleted. How to spend a load:
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

### 1.0 🔴 THIS WINDOW — the deploy manifest, in order. Opened 2026-08-15.

Assembled by DECIDE against the owner's broadcast *"game is down, stage the next
load and prepare additional content"*. **Everything below §5 is uninterpretable
until this section is finished** — five of the six live items are `blocked — needs
deploy`, not blocked on a question.

| # | deploy | item | why this order |
|---|---|---|---|
| **0** | `echo all > ".../DefDump/dump_request.txt"` — §1a | — | 🔴 **One `echo`, and it is not optional this load.** Read at STARTUP only. The dump on disk is from **2026-08-14 01:20**, before eleven mods left and `mandrake.starwarsraces` arrived, so every `validate_patch.py --defs` run against `Jawa_Armoury` and `Jawa_Patches` is currently checked against a def universe that no longer exists. Miss it and the next load pays 23 minutes for it |
| 1 | `python.exe src/RimMandrake/bridgetools/build.py --gm --apply` — or `./src/RimMandrake/Utils/shutdown_deploy.sh` | BUILD **B1**, closes **B0** | An **assembly, solo**. Everything in §3–§6 is a `jawa/*` call, so a wrong companion poisons every result after it. 🔴 `--gm` or `fire_incident` + `send_letter` are stripped and §5's L3 cannot fire at all |
| 2 | `deploy_custom_mods.py --mod JawaPlantGrowth --plan` then `--apply` | CHECK **C38** | The **second and last assembly**. Deploy it **alone**, not beside #3 — a new DLL in a mixed batch poisons attribution for everything beside it. Then add `mandrake.jawaplantgrowth` to `ModsConfig.xml` **after `brrainz.harmony`** or the Harmony postfix never binds |
| 3 | `deploy_custom_mods.py --mod DesertVehicleReskin --plan` then `--apply` | CHECK **C39** + **C41** | Pure XML and loose PNGs — no window needed, but do it now so it rides this load. This is an **update**, the mod is already at `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\DesertVehicleReskin`. 🔴 `mandrake.desertvehiclereskin` must sit **after** `sarg.alphavehiclesneolithic` or the labels change and the art does not |
| 4 | `ModsConfig.xml` chores in ONE pass | BUILD **B25** | Not gated on this window at all (§1b) — a config file is writable game up or down. Standing changes: **mechanoids OFF**, disable `com.yayo.yayoAni.continued`, pin the six `loadBottom`+`loadAfter` userRules |
| 5 | Write the three signatures into `EXPECTED_FAILURES` | BUILD **B23** | Must land **before launch** or the load spends attention on errors we already know about |
| 6 | `python.exe src/RimMandrake/Utils/refresh.py` | B25(b) | **Last.** It reads the list the four steps above just finished changing |

⛔ **NOT in this window, and this is a change:** `JawaSeaShaper.dll`. The repo copy
(`b7730027`) and the deployed copy (`82b48e53`) differ and that is **expected** —
the sea left v1 when the owner ruled worldgen manual on 2026-08-14. See D-CRIT in
`infrastructure/state/queue/DECIDE.md`, which was superseded today and used to say
the opposite. Do not spend the window on it.

📌 **The window is not the load.** Steps 2 and 3 make §5's items collectable; they
do not collect anything. Nothing here is finished until the game is up and §5 runs.

### 1a. 🔴 Arm the def dump — NOT optional on THIS load. Do it now.

```bash
echo all > "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/dump_request.txt"
```

**Read at STARTUP only** — armed before launch, or not at all. There is no second
chance inside the load.

⚠️ **This section used to read "OPTIONAL, gates nothing". That was wrong, and BUILD
caught it 2026-08-15.** It is true on a load where the mod set has not moved. **This
load is not one of those.** The live dump at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\`
was written **2026-08-14 01:20**, and since then eleven mods left and
`mandrake.starwarsraces` arrived — 585 → 575, including the three donors whose defs
half the repo still names. ⇒ **The dump on disk describes a def universe that no
longer exists.**

What is actually downstream of it, and this is the gate:

- **`validate_patch.py --defs` is only as true as the dump it is handed.** Every
  patch in `Jawa_Armoury` and `Jawa_Patches` validates against it. A patch whose
  xpath now matches nothing reports **clean**, because the def it targets is still
  in the stale dump — and 🔴 **a patch that matches nothing logs nothing at load
  either**, so neither route catches it.
- `refresh.py` cannot manufacture it. Its own table says the live dump costs **A
  FULL GAME LOAD, ~23 minutes**. Skip the arming and the *next* load pays for it.

📌 **Cost of arming: one `echo`. Cost of not arming: every offline validation until
the load after this one runs against the wrong mod set.** That is not "gates
nothing" — it silently gates correctness on everything that consumes a def dump.

### 1b. `ModsConfig.xml` — BUILD's alone, and NOT gated on this window

🔴 **Owner's ruling, 2026-08-15: nothing blocks on RimSort, or on the game being
closed, for a config file of any kind. Never ask whether RimSort is open.** It does
not autosave, and the owner will not click Save without asking first. So there is no
collision to race, no mtime to read first, and no window to wait for. Write it.

**RimWorld does not rewrite it on exit** either — measured twice. This section is in
§1 for ordering convenience only; a config edit is legal at any moment, game up or
down. The down-window is for **assemblies**, which the OS locks while the game runs.

A mod-list change takes effect **only at startup**. Editing while the game runs is
inert, not destructive — reading the running game as evidence the edit "failed" is
the trap.

After an external edit, RimSort's in-memory view is stale. The whole mitigation is
one sentence to the owner: *"RimSort is open — hit Refresh."*

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

📐 **If the window gets tight, §1.0's order IS the ranking** — it is sorted by what
the window destroys, not by severity. A severe bug whose fix is already live is not
a claim on a scarce window.

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

**Two things settle in that first harvest and nowhere else:**

- 🔴 **CHECK C36 — the donors-off configuration.** `btd.xenotyperemix.starwars`,
  `guy762.starwarsxenotypes` and `neronix17.outerrim.galacticdiversity` are OFF and
  `mandrake.starwarsraces` stands alone. **Pass = the log carries no `Could not
  resolve cross-reference` naming a `guy762_`, `OuterRim_` or `BTD_` def, and no
  `Could not find type named`.** `harvest_log.py --show crossref` reads the actual
  lines. ⚠️ 70/70 species already spawn with the right xenotype — that half is
  **banked, do not redo it**. Only the crossref sweep is open.
- **The `[JawaPlantGrowth]` startup line** (§5 L6 step 1). It is emitted once, at
  startup, and it is the only positive evidence that assembly bound at all.

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

🔴 **Read the rows in order.** L0 is one screenshot and it decides whether a large
body of art work closes or reopens; L1–L4 need `jawa/*` tools that only ship in
§1.0 step 1. **Detail lives in the queue item named in each row — this table is the
order and the call, not the whole plan.**

| # | call | item | why it is worth a line |
|---|---|---|---|
| **L0** | `jawa/clear_ui`, then `jawa/spawn_pawn kindDef=Colonist faction=PlayerColony xenotype=RimMandrakeRodian`. **Look at its face. Screenshot it.** | CHECK **C37** | 🔴 **FIRST ACTION ON THE MAP.** Facial Animation's per-xenotype opt-out was rewritten (86 → 156 entries) but FA reads its config **only at startup**, so it has never once been active. **Snoot visible ⇒ the whole art failure closes.** Still a human face ⇒ FA was not the cause and the head-gene findings (10 species with no head-forcer, Rodian forced to a generic Outland reptile head) move back to the top. One pawn, one look. ⚠️ **`faction` is not optional** — omit it and the pawn spawns into the Empire, hostile |
| L1 | `rimworld/spawn_thing def=SmallThruster x=45 z=131`, then `jawa/inspect_string` on it — read for `WarningThrusterInside`. ⚠️ **`jawa/spawn_thing` DOES NOT EXIST**; the prefix is vanilla `rimworld/`, or `jawa/spawn_batch` for more than one | BUILD | **Cheapest launch gate we own.** Outdoor-required ⇒ the exported hull needs its stern cut back, a whole deck re-lay. Substructure-free-only ⇒ nothing to change. One paused call decides a large piece of rework. Needs `jawa/inspect_string` (§1.0 step 1) |
| L2 | `jawa/spawn_pawn kindDef=Jawa_Tribal_Scavenger` **×6**, then one Geonosian Foundry Hive pawn, then read a Jawa's gear and let it socialise | CHECK **C40** | Three deployed-but-unproven fixes in one spawn pass. **Six armed Jawa** (not civilians) · **a Geonosian that is not a baseliner** (empty `xenotypeChances` looks like a content gap, not a dropped node) · **a Jawa wearing `guy762_Robes_jawa` + `guy762_JawaHood` and speaking a Jawa voice line**. 🔴 The gear defs live in a mod we KEPT — their presence in a dump proves nothing; **the pawn wearing them is the only evidence** |
| L3 | Fire ONE Galactic Empire raid and screenshot it — 🔴 **procedure below the table, do not improvise it** | DECIDE | The biggest open design question DECIDE owns: **before we repair the antagonist, someone must see whether it reads as one.** ~5 min. Needs `jawa/set_faction_relation` (§1.0 step 1) if the Empire is not already hostile |
| L4 | Spawn `KotORDroidGood_3C` **twice** — the 2nd must NRE | BUILD | 30 s, any map. The whole causal chain (`isOrganic=false` ⇒ no `Pawn_RelationsTracker` ⇒ HAR NRE on the 2nd same-def pawn) rests on this. **If the 2nd does not throw, the chain is wrong and the item re-opens.** An owner decision is queued behind it |
| L5 | **Architect ▸ Vehicles** — read the five Tier-0 land blueprint labels. Then spawn `AV_OxCart`, `AV_Chariot`, `AV_CoveredCarriage`, `AV_WarChariot`; rotate each north/south/east; **Architect ▸ Props and Decor** for the `VFEPD_*` twins | CHECK **C41** + **C39** | Reads verbatim `dewback cart` · `ronto wagon` · `bantha dray` · `dewback war cart` · `eopie sled`; `Chariot`/`Ox cart`/`Dog Sled` appear **zero** times. 🔑 **A Vehicle Framework vehicle spawns as a PAWN** — `jawa/list_things` returns nothing at the cell, use `jawa/list_pawns`. 🔴 **The art reaches every def by texPath override whether or not a patch ran** — only the LABEL and the per-def COLOUR are evidence. The **architect menu is the tell**, because the blueprint is a third def the sled pass never touched. ⛔ Do not check west (auto-mirrored from east) |

#### 🌱 L6 — plant growth. **A SECOND MAP, and it is the point.** CHECK **C38**

Do this last: it needs its own quicktest, and then **a second one on `PoisonForest`**.
A biome branch cannot be tested by walking across the first map.

1. **Startup log first** — `[JawaPlantGrowth] scaling <N> plant defs (default x4, tree x2.5), <M> exempt, 1 terminator biome(s) at x0.4.` 🔴 **This line is the only positive evidence the assembly ran.** Absent ⇒ the answer is *"not deployed / not in ModsConfig"*, **not** *"no effect"*, and nothing below it means anything.
2. Map 1 (temperate/arid): spawn `Plant_Corn` and `Plant_TreeOak` side by side on fertile soil, read growth %, run one in-game day, read again. **The corn must be roughly 4× the oak's growth percentage** (~36% vs ~8%). Near 1× ⇒ the tree band is not firing.
3. Same map: spawn `Plant_TreeAnima` — it must read ~4% after that day, **not** ~10%. That is the exemption.
4. **Map 2, generated fresh on `PoisonForest`** (Advanced Biomes): same two plants, same day. 🔴 **The corn gains ~10%, LESS than map 1 and less than vanilla's ~8.8% would be an increase over.** Slower, not faster. **This is the check most likely to be skipped and the only one that proves the biome branch runs at all.**

⚠️ A 0% reading is not evidence — the postfix returns early on `__result <= 0`
(night, out of temperature band, unlit). **Read growth in daylight, in season.**
⛔ Not in scope: wild-plant REPOPULATION. `wildPlantRegrowDays` is R-G4, it did not
ship, and a burnt PoisonForest staying bare proves nothing about this patch.

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
| **The float-menu route** | `rimworld/right_click_cell` reports *"Dispatched a live right-click…"* and does nothing, as per the trap file. Anything whose only route is a context menu is uncollectable |
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
