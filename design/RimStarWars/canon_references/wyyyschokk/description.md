# Wyyyschokk

**defName**: `Wyyyschokk` (bare, third-party — lives in `mlie.starwarsanimalcollection`,
patched by `src/RimStarWars/Shokk/Patches/RSW_Shokk_Wyyyschokk.xml`, packageId
`mandrake.rsw.shokk`)

## Sourced text (Wookieepedia)
### Canon — https://starwars.fandom.com/wiki/Wyyyschokk

Wyyyschokk were a species of gigantic spider that lived on Kashyyyk (jungle and forest), taller than 2 metres per the Bestiary. Highly intelligent and extremely hostile, they ensnared prey by casting a web-like enzyme from their mandibles from a distance, and often ambushed prey by dropping from the forest canopy or hiding underground, then crushed the prey's head in their mandibles. A notable subspecies was the Albino Wyyyschokk (also in *Star Wars Jedi: Fallen Order*). An adult could lay up to 1,000 eggs a year in extremely durable egg sacs of webbing, saliva and a secretion from lymphatic nodes under each leg; hatchlings took up to five days to eat out of the sac. At least 15% of Kashyyyk's forests were estimated covered in their webs, and Wookiee children were taught to defend against them from age three. First canon appearance: *Fallen Order* (2019); Legends origin earlier. The canon page gives no body colour.

### Legends — https://starwars.fandom.com/wiki/Wyyyschokk/Legends

Also called webweavers or Kashyyykian giant weavers; the most dangerous predator on Kashyyyk. Pack-hunting, tracked prey over a kilometre, immobilised victims with thick web strands and poison from upraised mandibles. Skin and hair grey, red, green or blue; eyes yellow, blue or red.

### Bloggathehutt — https://bloggathehutt.wordpress.com/2019/06/10/species-of-the-week-wyyyschokk/

Fan blog (not Lucasfilm; a short 'Species of the week' card, fetched 2026-10-17, verbatim-ish, chatter trimmed). It adds nothing beyond Wookieepedia beyond the blog author's notes; no contradiction with the canon text found.

> Designation: Non-sentient
> Homeworld: Kashyyyk
> Fandom: Star Wars
> Appearances: Jedi: Fallen Order
> Wyyyshokk are a large species of spider native to the wilds of Kashyyyk along with a number of other deadly species. They attack by shooting webbing at their victims then pounce on them to finish them off. They are a deadly threat even to enemies armed with blasters as they have thick hides.
> I really enjoyed watching the gameplay demo for Jedi: Fallen Order and reading the information about the assault on Kashyyyk. Seeing these creatures return from Legends to tangle with a Stormtrooper patrol then prove a significant threat to your Jedi main character made me really excited to play the game

## Visual brief — RULED (owner correction, 2026-09-13)
The owner's own lore images (comics/game art) show the real canon look:
- **Blue-grey body**
- **A bold yellow-orange cross marking on the abdomen** — the single most
  identifying feature; a render without it is not a Wyyyschokk
- **Spiky bristle tufts**
- **Blue-black legs**
- **Clustered black eyes**

Distinctive and vivid — not a generic brown hairy spider. The 2026-09-13
canon-brief agent's brown-spider render is the negative example this library
exists to prevent from recurring.
- **Bloggathehutt image (viewed 2026-10-17, `bloggathehutt_post_image.png`):** a wyyyschokk (Jedi: Fallen Order demo): spherical armoured abdomen with banded green-yellow plates, dark spider legs, glowing sensor spots, in jungle undergrowth. Fan-blog card image; compare against the existing Wookieepedia images before trusting any colour or proportion difference.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the `## ruling` below (owner visual correction 2026-09-13, confirmed 2026-09-14 on `wookieepedia_jfo_infobox.jpg`) and that image's caption.*
- [ ] BODY PLAN: a gigantic spider (taller than 2 m): a big rounded abdomen behind a head with mandibles, on long jointed clawed spider legs
- [ ] COLOUR LAYOUT: blue-grey body (not brown); blue-black legs; a bold yellow-orange cross marking down the centre of the abdomen as the brightest element; black bristle tufts; black eyes (owner ruling 2026-09-13: "blue-grey body, yellow-orange abdomen cross, spiky bristle tufts, blue-black legs, clustered black eyes")
- [ ] Bold yellow-orange cross marking on the abdomen (the single most identifying feature — a render without it is not a Wyyyschokk; the ruling: "a regen without the abdomen cross fails review")
- [ ] Spiky bristle tufts, around the rim of the abdomen
- [ ] Clustered black eyes (a tight cluster, roughly eight, above the mandibles)
- [ ] NEGATIVE: not a generic brown hairy spider (the 2026-09-13 brown-spider render is the named negative example), not a tarantula without the cross

## Engine limits
none known — no donor mod sprite could be obtained at all (creature art ships packed in Unity AssetBundles, not loose files), so there is nothing on disk to test against a rendering-pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Wyyyschokk (Wookieepedia — text pulled
  2026-09-13, underselling the visual; re-fetch for the full infobox image set)
- Owner's own lore image references (comics/game art) — not yet captured as
  files in this folder; see `Watch out` on the item.
- https://bloggathehutt.wordpress.com/2019/06/10/species-of-the-week-wyyyschokk/ (fan blog)

## Candidate images
- `wookieepedia_jfo_infobox.jpg` — Wookieepedia infobox render from *Star Wars
  Jedi: Fallen Order* (`Wyyyschokk-JFO.png`): a close-up render matching the
  ruled visual almost exactly — blue-grey rounded abdomen, a bold red-orange
  cross marking down the center, spiky black bristle tufts around the rim,
  blue-black clawed legs, and a tight cluster of ~8 black eyes above the
  mandibles. Strongest single confirmation of the ruled look.
- `official_art_fallenorder_concept.jpg` — official Respawn/Dark Horse
  concept art (via creativeuncut.com's Fallen Order gallery, credited
  Jean-Francois Rey): a sheet of six grayscale exploratory sketches (varying
  leg count/posture, some with a bulbous head-sac instead of a cross-marked
  abdomen) plus one colored final-direction painting at the bottom showing a
  yellow/gold body with a **red** (not yellow-orange) cross marking in a
  dark forest web setting — close to the ruled look but the cross reads more
  red than yellow-orange here, worth flagging as a minor candidate
  disagreement on the cross's exact hue.
- `wookieepedia_eggs.jpg` (`WyyyschokkEggs.png`) — a cluster of large
  leathery egg sacs in a web, tan/cream colored; no adult visible, included
  for egg-sac texture/color reference only.
- `wookieepedia_cocoonedstormy.jpg` (`CocoonedStormy.png`) — a stormtrooper
  wrapped in Wyyyschokk silk webbing; shows web color/texture (pale
  cream-white) but no clear adult body shot.

**Donor mod sprite not obtained**: `mlie.starwarsanimalcollection`'s current
1.6 release ships creature art packed inside Unity AssetBundles rather than
loose PNGs (confirmed via the mod's public GitHub mirror,
`github.com/emipa606/StarWarsAnimalCollection` — its `Textures/` folder holds
only an `UpdateInfo` subfolder), and no Steam Workshop preview screenshot
specifically labeled Wyyyschokk was found this pass. Revisit if the donor mod
is ever installed locally.
- `bloggathehutt_post_image.png` — FAN BLOG https://bloggathehutt.wordpress.com/2019/06/10/species-of-the-week-wyyyschokk/; post card image (not Lucasfilm).

## ruling
**RULED** (owner, 2026-09-13, verbatim visual correction — see Visual brief
above): blue-grey body, yellow-orange abdomen cross, spiky bristle tufts,
blue-black legs, clustered black eyes. This is the acceptance exemplar for
`CANON_CREATURE_REGEN_1` — a regen without the abdomen cross fails review.

**Owner confirmation, 2026-09-14** (review sheet): picked `wookieepedia_jfo_infobox.jpg` as the strongest match to the ruling above.
