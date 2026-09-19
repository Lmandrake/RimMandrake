# CODEX_EDIT_TIMEOUT_1 — root cause found and fixed: orphaned Windows-Sandbox helper processes

Filed after Phase 0 calibration (`ART_PIPELINE_DAEMON_1`) hit `edit` mode
(image-conditioned, `codex_image.py edit --image <ref>`) failing 3/3 at
240s/360s/480s, zero images ever reaching `generated_images/`
(`Transient/artpipe_calibration_2026-09-09/CALIBRATION.md` §3, §6.1).

## Root cause — CONFIRMED live, 2026-09-09

The 3 failed attempts all ran against the **same per-worker isolated
`--codex-home`** (`queue_N1/.worker_homes/w0`), one after another. On this
Windows install, `codex.exe exec --sandbox workspace-write` spawns a
**separate, elevated child process** —
`codex.exe --run-as-windows-sandbox --windows-sandbox-private-desktop
--windows-sandbox-level elevated ... --codex-run-as-fs-helper` — to enforce
the filesystem permission profile. `codex_image.py`'s own
`subprocess.run(cmd, timeout=...)` only kills the *immediate* `codex exec`
child on a timeout; Windows does not cascade-kill a process's own children,
so **every timed-out call against an isolated home leaked that elevated
helper as a permanent orphan.**

Found live, 3+ hours after the calibration run: 4 `codex.exe
--run-as-windows-sandbox ... --codex-run-as-fs-helper` processes still
running (PIDs 30504/36580/27476/24604, `CreationDate` 14:35–14:51 on
2026-09-09 — matching the 3 documented timeout attempts almost to the
minute), all near-zero CPU (idle, not spinning), one naming
`queue_N1\.worker_homes\w0`, a directory that **no longer exists on disk**.
Killed them (`Stop-Process -Force`) as part of this investigation — they
held no live value and blocked nothing else, but see risk note below.

**Why this produces a categorical 3/3 failure, not just "slow":** each
retry in the calibration reused the *same* `w0` home while the prior
attempt's orphaned helper was still alive on it, so each subsequent call
started already contended against its own predecessor — consistent with
"more timeout, still zero output" across 240→360→480s, instead of the
later attempts simply needing (and getting) more time.

## Reproduced clean and fixed

Isolation of the two variables, live, this session (see
`Transient/codex_edit_repro_2026-09-09.log`,
`Transient/codex_edit_repro_isolated_2026-09-09.log`,
`Transient/codex_generate_isolated_2026-09-09.log`):

| call | home | helper spawned | result |
|---|---|---|---|
| `edit`, same AutomatedSmelter reference | **shared** `~/.codex` | no | OK, 71s, no harvest needed |
| `edit`, same reference, **fresh** isolated home | isolated (freshly seeded, no prior orphan on it) | yes | OK, harvested at 200s cutoff — image had already landed |
| `generate`, no reference | fresh isolated home | (not confirmed either way) | OK, harvested at 120s cutoff |

A single, fresh, uncontended isolated-home `edit` call completes and lands
its image — the mode is not "broken" in general. `generate` against an
isolated home is *also* slower than the shared home and also needed the
harvest fallback, so the elevated-sandbox path is a real per-call latency
tax for **any** isolated-home call, edit or generate — not an edit-only
defect. What made the 3 documented attempts categorically fail (zero
output even at 480s) is the **repeated reuse of one fouled home**, not edit
mode itself.

**Fix shipped**: `skills/generating-images/scripts/codex_image.py` —
`kill_orphaned_sandbox_helpers()` + a call site in `do_image()`. On a
timeout against an explicit `--codex-home` override (never the shared
default, where a concurrent unrelated call could legitimately have its own
helper), it harvests first (unchanged priority), then finds and
force-kills any `--run-as-windows-sandbox` helper whose command line names
that exact home, via `Get-CimInstance Win32_Process` + `Stop-Process`. This
stops a worker's home from ever being handed to its own next job already
fouled by an orphan — which is exactly the daemon's real usage pattern
(one long-lived home per worker slot, many jobs in sequence).
3 new selftests added to `selftest_codex_image.py`
(`test_kill_orphaned_sandbox_helpers_parses_pids`,
`..._survives_powershell_failure`,
`test_orphan_cleanup_only_fires_on_timeout_with_home_override`); full
47/47 repo selftest suite re-run clean.

## What this does NOT fix

The elevated-sandbox path itself is measurably slower (~150–250s vs 71s)
and, per the original 3/3, can apparently still fail outright under enough
contention — that is upstream Codex-on-Windows sandboxing behaviour on
this machine, not something `codex_image.py` controls. For
`ART_PIPELINE_DAEMON_1`'s worker design: budget isolated-home `edit` calls
at ≥250–300s (not the calibration's 240s floor), and this fix now means a
timeout there cleans up after itself instead of compounding into the next
job on the same worker.

## Environmental checks ruled out
- Auth: `codex_image.py probe` clean, `chatgpt` auth mode, version
  `codex-cli 0.153.4` responding normally throughout.
- No stuck Windows Security/UAC dialog on the interactive desktop
  (`system_screenshot.py` capture reviewed directly — RimWorld's own debug
  log window was on top, nothing else). A prompt on the sandbox's own
  *private* desktop would not appear here regardless — plausible but not
  directly observed; the orphan-process finding is the confirmed mechanism
  and is sufficient on its own to explain the failure pattern.
- Reference image path/format: valid RGBA PNGs, same ones used successfully
  by the shared-home repro — not the blocker.

## criteria
- [x] Reproduced with a shortest-reasonable-effort repro (three real, live
      `codex_image.py` calls; not inferred).
- [x] Root cause identified with live process evidence, not a guess.
- [x] Fixed (orphan cleanup) and verified (selftests + live orphan kill).
- [ ] Not verified: whether the elevated-sandbox path can still fail
      outright on a genuinely fresh, uncontended home given enough time —
      no repro of that observed this session; treat as open risk for the
      daemon's own live drain, not this item's scope.
