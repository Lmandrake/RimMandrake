# Done claim

- unseen: Reskin and re-text every map-scatter wreck (tanks, trucks, cars, ancient junk) into Star Wars scavenger wreckage: census what exists and what spawns it, mine the donor mods slated for removal (urban r is done as `infrastructure/state/items/FASCINATING_WORLD_JUNK_1.md` says, shown by fresh evidence. | evidence: `whittle/fascinating_world_junk_1/evidence/selftest_junk_roster.log` `whittle/fascinating_world_junk_1/evidence/census_vs_roster.txt` `whittle/fascinating_world_junk_1/evidence/census_unpatched.json` `whittle/fascinating_world_junk_1/evidence/census_patched.json` `whittle/fascinating_world_junk_1/evidence/roster_contact_sheet.png` `whittle/fascinating_world_junk_1/evidence/dev_start_save_existing_map_inventory.txt` `whittle/fascinating_world_junk_1/evidence/dev_start_save_map_vs_roster.txt`

The verdict is "unseen" because the item's verify section is a live one: a real arrival map at Zeddo's Yard,
screenshotted and measured whole-map with `jawa/list_things`; one Fall Line map; a full-list load; and the owner
LOOKING at the screenshot and the contact sheet. My lane is offline: no game, no bridge. Each of the four phases
stands as follows (published at `29b71f8f34`):

- **Phase 1, census:** done 2026-09-13 (`design/Jawa/worldbuilding/junk/junk_census_2026-09-13.md`). It now has a
  re-runnable instrument, `src/RimStarWars/StarWarsPatches/junk_spawn_census.py`, which reads:
  - the 14 vanilla junk GenSteps, including the C# hard-coded lists;
  - the Scarlands prefabs' contents;
  - our Zeddo's Yard template and our scatter steps.

  It finds 105 spawnable defs before the cut and 80 after.
- **Phase 2, donor ideas:** done 2026-09-13, in the same census doc.
- **Phase 3, roster:** `design/Jawa/worldbuilding/junk/junk_roster.json`, as data. It holds:
  - 4 regions (zeddos_yard / fall_line / scatter / rakatan);
  - 11 kinds, each giving what it was, what it yields and what it risks, with its regions;
  - 83 kept defs;
  - 20 cut defs and 5 cut prefabs: the roads, crane yard, container lot and forklift yard that carry cars and trucks.

  It was ruled as a delegated design call: the owner's 2026-10-09 card "appearance now, flavours later" ordered the
  phases, and appearance has since shipped. The owner can overrule any row.
- **Phase 4, re-graphic and re-text:**
  - The 24 vehicle and war-machine defs carry judged Star Wars art: 179 variants, from STARWARS_JUNK_RESKIN_1.
  - This round took "tank" and "truck" out of the last labels and descriptions ("assault repulsorcraft hulk",
    "cargo speeder hulk").
  - The cut patch is generated from the roster, so the trucks, chem trucks, forklifts, road sections and strip-mall
    junk no longer scatter.
  - On Fall Line tiles, `RUT_FallLine_NoOldJunk` prevents all 14 vanilla old-junk steps, and the junk factor is 0.
  - Mod Settings: `junkRosterCut` and `noOldJunk`, both default on; off means vanilla.

Offline proof: `selftest_junk_roster.py` passes 22 of 22 checks. They show:
- every def that can spawn (80) is in a kept kind;
- none is on the cut list;
- every cut xpath hits its GenStep;
- no scatter group is left empty;
- no kept label says car, truck or tank;
- the yard template's 17 defs all sit in yard kinds;
- the Fall Line prevent list covers all 14 vanilla sources;
- both DLLs match their source hashes.

Planted-defect probes show the checks can see a failure.

The real-data check: the pre-change map inside the dev start save has 58 instances the new roster would not place,
and every one of them is a def that is cut or arrives only inside a cut prefab.

## What I'm least sure about
- **Whether the runtime `extraGenSteps` edit takes effect in a real map generation.** It is read from the engine
  source (MapGenerator joins mutator extraGenSteps before the preventsGenSteps filter), not seen live.
  `FallLineOldJunk.Report` (`jawa/static_call`) reads it back in a running game.
- **Whether the cut patch applies with zero errors under RimWorld's own XPath.** It is emulated in the selftest,
  not loaded.
- **Whether `ScatterRuinsSimple` and `AncientUtilityBuilding` place more defs than the census resolves.** Both are
  listed as UNRESOLVED: furniture conditions, and the default Wall/Door.
- **Whether the roster rows are the owner's taste.** For example, chembarrels and razor wire are kept, and the
  hydrant is kept under its vanilla label.

## What I did not test
- No game load, no arrival map, no screenshot, no `jawa/list_things`. That is the live step, noted on the item
  (`needs bridge`).
- Existing maps are not migrated. A map generated before this change (e.g. the one in
  `world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`) keeps its trucks; the shipped arrival map must be
  generated fresh.
- New art for the 59 kept defs that keep their vanilla look (crates, containers, cranes, barriers, ruins): their labels carry no earth
  vehicle nouns, so they were left as vanilla.
