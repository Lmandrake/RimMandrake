# Dalgo

**defName**: `RSW_Dalgo` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia + Clone Wars wiki)
Dalgos are a reptilian species native to the dense jungles of Onderon (also
found on the desert moon Zardossa Stix). Unlike their smaller herbivorous
cousins, dalgos are carnivorous predators — but are still domesticated for
the same roles: Onderon rebels used dalgos as beasts of burden and battle
mounts during the Onderonian Civil War (*The Clone Wars* Season 5, beginning
with "A War on Two Fronts"). Height 2.5-3 meters (*Star Wars Encyclopedia*). Wookieepedia infobox gives:
**orange** skin, **purple** eyes, a dorsal crest, unusually high body
temperature, and three nostrils.

The Legends article (`https://starwars.fandom.com/wiki/Dalgo/Legends`, citing *Stay on Target*)
classes the dalgo as "Equine", calls it "four-legged animals", with the same orange skin, purple eyes
and 2.5-3 m height; the canon infobox says "Reptilian" and lists Tipping Points among its appearances.

The companion Clone Wars wiki fills in the body plan the Wookieepedia entry
only stubs: dalgos are sure-footed reptilian quadrupeds built for
long-distance running and swift sprints as well as cargo-pulling. The
long-snouted head carries a heat-radiating crest running its length, ending
in a wide, blade-like tail. Three large nostrils sit atop the forward crest,
venting air from powerful lungs. The mouth has sharp teeth including two
lower tusks, and a forked tongue used to scent-track danger in the thick
jungle air.

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** The Clone Wars season five / Encyclopedia render (`wookieepedia_encyclopedia_art.png`, toon-shaded rearing dalgo with rider) was deleted. No live-action or photoreal dalgo exists (searched: `Images of dalgos`, `Dalgo` and `Dalgo/Legends` page images — only these two pieces); the reference is the painted *Stay on Target* sourcebook art `wookieepedia_sot_art.png`, which this entry's ruling already picked. Render it more realistically than the painting: real reptile skin, real muscle.

What `wookieepedia_sot_art.png` shows: a tall, long-legged, **horse-like four-legged reptilian runner** — deep muscular chest, long thin legs ending in rounded hoof-like pads, a long upright neck. The head carries a large **ridged, fan-like crest** sweeping back from the crown, a long snout. The hide is a smooth warm **rust-orange** with darker reddish shading and a paler tan underside; the tail ends in a wide, curling, blade/fin-like tip. Shown saddled and bridled as a mount.
🔴 The earlier brief called it a "raptor/theropod" stance; the image shows a **four-legged, horse-like** stance, not a biped.

**The current donor sprite (`donor_current_sprite.png`) disagrees on body
proportions**: it keeps the correct orange/rust coloring and a small
head-crest, but renders the animal as a low, stocky, elongated
dachshund-shaped quadruped with short stubby legs and a curled tail — the
opposite of the tall, long-legged running/sprinting build shown in every
reference image. The blade-like tail tip and forward-facing nostril crest
are also not legible on the donor sprite. Any regen should raise the body
onto long thin legs, lengthen the snout, and keep the orange-with-cream-
underside palette and dorsal crest.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in `wookieepedia_sot_art.png` as read by the visual brief, the canon/Clone Wars wiki text (crest, three nostrils, tusks, blade tail), and the `## ruling` below.*
- [ ] BODY PLAN: a tall (2.5–3 m), long-legged, horse-like four-legged reptilian runner — deep muscular chest, long thin legs ending in rounded hoof-like pads, a long upright neck, long-snouted head — not a low-slung lizard and not a biped
- [ ] COLOUR LAYOUT: smooth rust-orange hide over the body with darker reddish shading along the back and a paler tan underside; eyes purple
- [ ] Large ridged fan-like crest sweeping back from the crown of the head (text: the crest runs the animal's length)
- [ ] Long snout (text: sharp teeth and two lower tusks)
- [ ] Wide, curling, blade/fin-like tail tip
- [ ] Realistic rendering: natural smooth reptile-skin texture and muscle under real lighting, no outlines, no cartoon shading
- [ ] Owner rulings carried: 2026-09-14 picked the *Stay on Target* art and noted "But the Donor mod really isn't too bad this time." (palette and crest, per the brief); 2026-10-04 on the redo: "Canon shows somthing more like C. We need a high quality version of that. Look at Canon please." (C = the sail-crested orange dalgo render `pyrelands_dalgo_v1`)
- [ ] NEGATIVE: not a dachshund-shaped low stocky quadruped with short stubby legs and a curled tail (the donor's proportions), not a raptor/theropod biped, not a horse (scaly reptile skin, crest, blade tail, no mane)

## Engine limits
none known

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
  (*Stay on Target* sourcebook art, Legends — file `Dalgo_SoT.png`; saddled dalgo rearing)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary
  mod, east-facing base variant), low stocky orange quadruped with small
  head-crest
- `wookieepedia_sot_art.png` — *Stay on Target* (Legends sourcebook) art, standing saddled
  dalgo on rocky ground, shows the full long-legged runner silhouette and
  blade-like tail tip

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_sot_art.png`

> "But the Donor mod really isn't too bad this time."

**REDO** (owner, 2026-10-04, doubles sheet `Transient/art_doubles_compare_2026-10-04.decisions.json`, item ART_VERSION_WRANGLING_1) on `swanimals/Dalgo/Dalgo`:

> "Canon shows somthing more like C. We need a high quality version of that. Look at Canon please."

(C = render `pyrelands_dalgo_v1`, a cartoon-register sail-crested orange dalgo.)
