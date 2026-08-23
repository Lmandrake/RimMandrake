# NEXT_RELOAD.md — the run sheet for the NEXT game load

> ## 🔴 THE 2026-08-22 EVENING LOAD RAN, AND IT IS SPENT — REP, 2026-08-22 23:5x
>
> **Everything below this block was written at 21:50 for THAT load.** It is history now,
> not a plan. Read it for the offline verifications it banked (still valid); do not read
> it as the run sheet for the next launch.
>
> **Score: 7 of 8 signatures passed. F6 FAILED — 3,037 `Could not resolve cross-reference`
> against a baseline of 25.** Cause measured, not guessed: **26 of the planet's 28 BiomeDefs
> did not exist in the running game.** Our own generated `BiomeCast_Ashkarr.xml` wrote
> `<li>` wrappers into `wildAnimals`, whose `LoadDataFromXmlCustom` reads the node NAME as
> the animal — `ArgumentNullException`, and RimWorld discarded the whole BiomeDef, 22 times.
> ⚠️ **It is the same shape as the `SkillGain` bug this file celebrates fixing above** —
> `<li>` inside a custom-loader field — found in a different generator a day later.
> It escalated past cosmetic: world generation itself now dies in
> `WorldPathGrid.CalculatedMovementDifficultyAt` on a null biome, so **no new game can start
> in a process that loaded the broken file.**
>
> ### 🔑 THE NEXT LOAD IS THE BIOME RESTORATION LOAD, AND IT HAS A GATE
>
> **Its five signatures are already written, before the launch, as the waiver requires** —
> the block headed *"the BIOME RESTORATION load"* at the foot of
> `infrastructure/state/EXPECTED_FAILURES_next_load.md`. ⚠️ **That block is numbered `§6`
> and `§6` is already a closed load with a filled Results table** — filed as
> `BIOME_BLOCK_MISNUMBERED_SIX_1` for CHECK. Read it by its title, not its number, until
> that is fixed.
>
> 🔴 **F1 is the gate: `Exception loading def from file Biomes_` must be 0. It was 22.**
> Until it reads 0, **nothing else on this load is attributable** — a missing biome poisons
> world gen, faction placement, animal spawns and every count downstream of them. Score F1
> first and stop if it fails.
>
> ### WHAT IS QUEUED BEHIND THE GATE — measured 2026-08-22 23:5x, not remembered
>
> ```
> grep -c "^needs:    \(bridge\|game-up\|harvest\)" infrastructure/state/queue/*.md
> ```
>
> | seat | doing | ready | proposed | total gated on a load |
> |---|---|---|---|---|
> | **BUILD** | 10 | 14 | 5 | **29** |
> | **CHECK** | 6 | 9 | 16 | **31** |
> | **DECIDE** | 1 | 0 | 0 | **1** |
> | | **17** | **23** | **21** | **61** |
>
> ⭐ **40 are ready for testing** (`doing` + `ready` — claimed by a seat and unblocked).
> ⚠️ **21 are `proposed`** — filed, nobody has taken them. They are not "ready"; a proposed
> item has no seat committed to reading its result, and riding one on a load usually buys
> an unread answer. Claim it first or leave it.
>
> ⛔ **AND THE HONEST GAP: most of those 40 carry no named decision string.** §2 of
> `skills/rimworld-load-round/SKILL.md` is explicit — *"an item with no named string is not
> verifiable; it is a hope."* Only the five biome signatures are written down for this load.
> **Whoever launches owes the rest a string and a baseline BEFORE the game starts**, and
> that is per item, in its own seat's hand.
>
> ### ⏳ Two things the DOWN window is the only chance for
>
> 1. **Assemblies deploy only while the game is closed** — the OS locks them otherwise.
> 2. **The previous `Player.log` is overwritten at next launch.** The evening load's log is
>    the only evidence for the biome diagnosis; copy it out before launching.
>


> 📦 **The 2026-08-22 evening load's hold-condition block and its pre-load brief moved to
> `infrastructure/state/NEXT_RELOAD_ARCHIVE.md` on 2026-08-23** — that load ran and is scored.
> Nothing was deleted. ⚠️ This is the SECOND time this file has had to be cleared of a spent
> load; the standing fix is per-load blocks with an index, filed as `RUN_SHEET_PER_LOAD_BLOCKS_1`.


---

## 1. 🔻 WHILE THE GAME IS DOWN — the only window for a deploy

Everything in this section is inert or refused while RimWorld runs. If the game is
already up, skip to §2.

### 1.0 ✅ THE DEPLOY MANIFEST IS EMPTY — reassembled DECIDE, 2026-08-22 13:05

> 🔴 **The 2026-08-15 manifest that stood here is GONE, and every row of it has shipped.**
> It listed six numbered deploys against legacy IDs (`B1`/`B0`, `C38`, `C39`, `C41`, `B25`,
> `B23`). Leaving it would have sent someone to re-deploy work that landed a week ago —
> which is exactly how this sheet became dangerous rather than merely old.

**Measured 2026-08-22 12:50, not assumed:** `deploy_custom_mods.py` reports **everything in
sync**, 0 pending, 14 files held on purpose (the WreckedMachines v2 park). The companion is
deployed at **`7be4d084`**. ⇒ **Nothing is waiting on this window.**

⛔ **Do not skip the window anyway — re-run the planner before launching.** BUILD may land an
assembly between now and the launch, and an assembly cannot be written while the game runs.

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py            # plan only
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply    # only if the plan is non-empty
```

### The ordering doctrine — still true, and the reason the old manifest was numbered

Keep these whenever a deploy DOES appear; they are what the dead table was really carrying.

- 🔴 **An assembly deploys SOLO.** Every call in §3–§6 is a `jawa/*` call, so a wrong companion
  poisons every result after it. Two new DLLs in one load is a bisection you pay for later.
- 🔴 **A new mod's `ModsConfig.xml` position is part of the deploy**, not a follow-up. A Harmony
  patch mod must sit **after `brrainz.harmony`** or the postfix never binds; a reskin must sit
  **after the mod it reskins** or the labels change and the art does not.
- 🔑 **`ModsConfig.xml` is NOT gated on this window** (§1b). No config file ever waits — owner's
  ruling 2026-08-15. Only assemblies wait, because the OS locks them.
- **Expected-failure signatures land BEFORE launch**, never after — a signature invented after
  reading the log is a story that fits, not evidence. `EXPECTED_FAILURES_next_load.md`.
- **`refresh.py` is NOT a launch gate** (DECIDE, 2026-08-15). The dump is armed at step 0 and
  STARTUP recaptures it, so a dump rebuilt now is superseded ~25 minutes later. It runs in §9.

📌 **The window is not the load.** Steps 2 and 3 only make §5 collectable; nothing here
is finished until the game is up and §5 runs.

### 1a. Arm the def dump — worth doing, and it closes one real gap. ✅ done 13:27.

```bash
echo all > "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/dump_request.txt"
```

**Read at STARTUP only** — armed before launch or not at all. 18.7 s. Do it because this
window deploys three mods, and for the one-way gap below.

⚠️ **The gap is ONE mod and it runs ONE way.** Dump `modCount` 576, live `activeMods`
575; the diff is `regrowth.botr.boilingforest` in the dump and **nothing** missing from
it. So nothing that loads is unseen by `--defs` — but the dump still carries defs from
a mod that no longer loads, and an xpath onto *those* validates **clean** while matching
**nothing** in game. Live instance: `JawaWorld_BiomeMix.xml:140` scores
`RG_BoilingForest`. Re-arming closes it.

🔴 **Two escalations on 2026-08-15 — mine and REP's — were both wrong, both from
reading AGE.** This section briefly claimed the dump was from 2026-08-14 and described
a dead def universe. It was captured **that same day** (`capturedUtc
2026-08-15T15:10:11Z`, mode `all`), with `mandrake.starwarsraces` present and all three
donors gone.
- `defs/` reads `Aug 14 01:20` because the dump **overwrites files in place** — no
  entries created or deleted, so the **directory mtime never moves.** It is not the
  contents' mtime. Any tool that rewrites a fixed set of filenames leaves one behind.
- **The verdict that was right throughout was `refresh.py`'s**, because it keys on the
  **load-set fingerprint**, not the clock — and it named the one real mod.
⇒ **Trust the fingerprint over any timestamp — folder, file or manifest.** Dump
location and freshness are published by the seat that measures them:
`infrastructure/state/observed/LIVE.md`. Read that; do not re-derive it here.

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

⛔ **THE WHOLE MECHANOID SUBJECT IS SHUT — owner 2026-08-15, both halves.** They STAY
(reversing this file's morning text), B25(c) is dead, and there is **no mech art review**
either. `review/mech_register.html` needs no eyes and schedules nothing. Do not re-derive
the cut from the O-v2 line in any other doc.

Standing change when a list edit is next made: **disable
`com.yayo.yayoAni.continued`**. 🔴 **Owner, firsthand, 2026-08-15: Yayo stays out** —
lightsabres are **significantly displaced from where they should be during attack**,
not merely the up-and-behind-on-draft artifact this line used to cite unsourced. The
ruling is the owner's observation, not a `[v2]` deferral.

Then `python.exe src/RimMandrake/Utils/refresh.py` — **Windows** interpreter; WSL's
`python3` fails on the Windows paths with a bare `cannot read ModsConfig`.

### 1c. 🔴 The five deploy traps. Each has cost a load or nearly did.

| trap | what it does |
|---|---|
| **`--apply` bare** | overwrites the game copy from the repo **including a peer's half-finished work**. Always scope it: `deploy_custom_mods.py --mod <name> --apply`. ⚠️ **There is no `--plan` flag** — it is an argparse *error*, and the tool is **dry-run by default**. Eleven docs said `--plan` (fixed 2026-08-15); a seat copying one got a usage error, not a plan, and the dangerous misread is "the dry run did nothing, so I'll just `--apply`" |
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
| **L0b** | Confirm the ideoligion **LOADS**, then check its **16 `AbilityDef`s resolve** | CHECK **C42** | ✅ Offline half DONE (`6c0f307`): `The Salvation.rid` 267 refs, 251 resolve, **zero dangling**, **101 precepts** (not the 82 previously written); `MandrakeJawa.xtp` 36/36. 🔴 **What is left is live-only and cannot be faked offline** — `AbilityDef.json` is one of 79 EMPTY def-type files in the dump, so "absent from the dump" says NOTHING about those 16. It bakes at world creation like the factions. ⇒ Settle before the faction/ideo row is called done |
| L1 | `rimworld/spawn_thing def=SmallThruster x=45 z=131`, then `jawa/inspect_string` on it — read for `WarningThrusterInside`. ⚠️ **`jawa/spawn_thing` DOES NOT EXIST**; the prefix is vanilla `rimworld/`, or `jawa/spawn_batch` for more than one | BUILD | **Cheapest launch gate we own.** Outdoor-required ⇒ the exported hull needs its stern cut back, a whole deck re-lay. Substructure-free-only ⇒ nothing to change. One paused call decides a large piece of rework. Needs `jawa/inspect_string` (§1.0 step 1) |
| L2 | `jawa/spawn_pawn kindDef=Jawa_Tribal_Scavenger` **×6**, then one Geonosian Foundry Hive pawn, then read a Jawa's gear | CHECK **C40** | Three deployed-but-unproven fixes in one spawn pass. **Six armed Jawa** (not civilians) · **a Geonosian that is not a baseliner** (empty `xenotypeChances` looks like a content gap, not a dropped node) · **a Jawa wearing `guy762_Robes_jawa` + `guy762_JawaHood`**. ⛔ The voice half is DEPRECATED (owner, 2026-08-16) — do not unpause to hear a line, do not grade it. 🔴 The gear defs live in a mod we KEPT — their presence in a dump proves nothing; **the pawn wearing them is the only evidence** |
| L3 | Fire ONE Galactic Empire raid and screenshot it — 🔴 **procedure below the table, do not improvise it** | DECIDE | The biggest open design question DECIDE owns: **before we repair the antagonist, someone must see whether it reads as one.** ~5 min. Needs `jawa/set_faction_relation` (§1.0 step 1) if the Empire is not already hostile |
| L4 | Spawn `KotORDroidGood_3C` **twice** — the 2nd must NRE | BUILD | 30 s, any map. The whole causal chain (`isOrganic=false` ⇒ no `Pawn_RelationsTracker` ⇒ HAR NRE on the 2nd same-def pawn) rests on this. **If the 2nd does not throw, the chain is wrong and the item re-opens.** An owner decision is queued behind it |
| L5 | **Architect ▸ Vehicles** — read the five Tier-0 land blueprint labels. Then spawn `AV_OxCart`, `AV_Chariot`, `AV_CoveredCarriage`, `AV_WarChariot`; rotate each north/south/east — ⭐ **and look at the ART while you are there**: `VEHICLE_SPRITE_ARTEFACT_CLEANUP_1` (`922b9207`, `073e5399`) removed 24 floating black specks from the north/south facings and stopped the east trim eating the beasts' tails. **No detached black mark anywhere near an animal**, and on east the dewbacks, rontos and banthas end in a tail rather than a straight vertical cut. ⛔ The Chariot's single dewback is DELIBERATELY still short-tailed — its band cannot hold the full tail without shrinking the animal, and that was decided by looking; **Architect ▸ Props and Decor** for the `VFEPD_*` twins | CHECK **C39** only — ⛔ **C41 is NOT collectable this load** | 🔴 **CORRECTED 2026-08-22 — THE TEXT PASS SHIPPED AND THIS ROW SAID THE OPPOSITE.** `VEHICLE_IDENTITY_TEXT_PASS_1` landed at `88f9fe43`, deployed. This cell used to say the beast names DO NOT EXIST YET and that seeing `Ox cart`/`Chariot` was the expected result — following it now would file today's work as a failure. **Expect, verbatim:** `dewback chariot` · `dewback war chariot` · `ronto wagon` · `bantha cart` · `eopie sled`. ⚠️ Three of those names differ from the ones this row predicted — it guessed `dewback cart`, `bantha dray`, `dewback war cart`. **Read what is on screen, not what was predicted.** `Chariot` · `Ox cart` · `Covered Carriage` · `War chariot` · `Dog Sled` must appear **zero** times. ✅ **And the architect menu is now a REAL second check rather than the only one**: every vehicle is two defs, and the `_Blueprint` half was patched this time — it had been carrying "Dog Sled … over ice and through snow" in the build menu since 2026-08-15. 🔑 **A Vehicle Framework vehicle spawns as a PAWN** — `jawa/list_things` returns nothing at the cell, use `jawa/list_pawns`. 🔴 **The art reaches every def by texPath override whether or not a patch ran** — only the LABEL and the per-def COLOUR are evidence. The **architect menu is still worth reading**, but ⚠️ its old reason is dead: it said the blueprint was "a third def the sled pass never touched", and as of `88f9fe43` every `_Blueprint` IS patched. It is now a second independent confirmation, not the only one. ⛔ Do not check west (auto-mirrored from east) |

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
**which overwrites it.** ⇒ if ~~`OuterRim_GalacticEmpire`~~ **`Empire`** (⛔ the vessel
changed 2026-08-20 — `infrastructure/state/OWNER_DECISIONS.md`) is not hostile, the raid
fires, reports `success:true`, and you photograph **a different antagonist**.
Nothing in the reply flags it.

1. ~~`jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true`~~ ⛔ **DEAD 2026-08-20 — wrong vessel.** Use `jawa/fire_incident incidentDef=RaidEnemy faction=Empire dryRun=true` — **abort on `canFireNow:false`.** ⚠️ `Empire` is hostile only once `GalacticEmpire.xml`'s `permanentEnemy` Add has landed; a `canFireNow:false` here is more likely a deploy miss than an engine problem.
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
`infrastructure/state/TEST_PLAN.md` Part 5.
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

📌 **This `refresh.py` is a RE-run, not the first.** BUILD ran it at 15:51 after the
list edit and it resolved 575/575. Run it again anyway: the armed DefDump recaptures
at startup, so the artefacts stamped at 15:51 describe the stack as it was *before*
this load's dump landed.

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

## 10. 🧪 INHABITED — ⛔ NOT a first run any more. Owner: *"full 578 now, minimal after"*, 2026-08-20

> 🔴 **RENUMBERED AND ITS PREMISE CORRECTED — DECIDE, 2026-08-22.** This was a second `## 9.`,
> which is why cross-references to "§9" were ambiguous. **It is §10.**
>
> ⛔ **`Inhabited` is NOT a first run.** It ran on 2026-08-21/22 and loaded **193 of 294**
> characters, because all 101 CharacterDefs carrying a `<skills>` block were discarded at def
> load. The sequence below says a positive sighting settles the architecture gate — **it cannot,
> while a third of the cast is absent.**
>
> ✅ **The fix has landed** (`c6060ae8`, `b24dde99`) and regenerates byte-identical, so the
> sequence below MAY now be run. 🔑 **But its baseline is valid ONLY if `[Inhabited] ready:`
> reads 294.** If it reads **193**, the fix did not reach the game: **stop, and no number in
> this section counts.**
> ⚠️ **Do not delete this sequence.** The first-run test is still the right test — it was the
> ORDERING that broke. It has to run after the cast fix, not before.

**On THIS load (578).** Reach a quicktest colony, then dev menu → **Inhabited**:
`Create place at current tile` → `Stuff roster (3 pawns)` → `Report roster`.
Write down the three **ThingIDs, names, relations count, hediff count** — that is the
baseline the whole architecture gate is measured against.
⭐ **The positive sighting matters more than a clean log**: a mod that loads and does
nothing logs nothing. If the `Inhabited` category is absent from the dev menu, the DLL did
not load and no other Inhabited result this load means anything.
Three first-run failure signatures are written at §4 of `EXPECTED_FAILURES_next_load.md`.

**AFTER, on minimal.** `ModsConfig.MINIMAL.xml` is now **14** — `mandrake.inhabited` added
last (it patches vanilla and needs Harmony). Ideology and `brrainz.rimbridgeserver` were
already in it, so `Patch_BeggarsFromPool` has a real target and the bridge works.
```
python3 src/RimMandrake/Utils/modlist_swap.py --minimal --apply
```
🔴 **Disarm the dump before that swap** — `rm DefDump/dump_request.txt`. A dump captured on
a 14-mod debug list reports every real mod's defs as *"does not exist in the live game"*.
🔴 **`--restore` before the owner plays.** Leaving his machine on 14 mods is the one
unacceptable outcome.
**Why minimal, in one number:** `ROSTER_SURVIVES_OFFMAP_PROOF_1` needs save → quit → RELOAD,
so it costs **two** loads. ~45 s on minimal against ~50 min on the 578.

---

## 🌱 BIOME FLORA — 24 rosters replaced, DEPLOYED 2026-08-23 03:27, never yet loaded

`BiomeFlora_Ashkarr.xml` (24 `PatchOperationConditional` → `PatchOperationReplace`) is in the
game copy and verified byte-identical to the repo. **Defs parse only at startup**, so nothing
about it is true until the next cold load.

**The lines that decide it, in order:**

1. 🔴 **`BiomeDef` count must still be 80.** An `<li>` inside a `LoadDataFromXmlCustom` field
   discards the WHOLE def silently — that is exactly how 26 BiomeDefs were lost on 2026-08-23.
   This patch uses the dictionary-key form (`<Plant_TreeDrago>0.08</...>`) precisely to avoid
   it, but **the count is the proof, not the intent.** 54 means it happened again.
2. **Zero `Could not resolve cross-reference` naming a plant defName.** All 132 were checked
   against the live dump (68,518 defNames, 578 mods) before deploy, so a hit here means a mod
   changed underneath us, not a typo.
3. **Zero red errors naming `BiomeFlora_Ashkarr`.** ⚠️ A `PatchOperationReplace` that matches
   nothing IS a red error — but each is wrapped in a Conditional on the same xpath, and all 24
   biomes were confirmed to carry a `wildPlants` node, so all 24 should apply.

**Then LOOK, which is the only real verdict.** One map each in `Desert`, `HorrorWastes` and
`AB_MycoticJungle`:

| biome | what proves it | what failure looks like |
|---|---|---|
| `Desert` | drago tree, saguaro, agave, pincushion cactus, hardy grass | the old 21-plant list, incl. thornwood and martyr, which now belong to `PoisonForest` |
| `HorrorWastes` | horrorweb, blood bouquet, tentacular/globular aberration, flesh tree | 🔴 **agave** — that is the shipped roster, so the patch did not apply |
| `AB_MycoticJungle` | agarilux, domecap, stropharia, witches' oyster, devilstrand | anything from another family |

⚠️ **A biome reading BARE is not necessarily a failed patch.** 642 of 669 plants have
`minGrowthTemperature` 0.0 °C and half this planet is below that — the rosters are assigned by
look and lore, and `NORMALIZE_TEMPERATURE_TOLERANCES_1` is what makes them grow. Judge the
patch by the ROSTER the biome holds, not by how much of it has sprouted.

⚠️ **`ExtremeDesert` (0.008) and `Wasteland` (0.0099) have near-zero `plantDensity`** — 4,935
tiles, 22.6% of the planet — and will read bare no matter what roster they carry. That is the
shipped value, deliberately untouched by this pass. See `BARE_BIOMES_NEED_DENSITY_1`.
