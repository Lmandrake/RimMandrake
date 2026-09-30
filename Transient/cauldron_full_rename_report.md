# CAULDRON_FULL_RENAME_1 — report

Status: rename executed, verification in progress (selftests running)

## Task
Rename src/RimMandrake/PoisonForest/ (Poison Forest / PoisonGround biome mod)
to "Cauldron" all the way down: packageId, mod folder, csproj/assembly,
C# namespace, About.xml, defNames, texPaths, cross-mod patches/references,
live-save BiomeDef concern.

## Precedent
CRACKEDLANDS_FULL_RENAME_1 is NOT a completed-rename precedent — it is still
`doing (BLOCKED)` in the FOUNDRY queue. FOUNDRY ran the live-tile check first
(per the item's own gate), found RM_FloodedCanyon on 44 live world tiles, and
escalated to the owner with three options rather than picking one itself. No
defName was ever renamed for Cracked Lands. The shape to replicate is
procedural: run the live-tile/savegame check FIRST, and if a BiomeDef defName
has nonzero live tiles, do NOT rename that defName — leave it, document it,
same as CRACKEDLANDS did.

## Live-tile check (offline, via worldmap.py — no bridge, no live game)
Read `CANONICAL_ASHKARR_START_2026-09-12.rws`'s world tileBiome grid offline
using `src/RimMandrake/Utils/worldmap.py`'s `WorldGrid` (shortHash decode
against the freshest def dump, captures/2026-09-29T03-31-24Z). Sanity probe:
RM_FloodedCanyon read exactly 44 (matches FOUNDRY's own live-bridge figure
from the CRACKEDLANDS escalation byte-for-byte) — cross-validates the offline
method against the live method.

Result:
- `RM_PoisonForest`: **0 tiles** — safe to rename (0-tile mid-migration state
  is expected/normal per CLAUDE.md, not a defect).
- `RUT_PoisonForest`: **546 tiles** — live, in active use. BLOCKED, same as
  CRACKEDLANDS' RM_FloodedCanyon. Did NOT rename this defName.
- Grep of the save's plain-text XML for any PoisonForest-derived string
  (items/thoughts/terrain defNames) returned ZERO hits — confirms no other
  defName in this family (item/thought/terrain) is Scribe-referenced by the
  live save, so those were safe to rename.

## What was renamed
- `src/RimMandrake/PoisonForest/` -> `src/RimMandrake/Cauldron/` (git mv),
  including the BiomeDef (`RM_PoisonForest` -> `RM_Cauldron`), terrain
  (`RM_PoisonSoil(Rich)` -> `RM_CauldronSoil(Rich)` — owner-typed: "Poison
  ground gets renamed to this biome"), C# namespace
  (`RimMandrake.PoisonForest` -> `RimMandrake.Cauldron`), all PoisonForest-
  named classes/files, csproj AssemblyName/RootNamespace/Compile-Include,
  packageId (`mandrake.rm.poisonforest` -> `mandrake.rm.cauldron`), About.xml
  display name.
- Utinni-tier files that reference the biome WITHOUT touching the frozen
  `RUT_PoisonForest` BiomeDef defName itself: `WildAnimals_PoisonForest.xml`
  -> `WildAnimals_Cauldron.xml` (xpath target `RM_PoisonForest` ->
  `RM_Cauldron`), `PoisonForest_ToxicPrizedMeat.xml` ->
  `Cauldron_ToxicPrizedMeat.xml`, `RUT_PoisonForestPrizedMeats.xml` ->
  `RUT_CauldronPrizedMeats.xml`, `RUT_PoisonForestMeatThoughts.xml` ->
  `RUT_CauldronMeatThoughts.xml` (+ the two Thought defNames
  `RUT_AtePoisonForestMeat{Direct,AsIngredient}` -> `RUT_AteCauldronMeat*`).
- `AncientDangerGenSteps_AmbientDoctrine.xml`: the `RM_PoisonForest` xpath ops
  (2 PatchOperationConditional blocks) -> `RM_Cauldron`; the `RUT_PoisonForest`
  ops and the donor mod's bare `PoisonForest` ops are UNCHANGED (correct).
- Additive-only fixes (list-every-plausible-name style, matching existing
  code convention) in `PyrelandsTuning.cs`'s `NearTerminatorBiomeDefNames` and
  `RUT_ExplosiveGrowthRoster.xml`'s `noSoakBiomes`: added `RM_Cauldron`
  alongside the still-present old entries.
- Canonical design files (git mv + reference fixups): `poison_forest.md` ->
  `cauldron.md`, `poison_forest.json` -> `cauldron.json`, `poison_forest.csv`
  (enrichment plan) -> `cauldron.csv`. Updated live cross-references in
  `design/INDEX.md`, `README_BIOME_GRAMMAR.md`, `_def_bindings_2026-09-09.md`,
  `biome_mod_architecture.md` (row 10), `biome_mod_unification_spec.md`,
  `flowworks_liquid_matrix.md`, `infrastructure/state/facts/biome_paint_list.md`
  (both rows — RM_ row renamed, RUT_ row's defName column left alone but its
  prose corrected to say `mandrake.rm.cauldron`/`RM_Cauldron`).
- Tooling: `biome_name_migration.py`, `biome_flora.py` (dict VALUES updated,
  lookup KEYS which are short internal identifiers left as-is),
  `biome_load_proof.sh` (mapping updated).

## Deliberately NOT renamed (documented exceptions)
1. **`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PoisonForest.xml`** — the
   frozen campaign twin's own `<defName>`. 546 live world tiles (measured
   offline, see above). Left byte-for-byte untouched, exactly as its own
   header already says it is frozen. This mirrors CRACKEDLANDS_FULL_RENAME_1's
   still-open block and should get the same owner call the coordinator/owner
   already owes that item (rename now and ride to world-remake / hold the
   defName until world-remake / live-paint the 546 tiles to the new name
   first).
2. Donor-owned strings, never ours: `<texture>Biomes/PoisonForest</texture>`
   (BiomesPlus texture path), `BiomesPlus.BiomeWorker_PoisonForest` (donor
   class name), the donor mod's own bare `PoisonForest` BiomeDef references in
   `AncientDangerGenSteps_AmbientDoctrine.xml`.
3. Historical/dated records left as history (not rewritten): the frozen sheet
   `cauldron.md`'s 240-line body prose (title + one banner line updated only —
   "amendments add detail, they never change a ruling"), the dated review
   `cauldron_bedazzle_review_2026-09-28.md`, `biome_name_candidates_2026-09-26.md`
   (a superseded naming-candidates brainstorm), quoted historical ruling text
   inside `cauldron.json`'s `evictions`/`law` fields, all closed items and
   handoffs, `world/**` (savegame-derived records).
4. Derived/generated artifacts not hand-edited (will pick up the rename next
   regeneration): `infrastructure/dashboards/hub/tabs/health.html` and similar
   dashboard JSON, `infrastructure/state/logs/**`.
5. Not swept: ~90 files matched a bare "PoisonForest"/"poison_forest" substring
   in CSV/JSON data dumps, review artifacts and prose docs that don't carry a
   defName/packageId/namespace token — triaged and judged lower-risk/lower-value
   than the code-level and functional-doc fixes above, given effort budget.
   None of these affect load/build correctness.

## Build/test verification
- All touched/moved XML parse clean (`ElementTree`, 15 files).
- `cauldron.json` is valid JSON.
- `dotnet build RM_Cauldron.csproj -c Release` (Windows-native dotnet.exe via
  WSL interop): **Build succeeded, 0 warnings, 0 errors.** Produced
  `RimMandrake.Cauldron.dll` + a freshly regenerated `.srchash` sidecar
  (via `src/Directory.Build.targets`' own MSBuild target, not hand-written).
- `run_selftests.py`: pending (see below).

## After-census (git grep, sanity-probed on `korrum`)
- `RM_PoisonForest` (exact token): 0 remaining in-scope, live occurrences
  except the deliberate additive keeps (PyrelandsTuning.cs,
  RUT_ExplosiveGrowthRoster.xml) and the two historical/dated docs named above.
- `RUT_PoisonForest`: still present everywhere it was before (unchanged, by
  design — the block).
- `mandrake.rm.poisonforest` / `RimMandrake.PoisonForest` (namespace): 0
  remaining in-scope except the one historical dated-review doc.
- New token `RM_Cauldron` / `mandrake.rm.cauldron` / `RimMandrake.Cauldron`:
  present everywhere expected.

## Unverified / risks
- `run_selftests.py` full run not yet confirmed complete (background, >120s).
- No live/bridge verification performed (forbidden by task scope) — build and
  static checks only.
- The ~90-file "not swept" prose/CSV corpus (see exception 5) still says
  "poison forest"/"PoisonForest" in various forms; harmless to load/build but
  not literally zero per the item's stated criterion.
