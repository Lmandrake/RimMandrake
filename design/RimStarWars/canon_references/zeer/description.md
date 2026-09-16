# Zeer

**defName**: not vendored in this repo; lives only in the third-party donor mod
`mlie.starwarsanimalcollection` ("Star Wars Animal Collection (Continued)"),
which is ACTIVE in the mod list but whose install could not be located on
disk this pass (checked both the Steam Workshop content cache at
`294100/` and `.../RimWorld/Mods/` — see `PYRELANDS_CREATURE_RERENDER_1`
notes). No local ThingDef/PawnKindDef or sprite file exists to read.

**Provenance flag**: the task brief that requested this library entry
described Zeer as a "KOTOR-era creature." That does not match what
Wookieepedia actually has on file — the only "Zeer" creature article is a
*Star Wars Legends* species from the prequel-era Naboo video game *Star
Wars Episode I: The Gungan Frontier* (2000), unrelated to *Knights of the
Old Republic*. Documented here as found, not adjusted to fit the brief.

## Sourced text (Wookieepedia/Legends)
Zeer were a species of giraffe-like, non-sentient herd creatures native to
the northern temperate and subtropical regions of Naboo, later also used to
populate the moon Ohma-D'un and displayed for trade on Coruscant in the New
Republic era. Infobox stats: height ~15 feet, length ~9 feet. Distinctions:
tall, with two swiveling horns on the head "similar to that of a dwarf
bantha." They traveled in herds and grazed on leaves from the tops of tall
trees; described as relatively calm. Illegal poachers on Naboo killed many
zeer before the Rebellion era, sharply reducing the population, which began
recovering during the Galactic Civil War. First appearance: *Star Wars
Episode I: The Gungan Frontier* (Nintendo 64, 2000); sourced description
text comes from *The Wildlife of Star Wars: A Field Guide* (2001).

## Visual brief
Both candidate images are consistent with each other and with the "giraffe-
like" text. `wookieepedia_infobox.jpg` shows a full-body standing animal:
an unmistakable giraffe silhouette — long thin neck, long thin legs, a
small head atop the neck, and a long thin tail — rendered in a **tawny/tan
base coat with dark rust-brown tiger-style banding/striping** running across
the neck, shoulders, and legs (not giraffe-style blotches — true crosswise
stripes, closer to the "tiger-striped" convention this bestiary keeps
finding on Star Wars creature art, e.g. Anooba). `wookieepedia_exhibition.jpg`
is a closer head-and-neck crop of two zeer at a livestock exhibition, and is
the only image that shows the horns clearly: a pair of pale, curved,
backward-hooked horns rising and curling from the top of the head — thin
and swept back, not the thick ridged single horn seen on other bestiary
entries (e.g. Dalgo, Iriaz). This image also confirms the same tan/rust
banded coat pattern on the neck at closer range, and shows the animals
fitted with tack (a rope/lead line), consistent with domesticated livestock
display rather than a wild pose.

No donor mod screenshot could be obtained — `mlie.starwarsanimalcollection`
is not present anywhere on this machine's disk (Workshop cache or common
Mods folder), so there is no `donor_current_sprite.png` candidate for this
entry.

## Must show
- [ ] Long thin neck with a small head atop it (giraffe-like silhouette)
- [ ] Long thin legs and a long thin tail, in giraffe-like proportion — not stocky
- [ ] Tawny/tan base coat with dark rust-brown crosswise, tiger-style banding/striping on the neck, shoulders and legs — not giraffe-style blotches
- [ ] A pair of pale, thin, curved horns swept back from the top of the head — not a single thick ridged horn

## Engine limits
none known — no donor mod screenshot or sprite could be obtained at all (the donor mod is not present anywhere on this machine's disk), so there is nothing on disk to test against a rendering-pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Zeer/Legends (Wookieepedia article text,
  pulled via
  `starwars.fandom.com/api.php?action=parse&page=Zeer&prop=wikitext`,
  2026-09-13; the bare "Zeer" title resolves straight to this Legends
  article, confirming no current-canon version exists)
- https://static.wikia.nocookie.net/starwars/images/0/07/Zeer.jpg (species
  infobox image, full-body standing zeer)
- https://static.wikia.nocookie.net/starwars/images/f/f7/Zeer2.jpg ("Two
  zeer at the Coruscant Livestock Exchange and Exhibition," head/neck crop)

## Candidate images
- `wookieepedia_infobox.jpg` — Wookieepedia species-infobox art: full-body
  standing zeer, giraffe silhouette, tan coat with dark rust tiger-stripe
  banding, long thin neck/legs/tail
- `wookieepedia_exhibition.jpg` — closer crop of two zeer on lead lines at
  the Coruscant Livestock Exchange, the only image showing the pair of
  pale curled/hooked horns clearly, confirms the banded coat pattern at
  closer range

## ruling
