# RIMMANDRAKE_DIAGNOSE_PLOT_H_BYSTANDER_BRUISES_NOT_ITS_PAWN

Split from HARNESS_REPAIR_CAUSE_4D2C5B87_3. That item's swept fault (SITE, fixed at 9f434a10d1) and this one share
only the normalized cause signature `surprise: safe_advance stopped ... hurt: health # -> #; newest`.

## spec

- Sighting: testq job `J20261124T124826Z-321546` (FlowWorks, Steve1, runner e29c59c404). The row
  `plot_H_depth_ladder/pawn_height_ladder_look` read UNMEASURED: `safe_advance stopped after 120 of 200 tick(s): hurt:
  health 1 -> 0.91; newest hediff Bruise/Torso age 60`. Its two sibling rows were held by the same stop.
- Sheet: SteveDesktop `~/rm/runner/Transient/modcheck/FlowWorks_20261124T130616Z.json`,
  `summary.chains[1].components[1].surprises`. The stop has two triggers on the same tick 16992: Burgess (19141)
  `Bruise/Torso` and Buddy (19260) `Bruise/Hand`. The chain's own pawn is Human19283 (from `order_pawn`), so both hurt
  pawns are bystanders.
- `superdeepCaptureEnabled` is OFF in this block, so the pit fall path (`RM_SuperdeepTrapState.Tick`) cannot have
  dealt the Blunt damage.
- FlowWorks chains do not call `helpers.settle_bystanders`. LeaningScrub and Cauldron do. So the site's colonists roam
  free during the chain. A vanilla social fight between two of them is the lead hypothesis [guess ~60%]. It is not
  measured.

## classify

Decide the class first, from a reading:
- SITE: a vanilla event among the bystanders (social fight, animal). Fix the staging: settle or draft the bystanders
  for this chain. Do not change the check.
- MOD: FlowWorks hurt the bystanders. File the finding on the mod.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = a FlowWorks testq job that names `plot_H_depth_ladder`, run after the fix, has rows with a verdict, and no row
carries the cause:

    python3 src/RimMandrake/Utils/testq/retest.py passed-since FlowWorks plot_H_depth_ladder 2026-11-25T09:55:00Z HARNESS_REPAIR_CAUSE_4D2C5B87_3

Negative control: `retest.py passed J20261124T124826Z-321546 HARNESS_REPAIR_CAUSE_4D2C5B87_3` exits 1, before and
after the fix.

## forbidden

- heal: no retry or auto-restart that turns the stop into a pass without removing its cause.
- drop the check: no row, chain or `retest.CAUSES` pattern removed; no blanket declaration of bystander hurts.

## criteria

- the class is recorded on this item with its evidence before the fix;
- the verify command exits 0 on a job run at the fix's sha;
- the negative control exits 1.

## refs

file: src/RimMandrake/FlowWorks/northstar/extensions.py
file: src/RimMandrake/Utils/modcheck/helpers.py
