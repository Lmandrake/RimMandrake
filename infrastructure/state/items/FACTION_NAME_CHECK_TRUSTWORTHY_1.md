## spec
Two companion fixes are built and **not deployed** — the game was up and the assembly is
locked. Both ride `NEXT_RELOAD.md` §1.0 step 1:
`python.exe src/RimMandrake/bridgetools/build.py --gm --apply`.

| fix | commit |
|---|---|
| `world_lint`'s `landBiomeSubmerged` no longer counts a `Lake` below sea level as submerged land | `dbfe46d` |
| `faction_name_get`'s `isGenerated` compares against the AUTHORED name, and `clear` restores it instead of the label | `37ac949` |

⚠️ **Confirm the deployed companion is the one carrying these** before believing any number
below. A stale companion and a working fix look identical from the bridge.

🔴 **`FACTION_NAMES_ARE_GENERATED_1` MUST NOT BE WORKED UNTIL THIS DEPLOY LANDS.** It aims
`faction_name_set action=clear` at whatever `generatedCount` reports, and against the OLD
companion that clears nine deliberately authored names — the Galactic Empire's and the
Junkers' among them — by overwriting them with `defLabel`.

## verify
On a live world, 578 mods:

    jawa/world_lint          -> landBiomeSubmerged, lakesAboveSeaLevel, waterBiomeOnRaisedLand
    jawa/faction_name_get    -> generatedCount, generatedOverAuthoredCount

then force a genuine submerged-land case and confirm the lint still FIRES:

    jawa/world_tile_set  {"tiles":"<a Desert tile>","elevation":-5}
    jawa/world_commit ; jawa/world_lint

## criteria
- `landBiomeSubmerged` reads **0** with the Scald at −30, and **1** with one Desert tile
  forced to −5 — narrowed, not disabled. `lakesAboveSeaLevel` and `waterBiomeOnRaisedLand`
  both still read 0.
- `faction_name_get` reports **0** for `generatedOverAuthoredCount` where the twelve authored
  factions wear their `fixedName`, and still reports the ~15 third-party factions carrying no
  `fixedName` under `generatedCount`. The nine known false positives — `Empire`,
  `Jawa_Junkers`, `PirateYttakin`, `DV_PirateKeshig`, `AG_XenohumanPirates`,
  `CannibalPirate`, `BS_Muspelheim`, `BS_Niflheim`, `BS_OgreFaction` — must all read
  `isGenerated: false`.
- Each row carries `authoredName` and `hasFixedName`.
