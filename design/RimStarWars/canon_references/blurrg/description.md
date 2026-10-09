# Blurrg

**defName**: `RSW_Blurrg` (self-contained port in this repo's own `src/RimStarWars/SWBestiary`,
`Defs/ThingDefs_Races/RSW_Blurrg.xml`; TAMED-ONLY, in no biome roster)

## Sourced text (Wookieepedia)
Blurrgs are a non-sentient, two-legged reptilian species used as beasts of burden and
mounts on many worlds. Origins given: Miv'rah, Ryloth, Arvala-7 and Endor (subspecies
Arvalan, Rylothian and Forest blurrg). Habitat: semi-arid temperate zones, deserts,
forests and mountains.

Body: **two short arms, each with two clawed fingers**; a thick tail used for balance;
hip joints set unusually high on the body; a large mouth with many sharp teeth that can
chew through most materials. Omnivorous - grasses and weeds, but also other organisms,
including their own kind. Egg-laying (*Smuggler's Gambit*); males were eaten by females after
mating (*The Mandalorian* Ch. 1, per the page). Height about 2 m (Clone Wars) to 2.5-3 m (Endor); the page gives no hip/shoulder reference point; length about 4 m; lifespan
35-40 years.

Colour: usually dark - blue, green, grey, brown or black - with lighter mottled patterns
in blue or orange; skin colour "mottled brown"; eyes black. Cham Syndulla's blurrg had
white head markings.

Behaviour: very fast (easily outpaced the Republic's AT-RTs, which top out at 75 kph on flat terrain; the 75 kph figure is the AT-RT's, not the blurrg's), strong load carriers, ill-tempered
and vicious when provoked; one bucked a clone rider. Users: Ryloth's Twi'lek Resistance,
Kuiil, Din Djarin. First canon appearance: "Liberty on Ryloth" (2009).

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** Deleted: the Clone Wars-era Legends render (`wookieepedia_legends_1.webp`, `Blurrg TCW.png`) and the Smuggler's Gambit game frame (`wookieepedia_canon_2.webp`). Kept/added realistic references, all *The Mandalorian* live-action/realistic CGI: `wookieepedia_canon_1.webp` (Star Wars Book studio render), `wookieepedia_canon_3.webp` (Chapter 1 film still, side view in a paddock), `wookieepedia_canon_4.webp` (Chapter 1, two blurrgs ridden away from camera, rear view). The painted Wildlife field-guide plate `wookieepedia_legends_2.webp` stays as a Legends size/young reference only.

What the realistic images show (and where it corrects the text-only brief written earlier):
- **Body:** one huge rounded mass in which head and torso merge — almost no neck; the giant head IS the front of the body. Carried on two thick, short, elephant-like hind legs with broad flat feet; a thick tapering tail drags low behind.
- **Skin:** almost uniform **dark slate grey to charcoal**, thick and heavily wrinkled/folded like elephant or rhino hide, with deep fold lines down the back. 🔴 **The earlier text-only brief's "mottled hide with lighter patches, paler belly" is NOT what the live-action creature shows** — at most a faint tonal variation; no patches, no pale belly.
- **Mouth:** an enormous wide gape with purplish-grey lips and ragged rows of long, uneven, yellowed fangs that jut outward; a pink tongue.
- **Eyes:** small, dark brown, set high on the sides of the head under a heavy brow ridge.
- **Forelimbs:** two very short, thin arms hanging from the chest under the jaw, each ending in a few hooked claws — tiny relative to the body, but clearly present.

**Discrepancy against the queued art.** Artpipe jobs `rsw_blurrg_v1_{south,east,north}`
(item `LEANINGSCRUB_BEDAZZLE_SITTING_1`) and the design brief section 8 of
`design/Jawa/worldbuilding/biomes/leaningscrub_bedazzle_cast_2026-09-29.md` say "no
functional forelimbs". Canon says two short two-fingered clawed arms, and the ported
BodyDef keeps both arms with claw attack tools. **The Must-show below wins over the
render**: a regen that shows no arms at all is wrong on canon. The queued jobs' `drawsize`
is 1.0; the def's adult drawSize is 2.4.

## Must show
- [ ] Bipedal: one huge rounded head-and-body mass with almost no neck, on two thick short elephant-like hind legs with broad flat feet
- [ ] Two SHORT thin forelimbs hanging under the jaw, ending in hooked claws (not absent, not full-size arms)
- [ ] Thick tapering tail carried low behind as a counterbalance
- [ ] Enormous wide mouth with purplish lips and ragged rows of long, uneven, outward-jutting yellowed fangs
- [ ] Nearly uniform dark slate-grey, heavily wrinkled elephant-like hide — no light mottled patches, no pale belly
- [ ] Mount-sized bulk, clearly bigger than a person (ridden in canon)
- [ ] Realistic rendering: natural thick wrinkled hide texture and lighting, no outlines, no cartoon shading

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Blurrg (Wookieepedia article text, pulled via
  `starwars.fandom.com/api.php?action=parse&page=Blurrg&format=json&prop=wikitext`, 2026-09-29)

## Candidate images
- `wookieepedia_canon_1.webp` — *The Mandalorian* blurrg, realistic CGI studio render (The Star Wars Book); file `Blurrg-TSWB.png` — https://static.wikia.nocookie.net/starwars/images/f/f7/Blurrg-TSWB.png/revision/latest?cb=20241114043748
- `wookieepedia_canon_3.webp` — *The Mandalorian* Chapter 1 film still, side view (Topps Authentics); file `Blurrg-ToppsAuthentics.jpg` — https://static.wikia.nocookie.net/starwars/images/d/d3/Blurrg-ToppsAuthentics.jpg/revision/latest?cb=20200524192533
- `wookieepedia_canon_4.webp` — *The Mandalorian* Chapter 1 film still, two ridden blurrgs from behind on Arvala-7; file `Blurrgs-Arvala7-TMS1C1.png` — https://static.wikia.nocookie.net/starwars/images/9/9b/Blurrgs-Arvala7-TMS1C1.png/revision/latest?cb=20220206230757
- `wookieepedia_legends_2.webp` — LEGENDS painted Wildlife of Star Wars field-guide plate, blurrg with young beside an Ewok for size (illustration, Legends only); file `Blurrg2-woswfg.jpg` — https://static.wikia.nocookie.net/starwars/images/6/69/Blurrg2-woswfg.jpg/revision/latest?cb=20070112142710

No donor sprite available (donor art is AssetBundle-only). Native drop-in folder
`D:\Luke\dev\Rimworld\src\RimStarWars\SWBestiary\Textures\Things\Pawn\Animal\RSW_Blurrg\`.

## ruling
(empty — owner has not reviewed this entry; canon stands unopposed.)
