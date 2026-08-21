## spec
`src/RimMandrake/Utils/make_vehicle_mask.py:67` inserts
`src/RimMandrake/skills/...` into `sys.path`. There is no such directory, so
`import pnglib` fails — which breaks **both**
`DesertVehicleReskin/Source/build_eopie_sled_north.py` and
`...south.py`, since each imports this module.
Found by the 2026-08-20 cleanup audit
(`infrastructure/output/audit_2026-08-20_code.md`). **Fix it; do not
quarantine it** — it has live callers, it is just pointing at a path that
moved.

## verify
`python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/Utils'); import make_vehicle_mask"`
succeeds, and both sled build scripts import clean.

## criteria
the two sled scripts run again.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20. `make_vehicle_mask.py` now resolves `pnglib` at
`<repo root>/skills/generating-images/scripts` — the old path went up ONE level
to `src/RimMandrake/skills`, which has never existed. It also raises a named
`ImportError` if the directory is missing, so the next move fails loudly instead
of silently.
verify output:
  `make_vehicle_mask imports clean; pnglib from
   /mnt/d/Luke/dev/Rimworld/skills/generating-images/scripts/pnglib.py`
⚠️ **THE ITEM'S BLAST RADIUS WAS WRONG.** It says the break took down
`build_eopie_sled_north.py` and `south.py` *"since each imports this module"*.
**Neither imports it.** Grepped all three sled builders: `make_vehicle_mask` is
named only inside COMMENTS explaining the warm-hide rule. The path bug was real;
the two casualties were not.
🔴 **A separate and larger problem, found while checking: none of the three sled
builders can run here at all.** All three open with `from PIL import Image,
ImageDraw` and **Pillow is not installed** in this Python (`ModuleNotFoundError:
No module named 'PIL'`), nor is there a Windows Python beside it carrying one.
`refresh.py`'s header lists contact sheets as "offline + Pillow, seconds", so
something used to have it. Not fixed — installing a dependency is not mine to
decide — but nobody should record the sled scripts as working until it is.
