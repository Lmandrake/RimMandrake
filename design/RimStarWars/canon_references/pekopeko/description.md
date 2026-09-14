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
  Royal Palace per *Battlefront II*.
- **Legacy/Legends** (`Peko-peko/Legends`): large, strong "reptavians" native
  to the Gungan swamps of Naboo (a second breed on Nal Hutta), length ~3
  meters. Coloring: **blue and yellow skin, indigo-sapphire feathers** —
  concept artist Terryl Whitlatch developed it from a real-world peacock and
  a hyacinth macaw. Clawed wings (hoatzin-style) for climbing in the
  tree canopy, a powerful beak that can crush coconut-sized nuts, fairly
  toxic skin/feathers (causes stomach pain, vomiting, occasional death in
  predators, though not universally). Preyed on by tusk cats; ate kaadu eggs.
  Used as a mount in *Star Wars Galaxies* — a mutated "Toxic peko-peko"
  variant bred by Cornelius Evazan was sold as a loot-card mount.

**Both canon tiers agree on the core fact that matters for art: this is a
blue, peacock/macaw-derived bird, not a drab or reptilian-brown one.**

## Visual brief
This is a second text-vs-image mismatch case, same shape as the Wyyyschokk
one this library exists to catch — most of the easily-found candidate images
do NOT show the blue coloring the text insists on, and only one candidate
actually confirms it:

- `wookieepedia_battlefront2_painting.jpg` — **the one candidate that
  matches the sourced text.** The in-universe Theed palace painting (current
  canon, *Battlefront II*) shows the peko-peko perched on Padmé's arm with
  unmistakable **peacock-blue wing and tail plumage**, a small yellow/gold
  head crest, long trailing tail feathers with pale gold edging, and a
  raptor-like curved beak. This is the strongest single confirmation of the
  "peacock + macaw" description and should be treated as the visual anchor.
- `wookieepedia_fieldguide.jpg` — an unlit gray 3D model/render (body plan
  only: long S-curved neck, elongated toothy-looking beak/skull, folded
  wings, long tail) — confirms silhouette and beak shape but carries **no
  color information at all**; do not read "gray" as canon.
- `wookieepedia_infobox.jpg` — a small flat cartoon icon in tan/khaki/gold
  with a bony reptilian-looking head; this reads as a generic wiki
  species-icon illustration rather than accurate canon color and visibly
  UNDERSELLS the blue plumage the text describes — exactly the failure mode
  this library exists to catch. Keep it only as a cautionary example, not a
  reference to render from.
- `swg_toxic_pekopeko_mount.jpg` — in-game screenshot from *Star Wars
  Galaxies* of the mutated "Toxic peko-peko" mount: reddish/rust-orange
  plumage on a winged reptavian body. Per the source text this is an
  explicitly MUTATED variant (bred by an outlaw for toxin/aggression), so its
  red-orange color is not representative of a baseline peko-peko — it is
  useful for body plan (wings, clawed feet, elongated beak) but the color
  should be disregarded for a baseline render.

**Net read: render blue** (`wookieepedia_battlefront2_painting.jpg` is the
target), peacock/macaw-style plumage, long trailing tail feathers, clawed
wings, a strong hooked/nut-cracking beak. The gray model gives the cleanest
body-plan silhouette. The tan icon and the red mutant screenshot are both
off-canon for color and should not be used as color references.

## Source URLs
- https://starwars.fandom.com/wiki/Peko-peko (current canon page, wikitext
  pulled 2026-09-13)
- https://starwars.fandom.com/wiki/Peko-peko/Legends (Legends page, wikitext
  pulled 2026-09-13)
- https://starwars.fandom.com/wiki/Toxic_peko-peko (mutated SWG variant)
- https://static.wikia.nocookie.net/starwars/images/2/22/Amidala_painting-BF2.jpg (Battlefront II in-universe painting, current canon)
- https://static.wikia.nocookie.net/starwars/images/c/c5/Pekopeko-woswfg.jpg ("Wildlife of Star Wars: A Field Guide" model render)
- https://static.wikia.nocookie.net/starwars/images/8/8d/Peko-peko.jpg (Wookieepedia infobox icon)
- https://static.wikia.nocookie.net/swg/images/a/a2/Toxic_Peko-Peko_Mount.jpg (Star Wars Galaxies in-game mount screenshot)
- Donor mod `mlie.starwarsanimalcollection` (Steam Workshop, current 1.6
  release id 3497316713 and legacy id 2903582351) — attempted to pull a
  preview screenshot or loose texture via the mod's public GitHub mirror
  (`github.com/emipa606/StarWarsAnimalCollection`); the repo's `Textures/`
  folder only contains an `UpdateInfo` subfolder (creature art now ships
  packed in `AssetBundles/`, not as loose files), and the workshop preview
  image search did not surface a screenshot specifically labeled PekoPeko.
  **No donor-mod sprite obtained this pass** — see rule below.

## Candidate images
- `wookieepedia_battlefront2_painting.jpg` — Theed palace painting of Padmé
  holding a peko-peko (*Battlefront II*, current canon): blue peacock-style
  plumage, gold head crest, trailing tail feathers. **Best color reference.**
- `wookieepedia_fieldguide.jpg` — unlit gray 3D model render from "The
  Wildlife of Star Wars: A Field Guide": body plan / silhouette only, no
  color signal.
- `wookieepedia_infobox.jpg` — small flat wiki icon, tan/khaki/gold coloring;
  undersells the canon blue plumage, kept as a cautionary example.
- `swg_toxic_pekopeko_mount.jpg` — *Star Wars Galaxies* in-game screenshot of
  the mutated "Toxic peko-peko" mount: reddish-orange plumage (off-canon
  color, mutant variant only, useful for body plan/wings).
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — the
  mod is not present on this machine, its current release packs art in
  AssetBundles rather than loose textures, and no labeled workshop preview
  screenshot was found this pass. Revisit if the mod is ever installed
  locally or a labeled preview surfaces.

## ruling
(empty — owner has not reviewed this creature yet)
