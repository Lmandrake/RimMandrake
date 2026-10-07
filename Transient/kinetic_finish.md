# Kinetic Arms + Explosive Knockback — finish pass (FOUNDRY helper, 2026-10-06)

Owner order: "fully build the Thump weaponry and the Explosive Kick mods start to finish, then build their validation plans."
Item: KINETIC_BLAST_WEAPONS_1. Mods: `mandrake.rm.kineticarms`, `mandrake.rm.explosiveknockback`.

## Gap list (design §3/§9/§10 vs src)

Already built (verified in src): all 8 weapons + projectiles + per-weapon DamageDefs with force/maxThrowCells; Thump patch
(force 2.5, cap 8); push-along-shot via RM_Projectile_KineticBolt back-step + cone (KA, not an EK field); kicker mine
(facing, re-arm fuel, reset guard); pulse cannon stored charges (Q6); pirate looters 2%; KA Mod Settings (8 toggles,
strength, thump toggle/force, kicker, pulse charges, looted); 16 kba_ sprites installed. No research/no recipes = owner ruling.

OWED:
- EK-1 lookup order projectile ThingDef -> weapon ThingDef -> DamageDef -> unpatched (whole-config, explicit 0 wins). MISSING.
- EK-2 `impactFactor` field (palm thumper 0). MISSING.
- EK-3 `immuneBodySizeOverride` (grav-ram 3.6). MISSING.
- EK-4 stun-recovery window (KbImmunity.CanLaunch, saved timestamps, setting default 120). MISSING.
- EK-5 shield absorbs throw + energy debit force x10 (Q4). MISSING.
- GSS-1 kinetic blasts do not cut cords (Q3) + KA setting "Kinetic blasts cut aerial cords" default off. MISSING.
- KA-1 ruins placement: nothing places the weapons anywhere a player finds them (no thingSetMakerTags, no ThingSetMaker
  patch). §10 calls it a Utinni patch, but Ancient Danger ruins are vanilla (MapGen_AncientTempleContents), and the RM mod
  must stand alone (Q11a) -> build an RM ThingSetMaker option in KA. MISSING.
- KA-2 settings from design §4 table not present: kicker hidden from enemies, pulse power draw, recovery window (EK),
  cords toggle, ruins toggle/chance. MISSING.
- KA-3 ring fleck art (kba_RM_Explosion_KineticRing) has no consumer; 8 kba_icon_* have none by design (no research/gizmo).
- KA-4 grav-ram uses its override (EK-3) and palm thumper impactFactor 0 (EK-2): def wiring after EK.
- VAL: both validation.py + walks need L0 for each new feature, L1/L2 owed criteria.

## Built this pass
- EK-1..5 built, kernel K-13..K-16 (88/88), DLL rebuilt, 6 new proof scenes (not run live) — published ff6330011.
- GSS-1: Patch_GenExplosion_CutSpans skips a DamageDef carrying `RM_KineticBlastExtension` (by type name); KA marks both
  families' abstract bases; KA setting "Kinetic blasts cut aerial cords" (default off) removes the marker. GSS DLL rebuilt.
- KA-1 ruins: `RM_ThingSetMaker_KineticRuins` added to vanilla MapGen_AncientTempleContents (35% PROVISIONAL, shells 5-12),
  honours per-weapon toggles at generate time; KA-16 kernel.
- KA-2 settings: ruins on/chance, kicker hidden (KnowsOfTrap postfix), pulse power draw, cords toggle.
- KA-3 ring fleck art collected via art ledger, `RM_Fleck_KineticRing`, drawn at every KA blast.
- KA-4 palm impactFactor 0, grav-ram immuneBodySizeOverride 3.6.
- 6 new KA proof scenes (not run live). KA DLL rebuilt.

## Validation plans
(pending)
