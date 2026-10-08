# Glower shielding (WARSCAR_AEROSOL_SCREEN_1 part 9), 2026-10-07, offline, uncommitted

Files (under src/RimMandrake/Scarlands/):
- Source/RM_GlowerShield.cs (new): RM_CompGlowerShield (static room registry), RM_StatPart_GlowerShield, Harmony prefix on ToxicUtility.DoPawnToxicDamage (halves room toxic damage incl. tox gas), RM_PlaceWorker_WallAdjacent.
- Source/RM_Warscar.csproj: Compile Include added.
- Source/RM_WarscarMod.cs: glowerShieldingEnabled (default true), Scribe + UI checkbox.
- Defs/ThingDefs_Buildings/RM_GlowerShielding.xml: RM_GlowerShieldPanel (80 crust + 20 steel, unpowered, +0.35 ToxicEnvironmentResistance room-wide, damage x0.5), RM_GlowerPlate (20 crust + 10 steel, Mass 8, Waist/Belt, +0.5 ToxEnvRes, +0.2 ToxicResistance, TableMachining, Crafting 4).
- Patches/RM_GlowerShielding.xml: adds the stat part to ToxicEnvironmentResistance.parts.
Art: placeholders (RM_LoosenedPanel, vanilla ShieldBelt texture), no new PNGs.

Build: winbuild RM_Warscar.csproj succeeded, 0 errors. validate_patch: patch and defs OK (static only, no --defs).

Unverified: all in-game behaviour; wall-adjacent PlaceWorker; stat part showing in explanation; Standable panel on a wall-adjacent cell; plate sharing Belt layer with shield belt; numbers invented.
