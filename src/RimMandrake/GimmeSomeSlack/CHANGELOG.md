# Changelog

Version here must match `<modVersion>` in `About/About.xml`. Never deployed (`.md` is skipped by deploy_custom_mods.py).

## 1.0.0 — 2026-10-15 (release candidate, not published; repackaged 2026-10-16)

Package DLL: `Assemblies/RimMandrakeGimmeSomeSlack.dll` sha256 `5e523c88…cbce6fa3` (its `.srchash` `# dll:` line),
built from 2b215d4589. A DLL whose hash differs from this line is not the packaged one: repackage.

- 2026-10-16 repackage: every Harmony patch belongs to a Mod Settings feature, and a patch that fails to apply
  switches only its feature off (the player's own choice is kept in the settings file); Harmony applies after both
  settings files load; with Overhead lines off the anchor style menu no longer opens; a conduit end beside a powered
  device draws one cord, not a second sparking end.

- First packaged release: player-facing description, `About/Preview.png` (built by
  `src/RimMandrake/Utils/build_mod_previews.py`), modVersion, and Harmony plus all five expansions declared as requirements.
