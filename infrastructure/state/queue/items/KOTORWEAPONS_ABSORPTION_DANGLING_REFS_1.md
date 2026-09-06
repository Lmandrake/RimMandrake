# KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1

Found during DIRTY_CODE_REVIEW_STANDING_LOOP_1 pass over the
Absorbed_AdditionalMods/Absorbed_KotorCore/Absorbed_KotorWeapons pool. Same
pattern as the already-closed WEAPONTAGS_RENORMALISE_STALE_DEFS_1
(guy762_brifle_rohlan/sith dead refs), but inside the Absorbed_* Defs
themselves rather than a StarWarsPatches renormaliser, and a wider set of
defNames.

Both `gen_kotorcore_absorption.py` and `gen_kotorweapons_absorption.py` write
a `BLOCKED_manifest.txt` listing defNames deliberately excluded from
absorption because their comp/verb classes belong to a donor mod (SWCP.*,
taranchuk_homingprojectiles.*, AthenaPort.*) judged out of scope. But the
generators never checked whether OTHER absorbed defs reference those same
excluded defNames by string (defaultProjectile, relatedBuildCommands,
hand-mod-positioning keys). Confirmed via `mcp__rimsage__get_def_details`
against the live def dump: none of the listed defNames resolve.

Confirmed `guy762.KotORWeapons` is ABSENT from the live ModsConfig.xml (per
WEAPONTAGS_RENORMALISE_STALE_DEFS_1) while `guy762.mm.kotorcore` IS present
(grep of ModsConfig.xml, 2026-09-06). `deploy_custom_mods.py` shows the whole
Armoury folder deploys with no DEPLOY_HOLD entry on any Absorbed_KotorWeapons
file, so the file headers' "do NOT deploy until [guy762.KotORWeapons]
retires" note is not tool-enforced, and the retirement condition has already
happened — these Absorbed_KotorWeapons files are live now, not latent.

## Confirmed dangling `defaultProjectile` references (hard cross-refs; each
should log "Could not resolve cross-reference" and break that verb)

- `Absorbed_KotorWeapons/ModularPartDefs/Absorbed_KotorWeapons_ModularPartDefs_Wristgun.xml`:
  `<defaultProjectile>KotORMissile_seeker</defaultProjectile>` (~line 312),
  `<defaultProjectile>KotORMissile_whistlingbird</defaultProjectile>` (~line 530)
- `Absorbed_KotorWeapons/ModularPartDefs/Absorbed_KotorWeapons_ModularPartDefs_JetpackMissile.xml`:
  KotORMissile_highex (~56), KotORMissile_plasma (~114), KotORMissile_ion
  (~172), KotORMissile_buster (~230)
- `Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_WeaponRanged_KotORIonPistol.xml`:
  `<defaultProjectile>KotORElectricBolt</defaultProjectile>` (~338)

All six missile projectiles and KotORElectricBolt are on the
Absorbed_KotorCore BLOCKED manifest (taranchuk_homingprojectiles./AthenaPort.
comp classes never ported). `guy762.mm.kotorcore` IS still active, so these
might resolve TODAY via kotorcore's own live Defs rather than ours —
unverified; the def dump is the only check made here and dump freshness
against the current 596-mod list is unconfirmed (CLAUDE.md: dumps decay).
Needs verification against a live game load (Player.log "Could not resolve
cross-reference"), not another dump read.

## Also found — likely lower severity, verify before assuming any error

- `Absorbed_KotorCore/ThingDefs_Buildings/Absorbed_KotorCore_Structure_SWWalls.xml`:
  `<relatedBuildCommands>` lists guy762_Autodoor1x1_DoomgiverA/TatooineA/
  SandcrawlerA/DreadnaughtA and guy762_DoubleAutodoor_*VerticalA
  (SWCP.RimframeGrineerDoors. class, excluded) — these are
  guy762.mm.kotorcore's OWN excluded defNames referenced from ITS OWN
  absorbed wall defs. Whether the live (non-absorbed, still-active) kotorcore
  mod provides these doors via a third framework (SWCP) not confirmed present
  in the active mod list needs checking.
- `Absorbed_AdditionalMods/kotorweapons/ShowMeYourHands/Absorbed_Kotorweapons_ShowMeYourHands_handmodpositioning.xml`:
  references guy762_brifle_sith, guy762_brifle_rohlan, guy762_hvyrepeater
  (+_mando/_massdriver/_baragwin/_ordo), guy762_mininglaser — likely a
  defName-keyed hand-position dictionary that silently no-ops on a miss
  rather than erroring, but not verified.

## Not fixed here

The actual repair (port a local projectile/comp, cut the affected
verb/part, or reinstate the excluded content into scope) is a content/design
call, not a bounded one-line fix, and duplicate-defName risk means any fix
must be checked against whichever guy762 mod is still active. Recommend:
verify against a real Player.log with the full mod list loaded first (this
review session had no bridge/game access), then decide per file.
