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

## done (FOUNDRY belt builder, 2026-10-04)
1. **Canonical save read** (python iterparse of `CANONICAL_ASHKARR_START_2026-09-12.rws`, `genes/xenotype` under each
   pawn): 3 pawns carry a cut xenotype — Hussar `Human62211` "Teresa" (Salvager_Elite, Faction_24, **pawnsMothballed**),
   Neanderthal `Human658908` "Anita" and `Human663663` "Lucia" (Villagers, **pawnsDead**). None is on a map or a founder;
   on load each falls back with a Scribe "Could not load reference" line, expected and harmless.
2. **Inhabited repoints** (race is prose, `CharacterDef.race`): Hesk Varo Hussar→**Echani** (combat-loving warrior
   culture whose sparring is conversation — the rib-breaking apologiser); Bo Kesh Yttakin→**Wookiee** (enormous, Hutt
   slave-hold childhood, animals as kin); Hakko Vurr→**Ortolan** (eats anything, appetite as vocation); Pell Yoon→
   **Sullustan** (warm, sociable, can't keep a secret); Yorrum Pell→**Chadra-Fan** (big-family chatter). All in the
   canon library.
3. **PawnFlavor**: the 11 `PatchOperationSequence` blocks deleted; the Odyssey and VRE-Saurid FindMod wrappers left
   empty were removed with them.
4. **Cherry Picker SHIP**: typed `XenotypeDef/<X>` for all 11 (no bare keys). The tag→surviving-item index rebuild does
   not apply (xenotypes carry no weapon/apparel tags). Live config NOT applied (it diverges from SHIP; game-down work).
5. **Sanguophage**: filed `SANGUOPHAGE_KEPT_UNREACHABLE_1` (needs owner).
Check: `src/RimUtinni/UtinniPatches/selftest_xenotype_defcut.py` (sanity probes + 4 mutants). Live half: next harvest
must show no cross-reference lines naming the eleven beyond the 3 save pawns above.
