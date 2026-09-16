# Ortolan

**defName**: `RSW_RimMandrakeOrtolan` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_HuttCartel: R`, `OutlanderCivil: R` — rare in both.
Note: `design/Jawa/race_regen_architecture.md` §4.2 refers to Ortolan as "already
shipped"; the def is present and this entry treats it as in.

Unlike the other three species in this batch, **the canon (Disney-era) article is the
substantive one** — the Ortolan has been on screen since *Return of the Jedi* (1983)
and has a real biology section. No `/Legends` fallback was needed.

## Sourced text (Wookieepedia)

**Canon article** (`/wiki/Ortolan`), infobox:

- **Class: elephantine** (Leland Chee, Holocron-keeper Instagram, 2024-08-03).
- **Skin colour: blue** (*Return of the Jedi*). **Eye colour: black.**
- **Distinctions: sensitive ears; two limbs; articulated nutrient-absorbing digits.**
- **Lifespan: 71+ years** (*Star Wars: Absolutely Everything You Need to Know*).
- Origin **Orto**; **habitat: ice and snow** (*Star Wars: The Visual Encyclopedia*);
  language **Galactic Basic Standard**.
- ⚠️ **Height and mass are BOTH empty in the infobox — unsourced.** The prose says
  "squat," and that is the only size information that exists. Do not invent a number.

**Biology and appearance** (canon, close to verbatim): Ortolans were a sentient,
**elephantine** species of **squat, blue-skinned bipeds** with **trunk-like noses** and
**two beady black eyes**. They also possessed **small mouths filled with blunted teeth
behind their noses** and **a pair of large, floppy ears** which were **sensitive to
sound** and **used to store fat**. 🔑 **"Ortolans fended off the cold of their icy and
snowy habitat by eating their way to a blubbery body"** — the species is a cold-world
species whose defining behaviour is continuous eating. **"They had two limbs which they
used both for walking and fine manipulation"** (the article's own odd phrasing, quoted
as written). 🔑 **"Their articulated digits were able to absorb food and drink as well
as play musical instruments"** — Ortolans **eat through their fingers**, which is the
species' single most unusual sourced ability. According to Inspector Thanoth, **their
secretions were "quite distinctive."** They spoke Galactic Basic. Average lifespan
**71+ years**. **Maximilian Rebo**, founder of the **Max Rebo Band**, was a male
Ortolan — the species' cultural signature is **musicianship**.

**Behind the scenes** (canon article): a StarWars.com piece on *Star Wars Resistance*
"The High Tower" describes a prop as **"an Ortolan doll (with extra limbs)"**, matching
**the Legends depiction** — i.e. **Legends Ortolans had more than four limbs; the
current canon Ortolan does not.** Worth knowing so old art with extra arms is not
mistaken for the modern species.

**Unusual abilities, summarised:** **nutrient absorption through the digits**;
**sound-sensitive ears** that double as **fat stores**; **cold tolerance by way of
blubber** rather than fur. **No Force sensitivity, no combat trait, and no intelligence
claim of any kind appears in the article.**

## Visual brief

The two references agree closely, and both are strong: one is a **live-action
screencap** (*The Book of Boba Fett*, so the current on-screen creature design) and one
a comic panel showing **two** Ortolans together.

- **Colour: mid-value blue, slightly desaturated and greyed, with faint darker
  mottling/freckling over the crown, shoulders and belly.** The comic shows the hue
  varying between individuals — one clear blue, one **blue-green/teal** — so a small
  hue spread is canonical, but nothing near a full colour menu.
- 🔑 **Silhouette is dominated by TWO features: the ears and the belly.** The **ears
  are enormous, narrow, tapering and PENDULOUS**, hanging from high on the skull down
  past the shoulders to roughly elbow level, and drooping forward. They are **not**
  round elephant fans — they are long soft lobes. The **belly is a single huge rounded
  mass** that the arms rest on; the torso has no waist.
- 🔴 **The eyes are LARGE, round, glossy and solid black — set wide and high on the
  skull with no visible sclera, iris, brow or lid.** The prose word "**beady**" is
  misleading and is exactly the kind of phrase a text-only prompt turns into tiny pin
  eyes. Trust the images: they are big, wet, doll-like black spheres. (This means the
  def's `RSW_Eyes_Big` is *correct*, unusually.)
- **The trunk is short-to-medium, thick at the base, tapering, and hangs straight down
  to about mid-chest** — an anteater/tapir proboscis, not a long prehensile elephant
  trunk and not a thin Kubaz snout. **No mouth is visible from the front at all**; the
  small blunt-toothed mouth is tucked behind and under the trunk.
- **The head is a broad rounded dome** continuous with the neckless body.
- **Arms are short and thick.** **Hands are small, blunt and have SEPARATE, clearly
  articulated short fingers with pale nails** — five per hand in the screencap, gripping
  a keyboard edge in one image and a satchel in the other. **They are dexterous.** This
  matters: canon says these digits both absorb food *and* play instruments.
- **No hair, no beard, no fur anywhere.** Skin is bare and slightly rubbery, with soft
  wrinkle folds at the joints and under the trunk.
- **Posture: seated or hunched forward, arms resting on the belly.** Both references are
  sedentary. No canon reference for an Ortolan walk or a fight pose was found.

🔴 **`donor_current_sprite.png` is not Ortolan art. There is NO Ortolan texture anywhere
in `src/`** (a repo-wide search for `ortolan` returns nothing at all). The sprite here is
`RimMandrakeSW/SWX/Pawn/HeadType/kubaz/Male_Kubaz_south.png`, which is what the def's
`RSW_Head_kubaz` gene actually forces the game to render. It is a **narrow tapered
cranium with a thin bristly snout and small angry slanted eyes** — the opposite of the
Ortolan head in every respect that matters: the dome is narrow instead of broad, the
proboscis is thin and stippled instead of thick and smooth, and the eyes are small
slits instead of large black spheres. Treat it as a **negative reference**: it documents
the bug, not the species. (One mitigation: the Kubaz head base carries no
`useSkinShader: false`, so the blue skin genes *will* tint it — the shape is wrong, not
the colour.)

## Def-versus-canon (flagged — not fixed)

- 🔴 **`RSW_Head_kubaz` is the wrong species' head.** An Ortolan is a broad dome, a
  thick drooping trunk and two huge black eyes; the Kubaz head is a narrow skull with a
  thin bristled snout and small slitted eyes. This is the biggest defect in the def.
- 🔴 **`Hands_Pig` directly contradicts the species' one unique canon ability.** Canon:
  *"their articulated digits were able to absorb food and drink as well as play musical
  instruments,"* and both reference images show separate short fingers with nails
  gripping objects. Trotters cannot do that. Relatedly, **nothing in the def represents
  nutrient-absorbing digits at all** — the species' signature trait is simply absent.
- 🔴 **Nothing represents the sound-sensitive ears.** `Ears_Floppy` gets the shape
  (correctly — see below) but **the hearing acuity, the single sourced sense in the
  article, has no gene**, and neither does the ears' canon role as **fat storage**.
- 🔴 **No `nameMaker`.** Ortolan pawns will get default human names. (Compare
  `RSW_RimMandrakeNelvaanian`, which does have a species namer.)
- ⚠️ **`Body_Hulk` contradicts "squat."** `Body_Fat` is well sourced — the species
  deliberately eats itself blubbery — but *hulk* reads as tall and powerfully built, and
  no source supports it. Nothing in the def makes an Ortolan **short**, which is the
  one shape word canon actually uses. (Height is unsourced, so a specific number cannot
  be claimed either way.)
- ⚠️ **`Learning_Slow` and `AptitudePoor_Cooking` are unsourced.** The article makes no
  intelligence claim about Ortolans at all, and `AptitudePoor_Cooking` is a strange
  choice for a species whose defining behaviour is **consuming large amounts of food**.
  🔑 Meanwhile the species' most famous cultural fact — **musicianship, the Max Rebo
  Band, digits built to play instruments** — has **no artistic aptitude gene**. The def
  has the sign backwards on the two traits canon actually comments on.
- ⚠️ **`Nearsighted` and `Immunity_Strong` are unsourced.** Neither vision nor disease
  resistance is mentioned anywhere in the article.
- ⚠️ **No eye-colour gene for the sourced BLACK eyes.** `RSW_Eyes_Big` gets the size
  right (the images beat the word "beady" here) but not the colour.
- ⚠️ Cosmetic but telling: **`iconPath` is the vanilla `UI/Icons/Xenotypes/Pigskin`**,
  and the hands gene is `Hands_Pig`. The Ortolan appears to have been built by
  reskinning a pig. The canon classification is **elephantine**.
- ✅ **Correct and worth keeping:** `MinTemp_LargeDecrease` (sourced — **icy, snowy
  homeworld**, and the blubber exists to fight the cold); `Body_Fat`; `Ears_Floppy`
  (sourced **large floppy ears**, and the images show them as the dominant silhouette
  feature); `Skin_Blue` + `Outland_Skin_PaleAzure` (sourced blue, with the mild
  individual hue spread the comic shows); `RSW_Eyes_Big` (matches the images);
  `Hair_BaldOnly` + `Beard_NoBeardOnly` (correct — no hair anywhere);
  `StrongStomach` + `RobustDigestion` (defensible from *"consumed large amounts of
  food"*); **no lifespan gene** — correct, since the sourced **71+ years** is close to a
  vanilla human and needs no modifier. **No psychic or Force genes** — correct, nothing
  is sourced.

## Source URLs

- https://starwars.fandom.com/wiki/Ortolan — canon article, and the substantive one.
  Direct page HTML is Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Ortolan&format=json&prop=wikitext`
  (12,004 bytes of JSON), 2026-09-15. Source of every fact above.
- https://static.wikia.nocookie.net/starwars/images/3/3f/MaxRebo-BoBFCh2.png
  (File:MaxRebo-BoBFCh2.png, the canon infobox image, *The Book of Boba Fett* "Chapter
  2: The Tribes of Tatooine" → `wookieepedia_max_rebo_bobf.jpg`)
- https://static.wikia.nocookie.net/starwars/images/7/7e/Azool_and_Max.png
  (File:Azool and Max.png, wiki caption *"Maximilian Rebo and Azool Phantelle, two
  Ortolans"* → `wookieepedia_azool_and_max.jpg`)
- `https://www.starwars.com/databank/` — **not fetched this pass.** The article cites a
  Databank entry for *Garsa's Sanctuary*, not for the species; no species-level Databank
  page was attempted.
- Not consulted: *Star Wars: Alien Archive*, *Ultimate Star Wars*, *Star Wars Character
  Encyclopedia: Updated and Expanded*, *The Visual Encyclopedia* — only Wookieepedia's
  transcription of them.
- `/wiki/Ortolan/Legends` was **not** fetched: the canon article is complete enough, and
  the canon article itself warns that the Legends depiction **had extra limbs**, so
  Legends art is a hazard rather than a help for this species.

## Candidate images

- `wookieepedia_max_rebo_bobf.jpg` — **the reference of record.** The canon infobox
  image: a live-action screencap of Max Rebo seated at his keyboard in *The Book of Boba
  Fett*. Settles the mid-blue mottled skin, the enormous pendulous ears hanging to elbow
  level, the thick tapering trunk to mid-chest with no visible mouth, the two large
  round glossy **black** eyes set wide and high, the neckless single-mass belly, the
  short thick arms, and the small blunt hands with **separate articulated fingers and
  pale nails**. Practical creature effect rather than an artist's interpretation, so
  this is the strongest possible evidence.
- `wookieepedia_azool_and_max.jpg` — a comic panel with **two** Ortolans together
  (Max Rebo and Azool Phantelle). Stylised line and flat colour, so read the palette as
  the colourist's — but its value is confirming that the **ear/trunk/belly arrangement
  recurs across individuals** while the hue shifts (one blue, one blue-green/teal), and
  it shows the hands **gripping** an object, corroborating real dexterity.
- `donor_current_sprite.png` — 🔴 **negative reference.** Not Ortolan art; it is the
  **Kubaz** head (`.../HeadType/kubaz/Male_Kubaz_south.png`) that the def's
  `RSW_Head_kubaz` gene forces. Kept to document the defect. **No Ortolan texture exists
  anywhere in `src/`.**

## ruling
(empty — owner has not reviewed this race yet)
