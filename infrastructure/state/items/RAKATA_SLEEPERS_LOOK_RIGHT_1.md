## spec
Six ancient pawn kinds now force `RimMandrakeRakata` at 1.0 with
`useFactionXenotypes false`, so every sleeper thawed out of a cryptosleep casket
looks Rakatan instead of like an ordinary human.
🔴 **DO NOT VERIFY THIS FROM THE LOG.** `PatchOperationFindMod` returns **true on
no match**, so a clean log proves the guard ran and never that the patch landed.

## verify
off the NEXT def dump, `AncientSoldier` and `AncientSoldier_Leader` read
`xenotypeChances` containing exactly `RimMandrakeRakata: 1.0` and
`useFactionXenotypes: false`. ⚠️ The four `Ancient urban ruins` kinds too, if that
mod is still active.

## criteria
🔴 **CRACK A CASKET AND LOOK.** The pawn is visibly Rakatan, its inspect pane
reads **"Forsaken soldier"**, and its bio/gene tab reads **"Rakata"** — both, and
they are supposed to differ: the exonym is what our people call them, the endonym
is what they call themselves.
🔴 **AND THE ENCOUNTER MUST PLAY EXACTLY AS BEFORE.** Same spawn count, same gear,
same difficulty. This is an appearance change and nothing else; report any
behavioural difference as a defect.
⚠️ Watch for the Avaloi: `det.avaloi` injects `DV_Avaloi` into the `Ancients` and
`AncientsHostile` faction sets at 0.15/0.10, so roughly one sleeper in ten used to
generate as an Avaloi. **Zero Avaloi sleepers now** is part of the pass.

## notes
**from:** BUILD, 2026-08-20. `AncientsAreRakata.xml` is written, validated and deployed.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
