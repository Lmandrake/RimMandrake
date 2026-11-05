You are a blind art judge for RimWorld mod art you did not make. Judge only.

Bar (the item's done-when): "Each pipe-pole look has its own art: an upright oblique support with a saddle clamp gripping the overhead pipe at the PipeSpan seat height, no insulators; four looks; judged on a true-scale sheet beside a human and the PipeSpan strand." The defect being fixed: pipe poles wore the GSS power-pole art (crossarm + insulator crowns), so a pipe support read as an electrical pole and nothing visibly held a pipe.

Image 1 (sheet_final.png): true scale, 64 px per cell. One row per look, top to bottom Scrapper, Industrial, Modern, Futuristic. Leftmost in each row: the OLD stand-in (the GSS power mast), for contrast only, NOT judged. Then two NEW pipe poles joined by that look's pipe span strand, with a vanilla colonist between them. The span is drawn over the poles because the game draws spans above buildings (so the clamp's top strap is hidden under the pipe in game; the saddle shows below it); it is drawn straight (in game it sags slightly).
Image 2 (heads_2x.png): the new pole heads at 2x nearest-neighbour; top row = left pole of each pair, bottom row = right pole; looks left to right Scrapper, Industrial, Modern, Futuristic. (White bars are crop padding, not art.)
Image 3 (ref.png): the four old masts at full texture size with each look's ground pipe below, for material-family reference.

For each look decide PASS or FAIL: reads as a pipe support, not a power pole; no insulators; a saddle clamp visibly holding the pipe at strand height; matches its look's material family; sensible scale beside the colonist; no rendering defects (halos, fringes, key-colour residue, cut-offs). FAIL only for a defect a player would notice at normal game zoom; list minor points separately.

Answer ONLY with JSON: {"looks":{"Scrapper":{"verdict":"PASS|FAIL","why":"...","minor":["..."]},"Industrial":{...},"Modern":{...},"Futuristic":{...}}}
