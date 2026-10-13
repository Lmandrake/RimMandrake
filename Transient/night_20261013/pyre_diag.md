# Pyrelands diag (offline, 2026-10-13 night)

## 1 PYRE_ANIMALS_DIAGNOSE_TEN_IS_NOT_TWELVE -> SITE (mapgen roll variance) + HARNESS (bar is empirical)
- Biome RM_Pyrelands animalDensity 2.1; roster = 8 inline RM_ + 7 RSW_ patch-added (WildAnimals_Pyrelands.xml); map 250x250.
- The `>=12` bar in validation.py (animal_census) has no source in design/; it is an observed floor.
- Totals over 10 fresh-site censuses: 10(p8a: 9 Gizka+1 Flamefang),14,14,15,16,16,16,16,18,22. Vanilla GenStep_Animals
  fills by wildlife POINTS (herds of random kinds), so a roll of tiny Gizka + one heavy Flamefang gives few bodies.
  Count is therefore a poor instrument; 1 in 10 under 12 is expected variance, not a MOD defect.
- Site builder does not remove animals: it abandons only the quicktest colony settlement (northstar_site.py ~L339); wild animals on the fresh map are untouched. (Not live-proven.)
- Pre-mapgen-season hypothesis: not distinguishable offline; the 20261013b count (10) sits inside the prior range.
- No code change: loosening a bar without owner/spec is a ruling. Proposed: bar on distinct kinds + biome_probe roster (already checked) and demote count to a >=8 floor, or re-roll once.
- Live check (minutes): 3 fresh 250x250 map gens on RM_Pyrelands, read `animal census` each (~90 s each); if min >=12 over 3 and p8a stays the outlier, close as variance.

## 2 PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE -> MOD (think-tree priority race), harness-visible
- Dive = RM_JobGiver_BurrowOnFire, inserted at Animal_PreWander (prio 56) in the MAIN animal tree.
- Vanilla Animal tree order: ... AnimalConstant runs FIRST on a constant-think pass: `JobGiver_AnimalFlee` ("Flee enemies, tornados,
  meteorites, etc.") preempts anything in the main tree, and its follow-up is Wait/Wait_Wander. Failing samples:
  p5 [ShadeDash,ShadeDash,Flee x5,Wait x8]; p7 [GotoWander,Wait_Wander,...,Flee x3,Wait_Wander...,Wait_MaintainPosture] -- never RM_Burrow.
  Passing samples: [GotoWander,GotoWander,RM_Burrow], [ShadeDash,ShadeDash,RM_Burrow] -- giver won before Flee triggered.
- So whether Burrow or Flee wins is a race between BurnLine measure (<=60 ticks) + a think pass, and AnimalFlee's danger test. When Flee wins, the
  pawn is stuck in Flee/Wait and burrow is only reached when those end (cooldown/short window 1500 ticks was not enough, p5 8 Waits).
- Not fixable offline with confidence: a fix is C# (host the burrow giver ahead of AnimalFlee, e.g. Harmony prefix on JobGiver_AnimalFlee.TryGiveJob
  returning null for burrow-extension pawns when FireIsNear and burrow allowed, or accept Flee as legit and let the row wait longer).
- Live check (minutes, bridge): spawn Ashwallow, light fire; sample curJob every 10 ticks for 300 ticks (not every 100) -> confirm Flee precedes Burrow
  in failures. Control: place the grazer 13-14 cells from the fire (inside detectionRadius 15, outside AnimalFlee's danger radius): predicts Burrow every time.
  Also read JobGiver_AnimalFlee with rimsage (read_csharp_symbol) to confirm it tests fire and its radius.
