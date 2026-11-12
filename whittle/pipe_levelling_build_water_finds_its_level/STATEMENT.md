# PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: done statement

Item title: Connected bodies of water level out slowly through pipes by gravity (extending tanks' slow gravity emptying), owner: 'Let's see if we can do this'. Feasibility first. Spec: design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §Owner's answers 7
Written by wc.py setup (no model) from the ledger criteria and `infrastructure/state/items/PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL.md`; the item file's spec and verify sections are the owner's words where it has them.

- **A1 (L0):** offline built baa270b9e8+0ac23150a2: SelfTest LEVELLING_* (Source/SelfTest/LevellingChecks.cs) green: exact volume incl. limitless net, energy never rises, two-
- **A2 (L0):** budget case: 200 bodies (40 of 40,000 squares), 400 links, 64 links per cycle: kernel 89 us per 250-tick cycle; feasibility written in the design doc's ### Leve
- **A3 (L1):** 325x325 map, two 40,000-cell basins, 200 links: live tick time and allocations of RM_Levelling.Tick (the dug-run walk is unmeasured offline).
- **A4 (L2):** two ponds of unequal height joined by a hose with two open ends level out (HoseNetProbe levelMoves > 0, surfaces within 1 cm), the hose reads "Levelling: flowin
- **A5 (L2):** a water pond and an oil pit joined the same way exchange nothing; the hose reads "different liquids never mix".
