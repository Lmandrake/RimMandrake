# GELATINOUSSLIME_FIRST_LOAD_ERRORS_1 — the first load with the mod active found three faults

## context

`GelatinousSlime` was built, deployed and **absent from `ModsConfig`** until 2026-09-21,
when the owner ruled it active (`OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1`). The first cold load
with it enabled (620 mods, `Transient/Player.log.coldload_2026-09-21`) surfaced faults that
were invisible while the mod was inert. **This is the load doing its job** — none of these
is a regression.

## the faults

**1. `wildGroupSize` is in the wrong element — 2 occurrences.**
`wildGroupSize` is a **`PawnKindDef`** field, not a `RaceProperties` field. Inside `<race>`
it produces
`XML error: <wildGroupSize>1~1</wildGroupSize> doesn't correspond to any field in type RaceProperties`.
MEASURED by parsing each file and testing enclosure:

| file:line | verdict |
|---|---|
| `src/RimMandrake/GelatinousSlime/Defs/ThingDefs_Races/Gelatid.xml:92` | inside `<race>` — **error** |
| `src/RimMandrake/GelatinousSlime/Defs/ThingDefs_Races/Titanoslime.xml:94` | inside `<race>` — **error** |
| `src/RimMandrake/GelatinousSlime/Defs/ThingDefs_Races/Titanoslime.xml:199` | in the `PawnKindDef` — correct, leave it |

⇒ Delete the two inside `<race>`. The `PawnKindDef` already carries the real one, so group
size is **not** currently broken in play — only the log is dirty.

**2. `[Def Error]: RM_Titanoslime`** in `Defs/ThingDefs_Races/Titanoslime.xml`. A ConfigError
means the def **loaded but is wrong**. ⚠️ Its detail line was not captured cleanly in this
pass — read it with
`python3 src/RimMandrake/Utils/harvest_log.py --log <log> --show configerror` before
guessing, and check `check_config_errors.py` / the config-error baseline first, since that
tool classifies every line and nobody should re-derive it by eye.

**3. The mod's cure geography is inert** — `Defs/Patches/DryingBiomes.xml` is a patch file
under `Defs/`. Own item: `PATCH_FILES_UNDER_DEFS_INERT_1`.

## Watch out

- ⚠️ **Magenta rendering is expected and is NOT a fault** — the mod has no art yet and
  magenta is the missing-texture colour.
- ⚠️ The permanent-growth change (`8b9483b2e`) is **not testable from a load** — it is
  runtime behaviour over time. Spawn one via the bridge, feed it, confirm it does not shrink,
  and confirm `SlimeSettings.titanoslimeReversible` defaults false.

## criteria

A cold load with GelatinousSlime active produces zero errors naming any `RM_Titanoslime`,
`RM_Gelatid` or GelatinousSlime file, and the cure geography is confirmed applied in game.
