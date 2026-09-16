# Zakkeg

**defName**: `Zakkeg` (third-party, mlie.starwarsanimalcollection, not
vendored — the mod's 1.6 release packs creature art inside Unity
AssetBundles rather than loose PNGs; see "donor art" note below)

## Sourced text (Wookieepedia)
Two separate Wookieepedia entries exist and they read very differently —
current canon has almost nothing, Legends has the full creature the task
brief describes:

- **Current canon** (`Zakkeg`): reduced to a figure of speech. The
  mercenary Saponza calls a heavily-fortified Tusken Raider warlord "a
  crafty Zakkeg," and a smuggler is described as "stubborn as a zakkeg, and
  twice as mean." The infobox is entirely blank — no size, color, habitat,
  or origin given in current canon.
- **Legends** (`Zakkeg/Legends`) — **this is the creature the task brief
  describes**: rare alpha-predators indigenous to **Dxun**, matching the
  brief's "Dxun (KOTOR-era, similar habitat to Boma)" note exactly. Huge
  armored quadrupeds, solitary and territorial, **reptilian class**, length
  greater than 4 meters, **4 powerful taloned legs**, **thick knobbed
  scales**. Carnivorous; preyed on cannoks, maalraas, and even bomas.
  Killing one was considered a mark of great honor among Mandalorians.
  First appeared in *Knights of the Old Republic II: The Sith Lords*
  (2004); later appeared in *Star Wars: The Old Republic* (including as a
  huntable creature and a Cartel Market mount/pet source), where a
  Mandalorian clan is noted to have hunted zakkegs regularly and used their
  hide for armor.
  - **Direct in-universe description** (Mandalorian guard captain, KOTOR
    II): *"It's a huge, red lizard that's built like a Baragwin battle
    tank. It has a hide so thick it might as well be durasteel plating."*
    — this is the single strongest color cue in the sourced text: **red**,
    not brown or black.

## Visual brief
Two candidate images, both game-rendered 3D models rather than illustration,
and they show a body-plan match but a color disagreement worth flagging:

- `wookieepedia_kotor2_juvenile.png` (captioned "A juvenile zakkeg," in-game
  render, KOTOR II) — a **rust-red/copper-brown** quadruped with a jagged
  spiked ridge running along the spine from head to tail, a low-slung
  reptilian toothy head with small yellow eyes, thick knobbed/bumpy hide,
  and stocky clawed legs. This is the closer color match to the in-universe
  "huge, red lizard" quote.
- `wookieepedia_swtor_adult.jpg` (in-game render, *The Old Republic*) — the
  same body plan at adult scale: spiked dorsal ridge, low reptilian head
  with visible fangs and small eyes, thick knobbed scales, four
  heavy-clawed legs, a tapered tail. Coloring here reads **dark
  brown-to-near-black**, noticeably darker/duller than the juvenile render
  and than the "red lizard" quote.

**Net read**: body plan is consistent and well-confirmed across both
sources and the text — a stegosaur-like reptilian quadruped predator with a
spiked dorsal ridge, thick knobbed/armored hide, a low toothy head, and four
heavy taloned legs, roughly the size of "a battle tank." Color is the one
open question: the sourced in-universe quote and the juvenile render both
point to **red/rust**, while the adult SWTOR render is darker
brown-black — plausibly a juvenile-vs-adult color shift (common in reptile
Wookieepedia analogues) rather than a contradiction, but not confirmed
either way. Favor red/rust as the primary color anchor since it is the only
one both an in-universe character quote AND an image agree on.

## Must show
- [ ] Stegosaur-like reptilian quadruped with a jagged spiked ridge running along the spine from head to tail
- [ ] Thick, knobbed/bumpy armored hide over the whole body
- [ ] Low-slung reptilian head with visible fangs/teeth and small eyes
- [ ] Four heavy, thick, clawed legs on a stocky body ("battle tank" scale)
- [ ] Rust-red/copper-brown as the primary colour anchor (a darker brown-black variant is attested but unconfirmed as a separate life stage)

## Engine limits
none known — no donor-mod sprite could be obtained at all (creature art ships packed in Unity AssetBundles, not loose files), so there is nothing on disk to test against a rendering-pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Zakkeg (current canon, wikitext pulled
  2026-09-13)
- https://starwars.fandom.com/wiki/Zakkeg/Legends (Legends — the Dxun
  predator matching the task brief; wikitext pulled 2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/3/30/Zakkeg.jpg (SWTOR
  adult render)
- https://static.wikia.nocookie.net/starwars/images/5/5b/JuvenileZakkeg.png
  (KOTOR II juvenile render)
- Donor mod `mlie.starwarsanimalcollection` — `About.xml` confirms
  packageId `Mlie.StarWarsAnimalCollection`, GitHub mirror
  `github.com/emipa606/StarWarsAnimalCollection`; its `Textures/` folder
  contains only an empty `UpdateInfo` subfolder (creature art ships packed
  in AssetBundles, not loose files) — same finding as the `pekopeko` and
  `wyyyschokk` passes. No workshop preview screenshot specifically labeled
  Zakkeg was located this pass.

## Candidate images
- `wookieepedia_kotor2_juvenile.png` — juvenile zakkeg, KOTOR II in-game
  render: rust-red/copper hide, spiked dorsal ridge, reptilian head.
  **Best color match to the sourced "red lizard" quote.**
- `wookieepedia_swtor_adult.jpg` — adult zakkeg, SWTOR in-game render: same
  spiked-ridge stegosaur-like body plan, but dark brown-to-black hide
  (darker than the juvenile render and the sourced color quote).
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — same
  AssetBundle-packaging finding as prior waves; revisit if the mod is ever
  installed locally or a labeled preview surfaces.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_kotor2_juvenile.png`
