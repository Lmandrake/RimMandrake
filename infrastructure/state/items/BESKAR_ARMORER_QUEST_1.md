# BESKAR_ARMORER_QUEST_1 — the Blackstar quest to the Mandalorian armorer

## spec
Spec: `design/RimMandrake/beskar_armorer_quest_design_2026-10-09.md` (the decided design; every question ruled
2026-10-09, typed and by card). Parent: CANON_MATERIALS_BUILD_1 (its L7 removes `kotor_IngotBeskar_recipe` and
beskar mining yields; not this item).

Build, in a new mod `src/RimUtinni/BeskarArmorer` (`mandrake.rut.beskararmorer`):
- the orbital covert `RM_ArmorerCovert` (Orbit layer, gravship, permanent, map regenerated per visit) with the
  Armorer, two sworn, and `RM_ArmorerForge` (spec §2);
- route 1: releasing a captured Blackstar Mandalorian (`RUT_Jawa_Blackstar_Heavy`/`_Leader`) starts
  `RM_Quest_ArmorerDebt`, which reveals the covert (§3);
- route 2: incident-offered `RM_Quest_ImperialPrisonBreak` at the `RM_ImperialDetentionPost` site, Empire heat
  raised a lot, same reveal (§4);
- the C# seam: no bill outside her forge consumes beskar, only she works her forge, smelting beskar gives steel
  + slag (§5); heat recorded to `RM_HeatEvents` for the GM blackboard (§6); Mod Settings (§7).

## criteria
- L1 L4: owner rules the design questions (done 2026-10-09: route, orbital base, tribute, smelt yield, return
  any time, harm consequence)
- L2 L0: `validate_quest.py` is clean on both QuestScriptDefs, and the def/recipe generator logs no errors on a
  minimal-list load
- L3 L0: offline selftests pass for beskar mass, melt count × 0.8, the smelt replacement (steel ⌈n/3⌉ + 1
  `ChunkSlagSteel`, never beskar) and the bill ingredient gate
- L4 L1: route 1 live: releasing a captured `RUT_Jawa_Blackstar_Heavy` offers `RM_Quest_ArmorerDebt`, and after
  its delay `RM_ArmorerCovert` exists on the Orbit layer; releasing any other pawn does not
- L5 L1: the covert is reached by gravship; melting beskar pieces at `RM_ArmorerForge` returns 4/5 of their beskar
  mass, and a reforge bill there produces the chosen beskar gear; a colonist cannot start either bill
- L6 L1: no colony bench can fill a bill with beskar (Mando gear, or Metallic-stuff gear with beskar as stuff),
  and smelting a beskar item at the electric smelter yields steel + slag
- L7 L1: leaving the covert and gravshipping back regenerates the map with the same three pawns; no visit limit
- L8 L1: damaging the Armorer, a sworn guard or a covert building marks the covert lost (gone on departure, never
  re-revealed by either route), fires a Blackstar raid at once, and records max `Pirate` heat in `RM_HeatEvents`
- L9 L1: route 2 offers via `RM_BlackstarPrisonBreakOffer` (not before day 30, never while the covert is revealed
  or lost); breaking the detainee out records Large Empire heat, sends an Empire pursuit raid, and reveals the
  covert; his death or the timeout fails it
- L10 L1: each Mod Settings toggle off disables its part; the whole mod off leaves beskar smelting vanilla

## verify
Record with `rimflow verify BESKAR_ARMORER_QUEST_1 --criterion <ID> ...`.
