## spec
`RUSTCATHEDRAL_WORN_BIT_ARC_1` shipped proved offline only: both DLLs build, `selftest_rustcathedral_wornbit.py` and
STATIC pass. Nothing has been loaded in a game. Deploy mandrake.rm.rustcathedral (or the Biomes composition) plus Rites
and UtinniPatches on a minimal list, then run:
- `validation.py` chain `worn_bit` (src/RimMandrake/RustCathedral) and `worn_bit_gods` (src/RimUtinni/Rites).
- A look at what no proof reaches: the float-menu orders on a wild borehulk, the job drivers with two real colonists,
  the yard dialog on a real caravan, the favour at the comms console, the kept hulk's gizmos, a save and reload mid-arc.
Read the FIRST exception in Player.log: an unknown XML field in the new defs or a DefOf miss shows only at load.

## criteria
Every `worn_bit` and `worn_bit_gods` row PASS on one run, no red log line naming RM_WornBit, and any bug found fixed.
