## spec
Owner broadcast, 2026-08-15, relayed by REP: *"Game is down, offline work may
begin. Stage the next game load and prepare additional content. Ensure the
mod list shows the many removed mods correctly (BUILD)."*

Game confirmed DOWN (`tasklist.exe`, no `RimWorldWin64.exe`). The shutdown
window is OPEN, which is the only window for the deploy-gated items —
`queue/BUILD.md` B0 and B1 both say "game must be DOWN" and have been
waiting on exactly this.

Two halves, both yours:
1. STAGE THE LOAD. `infrastructure/state/NEXT_RELOAD.md` is assembled by you.
   Order it, make every item name the call that produces its evidence, and
   sweep the seat queues for anything `blocked — needs a live game`
   (CHECK's C37 70-race lineup is parked waiting on a load).
2. PREPARE ADDITIONAL CONTENT. Spec it and feed BUILD. The mod-list half is
   the owner's explicit assignment to BUILD and is filed there as
   `mod-list-shows-descoped-removals-9c4e12`; it is already measured correct,
   so do not re-spec it.

## verify
`NEXT_RELOAD.md` is ordered top-to-bottom with a call named per item, and no
item in it is one the down-window makes unnecessary.

## criteria
the load answers every question staged in it; nothing needs a second load
that could have ridden this one.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

done — 2026-08-15, both halves. `0459627` + `ac8cee7`.
HALF 1, the load. `NEXT_RELOAD.md` opens with **§1.0 THIS WINDOW**, a
six-step ordered deploy manifest, and §5 carries **six** live items in order
instead of three — C37's Rodian snoot is L0 and first, then C40, C41+C39,
and C38 last because it needs a second `PoisonForest` map. C36's crossref
sweep moved to §2 where the startup harvest actually collects it. 378/400
lines, in budget. ⛔ **The `[v2]` sea assembly is struck from the window** —
see D-CRIT, superseded today; B0's line is corrected.
HALF 2, the content. **B66** folds D-CHK2 and D-CHK3 into one
`gen_races_mod.py` regenerate — it must ride THIS window or L0 photographs
four species that are magenta for a cause already diagnosed. **B67** is the
find: the seven cherrypick decision files are gitignored as "derived", so
~1,300 owner keep-judgements live on one disk, and `cherrypick_build.py` has
never validated any of the 1,308 deployed keys. Chain step 1 corrected in
`V1.md` — five categories are decided and live, not "weapons and apparel
next". The owner ask is in `queue/HUMAN.md`.
