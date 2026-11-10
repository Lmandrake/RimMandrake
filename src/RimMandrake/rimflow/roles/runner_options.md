# Runner selection

Claude is the default. Designer: `role_launch.py run-now --role Designer --runner codex --concept <dir> --by <seat> --why <reason> --apply`.
Relentless: set `runner: codex` in its rules JSON; Builder/Judge prompts and proof/verdict acceptance stay the same.

Whittle: `python3 "$WORKFLOWS_ROOT/whittle/run.py" --runner codex --cwd <project>`; Artisan: `RUNNER=codex LOGS=<logs> bash ralph/loop.sh`.
Set `RIMMANDRAKE_ROOT` to this clone and `WORKFLOWS_ROOT` to MandrakeWorkflows; see its `tools/RUNNERS.md` for setup.

Model comes from `codex_model` or `CODEX_MODEL`, then the CLI config; effort from `codex_effort` or `CODEX_EFFORT` (default high).
`codex_sandbox` / `CODEX_SANDBOX` defaults to workspace-write. The existing Windows Codex helpers provide binary discovery and path conversion.

The weekly `ops_watch.c_codex` meter must report MEASURED usage and reset; unreadable or >90% used refuses.
Each Codex run writes `<out>.events.jsonl` and `<out>.spend.json` (runner named; missing usage is UNMEASURED), separate from Claude budgets.

Ext4 work runs from the documented drive-local Codex scratch; the prompt directs all repository operations through WSL against the original clone.
UNC `-C` accepted a text-only probe on 2026-11-09 but tool execution failed with a sandbox setup-refresh error; no automatic sandbox relaxation or Claude fallback is attempted.

On Archmagi the default Windows workspace-write sandbox also denied WSL with `Wsl/Service/E_ACCESSDENIED`; ext4 workers require an explicit `codex_sandbox: danger-full-access` selection (or `CODEX_SANDBOX`).
The isolated Designer smoke passed with that selection. Windows-launched WSL processes do not inherit Linux systemd filesystem walls; Judge confinement has no live certification here.
