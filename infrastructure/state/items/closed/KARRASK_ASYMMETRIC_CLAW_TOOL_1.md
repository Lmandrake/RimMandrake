## spec
Found by a code-review pass (2026-09-04) while marking
`src/RimStarWars/Livestock/Defs/ThingDefs_Animals/ThingDefs_Karrask.xml`
clean. `RSW_Karrask` (a `QuadrupedAnimalWithPawsAndTail`) defines a
`<tools>` list with a `foreclaw` tool linked to `FrontLeftPaw` only — there
is no matching tool for `FrontRightPaw`. Sibling creature `Cindermare`
(`src/RimStarWars/.../ThingDefs_ForsakenCrags.xml`, same body type) defines
symmetric left+right claw tools, which is the pattern to match. As shipped,
the karrask's right forepaw has no attack tool at all — reads as an
authoring oversight (a copy-paste that only got the left side) rather than
a deliberate asymmetric-creature design choice, but nobody has confirmed
that with the owner.

## verify
- Compare the karrask's `<tools>` list against Cindermare's (or another
  `QuadrupedAnimalWithPawsAndTail` in this repo) side-by-side.
- If it's confirmed an oversight: add the missing `FrontRightPaw` foreclaw
  tool, mirroring the left one's `power`/`cooldownTime`/`capacities`.
- If the owner confirms it's deliberate (a wild guess with no evidence
  either way right now): leave as-is, but note WHY in a comment so the next
  reviewer doesn't re-flag it.

## criteria
- The karrask's melee tool list is symmetric like its body-type siblings,
  OR there's a recorded reason it isn't.
