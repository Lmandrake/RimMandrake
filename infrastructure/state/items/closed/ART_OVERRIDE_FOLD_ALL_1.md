# ART_OVERRIDE_FOLD_ALL_1

## spec
Owner decision by card, 2026-10-09: fold ALL 59 remaining single-creature `*ArtOverride` mods (28 under
`src/RimStarWars`, 31 under `src/RimUtinni`) into the mod that owns each creature, exactly like the Silooth
precedent (SILOOTH_ART_FOLD_1, `616bbcdf3`). Built offline 2026-10-09; every standalone folder is deleted and
its packageId is gone from every tracked modlist snapshot (`infrastructure/state/modlists/`, `deployed/config/`).
No About.xml `loadAfter` or compose list named any of them.

The fold is data: `src/RimMandrake/Utils/art_fold_manifest.json`, one row per creature, read by
`src/RimMandrake/Utils/art_fold_check.py` (GONE / RESOLVES / PATCHED / NO-DANGLE / UNLISTED / KEPT, Silooth
row as the sanity probe, `--selftest` 8/8). Four shapes:

- **Moved (48).** Art now at `<Owner>/Textures/<Tier>/<Owner>/<Name>/`, same file names. Our own defs that drew
  the donor path were edited in place; the donor PawnKindDef is redirected by
  `<Owner>/Patches/ArtFold/<Name>_ArtFold.xml` — a PatchOperationConditional matching the texPath by VALUE
  (`/Defs/PawnKindDef//texPath[text()="<old>"]`), so every life stage / gender slot the old same-path override
  reached is redirected and a load without the donor is a silent no-op.
  - SWBestiary (24): Anooba Dewback Dragonsnake Fambaa Gizka Grank GreaterKraytDragon Gualaar Hawkbat Horax
    Insectomorph Kinrath Kreetle Mynock Nuna Ollopom Orray PekoPeko Ronto Shiro Vornskyr Whisperbird Zakkeg Zeer.
    Dewback's three `_<facing>m` masks (CutoutComplex) moved with it. ShiroB is drawn only by RSW_Shiro (no donor
    slot), so it has no patch op.
  - Shokk (1): Wyyyschokk — `RSW_Shokk_OllathrixSkin.xml` and `validation.py` literals updated. (Shokk's
    validation.py "expected 8 patch operations, found 7" fails on HEAD before this change too.)
  - UtinniPatches (23): Lockjaw AcanthamoebaGigantea Beetlefleet BlackSwarmling BloodShrimp Bumbledrone
    BumbledroneHierophant DryadCorruptor DryadTumorous Frostmite GreenGoo Grithe Grutt OcularJelly Plasmorph
    RaptorShrimp ShadowCharger Spidercat Swarmling TarGuzzler Terramorph Thunderox Visceral. Grithe/Grutt label
    patches moved to `UtinniPatches/Patches/ArtFold/`. Owner choice: the RimUtinni campaign layer, where these
    donor creatures' identity (rename) patches already live; Lockjaw (filed under RimStarWars but an Alpha
    Animals creature, renamed by the Miasma sheet) goes there too.
- **Absorbed (5).** The RM port already carries the identical bytes; only the donor redirect patch was added, in
  that mod: Agaripod -> TheRot `RM_Agaripod`, DecayDrake/Thermadon -> Miasma, Rimclaw -> Scarlands `RM_Rimclaw`,
  Helixien -> Scarlands `RM_Bileworm`.
- **Same path (3).** Dalgo, Iriaz: SWBestiary already shipped identical bytes at `swanimals/<Name>/`. Megathrips:
  moved into UtinniPatches at the donor's own path (`Things/Pawn/Animal/Megathrips/`) because its CutoutComplex
  masks are the donor's, paired by path; a new path would drop them.
- **Dead (3).** Wildpod (TheRot already repoints AA_Wildpod to identical bytes), Mantistanis (GR_Mantistanis dead;
  bytes kept as `src/RimMandrake/Utils/art_check_fixtures/MantistanisTextures`), MycoidColossus (TheRot repoints
  the donor to different art; the unbound override PNGs kept at `src/RimMandrake/TheRot/ArtUnbound/`, outside
  Textures/). Mantistanis and MycoidColossus had no About.xml.

ART_OVERRIDE_FAMILY_SCRIPT_1's member glob is now empty: that family no longer exists.

## deploy note (next game-down; NOT applied)
Order matters — deploy the owners FIRST, then remove the old mods, or the creatures fall back to donor art.
1. Plan then `--apply` with `deploy_custom_mods.py` for SWBestiary, Shokk, UtinniPatches and the
   RimMandrake.Biomes compose (Miasma, Scarlands, TheRot members).
2. Delete these 59 folders from `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\` (all present
   2026-10-09): AcanthamoebaGiganteaLargeArtOverride AgaripodArtOverride AnoobaArtOverride BeetlefleetArtOverride
   BlackSwarmlingArtOverride BloodShrimpArtOverride BumbledroneArtOverride BumbledroneHierophantArtOverride
   DalgoArtOverride DecayDrakeArtOverride DewbackArtOverride DragonsnakeArtOverride DryadCorruptorArtOverride
   DryadTumorousArtOverride FambaaArtOverride FrostmiteArtOverride GizkaArtOverride GrankArtOverride
   GreaterKraytDragonArtOverride GreenGooArtOverride GritheArtOverride GruttArtOverride GualaarArtOverride
   HawkbatArtOverride HelixienArtOverride HoraxArtOverride InsectomorphArtOverride IriazArtOverride
   KinrathArtOverride KreetleArtOverride LockjawArtOverride MantistanisArtOverride MegathripsArtOverride
   MycoidColossusArtOverride MynockArtOverride NunaArtOverride OcularJellyArtOverride OllopomArtOverride
   OrrayArtOverride PekoPekoArtOverride PlasmorphArtOverride RaptorShrimpArtOverride RimclawArtOverride
   RontoArtOverride ShadowChargerArtOverride ShiroArtOverride SpidercatArtOverride SwarmlingArtOverride
   TarGuzzlerArtOverride TerramorphArtOverride ThermadonArtOverride ThunderoxArtOverride VisceralArtOverride
   VornskyrArtOverride WhisperbirdArtOverride WildpodArtOverride WyyyschokkArtOverride ZakkegArtOverride
   ZeerArtOverride. (SiloothArtOverride is already gone from the game folder.)
3. Drop from the live `ModsConfig.xml` activeMods every `mandrake.rsw.*artoverride` / `mandrake.rut.*artoverride`
   entry — 47 of the 59 were active on 2026-10-09 (the manifest's `packageId` column is the full list).
   Untracked `deployed/config/ModsConfig.before-*` backups written by other windows still name them; a restore
   from one re-adds them (harmless warnings once the folders are gone).

## criteria
- F1 L0: `python3 src/RimMandrake/Utils/art_fold_check.py` reports 60 creatures, 0 red, Silooth probe PASS
- F2 L0: no `src/*/*ArtOverride` folder exists and no tracked modlist snapshot names an `*artoverride` packageId
- F3 L1: after deploy, a donor-def and an RSW_-port specimen of three moved creatures (one SWBestiary, one
  UtinniPatches, Dewback for its masks) draw our art, and Player.log has no "Failed to find any textures" for
  a `RimStarWars/SWBestiary/`, `RimStarWars/Shokk/` or `RimUtinni/UtinniPatches/` path
