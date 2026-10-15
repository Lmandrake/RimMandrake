# TESTSITE_SAVES_BUILD_ONE_CALM_MAP — sitting 2026-10-15

Item: `TESTSITE_SAVES_BUILD_ONE_CALM_MAP` (owner by card 2026-10-15: "Clean saved maps").

## 1. Inventory — how each suite gets its map today
- GSS `proof_all.py --live`: P1 makes a fresh quicktest map (`--no-fresh-map` = current); `calm_map()` (P2c + P3) disarms
  triggers, hostile buildings, non-colonists, unfogs all + re-sweeps.
- FlowWorks `validation_v2.py --live --fresh-map`: up to 4 quicktest rolls (frozen biomes); L1 refuses non-pristine engine / rain.
- FlowWorks rivers: `river_site.py` founds a mild river colony in the current world (>= 2 moving-water edges, fish biome),
  then `extension_proof.py --site river`.
- Pyrelands: already a save (`northstar_site.py --reload-only --tag r6`, fixture `NS_Pyrelands_site_1_417df172fdb5_r6`);
  its `ruins` chain and wildlife census read map content, so only dangers may go.
- r5-r8 hazards were all on fresh maps: mechs/fleshbeasts released by the unfog from shrines (r8 probe: AncientCryptosleepCasket
  + AncientHermeticCrate + Sarcophagus beside every released group), hives/spiders at arm, storm fires, Bumbledrone on a
  leftover candidate map, river into the sea, wide-river ferry banks.

## 2. Design
Full text `design/RimMandrake/test_site_saves_2026-10-15.md`. THREE saves: `calm` shared by GSS + FlowWorks v2 (same needs:
250x250 quicktest home, mild, dry, pristine engine; each clears its own sites; each run is a fresh load); `river` own (plot
repaints cut rivers; v2 needs a pristine engine); `pyrelands` own (50 C is the subject; ruins/wildlife measured -> narrower
`danger` clean profile). Caskets/crates/sarcophagi vanish BEFORE the unfog (Building_Casket.Destroy(Vanish) ->
ClearAndDestroyContents, rimsage 1.6: sleepers destroyed, never dropped). Whole-map unfog + re-sweep; read-back gate before save;
Saves backed up; never overwritten (next _vN).

## 3. Code changes
- NEW `src/RimMandrake/Utils/modcheck/test_site_saves.py` (build/load/check/list; registry `test_site_saves.json`) +
  `selftest_test_site_saves.py` (fake map: order, release-by-unfog, profiles, player-building kept, never-overwrite, load path).
- `proof_all.py`: P1 loads `calm` by default (`--fresh-map` / `--no-fresh-map` / `--site-save`); P1 row carries mapMode + receipt.
- `validation_v2.py`: `--live` loads `calm` (`--fresh-map` / `--current-map` / `--site-save`).
- `extension_proof.py`: `--site river` loads `river` (`--current-map` / `--site-save`).
- Selftests: selftest_test_site_saves 0 fail; selftest_proof_all ALL PASS; v2 offline O-LIVE-NEG PASS + mock GREEN 61/61;
  selftest_extensions PASS; selftest_river_site 0; lint_calls on the new module: 33 literal calls, 0 schema problems.
- Review: test_site_saves.py (found + fixed: `_player` read `factionName`, the colony's own name, so a player turret would
  have been vanished; unchecked post-unfog trigger pass), selftest, extension_proof.py -> clean after commit.
  proof_all.py (930 lines) and validation_v2.py (3.9k lines): diff reviewed only, left DIRTY (no full-file review this sitting).

## 4. Live — bridge, deploy, tier
HELD by the coordinator before Phase 2 (FOUNDRY art deploy with the game down): no deploy / mod-list swap / launch until "go".

## 5. Saves built
(pending)

## 6. Proof — load + run per suite
(pending)

## 7. Teardown
(pending)

## 8. Left / NEXT
(pending)
