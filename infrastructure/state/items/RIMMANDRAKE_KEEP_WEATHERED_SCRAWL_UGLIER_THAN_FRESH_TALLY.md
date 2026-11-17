## spec
Found by the Graffiti 0.1.0 blind challenge, cycle 2 (RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_TWO_TESTS_FIRST), 2026-11-17. Class: **Polish**, bar `ugliness_visible`.

**Criterion:** the same hand's scrawl inspects uglier than its tally (the bar names no age; its scene reads them fresh)

**Evidence:**
- NetBeauty = MarkBeauty x (1 - 0.6 x Fade) and a scrawl's life is 0.8x a tally's, each +-25% by id: an awful hand's scrawl (id 2) and tally (id 3) painted the same tick outdoors read -5.23 and -6.0 at day 9.5 (scrawl at weather step 3, tally at 0); a poor hand flips at step 4 (-2.4 vs -2.5) [measured, the kernel formulas replayed in python]
- the picture weathers with the stat (eroded paint), so look and stat still move together; lane 1 row L1_UGLINESS_SAME_HAND_EVERY_CRAFT passes fresh

**Smallest fix:** wear the vandalism separately: NetBeauty = CraftBeauty x worn - ScrawlVandalism (or floor the scrawl's worn beauty at the tally's), with a fuzz case over age

Record: `design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/faults.json`.

## criteria
a weathered scrawl never inspects less ugly than the same hand's same-day tally

## verify
Acceptance test: a GraffitiFuzz beauty case over age (same hand, same tick, any two ids, roofed or not): NetBeauty-as-computed of the scrawl < the tally's at every age before either is gone. None exists yet; the python replay in faults.json evidence fails today (ids 2/3, day 9.5).
