## spec
The def dump changed layout — it is now `DefDump/captures/<ISO>/{defs/,manifest.json,animals.json}`
plus a top-level `defs.sqlite` — and **at least two tools still expect the old
`DefDump/defs/*.json` root**. Both fail in the worst way: they report something that reads as
a real finding about the game.

| tool | what it does when pointed at the DefDump ROOT | truth |
|---|---|---|
| `src/RimMandrake/Utils/cast_to_xml.py` | `FAIL: no TraitDef.json at …` and exits | the tool is fine; it wants `captures/<id>/defs` |
| `skills/rimworld-modding/scripts/validate_patch.py --live` | prints `no defs/ under …DefDump; live checks skipped` and **passes the patch anyway** | 🔴 the `--live` half of every verification silently did not run |

🔴 **The second one is the dangerous one.** Several queue items specify verification as
*"validate with BOTH `--defs` and `--live`"*. Pointed at the root, `--live` degrades to a
one-line notice in a wall of output and the run still ends `OK - 0 errors`. **Every `--live`
check run against the root since the layout changed proved less than its author thought**,
including one in this session (`HORROR_WASTES_COLD_TERRAIN_1`, worked around by querying
`defs.sqlite` by hand).

## fix
Teach both tools to resolve a DefDump root to its newest capture — `captures/*/defs`, picking
the highest ISO name — and to say which capture they chose. ⛔ **Do not just fix the call
sites.** The next person will pass the root too; the root is the obvious thing to pass.

⚠️ **Choosing the NEWEST capture is not automatically right.** Measured 2026-08-23: the newest
capture, `2026-08-23T07-12-04Z`, was taken with the Star Wars donor mods switched OFF, which is
why `gen_races_mod.py` refuses to write (it would ship 63 species against 69 on disk). A
resolver must report the capture's `modCount` and let the caller refuse it, not silently pick
the latest. The known-good full capture today is `2026-08-21T22-44-59Z` at 578 mods.

## verify
- `python3 src/RimMandrake/Utils/cast_to_xml.py --dump "<DefDump root>"` runs and names the capture it used.
- `validate_patch.py --live "<DefDump root>"` performs live checks, and **says so**, rather than skipping.
- 🔑 A deliberately wrong defName in a test patch is CAUGHT by `--live`. That is the only proof the live half ran.

## criteria
- [ ] Both tools accept the DefDump root and resolve it to a capture.
- [ ] Each prints the capture id and its modCount.
- [ ] `--live` never skips silently: no capture found must be a loud refusal, not a notice.

## Watch out
⚠️ **`defs.sqlite` is a THIRD shape**, and it is not a drop-in for either — it does not
serialise `Vector2`/`Color` (`drawSize`, `colorSpectrum` read null), nor dictionary-keyed
custom fields (`wildBiomes`, `wildPlants`, `terrainsByFertility` all read null), nor
`TerrainDef` bodies. Anything needing those must read the mod XML on disk.
