# Nikto

**defName**: `RSW_RimMandrakeNikto` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_HuttCartel: A` (abundant) and `Jawa_Junkers: S`.

## Sourced text (Wookieepedia)
Infobox: origin **Kintan**; habitat "acclimated to desert climates"; skin colour
gray, green, red, blue; eye colour black, blue, yellow; distinctions "**scaled
skin**, **symmetrical horns**, **head spikes**, **movable facial features**".
🔴 **No height, mass or lifespan is given — do not supply one.**

🔑 **Nikto are a SUBSPECIES species, and the subspecies differ visibly.** The
article names at least four:
- **Kajain'sa'Nikto** (**red Nikto**) — well adapted to arid desert climates.
- **Kadas'sa'Nikto** (**green Nikto**) — also well adapted to arid desert climates.
  **Green Nikto offspring were born from eggs**, and were therefore called
  **hatchlings**. **This subspecies was incapable of blushing, as their skin only
  contained green pigments, and had a thick, stiff quality.**
- **Esral'sa'Nikto** (**mountain Nikto**) — occupied more temperate, lush
  environments, and 🔑 **had NO horns, possessing fan-like facial "fins" instead.**
- **Nikto Ijosap'sai** — commonly mistaken for the Prae'tus species.

**Both red and green Nikto were distinguished by their scaly, coarse skin and
various facial horns and spikes.** For a desert campaign the red and green
subspecies are the relevant ones; the hornless fan-finned mountain Nikto is a
genuinely different face and should not be blended into the same sprite.

**Unusual abilities.** The canon article as fetched claims **no special sense,
resistance or capability** — the distinctives are all morphological ("movable facial
features" is the only unusual one, and the article does not elaborate on it). Do not
invent an ability here. Note that green-Nikto oviparity (egg-laying) and the
inability to blush are the only two physiological facts stated, and both belong to
the green subspecies specifically, not to the species as a whole.

## Visual brief
🔴 **The infobox's four-word distinction list ("scaled skin, symmetrical horns,
head spikes, movable facial features") drastically undersells the head, and it also
misleads on colour. The images are far more specific.** From the live-action
reference (a Kintan Strider, i.e. a Nikto):

- 🔑 **The cranium is a PLATED CARAPACE, not merely "scaled skin."** The crown and
  forehead are covered in a mosaic of large, hard, overlapping plate segments —
  helmet-like, geometrically tessellated, sharply distinct from the softer skin of
  the throat and neck below. This armoured skull-cap is the species' single
  strongest read at any size, and "scaled skin" does not convey it.
- 🔑 **Two prominent horns curve UP and INWARD from the cheeks/temples**, flanking
  the face and rising past the level of the eyes. They are large, pale, tusk-like
  and symmetrical — this is the "symmetrical horns", and they are much bigger
  relative to the head than the phrase suggests.
- **The face below the plating is flat and deeply creased**, with radiating furrows
  from the eyes and mouth.
- **A small flat nose with two slit nostrils**, barely projecting.
- **Small, dark, deep-set eyes.**
- **A wide, down-turned mouth with a heavy protruding lower lip / chin pad** — the
  lower face juts.
- 🔴 **Colour contradicts the list.** This individual — a red Nikto by subspecies
  name — is a **pale putty tan / pinkish-tan**, not red. The four listed colours
  (gray, green, red, blue) are the subspecies *names* more than they are observed
  hues: "red Nikto" in practice photographs as **warm tan-to-clay**, not scarlet.
  A saturated red Nikto sprite would be wrong for the reference individual.
- **The body is thickset, broad-shouldered, fully humanoid** in proportion, and
  wears **ordinary battered workwear** — in the reference, a leather biker vest with
  patches over a canvas work shirt, black gloves, dark trousers, plus a quilted /
  scaled midriff panel. The **live-action gang** image shows the same register
  across a whole group: scavenger-biker leathers. **A Nikto reads as a person in
  hard-worn leathers with an armour-plated, horned head.**
- The **animated guard** image agrees on the plated crown and the up-curving cheek
  horns while pushing the hue greener and the shapes more graphic — useful as
  independent confirmation of structure across media, and as a green-subspecies
  datapoint.

## Must show
- [ ] Cranium covered in a plated carapace — large, hard, overlapping tessellated plate segments, helmet-like, distinct from the softer skin below
- [ ] Two prominent horns curving up and inward from the cheeks/temples, large, pale, tusk-like and symmetrical, rising past eye level
- [ ] Flat, deeply-creased face with radiating furrows from the eyes and mouth
- [ ] Small, dark, deep-set eyes and a wide, down-turned mouth with a heavy protruding lower lip/chin pad
- [ ] Skin reads as pale putty-tan/pinkish-tan for a "red" Nikto, not a saturated red

## Engine limits
none known

## donor art
**donor_current_sprite.png is weak evidence, and there is a wiring defect behind
it.** The copied file is `SWX/Pawn/HeadAttachments/nikto/facespines_south.png` —
two small clusters of black facial spines. Separately,
`SWX/Pawn/HeadType/` has **no `nikto` directory**, so there is no dedicated Nikto
head sprite on disk.

🔴 **Verified from the defs, not assumed**: the Nikto xenotype's gene list includes
`RSW_NiktoHead`, `Hair_BaldOnly`, `Body_Standard` / `Body_Hulk`,
`RSW_Skin_SlateRed`, `RSW_Skin_SlateBlue`, `RSW_Skin_DarkGreen`,
`RSW_Skin_MidGray` and `Skin_LightGray` — so the four subspecies hues are modelled
as skin-colour options, which is a good match to canon. **But the gene that uses
this facespines texture, `RSW_Brow_facespines`, appears in NO xenotype's gene list
at all** (checked across every `XenotypeDef` in `RimMandrakeXenotypes.xml`: zero
occurrences of `<li>RSW_Brow_facespines</li>`). The art and the gene both exist and
nothing consumes them — so the facial spines currently never appear in game on any
pawn. **Nothing on disk supplies the plated cranial carapace or the large
up-curving cheek horns**, i.e. both of the features the images identify as
definitive.

## Source URLs
- https://starwars.fandom.com/wiki/Nikto (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Nikto&format=json&prop=wikitext`,
  26,755 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/4/48/KintanStriderSpeedBiker-Villains2024.png (File:KintanStriderSpeedBiker-Villains2024.png, the infobox image → wookieepedia_infobox_kintan_strider.jpg)
- https://static.wikia.nocookie.net/starwars/images/0/0f/NiktoGuard-TCWCEJtB.png (File:NiktoGuard-TCWCEJtB.png → wookieepedia_guard_animated.jpg)
- https://static.wikia.nocookie.net/starwars/images/7/70/KintanStriders-BoBFCh4.png (File:KintanStriders-BoBFCh4.png → wookieepedia_gang_liveaction.jpg)
- NOT fetched this pass: the per-subspecies articles
  https://starwars.fandom.com/wiki/Kajain%27sa%27Nikto,
  https://starwars.fandom.com/wiki/Kadas%27sa%27Nikto and
  https://starwars.fandom.com/wiki/Esral%27sa%27Nikto — worth a later pass, since
  the subspecies faces genuinely differ (especially the hornless, fan-finned
  mountain Nikto, for which this entry has NO image).

## Candidate images
- `wookieepedia_infobox_kintan_strider.jpg` — **the reference of record.** The
  infobox image: a live-action Nikto from the chest up on a transparent background,
  high resolution. Settles the plated cranial carapace, the two large up-curving
  cheek horns, the creased flat face, the flat slit-nostrilled nose, the protruding
  lower lip, the pale putty-tan hue (against "red"), and the battered-leathers
  dress register.
- `wookieepedia_gang_liveaction.jpg` — a group of live-action Nikto. Confirms the
  head structure recurs across individuals and shows the species as a crowd, useful
  for the Cartel/Junker gang read.
- `wookieepedia_guard_animated.jpg` — an animated Nikto guard. Stylized, so treat
  line and hue as the artist's; its value is independent structural confirmation
  (plated crown, up-curving horns) in a different medium and at a greener hue.
- ⚠️ **Missing: any image of the Esral'sa'Nikto (mountain) subspecies**, whose face
  is hornless with fan-like fins. Anyone continuing this entry should fetch one
  before treating the horned face as the whole species.

## ruling
(empty — owner has not reviewed this race yet)
