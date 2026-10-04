# Gorg

**defName**: `RSW_Gorg` — in-repo label "gorg"; no variants

> Entry created 2026-10-04 (`canon_gapfill.py`, then images viewed and the brief written by hand).
> Root cause of the owner's "nothing for Gorg": there was **no gorg entry at all** in this library
> (none of RSW_Gorg / RSW_LongtailGorg / RSW_FrilledGorg had one), so the review sheet said
> "no canon-library entry". Both the canon page and `Gorg/Legends` are used here.

## Sourced text (Wookieepedia)
### Canon — https://starwars.fandom.com/wiki/Gorg

Gorgs, also known as chubas, was a general term used for several species of amphibians used as food by many different sentient species. They were available for seven wupiupi in the markets of Mos Espa on the planet Tatooine, During the Naboo Crisis, the Gungan Jar Jar Binks attempted to use his long tongue to grab one from a stall for free. The Hutt crime lord Jabba Desilijic often ate gorgs, swallowing one live at the Boonta Eve Classic podrace and thirty-six years later in his palace. Kadas'sa'Nikto were also known to eat gorgs live.

### Legends — https://starwars.fandom.com/wiki/Gorg/Legends

Gorgs, known as chubas in Huttese, were small precocious amphibians that could be found on several planets, from the swamps of Naboo  to the deserts of Tatooine (the latter being their original native planet). They were popularly favored as food by many humanoid species (including on Tatooine), either dried, fricasseed, or roasted in manak leaves. In Huttese, "hot chubas" were called "hotsa chuba."

**Biology and appearance** There were many species of gorgs, including long-tailed, three-eyed, and four-eyed varieties. Different types of gorgs were eventually introduced to the populations of Naboo and its moon of Rori, where they evolved to become large, flesh-eating creatures.

Sometimes, during times of great drought on their native world of Tatooine, gorgs hibernated in burrows, encasing themselves in a cocoon of hardened saliva. Occasionally, these burrows that gorgs used for general shelter and hibernation could be within profogg "towns".

Natural predators included worrts, which the gorgs themselves were somewhat similar to, but smaller and more ambulatory.

Gorgs were also known to be mutated by bio-engineers. One such mutation resulted in the successful growth of a chubafly: a colorful gorg but with wings that made it capable of flying.

## Visual brief
🔑 **Gorg is a SPECIES WITH SEVERAL LEGITIMATE LOOKS, not one look** (owner, 2026-10-04: there
are many kinds, all equally considered gorg). The canon page calls "gorg" "a general term used
for several species of amphibians"; Legends names "long-tailed, three-eyed, and four-eyed
varieties". Every variant below is a valid gorg; none is the "real" one. Shared by all: a
**small (Legends: 0.2 m tall, up to 0.3 m long) frog/newt-like amphibian with a very wide mouth**.

| # | variant | colour | shape | size cue | source image |
|---|---|---|---|---|---|
| 1 | **purple four-eyed gorg** | violet-purple, iridescent teal/mint and cream highlights, darker purple spots, cream belly | squat frog body, flat head swept into two pointed side-lobes, very wide lipless grin, **four small green eyes in a row**, webbed long-toed hind feet, no tail | small | `wookieepedia_legends_1.webp` (Legends infobox, `Gorg-WoSW.png`, *Wildlife of Star Wars* painting) |
| 2 | **pale grinning gorg** | pale cream-green, white-speckled bulbous belly | bulbous pear body, huge **toothy grin with red tongue**, fringe of green tendrils/barbels hanging below the mouth, green webbed feet | small, round | `wookieepedia_nl_gorgs1.webp`, left (TPM market concept art) |
| 3 | **hammer-headed gorg** | mottled mid/dark green | **broad flat hammer/arrowhead head with eyes at the outer corners**, tendril barbels under the jaw, clawed fingers | small, heavy-headed | `wookieepedia_nl_gorgs1.webp`, lower centre |
| 4 | **spiky-backed gorg** | peach/tan body, **lavender-purple spiky dorsal ridge**, brown speckles | bulbous pear body, spindly limbs with **orange-yellow ball-tipped toes** | small, round | `wookieepedia_nl_gorgs1.webp`, upper centre |
| 5 | **fin-tailed gorg** | pale green, speckled belly, red eye | slender newt body, upturned **toothy jaw**, **long thin tail ending in a webbed paddle/fin** | small, long | `wookieepedia_nl_gorgs1.webp`, right |
| 6 | **spotted long-tailed gorg (the film gorg)** | tan/ochre with dark brown spots on screen (`wookieepedia_legends_2.webp`, TPM prop); lime-green with dark-green leopard spots on the canon infobox figure (`wookieepedia_canon_1.webp`); brown in ROTJ (`wookieepedia_legends_3.webp`) | sprawled lizard-frog, bulging eyes, **long thin tail**, long splayed clawed toes, **long red tongue** | small | `wookieepedia_canon_1.webp`, `wookieepedia_legends_2.webp`, `wookieepedia_legends_3.webp` |

`wookieepedia_nl_gorgs1.webp` is the Dutch Wookieepedia's illustration on its `Gorg` page
(file `Gorgs1.jpg`, used by nl:Gorg only): four different gorgs hung by their feet for sale,
TPM Mos Espa market concept-style painting. It is the single best evidence that gorgs vary
in **shape**, not only colour.

**Images vs prose:** the prose never gives a colour; colour comes only from images and differs
by variety. No height/mass beyond the Legends infobox (0.2 m tall, up to 0.3 m long) is sourced.

### Our defs vs these looks (checked 2026-10-04)
`RSW_Gorg` already uses `alternateGraphics` (`alternateGraphicChance` 0.8) with **six looks**:
base + `GorgA`–`GorgE` under `src/RimStarWars/SWBestiary/Textures/swanimals/Gorg/`. But all six
are the **same donor silhouette recoloured** (blue, green, ochre, salmon, purple, pink-spotted) —
they vary colour only. The canon variants above vary **shape** (four-eyed lobed head, hammer
head, spiky back, fin tail, long tail). So the slot structure can already carry one canon look
per slot; the art would have to be new per slot. Same mechanism exists on `RSW_LongtailGorg`
(base + A–D, one long-bodied fluke-tailed silhouette recoloured) and `RSW_FrilledGorg` (base +
A–C, a spiky-backed silhouette recoloured). Unsourced observation: the donor's frilled gorg's
spiky back resembles variant 4 and its longtail gorg's fluke resembles variant 5 — plausible
donor inspiration, not a canon fact. Proposal only, not done: no cosmetic change without the
owner's word.

## Must show
- [ ] Every variant: small, squat or newt-like amphibian with a very wide mouth
- [ ] Variants differ in SHAPE, not only colour (lobed four-eyed head / hammer head / spiky back / fin tail / long tail)
- [ ] Purple four-eyed variant, if used: violet-purple with teal/cream highlights, two swept-back head lobes, four small eyes
- [ ] Film variant, if used: long thin tail and dark spots on tan/brown (or green) skin
- [ ] Webbed or long-toed splayed feet

## Engine limits
- A single-channel tint mask cannot express the purple-with-teal iridescence, the spots, or a
  differently-coloured spiky ridge (variant 4) — those need art, not a colour value.
- Shape variants need separate art per `alternateGraphics` slot; tinting one silhouette (what
  ships now) cannot produce them.
- The four-eyed face is a few pixels at RimWorld animal scale: a wide head with an eye row.

## Source URLs
- https://starwars.fandom.com/nl/wiki/Bestand:Gorgs1.jpg (Dutch Wookieepedia file used on nl:Gorg; pointed out by the owner 2026-10-04)
- https://starwars.fandom.com/wiki/Gorg (canon; wikitext pulled via the API 2026-10-04)
- https://starwars.fandom.com/wiki/Gorg/Legends (Legends; wikitext pulled via the API 2026-10-04)

## Candidate images
- `wookieepedia_canon_1.webp` — CANON page `Gorg`; wiki caption: infobox image. File: `Gorg tongue.png` — https://static.wikia.nocookie.net/starwars/images/c/ce/Gorg_tongue.png/revision/latest?cb=20221122050031
- `wookieepedia_legends_1.webp` — LEGENDS page (non-canon continuity) `Gorg/Legends`; wiki caption: infobox image. File: `Gorg-WoSW.png` — https://static.wikia.nocookie.net/starwars/images/d/da/Gorg-WoSW.png/revision/latest?cb=20230904021132
- `wookieepedia_legends_2.webp` — LEGENDS page (non-canon continuity) `Gorg/Legends`; wiki caption: A gorg for sale in Mos Espa. File: `Gorg db.jpg` — https://static.wikia.nocookie.net/starwars/images/a/a2/Gorg_db.jpg/revision/latest?cb=20071124191517
- `wookieepedia_legends_3.webp` — LEGENDS page (non-canon continuity) `Gorg/Legends`; wiki caption: Jabba the Hutt consumed gorgs live. File: `Longtailfrog.jpg` — https://static.wikia.nocookie.net/starwars/images/9/91/Longtailfrog.jpg/revision/latest?cb=20060620041238
- `wookieepedia_nl_gorgs1.webp` — DUTCH Wookieepedia (nl) `Gorg` page illustration, four gorg varieties hanging for sale (TPM market). File: `Gorgs1.jpg` — https://static.wikia.nocookie.net/starwars/images/1/11/Gorgs1.jpg/revision/latest?cb=20070503175729&path-prefix=nl

## ruling
(empty — owner has not reviewed this creature yet)
