# LOAD_PROCEDURE.md — what is true on EVERY game load

> 🔑 **The half of the old run sheet that does NOT change per load**, split out of
> `NEXT_RELOAD.md` on 2026-08-23 (`RUN_SHEET_PER_LOAD_BLOCKS_1`). Mixing standing procedure
> with one load's payload is what made that file rot: the payload went stale and nobody would
> delete it, because the procedure around it was still live.
>
> ⭐ **Numbers are ONE sequence across TWO files and are deliberately not renumbered** — other
> docs cite "§5 of NEXT_RELOAD" and "§3–§6". **§1 §2 §3 §7 §8 §9 are here**; **§4 §5 §6 §10 and
> the deployed-and-unproven blocks are in `NEXT_RELOAD.md`.**
>
> ⛔ **Nothing here is about a particular load.** A defName, a queue item ID, a grep string or a
> baseline number belongs in `NEXT_RELOAD.md`, not here.

---
## 1. 🔻 WHILE THE GAME IS DOWN — the only window for a deploy

Everything here is inert or refused while RimWorld runs. If the game is up, skip to §2.

### 1.0 The deploy manifest is empty — but re-run the planner anyway

⛔ **BUILD may land an assembly between now and launch, and an assembly cannot be written
while the game runs.** Never quote a stored sync state; measure it.

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py            # plan only
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply    # only if the plan is non-empty
```

**The ordering doctrine — keep these whenever a deploy DOES appear:**

- 🔴 **An assembly deploys SOLO.** Every call in §3–§6 is a `jawa/*` call, so a wrong
  companion poisons every result after it. Two new DLLs in one load is a bisection you pay
  for later.
- 🔴 **A new mod's `ModsConfig.xml` position is part of the deploy**, not a follow-up. A
  Harmony patch mod must sit **after `brrainz.harmony`** or the postfix never binds; a reskin
  must sit **after the mod it reskins** or the labels change and the art does not.
- 🔑 **`ModsConfig.xml` is NOT gated on this window** (§1b). Only assemblies wait, because the
  OS locks them.
- **Expected-failure signatures land BEFORE launch**, never after — a signature invented after
  reading the log is a story that fits, not evidence. `EXPECTED_FAILURES_next_load.md`.
- **`refresh.py` is NOT a launch gate.** The dump is armed at step 0 and STARTUP recaptures it,
  so a dump rebuilt now is superseded ~25 minutes later. It runs in §9.

📌 **The window is not the load.** Nothing here is finished until the game is up and §5 runs.

### 1a. Arm the def dump — armed before launch or not at all

```bash
echo all > "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/dump_request.txt"
```

**Read at STARTUP only.** ~19 s. 🪤 The marker is **not consumed** — delete it afterwards or
every future load pays again.

⚠️ **A dump can carry defs from a mod that no longer loads**, and an xpath onto those
validates **clean** while matching **nothing** in game. Re-arming closes it.

🔴 **Trust the FINGERPRINT over any timestamp — folder, file or manifest.** The dump
overwrites files in place, so the directory mtime never moves and reads days stale while the
contents are current. `refresh.py` keys on the load-set fingerprint, which is why its verdict
survives when age-based ones do not. Location and freshness are published by the seat that
measures them: `infrastructure/state/observed/LIVE.md`. Read that; do not re-derive it here.

### 1b. `ModsConfig.xml` — BUILD's alone, and NOT gated on this window

🔴 **Owner's ruling, 2026-08-15: nothing blocks on RimSort, or on the game being closed, for a
config file of any kind. Never ask whether RimSort is open.** RimWorld does not rewrite it on
exit. A mod-list change takes effect **only at startup**; editing while the game runs is inert,
not destructive — reading the running game as evidence the edit "failed" is the trap. After an
external edit RimSort's in-memory view is stale, and the whole mitigation is one sentence to
the owner: *"RimSort is open — hit Refresh."*

⛔ **The mechanoid subject is SHUT — owner 2026-08-15, both halves.** They STAY, and there is
no mech art review. Do not re-derive the cut from any other doc.

🔴 **`com.yayo.yayoAni.continued` stays DISABLED — owner, firsthand 2026-08-15:** lightsabres
are significantly displaced from where they should be during attack.

Then `python.exe src/RimMandrake/Utils/refresh.py` — **Windows** interpreter; WSL's `python3`
fails on the Windows paths with a bare `cannot read ModsConfig`.

### 1c. 🔴 The five deploy traps. Each has cost a load or nearly did.

| trap | what it does |
|---|---|
| **`--apply` bare** | overwrites the game copy from the repo **including a peer's half-finished work**. Always scope it: `deploy_custom_mods.py --mod <name> --apply`. ⚠️ **There is no `--plan` flag** — it is an argparse *error*, and the tool is **dry-run by default**. The dangerous misread is "the dry run did nothing, so I'll just `--apply`" |
| **companion built without `--gm`** | silently **strips `jawa/fire_incident` and `jawa/send_letter`** off the game copy. The build refusing by default is the guard working. A low tool count looks identical to a stale build — check which you passed before concluding anything |
| **`strings -a`** | scans 7-bit ASCII, so a method-body literal (UTF-16LE, `#US` heap) reads as **ABSENT**. It proves a tool **name** and nothing about its body. **Use `strings -a -el`** |
| **deploying after launch** | RimWorld reads defs **once, at startup**. A def written after the process started is invisible to it while looking perfectly deployed on disk. Check with `find "<Steam>/Mods" -newermt "<process StartTime>"` before believing any no-show |
| **a new assembly in a mixed batch** | poisons attribution for everything beside it. Deploy an assembly **solo**. ⚠️ The write fails `OSError 22` while the game runs — loaded and locked; the refusal is safe, it cannot truncate |

📐 **If the window gets tight, §1.0's order IS the ranking** — sorted by what the window
destroys, not by severity. A severe bug whose fix is already live is not a claim on a scarce
window.

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
