# Dalgo

**defName**: `RSW_Dalgo` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia + Clone Wars wiki)
Dalgos are a reptilian species native to the dense jungles of Onderon (also
found on the desert moon Zardossa Stix). Unlike their smaller herbivorous
cousins, dalgos are carnivorous predators — but are still domesticated for
the same roles: Onderon rebels used dalgos as beasts of burden and battle
mounts during the Onderonian Civil War (*The Clone Wars* Season 5, beginning
with "A War on Two Fronts"). Height 2.5-3 meters. Wookieepedia infobox gives:
**orange** skin, **purple** eyes, a dorsal crest, unusually high body
temperature, and three nostrils.

The companion Clone Wars wiki fills in the body plan the Wookieepedia entry
only stubs: dalgos are sure-footed reptilian quadrupeds built for
long-distance running and swift sprints as well as cargo-pulling. The
long-snouted head carries a heat-radiating crest running its length, ending
in a wide, blade-like tail. Three large nostrils sit atop the forward crest,
venting air from powerful lungs. The mouth has sharp teeth including two
lower tusks, and a forked tongue used to scent-track danger in the thick
jungle air.

## Visual brief
Both candidate images (Star Wars Encyclopedia art and a "Secrets of Tatooine"
piece — note: shown mounted with tack despite the Onderon-jungle origin,
consistent with its use as a domesticated battle mount) agree closely and
match the text: a tall, long-legged reptilian runner with a raptor/theropod
build, not a low-slung lizard. The head has a pronounced sail-like dorsal
crest running from the crown down the neck, a long snout with visible sharp
teeth (including the lower tusks), and the hide is a warm **rust-orange**
with a paler cream/tan underside and belly, exactly matching the "orange
skin" infobox field. Both images show the animal saddled and reined as a
mount, legs long and thin, built for speed rather than bulk.

**The current donor sprite (`donor_current_sprite.png`) disagrees on body
proportions**: it keeps the correct orange/rust coloring and a small
head-crest, but renders the animal as a low, stocky, elongated
dachshund-shaped quadruped with short stubby legs and a curled tail — the
opposite of the tall, long-legged running/sprinting build shown in every
reference image. The blade-like tail tip and forward-facing nostril crest
are also not legible on the donor sprite. Any regen should raise the body
onto long thin legs, lengthen the snout, and keep the orange-with-cream-
underside palette and dorsal crest.

## Source URLs
- https://starwars.fandom.com/wiki/Dalgo (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Dalgo&prop=wikitext`,
  2026-09-13)
- https://clonewars.fandom.com/wiki/Dalgo (Clone Wars wiki, body-plan detail
  not present on the Wookieepedia stub, pulled via
  `clonewars.fandom.com/api.php?action=parse&page=Dalgo&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/8/83/Dalgo-SWE.png
  (*Star Wars Encyclopedia* reference art)
- https://static.wikia.nocookie.net/starwars/images/0/02/Dalgo_SoT.png
  ("Secrets of Tatooine" promotional/game art, saddled dalgo rearing)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary
  mod, east-facing base variant), low stocky orange quadruped with small
  head-crest
- `wookieepedia_encyclopedia_art.png` — *Star Wars Encyclopedia* art, saddled
  dalgo rearing on hind legs, shows head crest, snout, teeth, tusks, and
  orange/cream coloring clearly
- `wookieepedia_sot_art.png` — "Secrets of Tatooine" art, standing saddled
  dalgo on rocky ground, shows the full long-legged runner silhouette and
  blade-like tail tip

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_sot_art.png`

> "But the Donor mod really isn't too bad this time."
