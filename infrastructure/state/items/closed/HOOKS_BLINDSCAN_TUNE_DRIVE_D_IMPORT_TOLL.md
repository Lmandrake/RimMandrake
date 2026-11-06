## spec
`.claude/hooks/block_blind_scan.py` imports the `measure` package at startup, from a skill folder on the D: mount, on every Bash call. It reads 116 ms against 23 ms with the skill folder absent, and 31 ms for the next slowest hook. Hooks run in parallel, so this one hook sets the wall time of the whole Bash hook phase.

Most commands name no scanner. Defer the import until a command's segment names a scanner or reader. The hook must keep failing open if the skill is not installed.

Done when: `selftest_block_blind_scan.py` still passes, the import no longer runs for a command with no scanner, and `python3 src/RimMandrake/Utils/hook_latency.py` shows the `bash_common` before-wall down.

Evidence: `design/RimMandrake/hook_dispatcher_decision_2026-11-06.md`.
