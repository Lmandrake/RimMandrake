# BELT: Messy Conduit phase 1a build — 2026-10-02

Item: MESSY_CONDUIT_MOD_1. Seat FOUNDRY.

## Milestones
- [ ] M0 read spec + prototypes, claim item
- [ ] M1 Verse-free core lib + SelfTest vs Python oracle
- [ ] M2 mod skeleton (About, defs, invisible conduit, Harmony hookup-wire hide)
- [ ] M3 drawer SectionLayer + PowerNet live/dead + sparks
- [ ] M4 settings
- [ ] M5 placeholder textures
- [ ] M6 build + deploy
- [ ] M7 modset tier + validation.py + walk
- [ ] M8 live run + screenshots + record

## Log
- M0 done: spec + oracle read. rimflow claim REFUSED (item owned by OWNER); recorded a note instead.
- M1 done: Verse-free core (Source/Core: CordMath, CordWorld, CordGraph, CordPlanner, CordLayer, CordBuilder) + SelfTest vs Python oracle (export_oracle.py -> oracle_scenes.json, 7 scenes). 102/102 pass; --probe 7/7 scenes fail on planted mismatch. Note: tests written AFTER the port (not red-first); the probe is the can-fail evidence. Offline renders of C# geometry: Transient/messy_conduit_live_20261002/offline_csharp_*.png. Placeholder textures (12, validator PASS) by helper.
- M2-M5 done (code): About.xml (Harmony dep, incompatibleWith Invisible Conduit), RM_MessyCords MapMeshFlagDef, ConduitVisuals (C# texPath swap to transparent PNG, restorable at runtime; Hidden Conduit excluded), Harmony prefix on PowerNetGraphics.PrintWirePieceConnecting (only !forPowerOverlay and B is our conduit), CordWorldAdapter (map -> CordWorld), RM_MapComponent_CordGraph (rebuild-per-frame-on-demand, cross-section dirtying, 250-tick live poll, sparks via vanilla flecks, debug draw), SectionLayer_RM_MessyCords (ribbons + decals, boundary rect = printed extent), settings screen, MessyConduitProbe (state-read channel via jawa/mod_settings_field). Build OK (winbuild).
- DEVIATION from doc: texture swap is done in C# (not XML) so master-off restores vanilla art live; substructure LinkAllowed rule NOT applied in 1a (would make every hull edge a sparking break).
- M6 deploy+tier: deployed 16 files; tier messyconduit applied (9 mods; owner's 610-mod list backed up -> MUST --restore at end); game launched via Steam, bridge up in 34s; '[MessyConduit] targets: PowerConduit, WaterproofConduit; invisible=True' in Player.log. Offline tier 5/5 PASS.
- M7 live tier: run1 FAIL (scene error: lamp hooked main run -> branch pruned as needless spur, into-wall run diagonal); run2 FAIL (layer meshes 0: camera off-scene, sections regenerate only in view); run3 18/18 live rows PASS, 6 UNBUILT, 2 UNCOVERED, ~268 ticks.
- M8 done: decals were specks at 1/3 cell (art fills ~60% of canvas) -> scales doubled, FrayLive for live ends; rebuilt/redeployed/relaunched. Final live run 19/19 PASS (+6 UNBUILT, 2 UNCOVERED), result src/RimMandrake/MessyConduit/northstar/validation_result_20261002T135728.json; modcheck record -> REFUSED (honest: open bars). Screenshots + README in Transient/messy_conduit_live_20261002/. Design doc §8.13 "as built" added, stale "nothing built"/pause text replaced.
- Mod list: my --restore wrongly wrote the 610 full list (pre-swap live list was the 9-mod FLOWWORKS tier, not the full list); put back with `modset_builder --tier flowworks --apply`; live ModsConfig now == pre-swap snapshot (verified by parse). Older before-tier-flowworks.xml kept as deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml. Game DOWN.
