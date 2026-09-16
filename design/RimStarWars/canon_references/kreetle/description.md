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
four-to-five. A larger, more aggressive variant race exists, the
"Overkreetle." Gungans on Naboo used kreetles as nutcrackers and also ate
them. First appeared in the *Star Wars Episode I: The Gungan Frontier*
game; also appears in *Jedi Power Battles*, *Republic Commando* (rendered
there with only three pairs of legs, not five, per the "Behind the scenes"
section), *Star Wars Galaxies*, and several novels (later used only as an
insult, "kreetle," in Legacy-era books).

## Visual brief
Unlike the Peko-peko/Wyyyschokk cases, text and images **agree well** here —
all four candidates show the same basic body plan and there is no dramatic
"generic vs canon" contradiction. The one real disagreement is shell color:

- `wookieepedia_infobox.jpg` — the official species-page illustration (art
  from *The Art of Star Wars Episode I*/Jedi Power Battles era). Shows a
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
- `swg_kreetle.jpg` — *Star Wars Galaxies* in-game creature: same domed,
  ribbed-shell, many-legged body plan and pink eye-glints, but the shell
  renders as **olive/khaki-brown** rather than reddish-maroon — noticeably
  more green-brown than the other three sources. This is a genuine
  cross-image disagreement, not a text/image one: body plan and eye color
  agree everywhere, but SWG's coloring skews duller/greener while the
  *Republic Commando*-era art and screenshots both skew red.

**Net read**: a low, domed, segmented/ribbed shell (pillbug or hermit-crab
silhouette) in reddish-brown-to-maroon (SWG's more olive/khaki version is a
secondary, less-corroborated variant), a mottled tan/spotted head, dark
mandibles/tusks, bright yellow eyes, and many short jointed legs along the
sides (five pairs per the text; three pairs as actually modeled in
*Republic Commando*). This is a small, floor-hugging arthropod — treat it as
a scavenger/pest-scale creature, not anything human-sized.

## Must show
- [ ] Low, domed, segmented/ribbed shell (pillbug or hermit-crab silhouette)
- [ ] Shell colour reddish-brown to maroon (the better-corroborated read; olive/khaki-brown is a secondary, less-corroborated variant)
- [ ] Mottled tan/gold head with dark reddish spots
- [ ] Dark, curved mandibles/tusks at the front
- [ ] Bright yellow eyes
- [ ] Many short jointed legs along the sides of the body

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Kreetle (Legends article, wikitext pulled
  2026-09-13 via `https://starwars.fandom.com/api.php?action=parse&page=Kreetle&format=json&prop=wikitext`)
- https://static.wikia.nocookie.net/starwars/images/2/23/Kreetle.jpg (species-page infobox illustration)
- https://static.wikia.nocookie.net/starwars/images/3/35/KasBug.jpg ("A kreetle found on Kashyyyk," *Republic Commando*)
- https://static.wikia.nocookie.net/starwars/images/c/c4/GeonosianBug.jpg ("A kreetle found on Geonosis," *Republic Commando*)
- https://static.wikia.nocookie.net/starwars/images/6/66/KreetleSWG.jpg ("A Kreetle, as seen in Star Wars Galaxies")
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
- `swg_kreetle.jpg` — *Star Wars Galaxies* in-game creature render: same
  body plan but shell reads olive/khaki-brown rather than reddish-maroon —
  the one real color disagreement among the candidates.
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — not
  installed locally, ships in AssetBundles in its current release, and no
  labeled workshop preview screenshot was found this pass. Revisit if the
  mod is ever installed locally or a labeled preview surfaces.

## ruling
**RULED** (owner, 2026-09-13, review sheet): `wookieepedia_infobox.jpg`
