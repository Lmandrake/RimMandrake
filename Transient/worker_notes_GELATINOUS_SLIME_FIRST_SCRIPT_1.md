# worker note GELATINOUS_SLIME_FIRST_SCRIPT_1 (FOUNDRY subagent, 2026-10-01)

Files: `src/RimMandrake/GelatinousSlime/{validation.py,northstar_plan.py,northstar_site.py,northstar_mock.py,selftest_slime_suite.py}`,
walk `design/validation_walks/RimMandrake/GelatinousSlime.md` (DRAFT, blank hash, `## must be true` with arrows).

## State
- 39 components in 10 chains; 10/10 Mod Settings toggles covered (floor.uncovered == []).
- Offline: `cli.py run --mock ... --mock-skip-site` completes; `selftest_slime_suite.py` = clean run + Desert run + 22 injected faults, each turns its component red (0 problems).
- `lint_calls.py` over the mod folder: clean (36 literal calls).
- `modcheck floor --all` shows GelatinousSlime `DRAFT, 0 bars, "no bar"`. "bar met" only exists for owner-VALIDATED north stars (Graffiti, FlowWorks); agents may not validate. This is the expected state, not a defect.
- Packaging: the mod is FOLDED into `mandrake.rm.biomes`; EXPECT_MODS = mandrake.rm.biomes (like Pyrelands), not mandrake.rm.gelatinousslime.

## Tier
`baroque_wave0` already loads it (BRIDGE + mandrake.rm.biomes, 13 mods with deps, no Utinni patches so the default gene archive is the active one). The old `slime` tier adds mandrake.rut.patches (campaign archive, priority 100) and would change the archive checks: do not use it. No tier added.

## LIVE-RUN SHEET
1. Bridge: `rimflow bridge take --for "GelatinousSlime first script"`.
2. `python3 src/RimMandrake/Utils/modset_builder.py --tier baroque_wave0 --apply` (game closed / Player.log quiet 3 min), launch via Steam, wait for `Bridge token:` (cold load small: ~minutes), then `rimworld/start_debug_game_ready` for a quicktest map (map >= 100 each axis; preflight checks).
3. One line: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod GelatinousSlime --plan src/RimMandrake/GelatinousSlime/northstar_plan.py` (results JSON in `Transient/northstar/`).
4. Tick budget: ~1200+2000+120+600 (ladder) +700 +1200 +900 +10000 (read marks, two 5000 arms) +~6 hits = about 17,000 game ticks; at the measured 600-2800 ticks per step call that is 10-30 minutes; read-marks is the long pole (cut `wait_ticks(5000)` to 3000 only with the P(0) maths in the comment).
5. Site: scratch quicktest map, all 5 DLCs, NO god mode needed; suite clears + builds its own 40x40 at the map centre (left slime, right Concrete); colonists drafted. It runs on ANY biome. Run the `exposure_and_ladder` chain a SECOND time on a Desert/AridShrubland site to turn `drying_biome_decays` from UNMEASURED to a verdict (on a drying map `growth_rate_on_slime` / alert may be UNMEASURED by design).
6. Do not run the titanoslime chain next to anything you care about (damaged titanoslimes turn manhunter).

PASS/FAIL meaning (FAIL = MOD unless noted):
- all_defs_resolve FAIL: def discarded live (read Player.log first exception; a bad field/type). notFound lists them.
- terrain_tagged / drying_biomes_tagged FAIL: tag/patch missing live (patch inert: check Patches loading under composed LoadFolders).
- settings_defaults FAIL: shipped default drifted (titanoslimeReversible must be False).
- exposure_applies FAIL: MapComponent_SlimeExposure or tag dead. exposure_skips FAIL: resistance leak.
- growth_rate / stage1_wipes FAIL: rate differs from ruled (the constants in validation.py mirror Slimification.cs; if you change the C# deliberately, change them with the reason in the commit).
- returned_to_the_flow FAIL: names which of corpse/smear/raw slime is wrong (smear missing may be terrain filthAcceptanceMask: real finding).
- antidote / raw_slime UNMEASURED "order refused": HARNESS (UseItem / Ingest ordered_job shape, reservation); a FAIL after an accepted order is MOD.
- stage3_ends_panic FAIL: law 2 enforcement dead. UNMEASURED if the stage-1 control also leaves PanicFlee (differential invalid).
- seeker / titanoslime components read `jawa/inspect_string` rows from `things` or `results` (UNPROVEN shape): UNMEASURED = HARNESS, adjust the reader.

## UNPROVEN live shapes (first run will settle)
`jawa/inspect_string` row key (things|results) and `inspect` lines; `jawa/get_defs deep=true` giving `modExtensions` as dicts with `decayPerDay`; `mapBiome` is the defName; `get_defs` accepts the full class name `RimMandrake.GelatinousSlime.GeneArchiveDef`; `MapGeneratorDef/Base_Player.genSteps` readable (else UNMEASURED); `jawa/ordered_job` UseItem with targetBId=patient (read off CompUsable.TryStartUseJob); `jawa/alerts_list` row `type`.

## How each check is proven able to FAIL
`selftest_slime_suite.py`: env `NS_SLIME_MOCK_BREAK=<fault>` (see northstar_mock.py) makes the mock game violate one rule; the table in the selftest maps 22 faults to the component that must go red (def vanishes, tag missing, patch inert, genstep unregistered, wrong default, no exposure, 3x growth, no law-2, no alert, no dissolution, no smear, antidote no-op / no cost, eat no cure / no fee, read-marks ignores setting, marked costs nothing, seeker comp absent, rain unavailable, max stage ignored, no shedding, shed ignores setting). Live equivalents: absent a def by renaming its defName in a scratch copy; remove the tag from one terrain; drop Patches/DryingBiomes.xml.

## UNCOVERED (named in the walk)
Seeker prime/extract/inject/antidote race (needs companion tool `jawa/slime_seeker_load`; propose item SLIME_SEEKER_LOAD_TOOL_1, not filed by me), farm conversion (slime biome map + 50k ticks), visitor trickle/seed (slime-biome scratch map recipe, SLIME_BIOME_SITE_1), titanoslime engulf/permanent growth long-run, worldgen rarity / spawn-factor roster / mote text, art.
