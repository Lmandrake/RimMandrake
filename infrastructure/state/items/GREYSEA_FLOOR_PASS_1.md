# GREYSEA_FLOOR_PASS_1 — the whole Grey Sea floor pass

Filed 2026-09-25 under the owner's structure directive (typed to BENCH): one whole
pass per sea floor biome, INDIVIDUALLY, one sea at a time. The umbrella is
`SEA_FLOOR_AND_CATCH_PASS_1`; this item is the Grey Sea's execution. This file was
written 2026-09-27 to give the item the sections it reached `ready` without — the
ledger notes on this item are the primary record; nothing here supersedes them.

## Where it stands (from the 2026-09-26 sitting, all on this item's ledger)

- **Cast and catch are in good shape; the PLACE is not built** (BEDAZZLE inventory,
  note 2026-09-26T17:48). Cast: 5 of ours incl. `RM_Reefback` and `RM_Fessk`.
  Catch: 9 entries, maxFishPopulation 120, plus `RUT_RareGreyCatches`.
- **Fish RULED yes** (owner, 17:20) — overturns the roster's no-fish call; catch must
  be BIZARRE invented creatures, never reskinned vanilla fish.
- **Content drop captured** → `design/Jawa/worldbuilding/biomes/the_grey_deep_content_2026-09-26.md`
  (804 lines, verbatim); owner ruled it MERGES INTO the frozen sheet as additions (19:09).
- **Flora pass landed** → `the_grey_deep_flora_pass_2026-09-27.md` (`GREYSEA_FLORA_PASS_1`,
  plantDensity 0.14–0.22 proposed) — awaiting its sitting.
- **Danger/floor draft** → `the_grey_deep_danger_floor_pass_2026-09-27.md`.

## State 2026-10-02

All nine build children are done; `GREYSEA_FLORA_PASS_1` (doing) and `GREYSEA_RULED_CONTENT_1`
(blocked) remain. Nothing reaches a player until `SEABED_PER_SEA_FLOORS_1` gives the layer a real
per-sea floor; the live walk waits on that.

## spec — what closes this item

The build rides the filed children; this item closes when the Grey Sea floor map is
a PLACE, not just a cast list, and the owner has walked it in a live review sitting.

1. Children built and closed: `GREYSEA_ANCHOR_CREATURES_1` (pillar-mason + ossuary
   shrimp anchors; AA_Aerofleet cut is Grey-scoped only),
   `GREYSEA_FLOOR_FORMATIONS_1` (the pillars — the navigation system, currently NO
   def of any kind, the biggest hole), `GREYSEA_CRYSTAL_FLORA_1`,
   `GREYSEA_SALT_SNOW_WEATHER_1`, `GREYSEA_BRINE_POOL_DEFENCE_1`,
   `GREYSEA_BRINE_ELDERS_1`, `GREYSEA_SALT_CUISINE_1`, `GREYSEA_SESSILE_LAYER_1`,
   `GREYSEA_SHORE_MUTATOR_SPECIFICS_1`.
2. Flora ruled (Grey flora pass sitting) and the ruled roster wired with real
   plantDensity — the biome currently has zero plants, hasVirtualPlants false.
3. Reconciliation row settled AT THIS ITEM'S SITTING (carried from
   `TERMINALBIOMES_RM_MOD_BUILD_1`, 2026-09-25): RM_GreySea's pre-existing
   RUT_Sallik-family fishTypes vs the ruled sparse-by-law catch — coexist or cull.
4. Owner decisions owed (content-drop note, 18:50): five places the drop may
   contradict the frozen sheet (second colossal organism; abundant sessiles;
   retracting flora; salt snow; chemosynthesis) — BENCH's position is all five are
   additive; only he can rule. Plus the drop's §9 ten open questions, and the
   'Reshapers' exonym naming.
5. Roster amendment: the roster JSON's `flora: []` is now false; amend at the sitting.

## verify

- Every child item above closed, or explicitly re-scoped with a note here.
- A ship flown to the Grey Sea floor (the `RM_SeabedLayer` planet layer; the dive hatch is retired)
  lands on the Grey's own floor map with pillars, ruled flora, own terrain/weather where ruled — not
  the generic placeholder floor. Gated on `SEABED_PER_SEA_FLOORS_1`.
- Live review sitting held: the owner walks the floor map and rules it done.
