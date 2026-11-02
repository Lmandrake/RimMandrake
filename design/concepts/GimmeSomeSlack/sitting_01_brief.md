# The Designer, sitting 1: GimmeSomeSlack

Brief for the Designer's first real project. Written 2026-11-01 by a BENCH helper on the Conductor's order
(`CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`). Your instructions are `src/RimMandrake/rimflow/roles/designer.md`; this
file only says where to start. Launch (the Conductor runs it, never the role itself):
`python3 src/RimMandrake/rimflow/role_launch.py run-now --role Designer --by Conductor --why GimmeSomeSlack --apply`

## Why GimmeSomeSlack and not FlowWorks

The owner ruled the first real project is FlowWorks or GSS (2026-11-02, `PLANNING_BUILD_DAYS_OF_ORDERS_NO_HOME`).
GSS, for three reasons:

1. **It is the smaller mod.** Its walk is 155 lines against FlowWorks' 510 (`design/validation_walks/RimMandrake/`).
   The design says a small mod should fit in eight leaves. The first run has to show the whole process to its end,
   including the Cold Reader exam that has never been run. A smaller tree makes that likely in one or two sittings.
2. **FlowWorks is already anchored.** The design's worked example (§13) is a FlowWorks feature with owner lines
   *played by the author*. A first sitting on FlowWorks would read those fake answers as precedent. GSS has no played
   answers anywhere.
3. **GSS has real pruning work.** Its walk lists ten live `must be true` lines (M1 to M13, hoses moved out) and many owner quotes about look,
   motion and slack. Asking "would you reject the mod if only this were false?" will cut real lines. That is the skill
   this role exists to prove. FlowWorks would mostly test whether the Designer can summarise a big walk.

FlowWorks comes second, once GSS has been through the exam and the lock.

## What exists already (Stage 0 reading, in this order)

- `design/validation_walks/RimMandrake/GimmeSomeSlack.md`: `## north star` is VALIDATED and is what `root_ref` cites.
  Its `### the experience` holds his verbatim words from 2026-10-02 to 2026-10-05. Only those go in `## his words`.
- `design/RimMandrake/messy_conduit_design_2026-10-02.md`, `messy_conduit_phase2_design_2026-10-02.md`,
  `messyconduit_style_per_build_design.md`: the designs his words came from.
- The ledger: `rimflow` items and `--owner-said` events naming GimmeSomeSlack or MessyConduit.
- `src/RimMandrake/GimmeSomeSlack/`: the code exists. You read it for feasibility only. You never edit it.

## The retrofit

GSS is built and proved. Your tree describes the mod he wants, not the code that exists. When a built behaviour is
not something he would reject the mod without, it is no leaf, however well it is tested. When something he wants is
not built, it is still a leaf, and the gate will hold the mod until it is built. Say both plainly on the sheet.

## Leads for the first two rounds (yours to test, not findings)

- **Motion.** He said "Movement/animation is not appropriate for Northstar". Is the slack look a leaf with a still oracle
  (screenshot of stages of tangle), or a waiver? Picture both.
- **Boundary with FlowWorks.** M11 and M12 (hoses) moved to FlowWorks on 2026-10-11. Is "GSS draws nothing for a
  hose" a `does not`, or silent?
- **Overhead lines (M10, M10b).** Phase 2 added masts, spans and a wire-down alert. Is this core to "everything is a
  too-long extension cord", or a second mod living in the same folder? Pruning question.
- **Styles (M13).** Four art styles per build. Would he reject the mod with one style only?
- **Removal (E1).** He paused removal checks (2026-10-04). That is a test cadence, not a waiver of the property.
  Ask whether "a save loads clean without the mod" is a leaf.
- **Unsaid sweep.** A 40-colonist base with conduit under every room. What does the "huge tangle" look like, and
  what does it cost per tick? The floor already gives tick cost. Do not ask him a number the floor holds.

## This sitting

Stages 0 and 1 only, at most two rounds. End by writing `log.md` and a draft `sheet.md` in this folder, then hand
the Conductor one turn for him (claim, attack, picture, at most three asks), each ask checked with
`concept_tree.py askcheck`. Nothing goes on the ledger as his until he has said it. GSS builds belong to FOUNDRY.
You file nothing for building before Stage 5.
