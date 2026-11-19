# RIMMANDRAKE_DESIGN_UTINNI_HOLY_REPAIR_AFTER_GENERIC

## spec
The owner, 2026-11-19 ~8:35 AM PST (whole quote on `RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST`): "It has a
generic possible implementation and then the Utinni-specific weaving it into the god-ship concept. ... Then the Utinni
specialization would bring in the holy aspects of repairing the work."

The Conductor's delegated call (evidence-for-ask; never his words): the Utinni specialization is a separate designed
part in the RimUtinni tier (`src/RimUtinni`, `mandrake.utinni.*`), designed after the generic RM_ WreckedMachines design
settles (its Design Version 0.1.0 locked at the Designer's Lock stage). It is not part of 0.1.0's bars, and it moves
none of them.

What it designs: the holy aspect of repair on the Jawa ship. The fiction already exists and is the input, not the
settled answer:
- `design/Jawa/worldbuilding/ship_deck_plan.md`, the SACRED SCRAP ruling of 2026-08-06 and the repair ladder;
- `design/Jawa/wrecked_machines_resurrection.md` (owner 2026-08-31 "let's resurrect that now! Fix it.");
- `src/RimMandrake/WreckedMachines/V2.md` §7 (sacred scrap: the wreck cannot be cleared) and §8 (studying the wreck),
  including the recorded trap: `deconstructible=false` also breaks the vanilla `replaceTags` repair, so sacred scrap
  and build-over must be solved together (DESIGN.md §4).

These predate the modern Designer passes (his "Needs a LOT of work using our modern Design passes"): a Designer run
reads them as input.

Route: when the generic design is locked, admit a RimUtinni-tier concept to the Maturation Pipeline the same way
(`design/concepts/<Name>/`, `maturation.py seed`, `advance --owner-said` or the Conductor's act), with its own Design
Version. Its name and packageId are the Designer's first decision; check with `rimflow namecheck` and the About.xml
naming rules.

Not before: `RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST` reaches the Lock stage.

## criteria
A RimUtinni-tier concept for holy repair exists in the Maturation Pipeline, admitted after the generic WreckedMachines
0.1.0 design is locked, and its design text names how sacred scrap and the vanilla repair path coexist.

## verify
Acceptance test: none, design work (the Designer's own stages and exam check the design text; there is nothing to run
until it is admitted).
