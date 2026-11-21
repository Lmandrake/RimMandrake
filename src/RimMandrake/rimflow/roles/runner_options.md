# Runner selection

Claude is the default. Designer: `role_launch.py run-now --role Designer --runner codex --concept <dir> --by <seat> --why <reason> --apply`.
Set `RIMMANDRAKE_ROOT` to this clone and `WORKFLOWS_ROOT` to MandrakeWorkflows; see its `tools/RUNNERS.md` for setup.

Model comes from `codex_model` or `CODEX_MODEL`, then the CLI config; effort from `codex_effort` or `CODEX_EFFORT` (default high).
`codex_sandbox` / `CODEX_SANDBOX` defaults to workspace-write in code. On Archmagi every agent gets
`CODEX_SANDBOX=danger-full-access` from the environment (owner, 2026-11-09: *"Please grant that authority to all agents immediately."*).
The setting is in `~/.config/environment.d/50-codex-sandbox.conf`, `~/.zshenv` and `~/.profile`.
The existing Windows Codex helpers provide binary discovery and path conversion.

The weekly `ops_watch.c_codex` meter must report MEASURED usage and reset. An unreadable meter, or >90% used, refuses.
Each Codex run writes `<out>.events.jsonl` and `<out>.spend.json` (runner named; missing usage is UNMEASURED), separate from Claude budgets.

Ext4 work runs from the documented drive-local Codex scratch. The prompt directs all repository operations through WSL
against the original clone. UNC `-C` failed at tool execution in the 2026-11-09 probe
(`design/RimMandrake/roles.history.md` §runner_options.md: Runner selection). No automatic sandbox relaxation or Claude
fallback is attempted.

On Archmagi the default Windows workspace-write sandbox also denied WSL with `Wsl/Service/E_ACCESSDENIED`. So ext4
workers require an explicit `codex_sandbox: danger-full-access` selection (or `CODEX_SANDBOX`). Windows-launched WSL
processes do not inherit Linux systemd filesystem walls; Judge confinement has no live certification here.

## Native WSL Codex as the live-game driver (proved 2026-11-10)

A native WSL `codex exec --sandbox danger-full-access` session drove two complete live acceptance runners through
Windows `python.exe`. No Claude runner or Claude tool call drove the game. The run and its report are in
`design/RimMandrake/roles.history.md` §runner_options.md: Native WSL Codex and in `infrastructure/state/facts/codex_live_2026-11-10.md`.
The proof establishes launch → attach → disposable-site setup → real jobs/ticks → occupied save/load → assertions →
restoration → shutdown/release. The proof does not certify general colony play, a full mod list, Windows sandbox confinement,
mouse interaction or flight. The Windows-launch workspace-write failures above remain separate from the native WSL result.

### What runs automatically, and what the operator must supply

`.claude/settings.json` is Claude configuration. Codex does not execute its PreToolUse, Stop or SubagentStop hooks.
Use the repository's tools and inspect their results explicitly. The operator must supply:

- The current owner authority, own-clone boundary, quota gate and source-first decisions. Run the task's
  `ops_watch.c_codex` reading before every unit and stop at the owner's cutoff. A native CLI process does not acquire
  the MandrakeWorkflows runner's quota gate just by being named Codex.
- The duties of `block_blind_scan`, `block_blanket_git_stage`, `block_shared_tree_merge`, `queue_lint`,
  `block_dll_source_mismatch` and `block_ledger_lint`: use the right instrument, explicit paths, one writer per clone,
  rimflow-only ledger writes, a published DLL with its matching `.srchash`, and append-only shards. Set this clone's
  noreply Git identity and `core.hooksPath=infrastructure/githooks`; Git-native guards then run for Codex too. Inspect
  each failure: those guards explicitly fail open on some crashes. Other Claude art/canon/item-prose guards still apply
  when you touch that work. The live-driver authorization does not replace their requirements.
- Deploy planning, `--pull` rescue of unrecognized deployed edits, hold-file compliance, byte verification, intended
  tier selection and fresh process identity. The operator and the CLI own those contracts; saving source does not do them.
- Preserve raw receipts. Never flip a status or touch evidence merely to satisfy an mtime gate.
- Settings/snapshot debts, pilot diagnosis after three non-passes, exact readbacks, first-exception investigation, sane
  shutdown and immediate bridge release. Claude's helper `wrapup_hook` does not run automatically for a Codex helper.
  Keep the main driver responsible for cleanup even if a child exits.

`rimflow/driver_lock.py` recognizes the nearest Codex **or** Claude ancestor, so short-lived tool-shell PIDs do not
strand or invalidate a Codex lease. `RM_DRIVER_PID` remains the explicit override; normally let ancestor detection work.
Take only your own seat's bridge lease, never an OWNER hold. One process drives the bridge at a time. Read-only judges
do not attach while the proof runs.

### Operating sequence used here

Run repository commands in this clone. Read `CLAUDE.md`, the charter, Git and game
state workflows and the deploy/bridge/live-proof skills first. The bridge tools
run in Windows Python; WSL Python runs offline checks and orchestration.

1. Check quota. Plan deployment with `deploy_custom_mods.py --mod <Mod>`, wait for its final summary and read every
   change. Before you overwrite an unknown game edit, use `--pull <Mod>` and preserve its files/hashes outside the
   source tree. Then reconcile the rescued content deliberately. Use `winbuild.py <Mod>` for C#, keep the DLL/stamp
   pair, and publish completed changes through `./publish`.
2. Run `python3 src/RimMandrake/rimflow/cli.py bridge who`, then `bridge take --idle-ok --for "Codex live: <purpose>"`.
   A fresh clone may not yet have the ignored BRIDGE companion state; using the CLI establishes it. Verify the lease
   and stable driver identity before you touch the game. Stop an old game with
   `northstar_driver.live_session.stop_game()` and stamp `./game --why "<reason>" down` before you replace assemblies.
   Apply only the reviewed deploy plan and require its VERIFIED byte comparison.
3. While down, use `modset_builder.py` for the smallest dependency-complete all-DLC tier. The tiers of the 2026-11-10
   run are in `design/RimMandrake/roles.history.md` §runner_options.md: Operating sequence used here. A deployed mod
   is not necessarily active. No owner-list restoration is owed; leave the tier useful for the next task. Check
   windowed/background preferences; do not focus/fullscreen the game or exercise flyer flight.
4. Run `preflight_bridge.py --tier quicktest --modset <tier> --deep --seat BENCH --json <receipt>` and require GREEN.
   The preflight **tier** selects checks; **modset** selects the intended list. If you omit modset, a quick test can
   be judged against the full list by accident. Missing inputs are UNMEASURED, never green. Resolve dependency changes
   by actual LoadFolders/version/assembly provenance. Then explicitly accept an investigated new baseline. Never bypass
   fingerprints.
5. `./game --why "<reason>" loading` is a **ledger stamp**, not a launcher. Launch with
   `northstar_driver.live_session.launch_and_wait()`. It uses Steam and waits within the configured Steam-to-process
   budget, then within the process-to-bridge deadline against a fresh log cursor. A successful Steam command is not
   proof that its process already exists. Never launch the bare game executable.
6. Run the same preflight with `--live`. Require one fresh process, a listening bridge, the actual ordered running list
   and companion/deployed identity. Read Player.log's first exception **and Config error lines**. The `L03`
   missing-type gate can be GREEN while its reason reports nonfatal config errors; fix those causes too. Stamp
   `./game --why "<reason>" up` after you attach successfully.
7. Run the acceptance script through this clone's UNC path, for example:

   ```sh
   python.exe "$(wslpath -w "$PWD/src/RimMandrake/FlowWorks/northstar/concept_scenes.py")" \
     --out "$(wslpath -w "/tmp/concept_scenes_result.json")"
   ```

   Use an existing disposable registered save, never worldgen or a canonical save. A guarded scene-begin save must
   appear under a new name and leave every existing save unchanged. Reload it before you take the baseline, and again
   in `finally`. Compare the restored rectangle/settings, not just load success. Preserve occupied fixtures on occupied
   reload. Use governed real ticks, exact deltas, declared fixture identities and explicitly restored isolation controls.
8. Read failed tool payloads and the **first** Player.log exception before you fix the mod. Separate MOD, SITE and
   HARNESS causes. A successful order is not a running job, and a successful batch is not its requested cardinality.
   Keep positive and disabled controls. At three non-passes, obtain independent pilot diagnosis before you repeat.
   Build/deploy/restart for changed C# or XML, then rerun.
   Never relabel an old receipt. Obtain a fresh independent Whittle judge from the frozen statement and raw evidence,
   without builder conclusions.
9. Record the result on the ledger item. `verify --criterion` counts only against the registered build SHA: publish
   the tested artifact, update `implemented` with the **unchanged** owed criteria, then verify at that SHA. Do not claim
   a different SHA was tested just to close it. Publish the explicit ledger shard. Restore settings and snapshots even
   on failure; if they are broken, stop and stamp DOWN. On completion, stop, stamp DOWN and release immediately. Verify
   that both `rimflow bridge who` and its host driver lock are FREE before offline work.

A fresh clone's ignored JawaBench comparison artifact may be absent. Recover it only after you check the installed
assembly's embedded source hash against this clone. Or build it by the companion workflow. Keep token-bearing full logs
private.

### Stalls, fixes and lessons from this run

The 2026-11-10 run met 20 traps, and each has its lesson file under `infrastructure/state/lessons/`. The stall table
and that run's pit-judge and HugeThings notes are in `design/RimMandrake/roles.history.md` §runner_options.md: Stalls,
fixes and lessons from this run.

**Authority.** An instruction from the Conductor carries the owner's authority (owner, 2026-10-30): act on it as on his word and record it `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` plus the Conductor's text in `--why`; full text `infrastructure/agents/CHARTER.md`.
