# PekoPeko

**defName**: `PekoPeko` (bare, third-party — lives in
`mlie.starwarsanimalcollection`, NOT vendored in this repo; as of the current
1.6 release of the donor mod the creature textures ship packed inside Unity
AssetBundles rather than as loose PNGs, so no per-creature sprite could be
pulled from the donor's public GitHub mirror either — see "donor art" note
below)

## Sourced text (Wookieepedia)
Two separate Wookieepedia entries exist and they read differently:

- **Current canon** (`Peko-peko`, sourced to *Star Wars Battlefront II* and
  *Star Wars Bestiary, Vol. 1*): flying creatures of the Naboo swamps. **Blue
  feathering**, a long tail, clawed wings, a prominent beak used to crack
  nuts and peel fruit; mate for life, two chicks per litter. First seen (a
  pair flying over the Gungan Sacred Place) in *The Phantom Menace* (32 BBY).
  A painting of Queen Padmé Amidala holding a peko-peko hangs in the Theed
  Royal Palace per *Battlefront II*. The canon page's behind-the-scenes notes
  (citing the old Databank) say concept artist Terryl Whitlatch developed the
  coloring from a real peacock and hyacinth macaw, the beak was designed to
  crack coconut-sized nuts, and the wing claws resemble the hoatzin's
  (https://starwars.fandom.com/wiki/Peko-peko).
- **Legacy/Legends** (`Peko-peko/Legends`): large, strong "reptavians" native
  to the Gungan swamps of Naboo (a second breed on Nal Hutta), length ~3
  meters (the 3 m figure is Legends only). Coloring: **blue and yellow skin, indigo-sapphire feathers**.
  Clawed wings for climbing in the
  tree canopy, a powerful beak that can crush even the hardest nuts, fairly
  toxic skin/feathers (causes stomach pain, vomiting, occasional death in
  predators, though not universally). Preyed on by tusk cats; ate kaadu eggs.
  Used as a mount in *Star Wars Galaxies* — a mutated "Toxic peko-peko"
  variant bred by Cornelius Evazan was sold as a loot-card mount.

**Both canon tiers agree on the core fact that matters for art: this is a
blue, peacock/macaw-derived bird, not a drab or reptilian-brown one.**

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** Removed: `swg_toxic_pekopeko_mount.jpg` (a low-detail *Star Wars Galaxies* UI screenshot of the red mutant "Toxic peko-peko" mount). No live-action peko-peko exists on Wookieepedia (searched: "Images of peko-pekos"; its realistic-labelled files are Padmé film scenes with no bird in frame; the rest are Gungan Frontier game frames). The three remaining images are realistic painted/rendered art and agree on the look.

- `wookieepedia_fieldguide.jpg` — **the owner-ruled target ("Follow #3 closely").** Terryl Whitlatch's realistic naturalist plate from *The Wildlife of Star Wars: A Field Guide*: the bird perched on a branch, wings spread, **peacock/slate-blue wing and tail plumage** with pale edging, very long trailing tail feathers fringed in gold/olive, a yellow throat patch, a long curved neck and a long hooked, crested beak/skull with a dark crest at the back of the head.
- `wookieepedia_battlefront2_painting.jpg` — the in-universe Theed palace painting (*Battlefront II*, canon), realistic oil-painting style: the same bird on Padmé's arm, peacock-blue wings, long trailing tail with pale gold edging, a small yellow/gold head, raptor-like curved beak. Confirms the colour.
- `wookieepedia_infobox.jpg` — the Legends infobox `Peko-peko.jpg` (Databank original): an untextured grey 3D model, side view. Body plan only — long S-curved neck, elongated beak/skull with a knob crest, long wings, long tail. Carries **no colour**; do not read "grey" as canon.

**Net read: render blue**, as a real bird with real feather structure: peacock/macaw-style plumage, very long trailing tail feathers, clawed wings, a strong hooked nut-cracking beak. The red-orange Toxic mutant is not part of the target.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the field-guide plate per the `## ruling` below (owner ruling 2026-09-14: "Follow #3 closely."), the Battlefront II painting, and the owner ruling 2026-10-08 in the visual brief.*
- [ ] BODY PLAN: a real bird with real feather structure: a long S-curved neck, an elongated hooked beak/skull with a crest at the back of the head, long wings with claws, foldable close to the body, and very long trailing tail feathers — as in the field-guide plate (owner ruling 2026-09-14: "Follow #3 closely.")
- [ ] COLOUR LAYOUT: peacock/slate-blue wing and tail plumage with pale edging — not drab, tan, grey or reddish-orange; a yellow/gold patch at the head or throat; tail feathers edged pale gold/olive; dark crest at the back of the head
- [ ] Very long trailing tail feathers with pale gold edging
- [ ] Strong hooked, nut-cracking beak
- [ ] Realistic rendering: natural layered feather texture and lighting, no outlines, no cartoon shading (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using.")
- [ ] NEGATIVE: not the red-orange "Toxic peko-peko" mutant, not the untextured grey 3D model colour, not a drab or reptilian-brown creature

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Peko-peko (current canon page, wikitext
  pulled 2026-09-13)
- https://starwars.fandom.com/wiki/Peko-peko/Legends (Legends page, wikitext
  pulled 2026-09-13)
- https://starwars.fandom.com/wiki/Toxic_peko-peko (mutated SWG variant)
- https://static.wikia.nocookie.net/starwars/images/2/22/Amidala_painting-BF2.jpg (Battlefront II in-universe painting, current canon)
- https://static.wikia.nocookie.net/starwars/images/c/c5/Pekopeko-woswfg.jpg ("Wildlife of Star Wars: A Field Guide" painted plate)
- https://static.wikia.nocookie.net/starwars/images/8/8d/Peko-peko.jpg (Wookieepedia Legends infobox, grey 3D model render)
- Donor mod `mlie.starwarsanimalcollection` (Steam Workshop, current 1.6
  release id 3497316713 and legacy id 2903582351) — attempted to pull a
  preview screenshot or loose texture via the mod's public GitHub mirror
  (`github.com/emipa606/StarWarsAnimalCollection`); the repo's `Textures/`
  folder only contains an `UpdateInfo` subfolder (creature art now ships
  packed in `AssetBundles/`, not as loose files), and the workshop preview
  image search did not surface a screenshot specifically labeled PekoPeko.
  **No donor-mod sprite obtained this pass** — see rule below.

## Candidate images
- `wookieepedia_fieldguide.jpg` — *The Wildlife of Star Wars: A Field Guide* (Terryl Whitlatch), realistic naturalist painting; file `Pekopeko-woswfg.jpg` — https://static.wikia.nocookie.net/starwars/images/c/c5/Pekopeko-woswfg.jpg — **owner-ruled target.**
- `wookieepedia_battlefront2_painting.jpg` — *Battlefront II* in-universe Theed painting of Padmé holding a peko-peko (canon), realistic painting; file `Amidala_painting-BF2.jpg` — https://static.wikia.nocookie.net/starwars/images/2/22/Amidala_painting-BF2.jpg
- `wookieepedia_infobox.jpg` — Legends infobox, Databank original untextured grey 3D model render (body plan only); file `Peko-peko.jpg` — https://static.wikia.nocookie.net/starwars/images/8/8d/Peko-peko.jpg
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — its current release packs art in AssetBundles rather than loose textures, and no labeled workshop preview screenshot was found.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_fieldguide.jpg`

> "Follow #3 closely."
