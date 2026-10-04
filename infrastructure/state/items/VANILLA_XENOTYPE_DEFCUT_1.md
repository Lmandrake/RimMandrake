# VANILLA_XENOTYPE_DEFCUT_1 — slice 2 of the owner's 2026-10-03 "cut the twelve entirely"

Spec: the FOUNDRY cut plan section of `infrastructure/state/items/closed/VANILLA_XENOTYPE_REMOVAL_ASSESSMENT_1.md`.
Slice 1 (`ff934d915`) already removed every xenotypeSet reference, so a def cut leaves nothing dangling there.

## spec
1. Read the canonical save (`savemap.py`, never grep) for pawns carrying any of the eleven; list them.
2. Repoint the five Inhabited CharacterDefs (DrillInstructorHeskVaro: Hussar; Wildsteam BoKesh/HakkoVurr/
   PellYoon/YorrumPell: Yttakin) to Star Wars species — pick from the canon library, say why each.
3. Delete each cut xenotype's whole `PatchOperationSequence` block in
   `src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml`.
4. Cherry Picker TYPED cuts `XenotypeDef/<X>` for the eleven (never `cut_name`: `Neanderthal` is also a
   Beasts-of-the-Rim animal). Then rebuild the tag -> surviving-item index per `rimworld-content-moderation`.
5. Sanguophage: XenotypeDefOf binding — propose "unreachable, def kept" (faction/scenario/quest routes
   suppressed) to the owner; do not delete the def.

## verify
- A check that reds if any `XenotypeDef/<X>` of the eleven is absent from the Cherry Picker settings, if
  any src file still names one as a race/xenotype, or if a PawnFlavor block for a cut def remains.
- Next harvest: no Scribe/cross-reference lines naming the eleven.
