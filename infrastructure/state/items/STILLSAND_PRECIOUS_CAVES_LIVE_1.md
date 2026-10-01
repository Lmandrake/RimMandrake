# STILLSAND_PRECIOUS_CAVES_LIVE_1 — see the rare rock and its cave on real maps

Split from `STILLSAND_PRECIOUS_CAVES_1`, which built the gen steps offline (`mandrake.rm.stillsand`:
`Source/RM_PreciousCaves.cs`, `Defs/MapGeneration/RM_PreciousCaves.xml`,
`Patches/RM_PreciousCaves_BiomeGenSteps.xml`). The geometry is covered offline by
`src/RimMandrake/Utils/selftest_precious_caves.py`; nothing has run in the game yet.

## spec

1. Deploy `Stillsand` (it now depends on `mandrake.rm.environmentalhazards`).
2. Generate ten `RM_Stillsand` quicktest maps and read `Player.log` for the
   `[Stillsand] precious cave:` and `[Stillsand] precious cave roll:` lines.
3. Look at each cave: mouth on the shade side, thick roof over the chamber, the row's contents present.

## criteria

- Across ten Stillsand quicktest maps with rock, at least eight carry a cave whose mouth faces away
  from the sun; the table rolls are logged.
- A guzzka lair spawns the guzzka on its clutch.
- Nothing spawns a cave outside rock.
- The "Rock island" letter fires once on the player's home map and names the outcrop and its bearing.
