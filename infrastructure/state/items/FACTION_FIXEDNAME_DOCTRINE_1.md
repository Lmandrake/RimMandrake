## spec
BUILD, 2026-08-20. Ten factions in the live world wear generated names; the
repair is filed as `FACTION_NAMES_ARE_GENERATED_1` in `queue/CHECK.md` and needs
no def change — clearing the stored name makes each fall through to its
`def.LabelCap`, which is already correct.
⇒ **The repair is settled. This item is only about RECURRENCE.**
`FACTION_SPEC.md:71` says `fixedName` is for *"only where the world must say a
specific name"* — a deliberate restraint, and BUILD is not overriding it
unilaterally. But the evidence is now in: **without `fixedName`, a newly
generated world names these factions at random**, and this one did.
THE QUESTION: does the restraint survive that? Two readings, both defensible:
  (a) **Add `fixedName` to all ten.** The campaign names these factions
      everywhere; a generated name is never wanted. Costs ten one-line patches.
  (b) **Leave the defs alone.** The world is generated ONCE and then frozen, so
      a repair-after-generation is sufficient and the restraint stands. Costs
      nothing now, and costs the same repair again if the world is ever rebuilt.
⚠️ `FACTION_SPEC.md:124` is relevant and easy to miss: *"Do NOT patch
`factionNameMaker` away — `fixedName` overrides it for the faction, and the namer
is still used for settlements."* So (a) is safe for settlement naming.
⚠️ One nuance either way: `def.LabelCap` capitalises, so `the Junkers` presents as
**"The Junkers"**. If the lower-case article is wanted, that faction needs an
explicit name regardless of which reading wins.

## verify
whichever is chosen, written into `FACTION_SPEC.md` beside the existing
`fixedName` line so the next reader is not left with the bare restraint.

## criteria
—

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE
