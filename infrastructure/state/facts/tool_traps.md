# Tools with surprising side effects — RimMandrake

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

## Machine and research facts

- 🔴 **RimSage answers on the Windows Desktop ONLY — on the Mac laptop it has never
  connected** (MEASURED 2026-09-16: five timed-out session logs 2026-09-02→09-16,
  `mcp.rimsage.com` TCP-dead while general egress is fine, no `mcp__rimsage__*` tool in
  the toolset at all, no cached decompiled tree). So on the laptop an **engine-internals
  question is UNMEASURABLE** — say so rather than reasoning from a doc, and never brief a
  subagent to "use RimSage" there: it costs a whole run to rediscover. Still fine offline
  on either machine: the def dump (`measure`, `refresh.py`) for DEFS, and reading our own
  source. ⚠️ **Several docs assert engine facts that trace to an earlier agent's prose,
  not a decompiler** — `About.xml`'s "vanilla ignition already works on any flammable
  terrain", and `Flood.noPossibleCell` being private with no accessor. Do not launder
  those into measurements.
- ✅ **CANON research DOES work from the Mac, and directly.** Wookieepedia's
  `action=parse&page=<X>&format=json&prop=wikitext` API answers unauthenticated over plain
  `curl` with **no size cap** (MEASURED 2026-09-23: 13 dianoga pages pulled clean). ⇒ Prefer it
  over Fetcher, which **silently TRUNCATES AT 50,000 chars** and has eaten a species' whole
  Biology section. Resolve titles with `action=query&list=search&srsearch=<name>` — a guessed
  exact page title returns MISSING for real subjects constantly, which is not evidence a subject
  is non-canon. ⚠️ `timeout` does not exist on macOS and its failure **resets the shell's cwd**;
  use `curl --max-time`.
- 🔴 **The SteveDesktop runner's Python has no third-party packages unless someone installed
  them** — a proof row that imports one fails there as a FAIL that is a machine fact, not a mod
  defect (MEASURED in the findings fold: `No module named 'PIL'` on four FlowWorks diptych rows,
  job J20261026T004751Z-6e5292; `No module named 'lxml'` on Cuisine
  `rotting_bed_grows_marsh_fungus/offline_patch_shape`, 2026-11-06). Before judging such a row,
  read the import: a `ModuleNotFoundError` row is a runner-environment finding (Operations), and
  a validation script should import optional packages inside the row and report UNMEASURED, never
  FAIL, when they are absent.
- 🔴 **If a driver reads UNMEASURED 'no result at the current mod hash' although it ran and its rows PASS, compute `mod_hash` twice with the same interpreter that stamped it.** On one Windows desktop `python.exe` gave a different hash on every run with identical file bytes: logical CPU 18 returned wrong SIMD hash results (pinned with `start /affinity`, sha256 gave 60 different digests out of 60; md5 and crc32 stay stable and hide it). Probe by hashing the same buffer N times, pinned per core, not by rereading files.

## Tools with surprising side effects
- 🔴 **When a new game or world won't start, read the FIRST exception in `Player.log`, not the
  loudest.** `rimworld/start_debug_game_ready` and `load_game_ready` both work (VERIFIED on the
  full mod list, 2026-09-27). They were "broken on any mod list" for a while, but every
  visible symptom was a cascade from one of three bugs in our own content, and none was in the
  engine. (1) A `BiomeWorker.GetScore` called `SurfaceTile.Rivers`, which NREs because the
  biome isn't assigned yet during `WorldGenStep_Terrain`. Terrain gen died on tile 0, and the
  loud `WorldPathGrid`/`WorldGrid.get_Item` out-of-range spam came after it. Read the raw
  `potentialRivers` instead. (2) A drug (non-`None` `drugCategory`) with no
  `CompProperties_Drug` NREs `DrugPolicy.InitializeIfNeeded` inside `Game`'s constructor.
  `DrugBase` does not supply that comp. (3) A creature ThingDef naming a type from an
  inactive mod gets discarded, and the raceless PawnKindDef it leaves behind kills
  `GeneticRim.Core`'s cctor, which stops starting-pawn generation
  (`DEBUG_GAME_READY_WORLDUI_CRASH_1`). Harness: `src/RimMandrake/bridgetools/prove_quicktest_world.py`.
- 🔴 **A `PreToolUse` hook added to `.claude/settings.json` mid-session does not fire** — not for this window's Bash calls and not for its subagents' — until a new session starts; a hook already present at session start does fire for subagents. Test a new hook in a fresh window, never by exercising it in the one that added it.

- 🔴 **What outlives a dead parent (MEASURED 2026-11-01, real `claude_bounded` runs; `D:\ClaudeWork\rimmandrake\helpers_dead_parent\probe`).**
  SIGTERM (goodbye, ticket restart, backstop): background Bash and a subagent's running Bash die with exit 137, no report.
  SIGKILL (crash, kill fallback): the LLM loops die, but both Bash commands run on as orphans, finish, and nobody reads
  them. `/clear`: the only route that lost helpers in 7 days, and it has no restart record. Reboot or WSL restart: all of
  it, `setsid` included. Only `setsid`/`systemd-run` outlives TERM and KILL, and a watcher in `run_in_background` dies
  at the next goodbye while the remote work it watches carries on. `helper_receipts.py` reports all of these to the
  next window; it does not keep them alive.

- 🔴 **A backgrounded `Agent` dies at 600 s of silence and leaves NOTHING on disk.** Three died
  that way 2026-09-17, all mid-read before their first write, all leaving a clean tree — so each
  cost a whole run rather than being truncated; the two that survived streamed output at 385 s
  and 575 s. **Brief every writing subagent to create its output file as a skeleton FIRST and
  fill it section by section** — a file write emits progress and persists partial work. A long
  read-then-write brief is the shape that trips it.
  🔴 **It happened AGAIN 2026-09-23** on a mechanical creature census, and the cheaper lesson is:
  for a **mechanical** census (glob, parse, count, tabulate), writing the script inline costs less
  than briefing an agent to survive the watchdog. Reserve subagents for work that needs judgement.
- ⚠️ **Two `PreToolUse` gates refuse tool calls outright and are easy to trip:**
  the `Agent` tool **refuses without an explicit `model`** (omitting it silently inherits this
  seat's tier, which is how past censuses ran on Opus; named agent types and `fork` are exempt) —
  ladder in `infrastructure/agents/Agent_Policy.md`. And `AskUserQuestion` is validated by
  `validate-question-card.py`: a `header` longer than **12 characters**, or a question not ending
  in `?`, refuses the **whole card**. Count the header before calling.
- 🔑 **A question-card option LABEL the owner clicks is OUR sentence, not his** — record it with
  `--by-card`, never `--owner-said`. Full rule: one field per kind of authority (owner, by question card 2026-10-11): `--owner-said` = his words (typo fixes and joining his own sentences are fine, meaning unchanged) · `--by-card "<question → option>"` = a decision he took by card (the label is our text) · `--per-ruling <item-id|event>` = a standing ruling cited by reference (it stands until he changes it) · `--why "…"` = your own words. No transcript proof runs; nothing checks a quote but its shape.
- ⚠️ **`RM_CreatureBehaviors.csproj` sets `EnableDefaultCompileItems false` and lists every file.** A new
  `.cs` in `Source/` without a `<Compile Include>` line **compiles into nothing, with no error**. Adding a
  file to that assembly is always a two-file change.
- 🔴 **`handoff.py` cannot tell two BENCH windows apart.** It REFUSES on "BRIDGE still held by
  BENCH" even when the hold belongs to the *other* window's live session, because both sign as
  `BENCH`. ⛔ Do not release it to satisfy the gate — that breaks a live game. `--force` records
  it as open, which is the correct exit, and the handoff must name whose hold it was.
- 🔴 **`modcheck run <Mod>` REWRITES the live `ModsConfig.xml`** — it calls `modlist_swap` and
  swaps to MINIMAL. It reads like a query verb and is a Charter expensive-list action. On the
  Mac it dies on the Windows path; on the Desktop it swaps his list unasked (2026-09-17).
- 🔴 **`daemon-reload` restarts the count of a `systemd-run --on-active` timer** (measured 2026-11-06,
  OPS_TIMERS_REVIVE_115F: a 30 s timer with a reload at +20 s fired at +50 s; an `--on-calendar` one fired at +30 s).
  Selftests and deploys reload often here, so a delay beyond a few minutes needs `--on-calendar`.
- 🔴 **`pkill -f` / `pgrep -f <pattern>` match the agent's own shell (exit 144), and a self-matching wait loop never ends.** Use `ps -eo pid,args | grep '[p]attern'` and wait on a PID. `setsid nohup cmd &` then `ps -p $!` shows nothing even though the job lives (setsid forks when it leads a process group, so `$!` is setsid's own pid); check liveness with `pgrep` or launch with `systemd-run --user --slice=rm-harness.slice`, and never delete a job's clone on a `ps -p $!` miss. `/tmp` is tmpfs: a full clone of the repo there fills it (8 GB).
- ⚠️ **The modal sweep's `jawa/window_list_close` answer "No open window's type name contains X" (`success:false`) is the CLEAN, normal result.** Recording it as an ERROR marks every verdict of the run `unknown`. Likewise `python.exe` cannot run git on a `\\wsl.localhost` checkout, so run identity reads `unknown` and no deploy is proven fresh: run git through `wsl.exe`.
- ⚠️ **A staged build can reuse a stale DLL: `winbuild.py` in a scratch clone after `git checkout` printed BUILT in 1.7 s but the DLL lacked a method added in that sha (the Windows `obj/` cache judged the source current), and a mutation-test rebuild within ~1 s reuses the old DLL.** `touch` the changed `.cs` (sleep ~4 s) and rebuild with `winbuild.py <Mod> -- --no-incremental`, then confirm the `.srchash` changed and that a new method name is in the DLL bytes before committing it. `./publish`'s own rebuild already passes `--no-incremental`.
- ⚠️ **A live-harness `git archive` export must include ALL of `src/` (`src/Directory.Build.targets` too), not just `src/RimMandrake`.** GSS refused to go live on the partial export.
- ⚠️ **`artledger.install(mod, ...)` with an ABSOLUTE mod path writes a live event the pre-push art guard cannot match, and the push is refused.** Pass the repo-relative mod (e.g. `src/RimStarWars/SWBestiary`).
- ⚠️ **FlowWorks' `RimMandrake_FlowWorks.csproj` also sets `EnableDefaultCompileItems false` (like CreatureBehaviors).** A new `Source/*.cs` referenced only from XML builds into nothing and `winbuild.py` still says BUILT. Check that the `.srchash` lists the file, or have a selftest assert every folder file is in the Compile list.
- ⚠️ **Changing how a settings window CALLS a section (`X.DoSettingsSection(list)` to a wrapper) breaks literal source-shape checks** in FlowWorks SelfTest (`*Checks.cs` wiring asserts), `Utils/selftest_settings_screens.py` and per-mod py selftests. Grep the whole `src/` for the literal call text and run `selftest_flowworks_stock.py` before publishing.
- 🔴 **`modcheck/required_checks.py` ignores `--help` and rewrites `required_checks.json` for EVERY mod from the working tree**, so in a shared clone it bakes peers' uncommitted scripts (e.g. a `validation.py` with no suite) into the manifest. Regenerate it only from a clean tree, or at a landing that owns every changed script.
- ⚠️ **A selftest CRASH that never reproduces (e.g. 72 clean concurrent runs) comes from the fixture `git()` helper, the only `RuntimeError` source:** capture the `run_selftests` CRASH stderr tail on first sight; it carries git's stderr. Selftests that call `tempfile.mkdtemp` / `NamedTemporaryFile(delete=False)` must remove the file in a `finally` (the seat TMPDIR held 922 leaked `tmp*` entries, 18 GB).
- 🔴 **`retarget_donor_patch.py` renames donor-named blocks onto the `RSW_`/`RM_` twin even when a twin block already exists**, so a generated per-animal file ends with two blocks for one def and the later one wins (AnimalTolerances_Ashkarr: 56 pairs; the later raw-band pin undid the fitted ComfyTemperature band on 61 bounds, a silent hard spawn gate). After any retarget pass check generated patch files for repeated xpath writes with differing values and keep the widest. `gen_vault_layouts.py` and `gen_vault_quests.py` are byte-reproducible offline (run them; `git diff` must be empty); `gen_races_mod.py --check` proves the StarWarsRaces defs.
- ⚠️ **`scenarios_map.py --river --build` without `--fresh-map` builds on the CURRENT map, whatever it is** (run with map C current it placed 0 of 8 stations and rewrote `review/scenarios/map_r_placed.json`). `jawa/set_current_map` to map R's id first, then restore the tracked `map_r_placed.json` / KEYSHEET with `git show HEAD:<path> > <path>`.
- ⚠️ **Run the FlowWorks C# selftest from WSL ONLY as `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py`** (~65 s; stages the clone on `D:` and prints `N/842 passed` plus hose suites). A hand-rolled `stage_build` + `dotnet.exe` run lacks the FlowWorks Defs the checks read and shows ~86 false FAILs; read the verdict from the `N/842 passed` line. Two helpers in one clone share the staged build dir (`D:\ClaudeWork\rimmandrake\build\selftest_*`) and `.winbuild-tmp`: a second run fails `MSB3027`/`MSB3021` ('file locked by RimMandrakeFlowWorks.SelfTest') or `FileNotFoundError`, which is an env failure, not a verdict; wait ~40 s and retry.
- ⚠️ **`selftest_dispatcher` and `role_launch`'s schema read the role registry's clone path `/home/mandrake/rm/bench`**, so they fail on any machine without that clone (the SteveDesktop mutation baseline failed; worked around with a symlink to `~/mutation/RimMandrake`). A selftest that scans the real `/proc` shares it with co-running selftests: young same-uid children have an unreadable `environ` for a moment (`role_launch.scan_marked` went blind on 11/489 scans without a re-read; 0/479 with `SCAN_RETRIES=3`), so live-/proc assertions must rescan while blind and print the blind reason.
- ⚠️ **`mutate4.py` in foundry_builder_gates rewrites the clone it runs in**: a tester must retarget a copy. `run_selftests.py` caps a run at 240 s, so `selftest_arena_tasks.py` (10 min) reads CRASH under it: run it directly.
- ⚠️ **`pulse_core.CLONES` lists bench and foundry only**: a program running from the Dispatcher clone that reads `read_ledger()` does not see its own RUNNER shard until a listed clone pulls. Pass the running clone too (`deadman_check.read_items`).
- 🔴 **`deploy_custom_mods.py` "in sync" is not proof a mod is wired.** It compares repo against deployed only, never deployed `About.xml` packageId against what `ModsConfig.xml` references. A half-executed tier-migration deploy left a mod whose packageId had drifted from `ModsConfig.xml`; nothing caught it for 2 days until `rimworld/load_game_ready`'s compatibility check refused the save. After a migration deploy, compare the deployed packageId with the parsed `ModsConfig.xml` entry.
- 🔴 **`modcheck run <Mod>` resets the live `ModsConfig.xml` to the owner's full list when it ends, even when it crashes.** It swaps to MINIMAL for the run and restores the full list on exit. Before the next restart or suite, reapply `modset_builder` tier, `launch_ready` and `start_debug_game_ready`; do not assume the test list is still in place.
- ⚠️ **FlowWorks C# SelfTest must run from the repo tree, not the winbuild stage.** `winbuild.py` stages FlowWorks `Source/` only, and the SelfTest reads sibling source files by walking up from the exe plus `Defs/`, `Patches/`, `Tools/` and other mods, so a run from `D:\ClaudeWork\rimmandrake\build\FlowWorks` always shows ~14 FAILs (`Could not find file ...`); read those as staging gaps, not regressions. Run it from `src/RimMandrake/FlowWorks/Source/SelfTest/bin/Release/net8.0` after `winbuild.py` (0 FAIL); the bench copy's exe exits 126 from ext4, so copy the staged `bin/Release/net8.0/RimMandrakeFlowWorks.SelfTest.*` there and run `dotnet.exe "$(wslpath -w <that dll>)"`.
- ⚠️ **`review_map.py --plan` (run to refresh `COVERAGE.md`) also rewrites `northstar/review/map/KEYSHEET.md` and `keysheet.html`**, and once downgraded 4 stations from 'works in game' to 'built, not yet seen' (88: 13->9 works). Commit only `COVERAGE.md` unless the keysheet change is understood.
- ⚠️ **`src/RimMandrake/Utils/modcheck/required_checks.py` ignores `--help`:** any argv other than `--check`/`--mod` REBUILDS and writes `required_checks.json` (~90 s). Read its docstring for usage and use `--check` to test staleness.
- ⚠️ **FlowWorks Mod Settings section structure** (braces, every setting in exactly one resettable section, section count) is audited by `src/RimMandrake/Utils/selftest_settings_screens.py`, NOT by any selftest under `src/RimMandrake/FlowWorks`: a misplaced brace that nested one Section inside another compiled and passed the C# SelfTest 773/773 and all 50 FlowWorks py tests. Run it after any settings-screen edit.
- ⚠️ **Parallel and repeated FlowWorks SelfTest builds collide on the shared stage.** The staged build dir `selftest_RimMandrakeFlowWorks.SelfTest_<hash>` is keyed by the clone tree, so a second build (another helper, or `--only` with both `selftest_flowworks_kernel_oracle.py` and `selftest_flowworks_stock.py` in one sweep) fails MSB3021/MSB3027/CS2012 (exe or obj DLL locked) and reports 'env/build failure, not a selftest verdict'; under `run_selftests` it shows as a 240 s timeout CRASH. That is a harness collision, not a code red: wait for `RimMandrakeFlowWorks.SelfTest` to exit and rerun alone. A fast loop can build into its own stage by overriding `selftest_winstage.stage_name_for` before `windows_project_path`. Helpers of one session also share a scratchpad dir, so a fixed name like `scratchpad/st.txt` is clobbered by a sibling: write logs under your own `D:\ClaudeWork` subdir. Time any new per-lay solver against the 4298-case hose fuzz first (a finite-difference clothoid fit pushed the full selftest past 535 s).
- ⚠️ **Attribute temp-dir size by `du` of the WHOLE dir before blaming a pattern.** The seat TMPDIR's '18G of leaked tmp* entries' was 78 MB of tmp*; the rest was pubclone (8.5G), harness scratch (5G), three `compose_RimMandrake.Biomes_*` dirs leaked by `biomes_compose.py:445` mkdtemp (1.4G) and `defs_copy.sqlite` (0.8G). To find which selftests leak, run each with its own fresh TMPDIR and list what is left (90 of 622 leaked). A new selftest should use `TemporaryDirectory` or the uniform atexit block that points `tempfile.tempdir` and TMPDIR at a private mkdtemp.
- ⚠️ **`selftest_flowworks_stock.py` takes a machine-wide fcntl lock at `$TMPDIR/flowworks_selftest_dotnet.lock`.** One helper looping `--only` runs in another clone starves every other clone's full run past the 540 s foreground cap (`run_selftests.py` allows 720 s for it). The stage dir is per-clone (sha1 of the clone root), so `TMPDIR=<private dir>` is safe and ran 1028/1028 in minutes. Fix candidate: key the lock per clone like the stage.
- ⚠️ **`run_selftests.py --only` takes file PATHS** (`src/.../selftest_x.py`), not bare test names; a bare name fails with 'names no such file'.
- ⚠️ **`run_selftests.py` shows only the head and tail of a test's ok lines**, so a failing test's captured output may not name the failing check (`selftest_dispatcher.py` failed once under 4 parallel tests, then passed four reruns; the check name was lost). Rerun the failing test alone and keep its raw output before calling a flake; the runner should print FAIL lines of a failing test.
