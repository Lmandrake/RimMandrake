# Changelog

Version here must match `<modVersion>` in `About/About.xml`. Never deployed (`.md` is skipped by deploy_custom_mods.py).

## Unreleased

- 2026-10-16: River Colors merged in (was its own mod, `mandrake.rut.rivercolors`, `src/RimUtinni/RiverColors`):
  the planet-map river gradient now lives in `Source/RiverColors/`, its settings are the "River colours" section of
  this mod's settings (`riverColors_`-prefixed keys; old standalone values are not imported), and its check is
  `selftest_flowworks_river_colors.py`. Remove `Mods\RiverColors` and `mandrake.rut.rivercolors` from mod lists.

## 1.0.0 — 2026-10-15 (release candidate, not published; repackaged 2026-10-16)

Package DLL as repackaged 2026-10-16: `Assemblies/RimMandrakeFlowWorks.dll` sha256 `c3dbac22…fa83fc`, built at fead0c39b9cd (canal level-solve fix f11976b49; live-proved 2026-10-16: calm 61/0/0, river extensions 20/0/1). The DLL has been rebuilt many times since; the current one is the `# dll:` line of its `.srchash`, and the next repackage rewrites this line. Still not signed off
by the owner (review walk in progress).

- 2026-10-16 repackage: liquids measured in litres; water settles to one flat level (new setting "Water settles to one
  flat level", default on) instead of 1,0,1,0 stripes; slime slips and slides; sluice gates turn with the canal like
  doors; map source/sink controls; four tank and container styles; hose joints; spill filth lands on soil.

- First packaged release: player-facing description, `About/Preview.png` (built by
  `src/RimMandrake/Utils/build_mod_previews.py`), modVersion, and Harmony plus all five expansions declared as requirements.
