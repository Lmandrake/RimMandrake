# Four biomes — review package for the bridge driver, then the owner (2026-10-23)

Written by a FOUNDRY offline helper. Pyrelands, Leaning Scrub and Cauldron are covered here; **Contagion is
another helper's** (its two northstar FAILs, CONTAGION_BURN_DIAGNOSE_NATIVE_FEELS_NOTHING and
COALESCENCE_STAGE_DIAGNOSE_STUCK_AT_ONE, are in flight). Save and map names are **TBD**: the driver names them
when it makes them. Before anything reaches the owner, the driver looks at every capture and drops the broken ones
(owner, 2026-10-22: "nothing reaches the owner unread").

## 0. Before any biome: one deploy, one tier

- **Game DOWN**, then `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes`. Read the plan (it
  currently shows drift, including stale Wasteland/VaultRoot files in game that are not in the repo: leave them unless
  you know they are yours). Then `--apply`. That one deploy carries the three DLLs rebuilt today: Cauldron
  (637645762), ExplosiveGrowth (aa1705a43) and LeaningScrub (7b9681f28). Pyrelands' FireEcologyHook.dll did not
  change (05033a3f7 is already deployed: md5 d0a5cb5e).
- **Tier: `biomes_sprint`** (`modset_builder.py --tier biomes_sprint --apply`, only with the game down). It is the
  only sprint tier that loads `mandrake.rsw.swbestiary` + `mandrake.rut.patches`, which Leaning Scrub's fire-stamper
  rows need. On the 16-mod minimal list those rows read UNMEASURED by design.
- Hold the bridge (`rimflow bridge take --for "four biomes review prep"`), and release it the moment you stop.

## 1. Pyrelands

**Machine rows first (driver):**
1. Reload the calm2 fixture: `python.exe src/RimMandrake/Pyrelands/northstar_site.py --reload-only --tag calm2`.
2. Run the Pyrelands chain `opening_front` **first in the session**. Its new row `opening_front_old_save_inert`
   (PYRE_OPENING_FRONT_BUILD_SMOKE_ON_ARRIVAL A4, old-save half) must read PASS: `done=True lit=0 litTick=-1`, with
   mapAge above 2500. It reads UNMEASURED if `RearmOpeningFront` has already run in this session; if so, reload the
   fixture. The fresh-map half of A4 was already seen on 2026-10-23 (`lit=4 litTick=59`).
3. Then `rimflow verify PYRE_OPENING_FRONT_BUILD_SMOKE_ON_ARRIVAL --criterion A4 ...`.

**What the owner walks.** Use a fresh RM_Pyrelands map on a tile whose neighbours are also Pyrelands (biome
transitions blend in the neighbours' edges). Save it as a keeper: `RM_Review_Pyrelands_<date>` (TBD).
- North-star walk bars: `design/validation_walks/RimMandrake/Pyrelands.md` `## north star` (VALIDATED). Look at:
  plant and animal distribution, deep-ash ground, grass carpet, the burn line on arrival (`pyre_burn_line_present`,
  which is PYRE_OPENING_FRONT A5 L4), scorch-fruit only on burned ground, scorched ruins, and the three weathers
  (ash fall, cinderfall, black rain).
- PYRELANDS_STRUCK_GLASS_RITE_BUILD_1 A3 (L4): the Struck Glass rite in play. The ring art is accepted-for-now.
- PYRELANDS_GRASS_SATURATION_1: only his look at the two-species ground fill is left.
- **Leave out:** the fire-hawk carrying embers. It is flight, so it waits for a joint session
  (FIREHAWK_FLIGHT_BEHAVIOR_1). The titan passage has no giant in this biome yet
  (PYRELANDS_TITAN_POPULATE_FIRE_NO_FOOTFALL).

## 2. Leaning Scrub

**Machine rows first (driver).** Site `RM_TestSite_leaningscrub_v2` on `biomes_sprint`. Run
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod LeaningScrub --plan src/RimMandrake/LeaningScrub/northstar_plan.py`.
New rows to read, each one able to fail:

| row | item / criterion | PASS means |
|---|---|---|
| `sweetline.warden_tamed_lead_hands_over` | SCRUB_WARDEN_FIX_TAMED_BOSS_STILL_REIGNS A1 | with the first warden tamed (no prune), the lead passes to the next wild warden |
| `sweetline.warden_tamed_tree_still_watched` | same | a colonist's CutPlant raises the meter within 960 ticks (the chain then stops the job and calms the roost) |
| `edge_fixes.pyre_thin_line_follows_blaze` | SCRUB_PYRE_FIX_FIVE_FIRES_FIVE_ISLANDS A1 | 5 fires as 5 islands read "too little caught"; the same 5 in one cluster do not (no stamper needed) |
| `edge_fixes.bloom_spares_manhunter` | SCRUB_BLOOM_FIX_MANHUNTER_GETS_SHY A1 | the calm crustweevil flees and the manhunting one keeps its rage |
| `edge_fixes.map_step_refuses_pawn_cell` | SCRUB_GENSTEP_FIX_TIDIES_THEN_QUITS A1 | the sweetline step refuses a cell holding a pawn and keeps that cell's steel and grass |
| `edge_fixes.vissler_arm_draws_meat_eaters` / `_off_draws_none` | LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 A2 | every meat-eating walker on the roster picks a hungry-adjacent arm; none does with the toggle off |
| `dripping.dripping_survives_harvest` | LEANINGSCRUB_ENRICHMENT_QUICKTEST_1 A3 rerun | reads "N% grown" (4cdec5dd8). A missing line is now UNMEASURED, never a pass |
| `stamp.*`, `pyre.pyre_lights_fields_and_calls_herd`, `bystanders.*` | LEANINGSCRUB_ENRICHMENT_QUICKTEST_1 A3 (GREEN-MIN) | need RSW_ShrublandGiant's RM_FireStamperExtension: **biomes_sprint only** |

- **Never live-test:** SCRUB_BLOOM_FIX_ERUPTOR_FLEES_GROUNDED A1. It is the eruptor taking off, which is flight, so
  it waits for a joint session with the owner. Dustflutter launch (`scrub_runway_bloom_launches_dustflutters`) is the
  same.

**What the owner walks.** The saved Scrub site, or a fresh RM_LeaningScrub map saved as `RM_Review_LeaningScrub_<date>`
(TBD). The Lean heading is locked before the save.
- North-star walk bars (DRAFT, agent guesses for him to accept or cut): `design/validation_walks/RimMandrake/LeaningScrub.md`.
  Look at: the scrub leaning one way with the wind, the Gale reading as driven dust (picked dust art A is installed), the
  Stall holding small animals still, the fuzz plain, the venomvine forms told apart, the sweetline tree as a landmark,
  and the fauna line-up. Two things must never show: a windless calm day, and mixed lean directions.
- SCRUB_WIND_BUILD_LEAN_ON_PURPOSE A5 (L4): the lean and the Gale, in game.
- LEANINGSCRUB_MECHANICS_BUILD_1 A3 (L4): his nine-mark re-score.
- LEANINGSCRUB_VENOMVINE_SITTING_1: all 11 venomvine forms in one in-game sitting.
- SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY A2: the settings window, where the master greys its dependents and Reset-all works.
- Art still waiting on his pick, which is a sheet and not the walk: LEANINGSCRUB_SHEET_ART_REDO_1 (26 kept-art
  conflicts and 6 awaiting a pick). BARKWARDEN_TINT_JUDGE_GREY_ON_GREY: look at the three creatures in the review save.
- **Leave out:** the titan passage (no giant homed: LEANINGSCRUB_TITAN_POPULATE_SCRUB_UNSTOMPED).

## 3. Cauldron

**Machine rows first (driver).**
1. **A fresh RM_Cauldron map is required.** `RM_TestSite_cauldron_v2` was generated before the vent-ring fix
   (637645762), so `vent_gardens` reads UNMEASURED (`ringPass=0`) on it. Either generate a fresh map, or, after the
   deploy, rebuild the site (`test_site_saves.py build cauldron`, which makes v3).
2. On that fresh map, run the Cauldron chains `vent_gardens` and `ruins` first: they read the map as generated, before any
   chain clears a pad. `vent_flowers_ring_vs_control` PASS means each vent flower is at least 3 times denser in its vent
   ring than more than 20 cells from every vent. This is CAULDRON_VENT_ENRICHMENT_HOOKS_1 A3.
3. For the A4 OFF arm, generate a second fresh map with `ventGardensEnabled` off. The same row must read PASS there
   with flat rings (`ringPass=2`).
4. On the same Cauldron map, run ExplosiveGrowth `probe_stalled.stalled_biome_never_cycles` (EXPLOSIVE_PLANT_GROWTH_1 A3).
   On a stalled map, r=0.4 on every arm is the ruled stunted rate and **not a bug**. The row proves the "never cycles"
   half: a forced charge must be dropped by one real ledger pass. On a Cauldron map `probe_rules` now reads
   UNMEASURED (SITE) on purpose.
5. Still owed and untouched here: CAULDRON_ENRICHMENT_LIVE_PROOF_1 A4 (all three toggles off), and
   CAULDRON_MECHANICS_BUILD_1 A1-A7 (L1/L2/GREEN-MIN).

**What the owner walks.** That fresh map, saved as `RM_Review_Cauldron_<date>` (TBD).
- North-star walk bars (DRAFT): `design/validation_walks/RimMandrake/Cauldron.md`. Look at: wet-black dusk at noon,
  the vent-bloom haze, never rain or snow, metal-sweating trees, the two dark soils (his sheet picks were installed at
  7cf999388), the natives told apart, and never a magenta square.
- New since the last look: **vent flower rings**. Crystal flowers ring stable vents, blood bouquets ring chronic
  leaks, and giant toxic flowers ring the vent that blew out lately. They should be visible at play zoom around the
  4-5 mapgen vents.
- CAULDRON_ENRICHMENT_VISUALS_1 A3 (L4): dewfall beads and saturation, assay flecks on old trees, and vexxiss prints.
- CAULDRON_MECHANICS_BUILD_1 A8/A9 (L4).
- **Leave out:** `cauldron_suush_floats`. The suush is a flyer (`fauna.suush_can_fly`), so it waits for a joint
  session. The titan passage has no giant here either (CAULDRON_TITAN_POPULATE_POT_WITHOUT_A_LID).

## 4. Contagion

Another helper owns it. Nothing in this file is about it.
