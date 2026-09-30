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
including their own kind. Egg-laying; in some accounts males were eaten by females after
mating. Height about 2 m (Clone Wars) to 2.5-3 m (Endor); length about 4 m; lifespan
35-40 years.

Colour: usually dark - blue, green, grey, brown or black - with lighter mottled patterns
in blue or orange; skin colour "mottled brown"; eyes black. Cham Syndulla's blurrg had
white head markings.

Behaviour: very fast (outran AT-RTs, roughly 75 kph), strong load carriers, ill-tempered
and vicious when provoked; one bucked a clone rider. Users: Ryloth's Twi'lek Resistance,
Kuiil, Din Djarin. First canon appearance: "Liberty on Ryloth" (2009).

## Visual brief
Written from the sourced text alone. **The reference images were not pulled or viewed for
this entry - the image half of the brief is UNREAD, not absent.** No donor sprite is
available either: the donor mod (mlie.starwarsanimalcollection) ships its art inside an
AssetBundle, and the port deliberately does not reuse it.

A heavy bipedal reptile with a big rounded body carried on two thick hind legs, hips high
and tail thick and low-slung behind for balance. Head large and long-jawed with visible
sharp teeth. **Two short forelimbs, each ending in two clawed fingers, held tucked against
the chest** - short, not absent. Hide mottled: dark base (grey-brown / brown, blue-green
allowed) with lighter mottled patches, paler belly. Mount-sized: about 2.4 cells at
adult drawSize.

**Discrepancy against the queued art.** Artpipe jobs `rsw_blurrg_v1_{south,east,north}`
(item `LEANINGSCRUB_BEDAZZLE_SITTING_1`) and the design brief section 8 of
`design/Jawa/worldbuilding/biomes/leaningscrub_bedazzle_cast_2026-09-29.md` say "no
functional forelimbs". Canon says two short two-fingered clawed arms, and the ported
BodyDef keeps both arms with claw attack tools. **The Must-show below wins over the
render**: a regen that shows no arms at all is wrong on canon. The queued jobs' `drawsize`
is 1.0; the def's adult drawSize is 2.4.

## Must show
- [ ] Bipedal: two thick hind legs carry the body, hips set high
- [ ] Two SHORT forelimbs, each ending in two clawed fingers (not absent, not full-size arms)
- [ ] Thick tail carried low behind as a counterbalance
- [ ] Large head, big mouth, many visible sharp teeth
- [ ] Mottled hide: dark base (grey-brown, brown, blue-green or black) with lighter mottled patches, paler belly
- [ ] Mount-sized bulk, about 2 m at the shoulder / hip line, clearly bigger than a person

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Blurrg (Wookieepedia article text, pulled via
  `starwars.fandom.com/api.php?action=parse&page=Blurrg&format=json&prop=wikitext`, 2026-09-29)

## Candidate images
None pulled. No donor sprite available (donor art is AssetBundle-only). Ships with no art
until artpipe jobs `rsw_blurrg_v1_*` finish; native drop-in folder
`D:\Luke\dev\Rimworld\src\RimStarWars\SWBestiary\Textures\Things\Pawn\Animal\RSW_Blurrg\`.

## ruling
(empty — owner has not reviewed this entry; canon stands unopposed.)
