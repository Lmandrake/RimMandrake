## spec
Graffiti scene `sc_weathered_raid_mark` (`src/RimMandrake/Graffiti/validation.py::scene_weathered_raid_mark`) starts with
"faction A's raid exit mark unroofed on the outer wall and a same-age A mark under a roof". No probe stages the roofed twin:
`RM_GraffitiProof.RaidExit` tags exterior walls only (`RM_GraffitiProof.cs:219`), `HostileThought` paints with a pawn of
`Enemy()`, a RANDOM enemy faction each call (`RM_GraffitiProof.cs:100,294`), and `jawa/static_call` cannot bind
`Filth_Mark.MakeMark`'s `Faction`/optional parameters to the raid's faction. So the scene's start component raises
`MISSING TOOL` naming this item.

Build: a public static probe in `RM_GraffitiProof.cs`, run right after `RaidExit` at the same tick, that paints one mark
by a pawn of the last raid's faction (`raidFaction`) on an interior face of the roofed room `BuildInterior` made
(`InInterior`, roofed), and answers its thing id, def and cell. Then in `scene_weathered_raid_mark` set `twin = (id, mark)`
from it (replacing the MISSING TOOL raise), and build the DLL with `winbuild.py Graffiti`. The live run stays UNRUN until a
bridge sitting (`modcheck run Graffiti`, chain `scene_weathered_raid_mark`).

Found by RIMMANDRAKE_RESTORE_GRAFFITI_RAID_WEATHER_CHECKS_FROM_BUNDLE.

## verify
Watched failing 2026-11-15 on the commit that filed this (AssertionError); expected `PASS` (1 pass):

    python3 -c "
    s=open('src/RimMandrake/Graffiti/validation.py').read().split('def scene_weathered_raid_mark')[1].split('@suite.chain')[0]
    assert 'MISSING TOOL' not in s and 'twin = (' in s, 'scene_weathered_raid_mark still raises MISSING TOOL / never stages its twin'
    print('PASS')" && python3 src/RimMandrake/Utils/winbuild.py Graffiti >/dev/null && echo BUILD-OK
