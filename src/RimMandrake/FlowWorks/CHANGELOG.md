# Changelog

Version here must match `<modVersion>` in `About/About.xml`. Never deployed (`.md` is skipped by deploy_custom_mods.py).

## 1.0.0 — 2026-10-15 (release candidate, not published; repackaged 2026-10-16)

Package DLL: `Assemblies/RimMandrakeFlowWorks.dll` sha256 `557d3a9a…c29c68eb` (its `.srchash` `# dll:` line),
built at 31f335066b. A DLL whose hash differs from this line is not the packaged one: repackage. Still not signed off
by the owner (review walk in progress).

- 2026-10-16 repackage: liquids measured in litres; water settles to one flat level (new setting "Water settles to one
  flat level", default on) instead of 1,0,1,0 stripes; slime slips and slides; sluice gates turn with the canal like
  doors; map source/sink controls; four tank and container styles; hose joints; spill filth lands on soil.

- First packaged release: player-facing description, `About/Preview.png` (built by
  `src/RimMandrake/Utils/build_mod_previews.py`), modVersion, and Harmony plus all five expansions declared as requirements.
