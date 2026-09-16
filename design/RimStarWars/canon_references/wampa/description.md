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
plains/ice caves of Hoth. A visually similar "cousin species," the Mogu,
exists on the warmer world of Koboh but is a distinct species.

## Visual brief
The candidate images broadly agree on white shaggy fur, black facial
features, and a heavyset ape/bear-like posture with prominent claws — but
they diverge on stance and menace level. The ESB-era infobox still (practical
suit, bound and hoisted by rope, arms raised) and the unused behind-the-scenes
still (screaming close-up, fangs bared, blood-streaked claws and muzzle) both
show a **bipedal, ape/yeti-like posture** with long shaggy white fur, dark
bald-looking facial skin around the eyes/muzzle, small dark eyes, and visible
sharp claws and fangs — genuinely frightening, not cute. The official comic
cover art (Luke dangling, wampa lunging with jaws open) confirms the same
white-furred, black-eyed, fanged, roughly humanoid-postured predator, plus
visible small horns on the head silhouette matching the "small cranial horns"
in the text.

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

## Engine limits
none known — the donor sprite's disagreement (a quadrupedal, four-legged grazing-animal silhouette with brown blotching and no claws or horns) is recorded as a wrong body-plan/pose choice for a regen to correct, not as a rendering-pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Wampa (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Wampa&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/d/d0/SkywalkerWampa.jpg (infobox art — practical suit still from *The Empire Strikes Back*, bound/hoisted)
- https://static.wikia.nocookie.net/starwars/images/7/70/Wampa_unused_btm.jpg (unused behind-the-scenes/promotional still — close-up snarl, claws and blood detail)
- https://static.wikia.nocookie.net/starwars/images/2/2c/GreatestMomentsTextless-AgeSolo1.png (official comic cover art — Luke dangling, wampa lunging)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary mod, east-facing base variant), quadrupedal white body with brown face blotching, no claws/horns visible
- `wookieepedia_infobox_esb.jpg` — ESB practical-suit still, bipedal, arms raised, ropes/rigging visible (production still, not in-universe view, but shows the canonical suit design)
- `wookieepedia_unused_concept.jpg` — unused behind-the-scenes close-up, snarling face, bared fangs, blood-streaked claws and muzzle
- `comic_cover_agesolo.jpg` — official comic cover art, wampa lunging at a dangling Luke Skywalker, clean modern illustrated take on the same design

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox_esb.jpg`

> "Correct. Giant ape-like predator, capable of standing upright."
