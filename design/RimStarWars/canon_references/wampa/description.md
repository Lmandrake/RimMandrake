# Wampa

**defName**: `RSW_Wampa` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia)
Wampas ("wampa ice creatures") were a carnivorous, semi-sentient, white-furred
species of mammal dwelling on the snow-clad planet Hoth. Wookieepedia gives:
height 2.5–3 meters, mass ~150 kg average (up to 200 kg max recorded), **white
fur**, **black eyes**, a pair of small cranial horns, and cave-dwelling
behavior. One of Hoth's top predators, using white fur as camouflage to
ambush prey (chiefly tauntauns) with razor-sharp fangs and claws, then
dragging the catch back to a cave to hang upside-down until consumed — which
is exactly what happens to Luke Skywalker at the start of *The Empire Strikes
Back*. Described as demonstrating advanced intelligence and caring about their
clans (semi-sentient, not a mindless beast). Diet: carnivore. Habitat: snow
plains/ice caves of Hoth. Wampas have predators of their own (for example fire-breathing dragon slugs, Tales from the Rancor Pit), hunted tauntaun, rayboo and willing to hunt humans, Sullustans or Mon Calamari, and live in clans (the establishment of Echo Base displaced one; Forces of Destiny, "Beasts of Echo Base", shows wampas entering the base). Young wampas (younglings) appear in Tales from the Rancor Pit. https://starwars.fandom.com/wiki/Wampa
A visually similar "cousin species," the Mogu,
exists on the warmer world of Koboh but is a distinct species.

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**

The illustrated comic cover (`comic_cover_agesolo.jpg`) was deleted 2026-10-08. Every remaining reference is
LIVE-ACTION *The Empire Strikes Back* (practical suit): `wookieepedia_esb_fullbody.png` (full standing body in the ice
cave, the clearest anatomy), `wookieepedia_esb_onearm.png` (the wounded wampa's head and shoulders, wet matted fur and
blood), `wookieepedia_infobox_esb.jpg` (the ruled image) and `wookieepedia_unused_concept.jpg` (unused suit, close-up).
From the live-action stills: a huge, heavy, upright ape/yeti with long, thick, shaggy cream-white fur that hangs in
clumps and parts over the limbs; a broad short-snouted face of dark grey-black bare skin with deep-set small dark eyes
and a jutting lower jaw of uneven fangs; two short dark ram-like horns curling down beside the face; long arms with
dark claws. Fur reads warm cream, not pure white, and is matted and dirty-pink with blood where it fed.

The candidate images broadly agree on white shaggy fur, black facial
features, and a heavyset ape/bear-like posture with prominent claws — but
they diverge on stance and menace level. The ESB-era infobox still (practical
suit, bound and hoisted by rope, arms raised) and the unused behind-the-scenes
still (the wiki captions it "an early, unused wampa costume design", so it is design evidence, not final on-screen anatomy; the released ESB footage takes priority) (screaming close-up, fangs bared, blood-streaked claws and muzzle) both
show a **bipedal, ape/yeti-like posture** with long shaggy white fur, dark
bald-looking facial skin around the eyes/muzzle, small dark eyes, and visible
sharp claws and fangs — genuinely frightening, not cute. The live-action full-body
still confirms small dark curled horns on the head matching the "small cranial
horns" in the text.

**The current donor sprite (`donor_current_sprite.png`) disagrees in body
plan, not just detail**: it is drawn as a **quadrupedal**, bear/dog-like
grazing-animal silhouette (side profile, four legs on the ground, gentle
posture) with tan/brown blotching on the face — none of the reference images
show a wampa on all fours, and none show brown blotching; every reference is
a bipedal, upright, arms-out predator with a mostly white coat and dark bare
skin only immediately around the eyes/muzzle. The donor sprite also omits the
claws and small horns entirely. A regen should correct the stance to
upright/bipedal-reaching and add visible claws and small head horns; this is
a bigger disagreement than the Dewback or Bantha cases and is worth flagging
prominently for the owner's ruling.

## Must show
- [ ] Bipedal, upright, ape/yeti-like posture — not a quadrupedal, on-all-fours stance
- [ ] Long, shaggy white fur coat, not brown/tan blotching
- [ ] Dark, bald-looking bare skin confined to around the eyes/muzzle only
- [ ] Visible sharp claws and fangs
- [ ] Small cranial horns visible on the head silhouette
- [ ] Realistic rendering: natural shaggy cream-white fur with clumping and natural snow-cave lighting, no outlines, no cartoon shading

## Engine limits
none known — the donor sprite's disagreement (a quadrupedal, four-legged grazing-animal silhouette with brown blotching and no claws or horns) is recorded as a wrong body-plan/pose choice for a regen to correct, not as a rendering-pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Wampa (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Wampa&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/d/d0/SkywalkerWampa.jpg (infobox art — practical suit still from *The Empire Strikes Back*, bound/hoisted)
- https://static.wikia.nocookie.net/starwars/images/7/70/Wampa_unused_btm.jpg (unused behind-the-scenes/promotional still — close-up snarl, claws and blood detail)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary mod, east-facing base variant), quadrupedal white body with brown face blotching, no claws/horns visible
- `wookieepedia_infobox_esb.jpg` — ESB practical-suit still, bipedal, arms raised, ropes/rigging visible (production still, not in-universe view, but shows the canonical suit design)
- `wookieepedia_unused_concept.jpg` — unused behind-the-scenes close-up, snarling face, bared fangs, blood-streaked claws and muzzle
- `wookieepedia_esb_fullbody.png` — *The Empire Strikes Back* live-action, full standing wampa in the ice cave holding a tauntaun limb; file `Wampa-BOSWI11.png` — https://static.wikia.nocookie.net/starwars/images/a/ac/Wampa-BOSWI11.png/revision/latest?cb=20241228061749
- `wookieepedia_esb_onearm.png` — *The Empire Strikes Back* live-action, the wounded wampa's head and shoulders; file `OneArm-ESB.png` — https://static.wikia.nocookie.net/starwars/images/0/02/OneArm-ESB.png/revision/latest?cb=20130320014431

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox_esb.jpg`

> "Correct. Giant ape-like predator, capable of standing upright."
