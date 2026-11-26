# Runner selection

Claude is the default runner. To run the Designer on Codex, use this command:
`role_launch.py run-now --role Designer --runner codex --concept <dir> --by <seat> --why <reason> --apply`.
Set `RIMMANDRAKE_ROOT` to this clone and `WORKFLOWS_ROOT` to MandrakeWorkflows. The setup is in MandrakeWorkflows, `tools/RUNNERS.md`.

- The model comes from `codex_model` or `CODEX_MODEL`, then from the CLI config.
- The effort comes from `codex_effort` or `CODEX_EFFORT` (default high).
- `codex_sandbox` / `CODEX_SANDBOX` defaults to workspace-write in code. On Archmagi every agent gets
  `CODEX_SANDBOX=danger-full-access` from the environment (owner, 2026-11-09: *"Please grant that authority to all agents immediately."*).
  The setting is in `~/.config/environment.d/50-codex-sandbox.conf`, `~/.zshenv` and `~/.profile`.
- The run goes through the one Codex door (Dispatch `door_agent.py`, loaded by `agent_runner.py`), on the one sign-in.
- The weekly `ops_watch.c_codex` meter must report MEASURED usage and a MEASURED reset. If the meter cannot be read, or reports >90% used,
  the launch is refused.
- Each Codex run writes `<out>.events.jsonl` and `<out>.spend.json`. The spend file names the runner. Missing usage is
  UNMEASURED. The spend is separate from Claude budgets.

Codex works directly in the clone. No automatic sandbox relaxation or Claude fallback is attempted. Confinement of a Judge
has no live certification here.

## Native WSL Codex as the live-game driver (proved 2026-11-10)

A native WSL `codex exec --sandbox danger-full-access` session drove two complete live acceptance runners through
Windows `python.exe`. No Claude runner or Claude tool call drove the game. The run and its report are in
`design/RimMandrake/roles.history.md` §runner_options.md: Native WSL Codex and in `infrastructure/state/facts/codex_live_2026-11-10.md`.

- The proof establishes this chain: launch → attach → disposable-site setup → real jobs/ticks → occupied save/load →
  assertions → restoration → shutdown/release.
- The proof does not certify general colony play, a full mod list, Windows sandbox confinement, mouse interaction or
  flight.
- The failures of the Windows-launch workspace-write sandbox (the 2026-11-09 probes, `design/RimMandrake/roles.history.md`
  §runner_options.md: Runner selection) remain separate from the native WSL result.

### What runs automatically, and what the operator must supply

`.claude/settings.json` is Claude configuration. Codex does not execute its PreToolUse, Stop or SubagentStop hooks.
Use the repository's tools and inspect their results explicitly. The operator must supply:

- **The authority and the quota gate.** Supply the current owner authority, the own-clone boundary and the quota gate.
  Run the task's `ops_watch.c_codex` reading before every unit. Stop at the owner's cutoff. A
  native CLI process does not get the quota gate of the MandrakeWorkflows runner only because it is named Codex.
- **The duties of six hooks:** `block_blind_scan`, `block_blanket_git_stage`, `block_shared_tree_merge`, `queue_lint`,
  `block_dll_source_mismatch` and `block_ledger_lint`. The duties are:
  - the right instrument;
  - explicit paths;
  - one writer per clone;
  - rimflow-only ledger writes;
  - a published DLL with its matching `.srchash`;
  - append-only shards.
- **The Git guards.** Set this clone's noreply Git identity and `core.hooksPath=infrastructure/githooks`. Then the
  Git-native guards run for Codex too. Inspect each failure: those guards explicitly fail open on some crashes.
- **The other guards.** Other Claude art/canon/item-prose guards still apply when you touch that work. The live-driver authorization
  does not replace their requirements.
- **The deploy duties.** The operator and the CLI own these duties. A save of the source does none of them:
  - deploy planning;
  - `--pull` rescue of unrecognized deployed edits;
  - hold-file compliance;
  - byte verification;
  - intended tier selection;
  - fresh process identity.
- **The evidence.** Preserve raw receipts. Never flip a status or touch evidence merely to satisfy an mtime gate.
- **The rest of the run.** Supply these:
  - settings/snapshot debts (each setting and snapshot that the run changed and must restore, step 9);
  - pilot diagnosis after three non-passes;
  - exact readbacks;
  - first-exception investigation;
  - sane shutdown and immediate bridge release.

  Claude's helper `wrapup_hook` does not
  run automatically for a Codex helper. Keep the main driver responsible for cleanup even if a child exits.

`rimflow/driver_lock.py` recognizes the nearest Codex **or** Claude ancestor. So short-lived tool-shell PIDs do not
strand or invalidate a Codex lease. `RM_DRIVER_PID` remains the explicit override. Normally let ancestor detection work.
Take only your own seat's bridge lease, never an OWNER hold. One process drives the bridge at a time. Read-only judges
do not attach while the proof runs.

### Operating sequence used here

Run repository commands in this clone. Before you start, read `CLAUDE.md`, the charter, and the Git and game
state workflows. Also read the deploy, bridge and live-proof skills. The bridge tools
run in Windows Python. WSL Python runs offline checks and orchestration.

1. Check quota. Plan deployment with `deploy_custom_mods.py --mod <Mod>`, wait for its final summary and read every
   change.
   - Before you overwrite an unknown game edit, use `--pull <Mod>`. Preserve its files/hashes outside the
     source tree. Then reconcile the rescued content deliberately.
   - Use `winbuild.py <Mod>` for C#. Keep the DLL/stamp pair. Publish completed changes through `./publish`.
2. Run `python3 src/RimMandrake/rimflow/cli.py bridge who`, then `bridge take --idle-ok --for "Codex live: <purpose>"`.
   - A fresh clone may not yet have the ignored BRIDGE companion state. Use of the CLI establishes that state.
   - Verify the lease and stable driver identity before you touch the game.
   - Before you replace assemblies, stop an old game with `northstar_driver.live_session.stop_game()` and stamp
     `./game --why "<reason>" down`.
   - Apply only the reviewed deploy plan. Require its VERIFIED byte comparison.
3. While the game is down, use `modset_builder.py` for the smallest dependency-complete all-DLC tier. The tiers of the 2026-11-10
   run are in `design/RimMandrake/roles.history.md` §runner_options.md: Operating sequence used here.
   - A deployed mod is not necessarily active.
   - No owner-list restoration is owed. Leave the tier useful for the next task.
   - Check windowed/background preferences. Do not focus/fullscreen the game or exercise flyer flight.
4. Run `preflight_bridge.py --tier quicktest --modset <tier> --deep --seat BENCH --json <receipt>` and require GREEN.
   - The preflight **tier** selects checks; **modset** selects the intended list. If you omit modset, a quick test can
     be judged against the full list by accident.
   - Missing inputs are UNMEASURED, never green.
   - Resolve dependency changes by actual LoadFolders/version/assembly provenance. Then explicitly accept an
     investigated new baseline. Never bypass fingerprints.
5. `./game --why "<reason>" loading` is a **ledger stamp**, not a launcher. Launch with
   `northstar_driver.live_session.launch_and_wait()`.
   - That function uses Steam for ArchBig. It starts ArchBig directly when Steam does not take the launch. It starts
     any other game directly. It waits within the configured Steam-to-process budget. Then it waits within the
     process-to-bridge deadline against a fresh log cursor.
   - A successful Steam command is not proof that its process already exists.
   - Never launch the bare game executable.
6. Run the same preflight with `--live`. Require one fresh process, a listening bridge, the actual ordered running list
   and companion/deployed identity.
   - Read Player.log's first exception **and Config error lines**. The `L03` missing-type gate can be GREEN while its
     reason reports nonfatal config errors. Fix those causes too.
   - Stamp `./game --why "<reason>" up` after you attach successfully.
7. Run the acceptance script through this clone's UNC path, for example:

   ```sh
   python.exe "$(wslpath -w "$PWD/src/RimMandrake/FlowWorks/northstar/concept_scenes.py")" \
     --out "$(wslpath -w "$(python3 ~/dev/Lodestar/bin/lib/agent_storage.py)/scratch/concept_scenes_result.json")"
   ```

   - Use an existing disposable registered save, never worldgen or a canonical save.
   - A guarded scene-begin save must appear under a new name and leave every existing save unchanged. Reload that save
     before you take the baseline, and again in `finally`.
   - Compare the restored rectangle/settings, not just load success.
   - Preserve occupied fixtures on occupied reload.
   - Use governed real ticks, exact deltas, declared fixture identities and explicitly restored isolation controls.
8. Read failed tool payloads and the **first** Player.log exception before you fix the mod. Separate MOD, SITE and
   HARNESS causes.
   - A successful order is not a running job. A successful batch is not its requested cardinality.
   - Keep positive and disabled controls.
   - At three non-passes, obtain independent pilot diagnosis before you repeat.
   - Build/deploy/restart for changed C# or XML, then rerun.
   - Never relabel an old receipt.
   - Obtain a fresh independent judge: a run that did not make the work. The judge works from the frozen statement and
     raw evidence, without builder conclusions.
9. Record the result on the ledger item. `verify --criterion` counts only against the registered build SHA.
   - Publish the tested artifact. Update `implemented` with the **unchanged** owed criteria. Then verify at that SHA.
     Do not claim that a different SHA was tested just to close the item.
   - Publish the explicit ledger shard.
   - Restore settings and snapshots even on failure. If they are broken, stop and stamp DOWN.
   - On completion, stop, stamp DOWN and release immediately. Before offline work, verify that both
     `rimflow bridge who` and its host driver lock are FREE.

A fresh clone's ignored JawaBench comparison artifact may be absent. Recover it only after you check the installed
assembly's embedded source hash against this clone. Or build it by the companion workflow. Keep token-bearing full logs
private.

### Stalls, fixes and lessons from this run

The 2026-11-10 run met 20 traps. Each trap has its lesson file under `infrastructure/state/lessons/`. The stall table
and that run's pit-judge and HugeThings notes are in `design/RimMandrake/roles.history.md` §runner_options.md: Stalls,
fixes and lessons from this run.

**Authority.** An instruction from the Conductor carries the owner's authority (owner, 2026-10-30). Act on the instruction as on his word. Record it with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` plus the Conductor's text in `--why`. Full text: `infrastructure/agents/CHARTER.md`.
