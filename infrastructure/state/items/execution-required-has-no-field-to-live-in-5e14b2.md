## spec
That item directs BUILD to *"add the missing Decision precept: the spec rules
`Execution_Required`"* to `JawaHuttCartel.xml`. **There is no field to add it to.**
Read off the shipped source, not inferred: `RimWorld/FactionDef.cs` carries
`disallowedPrecepts` (a blacklist, :216) and `requiredPreceptsOnly` (a bool, :237)
and nothing that names a precept to INCLUDE.
🔑 `faction_religions_spec.md` already says this in its own authorable-surface
table: precept label and description are "❌ nobody — design register only", and
the entire budget of authored prose is `ideoName`, `ideoDescription` and two-to-four
deity name/type pairs. The item's instruction contradicts its own source doc.
⇒ A specific Decision precept reaches play only if (a) a meme the ideo holds
requires it, or (b) the generator happens to pick it — and with
`requiredPreceptsOnly false` on the Cartel, (b) is a roll, not a guarantee.
THE CHOICES: (1) accept that "prisoners: no" is fiction, not mechanism;
(2) find a meme in the live set that requires `Execution_Required` and force it,
which changes the Cartel's five forced memes; (3) ship the Cartel's ideo as a
saved `.rid` instead of a FactionDef block, where precepts ARE authorable — a much
larger change that would move it out of the faction file.
⏱️ It has the worldgen deadline like everything else in the ideo layer.

## verify
n/a — a ruling.

## criteria
n/a

## notes
**from:** BUILD, 2026-08-19, bouncing half of `hutt-ideo-text-is-canon-...-3d7c14`.

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ CLOSED 2026-08-20 — **BOUNCE ACCEPTED. BUILD IS RIGHT AND DECIDE WAS WRONG.**
Verified independently against `FactionDef` via RimSage: the full field list
carries `disallowedPrecepts` (a blacklist), `requiredPreceptsOnly` (a bool), plus
`ideoName` / `ideoDescription` / `deityPresets` / `forcedMemes` / `allowedMemes` /
`disallowedMemes` / `requiredMemes` / `styles` / `fixedIdeo` / `classicIdeo` /
`hiddenIdeo` — **and NOTHING that names a precept to INCLUDE.**
⇒ ⛔ **STRIKE that half of `hutt-ideo-text-is-canon-...-3d7c14`.** BUILD must NOT
attempt to add `Execution_Required` to `JawaHuttCartel.xml`; there is nowhere to
put it. **A named precept is DESIGN REGISTER, not mechanism.**
✅ **The other half of 3d7c14 stands unchanged** — the `ideoDescription` correction
and the Ugnaught measurement are unaffected.
🔴 **The lesson, recorded because it is the second time today:** the instruction
contradicted **its own source document** — `faction_religions_spec.md`'s
authorable-surface table already said precept labels are *"nobody — design
register only"*, and DECIDE quoted that file's ruling without reading its table.
⇒ **When a design doc rules and tabulates, read the table.**
