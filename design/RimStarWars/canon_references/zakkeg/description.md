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
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**

**Animation-only canon — no realistic source found (searched: Wookieepedia pageimages Zakkeg and Zakkeg/Legends, catimages "Images of zakkegs"; only KOTOR II and SWTOR stylised game models exist).** The images below are animated/stylised; render this creature realistically anyway — real-world anatomy, materials and lighting, not the cartoon's flat shading or exaggerated proportions.

Two candidate images, both game-rendered 3D models rather than illustration,
and they show a body-plan match but a color disagreement worth flagging:

- `wookieepedia_kotor2_juvenile.png` (file `JuvenileZakkeg.png`, captioned
  "A juvenile zakkeg"; the wiki file page sources it to the 2020 SWTOR Cartel
  Market announcement, so it is a SWTOR pet render, NOT a KOTOR II render;
  the filename is historical) — a **rust-red/copper-brown** quadruped with a jagged
  spiked ridge running along the spine from head to tail, a low-slung
  reptilian toothy head with small yellow eyes, thick knobbed/bumpy hide,
  and stocky clawed legs. This is the closer color match to the in-universe
  "huge, red lizard" quote.
- `wookieepedia_swtor_adult.jpg` (file `Zakkeg.jpg`, the Legends infobox image;
  the wiki file page sources it to *Knights of the Old Republic II*, so it is
  the KOTOR II model, NOT SWTOR; the page does not call it an adult) — the
  same body plan: spiked dorsal ridge, low reptilian head
  with visible fangs and small eyes, thick knobbed scales, four
  heavy-clawed legs, a tapered tail. Coloring here reads **dark
  brown-to-near-black**, noticeably darker/duller than the juvenile render
  and than the "red lizard" quote.

**Net read**: body plan is consistent and well-confirmed across both
sources and the text — a stegosaur-like reptilian quadruped predator with a
spiked dorsal ridge, thick knobbed/armored hide, a low toothy head, and four
heavy taloned legs; Legends gives a length greater than 4 meters
(*Operation: Shadowpoint*; "built like a battle tank" is the guard captain's
simile, not a measurement). Color is the one open question: the KOTOR II quote
says red and the SWTOR pet render is rust-red, while the KOTOR II model image is
dark brown-black. No source states an age-based colour change, so none should
be assumed. All of this is Legends (appearance reference only); canon
(`Zakkeg`) holds only the proverbial mentions in *Star Wars: Commander* and a
Liana Kor Databank entry.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the Legends text, both game renders as described in the visual brief, and the `## ruling` below (juvenile render chosen).*
- [ ] BODY PLAN: a huge, low-slung, stocky reptilian quadruped ("built like a Baragwin battle tank"), stegosaur-like, on four heavy, thick taloned/clawed legs; low head carried forward; a tapered tail
- [ ] COLOUR LAYOUT: rust-red/copper-brown as the primary colour over the whole body (owner ruling 2026-09-14 chose `wookieepedia_kotor2_juvenile.png`, the rust-red render, matching the sourced "huge, red lizard"); a darker brown-black variant is attested but unconfirmed as a separate life stage
- [ ] A jagged spiked ridge running along the spine from head to tail
- [ ] Thick, knobbed/bumpy armoured hide over the whole body
- [ ] Low-slung reptilian head with visible fangs/teeth and small eyes
- [ ] Realistic rendering: natural knobbly armoured hide under natural daylight, no low-poly or stylised-game shading (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using.")
- [ ] NEGATIVE: not a smooth-skinned lizard or crocodile (no smooth scales, no missing dorsal spikes), not a slim long-legged predator; not a low-poly game model

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
