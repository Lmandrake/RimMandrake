# BLOCKED — AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR (CLAUDE_STEVEDESKTOP_OFFLINE4), 2026-11-11 20:05 -0800

The repo copy of this file (whittle/amend_hook_harden_swept_a_neighbour/BLOCKED.md) could not be written: the
SteveDesktop WSL root disk is in **emergency read-only**:
`/dev/sdd / ext4 rw,relatime,discard,errors=remount-ro,data=ordered,emergency_ro`,
and some /usr/bin binaries (file, findmnt, dmesg) return `Input/output error`. ext4 hit an error and remounted
itself read-only, so every clone under /home/mandrake on this machine (all Whittle loops, the runner) can neither
write nor commit. /tmp (tmpfs) and /mnt/d still write.

Needs the owner (it ends every WSL session on the machine): from Windows, `wsl --shutdown`, then check the disk
(e2fsck on the distro's ext4.vhdx) before restarting the loops.

Work done and saved here, ready to land once the disk writes again:
- draft/selftest_promised_hooks_wired.py -> .claude/hooks/selftest_promised_hooks_wired.py (the class guard).
  Run read-only via a /tmp overlay: main passes (30/30 promised hooks wired), --rev 943a7a66da passes,
  --rev 8fb9f7f2b6 FAILS (30/30 unwired). draft/evidence/guard_runs.txt.
- The amend refusal holds: hook selftest 50/50 (draft/evidence/hook_selftest.txt); the registered command line
  from .claude/settings.json denies `git commit --amend` and `--amend --no-edit` by JSON decision through the
  `2>/dev/null || true` suffix, and allows `--amend src/x.py`.
Remaining after recovery: copy the guard in, code review, `rimflow guard AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR --test
.claude/hooks/selftest_promised_hooks_wired.py --instance "--rev 8fb9f7f2b6"`, publish, BROADEN, DONE, judge.
