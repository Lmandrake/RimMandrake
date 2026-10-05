# MessyConduit -> Gimme Some Slack rename report

## Status
started Mon Oct  5 00:26:30 PDT 2026

## References found
- 304 files mention MessyConduit outside Transient; the mod folder itself (Source 77, northstar 127 run records, Defs 7, scripts);
  outside: modset_builder tier, selftest_messyconduit.py, modcheck required_checks.json (+ an unrelated peer's uncommitted edit in it),
  modcheck_status.json, validation_walks/RimMandrake/MessyConduit.md, live_queue/jobs.py comment, design docs, Utils/mockups/messy_conduit (22).
- Comments in CreatureBehaviors/TheForge/JawaBench cite the MessyConduit live finding historically: left as provenance.
- Save compat: GenTypes.GetTypeInAnyAssembly resolves saved Class= names (map components, things, job drivers) -> namespace rename
  needs a type-name shim (Harmony prefix mapping RimMandrake.MessyConduit.* -> RimMandrake.GimmeSomeSlack.*).
- Settings file = Mod_<deployed FolderName>_<Mod class>.xml (Verse.Mod.GetSettings). Old files live: Mod_MessyConduit_{MessyConduitMod,AerialLinesMod,FireHosesMod}.xml.
- Textures: 160 PNGs, 0 owner-kept -> moved through the art ledger (tw.copy + tw.sync retire), Textures/RimMandrake/MessyConduit -> .../GimmeSomeSlack.
- deploy_custom_mods deploys per folder name and prunes only inside a mod's own folder: it never removes a renamed mod's old folder.

## Steps / shas

## Proofs
- shas: 37a7f8dbb (rename, 388 files), 56408aefb (mockup scripts' tuple-form paths still wrote the old folder; fixed)
- winbuild GimmeSomeSlack: 0 warnings/0 errors; DLL RimMandrakeGimmeSomeSlack.dll has 0 UTF-8 'RimMandrake.MessyConduit' names
- selftest_gimmesomeslack.py 679/679 (incl. new legacy-name checks: type mapping + settings carry-over)
- run_selftests.py 177/179: FAILs are northstar_matrix C2 (reads Transient/messy_conduit_live_20261002 PNGs that a peer modified in the worktree, 51/52 ok) and selftest_utinnipatches_dump.py (unrelated)
- modcheck rename-key MessyConduit->GimmeSomeSlack; required_checks.json regenerated (22 checks); walk -> design/validation_walks/RimMandrake/GimmeSomeSlack.md
- deploy dry-run plans GimmeSomeSlack; `--mod MessyConduit` now refuses (unknown); modset tier gimmesomeslack plans harmony + 5 DLC + RimBridgeServer + SimpleCameraSetting, mod NOT INSTALLED until deployed
- pre-push art guard passed (160 textures moved via move_mod_textures.py: live events in art/events/BENCH.jsonl)

## Retire old deployed folder
deploy_custom_mods never removes a renamed mod's old folder (it prunes only inside a mod's own folder). With the game closed:
  python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod GimmeSomeSlack
  mv "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/MessyConduit" /mnt/d/Luke/dev/_rmscratch/retired_mods/MessyConduit   (mkdir -p first)
  python3 src/RimMandrake/Utils/modset_builder.py --tier gimmesomeslack --apply

## Live proof owed
- Player.log: '[GimmeSomeSlack] carried old Messy Conduit settings over to ...' x3 on first load; Config/Mod_GimmeSomeSlack_{GimmeSomeSlackMod,AerialLinesMod,FireHosesMod}.xml exist
- Mod Settings lists ONE entry 'RimMandrake: Gimme Some Slack' (probe already asserts the category)
- python.exe src/RimMandrake/GimmeSomeSlack/validation.py --live --fresh-map, then validation_aerial/hose/style(--save-load) as usual
- load a pre-rename save holding hoses/poles (any validation_*_save-load save from 2026-10-04): no 'Could not find class RimMandrake.MessyConduit' errors

## Owner rulings
- none blocking. Kept: defNames (incl. RM_MessyCords MapMeshFlagDef, SectionLayer_RM_MessyCords class), artpipe job names RM_MessyConduit_*, item IDs MESSY_CONDUIT_*, design doc filenames.

## Steps / progress
- texture move via ledger (160 PNG), git mv of the mod folder, sweeps, LegacyName.cs (+ GenTypes prefix, settings carry-over), LegacyNameChecks selftest written; next: build + selftests
- build OK (DLL has 0 old-namespace UTF-8 names), selftest_gimmesomeslack 679/679, modcheck rename-key done, required_checks regenerated (GimmeSomeSlack 22 checks), walk renamed; deploy dry-run plans GimmeSomeSlack; tier plan needs deploy first (NOT INSTALLED until deployed)
