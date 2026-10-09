# Kreetle

**defName**: `Kreetle` (third-party, mlie.starwarsanimalcollection, not
vendored — see Source URLs note below; as of the current 1.6 release the
donor mod ships creature textures packed inside Unity AssetBundles rather
than as loose PNGs, so no per-creature sprite could be pulled from the
donor's public GitHub mirror either)

## Sourced text (Wookieepedia)
Legends-only creature (current canon only shows an "Unidentified creature"
at Ronto Roasters in Galaxy's Edge that fans associate with the kreetle —
never formally named in current canon). Per the Legends article:

The **kreetle** was a parasitic, burrowing insect commonly found in homes
and around cities on multiple worlds (Tatooine, Naboo, Kashyyyk, Geonosis).
Species infobox: **skin color brown**, **eye color yellow**, distinctions
listed as *Shell*, *Ten legs*, *Large jaws*. Body text is more specific:
"equipped with five pairs of legs [ten legs total], a tough
**reddish-brown exoskeleton**, and large mandibles." Habitat: burrows,
desert, forest, swamp, urban; diet omnivorous, though behavior text also
says they "fed on flesh, whether living or dead" and attacked in groups of
four-to-five. The same page also says kreetles "thrived on garbage and vegetable remains" and often lived in abandoned profogg burrows, and (Jedi Power Battles) shared a symbiotic relationship with slaatik hagworms in the Lianorm Swamp. A larger, more aggressive variant race exists, the
"Overkreetle." Gungans on Naboo used kreetles as nutcrackers and also ate
them. First appeared in the *Star Wars Episode I: The Gungan Frontier*
game; also appears in *Jedi Power Battles*, *Republic Commando* (rendered
there with only three pairs of legs, not five, per the "Behind the scenes"
section), *Star Wars Galaxies*, and several novels (later used only as an
insult, "kreetle," in Legacy-era books).

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**
The low-poly *Star Wars Galaxies* render (`swg_kreetle.jpg`, olive/khaki shell) was deleted. The owner-ruled infobox plate (`wookieepedia_infobox.jpg`, a naturalistic watercolour from *The Wildlife of Star Wars*) is the realistic target; the two small *Republic Commando* screenshots stay as corroboration of colour only (dated game renders, not a rendering model). No live-action kreetle exists. Text and images agree on the body plan:

- `wookieepedia_infobox.jpg` — the official species-page illustration (naturalistic watercolour plate, *The Wildlife of Star Wars: A Field Guide*). Shows a
  low, domed, **segmented reddish-maroon ribbed carapace** (like a
  pillbug/woodlouse or hermit-crab shell), a tan/gold mottled head with
  dark reddish spots, prominent dark curved mandibles/tusks at the front,
  bright **yellow eyes**, and short jointed legs along both sides of the
  body. This matches the sourced text closely (reddish-brown shell, yellow
  eyes, large jaws, many legs) and is the strongest single reference.
- `wookieepedia_kashyyyk.jpg` — small in-game screenshot (*Republic
  Commando*, "A kreetle found on Kashyyyk"): low-res but shows the same
  domed, ribbed, **pinkish-maroon shell** with visible yellow eye-glints and
  short leg nubs. Confirms the shell color and low domed-beetle silhouette
  at production-game fidelity, not just concept art.
- `wookieepedia_geonosis.jpg` — small in-game screenshot ("A kreetle found
  on Geonosis," also *Republic Commando*): same domed **reddish/rust-pink
  ribbed shell**, yellow eyes, stubby legs — consistent with the Kashyyyk
  screenshot, reinforcing reddish-brown/maroon as the in-game standard
  color rather than a one-off render choice.

**Net read**: a low, domed, segmented/ribbed shell (pillbug or hermit-crab
silhouette) in reddish-brown-to-maroon, a mottled tan/spotted head, dark
mandibles/tusks, bright yellow eyes, and many short jointed legs along the
sides (five pairs per the text; three pairs as actually modeled in
*Republic Commando*). This is a small, floor-hugging arthropod — treat it as
a scavenger/pest-scale creature, not anything human-sized.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the Legends text and the owner-ruled infobox plate (`## ruling`, owner 2026-09-13: `wookieepedia_infobox.jpg`), corroborated for colour by the two *Republic Commando* screenshots.*
- [ ] BODY PLAN: a small, low, floor-hugging arthropod under a domed, segmented/ribbed shell (pillbug or hermit-crab silhouette); head at the front; many short jointed legs along both sides of the body (five pairs per the text)
- [ ] COLOUR LAYOUT: shell reddish-brown to maroon over the whole back; head mottled tan/gold with dark reddish spots; mandibles dark; eyes bright yellow, the brightest element
- [ ] Dark, curved mandibles/tusks at the front of the head
- [ ] Bright yellow eyes
- [ ] Realistic rendering: natural glossy chitin texture and lighting, no outlines, no cartoon shading (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using.")
- [ ] NEGATIVE: not a tall-legged spider or a long-bodied centipede (legs short, body low and domed); not an olive/khaki shell (the deleted Galaxies render); not human-sized

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Kreetle (Legends article, wikitext pulled
  2026-09-13 via `https://starwars.fandom.com/api.php?action=parse&page=Kreetle&format=json&prop=wikitext`)
- https://static.wikia.nocookie.net/starwars/images/2/23/Kreetle.jpg (species-page infobox illustration)
- https://static.wikia.nocookie.net/starwars/images/3/35/KasBug.jpg ("A kreetle found on Kashyyyk," *Republic Commando*)
- https://static.wikia.nocookie.net/starwars/images/c/c4/GeonosianBug.jpg ("A kreetle found on Geonosis," *Republic Commando*)
- Donor mod `mlie.starwarsanimalcollection` (Steam Workshop, current 1.6
  release id 3497316713, legacy id 2903582351) — the mod's listing and
  description confirm Kreetle is one of its 200+ included creatures, but no
  screenshot on the workshop page is individually labeled Kreetle (the page
  shows 16 unlabeled thumbnail screenshots spanning the whole roster). The
  public GitHub mirror (`github.com/emipa606/StarWarsAnimalCollection`) has
  only an `UpdateInfo` subfolder under `Textures/` — creature art ships
  packed in AssetBundles, not as loose files. **No donor-mod sprite
  obtained this pass**, same situation as `wyyyschokk/` and `pekopeko/` in
  this same directory.

## Candidate images
- `wookieepedia_infobox.jpg` — official species-page illustration: domed
  ribbed reddish-maroon shell, tan/spotted head, dark mandibles, yellow
  eyes, jointed legs. **Best single reference** — most detailed and matches
  the sourced text closely.
- `wookieepedia_kashyyyk.jpg` — small *Republic Commando* in-game
  screenshot: confirms domed ribbed pinkish-maroon shell and yellow eyes at
  production-game fidelity.
- `wookieepedia_geonosis.jpg` — small *Republic Commando* in-game
  screenshot: same reddish-maroon ribbed shell and body plan, corroborates
  the Kashyyyk screenshot.
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — not
  installed locally, ships in AssetBundles in its current release, and no
  labeled workshop preview screenshot was found this pass. Revisit if the
  mod is ever installed locally or a labeled preview surfaces.

## ruling
**RULED** (owner, 2026-09-13, review sheet): `wookieepedia_infobox.jpg`
