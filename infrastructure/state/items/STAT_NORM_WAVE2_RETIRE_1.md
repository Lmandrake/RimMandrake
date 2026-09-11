# STAT_NORM_WAVE2_RETIRE_1 — Wave 2 remainder executed

Owner-ruled 2026-09-11 (Wave 2 of the stat-normalization audit,
`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`).

## Ported then retired (donor content absorbed, defName-preserving, into src/RimUtinni/UtinniPatches)

- `joe.cephaloids` — all 10 defs (Landopus/Cephalope/Nautilant + eggs/bodies + custom body parts)
- `vanillaexpanded.vplantsesucculents` — all 10 desert-succulent plants + research project/tab
- `vanillaexpanded.vaewaste` — only `VAEWaste_Megatardi` (confirmed sole cast species via
  `cast_assignment.csv`/`BiomeCast_Ashkarr.xml`, weight 0.18 in Wasteland); its DLL
  (tox-cloud death action, toxic-ingestion effect) copied into the mod's own Assemblies/

## Verify-then-retire (no port needed)

Megafauna, MythicAges, FFAnimals, LittleCritters, DizzyEevee.BetterCrossbreeding +
DizzyEevee.RHenG — each cleared a fresh roster+save cross-check against the live
canonical save (`CANONICAL_ASHKARR_2026-09-09.rws`): zero placed `<def>` instances,
`race.wildBiomes` entries only ever appeared in the eviction file, never the real
cast-add file. No cast find; nothing escalated.

## Verification

- `validate_patch.py` (Data+Mods+workshop): Cephaloids/Succulents 0 errors. VAEWasteMegatardi
  0 errors except one texPath flag on `VAEWaste_ToxicLeather` — confirmed a scanner blind spot
  (packed into resources.assets like every vanilla leather), not a real gap.
- ModsConfig.xml (live) and ModsConfig.FULL.LATEST.xml: 9 packageIds removed, diffed
  token-by-token against a backup (`infrastructure/state/modlists/ModsConfig_before_stat_norm_wave2_retire_2026-09-11.xml`)
  — exactly those 9, nothing else touched. 5 stale `loadAfter` entries cleaned from
  UtinniPatches/About.xml.

## Owed

Live cold-load to confirm the retirement loads clean — next natural restart, not solo-forced.
