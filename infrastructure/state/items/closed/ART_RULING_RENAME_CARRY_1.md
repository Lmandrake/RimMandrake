# ART_RULING_RENAME_CARRY_1 — an owner's art ruling does not follow a creature when its def is renamed or its art is copied

**Incident (Contagion sheet 2026-10-05).** The owner asked, verbatim: "Not again! Where's the ikee art I had before? I liked it! Why do you keep changing the ikee art?"
- 2026-09-29: on the contagion cast sheet he ruled RM_Ikee "regen", with the note "ERROR! We liked the Ikee from before! … This thing is hideous." That rejected the new render `RM_Ikee_*`.
- `63a75d429` (09-28) restored the liked render, but into the Stillsand `RM_Ikee` folder.
- `0aff70110` (09-29, CONTAGION_RULED_CONTENT_1 Wave A) renamed the Contagion ikee to RM_ContagionIkee and filled its NEW folder with the rejected render from `_artsrc`, calling it "already generated and validated".
- `ef1a9f4c4` copied the same rejected render onto RM_Ogleknot.
- He purged `0ccc49cd…` on the deep_desert sheet. The purge was refused as "live elsewhere": those bytes are live as Ogleknot, which he kept as A tonight.
- Fixed tonight: RM_ContagionIkee is restored to the liked render (east 0a52fabd2e89, north f124c52df712, south a336837e6bad, the same bytes as RSW_Ikee) by `art install --ruling`.

**Why no guard refused.** The overwrite predates the art ledger (2026-10-04), so the guard never saw it. Three gaps remain open today:
1. A ruling is bound to a subject or texPath. A def rename or a new def for the same creature starts with no protection and no history.
2. A "regen" / rejected verdict does not mark the rejected bytes as rejected. Copying those bytes onto another subject or path is a mechanical install like any other.
3. When a purge is refused because the bytes are live elsewhere, nobody is told which slot holds a picture he rejected under another name.

4. `artledger.retire(owner_said=…)` cannot pass `art_guard`. With no reason it records "retire", which the guard calls unrecognised. With a `script:` reason, the guard refuses it for displacing a kept picture. So a kept picture can never be removed, even on his words. Hit 2026-10-05: the Contagion copies of RM_Shambles were left in place after the def moved to TheRot.

NEXT: make `art install`/the guard refuse (or flag) installing bytes that an owner ruling rejected for any subject, and carry rulings across a def rename via a subject alias.
