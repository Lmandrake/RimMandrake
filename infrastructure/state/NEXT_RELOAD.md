# NEXT_RELOAD.md — the run sheet for the NEXT game load

> 🔴 **OWNER RULING 2026-08-22 10:58 — THE COLD START IS HELD.** Asked what the next load
> is for, he chose: *"Both — hold until the cast fix lands, then one load."*
>
> ⛔ **Do not launch until `CAST_ROSTER_SKILLS_DISCARDED_1` has landed.** The five things
> already deployed and unproven (Flamebow off the kill list, `Flamebow_TagWiden.xml`,
> `JawaIon_FieldOurOwnGun.xml`, and the two assemblies deployed 10:30) are NOT urgent
> enough to buy a load of their own — they ride along with the cast fix. **One load
> answers everything; launching now costs two.**
>
> 🔑 **The reason is the architecture gate, not the deploys.** `ROSTER_SOAK_100_DAYS_1`
> measured against 193 of 294 people produces a baseline that has to be thrown away and
> re-measured, and a re-measure is another ~25 minutes.
>
> ✅ **BUILD owns the cast fix.** The owner confirmed the item stays filed where it is;
> CHECK does not take it.

> 🔴 **STALE — CHECK, 2026-08-22 10:40. This sheet was assembled 2026-08-20 07:35 and A
> WHOLE LOAD HAS HAPPENED SINCE** (the 08-22 08:40 run, 578 mods, rev591, now harvested
> and closed as `NEXT_LOAD_LOG_HARVEST_1`). Do not spend a cold load off it until DECIDE
> reassembles it — filed as `RUN_SHEET_REASSEMBLE_AFTER_LOAD_1`.
>
> **What that load already changed, so §0's brief is answering yesterday's question:**
> - ⛔ **§9's premise is broken.** `Inhabited` is not a "first run" any more — it ran, and
>   it loaded **193 of 294** characters. All 101 that carry a `<skills>` block are
>   discarded at def load (`CAST_ROSTER_SKILLS_DISCARDED_1`). §9 says a positive sighting
>   settles the architecture gate; it cannot, while 34% of the cast is absent. Do the §9
>   sequence only AFTER that item lands, or its baseline is measured against a short cast.
> - ✅ **Two deploys in §0 are already DONE** in the 10:30 game-down window: `Inhabited`
>   (in sync, 18 files) and `bridgetools --gm --apply` (`7df3c51b` → `e3e8a89c`, adding
>   `jawa/faction_name_get`, `faction_name_set`, `faction_create`).
> - ⚠️ **`harvest_log.py` changed under this sheet.** It was counting the load-time
>   patch-file manifest as evidence and reporting `303 / 5252 / 2224` RED against baseline
>   0 for MegafaunaYield, `Jawa_Patches` and `JawaVoice`. All three now read 0 / 0 / 2.
>   **Any number in this sheet quoted from the old tool is suspect.**
> - 🔑 **269 is a dead number.** The cast roster is **294** on disk. Anything here or in an
>   item that verifies against 269 is verifying against a roster the project outgrew.

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


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

## 0. ⏱️ PRE-LOAD BRIEF — 2026-08-20 07:35, assembled by DECIDE on the owner's *"prepare for game load"*

**Measured, not remembered.** ⚠️ **First written 07:35 while the game was still UP and BUILD
was mid-commit in this same tree; RE-MEASURED 07:5x with the game DOWN. Three rows moved and
the corrections are marked — read the right-hand column, not a number you remember.**

| check | reading (game DOWN, 07:5x) | consequence |
|---|---|---|
| RimWorld process | **not in `tasklist`** — the game is down | ⭐ **The deploy window is OPEN RIGHT NOW.** Assemblies are writable |
| deploy planner | 🟢 **"Everything in sync"** — 0 pending, 14 held (WreckedMachines, parked to v2 2026-08-12) | nothing is waiting on the window; it is open and empty |
| `modlist_swap.py --status` | LIVE **578 active**, md5 `deefb393…`, matches **FULL** | 🔴 the ~25-minute cold load, not the 22-second minimal one |
| `ModsConfig.xml` | **578**, mtime **07:37** — rewritten during this session | ⛔ ~~577 / mtime 00:49~~ was my 07:35 reading and is DEAD. `mandrake.inhabited` was enabled in `1254026` |
| 🔴 new assembly riding | **`Inhabited.dll` — 39,936 bytes, md5-identical repo↔game, and THE ENGINE HAS NEVER LOADED IT** | ⛔ ~~"no assemblies riding"~~ was my 07:35 reading and is DEAD. In-sync copies are not the same claim as *has run*. See the §4 correction in `EXPECTED_FAILURES_next_load.md` |
| live def dump | 🔴 **STALE** — `+ mandrake.inhabited` since the dump | ⛔ ~~"CURRENT, do not arm"~~ is DEAD: adding a mod lapses the dump. ✅ **Already armed** — `dump_request.txt` reads `all`. Leave it; **delete it after**, the marker is not consumed |
| offline artefacts | rebuilt — 6 CSVs written to `observed/2026-08-13/inventory` | current |
| previous `Player.log` | copied to `observed/2026-08-20/Player.log.pre-reload` (707 KB) | overwritten at next launch; tonight's evidence is safe |

🔑 **The lesson worth keeping, because it cost this brief its accuracy:** *four seats share
one working tree.* A measurement taken while a peer is committing describes a repo that
stopped existing. **Re-measure immediately before launch, never at the top of the session.**

### 🔴 Verified before launch, because generating on a stub is unrecoverable

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Worldbuilder\TidallyLocked\Preset.xml`
— **PRESENT**, 3,895 bytes, mtime 2026-08-20 00:59, **16 `Jawa_` lines**,
`myLittlePlanetSubcount 7`, `planetCoverage 1`, `saveGenerationParameters True`.
Matches the state recorded at handover in
`worldbuilder-preset-is-wiped-at-every-launch-not-just-on-steam-updates-6b1e4d`.
⚠️ **This is a READ, not a deploy** — that item is BUILD's by the owner's 2026-08-20 ruling
and DECIDE is not touching the file again.
🔴 **On the world-creation page, Configure Planet must read Scale 7 / Coverage 100%. If it
reads Scale 10 the preset lost its parameters — ABORT, do not generate.**

### What this load is FOR, in priority order

1. 🔴 **The 82 ideoligion precepts** — `sequence-the-ideoligion-check-before-the-faction-work-e3f1a7`.
   The largest unmeasured surface on the board, and an ideoligion **bakes at world creation
   and cannot be retrofitted**. ⚠️ **There is no offline route**: `validate_ideoligion.py`
   reads IdeoPresetDef and FactionDef XML and answers *"no religions found"* on a `.rid`.
   **Decision string: none — this one is a DIALOG, not a log line.** Load `The Salvation.rid`
   and read the precept list on screen. PASS = all 82 present by defName. ⚠️ *"71 missing"*
   was CHECK's own scrape bug — the block nests `RitualBehavior` / `RitualOutcomeEffect` /
   `RitualObligationTargetFilter` names, which are not `PreceptDef`s. Do not re-derive it.
2. **The xenotype, live** — `the-shipping-xenotype-drops-four-of-our-own-genes-7e31aa`.
   Fixed on disk 2026-08-15, **never confirmed live.** 🔴 The superseded wrong claim was
   *also* "36/36 references resolve" from an offline check, so **disk evidence cannot close
   this item** — only a spawn.
3. **`seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8`** — on the worldgen clock.
4. Everything already in §2–§6 below.

⛔ **NOT riding this load, and here is why, so nobody re-derives it:** the eight `INHABITED_*`
items filed to BUILD today have **no compiled assembly yet** — `ROSTER_SURVIVES_OFFMAP_PROOF_1`
is a soak that needs a DLL that does not exist. The river and rainfall work is authored into
`world/ASHKARR_WORLDMAP_tiles.csv` and reaches the game over the **bridge**, not through a
load.

### At launch, while it grinds
```
python3 src/RimMandrake/Utils/whats_new.py --seat <SEAT> --mark
```
**Launch, not close** — close is when work lands, so the deltas are not written yet.

### After it
```
python.exe src/RimMandrake/Utils/harvest_log.py
```
You paid for a full load; harvest the WHOLE log, not only what you changed.

---

## 1. 🔻 WHILE THE GAME IS DOWN — the only window for a deploy

Everything in this section is inert or refused while RimWorld runs. If the game is
already up, skip to §2.

### 1.0 🔴 THIS WINDOW — the deploy manifest, in order. Opened 2026-08-15.

**Everything in §5 is uninterpretable until this section is finished** — five of the
six live items are `blocked — needs deploy`, not blocked on a question.

| # | deploy | item | why this order |
|---|---|---|---|
| **0** | `echo all > ".../DefDump/dump_request.txt"` — §1a | — | ✅ **DONE 13:27 CHECK.** Armed for next startup. Right to do — 18.7 s, and it re-reads the stack *after* this window's three deploys. ⚠️ **The urgency I wrote here was FALSE**: the dump is from **today** (`capturedUtc 2026-08-15T15:10:11Z`), not 2026-08-14. See §1a for the folder-mtime trap that caused it |
| 1 | `python.exe src/RimMandrake/bridgetools/build.py --gm --apply` — or `./src/RimMandrake/Utils/shutdown_deploy.sh` | BUILD **B1**, closes **B0** | An **assembly, solo**. Everything in §3–§6 is a `jawa/*` call, so a wrong companion poisons every result after it. 🔴 `--gm` or `fire_incident` + `send_letter` are stripped and §5's L3 cannot fire at all |
| 2 | `deploy_custom_mods.py --mod JawaPlantGrowth` (dry run) then `--apply` | CHECK **C38** | The **second and last assembly**. Deploy it **alone**, not beside #3 — a new DLL in a mixed batch poisons attribution for everything beside it. Then add `mandrake.jawaplantgrowth` to `ModsConfig.xml` **after `brrainz.harmony`** or the Harmony postfix never binds |
| 3 | `deploy_custom_mods.py --mod DesertVehicleReskin` (dry run) then `--apply` | CHECK **C39** only — ⛔ **NOT C41** | Pure XML and loose PNGs — no window needed, but do it now so it rides this load. This is an **update**, the mod is already at `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\DesertVehicleReskin`. 🔴 `mandrake.desertvehiclereskin` must sit **after** `sarg.alphavehiclesneolithic` or the labels change and the art does not. 🔴 **C41 was paired here in error — B62 is UNBUILT** (`ready`, BUILD 2026-08-15; verified on disk: the folder holds 12 PNGs, C41 needs 24, and its 13 extra defs are absent). This deploy carries the eopie sled and nothing else |
| 4 | `ModsConfig.xml` chores in ONE pass | BUILD **B25** | Not gated on this window at all (§1b) — a config file is writable game up or down. Standing changes: disable `com.yayo.yayoAni.continued`, pin the six `loadBottom`+`loadAfter` userRules. ⛔ **NOT mechanoids** — see §1b |
| 5 | Write the three signatures into `EXPECTED_FAILURES` | BUILD **B23** | Must land **before launch** or the load spends attention on errors we already know about |
| 6 | `python.exe src/RimMandrake/Utils/refresh.py` | B25(b) | 🔴 **NOT a launch gate — DECIDE 2026-08-15.** Moved to §9, after the load. The def dump is armed (step 0) and STARTUP recaptures it, so a dump rebuilt now is superseded ~25 min later. Running it pre-launch costs window and buys a fingerprint that dies at the main menu. **Step 5 is the last thing before launch** |

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
| L5 | **Architect ▸ Vehicles** — read the five Tier-0 land blueprint labels. Then spawn `AV_OxCart`, `AV_Chariot`, `AV_CoveredCarriage`, `AV_WarChariot`; rotate each north/south/east; **Architect ▸ Props and Decor** for the `VFEPD_*` twins | CHECK **C39** only — ⛔ **C41 is NOT collectable this load** | 🔴 **B62 IS UNBUILT, so only `eopie sled` can pass.** `dewback cart` · `ronto wagon` · `bantha dray` · `dewback war cart` DO NOT EXIST YET — seeing `Ox cart`/`Chariot`/`Covered carriage`/`War chariot` here is the EXPECTED result, not a failure, and must not be written up as one. Read the four anyway and record them as the pre-B62 baseline. Original wording, valid only AFTER B62 ships: reads verbatim `dewback cart` · `ronto wagon` · `bantha dray` · `dewback war cart` · `eopie sled`; `Chariot`/`Ox cart`/`Dog Sled` appear **zero** times. 🔑 **A Vehicle Framework vehicle spawns as a PAWN** — `jawa/list_things` returns nothing at the cell, use `jawa/list_pawns`. 🔴 **The art reaches every def by texPath override whether or not a patch ran** — only the LABEL and the per-def COLOUR are evidence. The **architect menu is the tell**, because the blueprint is a third def the sled pass never touched. ⛔ Do not check west (auto-mirrored from east) |

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

## 9. 🧪 INHABITED — first run. Owner: *"full 578 now, minimal after"*, 2026-08-20

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
