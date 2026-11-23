# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only the old figures and the lines that are no longer true. Git holds
the rest. Each line below is a record, not a rule. The rewrite was on 2026-11-23.

## Does it already exist (§0)

- §0 once said "91 tools already ship" (2026-08-19). A source count on 2026-11-23 read 427 `jawa/` names. Counts move: recount.
- The source command once read `D:/Luke/dev/RimMandrake/src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`. WSL bash
  has no `D:/` path.
- The client command once read `python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\rimbridge_client.py --list-tools`,
  with no quotes. Bash removes those backslashes (measured: `can't open file 'D:\\Lukedev...'`).
- §0 once called the roster ~95 candidate tools. §6 also said ~95.
- §0 once called the SCALAR-only gap of `jawa/get_defs` a gap still to fix (BENCH, 2026-09-01). Commit `5d576b8568` added
  `deep` the same day.

## The cycle (§1)

- The kill step was once `taskkill.exe /F /IM RimWorldWin64.exe`. Archmagi now has two games with that image name.
- The launch step once named `D:\Luke\dev\RimMandrake\src\RimMandrake\bridgetools\launch_and_wait.sh`, and the proof step
  `D:\Luke\dev\RimMandrake\src\RimMandrake\bridgetools\prove_<thing>.py`, both with no quotes.
- `launch_and_wait.sh` once waited for the log to truncate. A lesson of 2026-09-21 said that its EXIT CODE was not the ready
  signal: it printed `TIMEOUT after 273s` on a cold load that went on to succeed at 1005 s. It told the reader to poll
  `Player.log` for this run's bridge-ready line, after the log truncated. `launch_ready.py` replaced that loop on
  2026-10-10 (`cbec3e5b54`): the old log is moved away, and READY needs a receipt of the current process.
- §1 once said "there is only one `RimWorld.exe` and one deployed `BridgeTools` DLL on the machine". Each game now has its
  own install and its own `BridgeTools` folder.

## The [Tool] pattern (§2)

- The class was once split across five files. The example call to `InvokeAsync` once passed no `cancellationToken`, against
  the lesson in `traps.md` § 3.

## The design rules (§3) and the guards (§4)

- Rule 9 once read: "**Avoid `jawa/` prefixes in prose inside descriptions.** `build.py` scans the assembly for `jawa/...`
  literals". Since 2026-09-06 (`da7cef3c55`) `build.py` reads the attribute table. Rule 3 also tells an author to
  name `jawa/world_commit` in a description.
- Rule 11 once listed a `cond_eval` tool as PLANNED, with all four condition items. `jawa/cond_eval` landed in
  `54558735f9b8` (2026-11-06).
- §4 once said that the removal guard also fires when "a docstring made a phantom name", and told the reader to verify that
  the loss is a phantom before `--allow-tool-removal`. It called DRIFT "Expected mid-session".
- §4 once had the lead "Two byte-scans, two different tolerances." `verify_gm_gate` matched LENGTH-PREFIXED tool names in
  the compiled blob. `tool_surface()` was looser, an upper bound that matched a name quoted in prose. So a
  `==`-count check against it failed forever, and the fix was to subtract a named `PHANTOMS` set, not to widen the
  tolerance. Both are exact metadata reads since 2026-09-06.

## The proof (§5)

- §5 once said that every `prove_*.py` opens with the same lines. On 2026-11-23, 17 of 47 name `start_debug_game_ready`.
