## spec
Code-review reachability audit found `RUT_FireHawk` and `RUT_FurnaceBeast`
(`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`)
declared `graphicClass: Graphic_Multi` on every lifeStage but shipping only
one PNG each (`FireHawk.png`, `FurnaceBeast.png`) — confirmed east-facing by
the original job comment and by eye. `Graphic_Multi` without `_south`/
`_north` suffixes falls back to drawing the bare/east file from every
rotation: technically loads, visibly wrong (never turns).

Queued two new artpipe jobs per creature (south, north) via
`src/RimMandrake/Utils/artpipe/fill_queue.py`, same prompt/style as the
original `pyrelands_firehawk_v1`/`pyrelands_furnacebeast_v1` jobs plus an
explicit "same individual creature, different angle" instruction in
style_notes. All 4 generated clean (`infrastructure/artpipe/done/
pyrelands_{firehawk,furnacebeast}_v1_{south,north}.json` + manifests,
`status: ok`, no validator since there's no reference).

Renamed the existing east PNGs (`git mv`) to `FireHawk_east.png` /
`FurnaceBeast_east.png` and added `_south`/`_north` alongside, straight into
this mod's own `Textures/` tree (own mod, not a donor override). Deployed via
`deploy_custom_mods.py --apply --prune --mod UtinniPatches`.

## verify
Live-verified on a quicktest map (`rimworld/start_debug_game_ready`) with a
temp mod list = `ModsConfig.MINIMAL.xml` + `mandrake.rm.weathersuite` +
`mandrake.rut.patches` (saved as
`infrastructure/state/modlists/ModsConfig.PYRELANDS_FACING_TEST.xml`;
pre-test live config backed up to
`ModsConfig_before_pyrelands_facing_test_2026-09-11.xml`). Spawned 3 of each
kind (faction `none`), locked rotations to south/east/north
(`jawa/set_pawn_rotation`), screenshotted and cropped each — all 6 read as
visibly distinct poses matching their rotation (FireHawk: south = chest/tail
toward viewer, east = beak right, north = back; FurnaceBeast: south = face
toward viewer, east = horn right, north = back with horn visible from
behind). No `Config error` lines for either def in `Player.log`.

⚠️ Did not restore the pre-test `ModsConfig.xml` afterward: another FOUNDRY
window took the bridge mid-test (`LOCKJAW_ART_WIRE_IN_1`, 17:45:51Z) and
relaunched the game under its own list before I could hand it back — I never
called `rimflow bridge take` myself before driving the live game (should
have). Left the live config alone rather than yanking it out from under
their active session; the backup file above still has the true pre-test
state for whoever restores the full list before the owner plays.

## criteria
Both creatures render a real directional sprite set (3 distinct facings) in
game, confirmed by looking, not inferred from a clean deploy plan.

## Watch out
No reference image existed for the south/north jobs (only the east PNG),
so this relies on prompt-text consistency (same description + explicit
"same creature, different angle" instruction) rather than an image-to-image
edit — matches the precedent set by `kreetle_v1_south`/`_north` (also
prompt-only, no reference). Screenshots (with pixel-crops) are not committed
to the repo; the visual evidence lives in this session's transcript. Anyone
re-verifying should just spawn + screenshot again — it costs a quicktest map,
not a cold load.
