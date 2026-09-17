# NORTH_STAR_WALK_AUTHORING_1 — visual bars for the walks that have none

**MEASURED 2026-09-17:** 78 validation walks (28 RimMandrake, 23 RimStarWars, 27
RimUtinni). **4 VALIDATED** (Pits, Graffiti, WreckedMachines, FlowWorks) · **2 DRAFT**
(Oracle, AtmosphericBase) · **72 carry no `## north star` section at all.** The item's
original text said 77; 72 is the unauthored count.

## 🔴 Owner ruling, 2026-09-17 — triage on visual surface BEFORE authoring anything

Asked where the 72 walks' `### must show` lines should come from, he chose:
**only mods with real visual surface get bars.** A mod that ships textures, terrain,
pawns or effects gets a checklist; a pure code or mechanics mod gets none.

Why it was asked, and why this answer: **validating a north star creates a refusal.**
FlowWorks ships zero textures, so validating its 16 bars made it fail the visual floor
from that moment. Authoring all 72 would mostly manufacture refusals against mods a
visual floor cannot judge.

⛔ The item's original ask — *"agent drafts candidate lines from each walk's must-be-true
plus sprites and settings"* — is NOT authorised by this ruling. All four validated walks
distilled their bars from a **verbatim paragraph the owner dictated**, and
`north_star_validation_spec.md` requires each line to name the phrase of his it came from
and add no claim of its own. Drafting from mechanical assertions is a different
provenance rule and was not adopted. **Provenance for the surviving set is still an open
question** — put it to him once the set is small.

## 🔴 Owner ruling 2, 2026-09-17 — the walk documents are repaired BEFORE any line is authored

Triage done (step 1 below): **32 bar owed · 38 no bar · 2 uncertain = 72**, independently
re-measured by BENCH, not taken from the subagent.

It surfaced a defect the spec did not anticipate: **25 of the 72 `subject:` paths name folders
that no longer exist** (MEASURED twice — subagent census and BENCH's own count). Two reorg
waves absorbed those mods into larger ones (`485380d4` "Sprint wave A"; SWBestiary's
`MECHANICAL_FAUNA_MERGE_WAVE_A`), so the walk describes a feature now living as a subfolder of
an unrelated mod. It hits **roughly half the bar-owed 32**. Separately, **three pairs of walks
now describe the same single PNG** from two files: BeastLairs/StructureInjectionsSW,
DesertFixtures/StructureInjectionsRUT, UtinniShell/MenuShell.

Offered the choice of starting on the four biggest art mods anyway (3,426 PNGs, all paths
valid), he chose the opposite: **finish all document cleanup first — repoint the vanished
subjects AND resolve the duplicate-image ownership — then author.** His reason follows his
standing cost principle: authoring once against accurate documents beats authoring twice.

⛔ Therefore no `### must show` line is written until steps 2 and 3 below are done and the
provenance question (step 4) is answered.

## spec

1. ✅ **DONE 2026-09-17.** Triage all 72 on visual surface only, from what each mod actually
   ships rather than what its prose claims. `uncertain` was a respected verdict; 2 landed
   there — AshkarrFlora (15 PNGs in an `_artsrc/` scratch dir, ThingDef `texPath` resolves to
   nothing, so a flora mod ships no art) and RiverSteam (now inside the already-VALIDATED
   FlowWorks under another name, so arguably not a separate walk at all).
2. **Repoint the 25 vanished `subject:` paths** at where the content actually lives now.
   Verify each successor exists on disk before writing it; never guess a path.
3. **Resolve the 3 duplicate-PNG pairs** — decide which walk owns the shared asset, so two
   checklists cannot make competing demands on one image.
4. **Ask him the provenance question** on the surviving set (dictate-and-distil, mine his
   existing rulings, or something else). All four VALIDATED walks distilled from a verbatim
   paragraph he dictated; drafting from mechanical assertions was explicitly not authorised.
5. Author in batches by visual family, largest visual surface first, once 2-4 are settled;
   he reacts rather than composes.

## verify

Triage covers exactly the 72 walks with no `## north star` section — no walk silently
dropped, and the 6 already-authored walks untouched. Counts stated MEASURED. No
`### must show` line written anywhere until step 4 is answered.

⛔ Do not touch the `## north star` sections of Pits, Graffiti, WreckedMachines or
FlowWorks: the recorded hash covers the whole section including prose, so any edit
silently reverts his validation.
