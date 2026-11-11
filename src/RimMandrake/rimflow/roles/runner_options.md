# Runner selection

Claude is the default. Designer: `role_launch.py run-now --role Designer --runner codex --concept <dir> --by <seat> --why <reason> --apply`.
Relentless: set `runner: codex` in its rules JSON; Builder/Judge prompts and proof/verdict acceptance stay the same.

Whittle: `python3 "$WORKFLOWS_ROOT/whittle/run.py" --runner codex --cwd <project>`; Artisan: `RUNNER=codex LOGS=<logs> bash ralph/loop.sh`.
Set `RIMMANDRAKE_ROOT` to this clone and `WORKFLOWS_ROOT` to MandrakeWorkflows; see its `tools/RUNNERS.md` for setup.

Model comes from `codex_model` or `CODEX_MODEL`, then the CLI config; effort from `codex_effort` or `CODEX_EFFORT` (default high).
`codex_sandbox` / `CODEX_SANDBOX` defaults to workspace-write in code, but on Archmagi every agent gets `CODEX_SANDBOX=danger-full-access` from the environment (owner, 2026-11-09: *"Please grant that authority to all agents immediately."*; set in `~/.config/environment.d/50-codex-sandbox.conf`, `~/.zshenv` and `~/.profile`). The existing Windows Codex helpers provide binary discovery and path conversion.

The weekly `ops_watch.c_codex` meter must report MEASURED usage and reset; unreadable or >90% used refuses.
Each Codex run writes `<out>.events.jsonl` and `<out>.spend.json` (runner named; missing usage is UNMEASURED), separate from Claude budgets.

Ext4 work runs from the documented drive-local Codex scratch; the prompt directs all repository operations through WSL against the original clone.
UNC `-C` accepted a text-only probe on 2026-11-09 but tool execution failed with a sandbox setup-refresh error; no automatic sandbox relaxation or Claude fallback is attempted.

On Archmagi the default Windows workspace-write sandbox also denied WSL with `Wsl/Service/E_ACCESSDENIED`; ext4 workers require an explicit `codex_sandbox: danger-full-access` selection (or `CODEX_SANDBOX`).
The isolated Designer smoke passed with that selection. Windows-launched WSL processes do not inherit Linux systemd filesystem walls; Judge confinement has no live certification here.

## Native WSL Codex as the live-game driver (proved 2026-11-10)

A native WSL `codex exec --sandbox danger-full-access` session drove the complete
Whittle pit-prison acceptance runner through Windows `python.exe`, then the
HugeThings P1 runner. No Claude runner or Claude tool call drove the game.
[The report](../../../../whittle/CODEX_LIVE_2026-11-10.md) links the raw attempts,
preflights, restoration receipts, independent pit judgment and published fixes.
This establishes launch → attach → disposable-site setup → real jobs/ticks →
occupied save/load → assertions → restoration → shutdown/release. It does not
certify general colony play, a full mod list, Windows sandbox confinement, mouse
interaction or flight. The Windows-launch workspace-write failures described
above remain separate from this native WSL result.

### What runs automatically, and what the operator must supply

`.claude/settings.json` is Claude configuration; Codex does not execute its
PreToolUse, Stop or SubagentStop hooks. Use the repository's tools and inspect
their results explicitly. In this session the operator supplied:

- The current owner authority, own-clone boundary, quota gate and source-first
  decisions. Run the task's `ops_watch.c_codex` reading before every unit and stop
  at the owner's cutoff (88% in this run). A native CLI process does not acquire
  the MandrakeWorkflows runner's quota gate just by being named Codex.
- The duties of `block_blind_scan`, `block_blanket_git_stage`,
  `block_shared_tree_merge`, `queue_lint`, `block_dll_source_mismatch` and
  `block_ledger_lint`: use the right instrument, explicit paths, one writer per
  clone, rimflow-only ledger writes, a published DLL with its matching `.srchash`,
  and append-only shards. Set this clone's noreply Git identity and
  `core.hooksPath=infrastructure/githooks`; Git-native guards then run for Codex
  too. Inspect failures: those guards explicitly fail open on some crashes.
  Other Claude art/canon/item-prose guards still apply when that work is touched;
  the live-driver authorization does not replace their requirements.
- Deploy planning, `--pull` rescue of unrecognized deployed edits, hold-file
  compliance, byte verification, intended tier selection and fresh process
  identity. These are operator/CLI contracts, not a side effect of saving source.
- Whittle completion and helper wrapup. Its Claude Stop hook normally checks
  DONE evidence, broaden work, judgment and freshness. Codex must run the workflow
  validator explicitly when using the full workflow and inspect any refusal;
  `whittle_stop.done_problems(...)` is the read-only claim check. Calling the Stop
  hook itself can move BLOCKED.md into history. This session used the authorized
  acceptance runner directly, kept the old blocked trial intact, and recorded
  new raw results plus a fresh independent judge; it does **not** claim a new
  complete Whittle orchestrator/Stop-hook run. Preserve raw receipts; never flip
  statuses or touch evidence merely to satisfy an mtime gate.
- Settings/snapshot debts, pilot diagnosis after three non-passes, exact readbacks,
  first-exception investigation, sane shutdown and immediate bridge release.
  Claude's helper `wrapup_hook` does not run automatically for a Codex helper.
  Keep the main driver responsible for cleanup even if a child exits.

`rimflow/driver_lock.py` now recognizes the nearest Codex **or** Claude ancestor.
Short-lived tool-shell PIDs no longer strand or invalidate a Codex lease.
`RM_DRIVER_PID` remains the explicit override; ordinarily let ancestor detection
work. Take only BENCH's bridge lease, never an OWNER hold. One process drives the
bridge at a time; read-only judges do not attach while the proof runs.

### Operating sequence used here

Run repository commands in this clone. Read `CLAUDE.md`, the charter, Git and game
state workflows and the deploy/bridge/live-proof skills first. The bridge tools
run in Windows Python; WSL Python runs offline checks and orchestration.

1. Check quota. Plan deployment with `deploy_custom_mods.py --mod <Mod>`, wait for
   its final summary and read every change. Before overwriting an unknown game
   edit, use `--pull <Mod>` and preserve its files/hashes outside the source tree;
   reconcile the rescued content deliberately. Use `winbuild.py <Mod>` for C#,
   keep the DLL/stamp pair, and publish completed changes through `./publish`.
2. `python3 src/RimMandrake/rimflow/cli.py bridge who`, then
   `bridge take --idle-ok --for "Codex live: <purpose>"`. A fresh clone may not yet
   have the ignored BRIDGE companion state; using the CLI establishes it. Verify
   the lease and stable driver identity before touching the game. Stop an old
   game with `northstar_driver.live_session.stop_game()` and stamp `./game --why
   "<reason>" down` before replacing assemblies. Apply only the reviewed deploy
   plan and require its VERIFIED byte comparison.
3. Use `modset_builder.py` for the smallest dependency-complete all-DLC tier while
   down. For the pit runner this was `flowworks` (12 mods). The HugeThings P1
   runner used the dynamic tier
   `mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_hugethingstestraces__mandrake_rm_patches`
   (14 mods). A deployed mod is not necessarily active. No owner-list restoration
   is owed; leave the tier useful for the next task. Check windowed/background
   preferences; do not focus/fullscreen the game or exercise flyer flight.
4. Run `preflight_bridge.py --tier quicktest --modset <tier> --deep --seat BENCH
   --json <receipt>` and require GREEN. The preflight **tier** selects checks;
   **modset** selects the intended list. Omitting modset can accidentally judge a
   quick test against the full list. Missing inputs are UNMEASURED, never green.
   Resolve dependency changes by actual LoadFolders/version/assembly provenance,
   then explicitly accept an investigated new baseline; never bypass fingerprints.
5. `./game --why "<reason>" loading` is a **ledger stamp**, not a launcher. Launch
   with `northstar_driver.live_session.launch_and_wait()`: it uses Steam, waits
   within the configured Steam-to-process budget, then the process-to-bridge
   deadline against a fresh log cursor. A successful Steam command is not proof
   that its process already exists. Never launch the bare game executable.
6. Run the same preflight with `--live`; require one fresh process, listening
   bridge, actual ordered running list and companion/deployed identity. Read
   Player.log's first exception **and Config error lines**. L03's missing-type
   gate can be GREEN while its reason reports nonfatal config errors. Fix those
   causes too. Stamp `./game --why "<reason>" up` after attaching successfully.
7. Run the acceptance script through this clone's UNC path, for example:

   ```sh
   python.exe "$(wslpath -w "$PWD/src/RimMandrake/FlowWorks/northstar/concept_scenes.py")" \
     --out "$(wslpath -w "$PWD/whittle/evidence/codex-live/new-relative.json")"
   ```

   Use an existing disposable registered save, never worldgen or a canonical
   save. A guarded scene-begin save must appear under a new name without changing
   an existing save; reload it before taking the baseline and in `finally`.
   Compare the restored rectangle/settings, not just load success. Preserve
   occupied fixtures on occupied reload. Use governed real ticks, exact deltas,
   declared fixture identities and explicitly restored isolation controls.
8. Read failed tool payloads and the **first** Player.log exception before fixing
   the mod. Separate MOD, SITE and HARNESS causes. A successful order is not a
   running job, and a successful batch is not its requested cardinality. Keep
   positive and disabled controls. At three non-passes obtain independent pilot
   diagnosis before repeating. Build/deploy/restart for changed C# or XML, then
   rerun; never relabel an old receipt. Obtain a fresh independent Whittle judge
   from the frozen statement and raw evidence, without builder conclusions.
9. Record the result on the ledger item. `verify --criterion` only counts against
   the registered build SHA: publish the tested artifact, update `implemented`
   with the **unchanged** owed criteria, then verify at that SHA. Do not claim a
   different SHA was tested just to close it. Publish the explicit ledger shard.
   Restore settings and snapshots even on failure; if broken, stop and stamp
   DOWN. On completion, stop/stamp DOWN and release immediately. Verify both
   `rimflow bridge who` and its host driver lock are FREE before offline work.

A fresh clone's ignored JawaBench comparison artifact may be absent. Recover it
only after checking the installed assembly's embedded source hash against this
clone, or build it by the companion workflow. This run recovered the matching
ignored artifact without redeploying it. The missing `.srchash` warning remains
visible; this is not a claim of versioned companion provenance. The tested mod
DLLs retain their own checked stamps. Keep token-bearing full logs private.

### Stalls, fixes and lessons from this run

Each row has a filed lesson; the report preserves failed attempts alongside the
accepted receipts. These were not reasons to skip a check.

| Observed trap | Cause and repair | Lesson file under `infrastructure/state/lessons/` |
|---|---|---|
| Harmony fingerprint missing/changed | `Current` vanished; resolve actual root + 1.6 folders, investigate the installed update, retain required/hash-change controls | `20261111T025910Z-BENCH-harmony-loadfolders-fingerprint.md` |
| Fresh-clone preflight cannot establish its environment | Establish CLI state, recover the ignored companion by source identity, name the actual test modset | `20261111T030129Z-BENCH-fresh-clone-live-preflight.md` |
| Codex lease changes between tool shells | Recognize the stable Codex ancestor, retain overrides and exclusivity | `20261111T030157Z-BENCH-codex-hooks-driver-identity.md` |
| Steam helper says process gone before creation | Honor separate process-creation and bridge budgets, use a fresh log cursor | `20261111T031026Z-BENCH-steam-delayed-process-creation.md` |
| Live-list check needs an omitted DefDump mod | Read `running_mods` directly, validate count/order and stable PID/start; unreadable is unmeasured | `20261111T031218Z-BENCH-live-list-without-defdump.md` |
| Proof transport/work-type assumptions | Match actual static arguments, `PatientBedRest` and returned order contracts | `20261111T031500Z-BENCH-pit-proof-transport-contract.md` |
| Generated warden cannot do care work | Bounded Baseliner fixture selection; verify all required enabled work types and food supply | `20261111T032108Z-BENCH-pit-prison-capable-fixtures.md` |
| Tending helper cannot find a worker | Select registered WorkGiverDefs, not an exact base worker class | `20261111T032704Z-BENCH-registered-tending-workgiver.md` |
| Prisoners disappear after occupied load | Default site cleanup removes hostile-faction pawns; request only modal-broker controls for occupied snapshots | `20261111T034115Z-BENCH-occupied-load-vanishes-prisoners.md` |
| Governor removes the expected staged hostiles | Declare only those fixture IDs, withdraw only owned declarations; retain unrelated danger stops | `20261111T034500Z-BENCH-declare-hostile-proof-fixtures.md` |
| Python-only repair restages a slow C# suite | Split fast driver faults from retained production math checks | `20261111T034836Z-BENCH-separate-fast-pit-driver-tests.md` |
| Upright inmate sleeps beside delivered food | Probe while rested before the day; explicitly require the awake fixture precondition | `20261111T035901Z-BENCH-awake-not-only-not-downed.md` |
| Normal berserk stops an isolated mechanism proof | Apply/read back standard quiet flags across reloads, restore exact prior flags; no random-event claim | `20261111T041023Z-BENCH-isolated-prison-proof-random-events.md` |
| New care order is accepted but queued | Stop the previous worker job, require real returned care job to be current before ticking | `20261111T042221Z-BENCH-care-clock-requires-running-job.md` |
| Valid passes do not discharge old-build criteria | Register the repaired published artifact before verifying its unchanged criteria | `20261111T043944Z-BENCH-acceptance-build-sha.md` |
| Harness plant counted as an elephant race | Select resolved race definitions, keep exact expected race controls | `20261111T044005Z-BENCH-harness-thingdef-not-race.md` |
| Existing test races produce config errors | ThingDef names cannot end in digits; rename both fixture races/kinds and callers to `*Adult` | `20261111T044400Z-BENCH-harness-def-numeric-ending.md` |
| Offline allowance mistaken for production cap | Read declared production constants; report cap exhaustion only when observed | `20261111T044621Z-BENCH-budget-fixture-not-production-cap.md` |
| 100 artboard subjects become one | Artboard rows use newlines, not semicolons; assert returned count and every row | `20261111T044944Z-BENCH-artboard-batch-needs-newlines.md` |
| Cleared site later holds CollapsedRocks | Remove roofs before supports, then clear and verify every subject cell | `20261111T045127Z-BENCH-site-clear-roofs-before-supports.md` |

The pit judge's four bullets are true, with relative D6 versus legacy absolute D4,
a healed upright fixture and a complete isolated 60000-tick day in each arm.
HugeThings retains sparse-workload and T3 retry/butcher checks in
`HugeThings/northstar/workload_corpse_live.py`. The current doorway promise is
growth sealing access until a real cutting job removes the plant, exercised by
`HugeThings/northstar/trunk_doors_live.py`; acceptance requires that script's own
current raw proof. Large Pawns live clearance,
adversarial cross-map live exhaustion, dense Rot timing, full-list integration
and the review's remaining P2/design work are still UNVERIFIED here.
