# Huge Things Rot walk — grid key (2026-10-07)

Save: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\HugeThings_RotWalk_2026-10-07.rws`
Map: quicktest map on a tile set to `RM_TheRot`, full mod list, paused, noon, clear. Ground in x 40-209, z 55-199 cleared and laid `RM_TheRotGrass`; all plants there destroyed first. No hostiles existed. Wild animals (nonplayer, not hostile) remain elsewhere on the map.

Each giant is at growth 1.0. The giant stands at its own cell; the trunk blocker Things (`RM_HugeTrunkBlocker`) stand from that cell's x-1 and northward, the plant's own cell stays open (design). Cells are (x, z), z grows north. Pitch 40 east-west, 35 north-south.

| cell | giant (defName) | name | drawn width | trunk W x D | blockers found |
|---|---|---|---|---|---|
| (80, 90) | AB_AgariluxPrime | grath elder | 20 | 4 x 4 | 15 (x79-82, z90-93, minus own cell) |
| (120, 90) | AB_DribblingCap | ruvvak weeper | 12 | 3 x 3 | 8 |
| (160, 90) | RM_Nogtyl | brommok timber | 12 | 3 x 3 | 8 |
| (80, 125) | RM_Arpeau | churrun mast | 10 | 2 x 2 | 3 |
| (120, 125) | AB_ArbuscularMycorrhiza | bollusk trunk | 9 | 3 x 3 | 8 |
| (160, 125) | AB_AgaricusDomeCap | skarrow dome | 7 | 3 x 2 | 5 |
| (80, 160) | AB_GiantAgarilux | vokkun pillar | 6 | 2 x 2 | 3 |
| (120, 160) | RM_PaleTree | quellan tree | 6 | 2 x 2 | 3 |
| (160, 160) | AB_WitchesOyster | turrok shelf | 6 | 2 x 1 | 1 |

All nine exist and every blocker count equals W x D minus 1, matching the patch. Re-read after reload of the save: unchanged.

Colonists: four at (116/120/124/128, 72) south of the grid; four more at (80,128), (160,128), (120,163), (80,152) added so the fog overlay reveals the grid (see below). Eight in all.

Things to know before judging
- Blockers appear only after a map tick (staged plants had none until ~375 ticks ran); the save already holds them.
- A fog-of-war overlay hides everything outside colonist sight even on this map (vanilla fog reads 0 fogged cells). The extra colonists revealed the grid for 240 ticks; the area is remembered, but unseen cells go dark again if the overlay behaves differently on his machine.
- Dark rubble/cliff strips remain near (66,113), (190,112) and (48,83) inside the cleared rectangle; terrain there was not fully flattened. They are outside the giants' footprints.
- Trunk sizes are first guesses from drawn width; nothing was fixed here. No visibly wrong trunk was judged from the screenshot (the whole-grid shot at this zoom is too small to compare trunk to art).
