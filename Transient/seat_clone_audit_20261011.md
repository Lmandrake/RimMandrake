# FOUNDRY seat clone audit 2026-10-11

Clone: /home/mandrake/rm/foundry. Read-only audit (fetch only). origin/main = 7400c6277. HEAD is 160 behind, 7 ahead.

## Summary
| class | count |
|---|---|
| (a) tracked modified, byte-identical to origin/main (phantom) | 40 |
| (a2) untracked but byte-identical to origin/main | 92 (of which 2 are .claude/skills symlinks, 3 item files are on origin under items/closed) |
| (b) line-ending-only difference | 1 (untracked design/RimMandrake/mod_audit/MASTER_REGISTRY.csv: local LF, origin CRLF) |
| (c) real uncommitted work absent from origin | 1 file: ledger shard (10 lines) |
| (c2) tracked-modified but STALE vs origin (origin has newer; local is an older state, not work) | 4 |
| (d) untracked scratch not on origin | 205 (154 Transient/*, 27 deployed/config backups, 21 conversations/*, 3 items) |

## Unpushed commits (git cherry origin/main HEAD)
5 of 7 match origin by patch-id: 0be88f8a6, 14fa9468a, 2ee9fb6fb, f12511920, 0457f6389.
2 show '+' (3f735d1b9 decay sweep, ac4c7356b decay sweep 3): patch-id differs only because of ledger-shard rebase context; same subjects are on origin as f53ad8125 and 1f145fb40, and every file they touch exists on origin. Treat all 7 as published. Their ledger lines are NOT all on origin (see c).

## (c) real work
- infrastructure/state/ledger/events/FOUNDRY.jsonl: 10 lines absent from origin's shard: 5 lease take/release (expired, worthless), 2 reconcile (GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN, LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED, verdict partial sha c97c48cdc), 1 implemented LIQUID_THIRST_CHAIN_1 (e623e9bf4), 2 notes (ALPHA_ANIMAL_PORTS_REHOME_1, TECHPRINT_FACTION_GATING_1). 7 of them sit in unpushed HEAD commits, 3 only in the worktree. Merge by appending lines (merge=union), never by checkout of a side.

## (c2) stale, origin newer (safe to discard)
- Transient/modcheck/fixtures.json: tick 300 vs origin 8637 (runtime noise)
- infrastructure/output/research_manifest_draft.csv: local lacks the heldByFactionCategoryTags,techprintCount columns origin has
- src/RimMandrake/Utils/modaudit/assemble.py: local hardcodes the CherryPicker /mnt/c path; origin uses game_paths.LOCALLOW
- src/RimUtinni/ResearchRetag/About/About.xml: local lacks two <li> (sarg.alphamechs, vanillaexpanded.vwe) origin has

## (a) phantom tracked files (40)
- design/Jawa/research_review/build_retag_patches.py
- design/RimMandrake/deepfire_luminous_pigment_spec.md
- design/RimMandrake/mod_audit/README.md
- design/RimMandrake/mod_audit/facts/mod_facts.csv
- design/RimMandrake/mod_audit/facts/mod_facts.jsonl
- design/RimMandrake/mod_audit/facts/session_context.json
- design/validation_walks/RimMandrake/LuminousPigment.md
- skills/README.md
- src/RimMandrake/LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll
- src/RimMandrake/LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll.srchash
- src/RimMandrake/LuminousPigment/Source/DeepfireGodDeltaDebugActions.cs
- src/RimMandrake/LuminousPigment/Source/DeepfireLightsOutCompat.cs (deleted locally, absent on origin)
- src/RimMandrake/LuminousPigment/Source/RM_LuminousPigment.csproj
- src/RimMandrake/LuminousPigment/validation.py
- src/RimMandrake/Utils/gen_pawnkind_roster.py
- src/RimMandrake/Utils/gen_weapon_register.py
- src/RimMandrake/Utils/modaudit/defscan.py
- src/RimMandrake/Utils/modaudit/diskfacts.py
- src/RimMandrake/Utils/modaudit/selftest_modaudit.py
- src/RimMandrake/Utils/modaudit/sources.py
- src/RimMandrake/Utils/modset_builder.py
- src/RimMandrake/Utils/weapon_tag_audit.py
- src/RimMandrake/bridgetools/prove_deepfire_god_deltas.py
- src/RimStarWars/Armoury/About/About.xml
- src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml
- src/RimStarWars/Armoury/Patches/Turrets_DamageDoctrine.xml
- src/RimStarWars/Armoury/Patches/Turrets_Renames.xml
- src/RimStarWars/Armoury/Source/gen_armoury_patch.py
- src/RimStarWars/Armoury/Source/gen_turret_doctrine.py
- src/RimStarWars/StarWarsPatches/Patches/WeaponTags_Renormalise.xml
- src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml
- src/RimUtinni/Doctrine/Patches/MegafaunaYield_OwnedPorts.xml
- src/RimUtinni/Doctrine/Patches/MegafaunaYield_OwnedPorts_Warscar.xml
- src/RimUtinni/Doctrine/Source/gen_megafauna_yield.py
- src/RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Races/RUT_Race_GreentideAnt.xml
- src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml
- src/RimUtinni/ResearchRetag/Patches/RUT_ResearchTabAssign.xml
- src/RimUtinni/UtinniPatches/About/About.xml
- src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml
- src/RimUtinni/UtinniPatches/Patches/BiomeCastEvictions_WildBiomes.xml

## (d) untracked scratch, not on origin: by area
Transient/** 154 (probe, .b4_*, .edl_*, modcheck queues); deployed/config 27 (ModsConfig backups); conversations/ 21 transcripts; infrastructure/state/items 3 (ASHKARR_PAINTER_NAMES_DIVERGED_1, FALL_LINE_MAJOR_REGION_LABEL_1, TWILIGHT_ART_REUSE_ELSEWHERE_1: closed on origin under items/closed/, so these are stale open copies). Full list: git ls-files --others --exclude-standard.
conversations/ transcripts (21) are the only scratch with possible archival value.

## Recommended safe procedure (NOT executed)
1. mkdir backup dir outside the clone; copy FOUNDRY.jsonl, conversations/ and (optionally) deployed/config + Transient out of the clone (cp -a).
2. git fetch origin; confirm: git merge-base --is-ancestor of the 7 local commits by subject (see above) - all already on origin.
3. Check bridge/game not mid-use by this seat (rimflow bridge who), no other process editing the clone.
4. git reset --hard origin/main (discards 40 phantom + 4 stale + 7 local commits). Untracked files remain; remove the 3 stale open item copies and the LF MASTER_REGISTRY.csv only after step 1.
5. Append the 10 ledger lines from the backup with `comm -13` against the new shard (union), run ledger_lint.py, commit that one path, pull --rebase, push origin HEAD:main.
