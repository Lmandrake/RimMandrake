# DRAWBRIDGE_LOOKS_WIRE_PICTURES_IN_WINGS — progress (BENCH helper)
status: STARTED 2026-10-21
- [x] claim item
- [x] read code/defs/contract
- [x] looks x tiers wired
- [x] gate art wired
- [x] laid plank + end piece wired
- [x] texPath resolution check
- [x] selftests
- [ ] build + commit + publish
## live look owed (NOT deployed; game up with his review map)
Deploy FlowWorks when the game is down (deploy_custom_mods.py --mod FlowWorks --apply), then look at:
- each look (Scrapper/Industrial/Modern/Futuristic) x tier (Timber/Steel) drawbridge: lowered, raised (leaf N=Face, S=Underside, E/W=Edge, W mirrored), planks beside the hinge
- winch house per look x tier (Steel Scrapper draws the plain steel winch: no Steel_Scrapper art)
- gate in an E-W wall (face) and N-S wall (edge), shut and open, per look x tier; a SHUT TIMBER gate in Scrapper (default look) draws the VANILLA DOOR: RM_DrawbridgeGate_Timber_Closed and _Closed_Scrapper were picked A on the 2026-10-20 sheet but never installed (owed art)
- laid raid plank: mid pieces + end pieces with hooks toward each bank, on N-S and E-W spans
## open question for him
- material pictures (RM_Drawbridge*_Timber/_Steel leaf, planks, gate) now show only where a look has none, as suspension parts do; with looks loaded the default look (Scrapper) wins
- 23:58 code written (paths in RM_DrawbridgeMath.DrawbridgeArtPaths; winch Graphic, gate DrawAt, deck Print raid plank); building
- 00:02 build OK; C# SelfTest 769/769; python drawbridge_art + suspension selftests GREEN; committing
