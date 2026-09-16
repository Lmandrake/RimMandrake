# Weequay

**defName**: `RSW_RimMandrakeWeequay` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_Junkers: S`.

## Sourced text (Wookieepedia)
Weequay are a sentient species native to the desert world **Sriluur**. Infobox:
**height 1.89 meters**; habitat deserts; skin colour blue, brown, gray, pink, red,
yellow; hair colour black, blond, brown, gray; eye colour black, blue, gold, gray;
distinctions "**tough, leathery skin that provided resistance to blasterfire**".

Weequays were common throughout the galaxy. **Evolving under merciless conditions,
their tough, leathery skin helped them endure the harsh environment of their
homeworld as well as providing natural resistance to blaster fire. This made
Weequays ideal bodyguards and bounty hunters.** **Some Weequay grew horns on their
lower jaw, while others had bumpy extensions of their skin.** Weequays often kept
their hair long.

**Unusual abilities — two, and both are mechanically interesting.**
- 🔑 **Natural resistance to blaster fire** from the leathery skin. This is a
  sourced, species-level damage resistance, not flavour — and it is specific to
  blaster/energy damage, not a general armour bonus.
- 🔑 **Weequays possessed the ability to communicate with other nearby Weequays
  through pheromones that were undetectable to non-Weequays.** A private,
  proximity-limited channel. (Note the ceiling: *nearby*, and *Weequay-to-Weequay*
  only — do not inflate it into telepathy or long-range comms.)
- **Weequays could also be Force-sensitive.**

## Visual brief
🔴 **The six-colour skin list ("blue, brown, gray, pink, red, yellow") badly
misdescribes the canonical Weequay, and every image agrees against it.** The
full-body reference costume, the two-Weequay image and the live-action bartender
all show a **desaturated putty grey-brown** — the colour of dried clay or weathered
leather. There is no blue, red or yellow Weequay in any of the three images. Treat
the colour list as a menu of rare individual variation and the canonical hue as
**grey-brown putty**.

🔴 **"Weequays often kept their hair long" is far too vague, and it is the entry's
most valuable correction.** The images do not show generally long hair. They show a
**specific, highly recognizable arrangement: an otherwise BALD cranium with one
thick coarse ponytail / topknot growing from the back-side of the skull and hanging
forward over the shoulder, well past the chest.** In the reference costume it is a
single heavy dark-grey braid-like fall of hair on the figure's right. This
one-topknot-on-a-bald-head silhouette is what makes a Weequay read as a Weequay,
and a sprite given ordinary long hair loses it entirely.

Also from the images:
- **The skin is the other signature: a deeply creased, furrowed, cracked hide.**
  Vertical and radial furrows run over the entire face — brow, cheeks, muzzle,
  jaw — like cracked mud or tree bark. Not wrinkles-of-age; a whole-surface
  texture. This *is* the "tough, leathery skin" of the ability, made visible, and
  it should be preserved rather than smoothed.
- **The cranium is bald, high and domed**, with the furrowing continuing over it.
- **Small, dark, deep-set eyes** under a heavy creased brow — hard to see, sunken.
- **A short, broad, flattened nose** with small nostrils, barely projecting.
- **A wide, thin, downturned mouth**, and along the jaw a scattering of **small
  nodules/spines** — this is the text's "horns on the lower jaw / bumpy extensions
  of their skin", and in the reference costume it reads as a cluster of small
  bumps rather than true horns. Both variants are attested; the bumpy version is
  what the images show.
- **Otherwise fully humanoid proportions.** The reference costume wears a leather
  jerkin with shoulder pads, pale blue shirt sleeves, leather bracers, a wide belt
  with a round buckle and pouch, cream trousers and boots — **ordinary
  spacer/guard workwear**. A Weequay should read as a person in workwear with a
  cracked-leather head and one topknot; the species has no costume of its own.
- The **live-action bartender** confirms hue and furrowing in a modern production
  and shows the topknot again; the **two-Weequay** image confirms that the topknot
  and the furrowed hide recur across individuals rather than being one character's
  makeup.

**donor_current_sprite.png is weak evidence.** The copied file is
`SWX/Pawn/HeadAttachments/weequay/ChinSpines_south.png`: two small clusters of
black chin nodules, and nothing else. **There is no Weequay head sprite on
disk** — `SWX/Pawn/HeadType/` has no `weequay` directory — so the species is a
vanilla RimWorld head with overlays. Verified from the xenotype's gene list, what
IS wired: `RSW_Beard_chinspines` (this file — so the jaw nodules do land, as a
*beard* slot), `Head_Gaunt`, `Hair_BaldOnly`, `RSW_Skin_MidGray`,
`Outland_Skin_Brown` and several other skin colours, plus `Hair_Gray` /
`Hair_Blonde` / `Hair_DarkBrown` / `Hair_DarkBlack`. So grey-brown skin and jaw
nodules land. 🔴 **But `Hair_BaldOnly` is wired, which means the single most
recognizable Weequay feature — the one heavy topknot — cannot appear at all**, and
the four hair-colour genes present alongside it have nothing to colour. **Nothing
on disk supplies the cracked-hide surface texture either.**

## Must show
- [ ] Skin is a desaturated grey-brown putty colour (like dried clay/weathered leather), not blue, red or yellow
- [ ] Deeply creased, furrowed, cracked-hide texture over the whole face and cranium — a whole-surface texture, not age wrinkles
- [ ] Bald, high, domed cranium with one thick coarse topknot/ponytail growing from the back of the skull and hanging forward past the chest
- [ ] Small, dark, deep-set eyes under a heavy creased brow
- [ ] Small nodules/bumps scattered along the jaw (not true, tall horns)

## Engine limits
none known — the donor evidence shows the jaw nodules and grey-brown skin are already wired via existing genes; the missing topknot is attributed to the `Hair_BaldOnly` gene forcing every Weequay bald, and the missing cracked-hide texture to an absent head sprite, not to a pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Weequay (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Weequay&format=json&prop=wikitext`,
  31,517 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/5/54/PagettiRook-RotJAVA.png (File:PagettiRook-RotJAVA.png, the infobox image → wookieepedia_infobox_fullbody.jpg)
- https://static.wikia.nocookie.net/starwars/images/1/17/Weequays.png (File:Weequays.png → wookieepedia_two_weequays.jpg)
- https://static.wikia.nocookie.net/starwars/images/7/73/WeequayBartenderMando.png (File:WeequayBartenderMando.png → wookieepedia_bartender_liveaction.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/weequay (official Databank).

## Candidate images
- `wookieepedia_infobox_fullbody.jpg` — **the reference of record.** The infobox
  image (File:PagettiRook-RotJAVA.png): a full-body Weequay costume on a
  transparent background, photographic fidelity. Settles the putty grey-brown hue
  against the colour list, the whole-face cracked-hide furrowing, the bald dome, the
  single heavy topknot falling forward over the shoulder, the sunken dark eyes, the
  flat broad nose, the jaw nodules, and the ordinary leather-jerkin workwear.
- `wookieepedia_two_weequays.jpg` — two Weequays together; shows the topknot and
  the furrowed hide recurring across individuals, which is what makes them species
  traits rather than one character's makeup.
- `wookieepedia_bartender_liveaction.jpg` — a live-action Weequay from the
  Mandalorian era; independent modern-production confirmation of hue, furrowing and
  topknot.

## ruling
(empty — owner has not reviewed this race yet)
