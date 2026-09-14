# Shiro

**defName**: `Shiro` (third-party, mlie.starwarsanimalcollection, not vendored — see Watch out)

## Sourced text (Wookieepedia)
Search for "Shiro" on Wookieepedia is noisy — results include `Shiro-trap` (a
symbiotic plant/animal pairing, not a separate species), `Unidentified small
sentient creature`, `aliens.fandom.com`'s own separate "Shiro" entry, and
several near-miss titles (`Shrikarai`, `Shryo`, `Shirro`, `Ssori`). The actual
species page is `https://starwars.fandom.com/wiki/Shiro` (pageid 589183),
confirmed as the animal species by its `{{Species}}` infobox and its
`Category:Creatures of Naboo` tag. That page carries both a canon stub and a
`/Legends` continuity page (`https://starwars.fandom.com/wiki/Shiro/Legends`,
pageid 58526) — this is the standard Wookieepedia split for an article with
both continuities, not two different creatures. I ruled out
`aliens.fandom.com/wiki/Shiro` (a fan-run wiki, not Wookieepedia/canon
Lucasfilm-licensed source — not used here) and the "Unidentified small
sentient creature" page (a different, unrelated entity that only turned up
because of shared search terms).

**Canon page (Shiro)**: Shiro were a turtle-like species found on Naboo.
Skin color is recorded in the infobox as green, sourced to the 2015 video
game *Disney Infinity 3.0* — this is also their first canon appearance. The
species originally appeared earlier in Legends, in the 1999 video game
*Star Wars Episode I: The Gungan Frontier*. The canon-page text itself is
very thin (one sentence) — the infobox art (`File:ShiroDisneyInfinity.png`)
is the primary canon visual source.

**Legends page (Shiro/Legends)**: much richer description. Shiros were
hard-shelled, benign, slow-moving reptiles (class: Reptile, non-sentient,
omnivorous) native to the Gungan Swamps of Naboo. Their main defense was
retracting head, legs and tail into a spiny/ridged shell. They fed on
mintri, zaela, grahn vine, chak-root, and occasional mud-dwelling crustaceans
and mollusks, and were popular with Gungan cooks. Notably, Shiros would roll
in mud and collect dirt and seeds between their shell ridges; Tooke-trap
plants would grow in these "soil pockets," forming a symbiotic pairing
nicknamed a "Shiro-trap" — the plant camouflaged the Shiro from its main
predator (the saw-toothed grank, which can crush shells), and the Shiro gave
the plant mobility. This confirms the task's note: **Shiro-trap is the
name for a camouflaged/symbiotic Shiro, not a different species.**
Source cited throughout: *The Wildlife of Star Wars: A Field Guide* (2001).

## Visual brief
Four images were retrieved, and they show real disagreement:

- `shirodisneyinfinity.png` (the canon infobox art, *Disney Infinity 3.0*) is
  a small, stylized, cartoonish render — a rounded green creature on a
  low-poly Naboo-swamp background. It reads as green-skinned as the infobox
  text states, but is a low-detail toy/game-art style rather than a
  naturalistic reference — body plan is hard to read precisely (chibi
  proportions), though the turtle-like rounded-shell silhouette is visible.
- `shirotrap_legends.jpg` and `shirotrap_retracted_legends.jpg` (both
  Legends-era, captioned "a Shiro-trap retracted into its shell") show the
  animal fully withdrawn — from these alone you mostly see a mottled,
  earth-toned, dirt-and-plant-covered shell mass, consistent with the "rolls
  in mud, collects seeds in shell ridges" text. Because the plant/soil
  disguise is the whole point of a Shiro-trap, these images are **not a
  clean read of the animal's own skin/shell color** — they show it
  deliberately camouflaged.
- `shiros_group_legends.jpg` (captioned as the general Legends infobox image,
  file `Shiros.jpg`, showing multiple individuals) is the best like-for-like
  match to the text: a group of hard-shelled, dome-backed reptiles with
  ridged/spiny shells in duller brown-green earth tones, resting in a muddy
  swamp setting — consistent with "hard-shelled... native to the Gungan
  Swamps," "rolled in mud," omnivorous swamp reptile.

**Disagreement**: the canon *Disney Infinity 3.0* art is a bright, clean
green cartoon creature; the Legends reference images (uncamouflaged group
shot) read as duller, mud-toned brown-green — but note the Legends text
itself explicitly says the animals accumulate mud and camouflage, so a
"clean" green Shiro may simply not appear undirtied in any Legends art.
**Treat the canon infobox image (`shirodisneyinfinity.png`) as the color
anchor** (it is the current, non-Legends canon source, and its green skin
color is also independently stated in the infobox text, not just visually
inferred) — but use the Legends group shot (`shiros_group_legends.jpg`) as
the anchor for **body plan and shell texture** (hard ridged/spiny dome
shell, stubby retractable head/legs/tail, turtle-like proportions), since
the canon art is too low-detail/stylized to read shell texture from.

## Watch out
No local donor sprite exists: the RimWorld mod this defName comes from,
`mlie.starwarsanimalcollection` ("Star Wars Animal Collection", 1.6 release),
is not installed or vendored anywhere in this repo, and its 1.6 build packs
creature art inside Unity AssetBundles rather than loose PNGs, so there is no
extractable donor sprite file. I checked the mod's Steam Workshop page
(`https://steamcommunity.com/sharedfiles/filedetails?id=3497316713`, the 1.6
"Star Wars Animal Collection (Continued)" listing) for a substitute
screenshot. The page's full animal roster list does include both "Shiro" and
"Shiro-Trap" by name, confirming the mod ships this creature — but the only
actual screenshot I could extract from the page (its main preview/header
image) is a generic collage advertising a different subset of animals
("Krayt Dragon, Rancor, Acklay, Reek, Nexu, Bantha, Dewback, Tauntaun, Nerf,
Gizka") with no Shiro-specific screenshot and no per-creature labeling on the
collage art, so **I did not save it** — I could not confirm which (if any)
figure in that collage is meant to be a Shiro, and saving an unlabeled guess
would risk exactly the kind of fabrication this library exists to prevent.
**No donor sprite was obtainable this pass.**

## Source URLs
- https://starwars.fandom.com/wiki/Shiro (canon article + infobox, pulled via
  `starwars.fandom.com/api.php?action=parse&page=Shiro&prop=wikitext`,
  2026-09-13)
- https://starwars.fandom.com/wiki/Shiro/Legends (Legends article, pulled via
  the same API pattern with `page=Shiro/Legends`, 2026-09-13)
- https://starwars.fandom.com/wiki/Shiro-trap (Legends "Shiro-trap" symbiosis
  article, confirms Shiro-trap = camouflaged Shiro, not a separate species)
- https://static.wikia.nocookie.net/starwars/images/1/17/ShiroDisneyInfinity.png (canon infobox art, *Disney Infinity 3.0*)
- https://static.wikia.nocookie.net/starwars/images/d/df/Shiro-trap.jpg (Legends, Shiro-trap camouflaged/retracted)
- https://static.wikia.nocookie.net/starwars/images/4/42/Shiro-trap_2.jpg (Legends, Shiro-trap retracted into shell, close-up)
- https://static.wikia.nocookie.net/starwars/images/f/fd/Shiros.jpg (Legends infobox art, group of Shiros)
- https://steamcommunity.com/sharedfiles/filedetails/?id=3497316713 (donor mod's Steam Workshop page, `mlie.starwarsanimalcollection` 1.6 — roster list confirms "Shiro" and "Shiro-Trap" are both included; no creature-specific screenshot found)

## Candidate images
- `shirodisneyinfinity.png` — canon infobox art (*Disney Infinity 3.0*), small stylized green creature, low-poly Naboo swamp backdrop — treat as the color anchor (green skin, per infobox text)
- `shiros_group_legends.jpg` — Legends infobox art, a group of Shiros in a muddy swamp setting, hard ridged/spiny dome shells, duller brown-green tones — treat as the body-plan/shell-texture anchor
- `shirotrap_legends.jpg` — Legends "Shiro-trap" image, animal camouflaged/retracted under plant and mud cover, not a clean skin-color read
- `shirotrap_retracted_legends.jpg` — Legends "Shiro-trap" close-up, fully withdrawn into shell, same camouflage caveat

## ruling
(empty — owner has not reviewed this creature yet)
