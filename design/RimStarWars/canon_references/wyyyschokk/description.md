# Wyyyschokk

**defName**: `Wyyyschokk` (bare, third-party — lives in `mlie.starwarsanimalcollection`,
patched by `src/RimStarWars/Shokk/Patches/RSW_Shokk_Wyyyschokk.xml`, packageId
`mandrake.rsw.shokk`)

## Sourced text (Wookieepedia)
A large arachnid predator native to Kashyyyk's Shadowlands. Canon Wookieepedia
prose (as pulled by the 2026-09-13 canon-brief pass) described it as
"near-black to dark reddish-brown chitin" — **this text description undersold
the real visual canon and is the worked example for why text alone fails; see
below.**

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

## Source URLs
- https://starwars.fandom.com/wiki/Wyyyschokk (Wookieepedia — text pulled
  2026-09-13, underselling the visual; re-fetch for the full infobox image set)
- Owner's own lore image references (comics/game art) — not yet captured as
  files in this folder; see `Watch out` on the item.

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

## ruling
**RULED** (owner, 2026-09-13, verbatim visual correction — see Visual brief
above): blue-grey body, yellow-orange abdomen cross, spiky bristle tufts,
blue-black legs, clustered black eyes. This is the acceptance exemplar for
`CANON_CREATURE_REGEN_1` — a regen without the abdomen cross fails review.

**Owner confirmation, 2026-09-14** (review sheet): picked `wookieepedia_jfo_infobox.jpg` as the strongest match to the ruling above.
