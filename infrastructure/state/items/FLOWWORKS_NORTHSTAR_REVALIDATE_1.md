# FLOWWORKS_NORTHSTAR_REVALIDATE_1

Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §2.4 and §7.

FlowWorks' `## north star` is VALIDATED (13 must + 3 cannot, hash matches, MEASURED 2026-09-30) but has
**zero pit bars**; Pits.md's 11+1 bind nothing (`modcheck run FlowWorks` reads only FlowWorks.md — the
`feature:` key is read by `doctor` alone). `PIT_SUPERDEEP_COLLAPSE_1` (authority over the spec) forbids
moving them as they stand and records his third-card-round rulings that rewrite them.

## to take to him (one sitting)
- The merged section text per plan §7 items 1–2 (new group "The pit — a superdeep excavation").
- The flagged structural changes, §7 item 3, each answered explicitly.
- The BLOCKED bars, §7 item 4: validate now (accept REFUSED until built) or park as candidate lines.

## acceptance
- `modcheck/cli.py validate FlowWorks --owner-said "<his words>"` recorded in the same sitting the text was edited.
- `northstar.parse(FlowWorks.md)` → VALIDATED; the pit bars present.
- `design/validation_walks/RimMandrake/Pits.md` deleted; `modcheck forget-key Pits` with a reason; `doctor` shows no ORPHAN_WALK for Pits.
- Any id he did not approve is absent (no agent-invented bar).
