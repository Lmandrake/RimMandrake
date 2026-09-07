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
