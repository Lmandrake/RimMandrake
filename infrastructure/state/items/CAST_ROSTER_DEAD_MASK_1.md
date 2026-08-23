## spec
Two `Inhabited` cast characters list a dead def under `<apparel>`, and the obvious
one-word fix is ALSO wrong. Both halves measured 2026-08-23 by CHECK, game DOWN.

    src/Jawa/Inhabited/Defs/CastRosters/CastRoster_HELIX.xml:479    <li>guy762_KelDorMask</li>
    src/Jawa/Inhabited/Defs/CastRosters/CastRoster_JUNKERS.xml:175  <li>guy762_KelDorMask</li>

**① The def does not exist in the running game.** `guy762.StarWarsXenotypes` was
deliberately switched OFF and consolidated into `mandrake.starwarsraces` — `C36`, and
`infrastructure/state/canon.yml:829`. The consolidation missed these two lines.
- live log, 578 mods: 2x `Could not resolve cross-reference to Verse.ThingDef named guy762_KelDorMask (wanter=apparel)`
- `measure get guy762_KelDorMask` -> `UNMEASURED — no def with this name in the capture`
  (`defs.sqlite mods=578/9a204707f6dc183d captured=2026-08-21T22:44:59Z`; ThingDef itself is
  MEASURED at 24904, so the type is complete and the absence is real)
- `grep` over every installed mod finds it in exactly one place on disk:
  `…/workshop/content/294100/2915192253/1.6/Defs/GeneDefs/GeneDefs_HeadAttachments.xml`
  — the retired mod. **⇒ two authored characters silently lose that item at spawn.**

**② ⛔ Renaming it to `RimMandrake_KelDorMask` would NOT fix it.** The successor exists and
loads — `measure get` returns `MEASURED 1 RimMandrake_KelDorMask (ThingDef 'Kel Dor breath
mask' from RimMandrake - Star Wars Races)` — but it is **not apparel**. It is
`<ThingDef ParentName="ResourceBase">` at `src/Jawa/RimMandrake_StarWarsRaces/Defs/Misc/SW_Support.xml:566-569`
and its own description reads: *"NOTE: This is not an apparel item! This can only be applied
to a pawn with a simple surgery!"* A rename resolves the cross-reference and then fails to
equip — trading a loud error for a silent one.

## fix — BUILD, but the choice is DECIDE's
The mask is worn as a GENE, not as apparel:
`RimMandrake_HeadAttachment_keldormask` (`…/Defs/GeneDefs/SW_Genes.xml:1569`), which applies
`RimMandrake_GeneHediff_keldormask` (`…/Defs/Misc/SW_Support.xml:277`) and spawns the item on
removal. So either:
  (a) drop the `<apparel>` line from both characters, or
  (b) give those two characters the gene instead — which is what "wearing a Kel Dor mask"
      actually is in this stack.
⚠️ Whether the cast format can express a gene at all is a `cast_to_xml.py` question, not
just an XML edit — `apparel:`, `item:`, `weapon:` and `skills:` are the four fields it
parses, and none of them is a gene.

## criteria
Next cold load: **0** occurrences of `Could not resolve cross-reference to Verse.ThingDef
named guy762_KelDorMask` (currently 2), AND the two characters visibly carry or wear the
mask — not merely a clean log, which dropping the line alone would also produce.

## Watch out
- 🔑 **`ThingDef` names in the cast rosters are NOT validated by the generator, on purpose**
  — `src/RimMandrake/Utils/cast_to_xml.py:48-52` says so. That is why this survived. Its
  stated reason has now been corrected in place (see the commit); the deliberate
  non-validation is a real decision, but it means a dead name here is only ever caught by
  reading a load log.
- ⚠️ **A whole-word grep is mandatory when auditing this class of thing.** A substring sweep
  of the retired mod's 364 defNames against `src/` appeared to show **79** dead references;
  with `grep -w` it is **25**, of which **21 are prose in comments and About.xml**, **2 are
  `<graphicPath>` filename fragments under `RimMandrakeSW/`**, and only **these 2** are live
  def references. The prefixed forks (`RimMandrake_KoTOR_NamerJawa` contains
  `KoTOR_NamerJawa`) generate the entire false positive.
- ✅ Cleared while here: `Jawa_Patches/About/About.xml:69` lists `guy762.StarWarsXenotypes`
  under `<loadAfter>`, which is harmless when the mod is absent, and every other
  `guy762_Eyes_*` / `guy762_xenotype_*` mention in our XML is inside a comment.
