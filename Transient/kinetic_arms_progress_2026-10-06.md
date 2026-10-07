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
