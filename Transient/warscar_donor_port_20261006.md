# WARSCAR_SHEET_DONOR_PORT_1 — port pass 2026-10-06 (FOUNDRY helper, offline, uncommitted)

Worked example: ABYSS_SHEET_DONOR_PORT_1 (708dbc9a8, 6ebae76c1). Each port = own def file (ThingDef + PawnKindDef)
in src/RimMandrake/Scarlands/Defs/ThingDefs_Races/, RM_Warscar row at the donor row's commonality, donor row removed,
RUT_Scarlands twin row swapped (`MayRequire="mandrake.rm.biomes"`). Every donor-only substitution is named in the
file header and marked PROVISIONAL.

## creatures
- [x] AA_Helixien -> RM_Bileworm (0.08). Body AA_Slug -> Snake; corpse-rotting + disgust aura (VEF) dropped, OWED.
- [x] SW_Juggernautbeetles -> RM_JuggernautBeetle (0.05). SW_FlameCut -> Cut (EMP extra damage kept); no leather; tunnelling dropped.
- [x] SW_Electricgryllotalpa -> RM_ElectricGryllotalpa (0.15). Arc projectile ported as RM_ElectricGryllotalpa_Arc, damage EMP (was burn+EMP).
- [x] SW_Electrictick -> RM_ElectricTick (0.3). Death burst -> EMP; custom think tree + no-corpse dropped.
  OWNER QUESTION: the vanilla MechPowerCell (2500 ticks) is kept, so every wild tick dies ~1 in-game hour after spawning (donor design).
- [x] RG_Rimclaw -> RM_Rimclaw (0.1). Body -> vanilla iguana body (horn -> HeadAttackTool); eggs -> live birth, gestation 30.
- Labels kept as ruled, only respaced/lowercased ("juggernaut beetle", "electric gryllotalpa", "electric tick").

## rosters
- [x] RM_Warscar inline rows (5 swapped/added; header corrected)
- [x] WildAnimals_Warscar.xml Isopoda block deleted (header corrected)
- [x] RUT_Scarlands twin rows (5 swapped)
- Warscar_Rename.xml: Rimclaw + Juggernaut description blocks deleted (no biome casts those donors now); Helixien
  bileworm block KEPT (donor still cast in Miasma, Cauldron, Slime, Contagion).
- RM_WarscarMod.cs: the one "interim donors" toggle (spined gow, rimclaw, helixien) -> five per-species toggles;
  validation.py DEFAULTS + new port/roster/texture checks.

## art (all via the art ledger, RIMFLOW_SEAT=FOUNDRY)
- [x] RM_Bileworm / RM_ElectricGryllotalpa / RM_ElectricTick / RM_JuggernautBeetle east/south/north: the owner's B
  picks (gapall_*_v1), --ruling 20378bc0df2321dcfa7c / 111be9e4455e8fa91079 / 937f0231e943a91424d6 / 2835dfc1040c75b749fe.
- [x] RM_Rimclaw east/south/north: bytes copied from src/RimUtinni/RimclawArtOverride (his A pick, the live picture).
  No ledger keep names those bytes, so it went in on --reason script:src/RimMandrake/Utils/art/art.py.
- Contact sheet looked at; alpha clean (corner alpha 0, coverage 0.23-0.43). `art.py guard worktree`: 0 unledgered.

## tuning companions (hand-written, PROVISIONAL, delete when generators emit the ports)
- [x] Doctrine/Patches/MegafaunaYield_OwnedPorts_Warscar.xml: bileworm Meat 560; gryllotalpa Meat 210 / Bone 75; juggernaut Meat 420 / Bone 150.
- [x] UtinniPatches/Patches/AnimalTolerances_OwnedPorts_Warscar.xml: bileworm -21.1..77.8, rimclaw -8..81.2,
  gryllotalpa -58..160, tick -50.1..120 (the generated file's pinned donor values).

## checks
- [x] Scarlands validation.py static: 0 failures.
- [x] validate_patch (Data + workshop + Mods), 11 files: 0 errors, 5 advisory warnings (LauncherShot lives in Core's
  resources.assets; the rest are the pre-existing Helixien rename block + the add-if-missing shape).
- [x] winbuild RM_Warscar.csproj: 0 warnings, 0 errors; DLL + .srchash rebuilt.

## left
- Owner question: electric tick's one-hour lifespan (keep the donor design or let wild ticks live).
- Owed mechanics named in headers: bileworm corpse-rot + disgust aura; flame-on-hit for the insects.
- Donors still cast elsewhere, untouched (evictions are stopped): AA_Helixien in Miasma/Cauldron/Slime/Contagion,
  SW_Electrictick in RUT_Wasteland. RimclawArtOverride still dresses the uncast donor RG_Rimclaw.
- Not deployed, not live-tested.
