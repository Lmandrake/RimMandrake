# artreg dead verbs, 2026-10-09
Verified zero live callers of `artreg.py verdict/committed/deployed` / `record_verdict/committed/deployed`:
src/, skills/, .claude/hooks, systemd user units, artpiped.py, fill_queue.py, console.py, selftests (only `withdraw` is tested), docs (only design text, historical Transient). git log -S in last month: only the creation commits and c2340fc39 (removal of the sole caller).
Removed: the 3 record_* functions, 3 argparse verbs, dispatch. Kept: `render`, `status`, `withdraw`, daemon/fill_queue writers, and replay of the legacy event kinds (render burn-up reads `committed`). No orphaned helpers remained; no selftests existed for them.
