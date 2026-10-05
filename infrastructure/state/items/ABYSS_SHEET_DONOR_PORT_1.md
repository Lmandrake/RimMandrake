# ABYSS_SHEET_DONOR_PORT_1 — the Abyss's donor rows become our own RM_ creatures and plants

Source: the owner's Abyss art sheet, ruled 2026-10-05
(`Transient/biome_ffar/abyss_sheet_2026-10-04.decisions.json`, ingested at `26df94528`; notes are verbatim there).
Art jobs: `Transient/biome_ffar/abyss_redo_jobs_2026-10-05.json` (each row carries `authored_label` /
`authored_description` = the text below, and `owner_note` = his verbatim note). Port machinery:
`DONOR_DEFS_PORT_TO_OURS_1` — use it, do not fork it. Biome mod: `src/RimMandrake/Abyss/` (composed into `mandrake.rm.biomes`).

## spec

He ruled 17 donor rows "Needs whole new description and name and graphics" (the sheet showed the
crag labels vrakk, dhukk, … with the donor art, so those labels are superseded too). Each becomes an
owned `RM_` def in the Abyss mod, ported from the donor's stats, under the name and description below,
cast in `RM_Abyss` in the donor row's place at the same commonality, the donor row removed. Names are
invented, franchise-free (Q11a), crag accent, checked 2026-10-05: 0 repo hits, 0 Wookieepedia titles.

| donor | new defName | label | size | description |
|---|---|---|---|---|
| AA_Nightling | RM_Grothik | grothik | donor | A lean, long-skulled night hunter that runs on six narrow legs. Its back bristles with loose barbed spines that it shakes off in a rattling spray as it lunges, and whatever they stick in, it follows down. It hunts only in the Dark and reads the crags with a row of small pale eyes along each side of its head. |
| AA_NightRam | RM_Dugrath | dugrath | donor | A broad, low grazer with a heavy wedge of fused plates for a brow. It crops glow-grass by night with its head down, and if cornered it does not turn: it drives the plated wedge forward and keeps driving. |
| AA_NightMule | RM_Gaddrum | gaddrum | donor | A tall, patient pack beast with a long sloping back built to carry, broad splayed feet for loose obsidian scree and a hide of thick wrinkled folds. It gives little milk and no wool, but nothing in the crags carries more, and it walks the Dark without a lamp. |
| AA_Murkling | RM_Kittrik | kittrik | donor | A small, quick scavenger that runs in chattering packs. It hums to its kin through a fluted crest on its snout, too low for human ears, and a pack can strip a carcass, or a careless camp's stores, in the time it takes to light a lamp. Its bite festers. |
| AA_CrepuscularBeetle | RM_Tarrgun | tarrgun | donor | A huge, slow, many-legged grazer under a domed carapace of overlapping plates, as long as a cart. It wakes when the Dark thickens and hardly sleeps, and the crags' old people broke it to the yoke: a tarrgun will haul all night without complaint. |
| AA_ShadowCharger | RM_Kraddun | kraddun | donor | A rangy grazer with two long, back-swept horns and a ridge of stiff bristle down its spine. Placid most of the year, the females charge and lock horns in the breeding season. Colonists ride it for its speed and keep it for rich milk and plenty of meat. |
| AA_Thunderox | RM_Bragmor | bragmor | donor | A heavy, shaggy grazer with a short stump of a horn and a deep chest that it fills to bray at the first prickle of a coming Witchfire storm; herders still listen for it. Kept for thick milk, warm fur and meat, it heals faster than almost anything else that grazes. |
| AA_DarkVandal | RM_Gukkath | gukkath | donor | A squat slab of muscle that roots through the grit in groups for buried fungus with its shovel-shaped lower jaw. Harm one and the whole group turns on you at once; a gukkath rampage has ended more than one careless camp. |
| AA_DuskProwler | RM_Rakketh | rakketh | donor | Something bred for killing rather than born to it: long-bodied and narrow, with muscular spring-blades folded along its back that fling it forward faster than the eye can follow and open as it strikes. Old hunts drove it almost to nothing; few who see one see it twice. |
| AA_Darkbeast | RM_Ugrothar | ugrothar | donor | A great hunched beast whose body is grown through with dark iron spines that are not bone. It carries a knot of the Dark with it wherever it walks, a moving patch no lamp can reach, and lets the whole of it loose only when it dies. Most hunters leave it alone for that reason. |
| AG_Gamma | RM_Bulgra | bulgra | **x2** ("great idea. Make twice as big.") | A low plant that grows a single round glowing globe the size of a melon on a short curved stem, soft-lit from within like a paper lantern. Colonists set them out as lamps. Nobody eats one twice: the flesh of the globe is deeply poisonous. |
| AB_GiantGamma | RM_GreatBulgra | great bulgra | donor; a BRIGHT natural sunlamp | The wild giant of the bulgra: a thick, twisted trunk lifting one huge glowing globe higher than a man, so bright it lights a farm-plot around it like a sunlamp. Light-shy plants and fungus should be kept well away from it. |
| AB_ToxicGamma | RM_BlightBulgra | blight bulgra | donor | A sickly kin of the bulgra that grows not one clean globe but a swollen, mushrooming mass of them, glowing a dim bilious green. It lights the ground beneath it with a sour darklight and fouls the air with spores. |
| AG_Septimum | RM_Skeddra | skeddra | donor | A tall, stiff plant built of stacked ridged segments, each ending in a whorl of narrow blades. Its stalks yield a tough, glossy fibre that weaves into hard-wearing cloth. |
| AB_GiantSeptimum | RM_ElderSkeddra | elder skeddra | **x2** | A skeddra grown to an enormous age: a column of ridged segments as thick as a man and twice as tall, crowned with a heavy flowering head. Its fibres are too old and hard to work. |
| AB_GiantStikehr | RM_Morkhul | morkhul | **x4** | A towering fungus whose stalk has hardened into true wood, crowned with a broad cap that glows faintly through the drifting dark. Felled, it yields timber; standing, it is the nearest thing the Abyss has to a forest. |
| AB_WildRadagast | RM_Vettrig | vettrig | donor | A low, twisting shrub of black wiry stems hung with clusters of small berries that glow like embers held in the hand. The berries are good to eat, and give a little light to pick them by. |

Also on this item:

1. **AB_GlowingGrass** — "More realistic, more variations." No rename asked. Port to an owned grass def
   (Graphic_Random) when the flora port lands; 3 variants queued (`abyss_glowinggrass_{a,b,c}_v1`).
2. **Wire the ruled art when it lands**: the 53 jobs above, plus RM_Cindermare's three facings
   (def is Graphic_Single today → Graphic_Multi), RM_Drokattak v2 (black/purple), the gekkrith set for
   `RM_Skarnix` (label renamed at `11a821c18`, defName kept: `RUT_Abyss` casts it), etchcap b/c and
   wickwood b/c variants (both become Graphic_Random folders).
3. 🔴 **RM_Etchcap renders nothing today**: its `graphicClass` is `Graphic_Random` but its texPath
   `RM_Abyss/Things/Plant/Etchcap` is a single PNG (`Etchcap.png`), not a folder. Moving it into
   `Etchcap/Etchcap_a.png` goes through the art ledger (`move_mod_textures.py`) with the variants.
4. **Install the sheet's other keeps** (`art.py install`): RM_Krizzak variants B–F, RM_Summ's summing pick B.
5. **Sorter leftovers** (label/description/cleaning landed at `11a821c18`): three C# strings still say
   "durrgak" — `RM_AbyssMod.cs` settings labels (lines ~116–118) and `RM_AbyssCryptid.cs` ~223; likewise
   "Skarnixes flee light" in `RM_AbyssMod.cs` ~147. Rename + rebuild via `winbuild.py Abyss`.
6. **Superseded art**: the 12 unwired `crags_<label>_*` sets (vrakk … thrizzik) were drawn for the
   superseded names; `ABYSS_CRAGS_ART_ON_PORTED_DEFS_1` step 1 is overtaken by this item for the 10
   rows here. The dusk rat redo there is dead (cut).
7. **Twin roster**: `RUT_Abyss` (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Abyss.xml`) still
   casts the cut rows; the sheet's cut was scoped to `RM_Abyss` (sheet law). Owner question, not done.
8. `Abyss_Rename.xml` labels for the 10 ported donors die with the port; delete those blocks then.

## criteria

Each of the 17 rows is an owned `RM_` def carrying the name and description above, cast in `RM_Abyss`
in the donor's place, with its ruled art; no `AA_`/`AB_`/`AG_` row remains in `RM_Abyss`; sizes
x2/x2/x4 applied; Abyss `validation.py` static PASS.
