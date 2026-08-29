# BUG_TURRET_ART_REDO_1 — redraw the cartoonish bug turrets

Owner, 2026-08-29 (verbatim): "Gotta redo the art on those cartoonish bug
turrets." Targets: VFEI2_Vilelobber, VFEI2_Thornworm (2x2) and
VFEI2_Thornspitter (1x1) — all three RULED into the Geonosian Foundry Hive
register on the turret canon (turret_register.json), with a proposed sonic
re-projectile still pending the owner's word.

Route: `generating-rimworld-sprites` (reference-matched canvas/alpha/silhouette,
offline validator) against the hive's existing art register; the current
textures live in VFE Insectoids 2 (texPaths in turret_register.json rows).
Deploy as a retexture patch, NOT an edit to the donor mod. Prove in-game per
the skill (texture binds by texPath — [[texture-binds-by-texpath-not-defname]]).
