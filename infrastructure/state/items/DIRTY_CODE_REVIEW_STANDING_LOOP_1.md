## the loop

Standing FOUNDRY full-file code-review loop, self-continuing. Pick a reachable file
not yet recorded CLEAN in `infrastructure/state/CODE_REVIEW_STATUS.json`, full-file
review it (never diff-scoped until it's CLEAN once), fix real bugs found, mark-clean
files with nothing significant found. Protocol: CLAUDE.md's "Code isn't clean until
a review says so" section.

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
