# Cold load 2026-09-21 — the strings that decide each entry, written BEFORE launching

Per `skills/rimworld-load-round` §2. If an entry is not decidable by a string written here,
it is not being tested this load.

Mod list: the full list, **620 active** (`ModsConfig_full_plus_gelatinousslime_2026-09-21.xml`).
Everything below is deployed and `VERIFIED in sync` as of launch.

## Entry 1 — Pyrelands rename (`PYRELANDS_DEFNAME_RENAME_1`)

| verdict | string in `Player.log` |
|---|---|
| ❌ FAIL | any occurrence of `RM_FE_Pyrelands` at all — the old name must be gone from the loaded game |
| ❌ FAIL | `Could not resolve cross-reference` … `RM_Pyrelands` |
| ❌ FAIL | `Could not find a type named` … `PyrelandsTuning` / `WildPlantAllowlist` / `RM_PyrelandsDensityEnforcer` |
| ✅ PASS | zero of the above, AND `RM_Pyrelands` appears as a resolved BiomeDef |

🔑 The three C# string literals are the risk. A wrong one **compiles clean and silently does
nothing** — so silence in the log is NOT pass on its own; the def must be seen resolved.

## Entry 2 — GelatinousSlime activation (`OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1`)

| verdict | string |
|---|---|
| ❌ FAIL | `mandrake.rm.gelatinousslime` absent from the `Loaded mods` block |
| ❌ FAIL | any `XML error` or `Could not resolve cross-reference` naming a `RM_Titanoslime*` def |
| ✅ PASS | present in the loaded list with no errors attributed to it |

⚠️ Magenta rendering is **expected** — the missing-texture colour, not a defect. Do not log it
as a failure.

## Entry 3 — Titanoslime permanent growth (`TITANOSLIME_SLIME_BIOME_1`)

⛔ **Not decidable from the log.** Growth permanence is runtime behaviour over time; the log
can only show the def loaded. This entry needs a bridge test, not a load — spawn one, feed it,
confirm it does not shrink, and confirm the shipped default of
`SlimeSettings.titanoslimeReversible` reads **false**.

## Entry 4 — Founders importer (`FOUNDERS_IMPORTER_OWED_1`)

Decided by **loading `FOUNDER_IMPORTER_LIVETEST_2026-09-21.rws`**, not by the startup log.

| verdict | check |
|---|---|
| ❌ FAIL | `Could not load reference to` … on any gene or pawn in that save |
| ❌ FAIL | fewer than 6 founders carry the `Wimp` trait |
| ✅ PASS | all 6 carry `Wimp` |

🔑 `Could not resolve cross-reference` (def loader, fixable by mods) is a DIFFERENT error from
`Could not load reference to` (Scribe — the save holds a dead name, no mod change fixes it).

## Standing expected-failure signatures — pre-existing, NOT caused by this load

⚠️ Write these down so they are not mistaken for regressions. Any error matching a known
standing failure is noise; anything else is signal.

## Harvest

⚠️ `launch_and_wait.sh` **exits 0 on TIMEOUT at 280 s**, and a full-list cold load has
measured **21 minutes**. The exit code is not the signal — grep the log for the bridge line.
⚠️ Copy `Player.log` out before the next launch overwrites it.
