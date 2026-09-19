# The Rot — flora and fauna names and regen briefs

**DRAFT — applied provisionally 2026-09-19 on the owner's ruling of the night before
(`ROT_FLORA_FAUNA_VERDICTS_1`, the 55-row sheet `Transient/rot_flora_fauna_review_2026-09-18`);
every name and every size here is his to overrule in the morning.** Nothing below changes
a ruling in the frozen sheet `the_rot.md`; it names what that sheet already admits.

What this file is: the 46 rows he marked **regen** (40 flora, 6 fauna), each with a new
campaign name, the mature width he ruled, a def description and a visual brief for the art
pipeline — plus the 2 rows he marked **keep** but also wrote "rename" on (agaripod, fungal
mimic mantis), which get a name and no art brief. One regen row (rustpuff) carries no note at
all, so it keeps its name and size and only gets a repaint. The machine-readable copy is
`rosters/rot_regen_briefs.json` (48 objects, `decision` = `regen` | `keep-rename`).

Inputs: his verbatim notes from the decisions file; current labels, descriptions, texPaths
and sizes read from the defs themselves (`RUT_RotSporeKit_*.xml`, `RUT_PaleTree.xml`,
AlphaBiomes' `Plants_MycoticJungle.xml`, Alpha Animals' `Races_*.xml`, SWBestiary's
`RSW_BiomesTeamPort_Races.xml`) — not from the sheet's prose.

⚠️ **Sheet defect found while doing this (MEASURED 2026-09-19):** the review sheet's
`FLORA_VSR` table lists 11 AlphaBiomes rows as "vanilla Plant-base default 0.3~1.0, not
authored on this def", and drew their to-scale panels at 1.0 cell. The defs themselves set
their own `<visualSizeRange>`: giant agarilux 3.5~6, dribbling cap 3.5~5, recurved
stropharia 3.5~5, slimy pholiota 3.5~5, arbuscular mycorrhiza 2~3.5, lilac beacon 1~2,
witches' oyster 1~2, agaricus domecap 1.5~2, glowing agarilux 1.3~2, agarilux 0.9~1.5,
glowstool 0.4~0.7. So for those rows he ruled a width while looking at a panel that was
too small by up to 6×. Both numbers are printed on each row ("sheet showed N"); where his
ruled width is *smaller* than the def's real width (giant agarilux 6 ← 6, recurved 5 ← 5,
slimy pholiota 5 ← 5) the ruling is effectively "as it is", and where it is larger
(dribbling cap 12 ← 5, domecap 7 ← 2, witches' oyster 6 ← 2) it still stands as written —
he may want a second look at exactly those six in the morning. The sheet is frozen and was
not touched.

How sizes land in the def: mature width = `graphicData.drawSize` (1.0 on every flora row)
× `plant.visualSizeRange.max`, so each ruled width becomes a `visualSizeRange` whose max is
the ruled number (keep the def's own min:max ratio, or 0.3× for a one-stage plant). Fauna
width is the adult life stage's `bodyGraphicData.drawSize`; the `bodySize` stat is a
separate number (health, meat, carry) and is **not** changed by this file — where a ruled
draw width is wildly out of step with bodySize the row says so.


## Style rules applied

Copied from `lantern_deeps_flora_names.md` (the owner's ruling there, 2026-09-18: *"New
names please just in the style of Star Wars. No nova please."* and *"I didn't want you to
look up specific canon"*), applied unchanged, plus three Rot-specific lines:

1. **Short coined noun, consonant-forward**, one or two syllables, a doubled consonant or a
   hard cluster (`-rr-`, `-kk`, `-sk`, `-th`, `-mm`) — the bantha / nerf / jogan / meiloorun /
   dianoga register. Never Latin, Greek, or a real-world mushroom name (no morel, oyster,
   stropharia, pholiota, agaricus, mycorrhiza).
2. **Coined noun + plain English job word**: `<stem> cap`, `<stem> lace`, `<stem> gourd`.
   The English half is what a farmer or a cook calls it — cap, dome, spire, shelf, mast,
   timber, trunk, lace, gill, hood, bell, lure, choker, weeper, salve, hearth, crown, veil.
3. **One coined stem per species, no shared stems, no family grades** — the four "agarilux"
   things and the two "wild-/agari-" pairs each get their own stem; kinship is written in
   the description, not the name. Nothing shares a stem with the Lantern Deeps set
   (thrakk, ossk, vellok, prenna, nurrik, quorr, zivvit, kuvra, brellik, puffer) or its
   alternates.
4. **Fauna are a bare coined noun** (bantha, nerf, dewback): no job word, because an animal
   has no single job.
5. **Lowercase labels**, vanilla convention; a defName rename is *not* proposed here — the
   defNames stay (art, patches, `wildPlants` rows and the Guardian Groves C# all key on
   them), only `label`/`description`/art change. Renaming defNames is a separate item if he
   wants it.
6. **Rot-specific:** no "nova"; no "lantern" (that word is the Deeps'); no "glow" as a stem
   (half the biome glows); a name may say what the thing *does to you* (choker, weeper,
   lure) because that is how a colonist would learn it.
7. **Harvested items are not renamed here** (`RUT_RawDulcis`, `RUT_Glimmerslime`,
   `RUT_LiveIngredient_*`, `AB_PurpleRawFungus`…): flagged on the row where the plant's new
   name makes the item's old name odd, for a follow-on pass.


## Flora

### AB_AgaricusDomeCap

- **agaricus domecap** → **skarrow dome** (alternate: vessk dome)
- group: flora · source: `sarg.alphabiomes`
- width: **7 cells** (currently 2 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `7 wide, rename`

**Description (def text).** A low, swollen dome of a mushroom, wide as a hut and mottled in the colours things use to say do not eat me. Everyone eats it anyway: the flesh under the skin is a potent psychotropic, harvested one careful cut at a time and taken with a great deal of caution, or none.

**Visual brief.** A single broad, low dome seven cells across — height about a third of its width, so the silhouette is a squashed hemisphere sitting almost flat on the mat, the stem hidden. Skin bone-white going lilac at the crown, blotched with sickly yellow-gold warning rings and a wet Sheen gloss on top; thin dark gill-slits visible only around the rim. No stalk, no protrusions: this is the one flat dome in a forest of towers. Scale cue: a colonist is shorter than the dome's edge is thick.

### AB_Agarilux

- **agarilux** → **tolluk cap** (alternate: hesska cap)
- group: flora · source: `sarg.alphabiomes`
- width: **unchanged, 1.5 (the review sheet showed 1 — sheet defect, see header) cells** (no size in his note)
- owner's note, verbatim: `rename`

**Description (def text).** The common tall mushroom of the pale forest: a lilac cap on a thick white stalk, studded with soft knobs that glow faintly when the air is wet. It has adapted to open ground and gives a few edible purple caps when harvested, more if you are patient.

**Visual brief.** A classic upright toadstool silhouette, one and a half cells wide and about as tall: rounded lilac cap, thick milk-white stalk, four or five pale glowing nubs studding the cap like rivets. Palette bone-white stalk, lilac cap, nubs a faint cold glow-blue. This is the baseline everything else is compared against, so keep it plain and clean; it currently reuses vanilla Core's Agarilux art and must not look like that file. Distinct from the glowcap (ithra) by having only a faint nub-glow and no light halo, and from the tall spire (quessa) by being squat.

### AB_AgariluxPrime

- **Agarilux Prime** → **grath elder** (alternate: dreth elder)
- group: flora · source: `sarg.alphabiomes`
- width: **20 cells** (currently 8)
- owner's note, verbatim: `20 wide, rename`

**Description (def text).** An elder of the pale forest, older than any settlement on the planet and wider than most. It breathes a standing cloud of suffocating spores that kills whatever wanders in, fungus or animal, and then reaches out with slow hyphae to eat the dead where they lie. Cut it and you join them, unless you are sealed against its breath to the last seam; a mortar works, from far enough away.

**Visual brief.** Twenty cells across — a hill, not a mushroom. A colossal, sagging, many-lobed cap like a landslide of pale flesh, bone-white on top shading to bruised lilac and wet black in the folds, with a ring of huge slack gills underneath that read as an overhang. Around its base, a skirt of thick creeping hyphae like roots, several holding the pale remains of animals. A visible haze of grey-lilac spore mist hanging at cap height. The Sheen gloss should be heaviest here — it is the biome's oldest surface. Nothing angular; it should look like architecture that grew. Must not resemble the donor's AB_AgariluxPrime.png (a purple cluster) — this is one body, one elder.

### AB_ArbuscularMycorrhiza

- **arbuscular mycorrhiza** → **bollusk trunk** (alternate: karrun trunk)
- group: flora · source: `sarg.alphabiomes`
- width: **9 cells** (currently 3.5 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `9 wide, rename`
- ⚠️ Harvest is vanilla `WoodLog` — fine. The description no longer mentions 'plant' or 'tree' symbiosis: §6 ban 1 (all-fungus). Also: the sheet panel he sized this against was 1.0 cell; the def is 3.5.

**Description (def text).** A fungus that long ago learned to grow a trunk. What it swallowed to learn that is gone; what is left is a pale, ridged column with a mushroom's cap and gills where a crown should be. A fair quantity of usable wood can be cut from the trunk.

**Visual brief.** Nine cells wide: a thick pale trunk, ridged and buttressed like a tree's, rising to a flat plate-cap that spreads far wider than the trunk, with a second, smaller cap tiered above it. Bone-white bark with grey seams, gill-underside lilac, cap tops dusted milk-white. The silhouette is a tree drawn by someone who has only seen mushrooms — tree mass, fungus surfaces. Distinct from the timber mushrooms (brommok, churrun) by its buttressed trunk and tiered plate caps; it must NOT read as an oak.

### AB_Bryolux

- **bryolux** → **hessuk moss** (alternate: warrik moss)
- group: flora · source: `sarg.alphabiomes`
- width: **unchanged, 0.95 cells** (no size in his note)
- owner's note, verbatim: `rename`

**Description (def text).** The glow-carpet of the pale forest: a blue-white mat of tangled sticky fibres, warm to lie on and slow to walk through, because it holds your feet. Where it is bright the ground is feeding; where it goes dark, the ground is cold.

**Visual brief.** A ground-cover tile (four meshes per cell, tiles seamlessly): a dense low tangle of fine fibres, glow-blue at the tips over a milk-white base, with wet gloss highlights and a few darker strands. It must read as MOSS from directly above — texture, not a shape — with no cap, no stalk and no hard edge, feathering to transparent at the tile edge. Palette glow-blue and bone-white; no green at all (this is not the pale-tree moss, lumma, which is white-green and only grows under one tree). Currently vanilla Core's Bryolux art; must not look like it.

### AB_DribblingCap

- **dribbling cap** → **ruvvak weeper** (alternate: dolm weeper)
- group: flora · source: `sarg.alphabiomes`
- width: **12 cells** (currently 5 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `12 wide, rename`
- ⚠️ Sheet panel showed 1.0 cell; the def is 5.0. His '12 wide' may have been calibrated against a picture five times too small.

**Description (def text).** A huge pink-lilac cap that weeps a thick, pungent resin down its stalk without ever stopping. The resin is a neurotoxin strong enough to drop a warg; collected carefully it tips a single dart, and nobody collects it carelessly twice.

**Visual brief.** Twelve cells wide, one of the biggest things standing: an enormous drooping cap, deeper than it is tall, sagging at the rim like wet cloth, over a short fat stalk streaked with long runs of glistening amber-gold resin that pool at the base. Cap milk-pink to lilac, resin lantern-gold and glossy, pools catching glow-blue reflections. The DRIP is the identity: every edge should have a droplet forming. Distinct from the grath elder (no spore haze, no hyphae, a single tidy cap) and from every other cap by the visible resin runs.

### AB_GiantAgarilux

- **giant agarilux** → **vokkun pillar** (alternate: thorrum stalk)
- group: flora · source: `sarg.alphabiomes`
- width: **6 cells** (currently 6 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `wrong size, 6 wide, rename`
- ⚠️ 'wrong size' — the panel he saw was 1.0 cell; the def already draws it at 6.0. Ruled 6 = as it is; art regen still owed.

**Description (def text).** A pale forest giant whose stalk has hardened into something you can build with — a weak wood, but wood, in a biome that has none. The cap glows faintly at its knobs; the stalk is cut for mushroom logs and grows back in a season.

**Visual brief.** Six cells wide and taller than wide: the silhouette is a PILLAR — a thick, straight, fibrous stalk with visible woody grain and bark-like ridges, topped by a comparatively small domed lilac cap with a few glowing nubs. Stalk bone-white shading to grey-lilac in the grain, cap lilac, nubs glow-blue, wet gloss on the cap only. It must read as timber-on-the-hoof; the stalk is the point, the cap is a hat. Distinct from the bollusk trunk (no buttresses, no tiers) and the tarrusk spire (not purple, not tree-shaped).

### AB_GlowingAgarilux

- **glowing agarilux** → **ithra glowcap** (alternate: sennik glowcap)
- group: flora · source: `sarg.alphabiomes`
- width: **4 cells** (currently 2 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `wrong size, 4 wide, rename`
- ⚠️ 'wrong size' — panel showed 1.0; the def is 2.0 (in-game glowRadius 10). Ruled 4.

**Description (def text).** The lamp of the pale forest: a tall lilac mushroom that gives off a wide, cold violet light from every knob on its cap. It grows only wild, and gives a few edible purple caps to anyone willing to harvest in the dark it makes brighter.

**Visual brief.** Four cells wide, tall: an upright toadstool whose whole cap is luminous — the knobs on the cap are bright glow-blue-violet points, and the cap flesh between them is lit from inside, lilac going to milk-white at the edges, with a soft halo painted into the alpha. Stalk pale and slender. This is the only cap where the LIGHT is the silhouette; the tolluk cap is the same shape unlit. Scale: about two colonists tall. Currently shares vanilla Core's Agarilux art with the tolluk cap; the two must look unrelated.

### AB_Glowstool

- **glowstool** → **nubbik stool** (alternate: murrit stool)
- group: flora · source: `sarg.alphabiomes`
- width: **unchanged, 0.7 (the review sheet showed 1 — sheet defect, see header) cells** (no size in his note)
- owner's note, verbatim: `rename`

**Description (def text).** A small brown-grey stool of a mushroom that smells like something died in a wet sack and tastes, cooked, surprisingly good. It grows in open ground here and gives a handful of edible caps.

**Visual brief.** Ankle-high, under one cell: a squat, slightly lopsided toadstool with a flat-topped tan-grey cap and a stubby off-white stalk, no glow, wet gloss on the cap. Plain, humble, edible-looking. Palette is the one warm-brown note in the biome — keep it muted and greyed so it still belongs to the pale forest. Distinct from the tinnik bell (which glows and is bell-shaped) and the rukka cap (which is wrinkled and lilac). Currently vanilla Core's Glowstool art; must not look like it.

### AB_LilacBeacon

- **lilac beacon** → **quessa spire** (alternate: dommik spire)
- group: flora · source: `sarg.alphabiomes`
- width: **3 cells** (currently 2 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `3 wide, rename`

**Description (def text).** A tall, narrow mushroom with a bright lilac cap held high on a pale spire of a stalk. It is far more nourishing than its neighbours and rather harder on the stomach; the caps are harvested a few at a time.

**Visual brief.** Three cells wide but much taller — a SPIRE: a slender tapering stalk two or three times the cap's height, topped by a small, vivid lilac conical cap, like a lit match. Stalk milk-white with faint lilac banding; cap the most saturated lilac in the set; no knobs, no glow halo. The narrowness is the identity: everything else here is squat or wide. Distinct from the ithra glowcap (no light) and tarrusk spire (not woody, not purple-grey).

### AB_RecurvedStropharia

- **recurved stropharia** → **orrusk crook** (alternate: kresh crook)
- group: flora · source: `sarg.alphabiomes`
- width: **5 cells** (currently 5 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `5 wide, rename`
- ⚠️ Sheet panel showed 1.0; the def is 5.0. Ruled 5 = as it is.

**Description (def text).** A big grey mushroom whose cap has curled up and back on itself into a crook, gills outward, like a hand cupped to the black sky. The stalk is hard enough to cut for mushroom logs.

**Visual brief.** Five cells wide: a thick grey-white stalk with woody grain, topped by a cap that curls UPWARD at the rim into a shallow bowl or crook, so the pale lilac gills face the sky and are the most visible surface from above. Rim edges frilled. Palette bone-white and ash-grey with lilac gill-lines, faint glow-blue nubs on the outer rim. The up-curl is the whole identity — every other cap here droops or domes. Distinct from the vokkun pillar (which has a small normal cap).

### AB_SlimyPholiota

- **slimy pholiota** → **glissik slimecap** (alternate: mennok slimecap)
- group: flora · source: `sarg.alphabiomes`
- width: **5 cells** (currently 5 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `5 wide, , rename`
- ⚠️ Sheet panel showed 1.0; the def is 5.0. Ruled 5 = as it is.

**Description (def text).** A blue-pink mushroom that sweats a clear slime insects cannot resist and cannot escape: they stick, they stop, and the fungus eats them where they lie. The same slime makes its flesh unusually rich, and it can be eaten raw.

**Visual brief.** Five cells wide: a broad convex cap in a milk-pink to glow-blue gradient, entirely sheathed in a thick clear slime layer that pools into glossy drips at the rim and around the base, with a few small dark insect shapes stuck in it. Stalk short and fat, slime-coated. The SLIME must read as a separate translucent layer — highlights and a bulging outline beyond the cap. Distinct from the ruvvak weeper (whose resin is amber and runs in streaks, not sheets) and the sikkra lure (tiny, teal, glowing).

### AB_WitchesOyster

- **witches' oyster** → **turrok shelf** (alternate: wessa shelf)
- group: flora · source: `sarg.alphabiomes`
- width: **6 cells** (currently 2 (the review sheet showed 1 — sheet defect, see header))
- owner's note, verbatim: `6 wide, rename`

**Description (def text).** A branching colony of shelf-caps growing one over another from a single foot, sharp-smelling and slow to spoil. The pink caps keep for a long time after harvest — longer than anything else the pale forest gives.

**Visual brief.** Six cells wide: a stepped stack of overlapping shelf-caps, fan-shaped, each one growing out of the one below, with no visible stalk — the silhouette is a rippling staircase of bracket fungi seen from above. Caps milk-pink at the growing edges shading to bone-white and grey at the base, with fine radial ridges; wet gloss along each rim. Distinct from the skarrow dome (one smooth dome) and the pimmik mold (a carpet, not a stack).

### RUT_AgelessCap

- **ageless cap** → **orlath cap** (alternate: jhorra cap)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 1.6 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Harvested item `RUT_LiveIngredient_AgelessCap` keeps its name here; rename it in the follow-on pass.

**Description (def text).** A pale, swollen cap said to give back years to anyone who drinks it brewed right — and it must be brewed here, alive, or not at all. It bears no malice; disturbing its mycelium is simply what makes it vent a choking cloud, and the cloud does not care why you came.

**Visual brief.** About one and a half cells wide: a single fat, smooth, bulging cap, bone-white with a faint pearly lilac sheen, taut like a full bladder, on a short thick stalk, with a subtle ring of dark vents where the cap meets the stalk and a thin grey spore wisp curling from one of them. Clean, valuable, slightly unsettling — it should look like a prize. Currently shares the crimson cap placeholder; must be its own thing, and it is white, not red.

### RUT_Arpeau

- **arpeau** → **churrun mast** (alternate: dravik mast)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **10 cells** (currently 2.5)
- owner's note, verbatim: `10 wide, , rename`

**Description (def text).** A mast of pale fungus standing in the milk ponds, lit from inside with a cold blue-green light. It grows fast and cuts into mushroom logs, though not many; mostly it is the thing you steer by across the shallows.

**Visual brief.** Ten cells wide and very tall: a cluster of three or four thick, straight, tapering trunks rising from one submerged base, with small conical caps at the tips and a cold glow-blue-green light bleeding from vertical seams in the trunks. Base wreathed in milk-white ripples (it stands in not-water). Palette bone-white trunks, glow-blue-green seams, a lilac tint at the cap tips. Distinct from the brommok timber (which is a single broad marsh trunk with no glow) and the bollusk trunk (buttressed, plate-capped).

### RUT_BlastpodShroom

- **blastpod shroom** → **kabbrik pod** (alternate: fennik pod)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.9 cells** (no size in his note)
- owner's note, verbatim: `keep general appearance, just improve, rename`
- ⚠️ Harvested item `RUT_BlastSpore` keeps its name.

**Description (def text).** A wild fungus whose swollen pods are packed with an oily spore-mass volatile enough to refine into chemfuel. It grows where it pleases and nowhere anyone plants it; it cannot be cultivated, or at least nobody has managed to.

**Visual brief.** Keep the existing BoomshroomGrown silhouette and composition and only improve it — the owner's words: 'keep general appearance, just improve'. Under one cell: a low cluster of taut, rounded pods on short stems, each pod with a faint warm lantern-gold glow at the seam as if lit from within, skins bone-white to grey with a wet gloss. Tighten the drawing, deepen the shadows, and add the Sheen gloss; do not change the number or arrangement of pods. Reference file: `src/RimUtinni/RotSporeKit/Textures/RotSporeKit/Things/Plant/Boomshroom/BoomshroomGrown/BoomshroomGrown_A.png` (a restyle, so this one job MAY carry a reference).

### RUT_BleedingTooth

- **bleeding tooth** → **rhukk tooth** (alternate: morrid tooth)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **2 cells** (currently 1)
- owner's note, verbatim: `2 wlde, , rename`
- ⚠️ '2 wlde' read as '2 wide'.

**Description (def text).** A large, blunt, tooth-white mushroom that beads and drips a red fluid thick as blood from every pore of its cap. It is harmless and it is not bleeding; nobody who sees one for the first time believes either.

**Visual brief.** Two cells wide: a squat, blunt, molar-shaped cap, bone-white and slightly translucent, with dozens of dark-red droplets beading on top and several long red runs down the sides pooling into a dark stain at the base. The red is the ONLY warm-red in the whole flora set — keep it deep and glossy, not orange. No glow. Distinct from the rhessa cap (which is red all over, smooth, no drips).

### RUT_Brightbell

- **shinebell** → **tinnik bell** (alternate: yammik bell)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **1.5 cells** (currently 0.7)
- owner's note, verbatim: `1.5 wide, rename`
- ⚠️ Label was 'shinebell' on a defName of Brightbell; both go.

**Description (def text).** A small, pretty bell of a mushroom that glows a soft lantern-gold in the dark and gives a bite or two of edible fungus. Colonists plant them along paths for the light, and children pick them for no reason at all.

**Visual brief.** One and a half cells wide: a cluster of two or three drooping bell-shaped caps on slender curved stalks, like a lily of the valley made of fungus, each bell lit lantern-gold from inside with a soft painted halo. Stalks milk-white, bells gold-to-cream. The warm gold is the identity — it is the one warm light in a glow-blue biome. Distinct from the nubbik stool (unlit, flat) and the sikkra lure (teal, sticky).

### RUT_CrimsonCap

- **crimson cap** → **rhessa cap** (alternate: vanni cap)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **2 cells** (currently 1)
- owner's note, verbatim: `2 cells, rename`

**Description (def text).** A broad crimson cap on a white stalk, the one saturated colour in a pale forest. It is good for nothing but looking at, and it is very good at that.

**Visual brief.** Two cells wide: a smooth, perfectly domed cap in a deep crimson going to wine-lilac at the edges, glossy with Sheen, on a clean milk-white stalk with a small skirt. No drips, no knobs, no glow — pure decorative shape. Tiles four to a cell, so keep the silhouette simple and centred. Distinct from the rhukk tooth (white with red drips). Currently the placeholder texture for the orlath cap and thurrom hearth as well; after this pass all three must differ.

### RUT_Dewshrooms

- **dewshrooms** → **sikkra lure** (alternate: nibbik lure)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.5 cells** (no size in his note)
- owner's note, verbatim: `, rename`

**Description (def text).** Tiny caps that light up a cold teal in the dark to draw small prey, which lands, sticks to the gills and is slowly digested. Whole swarms of gnats die to a single patch; the light is the trap.

**Visual brief.** Under half a cell, nine meshes per cell: a scatter of very small, thin-stalked caps with translucent glow-teal heads and sticky bead-droplets under the rims, a few tiny dark specks stuck to them. Teal-green glow with a soft halo is the identity (glowColor 15,104,106). Distinct from the tinnik bell (gold, bell-shaped, bigger) and the pimmik mold (no glow).

### RUT_DulcisPlant

- **dulcis** → **tamma sweetcap** (alternate: yubbra sweetcap)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **3 cells** (currently 1.3)
- owner's note, verbatim: `3 cells, rename`
- ⚠️ Harvested item `RUT_RawDulcis` and fungiponics/cantina references keep 'dulcis' until the follow-on item; the same-day dulcis* renders are at 1.3 cells and are superseded by the 3-cell ruling.

**Description (def text).** An oddly sweet mushroom grown in place of berries by everyone who lives under a roof of rock or spores. It tolerates cold, heat and filth, and its caps are eaten raw, dried, or stewed into the one dish every cantina on the night shoulder serves.

**Visual brief.** Three cells wide: a generous, plump cluster of rounded caps in a warm milk-white shading to a faint peach-lilac blush at the crown, on short stubby stalks, looking edible and ripe — the cantina fruit of the biome. Slight translucency at the cap edges, wet gloss. Grown/immature/harvested stages already exist as a same-day regen set (dulcisgrown_a_v1 etc.); rebrief those three at 3 cells with the same composition. Distinct from the pursk hood (violet) and nubbik stool (brown).

### RUT_EuphoricCrown

- **euphoric crown** → **lussa crown** (alternate: ephra crown)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 1.5 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Harvested item `RUT_LiveIngredient_EuphoricCrown` keeps its name here.

**Description (def text).** A broad, faintly luminous crown of a cap that brews into the pale forest's own pleasure tea — brewed here, alive, the day it is cut, or not at all. It keeps no defence of its own; ringed the way it is, it has never needed one.

**Visual brief.** One and a half cells wide: a wide, shallow, slightly upturned cap with a scalloped rim, so from above it reads as a crown; flesh milk-white lit with a soft lilac inner glow strongest at the centre, gills a deeper lilac, short pale stalk. Serene and inviting — it is meant to be reached for. Currently the violet wimple placeholder; must be its own art and paler than the pursk hood. The pekk fruit ring around it is separate art.

### RUT_FalseFruit

- **false fruit** → **pekk fruit** (alternate: nibbra fruit)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.6 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Alarm comp radius 18; harvest is 1 raw fungus.

**Description (def text).** Grown at the edge of a lussa crown's root mat and shaped to match it: a small pale fruiting body that looks exactly like the good stuff. It is not — touch one and the whole grove knows you are there, and what lives in the grove comes to see.

**Visual brief.** Just over half a cell: a small, tempting, rounded pale cap with the same milk-white-and-lilac colouring as the lussa crown, deliberately similar at a glance but with a subtly wrong detail up close — the gills run in a spiral rather than radially, and the stalk is threaded with fine dark root-hairs into the mat. No glow. Currently the mold-fruiting-bodies placeholder; must become a single small cap, not a carpet.

### RUT_FlakespireFungus

- **flakespire fungus** → **tarrusk spire** (alternate: hemmok spire)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **3 cells** (currently 2)
- owner's note, verbatim: `3 wide, , rename`

**Description (def text).** A slow-growing mushroom tree with a purple-grey spire of a cap and a stalk as hard as good timber. It takes half a year to reach cutting size and is worth the wait: strong, straight, and handsome enough to build a hall from.

**Visual brief.** Three cells wide, tall: a straight woody stalk with flaking, layered bark in grey-lilac (the flakes are the identity — shingled scales peeling upward), rising to a tall, narrow conical cap in dusty purple with a pale tip. No glow, no drips. It should read as a conifer made of fungus. Distinct from the quessa spire (thin, vivid lilac, no bark) and vokkun pillar (white, big straight stalk, small cap).

### RUT_FruitingBodies

- **mold fruiting bodies** → **pimmik mold** (alternate: fudduk mold)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.5 cells** (no size in his note)
- owner's note, verbatim: `, rename`

**Description (def text).** The fruiting bodies of a pale mold that carpets the forest floor wherever the mat is warm: a fuzz of tiny pins, each with a bead of a head. It is the most common thing in the biome and the least noticed.

**Visual brief.** Half a cell, twenty-five meshes per cell — a carpet texture, not a shape: a dense fuzz of pin-thin stalks with tiny round heads, bone-white to grey with faint lilac bead-tips, a few dark patches where it grows on something. Must tile without a visible edge and read as fine texture from the game's zoom. No glow, no gloss (it is dry-looking, the one matte thing in the biome). Currently also the pekk fruit placeholder; after this pass the two must differ completely.

### RUT_FurnaceCap

- **furnace cap** → **thurrom hearth** (alternate: brakka hearth)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **2 cells** (currently 1)
- owner's note, verbatim: `2 cells, rename`
- ⚠️ Harvested item `RUT_LivingFurnaceCap` keeps its name here.

**Description (def text).** A squat, thick-walled mushroom that runs its metabolism so hot it steams in the cold air of the forest. Cut one open and the flesh is body-warm right through; harvested whole and kept alive, its caps will heat a room for a couple of weeks before the tissue finally gives out.

**Visual brief.** Two cells wide: a low, thick, rounded cap with heavy walls, cracked on top like a loaf, with a warm lantern-gold to ember-orange glow showing through the cracks and a painted wisp of steam/breath-fog rising from it — the biome visibly exhaling. Skin bone-white going to warm grey around the cracks; gloss where the steam condenses. This is the one thing in the flora that reads WARM. Currently the crimson cap placeholder; must be its own art and not red.

### RUT_GreyLady

- **Grey Lady** → **sylla lace** (alternate: mirrin lace)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 1 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Currently also the regenerant veil placeholder.

**Description (def text).** A grey fungus that grows a fine cloth-like lace from beneath its cap, hanging to the ground in a veil. The lace is cut and woven as cloth; it is the pale forest's only fabric, and it is better than it has any right to be.

**Visual brief.** One cell: a tall grey-white cap with a long, hanging skirt of fine net-like lace draped from the cap rim to the ground, translucent with a visible mesh pattern, the stalk seen dimly through it. Palette ash-grey and bone-white with a faint lilac cast, no glow. The hanging lace is the identity. Distinct from the mirrash veil (which is a flat translucent sheet on the ground, not a skirt) and from the Lantern Deeps' prenna lace (blue-lit).

### RUT_MortalMorelPlant

- **mortal morel** → **vennik salve** (alternate: irrik salve)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **0.8 cells** (currently 1)
- owner's note, verbatim: `0.8, rename`
- ⚠️ Harvested item `RUT_MedicineFungal` keeps its name. 'morel' is a real-world mushroom name and goes.

**Description (def text).** A slow, delicate, honeycombed mushroom whose flesh is worked into fungal medicine. Sowing and harvesting it are both slow, careful work because the whole thing crumbles at a touch, and a crumbled one is worth nothing.

**Visual brief.** Under one cell (0.8): a single upright, elongated cap pitted all over with a honeycomb of deep pores, pale grey-white with lilac shadows in the pits, on a short milk-white stalk. Fragile-looking — thin edges, a crumb or two fallen at the base. No glow. Tiles four to a cell. Distinct from the tavvik crust (flat, leafy) and rukka cap (wrinkled, not pitted).

### RUT_Nogtyl

- **nogtyl** → **brommok timber** (alternate: gorrusk timber)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **12 cells** (currently 2.5)
- owner's note, verbatim: `12 wide, rename`

**Description (def text).** A massive marsh mushroom with a trunk as hard as wood, rooted in the milk ponds and growing fast enough to see. It cuts into ordinary wood, though not much of it for its size; it will only grow on soft, wet ground.

**Visual brief.** Twelve cells wide, very tall: ONE enormous straight trunk, pale and fibrous with shallow vertical grooves, flaring at the base into wide root-flanges that sink into milk-white shallows, topped with a small flat cap disproportionately tiny for the trunk. Bone-white going ash-grey in the grooves, cap lilac-grey, no glow. This is the biggest pure-timber silhouette in the biome; the vokkun pillar is the same idea at half the size with a rounder cap, and the churrun mast is a glowing cluster.

### RUT_Nuitae

- **nuitae** → **nissik gill** (alternate: harru gill)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **1 cells** (currently 0.6)
- owner's note, verbatim: `1 wide, rename`

**Description (def text).** A near-black cap whose gills glow brightly beneath it, so that it lights the milk it stands in and nothing above. It grows in the shallows or in ground wet enough to pass for them.

**Visual brief.** One cell: a dark, almost black cap (the darkest thing in the flora set), slightly tilted so a slice of the glow-blue underside shows, with the light spilling downward into a painted milk-white ripple at the base. Stalk short, dark grey. The contrast of black cap over blue-lit water is the identity. Distinct from the Lantern Deeps' nurrik gill only by biome context — make the water milk-white, not blue, and the cap matte.

### RUT_PaleMoss

- **pale moss** → **lumma moss** (alternate: ennik moss)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.45 cells** (no size in his note)
- owner's note, verbatim: `make look really like moss, rename`

**Description (def text).** A faintly glowing moss that only takes root beneath a quellan tree, fed by whatever the tree is doing underground. It gives off a soft, cold, white-green light of its own — the pale forest's usual answer to a lamp.

**Visual brief.** Owner's direction: 'make look really like moss'. Under half a cell, nine meshes per cell: a low, dense, cushiony moss texture with visible tiny fronds and a velvety surface, pale white-green (glowColor 200,230,205) with a very soft glow at the tips, no caps, no stalks, no mushroom shapes at all. Must read unmistakably as MOSS from above and tile seamlessly. Distinct from the hessuk moss (blue, stringy, sticky). Currently vanilla Grass_Anima; must not look like grass.

### RUT_PaleTree

- **pale tree** → **quellan tree** (alternate: ollun tree)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **6 cells** (currently 2.5)
- owner's note, verbatim: `6 wide, rename`
- ⚠️ LEAST SURE: the frozen sheet's §7 calls this 'the pale tree' by name. His note says rename; if he meant only the art, keep 'pale tree' and strike the row. Also the ruled 6 cells is 2.4× the current 2.5.

**Description (def text).** A bone-white tower of fungus grown in the shape of a tree, humming faintly at dusk, sacred to a wandering creed of the wild. Meditate long enough in its shade and you leave with a faint, tugging sense of the Force — and the unshakable feeling that you should find someone who actually knows what this is.

**Visual brief.** Six cells wide: a tree-shaped fungus — a smooth bone-white trunk splitting into a few thick pale limbs, each ending not in leaves but in a cluster of small milk-white caps, so the crown is a canopy of caps; a soft grey-white glow at the crown (glowColor 110,116,125) and lumma moss painted faintly at the base. Nothing angular, a hum you can almost see. Must not resemble vanilla TreeAnima (its current art) and must not have leaves — §6 ban 1. The most sacred silhouette in the biome; give it grace.

### RUT_Pusmelon

- **pusmelon** → **gubbra gourd** (alternate: blorrit gourd)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **1 cells** (currently 0.7)
- owner's note, verbatim: `1 wide, rename`

**Description (def text).** A gourd-like fungus, grey-green and bloated, that grows sacs of a foul-smelling liquid under its skin. Step on one and you will smell it for a day; nothing eats it, and nothing has to.

**Visual brief.** One cell, four meshes per cell: a squat, lumpy gourd shape, sagging with fluid, in a sickly grey-green (the only green in the set — keep it greyed and bruised, not leafy) with a few taut pale blisters on the surface and a wet gloss. A short stub of a stalk. No glow. Distinct from the kabbrik pod (a cluster of small glowing pods) and the tamma sweetcap (appetising).

### RUT_RegenerantVeil

- **regenerant veil** → **mirrash veil** (alternate: hallun veil)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 1.3 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Alarm comp radius 18. Harvested item `RUT_LiveIngredient_RegenerantVeil` keeps its name here.

**Description (def text).** A translucent, slow-pulsing veil of fungal tissue laid over the ground, threaded straight into the grove's own mycelial network, from which the pale forest's healing tea is brewed alive. Wound it and the whole network answers.

**Visual brief.** One and a third cells: a flat, translucent sheet of pale tissue draped over the ground and a low hummock, milk-white with faint lilac veins pulsing through it and a soft inner glow along the veins, the edges lifting slightly. No cap, no stalk — it is a veil, not a mushroom. Currently the grey lady placeholder; must be its own art, flat and sheet-like where the sylla lace is a hanging skirt.

### RUT_RustPuff

- **rustpuff** → **unchanged** (his note carries no rename)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.6 cells** (no size in his note)
- owner's note, verbatim: ``
- ⚠️ Regen without a note — read as 'repaint, keep name and size'. Confirm in the morning.

**Description (def text).** A large puffball mushroom that bursts at a touch into a cloud of flaky, rust-coloured spores. The spores stain everything and harm nothing; the forest floor is red-brown wherever a herd has walked through a patch.

**Visual brief.** Regen with NO rename and NO size change (his note is empty): under one cell, four meshes per cell, a plump round puffball, bone-white with a rust-brown dusting on top and a split at the crown leaking a puff of rust-coloured spores. The rust-orange is a deliberate warm accent against the pale palette. No glow. Keep the existing composition; improve the drawing and add the Sheen gloss.

### RUT_Sagecrust

- **sagecrust** → **tavvik crust** (alternate: rhomm crust)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.5 cells** (no size in his note)
- owner's note, verbatim: `, rename`

**Description (def text).** A tough, leafy crust-fungus that clings to rock and mat alike and survives on almost no light. Nothing much eats it and nothing much kills it; it is the last thing to go when the ground turns cold.

**Visual brief.** Half a cell, nine meshes per cell: a flat, leafy, lobed crust hugging the ground, grey-white with a dusty sage-grey cast and darker seams between the lobes, edges curling up slightly, dry-looking and matte. No glow, no gloss — with the pimmik mold, one of only two matte things here. Distinct from the lumma moss (soft, glowing) and hessuk moss (stringy, blue).

### RUT_Shinecap

- **shine cap** → **dremmik cap** (alternate: ulloth cap)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **4 cells** (currently 2.5)
- owner's note, verbatim: `4 wide, rename`
- ⚠️ Harvested item `RUT_Glimmerslime` keeps its name here.

**Description (def text).** A large slow-growing mushroom that lives in symbiosis with a surprisingly tasty slime mold, which spreads in glimmering sheets across its cap and is scraped off and eaten. The mushroom takes a full season to mature; the slime comes back in days.

**Visual brief.** Four cells wide: a broad, heavy, umbrella cap with a wide flat top, bone-white, entirely veined and pooled with a bright glimmering slime — lantern-gold and glow-blue iridescence in shifting patches, like oil on milk. Thick pale stalk. The iridescent slime sheet ON TOP of the cap is the identity; the glissik slimecap's slime is clear and hangs off the rim. No painted light halo (it glimmers, it does not glow).

### RUT_Skulltop

- **skulltop** → **vekkra choker** (alternate: morrgul choker)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **unchanged, 0.7 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Gas producer radius 5, `AB_MycoticSpores`.

**Description (def text).** A small, deadly mushroom that steadily breathes polluting toxic spores into the air around it. Anything not immune to poison that stands near one long enough chokes; it is the little cousin of the grath elder and it guards nothing but itself.

**Visual brief.** Under one cell: a squat, domed cap in a dead bone-white with dark hollow pits arranged so that from above it faintly suggests a skull without being one, on a thick short stalk, and a painted grey-lilac spore haze drifting from the pits. No glow, wet gloss. Distinct from the orlath cap (smooth, taut, valuable-looking) — this one should look like a warning.

### RUT_VioletWimple

- **violet wimple** → **pursk hood** (alternate: dommet hood)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **2 cells** (currently 0.7)
- owner's note, verbatim: `2 cells, rename`

**Description (def text).** A big violet-capped mushroom whose cap folds down around the stalk like a hood. It is not very productive, but the hood is edible and it is everywhere, and that is enough.

**Visual brief.** Two cells wide, four meshes per cell: a deep violet cap folded down and inward around a pale stalk so the silhouette is a hood or cowl, with a pale rim showing the gill-line, glossy. The most saturated VIOLET in the set (the lussa crown is pale and lit; the tolluk cap is lilac and open). No glow. Currently also the euphoric crown placeholder; after this pass the two must differ.

### RUT_Wrinklecap

- **wrinklecap** → **rukka cap** (alternate: thessik cap)
- group: flora · source: `mandrake.rut.rotsporekit`
- width: **0.9 cells** (currently 0.85)
- owner's note, verbatim: `.9 wide, rename`

**Description (def text).** A damp-ground mushroom with a cap wrinkled like a walnut, glowing a soft lilac from the folds. It is the grazers' staple; anything that eats fungus eats this first.

**Visual brief.** Just under one cell (0.9), four meshes per cell: a rounded cap creased with deep wrinkles and folds, milk-white ridges over lilac-glowing valleys (glowColor 126,108,155) with a soft halo, short pale stalk. Soft and edible-looking. Distinct from the vennik salve (pitted, not wrinkled, no glow) and nubbik stool (flat, brown).


## Fauna

### AA_Agaripawn

- **agaripawn** → **rennok** (alternate: tuskle)
- group: fauna · source: `sarg.alphaanimals`
- width: **7 cells** (currently 2)
- owner's note, verbatim: `7 wide, rename`
- ⚠️ Ruled 7 cells against a bodySize of 1.4 (a colonist is ~1.5 cells tall) — a 7-cell draw on a 1.4 body will look huge and hit like a boar. He may have meant the body, not the sprite; flagged, drawSize applied as ruled.

**Description (def text).** A shambling, waist-high hybrid of animal and fungus, its back and flanks grown over with living caps that feed it and hide it. It is slow, flammable, and never quite alone: hurt one and the others in the grove feel it and come. It breeds by throwing spores, so its young owe it nothing. Hunted or kept, it gives a little edible cap-flesh that keeps longer than most fungus.

**Visual brief.** Top-down pawn sprite, three facings, adult drawn seven cells wide: a low, broad, four-legged shambler whose entire dorsal surface is a garden of small lilac caps and milk-white knobs over a wet grey-white hide, a blunt eyeless head lost in the growth, thick stubby legs. Palette bone-white, lilac, wet black at the seams, a faint glow-blue at a few cap-tips, Sheen gloss on the hide. Must be clearly the smaller kin of the gromma (same cap-garden idea, half the mass, longer legs) and unlike the durrok (which carries no caps, only moss and rot).

### AA_Agaripod

- **agaripod** → **gromma** (alternate: bollogar)
- group: fauna · source: `sarg.alphaanimals`
- width: **unchanged, 3.8 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Keep + rename only; no art job. Alt 'bollogar' is a fallback if 'gromma' collides with something he knows.

**Description (def text).** A great slow mound of animal and fungus, grown over with living caps that feed it and hide it, so heavy with growth that bullets sink into it and do little. Fire is another matter. It breeds by throwing spores and feels the wounds of its kin across the grove; hunted or kept, it gives a good yield of edible cap-flesh.

**Visual brief.** KEEP — art not regenerated (his decision was keep; only the name changes). Current art: AgaripodArtOverride in the game Mods folder.

### AA_MycoidColossus

- **mycoid colossus** → **vorrugath** (alternate: drovvanth)
- group: fauna · source: `sarg.alphaanimals`
- width: **15 cells** (currently 6)
- owner's note, verbatim: `15 wide, , rename`
- ⚠️ Ruled 15 cells on a bodySize of 6 — the biggest sprite in the campaign. Applied as ruled.

**Description (def text).** A walking piece of the pale forest: a cold-blooded six-legged colossus with two spines and six eyes, its back a grove of full-grown caps that trap insects and feed it in turn. It breeds by sporulation and cares for nothing it spawns. It is rarely seen and never mistaken for anything else; when the grove is wounded and something this size answers, the wise are already leaving. Tamed, it can be trimmed for cap-flesh.

**Visual brief.** Top-down pawn sprite, three facings, adult drawn fifteen cells wide: a vast, low, six-legged body like a hill on legs, two ridged spines running the length of the back and diverging, six small pale eyes in a broad flat head, and the entire back carrying a full grove — several big lilac-and-white caps the size of the tolluk cap, glowing nubs, hanging hyphae, a spore haze. Hide wet black-grey with bone-white plates, Sheen gloss everywhere, the caps the same palette as the flora so it reads as forest that stood up. Nothing angular. Must not resemble the donor MycoidColossusArtOverride art.

### AA_Swarmling

- **swarmling** → **chittik** (alternate: skreelet)
- group: fauna · source: `sarg.alphaanimals`
- width: **0.5 cells** (currently 1.75)
- owner's note, verbatim: `0.5 wide, rename`
- ⚠️ Current adult drawSize 1.75 on a bodySize of 0.3 — the ruling shrinks the sprite to a size that finally matches the body.

**Description (def text).** A finger-long vermin, half insect and half spore-case, that is never seen alone. One is nothing; a swarm is a single body with a hundred mouths that shares every wound it takes. They lay their larvae in whatever they bite, and the larvae hatch when it dies.

**Visual brief.** Top-down pawn sprite, three facings, adult drawn half a cell wide (tiny — a colonist is three of these long): a small many-legged crawler with a pale segmented body, a bulbous spore-sac abdomen in milk-white with a faint lilac glow, dark wet-black head and legs, mandibles. The sac is the identity: it should look like a puffball that grew legs. Read cleanly at 0.5 cells — strong silhouette, few details. Distinct from the grellik (which is a fat weevil with a cap on its back).

### AA_Wildpawn

- **wildpawn** → **durrok** (alternate: bommet)
- group: fauna · source: `sarg.alphaanimals`
- width: **6 cells** (currently 2)
- owner's note, verbatim: `6 wide, , rename`
- ⚠️ Ruled 6 cells on a bodySize of 1.4 — same mismatch as the rennok; applied as ruled, flagged.

**Description (def text).** A small shambling mound of what looks like rotting matter, half animal and half fungus, that grew smaller and quicker than its swamp-bound kin for want of water. It burns easily, bleeds slowly, and heals fastest of anything here — but only in company. It breeds by throwing spores and gives a little edible fungus when hunted.

**Visual brief.** Top-down pawn sprite, three facings, adult drawn six cells wide: a lumpy, rounded, four-legged mound of matted pale fibre and moss-like growth in bone-white and ash-grey with lilac shadows, a slack eyeless front, short legs, trailing strands. No caps at all — that is the rennok's mark; this one is all mat and moss. Wet gloss. The mullgoth is the same body twice the mass and sagging.

### AA_Wildpod

- **wildpod** → **mullgoth** (alternate: sloggoth)
- group: fauna · source: `sarg.alphaanimals`
- width: **5 cells** (currently 3.8)
- owner's note, verbatim: `5 wide, rename`

**Description (def text).** A lumbering mass of what looks like decomposing matter, animal and fungus grown into one slow body. Bullets sink into it and do little; fire does a great deal. It breeds by throwing spores, its kin heal faster near it, and hunted or kept it gives a good yield of edible fungus.

**Visual brief.** Top-down pawn sprite, three facings, adult drawn five cells wide: a huge sagging mound of matted pale fibre, moss-like growth and wet dark rot, four thick legs almost hidden under the overhang, a slack front with no eyes, strands and drips trailing from the underside. Bone-white and ash-grey with lilac and wet-black, heavy Sheen gloss. No caps (that is the gromma). The durrok is this at a third the mass. Must not resemble the donor WildpodArtOverride art.

### RSW_FungalMantis

- **fungal mimic mantis** → **skerrith** (alternate: threxil)
- group: fauna · source: `mandrake.rsw.swbestiary`
- width: **unchanged, 3 cells** (no size in his note)
- owner's note, verbatim: `, rename`
- ⚠️ Keep + rename only; no art job.

**Description (def text).** A mantis larger than a person whose carapace grows its own fungus, so that standing still among the caps it is one of them. It hunts from that stillness, and its strike injects a numbing poison that drops the prey before it knows it was struck. When the grove's lure is touched, this is what comes.

**Visual brief.** KEEP — art not regenerated (his decision was keep; only the name changes). Current art: `src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FungalMantis/FungalMantis_south.png`.

### RSW_FungalWeevil

- **fungal weevil** → **grellik** (alternate: mukkrit)
- group: fauna · source: `mandrake.rsw.swbestiary`
- width: **4 cells** (currently 1.8)
- owner's note, verbatim: `disgusting fungus bug hybrid, rename, 4 cells wide`

**Description (def text).** A fat, slow weevil whose infestation became a partnership: the fungus lives in its shell and out of it, the beetle carries the spores wherever it crawls, and the growth hides it among the caps. It is harmless, revolting, and everywhere; its broods come back if you leave survivors.

**Visual brief.** Owner's direction: 'disgusting fungus bug hybrid'. Top-down pawn sprite, three facings, adult drawn four cells wide: a bloated, glossy, dark-shelled weevil with a long snout, whose carapace has split open under a mass of fungal growth — pale caps, milk-white gill-frills and lilac knobs erupting from the seams of the shell, strands of hyphae trailing from the leg joints, a wet black-and-bone palette with a sickly gloss. It should make a viewer wince: the bug is visibly being grown through. Distinct from the chittik (tiny, clean, spore-sac) and skerrith (long, elegant, camouflaged).


## Rulings table — one line each, his to strike

| # | defName | group | current label | new name | alternate | ruled width (cells) | current width (cells) |
|---|---|---|---|---|---|---|---|
| 1 | `AB_AgaricusDomeCap` | flora | agaricus domecap | **skarrow dome** | vessk dome | 7 | 2 (sheet showed 1) |
| 2 | `AB_Agarilux` | flora | agarilux | **tolluk cap** | hesska cap | — | 1.5 (sheet showed 1) |
| 3 | `AB_AgariluxPrime` | flora | Agarilux Prime | **grath elder** | dreth elder | 20 | 8 |
| 4 | `AB_ArbuscularMycorrhiza` | flora | arbuscular mycorrhiza | **bollusk trunk** | karrun trunk | 9 | 3.5 (sheet showed 1) |
| 5 | `AB_Bryolux` | flora | bryolux | **hessuk moss** | warrik moss | — | 0.95 |
| 6 | `AB_DribblingCap` | flora | dribbling cap | **ruvvak weeper** | dolm weeper | 12 | 5 (sheet showed 1) |
| 7 | `AB_GiantAgarilux` | flora | giant agarilux | **vokkun pillar** | thorrum stalk | 6 | 6 (sheet showed 1) |
| 8 | `AB_GlowingAgarilux` | flora | glowing agarilux | **ithra glowcap** | sennik glowcap | 4 | 2 (sheet showed 1) |
| 9 | `AB_Glowstool` | flora | glowstool | **nubbik stool** | murrit stool | — | 0.7 (sheet showed 1) |
| 10 | `AB_LilacBeacon` | flora | lilac beacon | **quessa spire** | dommik spire | 3 | 2 (sheet showed 1) |
| 11 | `AB_RecurvedStropharia` | flora | recurved stropharia | **orrusk crook** | kresh crook | 5 | 5 (sheet showed 1) |
| 12 | `AB_SlimyPholiota` | flora | slimy pholiota | **glissik slimecap** | mennok slimecap | 5 | 5 (sheet showed 1) |
| 13 | `AB_WitchesOyster` | flora | witches' oyster | **turrok shelf** | wessa shelf | 6 | 2 (sheet showed 1) |
| 14 | `RUT_AgelessCap` | flora | ageless cap | **orlath cap** | jhorra cap | — | 1.6 |
| 15 | `RUT_Arpeau` | flora | arpeau | **churrun mast** | dravik mast | 10 | 2.5 |
| 16 | `RUT_BlastpodShroom` | flora | blastpod shroom | **kabbrik pod** | fennik pod | — | 0.9 |
| 17 | `RUT_BleedingTooth` | flora | bleeding tooth | **rhukk tooth** | morrid tooth | 2 | 1 |
| 18 | `RUT_Brightbell` | flora | shinebell | **tinnik bell** | yammik bell | 1.5 | 0.7 |
| 19 | `RUT_CrimsonCap` | flora | crimson cap | **rhessa cap** | vanni cap | 2 | 1 |
| 20 | `RUT_Dewshrooms` | flora | dewshrooms | **sikkra lure** | nibbik lure | — | 0.5 |
| 21 | `RUT_DulcisPlant` | flora | dulcis | **tamma sweetcap** | yubbra sweetcap | 3 | 1.3 |
| 22 | `RUT_EuphoricCrown` | flora | euphoric crown | **lussa crown** | ephra crown | — | 1.5 |
| 23 | `RUT_FalseFruit` | flora | false fruit | **pekk fruit** | nibbra fruit | — | 0.6 |
| 24 | `RUT_FlakespireFungus` | flora | flakespire fungus | **tarrusk spire** | hemmok spire | 3 | 2 |
| 25 | `RUT_FruitingBodies` | flora | mold fruiting bodies | **pimmik mold** | fudduk mold | — | 0.5 |
| 26 | `RUT_FurnaceCap` | flora | furnace cap | **thurrom hearth** | brakka hearth | 2 | 1 |
| 27 | `RUT_GreyLady` | flora | Grey Lady | **sylla lace** | mirrin lace | — | 1 |
| 28 | `RUT_MortalMorelPlant` | flora | mortal morel | **vennik salve** | irrik salve | 0.8 | 1 |
| 29 | `RUT_Nogtyl` | flora | nogtyl | **brommok timber** | gorrusk timber | 12 | 2.5 |
| 30 | `RUT_Nuitae` | flora | nuitae | **nissik gill** | harru gill | 1 | 0.6 |
| 31 | `RUT_PaleMoss` | flora | pale moss | **lumma moss** | ennik moss | — | 0.45 |
| 32 | `RUT_PaleTree` | flora | pale tree | **quellan tree** | ollun tree | 6 | 2.5 |
| 33 | `RUT_Pusmelon` | flora | pusmelon | **gubbra gourd** | blorrit gourd | 1 | 0.7 |
| 34 | `RUT_RegenerantVeil` | flora | regenerant veil | **mirrash veil** | hallun veil | — | 1.3 |
| 35 | `RUT_RustPuff` | flora | rustpuff | **rustpuff** | — | — | 0.6 |
| 36 | `RUT_Sagecrust` | flora | sagecrust | **tavvik crust** | rhomm crust | — | 0.5 |
| 37 | `RUT_Shinecap` | flora | shine cap | **dremmik cap** | ulloth cap | 4 | 2.5 |
| 38 | `RUT_Skulltop` | flora | skulltop | **vekkra choker** | morrgul choker | — | 0.7 |
| 39 | `RUT_VioletWimple` | flora | violet wimple | **pursk hood** | dommet hood | 2 | 0.7 |
| 40 | `RUT_Wrinklecap` | flora | wrinklecap | **rukka cap** | thessik cap | 0.9 | 0.85 |
| 41 | `AA_Agaripawn` | fauna | agaripawn | **rennok** | tuskle | 7 | 2 |
| 42 | `AA_Agaripod` | fauna (keep + rename) | agaripod | **gromma** | bollogar | — | 3.8 |
| 43 | `AA_MycoidColossus` | fauna | mycoid colossus | **vorrugath** | drovvanth | 15 | 6 |
| 44 | `AA_Swarmling` | fauna | swarmling | **chittik** | skreelet | 0.5 | 1.75 |
| 45 | `AA_Wildpawn` | fauna | wildpawn | **durrok** | bommet | 6 | 2 |
| 46 | `AA_Wildpod` | fauna | wildpod | **mullgoth** | sloggoth | 5 | 3.8 |
| 47 | `RSW_FungalMantis` | fauna (keep + rename) | fungal mimic mantis | **skerrith** | threxil | — | 3 |
| 48 | `RSW_FungalWeevil` | fauna | fungal weevil | **grellik** | mukkrit | 4 | 1.8 |


## Collisions checked

- **No two new names alike, no two stems alike** — checked by script over all 48 new labels
  and their alternates (first five letters of every stem compared pairwise; the only
  intentional repeats are the English job words).
- **None equals an existing `<label>` anywhere in `src/`** — MEASURED 2026-09-19 against the
  5,209 distinct lowercase labels in `src/**/*.xml` (`grep -rhoE '<label>[^<]+</label>'`),
  zero hits for any new label or alternate (the one match is `rustpuff` against itself — it keeps its name).
- **None shares a stem with the Lantern Deeps set** (`lantern_deeps_flora_names.md`,
  proposed and alternates) — checked by eye and by the same script.
- Not checked, by instruction: canon. If a stem below happens to be a real Star Wars word I
  did not remember, that is a defect to swap for its alternate, not a source.

