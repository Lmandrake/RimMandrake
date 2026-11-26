---
name: rimworld-load-round
description: How to spend a RimWorld cold load — and how to stop needing one. A 13-mod minimal list loads in 22 SECONDS against ~15 minutes on the owner's full list, making a full edit-build-deploy-test cycle about a minute; modlist_swap.py does the swap and restore. Covers what that minimal list cannot prove. Arriving already confident instead of "restart and see", writing the Player.log strings that will decide each item before launching, batching by ambiguity, what ModsConfig.xml is and is not authoritative about, src/RimMandrake/Utils/refresh.py and whether a load is needed at all, the shutdown window where companion DLLs deploy, the doctrine delta at launch, and harvesting the whole log. Use before calling or queueing a restart, when the game is about to close or has just launched, after any mod-list change, and whenever you are tempted to say "restart and see".
---

# The load round

A cold load of the owner's full list costs about 15 to 25 minutes as measured (§0). Plan for **15 to 30 minutes**. Full-list testing is retired
until the integration phase (`design/RimMandrake/standing_rulings.md` §Mod development runs on small lists).
So never spend a load on one question. Never spend a load to learn a thing that you can read off disk.

## 0. 🟢 FIRST: does this load have to be expensive at all?

**There are several games; pick the one whose load is cheapest for the work.**

- ArchBig is Steam's install on Archmagi. The owner looks at staged work on ArchBig or ArchSmall.
- ArchSmall is its own install on Archmagi. ArchSmall has its own `ModsConfig.xml`, `Mods` and Saves.
- `RM_GAME_INSTANCE=b` points `game_paths`, `modlist_swap.py` and the deploy at ArchSmall.
- `python3 src/RimMandrake/Utils/game_instance.py launch ArchSmall --wait` starts ArchSmall.
- A tier list on ArchSmall loads beside a running ArchBig. A tier is a named small mod list of `modset_builder.py`.
- His full list on ArchSmall beside ArchBig does not fit in Archmagi's memory.
- No check needs ArchBig rather than another game: full-list testing is retired until the integration phase
  (`design/RimMandrake/standing_rulings.md` §Mod development runs on small lists). Work that finds ArchBig busy goes to ArchSmall.

**The load times, each with its date:**

| list | cold load | measured |
|---|---|---|
| a 13-mod MINIMAL list | **22 SECONDS** | 2026-08-19 |
| the full list | ~25 minutes | 2026-08-19 |
| the full list, second launch of a session | ~15 minutes | 2026-09-07 |
| the full list, five loads | 18.5-21 min | 2026-10-03 (`src/RimMandrake/Utils/load_policy.json`) |
| the full list | ~14.5 min | 2026-11-21 (`src/RimMandrake/Utils/game_instance.py`) |
| `ModsConfig.MINIMAL.xml` as it is now | UNMEASURED | none |

- The engine's own clock agrees with the 22 seconds:
  `[RimBridge] STARTUP_TIMING phase=bridge-start.total elapsedMs=12364`.
- A quicktest world on top costs **5 s**.
- ⇒ **The whole edit → build → deploy → launch → test cycle is about ONE MINUTE.**
- The rules below about a scarce load still apply to the owner's full list. For *tool and mechanism* work, a load is not
  scarce.
- Do not spend a full-list load to prove a thing that a 22-second load can prove.
- The full list held 576 mods on 2026-08-20. Read `ModsConfig.FULL.LATEST.xml` for the size, never a number in a doc.

⛔ **An XML-only change is proven by a MINIMAL-LIST RESTART, not by hot-reload (owner's ruling 2026-09-03).**

- Deploy. Restart on the minimal list (22 s). Read the def back with `jawa/get_defs`.
- **`jawa/hot_reload_defs` is retired as unstable.** The call hung a 589-mod game for 5 minutes. After that, the game
  could not generate any pawn, and every health flag still read green.
- ⚠️ The call also had a clean pass on a minimal list (0.04 s, 2026-09-02). The pass was real. The pass is *why* the
  call is retired, not gated. The call works on 19 mods and destroys pawn generation on 589 mods. So a seat cannot
  trust the call when the seat itself decides which case it is in.
- The main entry is `skills/rimworld-modding/SKILL.md` §2. The evidence is
  `infrastructure/state/items/closed/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`.
- Do not count `jawa/hot_reload_defs` as a speed path in an estimate of test time.

A **proof** (a `live-proof` command) never swaps the list or restarts the game itself:

- The `live-proof` runner refuses `modlist_swap`, `modcheck run` and `deploy … --apply`.
- A proof declares the smallest tier that holds its mod (`live-tier: <tier>`). testq runs the proof on that list.
- The rules are in `skills/live-debugging-proof-harness/references/lightspeed-authoring.md` §2, §6.

```
python3 src/RimMandrake/Utils/modlist_swap.py --status
python3 src/RimMandrake/Utils/modlist_swap.py --minimal   # or --restore (separate runs; mutually exclusive); add --apply
```

- `modlist_swap.py` only plans by default. With `--apply`, it archives the live file before each write.
- `modlist_swap.py --restore` writes FULL.LATEST. The owner's real list is frozen at
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`.
- After a `modset_builder.py --tier X --apply` swap, `modset_builder.py --restore` puts back the before-copy of that swap.
  The tool verifies that copy by md5, and refuses if there is none. `modset_builder.py --restore-full` writes FULL.LATEST.
- Never mix the two families: undo a swap with the tool that made the swap.

**The 13 of 2026-08-19, and why each one was there:** harmony · core + all five expansions · VEF (Alpha Biomes' hard
dependency) · `brrainz.rimbridgeserver` · alienworlds + tidallylocked · alphabiomes · mylittleplanet. The file holds more
mods now (§ What the minimal list CANNOT do).

- 🔴 **Odyssey is NOT optional.** `Tile.Landmark` returns null without `OdysseyActive`, and PlanetLayer/Orbit are Odyssey
  types. A list without Odyssey has no landmarks, and nothing reports that.
- **`brrainz.rimbridgeserver` is not optional.** Without it there is no bridge at all, however you deploy the
  companion DLL.

### Automated sweeps across many mod-list batches: `loadsweep/`

`src/RimMandrake/Utils/loadsweep/` (`gen_config.py` + `sweep_load.sh`) is a repo tool. The tool does the whole cycle for
you: write the config, restart through Steam, poll, and grep the verdicts.

- One cycle takes ~60 s on a small list. `gen_config.py` has its own base list of 9 mods. Your batch file of extra
  packageIds goes on top.
- The tool launches, waits and prints the standing failure counts: `config_errors`, `crossref_errors`, `patch_failed`,
  `typeload`, `recovery_hits`. You do not watch the load.
- `sweep_load.sh` stops and starts ArchBig only. The script refuses a shell that means ArchSmall.

⚠️ **Poll `"Bridge token:"` in `Player.log`, not the JawaBench ready line.**

- `Bridge token:` is written at bridge start. `Bridge token:` is the correct ready signal on ArchBig.
- ArchSmall writes a port line (`GABP server connected to GABS on port`) and no token line. `logwait.py` takes both.
- The JawaBench "ready" line is not a ready signal. Before 2026-10-10 that line appeared only on the FIRST tool call, so a
  wait for it could hang a sweep forever. The absence of that line is UNMEASURED. The absence never proves
  that the deploy did not take (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchInit.cs`). This command settles
  it: `python.exe src/RimMandrake/Utils/rimbridge_client.py --list-tools`.
- `sweep_load.sh` also watches for `"Recovered from incompatible or corrupted mods"`. That text ends the wait as a failure.
- After a relaunch, a hand-written grep first matches the token of the PREVIOUS session. The old text stays until the
  new process truncates `Player.log`. So also require a shrunk size, a small line count or a newer mtime
  (`skills/rimbridge/references/traps/lifecycle.md`, "`Player.log` PERSISTS between runs").
- **Don't hand-write that wait:** `python3 src/RimMandrake/Utils/logwait.py "Bridge token:" --timeout 900` counts only
  text written after the call. `logwait.py` needs no blind-scan override. In code, open `logwait.LogCursor()` BEFORE the
  launch.
- `src/RimMandrake/bridgetools/launch_ready.py` launches once, waits and reports READY only with a receipt of this process.
  Hold the bridge before you run it: it first kills a running copy of the same game.
- One command does the whole cycle (stop, tier, deploy, launch, wait, quicktest, run):
  `src/RimMandrake/Utils/northstar_driver/live_session.py`.

⚠️ **A load stuck at 6 active mods (Core + five expansions) is RimWorld's own corrupted-mods RECOVERY RESET, not a failure
of your config write.**

- Check the log for `"Resetting mods config and trying again"`.
- **The reset persists to disk:** `ModsConfig.xml` now holds 6 mods.
- So write your batch again before you relaunch. The same launch again only repeats the reset.

🟢 **Rapid QA win: sweep the ConfigError lines on every minimal/tier load, not just a full one.**

- `Def.ConfigErrors()` runs after every patch and inheritance resolve. The method catches real bugs that the offline
  `validate_patch.py` cannot see.
- Measured catches: dead pawnkinds with no race (`RaceProperties` unresolved), a bad `forcedMiss`, and thought stages out
  of `minSeverity` order. All came in ~2 s on a live load.
- `sweep_load.sh` already greps `^Config error in`. On a full load, `harvest_log.py --show configerror` (§8) reads the
  same class of line.
- A config error means that the def loaded and the ENGINE disapproves. The def is not necessarily wrong for our purposes.
  Before you file a finding of this sweep, run `src/RimMandrake/Utils/check_config_errors.py`. That tool classifies every line. The
  note of `harvest_log.py` at its `configerror` check (a run without `--show`) gives the baseline.

### Which list to test on (owner rulings)

- **Small mod lists are the way to test until one final verification pass on the whole list** (owner, 2026-11-02): *"small mod lists should always be the way to test until a final verification pass on the whole huge mod list."*
- **Huge Things belongs on the testing mod lists** (owner, 2026-10-16): *"We also need to include the huge things mod in our testing mods too. We have so many huge things, we want to make sure we're always compatible with them."*

### ⚠️ What the minimal list CANNOT do

* **The minimal list cannot reproduce the 21,872-tile geometry.** `ferny.Worldbuilder` is absent, and Worldbuilder loads the
  TidallyLocked preset. A quicktest comes out 119,904 tiles. So a check of real tile IDs needs the full list.
* **The minimal list does not have most content mods.** A patch against an absent content mod (RimStarWars/Utinni/Mandrake)
  matches nothing and logs nothing. So a PASS on minimal is UNMEASURED for that patch. Such an item needs a
  dependency-complete tier (`modset_builder.py --tier`).
  - Measured: a 21,872-row import validated at 81.6% on the minimal list. **Every** mismatch was one of 8 biome defs that
    the 13-mod list lacks. The tool had no defect.
* 🔴 **While the minimal list is installed, the live `ModsConfig.xml` is NOT evidence about the owner's full list.** Read
  `ModsConfig.FULL.LATEST.xml` instead. A research thread read the live file and reported Gravship Exporter inactive. The
  mod was active in the real list of 578.
* **No restore step** (owner, 2026-10-24): *"Never worry about my mod list restoration! … Until I start
  playing (months from now likely) you never need to "restore" mods to anything."* Leave the list on
  the tier that serves the work. The warning of `--status` while the minimal list is live is only information.
* **The minimal list is a file, not a number, and it grows; the owner's full list drifts too.**
  - `modlist_swap.MINIMAL` is the path `infrastructure/state/modlists/ModsConfig.MINIMAL.xml`. Count its `activeMods` with a
    parser, never from this page.
  - The file held 13 mods at the 22 s load of §0, and 27 on 2026-11-07. `modset_builder` tiers add 1-18 over it. The
    `acc_2026*` tiers are 31-46. Count them: whether that is added mods or a total is UNMEASURED.
  - Never quote a remembered total of the full list (578 drifting to ~593 in 2026-08; 315 on 2026-11-23). Print the total
    from `activeMods` in `ModsConfig.xml` at that moment.
* The list holds Ideology, `brrainz.rimbridgeserver` and `mandrake.rm.inhabited`. So the beggars
  Harmony patch of Inhabited (`src/RimMandrake/Inhabited/Source/Patch_BeggarsFromPool.cs`) has a real target, and the bridge
  works.
* A save, quit, reload soak costs TWO loads: ~45 s on minimal against ~30 min on the full list. That saving is the whole
  reason for small lists.
* Disarm the def dump (§5) before you swap to minimal. A dump from a debug list makes every real mod's def read as "does
  not exist in the live game".

More traps for this section: [references/traps.md](references/traps.md) § ⚠️ What the minimal list CANNOT do.

More traps for this section: [references/traps.md](references/traps.md) § 0. 🟢 FIRST: does this load have to be expensive at all?.

## 1. Never "restart and see"

**Arrive already confident.** A restart *confirms* a prediction. Do not use a restart to form one.

- Defs, `About.xml`, `ModsConfig.xml`, the workshop tree and the live def dump are ordinary files. Read the files first.
  The files beat the screen of a mod manager, and the files beat a launch.
- If the question truly needs the running game, put it in your queue for the next load. Do not launch for that question
  alone.

🔴 **The same discipline runs the other way for an intermittent bug: a load that already succeeded before you looked does
NOT prove that a reproducible stall is fixed.**

- `COLD_LOAD_STATIC_CTOR_STALL_1` was closed on exactly that evidence. Then someone caused a FRESH restart on purpose. The
  identical stall came back a 4th time: the same checkpoint, with the CPU still busy and no progress.
- An intermittent bug needs a restart that YOU cause, not a working state that you found.

More traps for this section: [references/traps.md](references/traps.md) § 1. Never "restart and see".

## 2. Write the decision strings BEFORE launching

A decision string is the exact `Player.log` string or count that settles one item. For **every** item on the load, write
these three things before the launch:

- the decision string;
- its baseline (the count that you expect with no change);
- what each outcome means.

You cannot verify an item with no named string. Such an item is only a hope.

⚠️ **Absence of a line is necessary, not sufficient.** A no-op patch logs nothing. So "zero hits" and "it worked" are
different claims. An item that succeeds in silence also needs an **expected-present** string, or a sighting on the screen.

## 3. Batch by ambiguity, not by count

A load buys **attribution**: you learn which change caused which result. Batch each change that cannot steal another item's
blame. Isolate each change that can.

| change | rides along? |
|---|---|
| config: load order, mod settings, un/subscribes | **free** — no attribution risk |
| a validated XML patch with named log strings | **yes** |
| a new C# assembly · a broad-patching mod | **solo** (one exception: the three-assembly waiver below) |

Twenty config changes in one load is fine. Two assemblies in one load is a bisection that you pay for later.

🔴 **The owner's three-assembly waiver STANDS — "batch it" — on one mandatory condition: write the three expected-failure
signatures down BEFORE launching.**

- A signature is the log text that shows which assembly failed, and how.
- The batch is safe only because the assemblies fail in *distinguishable* places. So write the differences down before the
  log exists.
- **A signature invented after reading the log is not evidence, it is a story that fits.**
- Write one signature per assembly in `infrastructure/state/EXPECTED_FAILURES_next_load.md`, before the game starts.
- Do not re-litigate the waiver. Do not quietly split the load out of caution.

## 4. Mod-list state on disk: what is authoritative, when

⚠️ **While RimWorld is running, disk state is NOT authoritative.** The game holds its list in memory. Steam does not remove
a folder that the game holds open. So a listed mod can be unsubscribed already, and a present folder proves nothing.

🔴 **RimWorld does NOT rewrite `ModsConfig.xml` on exit.** RimWorld writes the file when the list changes **in-game**, when
a failed load causes the recovery reset (§0), and in four start cases (`skills/rimworld-start-prep/SKILL.md` §3).

- **Before you reason about the list or the order at all, read `skills/rimworld-start-prep/SKILL.md`.** Three programs that
  do not coordinate (RimWorld, RimSort, Steam) write different parts of this state. That skill names the parts.

⚠️ **"Safe after a clean exit" is CONDITIONAL.** After a clean exit, `ModsConfig.xml` says **what the game loaded**, unless someone
edited the file during the session. The file never says **what is on disk now**. An unsubscribe in Steam or RimSort does not reach the game, and the exit writes
nothing. **So check the entry, the folder, and the mtime:**

```bash
# ArchBig's paths. ArchSmall has its own (§0).
CFG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml"
WORKSHOP="/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
# activeMods ONLY. `grep -c "<li>"` counts LINES (6 when the ids share one line, mods + 5 when each has its own);
# `grep -o "<li>" | wc -l` returns activeMods + the 5 knownExpansions. Parse it.
# Never quote a remembered total — print it, and quote the command with it.
python3 -c "import sys,xml.etree.ElementTree as ET;print(len(ET.parse(sys.argv[1]).getroot().find('activeMods')))" "$CFG"
ls -d "$WORKSHOP/<id>"     # what exists
stat -c %y "$CFG"          # was it rewritten at all?
```

**The mtime is the tell.** If the mtime is before the session, the game wrote nothing. The list still describes the
*previous* state.

**Never assert "your removal didn't land" while the game is up.** First ask if the game runs, or compare the mtime of
`Player.log` with the mtime of `ModsConfig.xml`. Then say what each timestamp implies.

🔴 **No config file waits for anything. Owner's ruling, 2026-08-15:** *"You NEVER
have to ask if RimSort is open. It does not autosave, and I will never save without
asking. Nobody blocks on RimSort or game close for config files of any kind."*

- You may write `ModsConfig.xml`, load order and user rules at any moment: game up or down, RimSort open or shut. **Never
  ask, never hold an item for a window.**
- Two guards of `modset_builder.py` still stand. The tool refuses `--apply`, `--restore` and `--restore-full` while its game
  runs. Then stop that game (§10), or use ArchSmall (`RM_GAME_INSTANCE=b`). The tool also refuses a seat that does not hold
  the bridge of that game. Then take that bridge. Do not ask the owner. `modlist_swap.py` has neither guard.
- The down-window (§6) exists only for **assemblies**. The OS locks an assembly while the game runs. That lock is a file
  lock, not a policy.
- Two hazards remain. An in-game list change writes over your edit. And after you edit the file, the view in RimSort is
  stale. So say "RimSort is open — hit Refresh".

More traps for this section: [references/traps.md](references/traps.md) § 4. Mod-list state on disk: what is authoritative, when.

## 5. Do I need a load at all? `src/RimMandrake/Utils/refresh.py` answers exactly that

Every generated artefact is a snapshot of ONE mod set, load order included. When you add a mod, the artefacts do not break.
The artefacts quietly describe a game that no longer exists.

```bash
python3 src/RimMandrake/Utils/refresh.py             # changes nothing; prints what is stale and its cost
python3 src/RimMandrake/Utils/refresh.py --offline   # rebuild everything not needing a load (seconds)
python3 src/RimMandrake/Utils/refresh.py --all       # offline + patches, in the right order
```

Dependency order: `ModsConfig.xml` → offline scan (**seconds**) → **live dump (a full load)** → generated patches,
`validate_patch.py --live`, `def_diff.py` (seconds each, but all need a *current* dump).

- Only the dump is expensive, and everything after the dump depends on it.
- `refresh.py` **refuses** to regenerate patches against a stale dump. That refusal is the point.
- The `official` dump is frozen and never needs a load to refresh it (`infrastructure/GAME_STATE_WORKFLOW.md`
  §Dumps: which one is canon). `refresh.py` prints `FROZEN` for it.

**Take a dump on a load that you already pay for.** Arm the dump with the marker file below. Then reach the **main menu**.
The dump writes at startup and needs no colony.

```bash
echo all > "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/dump_request.txt"
```

- Watch for `[RimDefDump]` in the log. A dump takes ~27 s and ~1.2 GB.
- **The marker is not consumed.** Delete the marker afterwards, or every load pays for a dump again.

⚠️ **Never capture a dump during a debug configuration** (mods pulled to isolate a bug).

- That dump is stale the instant the mods return. `validate_patch.py --live` then reports the defs of the pulled mods as
  *"does not exist in the live game"*. The result is a wall of confident false errors.
- Offline artefacts are cheap and correct themselves. Rebuild those freely with `--offline --note "<why>"`.

## 5a. ⏳ Delete throw-away saves WHILE THE GAME RUNS — expires when the campaign starts

**Owner's ruling, 2026-08-14.** A deletion of savegames with the game DOWN does not stick. Steam Cloud reconciles at the
next launch and restores the saves. Measured: 26 `.rws`, 701 MB, came back with their **original mtimes**.

> **The window where a deletion survives is while the game is RUNNING.**

- This rule covers throw-away debugging worlds only. The rule never covers a canonical save
  (`infrastructure/state/CANONICAL_SAVE.md`) or a save that holds options for his review (root `CLAUDE.md`).
- When you throw a debugging world away, delete the saves **and** the screenshots **after the game is live**, not after the
  game exits.
- **Do not disable Steam Cloud.** A disabled Steam Cloud is no longer the fix, and nobody asked for it.
- **A text that says "needs Steam Cloud disabled first" about a second deletion is wrong.** The deletion needs the game
  *running*.

🔴 **A post-`rm` count is NOT verification. Say "deleted, UNVERIFIED".** `Saves/` also read empty last time, and Cloud
restored all 26 at the next launch. **The only meaningful check is a count taken AFTER the game next starts.** Until then,
the ledger says *deleted, unverified*, never *gone*.

⚠️ **And check the delete actually deleted.** A compound `rm` with an unmatched glob removes **nothing** under zsh. The
zsh option `nomatch` aborts the whole command. So `rm -f a/*.rws b/*.bak c/*.png` with no `.bak` present deletes zero
files. The command prints one warning that is easy to miss. **Use `find … -delete`, or print before/after counts.** Measured
2026-08-14: this nearly produced a false report of "deleted 734 MB".

🔴 **This rule has an EXPIRY, and the expiry is part of it: it GOES the day the real campaign starts.** A standing habit to
"delete the saves" would destroy a live campaign. A rule that outlives its reason makes exactly that happen.

## 6. The shutdown window — announce it before the game closes

**A deployed assembly cannot be written while RimWorld runs.** The game holds the file memory-mapped. Windows refuses the
copy with `OSError: [WinError 1224] The
requested operation cannot be performed on a file with a user-mapped section open`.
So "takes effect next restart" is false for an assembly. You cannot write the file at all.

- So an assembly change waits for a **shutdown**, not a startup. You deploy the assembly between the close of the game and
  the next launch. ArchBig and ArchSmall each have
  their own `Mods` and `BridgeTools`. So a running ArchBig does not lock the files of ArchSmall.

> **Whoever calls a shutdown checks for waiting assemblies BEFORE the game closes.** Miss the window and the work waits a
> full cycle.

- The announcement is one command. When the game is down, run `./game --why "<your reason>" down`. The command writes the
  state in the ledger and messages no window. Other windows read the state with `rimflow next`. Say so in your reply afterwards. The CHECK seat, which this rule once told, is retired.
- So look for the waiting assemblies yourself: `rimflow` items with `needs: deploy`, and the plan-only run of
  `deploy_custom_mods.py --mod <name>` for each mod. A companion DLL has its own plan-only run
  (`skills/rimbridge-companion/SKILL.md`).
- In the middle of a session, "the repo artifact is ahead of the deployed copy" is the normal state. Do not treat that state
  as drift.

**The same gap is the only time the previous `Player.log` exists** under that name. The next launch replaces the file, and
only one old generation stays (`Player-prev.log` for ArchBig, `.prev` for ArchSmall). **Copy it out before you launch**, or
you can lose the evidence of everything you just did. `launch_ready.py` moves the old log to an archive for you.

## 7. At launch: take the doctrine delta

A seat reads doctrine once, at session start. Then peers add traps and file items for that seat, and the seat never learns.
The forced idle time of a load is when a sync is free.

```bash
python3 src/RimMandrake/Utils/whats_new.py --seat <SEAT> --mark   # your delta, then record HEAD
python3 src/RimMandrake/Utils/whats_new.py --all                  # every seat's staleness
```

**Launch, not close.** Work *lands* at close, so at close the deltas are not written yet.

## 8. After the load: harvest the WHOLE log

**You paid for a full load. Do not check only what you changed.**

```bash
python.exe src/RimMandrake/Utils/harvest_log.py                  # every standing check, with baselines
python.exe src/RimMandrake/Utils/harvest_log.py --show crossref  # read the actual lines
```

- The exit codes below are for a run without `--show`.
- Exit code 1 means that a check is above baseline, or that an expected line is missing. A missing log file and a wrong
  argument value also exit 1.
- Exit code 2 means that the tool refused to read the log: a different run, an unfinished load, or a `ModsConfig.xml` that is
  newer than the log. Wait for an unfinished load. A refusal is not a pass.
  If the game is at the main menu and you armed no dump, an old dump manifest can cause the refusal. Then run the tool again
  with `--stale-ok`, and say so when you quote the result.
- Exit code 0 means only that no listed check is above baseline. A no-op patch logs nothing.
- Triage by consequence, not by position or volume: dead mods first, then discarded defs, then unresolved cross-references,
  then stale Scribe references, then patch no-ops.

🔴 **`Reached max messages limit. Stopping logging to avoid spam.` makes `Player.log` stop dead mid-session.**

- The log then looks frozen (stale mtime, no new lines). Every later diagnosis is blind without a restart.
- The limit is itself a FINDING, not only a nuisance: something spams the log.
- One instance was thousands of `Tried to set terrain at (x, 0, z) to null.` lines in contiguous horizontal bands. The
  bands were the river channel itself, drawn with a null terrain.
- **Read the spam, do not just notice the cap.**

⚠️ **The mod count of a crash log comes from its own `Initializing new game with mods:` line, never from the list that you
BELIEVE was active.** A "full-list mapgen crash" was in fact a 19-mod tier. The wrong premise reached the owner as a
question (2026-09-21).

**Whoever needs the restart calls it, harvests the log, and writes up for everyone**, not only its own concerns.

- File each finding in the one list (`rimflow file`).
- File each surprise as a lesson (`python3 src/RimMandrake/Utils/lessons.py add "…"`).

More traps for this section: [references/traps.md](references/traps.md) § 8. After the load: harvest the WHOLE log.

## 9. Before you launch

Check each of these:

- You wrote the decision strings with their baselines (§2).
- Nothing in the batch makes another item unattributable (§3).
- You ran `refresh.py` (§5).
- You handled everything that needs the shutdown window (§6).
- You copied the old `Player.log` out (§6).
- Everything is **deployed**, not merely written (`skills/rimworld-deploy/SKILL.md`).
- With the game down, `python3 src/RimMandrake/Utils/preflight_bridge.py` says GREEN for the list that you will load
  (`infrastructure/GAME_STATE_WORKFLOW.md` §A REBOOT IS YOURS TO CALL). Put the
  list in place first. Pass `--seat <your seat>` and `--deep` (it lets the def lint run), and one of these:
  - the full list: `--tier full`;
  - the minimal list: `--tier minimal`;
  - a tier: `--tier quicktest --modset <tier>`.

⭐ **A pre-flight census, offline, would catch a whole class of crash in seconds before you spend the restart.** Do the
census before every cold load:

- Extract every type token of our namespaces from the XML of the ACTIVE deployed mods. Test each token against the bytes of
  all deployed DLLs.
- Byte-diff the repo `Assemblies/*.dll` against the deployed copies. One pass found that 6 of 65 differed.

🔴 **The load-abort string is not only `"Recovered from incompatible or
corrupted mods errors"`.** `"Caught exception while loading play data"` is also a dead load. A watcher that greps only the
first string reports an aborted load as "still loading" (2026-09-08).

More traps for this section: [references/traps.md](references/traps.md) § 9. Before you launch.

## 10. 🔴 Launch through Steam, never the bare `.exe` — bypassing it intermittently corrupts assembly loading

**Launch with the tool: `python3 src/RimMandrake/Utils/game_instance.py launch ArchBig --wait` (or `ArchSmall`).** The same
rule binds a relaunch, and a restart that a driver starts for a def or content change.

- For ArchBig, the tool asks Steam (`steam://rungameid/294100`). Steam can refuse, or stay silent, while another game
  runs. Then the tool starts the exe itself, as Steam does.
- For ArchSmall, the tool always starts the exe of that install. Each launch needs Steam running. A direct start
  also needs a `steam_appid.txt` in the game folder. The tool refuses a launch that lacks what it needs.
- If the game is up already, `launch` says "already running" and exits 0. That exit does not prove a fresh load. Stop the game
  first.
- **Never start `RimWorldWin64.exe` by hand**, although that route looks more direct and more reliable. The one direct start
  with a private folder is in the traps file below.
- Stop a game with `python3 src/RimMandrake/Utils/game_instance.py stop`. The tool stops by process id, and refuses while
  another holder has the bridge. Name the game:
  `--instance a` is ArchBig, `--instance b` is ArchSmall. Add `--force` if the game stays up.
  `Stop-Process -Force` on `RimWorldWin64` stops every game on the machine.

**What was measured (2026-08-30):**

- A launch through Steam loaded a 19-mod list cleanly: bridge up, 301 companion tools, all content.
- Then a bare start of the exe gave **"Recovered from incompatible or corrupted mods errors"**, **three times in a row**,
  with the same mod list and the same mod DLLs. RimWorld reset `ModsConfig.xml` to Core-only (6 mods) each time.
- The exception was a failure to resolve the `0Harmony` assembly version. The problem was not in content or defs.
- Two changed content files were put back, and the bare start **crashed the same**. So the content was not the cause.
- **Fix, confirmed:** a launch through Steam loaded cleanly at the first try.
- The one known difference between the launches was Steam. The text of that day gave this cause: a bare start skips what
  Steam does to mount and validate Workshop content (`steamapps/workshop/content/294100/*`). So the game can load a stale
  copy of a Workshop mod's bundled `0Harmony.dll`. No later run measured that cause.
- The full incident is in [references/history.md](references/history.md).

More traps for this section: [references/traps.md](references/traps.md) § 10. 🔴 Launch through Steam, never the bare `.exe` — bypassing it intermittently corrupts assembly loading.

## An idle main menu is not a load hang

More traps for this section: [references/traps.md](references/traps.md) § An idle main menu is not a load hang.
