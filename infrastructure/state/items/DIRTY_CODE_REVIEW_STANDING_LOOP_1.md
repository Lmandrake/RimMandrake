## the loop

Standing FOUNDRY full-file code-review loop, self-continuing. Pick a reachable file
not yet recorded CLEAN in `infrastructure/state/code_review/*.jsonl`, full-file
review it (never diff-scoped until it's CLEAN once), fix real bugs found, mark-clean
files with nothing significant found. Protocol: CLAUDE.md's "Code isn't clean until
a review says so" section.

🔴 **Always survey with `code_review_status.py list --show-untracked`, never bare
`list`.** Bare `list` silently omits every file that has never been given a status
entry at all — this is documented behavior (see the tool's own help text and
the 2026-09-13 FOUNDRY lesson in `infrastructure/state/lessons/`) but waves 1-43 of this exact loop didn't apply
it, so "0 DIRTY" was reported as a milestone multiple times while 346 never-entered
files sat invisible. Wave 44 (2026-09-24) rediscovered this the hard way. A future
curation pass should fold this into a skill; until then, this line is the fix.

## PAUSED — owner, 2026-09-20

Verbatim: **"Stop all clean/dirty code review until Wednesday 3pm token reset please."**

⛔ **Do not spawn or resume this loop — no mark-clean pass, no full-file review pass,
no bug-fix-under-this-item pass — before 2026-09-23 15:00.** This applies across a
reboot/new session; it is not scoped to one window's lifetime.

Progress so far today before the pause: two waves, 6 files marked CLEAN
(`RM_CompGrappler.cs`, `RM_CompProperties_Grappler.cs`, `RM_Hediff_Grappled.cs`,
`RM_MapComponent_LivingProduce.cs`), 2 real bugs found and fixed (`RM_LiquidTankUtility.cs`
closure-variable bug, `PyrelandsFireFront.cs` off-by-one on even fire-front widths — both
commits already pushed, see ledger). A third wave was launched and killed mid-start on
the owner's word — zero commits from it, nothing to clean up.

Resume normally after 2026-09-23 15:00 — this note is the only gate; no other ruling
changed.

## wave write-ups — one file per wave

Each wave's write-up is its own file, `infrastructure/state/code_review/waves/<utc>-<seat>-wave-<n>.md`
(e.g. `20261002T0712Z-FOUNDRY-wave-36.md`) — never appended here. Concurrent waves appending
to this one item file were a standing merge-conflict source (62 conflicted commits at K=5 in
the X2 history replay). Waves 1–35 (to 2026-09-27) are in
`infrastructure/state/code_review/waves/0000-history-to-2026-09-27.md`, frozen; read the
directory listing for everything since. The live tally is
`python3 src/RimMandrake/Utils/code_review_status.py list --show-untracked`, never a number
written in a wave file.
