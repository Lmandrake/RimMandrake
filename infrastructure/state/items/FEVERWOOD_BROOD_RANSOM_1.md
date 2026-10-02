# FEVERWOOD_BROOD_RANSOM_1 — the giant's story: the tank young are the sekkulaath's own, and returning them buys a gift from the bottom

Caused by `FEVERWOOD_SCORING_SITTING_1` (turn 1). Free tier for the mechanism (`mandrake.rm.feverwood`), campaign
tier for Sporefall's display tank and the Jawa trade (`src/RimUtinni/`). Design:
`feverwood_bedazzle_review_2026-10-02.md` §3 (*The Brood Ransom*), §4 row 1, §8. Ruling: the giant carries
**the ransom of its young** (decision taken by question card 2026-10-02 11:12 PDT), card text: *"the small
tentacled things every town keeps in prison tanks are its own young, and it knows: the more of them the world
holds, the bolder the pools get. Free one into a pool and the deep sets down one great gift from the very
bottom. The hook: the Wildsteam treetop town's famous display tank holds the biggest young one ever caught, and
freeing it would buy a gift and break the town's peace; the clan can also buy young ones from prisons and
"return" them for salvage."* NOT CHOSEN: the salvage house that feeds it, the lost crawler. The Wildsteam drum
was held off the card (it spends the plot-reserved emergence). The plot-reserved full emergence stays reserved:
nothing here triggers it.

## What exists (reuse, do not rebuild)

- `RM_SekkulaathTank` + `RM_CompCapturedSpecimen` (feeds, teaches, produces, escapes; occupant read from
  `occupantKindDefName`, which the campaign swaps to `RSW_Dianoga` in `RSW_SekkulaathTank_DianogaSwap.xml`).
- `RM_Sekkulaath_Juvenile` + `RM_CompEscapedCaptive` (stage 2: an escapee that reaches registered water
  "settles in").
- The porter limb's loot drop (`RM_CompTentacleLimb` l.187, `RM_TentacleLoot.RollLoot`).
- `RM_MapComponent_TentacleWatch` (ordinary emergence roll, `encounterPressure`, limb weights).

## spec

1. **The world's tally.** A `WorldComponent` `RM_WorldComponent_DeepYoung` counts the young the world holds:
   occupied tanks on every player map, `RM_SekkulaathYoungCask` items on player maps and in caravans, plus a
   per-settlement number for settlements flagged as keeping one (free tier: 0 unless a mod flags them; campaign:
   the prison towns and Sporefall). Scribed. Recomputed on a long interval, never per tick.
2. **The bolder the pools get.** `RM_MapComponent_TentacleWatch` scales its ordinary emergence chance and
   the snare/lash weights by the tally (a capped multiplier, `// INVENTED`, in Mod Settings). Readable: a
   Narrator letter when the tally crosses each threshold (*the pools have been restless since …*), and the
   pool's inspect string says how restless the deep is. Never silent.
3. **Freeing one.** Two routes, both deliberate player acts:
   - a **"Return to the deep"** gizmo on an occupied `RM_SekkulaathTank` (empties it; the juvenile spawns
     non-hostile, flagged `released`, and walks to the nearest registered pool), or
   - an `RM_SekkulaathYoungCask` item (a live young in a sealed water cask; minifiable-like carry item) used at a
     pool edge (a `CompUseEffect`, or a job on a designated pool cell).
   When a `released` young enters a Fever Wood registered pool, the porter rises at that pool within an hour and
   sets down **one great gift**: one roll from a new `RM_DeepGiftLoot` table of old, heavy things from the very
   bottom (an ancient ship component, an archotech-tier fragment, a sealed salvage crate; **defNames measured
   from the def dump, never guessed**, all DLCs assumed present). Letter names the gift. The tally drops by one.
   An **escaped** (not released) young that reaches water still only settles in (today's stage 2): no gift.
   One gift per young; a young freed outside the Fever Wood (any other water) settles in and gives nothing.
4. **Buying young.** `RM_SekkulaathYoungCask` is a trade good: free tier, exotic traders stock it rarely;
   campaign, the Wildsteam (`Jawa_WildsteamClan`) and the prison towns sell it, and the clan's own traders buy
   it back at a price that says what the deep is worth to them. The Narrator says what the deep thinks of
   traders in its children (a line on purchase and on return; campaign wording).
5. **Sporefall's display tank (campaign).** Sporefall, the Wildsteam's treetop town (`the_fever_wood.md` §8),
   holds a unique display tank, `RUT_SporefallDisplayTank` (or a flagged `RM_SekkulaathTank` instance), with the
   **biggest young ever caught** (a larger juvenile kind or a size-scaled hediff on the juvenile). Freeing it
   (stealing the young out, or breaking the tank so it escapes into a pool, then the gift rule above with a
   doubled-roll "greatest gift") **breaks the town's peace**: a large goodwill loss with `Jawa_WildsteamClan`
   and a letter from Sporefall. How the player reaches the tank (visiting the settlement map vs a quest site) is
   FOUNDRY's build call; the settlement's map or site must carry the tank.
6. **Mod Settings:** `broodRansomEnabled`, the boldness multiplier and cap, the gift-table weights, trader
   stock chance. Every field read by the code it claims to gate. All-off = today's behaviour.

Depends on: `FEVERWOOD_DIANOGA_GIANT_MAP_1` (soft: the campaign wording calls the young dianoga). Interacts with
`FEVERWOOD_DIANOGA_TANK_TUNING_1` (tank numbers) and `FEVERWOOD_TENTACLE_SETPIECE_TUNING_1` (the emergence
roll it scales): read both before changing the roll.

## criteria

Deterministic state reads, recorded in `FEVER_WOOD_FIRST_SCRIPT_1`'s `validation.py`:
- `jawa/get_defs` (`success`/`foundCount`): `ThingDef/RM_SekkulaathYoungCask` = 1; with the campaign loaded,
  the Sporefall tank def = 1.
- Tally: on a quicktest map with 2 occupied tanks and 1 cask, `RM_WorldComponent_DeepYoung`'s count (a
  `[Tool]` read) = 3; after emptying one tank via the gizmo and the young entering a pool, it = 2.
- Gift: the young released into a Fever Wood pool → within 2,500 ticks (`step_game_ticks`), exactly one new
  thing whose def is in `RM_DeepGiftLoot` exists within 6 cells of that pool, and a letter of the gift letter
  def was received. A young released at non-Fever-Wood water (or an escaped, not released, young) → 0 such
  things.
- Boldness: with tally 0 vs tally ≥ the first threshold, the TentacleWatch's effective emergence chance (a
  `[Tool]` read of the computed value, not a sampled count) is strictly greater at the higher tally, and equal
  when `broodRansomEnabled` is off.
- Campaign: after the Sporefall young is freed, `Jawa_WildsteamClan` goodwill with the player dropped by at
  least the configured amount (faction read before/after).
