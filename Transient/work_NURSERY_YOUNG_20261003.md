# MIASMA_FREE_NURSERY_YOUNG_1 work log (2026-10-03)
Started. Choices recorded below.
## Choices
- Defs added to TerminalBiomes' RM_SeaBeasts_Invented.xml (the adults live there; Miasma already depends on terminalbiomes): REQUIRES a file outside the Miasma folder. Added `Name=` to the four adult ThingDefs/PawnKindDefs so juvs can parent them (same as SiltLamprey/RustNipper).
- Four juvs RM_{CrimsonOpee,ThornbackColo,ShaleGorger,Reefback}Juv: Baby/Juvenile locked lifeStageAges, adult's texPath, drawSize 0.5x/0.75x of adult stage 0. No new art, none queued. Invented names -> RM_ tier, no Utinni involvement. Life stage moving between biomes: the allowed multi-home reason.
- Weights // INVENTED: 0.25 each, Reefback 0.15 (colossus). Added to RM_Miasma wildAnimals, strandedSpawnList, and creche youngKinds.
- No C#, no build, no new settings toggle (content rows, not a feature).
## Proof
- validation.py static PASS (new checks); validate_patch 0 errors on 3 files.
- Live criteria (get_defs foundCount 4; free-tier recede strands a new young) UNMEASURED; suite chain nursery_young_free_tier reports it.
