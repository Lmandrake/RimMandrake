# BENCH live sitting 2026-10-13 (pass 7, Pyrelands only, ratchet pilot's last red suite)

Pass HEAD **365b428d7b** (`claude_sha.txt`; includes ash paint retune b761462eba and scorch-cap harness fix e0aab994e3). `git archive` of src/ at `D:\Luke\dev\_rmscratch\bench_live_20261013`.
Tier: 23 mods (ratchet_pilot + mandrake.rm.patches), Steam launch. Owner list restored, md5 ee01dae9e30d121c78d88e474dacd8e8 (matches the before-copy). Game down, bridge released.
Deploy: biomes compose, 1 file (`Biomes/Pyrelands/Defs/BiomeDefs/Pyrelands.xml`). Game-only file kept, not repo-tracked: `RM_FE_QuickgrassA.png`, so the repo-deletion prune leaves it alone. FlowWorks plan: only game-side result JSONs, not applied. The other four mods were in sync.
JawaBench TEST profile valid until 2026-10-13T06:00Z, so it was not renewed. Startup: 0 `RM_FE_AshBase`, 0 XML errors, 0 exceptions. No mod source was edited and no harness code was changed. `pawncheck.py` is a new read-only probe (colonists, tick, death letters).

## Tally
| suite | result |
|---|---|
| Pyrelands main, map A (tile 38, fresh world) | 15 rows PASS, mapgen through cinderfall_distinct, incl. **ground_deep_ash 0.925** (52145/56397) and ruins_scorched PASS. Then the game dropped to the main menu (Entry) at about 17:37-17:38. **Cause untraced**; the next pass should watch for it. Every later row (17 FAIL "could not make the Pyrelands site current", 6 UNMEASURED) is HARNESS/SITE and **not counted**. |
| map B (tile 3) | build 1: quicktest start went IndeterminateError and stayed in Entry. Build 2 OK, but the run was REFUSED at gate B 3.8.8: the temperature sampler picked an unroofed Slate_Rough cell (138,98), where cell_temperature is ok=false. HARNESS (the sampler does not skip solid rock); not fixed, map dropped. |
| Pyrelands main, map C (tile 5, fresh world) | **30 PASS / 0 FAIL / 6 UNMEASURED**: 3 skipped long chains, plus furnacebeast_warmth, fulgurite_after_lightning and herd_follows (same as pass 6). **ground_deep_ash 0.942** (of 53605). Rows from furnace_room onward ran after the colony starved (see below), so they are **not counted** and were re-run. |
| re-run on a reloaded fixture C, colonists 6 alive before and after | furnacebeast_heats_room **PASS**; ullai_wired, giant_furnace_beast, sand_shovel x2, lightning_breaker x3 **PASS**; **burrowers_dive FAIL** (no RM_Burrowed in 1500 ticks beside fire; jobs Wander/Flee; flaky: FAIL pass 5, PASS x2 pass 6); fulgurite_after_lightning, herd_follows UNMEASURED (unchanged). |
| long split | burn_line_present **PASS** (4 free fires after 120360 ticks; it finished at about tick 501861, before the first death, so it counts). The fresh_burn and embergrass_regrow rows of that run came after the deaths and are not counted; embergrass_regrow was killed mid-run, so it is UNMEASURED SITE. fresh_burn_feeds_the_field re-run alone, 6 colonists alive before and after: **PASS** (field 0.4 -> 0.896, bonus 0.496; day1 0.413; after 15 h Black Rain watered 1.4, bonus 0). |

## Bars
- ground_deep_ash >= 0.85 on BOTH maps: **MET** (A 0.925, C 0.942).
- scorchfruit_fire_born: **PASS** on C (cap fix e0aab994e3 works: 0 ScorchFruit left after the cap-budget clear).
- scorchfruit_produces: **PASS** on C (harvest yielded RM_FE_ScorchFruitYield x5 stacks; a colonist ate one, food 0.19 -> 0.28). Not reached on A.
- ruins_scorched: **PASS** on A and C.

## Colony death on the long split (coordinator/owner question)
On the fixture C reload used by the long split, all 6 colonists died of **Malnutrition**. Letters: Mie t524483, Annabel 550801, Miu 556354, Tomboy 558497, Marisa 559416, Snyder 566697; GameEnded "Everyone is dead or gone" at 567096. Tales before that: Heatstroke (Snyder) about t384.8k, Exhausted about 470k, Downed 501k-532k.
- The fixture is saved at **t381501** with 6 colonists, starting food about 0.2, no food on the map, outdoor 56 C.
- The site builder's clock jump `jawa/time_set_ticks` to local mid-summer noon SIMULATES nothing (`northstar_site.py`: "time_set_ticks simulates nothing"). The colonists did not die in the jump itself. The jump puts unfed colonists into a 50+ C midsummer, and the deaths followed about 143k-186k ticks of real simulated time: the long split's 120360-tick burn-line wait plus the fresh-burn days. So the jump and the long waits together set up the starvation. The owner's point stands: a multi-day advance with live, unfed pawns is unsafe.
- The same thing happened on map C's main run: the clock went 439471 -> 715080 inside the furnace_warmth/furnace_room chains, which is why those later rows were re-run.
- Rows that ran within 1 day of the fixture tick (up to t439471 on C) are counted. The re-runs checked colonists (6) and death letters (0) before and after each chain.
- The GameEnded letter cannot be dismissed through the letter stack (`rimworld/dismiss_letter` refused it). Reloading the fixture cleared it.

## Player.log (tier)
burnedDef-is-flammable 0, Exception 0, NRE 0, IdeoFoundation_Deity 0, 7 "error" lines (the same pre-existing RUT_Jawa/meme config errors as pass 6).
