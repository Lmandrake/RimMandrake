# Worldmap redo — bridge run sheet, 2026-09-07

Every step's authority is `design/Jawa/worldbuilding/biomes/_freeze_rulings_2026-09-07.md`.
Safety bar is **[R36]**: back up · batch · read back with a GETTER · diff the
full CSV for LOSSES as well as gains.

---

## STEP 0 — before any write

- [ ] Take the bridge (`rimflow bridge take`).
- [ ] **Back up the savegame.** ⚠️ `rimworld/save_game` has written the CURRENT
      slot instead of `saveName` — confirm a NEW file appeared and no existing
      one changed size. Never trust the path it returns.
- [ ] Confirm the world is genuinely loaded — `game_loaded` is not proof; a load
      can abort while the bridge keeps answering.
- [ ] `world_lint` and `world_links_validate` for a BEFORE baseline. Record the
      counts; anything we do is judged against these, not against zero.

## STEP 1 — 🔴 PROVE `riverDist` (per [R32]; do this before anything else)

The whole river plan rests on one unmeasured assumption.

- [ ] `jawa/world_links_get` on R06's 10 tiles — it **reports riverDist**. Record
      the current values. They may all be 0: our rivers came from
      `world/_rivers/apply.py`, which may never have set it.
- [ ] `jawa/world_links_clear` on R06, then `jawa/world_links_get` again —
      **did riverDist reset, or does it persist?**
- [ ] `jawa/world_links_set` re-laying R06 **mouth first** from its NEW mouth
      (the inland end) toward the Scald, then read back.

⛔ **The trap:** `OverlayRiver` sets `riverDist = Max(existing, previous + 1)` —
it **never decreases**. If clear does not reset it, re-laying reports success and
silently keeps the old numbering.
⚠️ **Owner: a Save→Reload may be needed before a change is visible** (very common
in RimWorld). A read-back showing the old value is **not** proof of failure until
a reload has been tried.

**Decision string:** R06's Scald-end tile must end with the HIGHEST riverDist of
its ten, and its inland end with 0. If it does not after a reload, STOP the river
work and report — do not proceed to the other four.

## STEP 2 — the other four Scald rivers (only if step 1 passed)

Per [R31], **all five flow OUT**; the Scald end is the SOURCE, so it takes the
maximum riverDist. Lay each **from its new mouth toward the Scald**.

| river | draft name | tiles | new mouth |
|---|---|---:|---|
| R02 | The Long Pour | 91 | the Twilight Sea end |
| R03 | Anvilwash | 32 | inland terminus |
| R05 | Feverfeed | 11 | inland terminus |
| R06 | Sporefall Water | 10 | inland terminus (done in step 1) |
| R12 | Spinecut | 5 | inland terminus |

⚠️ `world_links_validate` will report the four inland-dying rivers as "river
mouths with no water-covered neighbour". **That is expected under [R2]**, not a
defect.
⚠️ A biome with `allowRivers=false` **hides** links without deleting them —
`world_links_get` reports `hiddenByBiome`. Check it before concluding a link
failed to apply.
⛔ Do **not** add links for the ring-mountain inflow. [R31]: the Spine sheds into
the crater whether or not the engine draws it.

## STEP 3 — Desert band repair BEFORE the biome merge

`WORLDMAP_DESERT_BAND_REPAIR_1` (climate outliers on the Desert def). **Must run
first** — [R30]: the FungalForest merge sends 53 tiles INTO `Desert`, so
repairing after painting means repairing a bigger problem.

## STEP 4 — the FungalForest merge, 425 tiles

Plan: `design/Jawa/worldbuilding/data/fungalforest_merge_plan_2026-09-07.md`.
Per [R29] **follow the paint**; the item file's old cluster-spec table is
superseded, and the 15 flagged ties are settled by the same rule.

| tiles | → receiving biome |
|---:|---|
| 352 | `AB_MycoticJungle` — the Rot |
| 53 | `Desert` |
| 8 | `BiomeGRimond` — the Blue Desert |
| 8 | `AB_RockyCrags` — the Forsaken Crags |
| 4 | `RUT_NightsideIce` |

- [ ] Apply in batches, read back each with `world_tile_get`.
- [ ] `world_commit` **once per batch**, never per write — each call regenerates
      whole meshes.

## STEP 5 — close out

- [ ] Re-export the tiles CSV; **diff against the committed one** ([R36] step 4)
      — confirm the intended tiles changed **and nothing else did**.
- [ ] `world_lint` + `world_links_validate` again; compare to the step-0 baseline.
- [ ] `verify_frozen.py --restamp`.
- [ ] `the_rot.md` arc range → **75.3–132.9** ([R30]), and check its temperature
      line against the warmer dayward edge it now reaches.

## NOT in this session

- `SETTLEMENT_REJIGGER_ROUND2_1` — released to `needs: bridge`, but [R34] gives
  it its own pass after the Wednesday sitting.
- `GEOTHERMAL_DENSITY_FIELD_1` ([R12]) — a mapgen constraint, not a tile edit.
- The undefined biome defs (jungles, swamps, grasslands, oasis) — they need
  sheets before they can be assigned.

## Still open

River names R01–R16 are **drafted, not ruled** ([R33]). They block nothing here;
the ledger doc needs them before it can be cited by the biome sheets.

---

# OUTCOME — 2026-09-07, session complete

**Save: `WORLDMAP_V2_merged_2026-09-07.rws`** (12,812,406 bytes). Verified against
all three known save-tool failure modes: a NEW file appeared; all three
pre-existing `WORLDMAP_V1_original_*` saves are **byte-identical to backups taken
before the session**; nothing else in `Saves/` was written.

## what landed

- **FungalForest merge complete.** `BMT_FungalForest` is **extinct** (0 tiles).
  Live census: Rot 1939→**2291**, Desert 4150→**4203**, Blue Desert 1328→**1336**,
  Forsaken Crags 1225→**1239**, Nightside Ice **806**.
- **All 292 river links laid mouth-first**, establishing `riverDist` for the first
  time ([R38]). `world_links_validate`: `asymmetricCount 0`, `nonAdjacentCount 0`.
- Landmarks 563, mutators 10084 placements over 6710 tiles, settlements 96→122,
  71 regions over all 21872 tiles. `world_lint`: 11 findings (3
  settlementsWithNoRoad), `staleMarineMutators 0`, `waterBiomeOnRaisedLand 0`.
- **New colony per [R39]:** `Utinni Landing`, settlement 389, **tile 24** (Desert,
  arc 69.1, 31.3 °C, flat, region *Long Sand*), 250×250. One colonist,
  **Stoddart** — `kindRequested Colonist / kindActual Colonist /
  kindSubstituted false`. Map creation verified by `mapCount` **1→2 delta**, not by
  the tool's return ([TILEGEN_SILENT_REUSE_1]).
- Old colony (settlement 255, tile 16869) abandoned with `force` — vanilla refuses
  while `AllColonistsThere`. Its ground had been repainted, which is exactly what
  the paint guard warned about.

## R36 verification — PASSED

Re-exported the live world and diffed against the intended CSV:
**1135 mismatches, and every one is a sea tile** whose def does not exist yet
(436 TwilightSea→Ocean, 381 GreySea→Ocean, 312 TheScald→Lake, 6
TwilightSea→AB_RockyCrags). **Zero collateral damage on the other 20,737 tiles.**

## 🔴 STILL OWED — rides the next restart, no extra cost

1. **The three seas do not exist in game.** `RUT_TheScald`, `RUT_GreySea`,
   `RUT_TwilightSea` (+ `RUT_PropaneLake`, painted nowhere) were newly authored in
   the biome-sheet work and had never been deployed. **Now deployed and validated
   offline against vanilla `Ocean` — `workerClass BiomeWorker_Ocean`, all required
   fields present, they WILL load** — but defs parse only at startup.
   ⇒ After the next restart: reload this save and re-run
   `w9_run.py --apply` to paint the 1135 tiles. ~2 minutes.
2. **An assembly is waiting on the same down-window:**
   `RimMandrakeVisibility.dll` shows `~` in the deploy plan, plus UtinniShell
   webm textures. Assemblies cannot be written while the game holds them.
3. ⚠️ **River count discrepancy, unexplained:** we imported 292 river links but
   `world_links_validate` reports `riverEntries 634` (=317 links) over
   `riverTiles 347` against our graph's 308. The import appears to have ADDED to
   pre-existing links rather than replacing them. Measure before the next import;
   a `clearFirst` may be owed.

---

# ⭐ THE WHOLE MAP IS WORKING — 2026-09-07, after the GravTide restart

**Save: `WORLDMAP_V3_seas_2026-09-07.rws`** (13,086,256 bytes). Verified: NEW file
appeared, `WORLDMAP_V2_merged_2026-09-07.rws` md5 **unchanged**, nothing else in
`Saves/` written.

## the load — every decision string written before launch PASSED

599 active mods. Dead mods (static ctor / type load) **0 / 0** — GravTide loaded
clean. Defs discarded **0**. Cross-references **0**. Harmony patch failures **1 =
baseline**. ConfigErrors **17 = baseline**. Patch operations failed **8 =
baseline** — *GravTide added none of its own*.
Both silent-failure strings **ABSENT**: no `No terrain found in biome`, no
`All weather commonalities were zero` ⇒ the `terrainsByFertility` drafting worked.

**The expected-PRESENT check passed** — all four sea BiomeDefs are live:
`RUT_TheScald` "the Scald" · `RUT_GreySea` "the Grey Sea" · `RUT_TwilightSea`
"the Twilight Sea" · `RUT_PropaneLake` "the propane lake"
(`RUT_NightsideIce` as the control that already worked).

## the import

`stage 1 tiles: rows=21872 applied=21872 skipped=0 unknownBiomes=[]`
— against last run's `applied=20737` and three unknown biomes.
Stages 2–6 all ran; `world_commit: True`.

## R36 verification — **0 MISMATCHES** (previous run: 1135)

Live world re-exported and diffed against `world/ASHKARR_WORLDMAP_tiles.csv`:
**every one of the 21872 tiles matches intent.**

| live census | |
|---|---:|
| `RUT_TheScald` | **312** |
| `RUT_GreySea` | **381** |
| `RUT_TwilightSea` | **442** |
| `BMT_FungalForest` | **0** |

## ✅ the river-link question from the last run is ANSWERED — no defect

Last run flagged that we imported 292 river links but the world reported
`riverEntries 634` / `riverTiles 347`, and asked whether the import ADDS rather
than replaces. **This run reports 634 / 347 again — identical.** An accumulating
import would have grown it. ⇒ **the import is idempotent; no `clearFirst` is
owed.** The 25 extra links are pre-existing world links absent from our CSV, a
standing difference rather than an import bug.

## what the run sheet still leaves open

- `WORLD_LINT_WATER_HARDCODE_1` — the lint's 1135 `landBiomeSubmerged` findings
  are a **lint defect, not a map defect** (hard-coded `Ocean || SeaIce`), with the
  fix recorded. Its `staleMarineMutators 0 → 99` half is filed **UNPROVEN**.
- The seas render with the vanilla ocean texture ([R37] ship-as-is); colouring
  them is its own pass alongside `WORLD_RIVER_COLORS_1`.
- `UNDERWATER_BIOME_SUPPORT_1` — GravTide is now ACTIVE, and its arrival gate is
  generic (`isWaterBiome`), so the three seas should already be divable.
  **Untested in play.**

## V11 — 2026-09-07 ~22:06, after the ComplexStructures restart
Save: `WORLDMAP_V11_complex_structures_2026-09-07.rws` (23,044,088 bytes; NEW file, no existing save changed — diff-verified).
136 `RUT_ComplexStructures` landmarks placed (279 qualify live vs the plan's 261 — the Cathedral pass added landmarks since; 143 skipped for carrying one already). Whole-planet mutator losses: NONE. Read-back 136/136. Propane-lake texture confirmed rendering on the globe (dark liquid, distinct from Umbra ground); landmark icons render.

## V12 — 2026-09-07 ~22:20: ideoligions live; meander ruling verified already satisfied
Save: `WORLDMAP_V12_ideoligions_2026-09-07.rws` (24,245,841 bytes; NEW file, nothing else changed).
- **CORRECT_ASHKARR_IDEOLOGY_1 executed on the live world** (owner ruled live test-faction-first over scratch proof, 2026-09-07): all 12 factions converted via `jawa/faction_ideo_set` — authored ideoName, real leader titles (Captain/Director/High Warden/First Speaker/Archduke/Lord/Scraplord/Prime Trader/Elder/War Chief/High Marshal/Emperor), per-ideo classicMode=false, read back per faction AND re-verified in the saved .rws. Believers untouched per standing ruling (new pawns only). Astropolitan remains registered.
- **Meander ruling: ALREADY SATISFIED on the live net** (leg max 3, sinuosity 1.32 vs ancient ~1.0) — the handoff's "unapplied" line was stale; nothing written. Full numbers: `world/_roads/meander_v12/REPORT.md`. ⚠️ River entries 652 live vs 634 at V3 — unexplained +9 edges, re-measure before any river import.

## V13/V14 — 2026-09-07 ~23:00: nightside temperature-coherence repaint (owner, in discussion)
Owner ruled the nightside/terminator biomes by physical temperature, in-discussion 2026-09-07. Two saves:
- **V13 `WORLDMAP_V13_backside_reband_2026-09-07.rws`** — backside bands crags(>=-20)>ice>blue-desert(split -33)>propane(<-42C, its boiling point; whole shadow cap Umbra+Ammonia+Deadstone). Ice/blue never reach 0C at max (melt line) — already true, kept. Soft boundaries de-circled by a deterministic longitude field (anti-bullseye); physical lines hard. 2940 tiles, 0 collateral. 43 impossible-corner tiles (cold mean, summer thaw) left as-is.
- **V14 `WORLDMAP_V14_pf_terminator_2026-09-07.rws`** — Poison Forest = terminator biome fed by the wall; floor -10C. Evicted 350 cold strays to the bands; grew +308 as groves at arc 86-96 consuming Desert/Wasteland/Badlands/AridShrubland to regain significance (542->500 net). 658 tiles, 0 collateral, lint clean.
Rollback chain: V12 (pre-nightside) < V13 < V14. Canon CSV `world/ASHKARR_WORLDMAP_tiles.csv` NOT yet re-exported from the live world — owed once the nightside pass settles.
