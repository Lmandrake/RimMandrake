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
- Fuzz family `brine` added (BestiaryFuzz.cs): run_selftests --only selftest_swbestiary.py selftest_swbestiary_fuzz.py GREEN 2/2.
- validation.py: STATIC PASS; new chain taozin_brine_tank_infuses_and_whitens (live, via RSW_BeastMechanicsProof.ProofBrineTank);
  toggles list now names the 4 taozin settings + 2 scrap-bird fields it was missing.
- Marked CLEAN: RSW_TaozinBrineTank.cs, RSW_BeastMechanicsDefOf.cs. Still DIRTY (touched, not fully reviewed):
  RSW_BeastKernel.cs, RSW_BeastMechanicsProof.cs, RSW_BeastMechanicsSettings.cs, BestiaryFuzz.cs, Program.cs.
- Committed db786f84ff, PUBLISHED 9847ab83bf.

## 5. Owed
- Deploy SWBestiary + Cuisine (game up; FOUNDRY holds bridge) - also carries the earlier taozin-split deploy.
- Live row SWBestiary taozin_brine_tank_infuses_and_whitens; the colonist carry job is unproven live.
- White art taozin_split_grub_brined_v1 to install (texPath Things/Pawn/Animal/RSW_TaozinGrub/RSW_TaozinGrub_Brined).
- Tank art: placeholder vanilla FermentingBarrel tinted; an art job is owed (cosmetic - owner permission).
- Concurrent: another BENCH helper is adding albinoDragonsnakeEnabled to the same settings file/csproj (DRAGONSNAKE_PAIR_*).
