# TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE — build log (BENCH AFK subagent, 2026-10-17)

## 1. Search for existing mechanics
- No animal-in-building / brine vat existed. Reused the Kolto tank shape (src/RimStarWars/Armoury/Source/KoltoTank/:
  Building_Casket + CompRefuelable + carry float-menu + job) and the shared RM_MechanicGates seam
  (RM_GenStep_PlacedSetPieces.ShouldSkipMap already reads an RM_MechanicGateExtension) for the nest switch.
- White look: vanilla PawnKindDef.alternateGraphics at chance 0 + Harmony postfix on PawnGraphicUtils.TryGetAlternate
  (decompiled: the alternate is seeded per thingIDNumber; pawns have no override field).

## 2. Design
- RSW_TaozinBrineTank (SWBestiary, MayRequire cuisine+stillsand): holds 1 tame grub, suspended; RM_Brine is fuel;
  each jar (2 days, setting) spends 1 brine -> 1 RSW_TaozinBrine beside the tank. Grub soak clock only runs while working.
- Grub comp RSW_CompTaozinBrining: brined ticks; >= 15 days (setting) -> pale for good.
- Settings (beast mechanics): taozinBrineTankEnabled, taozinDaysPerJar, taozinPaleDays, taozinNestEnabled (gate RSW.TaozinNest).

## 3. Build
- Built clean: RimMandrakeBeastMechanicsRSW.dll (0 errors, 0 CS warnings).

## 4. Review / selftests / validation row
(pending)

## 5. Owed
(pending)
