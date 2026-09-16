# Boma

**defName**: `RSW_Boma` (SWBestiary, texture folder `Boma`)

## Sourced text (Wookieepedia)
Bomas are **Legends** ravenous beasts native to **Onderon and its moon
Dxun** (KOTOR era, ~4000 BBY). Infobox: **skin color Green**, class
"Reptile," habitat jungle, diet carnivore. Distinctions: "Squat face with 2
horns and 2 tusks," "thick scales."

"A species of monstrous, wingless beasts that had green reptilian hides,
long tails, four horns, dagger-like claws, and savage teeth."

"Although most bomas were generally small, there were some that were
extremely large in size, as experienced by the Jedi Exile and her
companions while exploring [Dxun]." Dangerous predators known to kill
Mandalorians, themselves preyed on by zakkeg beasts and drexl. Also
appeared as tamed/ridden beasts — used by Jedi Knight Tott Doneeta (Force
animal-bond) to breach a citadel, and depicted as a large mount carrying a
howdah/canopy with multiple riders in *Empire's End* (11 ABY, set on
Onderon).

## Visual brief
The two candidate images show what reads as **two different "sizes" of
boma described in the text** ("most bomas were generally small... some
extremely large"), and they disagree sharply on scale/role but agree on
core coloring:
- The Databank-style render shows a **squat, monstrous, green** reptilian
  predator: bulldog/toad-like stance, a wide horned-and-tusked face, thick
  wrinkled scaled hide, short powerful clawed legs, a moderate tail —
  matches the infobox's "squat face, 2 horns, 2 tusks, thick scales" almost
  exactly. This is the small/wild predatory boma.
- The comic panel (*Empire's End*) shows an entirely different-scale scene:
  a large **blue-grey** quadruped beast of burden carrying a canopied
  howdah with multiple passengers (echoing the "extremely large" bomas used
  as mounts) — long tail, blunt horned snout, thick legs, more Triceratops/
  rancor-adjacent in proportion than the squat predator. Coloring here
  reads blue-grey/tan rather than green, a disagreement with the infobox's
  stated green skin color and with the first image.

Our own donor sprite (`donor_current_sprite.png`) is **green**, low and
squat with a stocky tail and blunt snouted head — this matches the small
predatory-boma reading (image 1 and the infobox skincolor) well, and does
not attempt the large-mount variant seen in image 2.

## Must show
- [ ] Squat, monstrous body with a wide face bearing 2 horns and 2 tusks
- [ ] Thick, wrinkled, scaled hide reading green
- [ ] Short, powerful, clawed legs
- [ ] Low, bulldog/toad-like stance
- [ ] Moderate-length tail

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Boma (Wookieepedia, text pulled via
  MediaWiki API `action=parse` 2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/0/02/Boma_Beast.jpg (File:Boma_Beast.jpg)
- https://static.wikia.nocookie.net/starwars/images/1/12/BomaEmpireEnd.jpg (File:BomaEmpireEnd.jpg)

## Candidate images
- `boma_wookieepedia_1.jpg` — Databank-style render (File:Boma_Beast.jpg):
  squat green monstrous predator, wide tusked/horned face, thick wrinkled
  hide, short clawed legs. Matches the infobox text closely; reads as the
  "small" boma variant.
- `boma_wookieepedia_2.jpg` — comic panel (File:BomaEmpireEnd.jpg, *Empire's
  End* 2, set on Onderon 11 ABY): a large blue-grey quadruped mount
  carrying a canopied howdah with riders — reads as the "extremely large"
  ridden boma variant the text separately mentions; disagrees with image 1
  and the infobox on color (blue-grey vs. green).
- `donor_current_sprite.png` — our own SWBestiary donor sprite (`swanimals/
  Boma/Boma_east.png`): green, squat, blunt-snouted quadruped — matches
  the small predatory-boma reading (image 1 + infobox skincolor).

## ruling
**RULED** (owner, 2026-09-13, review sheet): `boma_wookieepedia_1.jpg`
