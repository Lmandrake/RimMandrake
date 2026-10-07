# Full-list crash 2026-10-07 — BigAndSmall RaceFuser NRE → mods reset

Log copy: `/tmp/claude-1000/-home-mandrake-rm-bench/6a6f7a30-78db-4977-acaa-88c9d03de745/scratchpad/Player.log` (14:30 copy; scratch, not durable).

## Symptom
Player.log l.11839: "Caught exception while loading play data ... Resetting mods config", NRE in
`StatExtension.GetStatValueAbstract` <- `BigAndSmall.RaceFuser.MergeStatDefValues` [IL 0x2ff].

## RaceFuser.MergeStatDefValues — what is null (MEASURED)
Decompiled BigAndSmall 1.6 (`ilspycmd`, `D:\Luke\dev\_rmscratch\bs\RaceFuser.cs` / `.il`).
IL 0x2ff is the statement start of
`SetStatBaseValue(new, StatDefOf.ToxicEnvironmentResistance, Max(GetStatValueAbstract(secondary, StatDefOf.ToxicEnvironmentResistance), ...))`
(0x2d7–0x2fa = ToxicResistance, completed). Engine (RimSage): `GetStatValueAbstract => stat.Worker.GetValueAbstract(def, stuff)`;
NRE at 0x0 with no `get_Worker` / `StatWorker` frame ⇒ **`stat` is null**: `StatDefOf.ToxicEnvironmentResistance` was
never bound because the Core StatDef `ToxicEnvironmentResistance` was DISCARDED at def load.
Not the ThingDef, not a statBases entry — any fused race trips it. HugeThings is not implicated.

## Culprit def / mod (MEASURED)
Player.log l.894: `Exception loading def from file Stats_Pawns_General.xml: Could not find type named
RimMandrake.Scarlands.RM_StatPart_GlowerShield` — our Warscar patch
`src/RimMandrake/Scarlands/Patches/RM_GlowerShielding.xml` (commit 4b432de26, WARSCAR_AEROSOL_SCREEN_1 part 9)
adds that StatPart to Core's `ToxicEnvironmentResistance`. The type is missing because the **game-folder
Warscar DLL is stale**:

| DLL | size | has RM_StatPart_GlowerShield |
|---|---|---|
| repo `src/RimMandrake/Scarlands/Assemblies/RimMandrake.Warscar.dll` (sha256 24b6594f…, matches .srchash) | 165,888 | yes |
| game `...\Mods\RimMandrake.Biomes\Biomes\Warscar\Assemblies\RimMandrake.Warscar.dll` (mtime 08:30) | 147,456 | **no** |

The XML reached the game (08:31–08:35) but the DLL builds of 08:35 / 08:39 (d51eb5f71, 54ef134c2) never did.
Same cause explains `RM_CompProperties_GlowerShield`, and the RM_JobDriver_/RM_WorkGiver_ *Ring missing-type errors.
The plan's "in game, not in repo" files are NOT stale: they live in `src/RimMandrake/Scarlands` (compose key Warscar)
and the current plan shows them identical; only `RM_Aluun.png` / `RM_Hessal.png` are game-only.
Why the 14:05 apply skipped the DLLs is INFERRED (likely game held them locked → copy() "FAILED to write"); the
current dry-run still lists `~ Biomes/Warscar/Assemblies/RimMandrake.Warscar.dll` plus GelatinousSlime, Wasteland
and EnvironmentalHazards DLLs.

Design fragility (not fixed): one missing type in a patch on a CORE StatDef deletes that StatDef for every mod.

## Fix
- Deploy, game DOWN (no rebuild needed — repo DLL matches its srchash):
  `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply` — check no "FAILED to write".
- Source fix committed: `RM_RingSalvageJobs.xml` used `<iconTex>` on DesignationDef (no such field;
  log l.947) → `<texturePath>`.

## Game-folder prune owed
Nothing causal. Optional cosmetic: `--compose biomes --prune` would remove only
`Biomes/TerminalBiomes/Textures/Things/Pawn/Animal/RM_Aluun/RM_Aluun.png` and `RM_Hessal/RM_Hessal.png`.
ModsConfig must be restored to the full list (it was reset to 6).
