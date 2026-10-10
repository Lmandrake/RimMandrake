# CRACKEDLANDS_FULL_RENAME_1 — FloodedCanyon → CrackedLands, everywhere

Owner-typed at `FLOODEDCANYON_BEDAZZLE_SITTING_1` (2026-09-28): full conversion
from "flooded canyon" to "Cracked Lands" **for all defs and docs and code and
file names**. The player-facing label is already "the Cracked Lands"; this makes
the internals match. The rename gate is long closed (`NAMING_SCHEME_EXECUTION_1`,
2026-08-31) — renames are simply owed work.

## Ruling 2026-10-09 (decision taken by question card)

Rename now. Read the canonical start save for old-name references first; if any are found, STOP and report.

## Scope

1. **Defs**: `RM_FloodedCanyon` → `RM_CrackedLands`, and every defName carrying
   `FloodedCanyon` (GameConditionDefs, weather/incident/hediff defs, the
   `WildAnimals_CrackedLands.xml` xpath targets, `SandFishing_CrackedLands.xml`
   mirrors — sweep, don't enumerate from memory).
2. **Code**: C# namespaces/classes/files (`RM_MapComponent_CanyonFlood.cs` and
   friends keep their names if they don't say FloodedCanyon; anything that does,
   renames), csproj `<Compile Include>` lines updated in the same change
   (`EnableDefaultCompileItems` is false — a missed line is a silent no-compile),
   DLL rebuilt + `.srchash` regenerated and pushed together.
3. **Folder/file names**: `src/RimMandrake/FloodedCanyon/` → `CrackedLands/`,
   `Biomes.compose.json` wave-0 entry, About/packageId if it carries the old
   name, deploy tooling references (`deploy_custom_mods.py --mod` name — the
   deploy tool needs unique names across tiers).
4. **Docs**: every design/infra doc saying "Flooded Canyon"/`FloodedCanyon` as
   the current name (the program table row 4, the bedazzle review's title
   already carries both). Historical prose in closed items stays as history.
5. **Ledger/queue**: this sitting's item id stays `FLOODEDCANYON_BEDAZZLE_SITTING_1`
   (legacy ids are never renamed — cite with title attached).

## 🔴 Verification bars (before any defName change lands)

- **Live-tile / savegame check** (`biome-defname-deletion-must-check-live-tiles`):
  tileBiome in `.rws` is shortHash-encoded — a text grep of the save LIES. Check
  the canonical start save (`CANONICAL_ASHKARR_START_2026-09-12.rws`) and any
  keeper saves for `RM_FloodedCanyon` references via the savemap tooling with a
  def dump of the SAME mod set. If the save references it: ESCALATE with options
  (save edit vs ride the coming world remake) — do not silently break the save.
- The `RUT_CrackedLands` twin and its patches must still resolve after the
  rename (the Utinni patch xpaths that target `RM_FloodedCanyon` change too).
- Quicktest load after: zero cross-reference errors naming either def.

## verify

- Repo-wide sweep for `FloodedCanyon` returns only history (closed items, old
  handoffs, git log) — zero live defs/code/paths/docs (measured, with a sanity
  probe).
- Build clean, selftests pass, deploy plan clean.
