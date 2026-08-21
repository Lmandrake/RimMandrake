## spec
BUILD, 2026-08-20, while shipping `AncientsAreRakata.xml`. Four of the six ancient
pawn kinds were relabelled to the exonym — `Forsaken soldier`, `Forsaken captain`,
`Forsaken special unit` ×2. **Two were deliberately left alone**, because
renaming them is authoring rather than mechanics:
  `AncientMallGuards`  label today: **`"Fashion guy"`**  (combatPower 425)
  `AncientSlaughter`   label today: **`slaughter`**      (combatPower 525)
Both are from `Ancient urban ruins`, both carry `defaultFactionDef
AncientsHostile`, and **both now generate as Rakatan** — their xenotype is patched
exactly like the other four. Only the string is untouched.
⇒ So a player can currently thaw a casket and meet a Rakatan called *"Fashion
guy"*, standing next to a Rakatan called *Forsaken soldier*.
🔑 **The register rule is the constraint, not my preference:** modern people say
*the Forsaken* or *the Forgotten*; `Rakata` in a modern mouth is a scholar's word.
Anything chosen should sit inside that.
⚠️ These are the two heaviest kinds in the set, so whatever they are called is
what a player meets at the worst moment of an ancient encounter.
BUILD will ship whatever is chosen; it is four lines in a file that already
exists. ⛔ Not choosing is also a legitimate answer — the joke labels are
upstream's and there is an argument for leaving another mod's voice alone.

## verify
if renamed, `validate_patch.py --defs` stays at 0 errors.

## criteria
—

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE
