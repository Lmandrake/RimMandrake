# RIMMANDRAKE_KEEP_GRAFFITI_RAID_TAGS_OFF_NATURAL_ROCK

Found by the Stage 2 preflight of Graffiti 0.1.0 (steward run RIMMANDRAKE_STEWARD_GRAFFITI_PREFLIGHT_STAGE, 2026-11-15); table `design/concepts/Graffiti/version/test_table.json`, record `design/concepts/Graffiti/version/preflight.json`.

## spec
Test T_RAID_TAG_BUILT_WALL_ONLY in the table, specified at Stage 2, built at Stage 3 (red first). Observes: the exit-tag wall predicate rejects natural rock (MineableGold, granite) and accepts a built wall (held walk defect #2; GraffitiJobUtility.IsPaintableWall accepts isNaturalRock today)
File: `src/RimMandrake/Utils/selftest_graffiti_raid_tag_wall.py`. Reads: src/RimMandrake/Graffiti/Source/GraffitiJobUtility.cs, src/RimMandrake/Graffiti/Source/RaidExitTagger.cs

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_graffiti_raid_tag_wall.py` exits 0 on the shipped mod and goes red on a planted mutant of the behaviour (watched failing 2026-11-15: the file does not exist yet). Expected: 1 pass.
