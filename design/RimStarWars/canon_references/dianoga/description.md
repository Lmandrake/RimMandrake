# Dianoga

**defName**: `RSW_Dianoga` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia)
Dianoga ("trash squid" is the related/subspecies name used for Death Star
tank-dwelling specimens specifically) are large, sentient, omnivorous
cephalopods native to the swampy planet Vodran in the Si'Klaata Cluster
(Hutt Space). Body plan: **seven suckered tentacles**, an eyestalk, a mouth
of sharp teeth, and several hearts. Length 7-10 meters. Skin color is
**deep purple** on a mature adult, but dianoga can actively change color and
pattern for camouflage — turning black, gray, or even transparent. Blood has
a blue tint. They can regenerate lost limbs and have excellent hearing.
Hermaphroditic, with individuals able to identify as female, "diangous" (the
most common gender), or male. Diet: omnivorous — fish, crabs, bones, and
aquatic plants. Entirely water-dependent (can survive brief stretches in open
air but will dry out). Society: a primitive tribal culture with its own
complex humming language that carries through water and scares off prey;
they venerate water and believe in reincarnation.

Canon role: the most famous dianoga is the unnamed one living in the Death
Star's trash compactor in *A New Hope* ("There's something alive in here" —
Luke Skywalker). Other named/attested appearances: a dianoga in the flooded
wreck of a derelict *Venator*-class Star Destroyer on Bracca (*The Bad
Batch*), a dianoga family in the Bracca Badlands during the High Republic
Era, and dianoga living in the SoroSuub refinery's water tanks on Sullust
(*Star Wars Battlefront*).

## Visual brief
All three candidate images agree and clearly show the canon body plan: a
small stalked eye (a single eye, dark reddish, atop a thin stalk) sits above
a bulbous head/body mass; below that, a large circular mouth ringed with
sharp teeth sits at the center where the limbs converge; several long, thin,
tapering tentacles hang/radiate downward from the body. Coloration in the
clean infobox render is a deep maroon/purple-brown with a wrinkled, ridged
skin texture — matching "deep purple" in the text. The Sullust refinery
still shows the same tentacled silhouette lit gold underwater. The "Toothy"
jar image (a juvenile specimen preserved in a tank at a theme-park
prop/display) shows mottled olive-green through murky liquid — consistent
with the text's claim that dianoga can shift color/pattern, not a
contradiction of the purple default.

**The current donor sprite (`donor_current_sprite.png`) does NOT match the
canon body plan at all.** It depicts a four-legged, tailed creature with a
single eyestalk on top of its head — the eyestalk is the only correct detail
carried over. There are no tentacles, no central toothy maw, and the
overall silhouette reads as a legged mammal/reptile rather than a hanging
cephalopod with seven suckered limbs. This is a clear, high-confidence
mismatch: any regen must replace the legged body with a radial mass of long
thin tentacles beneath a small eyestalk, in deep purple/maroon tones, with a
visible toothed central mouth.

## Must show
- [ ] Single dark reddish eyestalk (a small stalked eye) atop a bulbous head/body mass
- [ ] Large circular mouth ringed with sharp teeth at the center where limbs converge
- [ ] Several long, thin, tapering tentacles radiating/hanging downward — not four legs and a tail
- [ ] Deep maroon/purple-brown base coloring with a wrinkled, ridged skin texture

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Dianoga (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Dianoga&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/d/df/Dianoga_BF.png
  (*Star Wars Battlefront* infobox render, clean full-body reference)
- https://static.wikia.nocookie.net/starwars/images/f/f8/Dianoga-BF.png (a
  dianoga in the SoroSuub refinery water tanks on Sullust, *Battlefront*)
- https://static.wikia.nocookie.net/starwars/images/d/d3/Dianoga_SWGE-D23_video.jpg
  ("Toothy," a juvenile dianoga on display, Galaxy's Edge D23 promo still)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary
  mod, east-facing base variant) — a legged, tailed creature with an
  eyestalk; does not match the tentacled cephalopod body plan
- `wookieepedia_infobox.png` — *Battlefront* infobox render, clean full-body
  shot showing eyestalk, central toothed mouth, and radiating tentacles in
  deep purple-maroon
- `wookieepedia_sullust_refinery.jpg` — a dianoga in the SoroSuub refinery
  water tanks on Sullust, confirms silhouette underwater/backlit
- `wookieepedia_toothy_swge.jpg` — a juvenile specimen ("Toothy") on display
  in a tank, mottled olive-green coloring, consistent with the species'
  color-changing camouflage ability

## Expansion pass — 2026-09-23 (deep research, owner-requested)

Requested by the owner at the Fever Wood design sitting: *"Consult the canon for the
beast for more info and do some deep research to expand that canon."* Every fact below
was pulled as **wikitext via the `action=parse` API** — not from search snippets —
across 13 dianoga-related pages. URLs at the end of this section.

### Anatomy and size — canon has TWO registers

- **Ordinary dianoga:** seven **suckered** tentacles, one eyestalk, a mouth of sharp
  teeth, **several hearts**, **blue-tinted blood**, **7–10 m** long. The explicit canon
  ability list is *"Seven suckered tentacles, several hearts, blue blood, **ability to
  change color**, **ability to regenerate limbs**."*
- **Legends adds:** up to 10 m but **most specimens only 5–6 m**; the seven tentacles
  **surround a fanged maw containing a sharp serrated probe**; a tentacle is
  **membraned** (one wrapped around Luke Skywalker's head).
- 🔑 **The giant dianoga is a SEPARATE canon subject, not a size variant of this
  entry.** *"Many times larger than an average dianoga and easily dwarfing a Human,"*
  with **barbed** tentacles rather than suckered, **red** skin and **red** eye, and a
  **giant red eyestalk about equal in length to its tentacles**. Its maw is *"a gaping
  maw lined with sharp teeth, **not unlike that of a sarlacc**"* — canon draws the
  sarlacc comparison itself, which `the_fever_wood.md` §4 independently arrived at.
  ⚠️ **Only ONE specimen was recorded in galactic history** (Coruscant sewers, c. 4 ABY),
  appearing solely in the *Shadows of the Empire* video game — whose article flags that
  the game contradicted its source material, so that individual is of doubtful Legends
  canonicity while *"that doesn't necessarily discount the canonical status of the
  species itself."* ⇒ Treat the giant form as **sourced but vanishingly rare**, which is
  precisely why an unusually large one reads as shocking even to people who know the
  species.
- 🔴 **Canon weak point: the eyestalk.** The giant dianoga was beaten *"by firing at its
  prominent eyestalk."* This is the only canon-attested way anyone has defeated one.
- **Omi**, the named Death Star specimen: purple skin *"that could change color to match
  her surroundings"*, **a green eye with red sclera**, and a single eyestalk protruding
  from the **centre** of her body.

### Colour — purple

Mature skin is **deep purple**, actively changeable to **black, gray, or even
transparent** for camouflage. Dianogan tea **stains lips purple and teeth black**, and
one drinker's teeth went *"a garish purple."*

⇒ **Purple is the colour association for this creature and its body parts**, confirmed by
the owner 2026-09-23.

### Culture, the hum, and reproduction

- *"Dianoga had a primitive tribal culture. When they were not feeding, they often spoke
  a deep, complex humming language. **Because its reverberations carried so completely in
  the water, that language scared away all nearby prey.**"* They **venerate water**.
- Hermaphroditic; **reproduction involved partners exchanging eggs with one another**, and
  the **life cycle begins with an egg** (a crate labelled "Dianoga eggs" is attested in
  *The Old Republic*).
- **Entirely water-dependent** — survives only brief stretches in open air before drying
  out. Combined with the **excellent hearing** already in this entry's original sourced
  text, the canon creature is a listener that cannot leave its water.

### Canon products — a real trade line, all sourced

Dianoga are **edible by humans** and support a named product family. ⭐ The owner's
2026-09-14 ruling below already assigned this material to the **Star Wars Cuisine mod**.

| product | canon detail |
|---|---|
| **Dianoga pie** | *"the most popular of the dishes made of dianoga meat"* — a **savory pie with a beige crust** and a seasoned filling. The **Houk** species are especially fond of it. House special at the **Meltdown Café** on Nar Shaddaa, served with **krayt milk**. An Imperial officers' field guide notes chefs *"could use dianogas to make a tasty pie, although troops were unlikely to come back for second servings."* |
| **Dianoga omelette** | Served at a canteen aboard the **first Death Star**; edible by humans. |
| **Dianogan tea** | Steeped from **chemicals found in the dianoga's spleen**, normally **served hot**. A **delicacy among Muuns**. **Temporarily stains lips purple and teeth black**, with a **mild narcotic effect**. Wookieepedia categorises it under **Drugs and medicine**. Favoured by Admiral Pors Tonith. |
| **Dianoga cream**, **Dianoga cream-filled donut** | Each attested as its own canon subject. |
| **Dianoga cheese** | Named by the owner; ⚠️ **UNCONFIRMED** — no page was pulled for it this pass. Do not cite as sourced until one is. |

### A canon flora neighbour

**"Dianoga's Kiss"** — a canon species of **brown tentacled plant** on the planet Balnab,
growing **alongside umbrella trees**. Named in *Star Wars: The Visual Encyclopedia*
(2017); first appeared in *The Clone Wars* S3E6 "Nomad Droids." Noted here because it is
a ready canon tentacled-plant injection for a swamp flora roster.

### Expansion-pass source URLs

- https://starwars.fandom.com/wiki/Dianoga
- https://starwars.fandom.com/wiki/Dianoga/Legends
- https://starwars.fandom.com/wiki/Giant_dianoga
- https://starwars.fandom.com/wiki/Omi
- https://starwars.fandom.com/wiki/Unidentified_Dianoga
- https://starwars.fandom.com/wiki/Dianoga_pie
- https://starwars.fandom.com/wiki/Dianoga_omelette
- https://starwars.fandom.com/wiki/Dianogan_tea
- https://starwars.fandom.com/wiki/Dianogan_tea/Legends
- https://starwars.fandom.com/wiki/Dianoga_cream
- https://starwars.fandom.com/wiki/Dianoga_cream-filled_donut
- https://starwars.fandom.com/wiki/Dianoga%27s_Kiss

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.png`

> "Yup. Mixture of #2 dominant with some hints of #1 is needed on how to Rimworld-ify it. And #3/#4 are inspiration for the Star Wars Cuisine mod!"
