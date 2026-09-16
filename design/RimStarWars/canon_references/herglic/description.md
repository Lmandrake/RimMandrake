# Herglic

**defName**: `RSW_RimMandrakeHerglic` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 778 —
that file is GENERATED, do not hand-edit).
Assigned `Jawa_DeepwaterCompact: S` — some, in the water faction only, which fits: the
Herglic is a **cetacean** (Wookieepedia files it under `Category:Cetacean sentient
species` in both the canon and Legends article).

## Sourced text (Wookieepedia)

**Canon article** (thin — the species has no height, mass, lifespan or origin recorded in
canon; all four are **UNSOURCED**, do not invent them):

> The Herglics were a species of sentient, hulking aliens with **black skin, a wide
> mouth, oily eyes, and a blowhole.**

Canon infobox: skincolor **Black**; distinctions **"Wide mouth; rows of tiny, serrated
teeth; tiny eyes in large head; no neck or chin; blowhole; slick skin; cartilaginous
shoulders."** Body text repeats: *"dark, slick skin, and oily eyes. They had a large head
with no neck or chin and a wide mouth with tiny, serrated teeth. Herglics also had
cartilaginous shoulders and a blowhole on their heads."* Canon behaviour is entirely
circumstantial — Herglics mistreated by the Empire, sheltering in the Coruscant junkyard
Level 1782; one enslaved by Trandoshan slavers and sold to be a gladiator, dying in
training; Gor-kooda working muscle for a Sullustan crime lord on Akiva.

**Legends article** (this is where the numbers and the personality live):

- **Height 1.7–2.2 meters** (`Galaxy of Intrigue`). The only sourced size figure that
  exists for the species. **Mass and lifespan are UNSOURCED in both articles.**
- Skin colour **pale blue** *or* **black** (`Ultimate Alien Anthology`); the text adds
  that some, like Hamar-Chaktak, had **pale pink** skin, and *"a few Herglics, such as …
  Narloch, displayed **white stripes down the sides of their head and arms**."*
- Origin **Giju**; language **Herglese**; distinctions *"aquatic organs; massive size."*
- *"Herglics were large bipeds that appeared to have evolved from water-dwelling mammals.
  Most of the evidence of their waterborne ancestry had been bred out so that, for
  example, **fins and flukes were replaced with arms and legs.** They did, however, still
  **breathe through a blowhole on the top of their heads.**"* The `hauum` sound of a
  Herglic clearing its blowhole is a Herglese word used to preface a significant remark.
- 🔑 **"They were tall and extremely wide, and had smooth, hairless skin."** Width, not
  height, is the defining proportion: *"a Herglic would take up two seats in a restaurant,
  and the majority of doorways required some manoeuvring."*
- **Behaviour, and it is not what the repo def says.** *"Herglics were pleasant and
  peaceful, but they had an **addiction to gambling and games of chance**."* They were
  *"typically easygoing and enjoyed meeting new people and visiting exotic locations,"*
  *"natural explorers and traders"* with *"an inquisitive but practical nature and calm
  persona that helped them interact with other species."* They are also **sensitive about
  their size** and feel self-conscious in Human-scaled facilities.
- **Technologically advanced, early.** They developed **hyperdrive independently**, built
  the Herglic Trade Empire in the Colonies, joined the Republic in 13,000 BBY, and their
  scouts established the Rimma Trade Route in 5500 BBY. Archaeology on their colony worlds
  found *"nonfunctioning machines that appeared to harness gravity"* at a level *"not
  paralleled during the time of the Galactic Empire."* Herglics own casinos at Reaper's
  World and privately run the gamblers' world Tresidiss with Hutt-affiliated criminal
  groups.
- **Unusual abilities: none.** No Force sensitivity, no venom, no natural weapon is
  recorded in either article. The one distinctive organ is the **blowhole**; the one
  distinctive social unit is the **pod ("pakk")**, with family members prefixed by *pod*.
  Do not invent an ability.

🔴 **Repo def contradicts canon on three counts** (report only; the def is generated —
`RSW_RimMandrakeHerglic` carries `AptitudePoor_Social`, `AptitudePoor_Intellectual`,
`AptitudePoor_Medicine`):

1. **`AptitudePoor_Intellectual`** against a species that invented its own hyperdrive,
   ran a trade empire predating the Republic, and left gravity-manipulating machinery
   archaeologists cannot explain.
2. **`AptitudePoor_Social`** against *"pleasant and peaceful … easygoing and enjoyed
   meeting new people … calm persona that helped them interact with other species,"* and
   against a species defined by **trade**.
3. The def's own description — *"can hit like a wrecking ball … thick skin allows them to
   shake off most blunt attacks"* — is **mod flavour with no Wookieepedia support.** No
   source in either article gives the Herglic a combat aptitude or damage resistance.
   `MeleeDamage_Strong` + `Body_Hulk` + `Outland_ThickSkin` are all built on that
   invented line. The sourced trait the def *omits* is the **gambling addiction**, which
   is the species' one canonical vice and would sit naturally on a RimWorld trait.

The def's skin genes (`Skin_InkBlack`, `Skin_SlateGray`) are defensible for canon-black
but drop **pale blue**, **pale pink** and the **white-striped** variant that Legends
records.

## Visual brief

🔴 **The prose word is "black". Every image shows the Herglic is an ORCA — and one of them
shows the marking pattern explicitly.** This is the single most important finding in this
entry: "black skin" read alone produces a black hulk, and that is wrong for at least one
canonical individual and understates all of them.

**Head — the whole species reads from it:**
- **The head is a whale's head worn as a face.** A single smooth, bulbous, forward-swept
  dome, widest at the crown, tapering to a **blunt rostrum**; there is **no neck and no
  chin** (canon text, and every image agrees), so the skull sits straight on the
  shoulders.
- **The mouth is a single wide lipless line running most of the head's width**, curving up
  at the corners into a permanent faint smile — a cetacean mouth-line, not lips. In the
  Legends line art (`wookieepedia_legends_alien_encounters_fullbody.jpg`) the lower jaw
  reads as a separate rounded pouch beneath it.
- **Eyes are small, set very wide and low on the sides of the head, near the mouth-line
  corners** — the "tiny eyes in large head" of the canon infobox. They are the *only*
  facial features besides the mouth. In `wookieepedia_canon_qensog_comic.jpg` they are
  small dark almonds; in `wookieepedia_canon_weapon_of_a_jedi.jpg` they are yellow with
  narrow pupils under heavy angled brow creases. **Neither image shows a nose** — there
  are at most a pair of small paired nostril slits.
- ⚠️ **No image in this set shows the blowhole**, which is canon text and would sit on the
  **top of the cranium** — an above-view (RimWorld's `_north`) detail. Treat the blowhole
  as textually canon and visually unconfirmed.
- **Marking pattern — trust the image.** `wookieepedia_legends_narloch_white_stripes.jpg`
  is an unambiguous **killer-whale pattern**: glossy black cranium and back, a hard-edged
  **white eye-patch above and behind each eye**, and a **white throat/lower jaw and belly**
  that runs down under the mouth. The prose calls this "white stripes down the sides of
  their head and arms"; the picture calls it orca countershading. **A Herglic that is
  uniformly one colour is the failure mode.**
- Colour, from the images rather than the word "black": Qensog is **slate grey-lavender**;
  the *Weapon of a Jedi* Herglic is **desaturated blue-purple**, not black. Both sit
  comfortably inside the Legends range pale-blue-to-black, and **neither is ink black.**

**Body:**
- **Extremely wide, barrel-chested and short-limbed relative to width** — the mass is in
  the shoulders and gut, not in height. Legends says 1.7–2.2 m, i.e. *human-tall*: the
  Herglic is **not a giant, it is a very broad person.** A RimWorld `Body_Hulk` gets the
  width right by accident and the height wrong if scaled up.
- **Shoulders are enormous and rounded, with no clavicle shelf** — consistent with the
  canon "cartilaginous shoulders."
- **Arms are thick and taper to broad paddle-like hands.** Digit count differs by image:
  the Legends line art gives a clawed three/four-digit hand, the comic a mitten-like
  paddle. **Digit count is unsettled — do not assert five.**
- **Legs are short, thick and column-like; the feet are broad and flat with no visible
  toes** (`wookieepedia_canon_weapon_of_a_jedi.jpg`, barefoot). Skin reads **smooth and
  slick with specular sheen**, hairless everywhere.

**Body vs. clothing** — both full-body images show a **dressed** Herglic and the clothing
is easy to mistake for anatomy:
- *Weapon of a Jedi*: the pale bands at the forearms and waist are **cloth wraps**, the
  green caps on the shoulders are **shoulder pads**, the olive trousers and the large
  beaded **necklace** are worn. The bare, unclothed anatomy is: torso, upper arms, hands,
  head, feet.
- Qensog wears a **green flight suit with a harness and chest plate** — the plated look on
  his cranium is skin, but the panelling below the jaw is the suit.
- Narloch wears a **white sleeveless tunic, black belt and dark trousers** with a pendant;
  the **white on his throat is skin**, and the white tunic sits right beneath it. Do not
  let the tunic absorb the throat marking, or vice versa.

**`donor_current_sprite.png` is `.../Heads/Herglic/Herglic_south.png` (512×512, RGBA) — a
greyscale tint mask,** which is correct and expected for a RimWorld humanlike head (the
game tints it from the pawn's skin-colour gene, so the absence of colour is not a defect
and the colour findings above belong on a gene). What it gets right: a large domed
neckless head with a low overhanging brow lobe, two angled eyes set low, two nostril dots.
What is **missing**: **there is no mouth at all** — the wide lipless mouth-line is the
species' most-cited feature and it is simply absent; there is no blowhole (`_north` would
be the place); and the eyes are set high-central rather than wide and low. 🔴 **And a
single-channel tint mask cannot produce the orca eye-patch/white-throat pattern at all** —
countershading needs either a second render node or a baked variant head, so if the owner
wants the Narloch pattern it is not a colour change, it is new art. `Herglic_east.png` and
`Herglic_north.png` exist; there is **no Herglic body art on disk**, so a Herglic is a head
on a standard RimWorld body, and the "extremely wide" proportion is unrepresented.

## Source URLs
- https://starwars.fandom.com/wiki/Herglic — canon article. Direct HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Herglic&format=json&prop=wikitext`
  (4,993 chars, 2026-09-15).
- https://starwars.fandom.com/wiki/Herglic/Legends — Legends article, via
  `…&page=Herglic/Legends&…` (14,756 chars, 2026-09-15). **Source of the only height
  figure and of the white-stripe, pale-blue and pale-pink variants.**
- https://static.wikia.nocookie.net/starwars/images/7/70/Qensog2-2015StarWars61.jpg
  (File:Qensog2-2015StarWars61.jpg, canon infobox image → `wookieepedia_canon_qensog_comic.jpg`)
- https://static.wikia.nocookie.net/starwars/images/a/a5/Herglic-TheWeaponOfAJedi1.jpg
  (→ `wookieepedia_canon_weapon_of_a_jedi.jpg`)
- https://static.wikia.nocookie.net/starwars/images/d/db/Herglic-AE.png
  (File:Herglic-AE.png, `Alien Encounters` → `wookieepedia_legends_alien_encounters_fullbody.jpg`)
- https://static.wikia.nocookie.net/starwars/images/2/27/Narloch1.jpg
  (File:Narloch1.jpg → `wookieepedia_legends_narloch_white_stripes.jpg`)
- https://static.wikia.nocookie.net/starwars/images/f/fa/Herglic.jpg
  (File:Herglic.jpg, Legends infobox → `wookieepedia_legends_infobox.jpg`)
- NOT fetched this pass: `https://www.starwars.com/databank/` has no Herglic species page
  that was attempted.

## Candidate images
- `wookieepedia_canon_weapon_of_a_jedi.jpg` — **the reference of record for body and
  colour.** Full-figure canon comic Herglic, head to bare feet: barrel torso, huge rounded
  shoulders, short thick legs, paddle hands, yellow narrow-pupilled eyes, wide up-curved
  mouth-line, **desaturated blue-purple skin rather than black.** Clothing (wraps, shoulder
  pads, trousers, necklace) is separated in the visual brief above.
- `wookieepedia_legends_narloch_white_stripes.jpg` — **the reference of record for
  markings.** Narloch, half-figure: unmistakable orca countershading (black cranium, white
  eye-patch, white throat). This is the image that contradicts "black skin."
- `wookieepedia_canon_qensog_comic.jpg` — canon infobox image. Best read of the head in
  three-quarter view: neckless slate-lavender skull, small dark eyes set wide, wide lipless
  mouth. Waist-up only, and he is in a flight suit.
- `wookieepedia_legends_alien_encounters_fullbody.jpg` — Legends `Alien Encounters` line
  art, full figure, **black-and-white, so it carries no colour information at all** — use
  it for silhouette and proportion only (the extreme width, the pouched lower jaw, the
  clawed hand). Its clothing is heavy: sash, boots, gloves, belt pouch.
- `wookieepedia_legends_infobox.jpg` — the Legends infobox image, low resolution
  (465×550) and the weakest of the set; kept for completeness.

## ruling
(empty — owner has not reviewed this race yet)
