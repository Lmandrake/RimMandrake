# UtinniPatches orphan audit — 2026-09-29

Item: `UTINNIPATCHES_ORPHAN_AUDIT_1`, caused by `BLUEDESERT_ORPHAN_LOAD_CRASH_1`.
Follow-on filed: `ROTSPOREKIT_GHOST_MOD_1` (see bottom).

## Method

1. `python3 src/RimMandrake/Utils/deploy_custom_mods.py` (plan only, no `--mod` filter)
   — walked all 133 standalone repo mod folders. Then
   `deploy_custom_mods.py --compose biomes` — walked the composed
   `RimMandrake: Baroque Biomes` mod (1129 files, folds in 29 per-biome dev
   folders including Miasma/TheSump/BlueDesert/TheRot at `compose_wave: 2`).
   Every "in game, not in repo" (`-`) line across both runs is an orphan.
2. Read `src/DEPLOY_HOLD.txt` first — none of the 39 orphans found matched a
   hold pattern (holds are for repo-only files awaiting art/rulings; these are
   the opposite direction, game-only files with no repo source at all).
3. For each orphan: read its content, `grep` the whole repo and the whole
   deployed `Mods/` tree for its defName(s) and basename, and — where a
   same-named file existed elsewhere in the repo — diffed defNames between the
   stale copy and the current one to confirm genuine duplication before
   deleting anything.
4. Game confirmed down (`tasklist.exe`) before any file operation.

## Result: 39 orphans found, all under two mods

**UtinniPatches (`mandrake.rut.patches`): 37 orphans.**
**LuminousPigment (`mandrake.rm.luminouspigment`): 2 orphans.**
**RimMandrake.Biomes (composed): 0 orphans** — fully in sync.
**All other 131 standalone mods: 0 orphans.**

## Classification

### Class A — stale duplicate-defName residue (30 files), UtinniPatches

`Miasma`, `TheSump` and `BlueDesert` used to be authored directly inside
UtinniPatches. They were split out into their own dev folders and now compose
into `RimMandrake.Biomes` (active, `mandrake.rm.biomes`). The split moved the
repo source but nobody pruned the OLD copies from the deployed game folder —
so **the same defName has been loading from two active mods simultaneously**:
UtinniPatches' stale copy and RimMandrake.Biomes' current one. Verified by
diff/defName-comparison for every one of these; a sample:

| file | defName(s) | duplicate now lives at |
|---|---|---|
| `Defs/HediffDefs/RUT_MiasmaExposure.xml` | `RUT_MiasmaExposure` | `Biomes/Miasma/...` |
| `Defs/TerrainDefs/RUT_TarMoat.xml` | `RUT_TarMoat` | `Biomes/TheSump/...` (byte-identical) |
| `Defs/EffecterDefs/RM_KrissekHalo.xml` | — (effecter) | `Biomes/BlueDesert/...` |
| `Defs/ThingDefs_Items/RM_ColdWax.xml` | `RM_ColdWax` | `Biomes/BlueDesert/...` |
| ...plus 26 more (GameConditionDefs, remaining HediffDefs, IncidentDefs, LotteryTableDefs, MapGeneration GenSteps, ThingDefs_Buildings/Items/Plants, ThinkTreeDefs, WeatherDefs, a Keyed translation file, and 4 Patches register/wiring files) | all confirmed `MATCH` | `Biomes/Miasma/...` or `Biomes/TheSump/...` |

Full list: `RUT_GradientSurge`, `RUT_MiasmaWeatherLock`, `RUT_SumpDuskLock`,
`RUT_MiasmaExposure`, `RUT_Miasma_FeverForgedMinor`, `RUT_Miasma_HardenedImmunity`,
`RUT_Miasma_StrangeTier`, `RUT_StrandedDeformation`, `RUT_Surge`,
`RUT_DigStratumTable`, `RUT_Miasma_CrecheScatterer`, `RUT_Miasma_GradientAxisGenStep`,
`RUT_TarMoat`, `RUT_CrecheMarker`, `RUT_DigShaft`, `RM_ColdWax`, `RUT_WickStem`,
`RUT_Plant_Wick`, `RUT_ThinkTree_SumpMouseWander`, `RUT_MiasmaWeather`,
`RUT_SumpWeather`, `RUT_SurgeWeather`, `RUT_Miasma_Mechanics` (Keyed),
`RUT_Miasma_CrecheScatterer_Register`, `RUT_Miasma_ForgeOnSurvival`,
`RUT_Miasma_GradientAxis_Register`, `RUT_SumpDuskLock_BiomeWiring`,
`RM_KrissekHalo`.

**Action: REMOVED** — pruned from the deployed UtinniPatches copy. The
composed `RimMandrake.Biomes` copies are untouched and remain the sole source.

### Class B — dead placeholder content (4 files), UtinniPatches

`RUT_Placeholder_SumpMouse.xml` + `RUT_Placeholder_SumpMouseRace.xml` and
`RUT_Placeholder_GreentideGiantTree.xml` + its texture were explicitly
authored as throwaway mechanism-proof stubs ("PLACEHOLDER... NOT the real
roster giant... not wired into any GenStep", own file headers). Both have
since been superseded by real roster content — `TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml`
(9 real fauna) and `Greentide/Defs/ThingDefs_Plants/RM_Greatbole.xml`
respectively (the latter's own header explicitly says "It retires
`RUT_Placeholder_GreentideGiantTree.xml`"). Confirmed via strict
`<defName>` search: neither placeholder defName exists anywhere in the repo
any more, and nothing in the currently-deployed game (any mod) references
either placeholder's defName outside comments/precedent text.

**Action: REMOVED.**

### Class C — redundant patch, superseded by inline content (2 files), UtinniPatches

`Patches/WildAnimals_GreySea.xml` and `Patches/WildAnimals_TwilightSea.xml`
were authored 2026-09-25 to inject `RSW_Reefback`/`RSW_Lanternwhale` (the
Star-Wars-tier creatures, `mandrake.rsw.swbestiary`) into `RM_GreySea`/
`RM_TwilightSea` because those biome defs didn't carry a reefback/lanternwhale
yet. Since then, `SEA_BEASTS_TIER_RULING_1` added franchise-free `RM_Reefback`
and `RM_Lanternwhale` **inline** into `RM_GreySea.xml`/`RM_TwilightSea.xml`
themselves (confirmed: both now ship `<RM_Reefback>0.005</RM_Reefback>` /
`<RM_Lanternwhale>0.005</RM_Lanternwhale>` directly). With the stale patches
still deployed, both seas were spawning **two** conceptually-equivalent giant
creatures (the RM_ one inline, plus the orphan patch's RSW_ one) at the same
commonality — not intended, and not what the current repo authors.

**Action: REMOVED.**

### Class D — inert dead patches, target a renamed def (2 files), UtinniPatches

`Patches/RotGuardianGroves_WildSpawn.xml` and `Patches/RotPaleTree_WildSpawn.xml`
both target `/Defs/BiomeDef[defName="RUT_TheRot"]/wildPlants`. `RUT_TheRot` no
longer exists as a defName anywhere in the currently active load — TheRot's
biome was renamed `RM_TheRot` as part of its own `RM_` migration
(`RM_TheRot_Biome.xml`). Confirmed no BiomeDef named `RUT_TheRot` exists in
any active mod, including the still-active `RotSporeKit` ghost mod (see
below) — only incidental prose mentions the string. `PatchOperationFindMod`/
`PatchOperationAdd` on a missing xpath target is a silent no-op ("a patch that
matches nothing logs nothing"), so these two were functionally inert, not
crashing anything — but they are stale residue referencing a dead defName,
exactly the class this audit exists to catch before some future change makes
`RUT_TheRot` resolve again unexpectedly.

**Action: REMOVED** (cleanup; was already harmless).

### Class E — superseded loose-art residue (2 files), LuminousPigment

`Textures/Things/Item/Resource/RM_Deepfire/RM_CrowncarpetFresh.png` and
`.../RM_Deepfire.png` are flat single-file PNGs left over from before both
items migrated to `Graphic_StackCount`'s folder-based art convention (repo now
ships `RM_Deepfire/RM_Deepfire/RM_Deepfire_a.png` and
`RM_Deepfire/RM_CrowncarpetFresh/RM_CrowncarpetFresh_a.png` — folders, not
loose files, at the same stem). `Graphic_Collection.GetAllInFolder` matches by
directory prefix, so the loose files are not picked up by the current
graphic and don't render; harmless disk waste.

**Action: REMOVED** (low-risk cosmetic cleanup, explicitly permitted by the
item brief for this class).

## Not touched — HELD files and stale-hold pattern warnings

27 `DEPLOY_HOLD.txt` patterns matched real UtinniPatches files this pass (11
still held — new art/rulings owed, untouched, correct). The full-sweep plan
also prints "9 hold pattern(s) matched NOTHING" for 9 `TheSump/...` entries —
this is **not** a defect: those holds are written for the composed path
(`Biomes/TheSump/...`) and correctly matched when checked via
`--compose biomes` (verified separately, 0 drift there). A plain `--mod`-less
plan run doesn't discover TheSump at all since it's folded into the compose
wave, so the warning is a false alarm from checking the wrong plan mode, not
a stale hold. Left as-is; not in scope for this item.

## The one thing bigger than a file orphan: RotSporeKit is a live ghost mod

While tracing why UtinniPatches' `RUT_SheenExposureLock.xml` was gated on
`mandrake.rut.rotsporekit`, found that packageId is **still ACTIVE** in the
live `ModsConfig.xml`, and its full folder — `Mods/RotSporeKit/`, ~130 files,
34 Defs + ~95 Textures — is **still fully deployed**, despite its own file
headers (and TheRot's own `RM_SheenExposureLock.xml`) stating it was
*dissolved* into `RimMandrake: The Rot` by `THEROT_RM_MOD_BUILD_1`. Every
defName was cleanly renamed `RUT_` → `RM_` during that absorption (no literal
duplicate-defName collision — verified 31-for-31 on `RotSporeKit_Flora.xml`),
and nothing currently active wires its content into any biome (the two
patches that did were Class D above, now removed) — so today it's dead
weight, not an active duplicate-spawn bug. But it is exactly the
`BLUEDESERT_ORPHAN_LOAD_CRASH_1` risk class: a whole "dissolved" mod nobody
actually retired from `ModsConfig.xml` or deleted from `Mods/`.

This is **outside `deploy_custom_mods.py`'s reach** — it only diffs
per-file within a mod folder that still has a repo counterpart, and
`RotSporeKit` has none (fully absorbed, no repo source at all), so no amount
of pruning UtinniPatches or the composed Biomes mod would ever surface it.

Filed as **`ROTSPOREKIT_GHOST_MOD_1`** (needs owner) rather than fixed here:
retiring it means editing `ModsConfig.xml` (both the live file and
`ModsConfig.FULL.LATEST.xml`) and deleting a whole deployed mod folder, and
before doing that someone needs to confirm the live campaign save
(`CANONICAL_ASHKARR_START`, ship at 17007) never saved a reference to an old
`RUT_`-prefixed RotSporeKit defName that would then dangle — a save-compat
check beyond this item's offline file-hygiene scope.

## Verification

Full re-run of `deploy_custom_mods.py` (all 133 standalone mods) and
`--compose biomes` (composed mod) after the prune: **0 "in game, not in
repo" lines anywhere.** `--mod UtinniPatches --mod LuminousPigment` alone:
`Everything in sync.` (exit 0).

## Tally

- Orphans found: **39** (37 UtinniPatches, 2 LuminousPigment)
- Removed: **39** (all of them — every one classified as either a confirmed
  duplicate, a confirmed-dead placeholder/patch, or harmless art residue;
  none required an owner call)
- Needs-owner-call: **0 file-level orphans**, but **1 follow-on item**
  (`ROTSPOREKIT_GHOST_MOD_1`) for the whole ghost mod this audit surfaced
