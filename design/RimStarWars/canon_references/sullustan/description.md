# Sullustan

**defName**: `RSW_RimMandrakeSullustan` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Matrix placement `OutlanderCivil: S` — some, so a settled-trader face rather than a
raider.

## Sourced text (Wookieepedia)

**Canon.** Sullustans were a species of **humanoids** from the planet **Sullust**,
experts at manufacturing, scientific and technological development, and economics,
having founded the **SoroSuub Corporation**. They were distinguished by **the two
flaps of jowls around their cheeks** and **large, mouse-like eyes** that were
**typically dark and gleaming**. They also had **large ears**. The species **wore
native headgear to cover their wide heads**; Nien Nunb modified one such piece into
a flight helmet. **Sullustese** was "a rapid chatter spoken in liquid tones."
Sullustans were a sophisticated species and **lived in subterranean cities
surrounded by lava**.

Infobox (canon): class **humanoid**; **skin gray, light**; **hair brown**; **eyes
black, brown**; **distinctions — two flaps of jowls around their cheeks,
mouse-eyed**; origin **Sullust**; habitat **subterranean**; language Sullustese.
**No height, mass or lifespan is given in canon** — UNMEASURED.

**Legends** (`Sullustan/Legends`, for the numbers and senses canon lacks — tag them
as Legends if used): class **near-Human**; **height 1–1.8 meters**; skin **pink,
gray, or light green**; eyes black; distinctions **large dark eyes, large rounded
ears, exceptional hearing, scarns, naturally tucked-in cheeks**. Round, **tapered
skulls**; **almond-shaped black eyes**; the facial jowls are named **dewflaps**.

> "Having evolved in the underground of their planet, their **wide earlobes provided
> excellent hearing and a sense of directional sound**, and their **large eyes
> provided exceptional low-light vision and excellent peripheral vision.
> Sullustans could see up to 20 meters in the dark** without being sensitive to
> infra-red, meaning they could effectively read and see normally with no light at
> all."

Also Legends: **corneal defects began after about 30 standard years**, after which
many wore special visors; some tattooed their heads. Like humans, a single heart and
one stomach. **Very difficult to get drunk, and no hangovers.** **Pink-skinned and
generally hairless, although facial hair occurred in some males** (Dllr Nep's white
goatee); **cranial hair was rare for males but females often grew it, and it was
considered a symbol of individuality.**

**Unusual abilities.** Two, both well sourced and both worth having: **low-light
vision** (canon "large eyes well adapted to the dark", Legends 20 m in total
darkness) and an **innate sense of direction** —

> "Sullustans possessed an exceptional innate sense of direction and intuition since
> their civilization grew in underground tunnels; **many were able to navigate a path
> after seeing a map only once.** This ability extended to sublight and hyperspace
> navigation … Sullustans made excellent scouts, pilots and navigators."
> (Legends)

**Size.** Canon gives none. Legends' 1–1.8 m band is wide, but every image shows a
short, stocky individual, and Legends' own prose calls them "a **diminutive**
species" — so short is the right read, and the def's `RSW_BodySizeGene_small` is
consistent with it.

## Visual brief

Four images: a practical costume/mask on a white background (the canon infobox), two
painted RPG/card pieces and one in-show CGI-era render. **They agree completely, and
the whole species reads on three features.**

- 🔑 **Two enormous pendulous jowl flaps — the "dewflaps" — hanging from below the
  eyes down past the jawline, meeting under the chin.** They frame a small pursed
  mouth set deep between them. In `wookieepedia_infobox_niennunb.jpg` they hang
  visibly *below* the chin line and read as separate lobes of flesh, not as cheeks.
  This, not the eyes, is the silhouette-defining feature: the head's outline is
  **widest at the jowls, low down**, giving an inverted-teardrop head.
- 🔑 **Large, round, glossy solid-black eyes** occupying much of the upper face, set
  forward and wide, with no visible white and no iris — "mouse-eyed" and "almond-
  shaped black" both land. Proportionally they are two to three times a human eye.
- 🔑 **Large, round ears set low and wide, projecting sideways from the skull**, with
  a visible thick outer curl and heavy lobe. In the infobox image they read as
  broad discs at the level of the mouth, not high on the skull.
- **A broad, high, domed cranium tapering to the rear** — "round, tapered skull" —
  which is what the canon "wide heads" and the native headgear are about.
- **No visible nose.** A short blunt muzzle sits between the eyes; there is no nasal
  bridge and no projecting snout. Do not give a Sullustan a nose.
- **Completely bald** in all four images, including the two female-ambiguous pieces.
- **Short, stocky, thick-necked, wide-shouldered**, with arms long relative to the
  torso and a slight forward hunch (`wookieepedia_negas_legends.jpg` walking).

🔴 **Skin: the images are grey, grey-pink and grey-blue — never human brown.**
`wookieepedia_infobox_niennunb.jpg` is a desaturated mauve-grey with pink around the
eye sockets; `wookieepedia_negas_legends.jpg` is a warm grey-tan; the
`wookieepedia_droid_specialist.jpg` render is distinctly **cool grey-blue**. This
matches the canon infobox ("gray, light") and Legends ("pink, gray, or light green")
and **contradicts the def's melanin genes** (see below). A brown-skinned Sullustan is
the failure mode.

**donor_current_sprite.png is fair evidence and mostly right.** It is
`OR/Things/Pawn/Humanlike/Heads/Sullustan/Normal_south.png` (512×512), the texture
behind head type `RSW_Sullustan` forced by gene `RSW_SullustanHead`. As with every
RimWorld humanlike head it is a **greyscale mask tinted at runtime from the skin-
colour gene**, so the absence of colour here is correct and the hue findings above
belong on the *gene*, not on this file. What it gets right: a broad rounded cranium,
two very large solid-black eyes set wide, and — importantly — **the paired dewflaps
are present**, rendered as a two-lobed shape hanging below the eyes over a hidden
mouth. What it lacks: **no ears** (they are a separate attachment), no ear-level
width, and the dewflaps stop at the chin rather than hanging past it, so the head
silhouette is a circle where canon is widest-at-the-jowls. There is exactly one head
type and one facial variant — no male/female or age variation, and no visor, tattoo
or goatee variants for the Legends details.

## Must show
- [ ] Two enormous pendulous jowl "dewflap" lobes hanging from below the eyes down past the jawline, meeting under the chin — the head is widest at the jowls, low down, giving an inverted-teardrop silhouette
- [ ] Large, round, glossy, solid-black eyes with no visible white or iris, occupying much of the upper face
- [ ] Large, round ears set low and wide, projecting sideways from the skull at about mouth level — not high on the skull
- [ ] Broad, high, domed cranium tapering to the rear, with no visible nose or nasal bridge
- [ ] Completely bald head
- [ ] Skin reads grey, grey-pink, or grey-blue — never human brown

## Engine limits
none known

### 🔴 Def-versus-canon contradictions (report only, do not fix)

- **`Skin_Melanin2` / `Skin_Melanin3` / `Skin_Melanin4` are the only skin genes.**
  Those are the vanilla *human* melanin tones (mid-brown through dark). Canon skin is
  **grey and light**; Legends adds **pink and light green**. **There is no grey, pink
  or green skin gene on this xenotype at all**, so every Sullustan the game generates
  will be a brown-skinned human tone — directly contradicting canon and contradicting
  all four reference images.
- **`Hair_BaldOnly` overstates it.** The canon infobox lists **hair colour brown**,
  and Legends says **females often grew cranial hair** and that it carried social
  meaning, with facial hair in some males. Bald is the male-typical case, not the
  species rule. (All four available images happen to be bald, so this is a
  text-versus-text finding, not an image one.)
- **The species' own ear art is not wired to the species.** The mod ships
  `SWX/Pawn/HeadAttachments/sullustan/BigEars_{south,east,north}.png`, but that
  texture belongs to gene **`RSW_Ears_big`** (`Defs/GeneDefs/SW_Genes.xml:871`), and
  the Sullustan xenotype instead lists **`Outland_Ears_Large`** — a gene from a
  dependency mod, not defined anywhere in this repo. So the Sullustan-named ear
  sprite is dead weight with respect to Sullustans, and what ears a Sullustan
  actually gets in game is decided by a def this repo does not own. **Verify in game
  before trusting either.** Separately, the shipped BigEars art is a pair of *small
  human-shaped* ears with lobes — not the large low-set discs canon describes.
- **`DarkVision` and `RSW_Eyes_Big` are well founded** ✅ (canon "large eyes being
  well adapted to the dark"; Legends 20 m in darkness).
- **Nothing represents the navigation/direction sense**, which is the species'
  single most-cited ability across both canons ("navigate a path after seeing a map
  only once", "excellent scouts, pilots and navigators"). The def instead assigns
  `AptitudeStrong_Construction` / `_Mining` / `_Intellectual`, which fit the
  manufacturing and subterranean-city fiction but not the piloting.
- **`Mood_Optimist` + `KindInstinct` are unsourced as species traits.** Nothing in
  either article characterises Sullustan temperament that way.
- **The jowls/dewflaps have no gene of their own** — they exist only inside the head
  texture, so they cannot vary and cannot be re-used. Recorded as a structural note,
  not an error.

## Source URLs

- https://starwars.fandom.com/wiki/Sullustan — canon article. Direct HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Sullustan&format=json&prop=wikitext`
  (200, 25,265 chars, 2026-09-15).
- https://starwars.fandom.com/wiki/Sullustan/Legends — Legends article, same API
  route (200, 50,000 chars, **response truncated at 50,000** so later sections were
  not read; the Biology and appearance section was complete). Source of the height
  band, dewflap name, 20 m dark vision, corneal defects, hair rules and the
  navigation claim.
- https://static.wikia.nocookie.net/starwars/images/0/04/NienNunbFull-SWBC62.png (File:NienNunbFull-SWBC62.png, canon infobox image → `wookieepedia_infobox_niennunb.jpg`)
- https://static.wikia.nocookie.net/starwars/images/b/b6/DroidSpecialist-FO.png (File:DroidSpecialist-FO.png, "a Sullustan droid specialist" → `wookieepedia_droid_specialist.jpg`)
- https://static.wikia.nocookie.net/starwars/images/5/58/NienNumb-HeroesResistance.png (File:NienNumb-HeroesResistance.png → `wookieepedia_niennunb_heroes.jpg`)
- https://static.wikia.nocookie.net/starwars/images/f/f5/Sullustan_NEGAS.jpg (File:Sullustan NEGAS.jpg, Legends infobox image, *The New Essential Guide to Alien Species* → `wookieepedia_negas_legends.jpg`)
- NOT fetched this pass: https://www.starwars.com/databank/sullustan (cited by the
  canon article for the jowls/mouse-eyed line; the Databank page itself was not
  retrieved).

## Candidate images

- `wookieepedia_infobox_niennunb.jpg` — **the reference of record.** The canon
  infobox image: a full-body practical costume on white, straight-on, high
  resolution. Settles the pendulous dewflaps hanging past the chin, the solid-black
  mouse eyes, the large low-set round ears, the mauve-grey skin and the short stocky
  build. The best single image for the head silhouette.
- `wookieepedia_negas_legends.jpg` — **the reference of record for the body.** A
  painted full-figure walking three-quarter view; clearest on proportions (short
  legs, long arms, forward hunch, thick neck) and on the tapered rear of the skull.
  Painted and Legends-tagged, so treat palette and status accordingly, though its
  face agrees closely with the infobox.
- `wookieepedia_droid_specialist.jpg` — a painted seated figure in a flight cap.
  Useful for two things: it is the **coolest-toned** skin of the set (grey-blue),
  widening the attested range, and the cap shows how the canonical "native headgear
  to cover their wide heads" sits over the cranium.
- `wookieepedia_niennunb_heroes.jpg` — a stylised *Heroes of the Resistance* piece
  of the same character. Stylised, so weak on detail and worth little beyond
  confirming that the dewflaps and black eyes survive heavy abstraction — which is
  the relevant test for a 128 px RimWorld head.

## ruling

(empty — owner has not reviewed this race yet)
