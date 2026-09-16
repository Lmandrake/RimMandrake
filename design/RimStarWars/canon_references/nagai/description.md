# Nagai

**defName**: `RSW_RimMandrakeNagai` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`)

## Sourced text (Wookieepedia)

⚠️ **The canon article is a stub** (6,480 chars, tagged `{{Expand|this page needs
expanding on all sections}}`) built almost entirely from the 2025 *Star Wars* comic
run. **Almost all substance for this species lives on the `/Legends` page** — that
page-title trap applies here more than for any other species in this batch.

**Canon.** Nagai were a sentient humanoid species hailing from the astronomical object
**Nagi**. Infobox: class **humanoid**; **skin colour pale white**; **hair colour
black**; 🔑 **eye colour RED**; distinctions **pointy ears**; origin Nagi. **Height,
mass and lifespan are blank in the canon infobox.** Biology and appearance, in full —
this is the entire canon section: *"The Nagai were a sentient humanoid species with
black hair, a pair of red eyes, and pale white skin. They also had distinct pointy
ears and **face markings unique to each member**."*

Society: individuals were **brave and strong-willed**, taking opportunities to rescue
one another and rebel for their freedom; they communicated verbally in Galactic Basic
Standard. History: by the New Republic era the Nagai had been **forcibly removed from
their homeworld to work in labour camps** by the Zantarrk Gang and the Fenril
Consortium, after the betrayal of the Nagai **Gallana Venk**.

**Legends** (also called the **N'Gai** and 🔑 **"the Knives"**). Infobox: class
**mammalian**; **height 1.8 meters**; **skin pale white**; **hair black**; **eye
colour gray**; distinctions **individualistic expression forms**; origin **Nagi**, a
planet in the dwarf satellite galaxy **Firefist** orbiting the galactic disk in the
**Unknown Regions**; language Nagaian.

Biology and appearance: **the Nagai were tall and thin near-humans with pale skin,
jet-black hair, gray eyes, and angular features.** **Considered attractive, yet gaunt
and frail looking by galactic standards, they were aware of the effect their
appearance had on others, and often allowed others to see them as weak until the time
was right to reveal their true skills.** **Possessing lightning fast reflexes, the
Nagai were known for their speed and agility in and out of combat**, with much of
their clothing — like traditional **Electromesh** armour — tailored around their
natural dexterity.

🔑 **The one genuinely unusual ability, and it is well sourced:** *"Nagai were noted
as being especially charismatic; a quality that was by and large the product of their
**enhanced vocal range**, allowing them to modulate and tailor their speech.
Described as incredibly **soothing and hypnotic**, a Nagai could **use their voice to
influence other sentient beings** — provided their voice could be heard, and their
words understood."*

Also: *"Despite their ubiquitous reputation as pale specters, Nagai were well known
for their **individualistic expression**, with clothing and hair styles varying
wildly from individual to individual depending on personal tastes and the image that
a Nagai wanted to convey."*

⚠️ **Canon and Legends disagree on eye colour**: canon **red**, Legends **gray**.
See the visual brief — the images side with red.

## Visual brief

🔴 **The def sets `Eyes_Gray`. Canon says red, and THREE of the four images show red
or red-amber eyes. This is the headline finding for this species.**

**`wookieepedia_gallanavenk_2025starwars2.png` is the reference of record** (Gallana
Venk, the canon infobox image, from *Star Wars* (2025) 2 — comic art, so read shapes
and colours rather than rendering):

- **Skin is a cold, chalky blue-white** — not warm ivory. The shadows go **grey-blue**,
  which is what makes the "pale specter" reputation read on the page. A warm pale
  human skin tone is the wrong answer.
- 🔑 **Eyes are RED/orange-red irises**, and they are the only warm colour on the face.
- **Ears are long, narrow, pointed and swept back and outward**, projecting clearly
  beyond the skull — elf-like, and much more prominent than "pointy ears" suggests.
- 🔑 **FACE MARKINGS: a thick dark grey-black horizontal BAR beneath each eye,
  spanning the cheekbone, with short vertical drip-lines running down from it.**
  Canon says these markings are **unique to each member**, so the bar is Gallana's
  own, not a species uniform — but a *dark, hard-edged, blocky* marking on the
  cheek/under-eye area is the canonical *kind*. Also **dark, near-black lips.**
- **Hair is jet black, worn as a stiff upright crest/mohawk** sweeping back off the
  crown.
- **The face is lean and angular** — high flat cheekbones, narrow jaw, sunken cheeks.

**`wookieepedia_nagai_g01p65.jpg`** (the Legends infobox image) is the **"the Knives"
picture** and confirms the build: **very tall, very thin, wiry**, narrow shoulders,
long thin limbs, a gaunt angular face with hollow cheeks, **stark white skin**, and a
huge wild spiky black mane. **Festooned with knives and daggers** on belt, bandolier,
thigh and boot. Note two things: the **ears are not visible here** (buried in hair),
and there are **no face markings** — consistent with Legends, which never mentions
them.

**`wookieepedia_nagai_turcov.jpg`** (a painted Legends cover) is the most
photographically-lit reference: **cool grey-white skin, long loose black hair, gaunt
face with severe cheekbones, lean muscular build**, wielding a sword. 🔑 **Its eyes
read clearly RED-AMBER, not gray** — so even the Legends-era painted art leans toward
the canon eye colour, and `Eyes_Gray` is supported by a single infobox field against
the weight of the pictures.

**`wookieepedia_nagai_telepath.jpg`** is **weak evidence and mostly costume**: a
Legends figure almost entirely enclosed in a wide-brimmed hat and voluminous
blue/purple robes. The little face that shows is **pale green-white, long, narrow and
downcast**. It contributes nothing on ears, eyes, markings or build. Keep it as a
fourth data point on pallor and the long narrow face; do not draw from it.

**There is no `donor_current_sprite.png` in this directory** — no Nagai-specific head
art was harvested, and the def uses the generic `Outland_SvelteHead` rather than a
species head. So there is currently **nothing Nagai-specific to critique on disk**,
and equally **nothing carrying the ears or the face markings.**

**Xenotype-versus-canon findings:**

- 🔴 **`Eyes_Gray` contradicts canon.** Canon eye colour is **red** — it is one of
  only five facts the canon article states — and the paintings agree. `Eyes_Gray`
  follows the **Legends** infobox. Given red eyes plus chalk-white skin is the
  species' entire visual signature, this is the most valuable single fix here.
  (Side note worth knowing, since Pantorans are also in this mod: red eyes on
  blue-white skin is exactly the **Chiss** silhouette, and the Pantoran entry
  records that Chiss get mistaken for Pantorans. Nagai, Chiss and Pantoran will all
  want distinguishing.)
- 🔴 **The canonical "face markings unique to each member" are not represented at
  all.** No marking gene, and no species head to carry one. This is a stated canon
  *distinction*, on par with the pointed ears — and the repo already knows how to do
  this, because `RSW_MirialanHead` bakes markings into a head mask.
- ⚠️ **`Aggression_Aggressive` is unsourced, and the def's description overreaches.**
  The `<description>` calls them *"an aggressive, honor-bound people."* Neither
  article says that: **canon** calls them **brave and strong-willed**, and
  **Legends** emphasises that they are **charismatic, individualistic, and
  deliberately appear weak until it suits them** — closer to guile than aggression.
  No "honour-bound" claim appears in either page I retrieved.
- ⚠️ **The description's "originate from a dwarf galaxy in Wild Space" is off.**
  Legends places Nagi in the dwarf satellite galaxy **Firefist**, in the **Unknown
  Regions**; canon just calls Nagi an "astronomical object". Wild Space and the
  Unknown Regions are not the same region.
- 🔴 **The enhanced vocal range / hypnotic persuasive voice is not represented as an
  ability.** `AptitudeStrong_Social` is a reasonable partial stand-in and is
  well-earned, but the sourced claim is a genuine influence power, not just skill.
- ⚠️ `RSW_BodySizeGene_big` may overshoot: the only sourced height is **1.8 m
  (Legends)**, which is tall-but-human. "Tall and thin" is right; *large* is a
  different claim. `RSW_Body_gaunt` + `Body_Thin` are exactly right.
- ✅ Correct and well-sourced: `Skin_SheerWhite` (pale white, both versions),
  `Hair_InkBlack` (black, both versions), `Ears_Pointed` (a stated canon
  distinction), `Outland_SvelteHead` ("angular features"), `Outland_Evasive` +
  `AptitudeStrong_Melee` ("lightning fast reflexes… speed and agility in and out of
  combat", and the nickname "the Knives"), `AptitudeStrong_Social` ("especially
  charismatic"), and `Turn_Gene_FreeSpirit`, which lands squarely on the sourced
  "well known for their individualistic expression."
- ⚠️ `Beard_NoBeardOnly` — no canon basis found either way.

## Must show
- [ ] Cold, chalky blue-white skin with grey-blue shadows — not warm ivory
- [ ] RED or red-amber eyes — the only warm colour on the face
- [ ] Long, narrow, pointed ears swept back and outward, projecting clearly beyond the skull
- [ ] Thick dark grey-black horizontal bar beneath each eye spanning the cheekbone, with short drip-lines running down from it
- [ ] Jet-black hair worn as a stiff upright crest/mohawk sweeping back off the crown
- [ ] Lean, angular, gaunt face — high flat cheekbones, narrow jaw, sunken cheeks, on a tall thin wiry build

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/Nagai (canon article, a **stub**; direct HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Nagai&format=json&prop=wikitext`,
  6,480 chars, 2026-09-15)
- https://starwars.fandom.com/wiki/Nagai/Legends (**where the substance is**;
  wikitext via `api.php?action=parse&page=Nagai/Legends&...`, 17,361 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/0/02/Nagai-G01p65.jpg → `wookieepedia_nagai_g01p65.jpg`
- https://static.wikia.nocookie.net/starwars/images/2/29/Nagai_telepath.jpg → `wookieepedia_nagai_telepath.jpg`
- https://static.wikia.nocookie.net/starwars/images/b/be/Nagai-TURcov.png → `wookieepedia_nagai_turcov.jpg` (saved with a `.jpg` name; the source file is a PNG)
- `wookieepedia_gallanavenk_2025starwars2.png` corresponds to
  `File:GallanaVenk-2025StarWars2.png`, the canon infobox image. It was already on
  disk from an earlier pass and was verified against the article's own file list
  this pass.
- NOT fetched this pass, and named so nobody assumes it was read: the print sources
  the Legends page cites for every appearance and ability claim —
  *Ultimate Alien Anthology* (skin, hair, distinctions, the hypnotic voice, the
  "appear weak" behaviour) and *Legacy Era Campaign Guide* (the 1.8 m height, the
  charisma/vocal-range claim, Nagaian language). No `starwars.com/databank` entry
  for this species was located or attempted.

## Candidate images

- `wookieepedia_gallanavenk_2025starwars2.png` — **the reference of record.** The
  canon infobox image (Gallana Venk, *Star Wars* (2025) 2). Settles chalk-blue-white
  skin, **red eyes**, long swept-back pointed ears, jet-black crest hair, and the
  canonical **dark under-eye bar face marking with drip lines**. Comic art, so read
  the shapes and colours, not the linework.
- `wookieepedia_nagai_g01p65.jpg` — the Legends infobox image. **The build
  reference**: very tall, wiry-thin, gaunt angular face, stark white skin, huge
  spiky black hair, and covered in knives (hence "the Knives"). No visible ears, no
  face markings.
- `wookieepedia_nagai_turcov.jpg` — a painted Legends cover. Best-lit reference for
  skin (cool grey-white), hair, cheekbone structure and lean musculature — and 🔑
  **its eyes read red-amber, siding with canon against the def's `Eyes_Gray`.**
- `wookieepedia_nagai_telepath.jpg` — **weak evidence, mostly costume.** A robed and
  wide-hatted Legends figure; contributes only pallor and the long narrow face. Do
  not draw appearance conclusions from it.

## ruling

(empty — owner has not reviewed this race yet)
