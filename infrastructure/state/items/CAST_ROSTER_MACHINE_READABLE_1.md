## spec
⚠️ **The blocker nobody has looked at.** The eleven cast files hold 269 authored
characters as PROSE. Measured 2026-08-20:
  present on every entry: name · race (a prose string, not a def) · gender
    (`m`/`f`/`none`/`f-presenting`) · age (int) · `traits:` (REAL `TraitDef`
    names, some with degree, e.g. `NaturalMood(Sanguine)`,
    `DrugDesire(ChemicalFascination)`) · `childhood:` · `adult:` · `hook:`
  absent from ALL of them: xenotype · pawnKind · faction defName · apparel ·
    skills. Weapons and genes appear only incidentally inside prose.
  ⚠️ `INHABITED_CAST_DROIDS.md` uses DIFFERENT FIELDS by owner ruling — `chassis`
    replaces race and `service-years` replaces age. Handle it, do not normalise
    it away.
Write `src/RimMandrake/Utils/cast_to_xml.py`: parse the eleven files into
`src/Jawa/Inhabited/Defs/CastRoster_<FACTION>.xml`, one `<Inhabited.CharacterDef>`
per character, carrying the authored fields verbatim plus the parsed `traits` as
real defNames.
🔴 **DECIDE owes you the four fields the prose does not carry** — xenotype,
pawnKind, apparel and skills. They are filed as `INHABITED_OPEN_QUESTIONS_1` in
`queue/DECIDE.md`. ⇒ **Build the parser and the def for what EXISTS now**; leave
those four fields optional and empty. Do not invent values for them — a guessed
xenotype ships a wrong-looking person into a frozen world.
⚠️ **The twelfth faction has no cast file.** Deepwater Compact (*the Balance*) is
tabled at `INHABITED_DESIGN.md:485-497` but has no `INHABITED_CAST_*.md`. That is
DECIDE's authoring debt, not a parser bug. Make the tool skip it cleanly.

## verify
the parser emits 269 `CharacterDef`s across 11 files, and
`python3 skills/rimworld-modding/scripts/validate_patch.py` reports every
`traits` entry resolving to a live `TraitDef`. A trait that does not resolve is
the ONE thing here that must fail loudly.

## criteria
the defs load with 0 red errors, and a named character from the roster can be
spawned by defName through the bridge.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20, `2cbb3ed` + `fca27b6`. `src/RimMandrake/Utils/cast_to_xml.py`
-> `src/Jawa/Inhabited/Defs/CastRosters/CastRoster_<FACTION>.xml`.
verify output:
  `269 characters across 11 files`
  `every trait and degree resolved against the dump.`  (807 traits, 0 failures)
  25 each except HUTT 19; 269 unique defNames, 0 collisions; all 11 files parse.
🔴 **ONE MEASUREMENT IN THE SPEC IS WRONG AND IT MATTERED.** *"present on every
entry: … age (int)"* — it is not. Eleven files write age EIGHT ways:
  `101` · `~90` · `60ish` · `300+` · `312 service-years` ·
  `61 years since activation` / `since assembly` / `since salvage` ·
  `six hems (33)` — the Jawa count age in robe-hems, years in the gloss ·
  `claims 40,000; is 90` — a droid who lies about his age ·
  `unknown` — authored deliberately, on 5 people
🔑 **The last integer in the string is the right answer in all eight**, including
the two that look like exceptions, because a writer puts the real number last and
the clause before it is the flavour. ⛔ **The verbatim text is kept on the def as
`ageText` regardless** — "six hems" IS the characterisation and reducing it to 33
throws the interesting half away.
⛔ xenotype, pawnKind, apparel and skills are emitted EMPTY and were not guessed.
⚠️ Deepwater Compact is reported as missing, cleanly, every run. Authoring debt.
⭐ **Beyond the item, because its own criteria needed it:** `CharacterApplier`
turns a generated pawn into an authored person — NAME and TRAITS, nothing else —
and a debug action spawns any of the 269 by name. Traits are REPLACED rather than
added, because a character written `Ascetic` who also rolled `Greedy` is a hook
the mechanics do not back. `InhabitedCastDef.characters` wires them into a cast,
and a pawn drawn from the displaced pool is never overwritten.
Live half filed to CHECK as `CAST_ROSTER_269_LOAD_1`.
