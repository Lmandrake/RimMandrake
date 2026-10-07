# Kinetic Arms build progress — 2026-10-06

Item: KINETIC_BLAST_WEAPONS_1. Relaunch after previous attempt died (OOM from /tmp clone).

## Milestones
- design §10 build-v1 addendum written (EK untouched; per-weapon DamageDefs; back-step cone bolts)
- 8e68f9e5e design addendum pushed
- mod built: defs (8 weapons + thump patch), C# (bolt/kicker/pulse/settings/proof), DLL+srchash via winbuild; validate_patch 0 errors; kernel 13/13; validation STATIC+MOCK pass; repo selftests 207/212 (5 fails in FlowWorks/UtinniPatches/rimflow/art-flaky, none Kinetic)
- 65b0565a9 mod pushed
- art: 16 kba_ sprites collected via art ledger into KineticArms/Textures; projectile art points east so RM_Projectile_KineticExplosive rotates draw -90; kba_icon_PulseCannon (failed) re-filed as kba_icon_PulseCannon_r2

## 2026-10-06 rulings
Card 23:28. (1) Factions, owner typed: "Mostly ruins only, but rare on raids that stole it from said ruins (pirates/outlaws)".
(2) Throw cap: decision taken by question card — "Let each weapon set it" (per-weapon/DamageDef max throw; others keep the global 6).
- started: reading EK kernel + settings
- EK: RM_KnockbackExtension.maxThrowCells (0=global) + setting 'Weapons that set their own maximum' scale; kernel CapFor; kernel 63/63, STATIC+MOCK pass, DLL built
- KA: per-weapon maxThrowCells on the 8 DamageDefs + Thump 8; grav_ram proof min 5->7; KA kernel 13/13, STATIC+MOCK pass, validate_patch 0 errors
- factions: RM_KineticLooterExtension patched on FactionDef Pirate (inherited by CannibalPirate/PirateYttakin/PirateWaster); Harmony postfix on PawnWeaponGenerator.TryGenerateWeaponFor swaps an armed pirate's gun at 2% (setting); kernel KA-14 (21/21), proof scene looted_pirates, walk line
- rulings recorded on item (rimflow note x2); design §1/§2/§3.2/§4/§5/§7/§9/§10 updated
- outlaws: Junkers+Blackstar inherit Pirate marker; Hutt via Utinni patch KineticArms_OutlawLooters.xml; lootMoneyFloor 300 Junkers; 1000 raider ceiling (kernel KA-15); DLL rebuilt

## 2026-10-07 ruins + tier
- started: found ruins loot already wired at 53186050e (vanilla MapGen_AncientTempleContents, uniform pick); remaining: rarity tiers, other ruin sources, test tier, item prose
- 111ac3588 rarity tiers (RuinsWeights 30/20/15/10/12/15/5/3, grav-ram rarest) + RM_ThingSetMaker_KineticComplex on 3 ancient-complex tables, toggle foundInComplexes; kernel 49/49, STATIC+MOCK pass, DLL rebuilt
- kineticarms tier added to modset_builder.py (13 mods, all 5 DLC; plan only, not applied)
- deployed KineticArms (3 files VERIFIED); selftests 220/222 (fails: rimflow items_glob_live, UtinniPatches dump - not Kinetic); item prose + rimflow note
