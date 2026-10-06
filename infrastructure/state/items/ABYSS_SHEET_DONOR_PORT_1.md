# ABYSS_SHEET_DONOR_PORT_1 — the Abyss's donor rows become our own RM_ creatures and plants

Source: the owner's Abyss art sheet, ruled 2026-10-05
(`Transient/biome_ffar/abyss_sheet_2026-10-04.decisions.json`, ingested at `26df94528`; notes are verbatim there).
Art jobs: `Transient/biome_ffar/abyss_redo_jobs_2026-10-05.json` (each row carries `authored_label` /
`authored_description` = the text below, and `owner_note` = his verbatim note). Port machinery:
`DONOR_DEFS_PORT_TO_OURS_1` — use it, do not fork it. Biome mod: `src/RimMandrake/Abyss/` (composed into `mandrake.rm.biomes`).

## spec

He ruled 17 donor rows (15 after sitting 2 cut the shadow charger and thunderox) "Needs whole new description and name and graphics" (the sheet showed the
crag labels vrakk, dhukk, … with the donor art, so those labels are superseded too). Each becomes an
owned `RM_` def in the Abyss mod, ported from the donor's stats, under the name and description below,
cast in `RM_Abyss` in the donor row's place at the same commonality, the donor row removed. Names are invented and franchise-free (Q11a). Two registers, owner 2026-10-05:
- **The black, many-eyed family** (the 8 creatures here plus `RM_Skarnix` ishvarith, `RM_Drokattak` ombrathia,
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
| AA_Nightling | RM_Sesserith | sesserith | donor | A lean, long-skulled night hunter on six spindly legs, its hide pitch black, with a row of small eyes glowing yellow down each side of its narrow head. A ridge of long, bone-white barbed spines runs from its neck to the tip of its tail; it shakes them off in a rattling spray as it lunges, and whatever they stick in, it follows down. Like all the black, many-eyed things of the Abyss, it seems less evolved than made, as if some old and patient cruelty once had the shaping of it. |
| AA_NightRam | RM_Olumetha | olumetha | donor | A broad, low grazer, inky black, with a heavy wedge of fused plates for a brow and four glowing yellow eyes beneath it. It crops glow-grass by night with its head down, and if cornered it does not turn: it drives the plated wedge forward and keeps driving. Herders say its line was bred long ago to serve masters who prized obedience above everything. |
| AA_NightMule | RM_Aveluthia | aveluthia | donor | A tall, ponderous pack beast hung in thick wrinkled folds of black flesh, on four pillar legs with broad splayed toes for loose obsidian scree. Its long head ends in a heavy drooping snout, and above it four yellow eyes glow softly. Nothing in the crags carries more, and it walks the Dark without a lamp. Old tales say the dark-robed masters who once ruled here bred it to bear their burdens, and it still bows its head to a hard voice. |
| AA_Murkling | RM_Lirrith | lirrith | donor | A small, quick, thin-legged scavenger with dark skin drawn tight over its ribs and a long hooked tail carried curled over its back. A fluted crest of pale green ridges runs up its snout, and below it four eyes glow yellow. It hums to its kin through that crest, too low for human ears, and a pack can strip a carcass or a careless camp's stores in the time it takes to light a lamp. Its bite festers, and the crag-tellers say that is no accident of nature. |
| AA_CrepuscularBeetle | RM_Moravatha | moravatha | donor | A huge, slow, many-legged grazer under a domed carapace of overlapping blood-dark plates as long as a cart, with four glowing yellow eyes set in its blunt head. It wakes when the Dark thickens and hardly sleeps. The crags' old masters broke it to the yoke, and a moravatha will still haul all night without complaint, as if it remembered whose it was. |
| AA_DarkVandal | RM_Ossumatha | ossumatha | donor | A squat slab of pitch-black, plated muscle that roots through the grit in groups with a shovel-shaped lower jaw, four yellow eyes glowing above it. Harm one and the whole group turns at once; an ossumatha rampage has ended more than one careless camp. Its rage is so complete and so quickly shared that the old stories call it a weapon someone once made and then lost. |
| AA_DuskProwler | RM_Ysvaltha | ysvaltha | donor | Something bred for killing rather than born to it: a long, low, sinuous body in near-black hide, a whip of a tail fringed with crimson barbs, and a narrow, needle-pointed head set with four glowing yellow eyes. Along its shoulders it carries curved, crimson-edged blades folded back like swept wings; they fling it forward faster than the eye can follow and open as it strikes. The dark masters who made it are long gone; their hounds were hunted almost to nothing, and few who see one see it twice. |
| AA_Darkbeast | RM_Nevarithia | nevarithia | donor | A great hunched beast on four heavy, hook-clawed legs, its charcoal hide split by veins of sickly yellow-green light and its back, shoulders and long jaw grown through with curved black spikes that are not bone. It carries a knot of the Dark with it wherever it walks, a moving patch no lamp can reach, and lets the whole of it loose only when it dies; its glowing veins pulse faster when it is roused. It is the oldest and strangest of the black kin, and the likeliest to have been made by those who mastered the dark. |
| AG_Gamma | RM_GlowGlobe | glow globe | **x2** ("great idea. Make twice as big.") | A low plant that grows a single round glowing globe the size of a melon on a short curved stem, soft-lit from within like a paper lantern. Colonists set them out as lamps. Nobody eats one twice: the flesh of the globe is deeply poisonous. |
| AB_GiantGamma | RM_GiantGlowGlobe | giant glow globe | donor; a BRIGHT natural sunlamp | The wild giant of the glow globe: a thick, twisted trunk lifting one huge glowing globe higher than a man, so bright it lights a farm-plot around it like a sunlamp. Light-shy plants and fungus should be kept well away from it. |
| AB_ToxicGamma | RM_SicklyGlowMushroom | sickly glow mushroom | donor | A sickly kin of the glow globe that grows not one clean globe but a swollen, mushrooming mass of them, glowing a dim bilious green. It lights the ground beneath it with a sour darklight and fouls the air with spores. |
| AG_Septimum | RM_PaddleVine | paddle vine | donor | A climbing plant of scarlet vines twined around one another, bearing broad, flat paddles in place of leaves and crowned with one huge flower-like leaf. Every surface glistens with fine faceted photoreceptors, like the eye of a fly, and the whole plant turns slowly toward any light. Its vines yield a tough, glossy fibre that weaves into hard-wearing cloth. |
| AB_GiantSeptimum | RM_GiantFibreStalk | giant fibre stalk | **x2** | A fibre stalk grown to an enormous age: a column of ridged segments as thick as a man and twice as tall, crowned with a heavy flowering head. Its fibres are too old and hard to work. |
| AB_GiantStikehr | RM_TreeMushroom | tree mushroom | **x4** | A towering fungus whose stalk has hardened into true wood, crowned with a broad cap that glows faintly through the drifting dark. Felled, it yields timber; standing, it is the nearest thing the Abyss has to a forest. |
| AB_WildRadagast | RM_GlowberryBush | glowberry bush | donor | A low, twisting shrub of black wiry stems hung with clusters of small berries that glow like embers held in the hand. The berries are good to eat, and give a little light to pick them by. |

Also on this item:

1. **AB_GlowingGrass** — "More realistic, more variations." No rename asked. Port to an owned grass def
   (Graphic_Random) when the flora port lands; his three kept variants are being re-tinted (`abyss_glowinggrass_{a,b,c}_tint_v1`).
2. **Wire the ruled art when it lands**: the jobs above and the sitting-2 jobs below, bound to the new defNames.
3. **Install the sheet's other keeps** (`art.py install`): RM_Krizzak variants B–F, RM_Summ's summing pick B.
4. **Sorter leftovers** (label/description/cleaning landed at `11a821c18`): three C# strings still say
   "durrgak" — `RM_AbyssMod.cs` settings labels (lines ~116–118) and `RM_AbyssCryptid.cs` ~223; likewise
   "Skarnixes flee light" in `RM_AbyssMod.cs` ~147. The labels `RM_Drokattak` → ombrathia and `RM_Cindermare` → saevitha landed
   (defNames kept); "Drokattaks rattle their quills" in `RM_AbyssMod.cs` ~128 is owed the same rename. Rename + rebuild via `winbuild.py Abyss`.
5. **Superseded art**: the 12 unwired `crags_<label>_*` sets (vrakk … thrizzik) were drawn for the
   superseded names; `ABYSS_CRAGS_ART_ON_PORTED_DEFS_1` step 1 is overtaken by this item for the 10
   rows here. The dusk rat redo there is dead (cut).
6. **Twin roster**: `RUT_Abyss` (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Abyss.xml`) carries none of the cut rows
   (sitting 2 cut the shadow charger and thunderox from both rosters). When the ports land, its donor rows follow `RM_Abyss`.
7. `Abyss_Rename.xml` labels for the 10 ported donors die with the port; delete those blocks then.

## sitting 2 (2026-10-05 evening) — picks, recolours, cuts

Ingested from the same decisions file (rulings stamped 20:00-20:11; jobs `Transient/biome_ffar/abyss_sitting2_jobs_2026-10-05.json`,
progress `Transient/biome_ffar/abyss_sitting2_close_progress_2026-10-05.md`). Descriptions in the table above are the FINAL look.

- 🔑 **Family look refined** (owner, verbatim on the dark vandal: *"Make hide pitch black with four glowing yellow eyes"*):
  the black kin are pitch/inky black with FOUR GLOWING YELLOW EYES. Recolour jobs (`*_v3`, derived per facing from his pick)
  are the art to wire: moravatha (pick tarrgun), ossumatha (gukkath), ysvaltha (rakketh), lirrith (kittrik), aveluthia (gaddrum;
  his baby/female picks were the donor's in-game AA_NightMule_baby B / _female C), olumetha (dugrath), sesserith (grothik; puppy
  pick = donor AA_NightlingPuppy B; his note gives yellow eyes, not a count, so its eye count is kept).
- **Wire as picked, no regen:** nevarithia = abyss_ugrothar_v1; giant fibre stalk = abyss_elderskeddra_v1; sickly glow mushroom =
  abyss_blightbulgra_v1; giant glow globe = abyss_greatbulgra_v1 (+ variants b/c_v2); glowberry bush = abyss_vettrig_v1 (+ b/c_v2);
  glow globe = abyss_bulgra_v1 (+ b/c_v2); tree mushroom = Graphic_Random of abyss_morkhul_v1 + abyss_treemushroom_c_v2 (his C,
  re-rendered at 1024 for the x4 size: "Needs regen at proper resolution.").
- **Glowing grass:** his three kept variants re-tinted dull glowing yellow-green (`abyss_glowinggrass_{a,b,c}_tint_v1`).
- **AG_Septimum** is now `RM_PaddleVine` / paddle vine (his note: "Needs whole new description and name and graphics. Try again,
  that looked like bad computer art. ..."); `abyss_paddlevine_v1`. The giant (`RM_GiantFibreStalk`, "Looks good.") kept its name.
- **Cut, both RM_Abyss and RUT_Abyss:** AA_ShadowCharger ("Cut this. Don't need it anymore."), AA_Thunderox ("cut this, no longer
  needed") — their RM_Sirathia / RM_Velessith ports are dropped.
- Done in this sitting, not owed here any more: #3 etchcap folder (Etchcap/Etchcap_a..c installed), wickwood Graphic_Random
  (RM_Wickwood_a..c), cindermare and ishvarith Graphic_Multi with their facing sets, ombrathia v2 installed.

## criteria

Each of the 17 rows is an owned `RM_` def carrying the name and description above, cast in `RM_Abyss`
in the donor's place, with its ruled art; no `AA_`/`AB_`/`AG_` row remains in `RM_Abyss`; sizes
x2/x2/x4 applied; Abyss `validation.py` static PASS.
