# Nuna

**defName**: `RSW_Nuna` (vendored in SWBestiary)

## Sourced text (Wookieepedia)
Nunas, also known as **"swamp turkeys,"** were small, non-sentient bipeds
native to the swamps of Naboo that spread across the galaxy and were also
found on Tatooine, Coruscant, and Saleucami. Infobox stats: height ~0.5
meters, mass ~4 kilograms, **skin color green**, **eye color white**,
Wookieepedia-classed **`[[Bird]]`**, habitat desert/swamp/urban, diet
omnivore (mostly plants, occasionally fish). They could not fly, were known
for their stupidity, but were adaptable and easy to care for — combined with
fast egg production, this made them a popular, easy livestock animal capable
of feeding a family of four per bird. When angered or threatened they could
inflate their bodies to a larger size. A 2020s comic (*Doctor Aphra* #33)
establishes they were capable of growing blue and red feathers. Canon role
is overwhelmingly culinary and background-livestock: roast nuna, deep-fried
nuna leg, Nuna Turkey Jerky (a real Galaxy's Edge/Batuu snack item at Ronto
Roasters), and nuna used as the ball in the sport "nuna-ball." They appear
as background livestock across the prequel trilogy, *The Clone Wars*, *The
Bad Batch*, *The Mandalorian*, and *The Book of Boba Fett*, almost always
as scenery or food rather than a creature shown up close.

## Visual brief
The three candidate images (all official render/promotional art of the
animal itself, not food shots) are internally consistent with each other but
**disagree sharply with the "bird" / "swamp turkey" framing in the text**.
None of the three shows anything resembling feathers, a beak, wings, or a
turkey-like silhouette. What they actually show is a squat, hunched,
**toad- or turtle-like amphibian/reptile**: a heavy domed/ridged shell-like
back rising into a peak, a wide froglike head with a broad flat mouth and
bulging pink or amber eyes, floppy skin flaps hanging at the sides of the
head (read as loose jowls/wattle, not ears), thick bent hind legs ending in
clawed toed feet, and mottled olive-to-dark-green pebbled/warty skin — no
visible feather texture anywhere, on any of the three images, across two
different render styles and two different eras of official art. The
front-on view (`wookieepedia_walkintime.jpg`) confirms the body is wider
than tall when viewed head-on, with the two hind legs doing all the
visible structural work, consistent with the "biped" description, but the
overall read is far closer to a bloated toad or snapping turtle than to any
bird. Skin color does match the infobox text (green). "Swamp turkey" as a
nickname reads as a folk/marketing name for a domesticated food animal
rather than a literal physical descriptor — the images support "turtle"
far better than "turkey."

**The donor sprite agrees reasonably well with the images**, better than
most creatures in this library: it is green, has a hunched dome-shaped back
with lighter banding suggesting a ridged/shell-like top, a forward-jutting
mouth/head, and a single small orange nub at the front-left that reads as a
stylized crest or wattle rather than a wing. It is far more simplified and
flat-cartoon-shaded than any candidate image (RimWorld's chunky low-detail
art style, no visible skin texture or individual toes), and it omits the
visible hind legs / froggy stance entirely — the sprite reads as a rounded
blob-with-a-face rather than a standing biped — but the *silhouette family*
(squat, hunched, domed-backed, green, toad/turtle-adjacent, not bird-like)
is a genuine match to canon, which is not true of every creature audited so
far in this library.

## Must show
- [ ] Heavy domed/ridged shell-like back rising to a peak
- [ ] Wide, froglike head with a broad flat mouth and bulging pink or amber eyes
- [ ] Floppy skin flaps hanging at the sides of the head (jowls/wattle, not ears)
- [ ] Thick, bent hind legs ending in clawed, toed feet, doing the visible structural work of standing
- [ ] Mottled olive-to-dark-green pebbled/warty skin — no feather texture, beak or wings anywhere

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Nuna (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Nuna&prop=wikitext`,
  2026-09-13, since the direct page fetch was Cloudflare-blocked)
- https://static.wikia.nocookie.net/starwars/images/4/4d/Nuna-SWCT.png (current Wookieepedia infobox art, credited on-wiki to *Star Wars: Card Trader*)
- https://static.wikia.nocookie.net/starwars/images/a/aa/Nuna.png (older full-body render used historically on the article/Databank)
- https://static.wikia.nocookie.net/starwars/images/8/80/Nuna-WIT.png (front-facing render)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite
  (`Nuna_f_east.png`, SWBestiary mod). Picked the **female east variant**
  arbitrarily as "the" base sprite — female and male live variants appear
  to be of equal status in the def/texture set (both have full
  east/north/south sets), so this is not a canon or gameplay preference,
  just a pick between two equally-live options.
- `wookieepedia_infobox.jpg` — current Wookieepedia infobox render
  (`Nuna-SWCT.png`), 3/4 side view, hunched toad/turtle body, domed ridged
  back, wide froglike mouth, pink eyes, floppy head flaps, clawed hind feet
- `wookieepedia_classic_render.jpg` — older full-body render (`Nuna.png`),
  same creature design from a different angle/lighting, confirms the body
  plan is consistent across separate official art assets
- `wookieepedia_walkintime.jpg` — front-on render (`Nuna-WIT.png`), shows
  the creature facing the camera: wide stance, two visible clawed hind
  legs, mouth/jowl detail, confirms width-forward silhouette

Note: two other files returned by the wiki's image index under the "Nuna"
name prefix (`Nuna_CW.png`, `NunasTwins.jpg`) were downloaded and inspected
but turned out to be unrelated art (a Jawa portrait and a starship
illustration respectively, likely a coincidental filename collision) — they
were discarded and are not included here.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.jpg`

> "E3 is canon. May need suggestion of thick bird-like legs to avoid making it look like a frog."
