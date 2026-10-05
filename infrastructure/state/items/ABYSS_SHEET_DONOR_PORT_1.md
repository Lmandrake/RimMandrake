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
cast in `RM_Abyss` in the donor row's place at the same commonality, the donor row removed. Names are invented and franchise-free (Q11a). Two registers, owner 2026-10-05:
- **The black, many-eyed family** (the 10 creatures here plus `RM_Skarnix` ishvarith, `RM_Drokattak` ombrathia,
  `RM_Cindermare` saevitha): smooth, sibilant names. Owner, typed: *"Those new smooth names are for Abyss creatures of
  the black style with multiple eyes uniquely. The 'possibly of Sith origin' type."* Every family description hints
  at a made, dark-mastered lineage without naming any franchise (the RM tier carries no IP). All 13 are drawn black
  with many eyes, each with its own accent colour (`abyss_family_v2_jobs_2026-10-05.json`).
- **Plants**: plain names that say what they look like (owner, by question card).
Checked 2026-10-05: 0 repo hits, 0 Wookieepedia titles (search API).

⚠️ **The 53 queued jobs were filed under the first (guttural) names** and some had already rendered when the
names changed, so the queued job files were NOT edited: their `target_def` reads the first names (`RM_Grothik`, `RM_Bulgra`, …)
The jobs JSON's `queued_as` field maps each row's job id/old target_def to the new name. Bind the renders to
the new defNames when wiring. Five jobs failed on a worker error ("Cannot run image generation while
constrained to final schema only."): bulgra, cindermare facings x3, drokattak north — requeue them.

| donor | new defName | label | size | description |
|---|---|---|---|---|
| AA_Nightling | RM_Sesserith | sesserith | donor | A lean, long-skulled night hunter on six narrow legs, black as the crags, with a double row of small pale eyes down each side of its head. Its back bristles with loose barbed spines that it shakes off in a rattling spray as it lunges, and whatever they stick in, it follows down. Like all the black, many-eyed things of the Abyss, it seems less evolved than made, as if some old and patient cruelty once had the shaping of it. |
| AA_NightRam | RM_Olumetha | olumetha | donor | A broad, low grazer, black-hided, with a heavy wedge of fused plates for a brow and a band of small dull eyes beneath it. It crops glow-grass by night with its head down, and if cornered it does not turn: it drives the plated wedge forward and keeps driving. Herders say its line was bred long ago to serve masters who prized obedience above everything. |
| AA_NightMule | RM_Aveluthia | aveluthia | donor | A tall, patient pack beast with a long sloping back, broad splayed feet for loose obsidian scree and a black hide of thick wrinkled folds, its long head set with many small, sleepy eyes. Nothing in the crags carries more, and it walks the Dark without a lamp. Old tales say the dark-robed masters who once ruled here bred it to bear their burdens, and it still bows its head to a hard voice. |
| AA_Murkling | RM_Lirrith | lirrith | donor | A small, quick black scavenger that runs in chattering packs, its narrow head beaded with eyes. It hums to its kin through a fluted crest on its snout, too low for human ears, and a pack can strip a carcass or a careless camp's stores in the time it takes to light a lamp. Its bite festers, and the crag-tellers say that is no accident of nature. |
| AA_CrepuscularBeetle | RM_Moravatha | moravatha | donor | A huge, slow, many-legged grazer under a domed black carapace as long as a cart, a ring of small glassy eyes set round its blunt head. It wakes when the Dark thickens and hardly sleeps. The crags' old masters broke it to the yoke, and a moravatha will still haul all night without complaint, as if it remembered whose it was. |
| AA_ShadowCharger | RM_Sirathia | sirathia | donor | A rangy black grazer with two long back-swept horns, a stiff bristle ridge down its spine and a crescent of eyes across its narrow face. Placid most of the year, the females charge and lock horns in the breeding season. Colonists ride it for speed and keep it for rich milk and meat; the riders who first bred it, the stories say, rode it to war under a darker banner. |
| AA_Thunderox | RM_Velessith | velessith | donor | A heavy, shaggy grazer in a coat of matted black fur, a stump of a horn on its brow and a cluster of small eyes peering out from under the shag. It fills its deep chest to bray at the first prickle of a coming Witchfire storm; herders still listen for it. Kept for milk, fur and meat, it heals faster than almost anything that grazes: a gift, some say, from whoever first bent its blood. |
| AA_DarkVandal | RM_Ossumatha | ossumatha | donor | A squat slab of black muscle that roots through the grit in groups with a shovel-shaped lower jaw, a row of tiny eyes glinting above it. Harm one and the whole group turns at once; an ossumatha rampage has ended more than one careless camp. Its rage is so complete and so quickly shared that the old stories call it a weapon someone once made and then lost. |
| AA_DuskProwler | RM_Ysvaltha | ysvaltha | donor | Something bred for killing rather than born to it: long, narrow and black, its slender head pricked all over with small cold eyes, with muscular spring-blades folded along its back that fling it forward faster than the eye can follow and open as it strikes. The dark masters who made it are long gone; their hounds were hunted almost to nothing, and few who see one see it twice. |
| AA_Darkbeast | RM_Nevarithia | nevarithia | donor | A great hunched black beast grown through with dark iron spines that are not bone, a mass of dim eyes crowded along its brow. It carries a knot of the Dark with it wherever it walks, a moving patch no lamp can reach, and lets the whole of it loose only when it dies. It is the oldest and strangest of the black, many-eyed kin, and the likeliest to have been made by those who mastered the dark. |
| AG_Gamma | RM_GlowGlobe | glow globe | **x2** ("great idea. Make twice as big.") | A low plant that grows a single round glowing globe the size of a melon on a short curved stem, soft-lit from within like a paper lantern. Colonists set them out as lamps. Nobody eats one twice: the flesh of the globe is deeply poisonous. |
| AB_GiantGamma | RM_GiantGlowGlobe | giant glow globe | donor; a BRIGHT natural sunlamp | The wild giant of the glow globe: a thick, twisted trunk lifting one huge glowing globe higher than a man, so bright it lights a farm-plot around it like a sunlamp. Light-shy plants and fungus should be kept well away from it. |
| AB_ToxicGamma | RM_SicklyGlowMushroom | sickly glow mushroom | donor | A sickly kin of the glow globe that grows not one clean globe but a swollen, mushrooming mass of them, glowing a dim bilious green. It lights the ground beneath it with a sour darklight and fouls the air with spores. |
| AG_Septimum | RM_FibreStalk | fibre stalk | donor | A tall, stiff plant built of stacked ridged segments, each ending in a whorl of narrow blades. Its stalks yield a tough, glossy fibre that weaves into hard-wearing cloth. |
| AB_GiantSeptimum | RM_GiantFibreStalk | giant fibre stalk | **x2** | A fibre stalk grown to an enormous age: a column of ridged segments as thick as a man and twice as tall, crowned with a heavy flowering head. Its fibres are too old and hard to work. |
| AB_GiantStikehr | RM_TreeMushroom | tree mushroom | **x4** | A towering fungus whose stalk has hardened into true wood, crowned with a broad cap that glows faintly through the drifting dark. Felled, it yields timber; standing, it is the nearest thing the Abyss has to a forest. |
| AB_WildRadagast | RM_GlowberryBush | glowberry bush | donor | A low, twisting shrub of black wiry stems hung with clusters of small berries that glow like embers held in the hand. The berries are good to eat, and give a little light to pick them by. |

Also on this item:

1. **AB_GlowingGrass** — "More realistic, more variations." No rename asked. Port to an owned grass def
   (Graphic_Random) when the flora port lands; 3 variants queued (`abyss_glowinggrass_{a,b,c}_v1`).
2. **Wire the ruled art when it lands**: the 53 jobs above, plus RM_Cindermare's three facings
   (def is Graphic_Single today → Graphic_Multi), RM_Drokattak v2 (black/purple), the ishvarith set for
   `RM_Skarnix` (label renamed at `11a821c18`, defName kept: `RUT_Abyss` casts it), etchcap b/c and
   wickwood b/c variants (both become Graphic_Random folders).
3. 🔴 **RM_Etchcap renders nothing today**: its `graphicClass` is `Graphic_Random` but its texPath
   `RM_Abyss/Things/Plant/Etchcap` is a single PNG (`Etchcap.png`), not a folder. Moving it into
   `Etchcap/Etchcap_a.png` goes through the art ledger (`move_mod_textures.py`) with the variants.
4. **Install the sheet's other keeps** (`art.py install`): RM_Krizzak variants B–F, RM_Summ's summing pick B.
5. **Sorter leftovers** (label/description/cleaning landed at `11a821c18`): three C# strings still say
   "durrgak" — `RM_AbyssMod.cs` settings labels (lines ~116–118) and `RM_AbyssCryptid.cs` ~223; likewise
   "Skarnixes flee light" in `RM_AbyssMod.cs` ~147. The labels `RM_Drokattak` → ombrathia and `RM_Cindermare` → saevitha landed
   (defNames kept); "Drokattaks rattle their quills" in `RM_AbyssMod.cs` ~128 is owed the same rename. Rename + rebuild via `winbuild.py Abyss`.
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
