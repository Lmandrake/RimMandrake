## spec
`faction_religions_spec.md` has eleven entries and says section 12, the Jawa, is
**deliberately empty** because the player faith ships as
`src/Jawa/ideoligion/The Salvation.rid`. But
`src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` (`Jawa_IndigenousTribes`,
label "Jawa Trade Moot") carries `<ideoName>The Salvation</ideoName>` with
`fixedIdeo true` and five `forcedMemes`, and no `ideoDescription`.
It reads as deliberate — the Trade Moot is Jawa, so it wearing the Jawa faith is
coherent, and `fixedIdeo` stops worldgen rolling a random faith over an NPC
faction we care about. But **the twelfth faith is the one the spec explicitly
declined to author**, so this is authored content with no ruling behind it and no
description text.
⇒ (a) confirm the Trade Moot keeps The Salvation, and give it an
`ideoDescription`; or (b) give it its own faith; or (c) strip the block and let
worldgen roll one.
🔑 It has the same hard deadline as the rest of B54: an ideo is generated once,
at world creation.
FIXED already, needing no ruling: three of the five memes are modded
(`sarg.alphamemes`, `vanillaexpanded.vmemese`) and carried no `MayRequire`.
They do now.

## verify
n/a — a ruling, not a build.

## criteria
n/a

## notes
**from:** BUILD, 2026-08-19, auditing B54. Not a defect that stops anything — a call that
nobody has made in writing.

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

ANSWERED AND BUILT 2026-08-19 - no ruling needed. Owner, in his own words:
*"We DID author a document describing the Jawa faith, and yes both the Trade Moot
and the player faction should share it."*
The document is `design/Jawa/worldbuilding/ideoligion/the_salvation_description.md`
and it had reached NEITHER artifact - the `.rid` was still carrying RimWorld's
stock generated blurb. Both carry the authored text now, byte-identical:
`JawaTribes.xml` `<ideoDescription>`, and `The Salvation.rid` `<description>` AND
`<descriptionTemplate>` (a mismatch between those two makes the in-game editor
re-roll the text). 2,374 characters, verified equal all three ways.
The nine gods live in the description because they have nowhere else to live:
`AM_Structure_Scavenger` is `deityCount 0` and cannot seat a deity.
