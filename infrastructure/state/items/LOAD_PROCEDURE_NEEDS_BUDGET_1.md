
## spec
`infrastructure/state/LOAD_PROCEDURE.md` was created 2026-08-23 by the `NEXT_RELOAD.md` split
(`RUN_SHEET_PER_LOAD_BLOCKS_1`). It has no entry in `BUDGETS`, so it falls to the
`infrastructure/state/*.md` default of **250** and reports **OVER +9** at 259 lines.

🔑 **It is not bloat — its provenance density is 2.7, the lowest in the repo.** What remains is
rules, full paths and paste-able commands, which `warn_doc_budget.py` says never to cut. This
is the case that hook names: *"If you truly cannot cut it, the BUDGET is wrong."*

**Suggested: 400** — what `NEXT_RELOAD.md` carried when it held both halves. It is standing
procedure for a ~25-minute irreversible operation and it earns the room.

⚠️ **DECIDE did not make this edit** because REP had `doc_budget.py` uncommitted in the shared
working tree at the time (raising `BUILDABLE.md` 500 → 800, adding `TEST_PLAN.md` 500, and
exempting `facts/*.md` with `None`). Editing it would have clobbered that.

## verify
`python3 src/RimMandrake/Utils/doc_budget.py | grep LOAD_PROCEDURE` reads `ok`.
Then `python3 .claude/hooks/selftest_warn_doc_budget.py` — it must still pass, because `BUDGETS`
is imported by the hook rather than copied.

## criteria
- [ ] A budget entry for `LOAD_PROCEDURE.md`, with a one-line reason in the same commit.
