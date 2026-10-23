# GREENTIDE_ANTS_MIGRATE_NO_ANT_LEFT_BEHIND

Owner, Biome card 8 by question card, 2026-10-22 (`design/RimMandrake/biome_owner_cards_2026-10-22.md`): move the
Greentide Raid Ants into the free Greentide mod under our own name (no Star Wars), then retire
`mandrake.rut.greentideraidant`.

## spec
- Moved into `src/RimMandrake/Greentide/` (mandrake.rm.greentide, composed into mandrake.rm.biomes), RM_ names, numbers
  unchanged: `Defs/ThingDefs_Races/RM_GreentideAnts.xml` (RM_GreentideAntRace, RM_GreentideAnt, RM_GreentideAntSoldier,
  RM_ThinkTree_GreentideAnt, RM_GreentideAntCarapace, RM_GreentideAntCarapaceWall) and
  `Defs/FactionDefs/RM_GreentideAnt_Faction.xml` (RM_GreentideAntFaction). The 8 textures were moved through the art ledger
  (`move_mod_textures.py --sub RUT_GreentideAnt=RM_GreentideAnt`). Four of them are owner-kept (ant and dessicated
  north/south). The pre-push art guard refuses retiring a kept slot without his words even when the same sha is live
  elsewhere: `art_guard.py` exempts `held_elsewhere` for a displacement, but not for a retire, whereas `artledger.retire`
  does allow it. So those four stay as a stub at `src/RimUtinni/GreentideRaidAnt/Textures/` (no About.xml, not
  deployable) until he releases them in words. That guard/ledger mismatch is a finding for the art-tool owner; the
  checker was not edited.
- Mod Settings (Greentide screen, "Giant ant raids", scope Now): `antRaidsEnabled` (off = every RaidStrategyDef listed
  in the faction's disallowedRaidStrategies, so `IncidentWorker_RaidEnemy.FactionCanBeGroupSource` refuses it, desperate
  pass included) and `antRaidStrength` 0.25-3 (divides both kinds' combatPower). `Source/RM_GreentideAntRaidApplier.cs`,
  no Harmony; proof entry `ProofApply`.
- Saves: NOT edited. Decided from the measurement: the four `ASHKARR_DEV_*_2026-10-20.rws` saves name
  `RUT_GreentideAntFaction` (a faction `<def>` and a faction-list `<li>`), `RUT_GreentideAntRace` (an `<animal>` row),
  `Corpse_RUT_GreentideAntRace` (7 thing-filter `<li>`), and PARITY_QUIET_R3 a hat whose `<stuff>` is
  `RUT_GreentideAntCarapace`. CANONICAL_ASHKARR_START_2026-09-12 and Autosave-1 name none. Every one is a Scribe def
  lookup, which goes through `BackCompatibility.BackCompatibleDefName`, the method the existing RM_DefAliasDef postfix
  (EnvironmentalHazards) rewrites. So nine typed aliases in `Defs/Misc/RM_GreentideTierMove_Aliases.xml` load them as the
  RM_ defs, kept until the world remake writes saves with the new names. Without them the log says "Could not load
  reference to ... named RUT_..." (Scribe: the save holds a dead name, no mod change fixes it) and the faction loads with
  no def. ("Could not resolve cross-reference" is the def loader and does not apply to saves.) The alias proof's type
  list gained FactionDef and PawnKindDef, or those rows would read FAIL.
- Cut: the mod folder, the six current mod lists (FULL.LATEST and the five RULED profiles), the `greentideant` modset tier
  (now wants only mandrake.rm.biomes), the required-checks row (regenerated), the mod archive row (RETIRED-MERGED). The
  five references (Doctrine About, MegafaunaYield, OnlyOurFactions, Armour_Leather comments; the old test manifest) now
  name the RM_ defs or are gone. Roster `the_greentide.json`, `cast_assignment.csv`, remake runbook G15 and the reinstate
  list name the RM_ faction/race.
- Owed, recorded and not invented: a coined name (label stays the plain "giant ant"; a Star-Wars-style name may be a
  campaign-layer label patch later), new art (the existing ledger pictures are reused, so no artpipe job was queued), two
  raid-call sounds (soundCall/soundAngry unset).

## verify
Offline: `python3 src/RimMandrake/Greentide/validation.py` (STATIC, incl. `ant_findings`: defs wired, art on disk, every
alias present); `python3 src/RimMandrake/Utils/selftest_settings_screens.py`. Live: Greentide chains `giant_ants`,
`defs_resolve`, `flip_antRaidsEnabled`, `flip_antRaidStrength` on a list carrying mandrake.rm.biomes.

## criteria
- A1 L0: Greentide STATIC PASS; settings-screens selftest all ok; both DLLs build; compose dry-run lists the ant files.
- A2 L1: deploy: `deploy_custom_mods.py --compose biomes --apply` (Greentide + EnvironmentalHazards DLLs, ant defs and
  textures), and the game copy `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\GreentideRaidAnt` removed, or
  its RUT_ defs load beside the RM_ ones if anything re-lists it.
- A3 L2: live: `giant_ants/*` PASS: both kinds spawn, raids off blocks every strategy and restores, strength 2.0 halves
  combatPower, `old_rut_names_load_as_rm_defs` PASS for all nine aliases.
- A4 L2: live: an ASHKARR_DEV save loads with no "Could not load reference" line naming RUT_GreentideAnt*, and
  `jawa/list_factions` shows the "They!" faction as RM_GreentideAntFaction.
- A5 L2: live: a forced RaidEnemy from the ant faction sends ants at the colony (directed assault); butchering one yields
  RM_GreentideAntCarapace.
