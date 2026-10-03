# GLURRO 2026-10-03 (started)
- Census: no glurro in src/ or artpipe before (find: 0). Pit solvent item (GELATINOUSSLIME_PIT_SOLVENT_1) does not exist, so "rendered down in the slime pit" = butcherProducts RM_GlurroSalveConcentrate x1 (no station).
- Defs: Defs/ThingDefs_Races/Glurro.xml (RM_Glurro, TurtleLike, resistant, CompProperties_Milkable milkDef RM_GlurroSalve every 6d x2, wildAnimals 0.3 inline on RM_GelatinousSlime); Defs/ThingDefs_Items/GlurroSalve.xml (RM_GlurroSalve strength 0.5, RM_GlurroSalveConcentrate 0.75; usable on a targeted pawn like the antidote); Defs/HediffDefs/GlurroSalved.xml (severity = strength, decays 0.25/day). All // INVENTED.
- Hook (C# needed: no vanilla stat carries it): Source/GlurroSalve.cs (in csproj) + HediffComp_Slimification multiplies GROWTH by (1 - severity, capped 0.8). Never reverses/stops; antidote stays the only cure.
- Toggle: SlimeSettings.glurroSalve (default true) gates the slowing; FIELDS/settings_flip/mock DEFAULTS updated.
- Validation: glurro_salve_defs (offline XML + live foundCount 3), glurro_salve_slows_growth (live: salved pawn on slime at ~half speed; UNMEASURED on a drying biome). Mock fault nosalve. Selftest: 53 clean / 25 faults / 0 problems.
- Art: 4 jobs filed (Glurro S/E/N, GlurroSalve); the concentrate has no CSV row, no art queued (3 texPath WARNs; magenta until generated).
- Not run: live (milk produce, salve on real pawn). Build: winbuild GelatinousSlime ok.
