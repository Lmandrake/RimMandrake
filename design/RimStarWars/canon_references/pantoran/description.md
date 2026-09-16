# Pantoran

**defName**: `RSW_RimMandrakePantoran` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`)

## Sourced text (Wookieepedia)

The Pantorans were **blue-skinned near-humans** native to the **moon Pantora**. They
were part of the Galactic Republic during the waning years of that government.
Infobox: class **near-human**; 🔑 **skin colour BLUE — a single entry, not a menu**;
**hair colour pastel colours, black**; **eye colour gold, black, blue**; origin
**Pantora**; **habitat marshy tundra**; language Galactic Basic Standard.
**Lifespan is blank — do not invent it.**

**Body.** Pantorans looked very similar to humans: **two legs, two arms ending in
five-fingered hands, a torso and a single head**. They had **blue skin that turned
INDIGO WHEN THEY BLUSHED**, and **yellow eyes** — though at least one Pantoran was
known to have blue eyes. **They grew hair on the top of the head, and, in males, on
the lower parts of the face.** The colour of their hair **varied from white and purple
to blue and black**. 🔑 **Known individuals ranged from 1.65 to 1.77 meters in
height** — squarely human, so no size gene is warranted.

**Markings.** *"Some Pantorans also displayed simple **golden facial tattoos** known
simply as **Pantoran tattoos** as a **status symbol** or to represent their **clan and
family**. Given to a Pantoran during **childhood**, these tattoos were **based on
ancient Pantoran texts**."* ⚠️ **Not every Pantoran has them** ("some"), and they mark
clan/status — a different meaning from Mirialan tattoos, which mark personal
achievements. Keep the two straight.

**Unusual abilities.**
- 🔑 **Cold resistance, and it is the best-sourced trait they have:** *"The Pantorans
  had a **greater resilience to low temperatures than humans**, showing **no signs of
  discomfort or unease in the frigid environment of Orto Plutonia** that humans could
  only survive in by wearing special insulated clothing."*
- 🔑 **Exceptional hearing**, stated in-universe by the Pantoran Cuata to Luke
  Skywalker: *"Don't whisper around a Pantoran, boy! **Our hearing is exceptional.**"*
- **Possibly different visual spectrum, but explicitly uncertain:** Kevmo Zink
  *"suspected that Rodians and Pantorans saw light across a different spectrum **but
  was unsure what the exact difference was**."* Speculative in-universe — do not
  promote it to a fact.

🔴 **Species-confusion warning that matters inside this mod.** *"The **Chiss**, a more
obscure blue-skinned species, were **sometimes mistaken for Pantorans**. However,
unlike the Pantorans, **the Chiss had red eyes**. On one occasion, the Chiss Imperial
Navy officer Mitth'raw'nuruodo wore dark glasses to hide his red eyes, and pose as a
Pantoran."* So **eye colour is the canonical discriminator between blue-skinned
species**: Pantoran = gold/yellow, Chiss = red. Note that this repo's **Nagai** def
also pairs pale-blue-white skin with the wrong eye colour — see `nagai/description.md`.
Blue-skinned humanoids need their eyes right or they collapse into each other.

## Visual brief

**The def's description ("blue skinned… commonly have golden facial markings…
capable of surviving in lower temperatures") is unusually accurate for this library.
The images refine two things: the blue is LIGHT and desaturated, and the markings are
not always gold.**

**`wookieepedia_papanoida_body_shot.png` is the reference of record** (Chairman
Papanoida, the canon infobox image, full body, live-action costume):

- 🔑 **The blue is PALE, cool and desaturated — a light periwinkle/ice blue**, not a
  saturated primary blue and not teal. A strong bright blue is the likely wrong answer
  from a one-word colour field.
- **Eyes are striking GOLD/YELLOW.**
- **White-grey hair and a short white-grey beard** — confirming the canon "white" hair
  entry and the "males grow hair on the lower parts of the face" line. **Pantoran
  males are bearded; do not force them beardless.**
- **Small GOLD/amber facial marks high on the cheekbone and temple** — sparse and
  simple, exactly as "simple golden facial tattoos" says.
- **Entirely human proportions and features** otherwise: human nose, human ears, human
  hands, human build. Pantoran appearance work is **skin hue + eye colour + facial
  markings + hair**, and nothing structural.

**`wookieepedia_pantoran_prisoner_sav.png`** (a male Pantoran of Black Sun,
painted close-up) is the second reference of record and **it contradicts the "golden"
generalisation, loudly**:

- 🔑 **This individual's tattoos are LIGHT BLUE-WHITE, not gold** — a large circular
  sunburst/ring emblem centred on the forehead, plus dense fine linework across the
  cheeks, jaw, throat and neck. **So Pantoran tattoos are not necessarily gold and are
  not necessarily confined to the face.** The prose only ever says *some* Pantorans
  have *golden* ones; this is evidently a different tradition or a different clan, and
  it is far more elaborate.
- **Deeper, more saturated blue skin** than Papanoida, with lighter blue highlights —
  so the hue range within "blue" is real.
- **Gold/yellow eyes** again, with dark pupils. **Slicked-back black hair** — the canon
  "black" hair entry.
- Human face throughout.

**`wookieepedia_pantoran_camping.jpg`** is a third painted reference: light-blue skin,
**blue-white hair swept back**, human build, no visible facial markings — a useful
reminder that **markings are optional** ("some Pantorans").

**`donor_current_sprite.png` — GOOD NEWS, and unusual for this library.** It is the
`RSW_PantoranHead` mask, and unlike the other heads in this batch it is **not purely
greyscale**: the head shape is a runtime-tinted grey mask, but the **facial markings
are baked in as actual GOLD** — four-pointed star/spike shapes above and below each
eye. That is canon-correct in colour (the "simple golden facial tattoos"), correct in
character (simple, geometric, sparse), and correct in placement (around the eyes on the
cheekbone). ✅ **The gold is deliberate and right; do not "fix" it to greyscale.** The
only shortfall is that it is one fixed pattern for every Pantoran pawn, where canon
makes the tattoos **clan- and family-specific and only present on some individuals**.

**Xenotype-versus-canon findings:**

- ✅ **`Skin_Blue` alone is correct.** Canon lists exactly one skin colour. Resist the
  urge to add a colour menu here — the restraint is the accurate choice.
- ✅ **`MinTemp_LargeDecrease` is the best-sourced gene on this def.** It matches the
  Orto Plutonia passage directly.
- ✅ **`RSW_PantoranHead`** carries the canonical gold markings (see above).
  **`Body_Standard`** is right for a 1.65–1.77 m near-human.
- 🔴 **Exceptional hearing is sourced canon and is not represented.** It is stated
  in-universe, in dialogue, as a species trait. Nothing in the gene list touches it.
- 🔴 **No eye-colour gene, and eye colour is this species' canonical discriminator.**
  Canon gives **gold, black, blue**; **both close-up references show striking gold**;
  and the article explicitly uses eye colour to tell Pantorans from Chiss. This is the
  highest-value appearance fix.
- ⚠️ **Hair set: `Hair_SnowWhite`, `RSW_Hair_DarkBlue`, `RSW_Hair_Lavender`,
  `Hair_Pink`, `Hair_BrightRed`, `Outland_HairColor_BrightAzure`.** White, blue,
  lavender and pink are all supportable as "pastel colours". But **`black` is in the
  canon infobox and there is no black hair gene** — and the Black Sun reference has
  black hair. **`Hair_BrightRed` is unsourced** and is not a pastel.
- ⚠️ **`Immunity_Weak`, `Beauty_Pretty` and `Turn_Gene_HighBeautyStandard` are all
  unsourced.** Nothing in the article says Pantorans are frail, unusually attractive,
  or unusually demanding about looks.
- ⚠️ **`Hair_Grayless` is unsourced and sits awkwardly with the images** — the infobox
  image is an older Pantoran with white hair and a white beard.
- **Not representable, and worth recording rather than hiding**: skin turning
  **indigo when blushing**; the tattoos being clan-specific, childhood-applied, and
  present on only *some* individuals; and the speculative different-visual-spectrum
  line (which should stay speculative).

## Source URLs

- https://starwars.fandom.com/wiki/Pantoran (canon article; direct HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Pantoran&format=json&prop=wikitext`,
  25,592 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/b/bf/Camping_Pantoran_FDSS.png → `wookieepedia_pantoran_camping.jpg` (saved with a `.jpg` name; the source file is a PNG)
- https://static.wikia.nocookie.net/starwars/images/e/e2/RiyolaKeevan-TravelWeekly.jpg — resolved this pass but **not** copied into this directory; three references plus the donor sprite were sufficient.
- `wookieepedia_papanoida_body_shot.png` corresponds to `File:Papanoida_body_shot.png`
  (the canon infobox image) and `wookieepedia_pantoran_prisoner_sav.png` to
  `File:Pantoran_Prisoner_SaV.png`. Both were already on disk from an earlier pass and
  were verified against the article's own file list this pass.
- NOT fetched this pass: https://www.starwars.com/databank/pantoran (the article's
  `{{Databank|pantoran}}` citation, and the source of the blue-skin claim), plus the
  two Databank pages that carry the only sourced heights —
  https://www.starwars.com/databank/chi-eekway-papanoida (1.65 m) and
  https://www.starwars.com/databank/chairman-papanoida (1.77 m). Print sources cited
  and not read: *Star Wars: The Visual Encyclopedia* (marshy-tundra habitat, tattoos
  as status symbol), *The High Republic: Path of Deceit* (tattoos given in childhood,
  the light-spectrum speculation), and *Thrawn* (the Chiss/Pantoran confusion).

## Candidate images

- `wookieepedia_papanoida_body_shot.png` — **the reference of record.** The canon
  infobox image: Chairman Papanoida, full body. Settles the **pale desaturated
  periwinkle blue**, **gold eyes**, **white hair and beard**, sparse **gold cheekbone
  markings**, and fully human proportions.
- `wookieepedia_pantoran_prisoner_sav.png` — **second reference of record, and the
  important corrective.** A Black Sun Pantoran, painted close-up: deeper blue skin,
  **light blue-white tattoos** (forehead sunburst plus dense cheek/jaw/neck linework)
  rather than gold, gold eyes, black hair. **Proof that Pantoran markings are not
  always golden and not always face-only.**
- `wookieepedia_pantoran_camping.jpg` — a third painted reference. Light blue skin,
  blue-white swept-back hair, **no facial markings** — the reminder that markings are
  optional.
- `donor_current_sprite.png` — the repo's `RSW_PantoranHead` mask. Kept as a
  **positive** reference: the four-pointed markings around the eyes are **baked in as
  real gold**, which is canon-correct in colour, character and placement. Its only
  limitation is being one fixed pattern on every Pantoran, where canon makes the
  tattoos clan-specific and optional.

## ruling

(empty — owner has not reviewed this race yet)
