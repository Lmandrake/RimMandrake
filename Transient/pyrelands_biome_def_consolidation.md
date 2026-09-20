# PYRELANDS_WRONG_BIOME_DEF_1 — offline consolidation (BENCH's start, offline half)

Status: OFFLINE HALF DONE. Not committed. World-side half untouched (BENCH's).

## 0. Independent re-measurement

Re-parsed `world/ASHKARR_WORLDMAP_tiles.csv` myself (21,872 rows, mtime
2026-09-12) with Python's csv module, not grep: `RM_FE_Pyrelands` = 0,
`ZBiome_Grasslands` = 222. Matches BENCH's figure exactly.

## 1. Inventory of ZBiome_Grasslands / RM_FE_Pyrelands references under src/

37 files matched. Most (`AnimalBiomeDuplicates_Fix/Generated.xml`,
`ZZZ_BiomeWildAnimalDuplicates_Generated.xml`, `FlowWorks_SubsurfaceLiquid_Ashkarr.xml`,
`FishTypesStrip_NoFishBiomes.xml`, `AncientDangerGenSteps_AmbientDoctrine.xml`,
`AnoobaDrawSize_Fix.xml`, `BiomeCastEvictions_WildBiomes.xml`) are whole-Ashkarr
generic biome-list patches that treat every painted biome uniformly — they don't
encode any claim about which def *is* the Pyrelands, so both defNames appear as
two of dozens of entries. Left untouched, out of scope.

**Content patches, decided individually:**

- `WildAnimals_Pyrelands.xml` — ALREADY CORRECT. All 3 real `PatchOperation`s
  target `RM_FE_Pyrelands` exclusively. Its 9 `ZBiome_Grasslands` hits are
  comment-only (citing `AnimalBiomeDuplicates_Fix.xml`'s unrelated donor
  duplicate-record fix, and clarifying `RSW_Anooba` is a separate def not wired
  to that donor). No change. (Note: the task brief's "7×/2×" count doesn't match
  what's on disk — re-measured directly, trust the file over the brief.)
- `AshStorms_Pyrelands.xml` — WRONG, FIXED. Its one live `PatchOperationAdd`
  put `AB_VolcanicAsh` on `ZBiome_Grasslands/baseWeatherCommonalities`.
  Repointed to `RM_FE_Pyrelands`. Left the two `WeatherDef[defName="AB_VolcanicAsh"]`
  relabel/redescribe ops alone — global label change, not biome-specific.
- `BiomeNames_Ashkarr.xml` (label: ZBiome_Grasslands → "the Pyrelands") and
  `BiomeFlora_Ashkarr.xml` (wildPlants: ZBiome_Grasslands → Quickgrass only) —
  LEFT ALONE, deliberately. Both are whole-Ashkarr generated files (one row per
  currently-painted donor biome) serving the *donor* def while it's still what
  222 tiles carry. `RM_FE_Pyrelands` already natively ships its own label
  ("the Pyrelands") and a much richer `wildPlants` table (EmberGrass 9.0 +
  Quickgrass 3.8) directly in its own def — nothing is missing to port. These
  entries go dead on their own once the repaint lands; no patch action needed.
- `BiomeDescriptions_Ashkarr.xml` — comment corrected, no patch added. Its
  header falsely claimed "no RUT_ BiomeDef exists yet for the Pyrelands" —
  false since 2026-09-11 (`RM_FE_Pyrelands` has its own native description).
  Did NOT add a description patch onto `ZBiome_Grasslands`: doing so would be
  porting Pyrelands content onto the donor, which is exactly what the owner's
  2026-09-20 ruling forbids (entrenches the donor). Left as a known, accepted
  gap until the repaint.
- `TileMutatorDefs_Batch2.xml` (`RSW_HuntingLodge` biomeWhitelist includes
  `ZBiome_Grasslands`) and `JawaWorld_BiomeMix.xml` (a `TidallyLocked`
  worldgen biomeBlacklist including `ZBiome_Grasslands`) — LEFT ALONE. The
  mutator is never placed on any tile (manual-placement-only, per its own
  header) and the blacklist belongs to a worldgen mechanism this project does
  not run at all (CLAUDE.md: no worldgen feature). Neither is live content.
- `RUT_Emberscythe.xml`, `RSW_Nuna.xml`, `RSW_Orray.xml` — comment-only
  provenance notes citing the original `cast_assignment.csv` row's donor
  defName; actual wiring for all three already lives in
  `WildAnimals_Pyrelands.xml` targeting `RM_FE_Pyrelands`. No change.
- Python world tools (`ashkarr_paint.py`, `ashkarr_landmarks.py`, etc.),
  `worldview.py`, `planet_portrait.py` — world-side, out of scope, untouched.
- `validation.py` (Pyrelands, AshkarrWeatherSuite, StructureInjectionsSW) —
  checked; all assert against the correct current def already, except one
  stale comment (below).

**Found in passing, escalating, not resolved here:**

`src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamHook.cs` and
`src/RimUtinni/UtinniPatches/Patches/ManyWaters_RiverSteam_Ashkarr.xml` both
carried a 2026-09-19 comment claiming the *opposite* of today's measurement —
"RM_FE_Pyrelands carries 222 tiles live, ZBiome_Grasslands carries zero,
MEASURED live (FOUNDRY bridge wave 2), jawa/world_tile_export." My own CSV
re-parse (above) contradicts this. The CSV's mtime (2026-09-12) predates that
claim by a week. Two readings: either a live `jawa/world_tile_set` switch on
2026-09-19 was done in a session that was never persisted to the canonical CSV,
or that claim was never true. **I did not adjudicate this — flagging for BENCH.**
I corrected both comments to state the measured facts and the unreconciled
conflict, without asserting which prior claim was wrong. The actual patch
operations in `ManyWaters_RiverSteam_Ashkarr.xml` already gate BOTH defNames
conditionally (cost-free either way) — no functional change needed there.

Also corrected: `src/RimMandrake/Pyrelands/validation.py` line ~14 claimed
`PYRELANDS_WORLD_SWITCH_1` "removed [ZBiome_Grasslands] from the worldmap" —
false. That item (closed 2026-09-11, `infrastructure/state/items/closed/
PYRELANDS_WORLD_SWITCH_1.md`) closed with its own criterion #3 (the live
`world_tile_set` step) unmet — owner went AFK mid-item. Corrected to state
this plainly.

## 2. Repoint decisions

Only one real content-patch repoint was needed: `AshStorms_Pyrelands.xml`'s
`PatchOperationAdd` xpath, `ZBiome_Grasslands` → `RM_FE_Pyrelands`. Everything
else was either already correct (`WildAnimals_Pyrelands.xml`), or correctly
left on the donor because it's whole-world generic machinery, dormant, or
would move content in the forbidden direction (entrenching the donor).

## 3. Validation

Ran `skills/rimworld-modding/scripts/validate_patch.py` on all 3 touched XML
files, with `--defs` against the Data/Workshop/Mods roots (15-mod minimal list
currently active) AND `--live` against a fresh DefDump (67,283 defNames /
618 mods). **Result: 0 errors, 2 pre-existing advisory warnings (unrelated to
my edit, already present in `ManyWaters_RiverSteam_Ashkarr.xml`'s pre-existing
add-if-missing shape).**

What this proves: the new `RM_FE_Pyrelands/baseWeatherCommonalities` xpath is
syntactically well-formed, `RM_FE_Pyrelands` and `AB_VolcanicAsh` both resolve
as real defNames in the live 618-mod dump, and no comment edit broke XML
parsing (no stray `--` introduced).

What it does NOT prove: that the patch actually *applies* against the tiles
players stand on today — it can't, because `RM_FE_Pyrelands` carries 0 tiles
right now (by design, per the item — this is expected, not a defect) and the
static/live cross-reference check only confirms the def **exists**, not that
any tile **uses** it. `PatchOperationConditional`/`FindMod` return true and
log nothing on zero matches, so a clean validate here is not evidence the ash
storm is visible in play — only the repaint (below) makes that observable.
Did not load-test in game (offline half; no bridge use per scope).

Non-XML edits (`RiverSteamHook.cs`, `Pyrelands/validation.py`) are comment-only
— no code or assertion logic changed, nothing to run against.

## 4. World-side change (NOT DONE — handing to BENCH)

Exact, precise spec:

1. In `world/ASHKARR_WORLDMAP_tiles.csv`, for every row where `biome ==
   "ZBiome_Grasslands"` (222 rows, confirmed by direct parse, column name
   `biome`), set `biome = "RM_FE_Pyrelands"`. Nothing else on those rows
   changes.
2. On the live/canonical world (whichever the CSV is meant to mirror), apply
   the same 222-tile switch via `jawa/world_tile_set` + `jawa/world_commit`,
   then read back with `jawa/world_tile_export` to confirm 222 tiles now read
   `RM_FE_Pyrelands` and 0 read `ZBiome_Grasslands`.
3. ⚠️ Before doing this, reconcile the 2026-09-19 conflict noted in §1 above —
   if a live switch was already attempted and lost, find out why it didn't
   stick (a reload from an older save/world state is the leading suspect,
   consistent with the 2026-09-17 23:31Z ModsConfig-reset incident already on
   record) before repeating the same steps blind.
4. Not done here, per explicit instruction: I did not touch the CSV or the
   world in any way.
