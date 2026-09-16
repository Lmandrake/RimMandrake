# Quarren

**defName**: `RSW_RimMandrakeQuarren` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_DeepwaterCompact: A` — abundant, alongside Mon Calamari and
Nautolan. `04_factions.md` faction 7 makes this politically loaded: *"the Balance
is a Mon Calamari doctrine the Quarren are required to hold"* — Quarren and Mon
Calamari share both a homeworld and a faction, so the two must be visually
**distinguishable at a glance** in the same raid group.

## Sourced text (Wookieepedia)
The Quarren were a **bipedal squid-like species** native to the aquatic world **Mon
Cala**, which they share with the Mon Calamari. Infobox: skin colour orange, pale,
purple, pink, salmon, tan, green; **eye colour turquoise**; habitat aquatic;
distinctions "four tentacles protruding from jaw; finned or suction-cup tipped
fingers; ability to spit ink in defense". 🔴 **No height, mass or lifespan is
given — do not supply one.**

**Appearance.** Four facial tentacles which protruded from their lower jaw. A pair
of deep turquoise eyes, **finned hands with suction-tipped fingers**, and **small
tusks on their mouth**. 🔑 **In the two long protrusions that extended from either
side of their faces, Quarren had gill-like structures that were actually hearing
organs** — the side flaps are ears, not gills.

**Unusual abilities — the ink is the headline and it has canonical detail.**
- 🔑 **Capable of spitting clouds of black ink as a defensive measure in combat.**
- 🔴 **Such ink could also be released from a Quarren's body when cut open at the
  mid-section by a lightsaber, a mortal act** — i.e. an ink-burst death, which is a
  usable and very specific gore detail.
- **Quarren would also release ink in their sleep during nightmares.**
- **Natural swimmers, most comfortable underwater, preferring to be immersed in
  liquid** — while also bipedal beings that could walk and sit upright.
- 🔑 **Any atmosphere without humidity could be bad for a Quarren's skin and nasal
  passages**, so off-world Quarren turned to products like **moruga nut oil** and
  took **extremely hot showers**. On a desert world this is a strong mechanical
  hook and it matches the Compact's canon leash ("wardens dehydrate off-water and
  both of you know it").
- **The Quarren and Mon Calamari shared the capability of sustaining cybernetic
  modifications**, and a **Quarren/Mon Calamari hybrid existed** during or prior to
  146 BBY.

**Culture/dress.** Similar to the Mon Calamari, **the Quarren typically wore
clothing that covered most of their body, though left their heads unadorned.**
While Quarrenese was their native language, they could also speak fluent Galactic
Basic Standard.

## Visual brief
The reference image is three Quarren in costume side by side, and it corrects the
prose in two places.

- 🔴 **"Finned or suction-cup tipped fingers" is contradicted by the images, and the
  images win.** All three individuals have **long, pointed, pale claw-like nails**
  extending well past the fingertips — conspicuously long talons, not suction pads.
  Nothing in the reference resembles a sucker. Trust the images on the hands: **long
  pale pointed nails.** (The suction/fin description may be a Legends-era or
  underwater-specific reading; it is not what the canonical costume shows.)
- 🔴 **The side "protrusions" are far more prominent than the prose implies, and
  they are the silhouette.** The text buries them in a clause about hearing organs.
  In the images they are **two large, wide, leaf-shaped fins projecting horizontally
  outward and slightly back from the sides of the head** — as wide as the head
  itself, making the head read as a broad triangle. At thumbnail size these ear-fins
  are what says "Quarren", more than the tentacles.
- **The four jaw tentacles hang down from below the mouth** like a thick, curling
  beard, reaching to about the collarbone, tapering and independently curved. Thick,
  fleshy, not thread-like.
- **The cranium is a tall smooth dome coming to a rounded point at the crown** —
  bald, high, no ridges. This is the feature most easily confused with the Mon
  Calamari's "high-domed head"; the distinguisher is that the Quarren dome is
  *narrow and peaked* while the ear-fins spread wide below it.
- **Small eyes set close together and high on the face** — much smaller than a Mon
  Calamari's. 🔴 **The infobox "turquoise" is not legible in the reference images**,
  where the eyes read as small and dark. Treat turquoise as sourced-but-not-visually-
  confirmed here.
- **Two small upward tusks at the mouth**, visible between the tentacles.
- **Colour: mottled tan / ochre / pinkish-brown**, with darker mottling in the
  creases and on the tentacles. 🔴 The colour list's "orange" and "purple" are NOT
  what the reference shows; **tan and salmon are the accurate entries.** A saturated
  orange or purple Quarren would be wrong for the canonical look.
- **Dress is heavy, layered and formal — robes.** In the reference, a crimson robe
  with a grey knitted tabard, a tan-grey coat, and a red robe with black
  under-sleeves. This matches the text ("clothing that covered most of their body,
  heads unadorned") and is a genuinely useful apparel note: Quarren are robed
  functionaries, not bare-chested aquatics.

**donor_current_sprite.png is partial evidence, and one of the better donor heads.**
The copied file is `SWX/Pawn/HeadType/quarren/Male_Egghead_south.png` — a
**greyscale mask**, correct and expected for a RimWorld humanlike head (the game
tints it from the skin-colour gene, so its lack of colour is not a defect; the hue
findings above belong on the gene). Its silhouette is a tall smooth dome, which
matches the peaked cranium well. Verified from the xenotype's gene list, what IS
wired: `RSW_QuarrenHead`, `Hair_BaldOnly` (correct for this species),
`Body_Standard`, `Skin_Melanin3`, `RSW_Skin_PaleOrange` and `RSW_Skin_DarkGreen`.
Additional Quarren art exists on disk and is the right art —
`SWX/Pawn/HeadAttachments/quarren/squidmouth_{south,east,north}.png` (the jaw
tentacles) and `earfins_{south,east,north}.png` (the ear-fins) — so both defining
features have textures. **A later pass should verify which genes consume
`squidmouth` and `earfins` and whether those genes are in the Quarren xenotype's
list; this entry did not check that specific wiring, and given the confirmed orphan
found for the Nikto facespines it should not be assumed.** Nothing on disk supplies
the long pointed nails.

## Must show
- [ ] Long, pointed, pale claw-like nails extending well past the fingertips — not suction-cup tips
- [ ] Two large, wide, leaf-shaped ear-fins projecting horizontally outward and slightly back from the sides of the head, as wide as the head itself
- [ ] Four thick, fleshy jaw tentacles hanging from below the mouth like a curling beard, reaching to about the collarbone
- [ ] A tall, smooth cranial dome coming to a rounded point at the crown — narrow and peaked, distinct from the Mon Calamari's broader dome
- [ ] Small eyes set close together and high on the face, much smaller than a Mon Calamari's
- [ ] Mottled tan/ochre/pinkish-brown skin — not the infobox's saturated orange or purple

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Quarren (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Quarren&format=json&prop=wikitext`,
  40,080 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/1/15/The_Quarren.png (File:The_Quarren.png, the infobox image → wookieepedia_infobox_three_quarren.jpg)
- https://static.wikia.nocookie.net/starwars/images/9/97/Quarren_-_SW_Battlefront.png (File:Quarren_-_SW_Battlefront.png → wookieepedia_game_render.jpg)
- https://static.wikia.nocookie.net/starwars/images/9/92/CalgrizMaul-2017DarthMaul2.png (File:CalgrizMaul-2017DarthMaul2.png → wookieepedia_ink_spit_comic.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/quarren (official Databank).

## Candidate images
- `wookieepedia_infobox_three_quarren.jpg` — **the reference of record.** The infobox
  image: three Quarren in costume standing together on a transparent background,
  photographic fidelity. Settles the wide horizontal leaf-shaped ear-fins, the four
  thick curling jaw tentacles, the tall peaked bald cranium, the small close-set
  eyes, the mouth tusks, the mottled tan/ochre/pink hue (against "orange/purple"),
  the long pale pointed nails (against "suction cups"), and the layered robed dress.
  Three individuals in one frame makes each of those a species trait rather than one
  costume's choice.
- `wookieepedia_game_render.jpg` — a game render of a Quarren; independent
  confirmation of ear-fin and tentacle geometry from a different production.
- `wookieepedia_ink_spit_comic.jpg` — a comic panel of the Quarren Calgriz **spitting
  ink** at Darth Maul in combat. The only image in this entry showing the defensive
  ink ability in use; stylized, so treat as an action reference rather than a palette
  reference.

## ruling
(empty — owner has not reviewed this race yet)
