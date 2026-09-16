# Zabrak (Iridonian)

**defName**: `RSW_RimMandrakeIridonian`, label `Iridonian`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, verified present).
Matrix placement: `TribeCivil: R`. Directory slug is `zabrak` because Wookieepedia's *species*
article is **Zabrak**; see the ruling on scope immediately below.

## 🔑 One species or two? — canon distinguishes them, and the def means the Iridonian subgroup
**Canon treats Iridonian as a subgroup of Zabrak, not a separate species, and it maintains both
articles.**
- The **Zabrak** article's infobox lists `subspecies = Dathomirian, Iridonian` (*Star Wars: The
  Visual Encyclopedia*), and the body states: *"There were two subspecies of Zabraks, the
  Dathomirians and the Iridonians."*
- The **Iridonian** article's infobox gives `class = Zabrak`, and its lead reads: *"Iridonians,
  also known as **Iridonian Zabraks**, were a **race** of the sentient **Zabrak species** native
  to the planet Iridonia."* ("Subspecies" and "race" are both used; the containment is
  unambiguous either way.)
- So: **Iridonian ⊂ Zabrak.** Not a distinct species, and not a mere demonym either — it is a
  named, visually distinguished subgroup with its own infobox.

🔑 **The def plainly means the Iridonian subgroup, and it means it correctly.** Its
`<description>` reads: *"Iridonians are a subspecies of Zabrak from the planet Iridonia, besides
having a crown of horns they are largely indistinguishable from humans"* — which is a **faithful
and precise** restatement of canon, unusually so for this batch. `nameMaker` is
`RSW_KoTOR_NamerIridonian` and the face gene is `RSW_FacialRidges_iridonian`; the intent is
consistent throughout.

🔴 **The consequence for the artist: the Iridonian is the Eeth Koth look, NOT the Darth Maul
look.** Maul is a **Dathomirian** Zabrak — the *other* subspecies — and this mod ships
`RSW_RimMandrakeDathomirian` as a separate xenotype. If the Iridonian sprite is drawn red-and-black
with tall spikes, the two defs become indistinguishable and the mod loses a distinction canon
makes. Both reference images for each are included here so the difference is visible side by side.

## Sourced text (Wookieepedia)
**Zabraks** were a **near-human, carnivorous** species native to **Iridonia** and **Dathomir**.
🔴 **The canon Zabrak infobox is almost entirely empty**: no height, no length, no mass, **no
skin colour, no hair colour, no eye colour**, no lifespan, no habitat. Its `distinctions` are
**vestigial horns, two hearts, facial tattoos**; diet **carnivorous**; language **Zabraki**.
The article carries `{{Expand|all sections}}`.

Biology: **Zabraks had evolved to be tough due to the nature of their homeworld Iridonia.** The
species was carnivorous and 🔑 **had two hearts, which allowed them to pump oxygenated blood
around their systems more quickly than other species meaning they could go faster for longer** —
a sourced trait with an explicit stated *mechanical* effect. **Some Zabraks possessed a ring of
small, vestigial horns that ran from high on their brow round to the back of their head. The
horns of males were generally more developed than those of females, although horn placement,
length, and thickness varied enormously across the species.** Zabraks **could be
Force-sensitive.** **Female Dathomirians did not have any horns, but males did.**

Society: **all Zabraks were fiercely independent**, usually taking roles that minimised being
ordered around; **mistaken by other species for aloofness or arrogance, which was erroneous,
although Zabraks were unashamedly proud of being survivors.** 🔑 **The majority of Zabraks wore
facial tattoos which often indicated familial ties, but could also simply be based on an
individual's personal taste.** 🔴 **They were a colonial species, having migrated and adapted to
dominate many worlds.** Iridonian Zabraks were commonly seen across the galaxy as **Jedi, bounty
hunters, independent traders, mercenaries or scouts**; criminal pursuits were often attractive to
younger Zabraks. Politically they were loyal to the Republic, **immediately opposed to the
Galactic Empire**, and many joined the Rebel Alliance and later the Resistance.

The **Iridonian** article supplies the colour data the Zabrak article lacks, all for Iridonians
specifically: skin **light, tan, light tan, dark, and moonlight-blue**; hair **black** and
**purple**; eyes **black, brown, light brown**. It gives **no height, mass or lifespan** and
carries `{{Species-stub}}`. Its named members are the Jedi **Eeth Koth** and **Agen Kolar**.

Because canon gives no size at all, **`Zabrak/Legends` was pulled** and is marked Legends
throughout: height **1.8 metres**, lifespan **80 years**, `distinctions` **horns, facial tattoos,
two hearts**, `subspecies` **several, distinguished by the number and pattern of horns.** Legends
adds that the **horns developed at puberty**, growing in patterns that identify the subspecies and
signalling an approaching rite of passage; that Zabraks shared some human eye pigments (blue,
green, grey) but **also had distinct colours such as orange and bright yellow**; that they
**typically covered their bodies in ritual tribal tattoos** symbolising lineage, birthplace or
personality; that they possessed **a second heart** and 🔑 **great resistance to physical pain**;
and that they **could breed with humans.** 🔑 Most usefully, Legends splits the two visual groups
explicitly: **the first, which included Zabraks from Iridonia, had horns that were STUMPED, and
features that resembled those of humans relatively closely, with skin tones ranging from pale to
dark brown and fairly common human hair colours including blonde, brown, red and black**; the
second group **had sharper, more jagged horns**, were **more distinct from humans**, with skin
tones including **red, yellow and orange.** Personality: proud, strong, confident, single-minded,
believing nothing was truly impossible.

## Visual brief
**The Iridonian face, from `wookieepedia_iridonian_eeth_koth.jpg`** — the Iridonian article's own
infobox image, and therefore the reference of record for this def:
- 🔑 **A crown of SHORT, BLUNT, CREAM-IVORY horns** — roughly seven readable — running in an arc
  across the top of the brow and continuing round the sides of the head, with the two at the
  temples projecting laterally and slightly back. They are **stubby cones, not spikes**: the
  tallest is maybe a third the height of the forehead. **Bone-coloured, distinctly paler than the
  surrounding skin.** This is Legends' "stumped" horn exactly, and it is what separates an
  Iridonian from a Dathomirian at a glance.
- **Pale tan / sallow yellow-ochre skin**, with an otherwise **entirely human face structure** —
  human nose, human mouth, human ears, human eye placement. The def's "largely
  indistinguishable from humans" is accurate.
- **Small raised nodules or bumps scattered on the forehead** between the horns — a subtle
  secondary texture, easy to miss and worth having.
- 🔑 **Fine, delicate dark tattoo lines on the chin and lower cheeks** — thin curved and vertical
  strokes in a symmetric pattern. **Line weight is hairline, not bold blocks.** This is the
  Iridonian tattoo idiom, and it is nothing like Maul's.
- 🔴 **Long, straight, jet-black hair past the shoulders**, worn in side braids with metal
  clasps — **on a MALE Iridonian.** This directly matters to the def (see below).
- **Ordinary human build and height**, in brown-and-cream Jedi robes.

**A second, independent Zabrak reference, `wookieepedia_infobox_zabrak.jpg`** (the Zabrak
article's own infobox, a *Battlefront*-era game render of a female Zabrak):
- **Bald**, with the **same crown of short blunt cream horns** ringing the hairline.
- **Pale, light skin**; human features; **fine dark markings radiating from the brow** rather than
  bold tattoo blocks.
- **Ordinary human proportions and height**, athletic, in a rust-and-ochre flight jacket with a
  blaster rifle.
- Confirms two things: **both bald and long-haired Zabraks are attested**, and **the short blunt
  horn crown recurs across individuals and media** — it is the species trait, and it is *always*
  paler than the skin.

**`wookieepedia_iridonian_skeleton.jpg`** — an in-show X-ray of Eeth Koth's skull, and the most
useful single frame here for an artist: 🔑 **the horns are BONE, real cranial projections rising
out of the skull itself** — five clear spikes across the crown plus lateral ones — not skin
growths, not ornaments, not attachments. So a Zabrak horn must read as **rigid and bone-coloured,
rooted in the head**, and the crown line must sit where the skull ridge is. The rest of the X-ray
shows an unremarkable humanoid ribcage; it is too noisy to resolve the second heart.

**The contrast reference, `wookieepedia_dathomirian_maul.jpg`** — this is what an Iridonian is
**not**: **crimson-red skin in bold black blocks**, **tall, sharp, dark-brown pointed horns**
standing well clear of the skull, **bald**, **yellow-orange irises with red rims**. Every one of
those four reads differently from the Iridonian references above. Keep it precisely so the
difference is checkable.

### Def-versus-canon (flagged — not fixed here)
- 🔴 **`Outland_BaldMale` is contradicted by the Iridonian article's own infobox image.** **Eeth
  Koth — the canonical male Iridonian and the picture at the top of that article — has long,
  straight, black hair.** Canon sources Iridonian hair as **black and purple**; Legends adds
  blonde, brown and red as *common* for the Iridonian group specifically. Bald-capping every male
  erases a sourced feature of the exact individual the def is modelled on.
- 🔴 **`Hair_Gray` is the only hair-colour gene, and grey is sourced nowhere.** Canon Iridonian
  hair is **black** and **purple**; Legends says **blonde, brown, red, black**. Combined with
  `Outland_BaldMale`, the shipped result is **bald men and uniformly grey-haired women** — neither
  of which any source or image supports.
- 🔴 **The two hearts are not represented at all** — and they are the species' most-cited
  distinction, listed in the canon infobox, the canon body text *and* both Legends
  `distinctions` fields, with an explicit stated effect: *"they could pump oxygenated blood around
  their systems more quickly… meaning they could go faster for longer."* That is a move-speed /
  stamina gene almost verbatim, and it is absent. **This is the single largest gap in the def.**
- 🔴 **`Outland_LowFertility` is contradicted by canon**, which calls Zabraks **"a colonial
  species, having migrated and adapted to dominate many worlds"** — and Legends notes they could
  interbreed with humans. Nothing anywhere suggests impaired fertility.
- ⚠️ **Legends' "great resistance to physical pain" is not represented**, though it is the other
  sourced physiological trait and maps cleanly onto existing pain genes.
- ⚠️ **`Aggression_Aggressive` overstates the sourced personality.** Canon is careful and almost
  corrective here: **fiercely independent**, proud of being survivors, and *"mistaken by other
  species for aloofness or arrogance, **which was erroneous**."* Legends: proud, strong,
  confident, single-minded. Independence and pride are the traits; aggression is a different
  claim, and the article specifically warns against the adjacent misreading.
- ⚠️ Unsourced species-wide: `Turn_Gene_Duelist`, `MeleeDamage_Strong`, `Beard_NoBeardOnly`.
  (Zabraks *can* be Force-sensitive per canon, and the def sensibly adds **no** psychic gene —
  that restraint is correct and is the right call, given Force powers are v2.)
- ⚠️ **No skin-colour gene at all.** Defensible for a near-human that inherits vanilla human
  skin, and the sourced *light / tan / light tan / dark* range is covered that way. But the
  sourced **moonlight-blue** is then unreachable, and so is Legends' second-group red/yellow/
  orange — the latter correctly, since that group is *not* Iridonian.
- ⚠️ **Mislabelled donor art:** `SWX/Pawn/HeadAttachments/iridonian/` contains **`Maul_south.png`
  and `Maul_east.png`** alongside Akaavi, Bao-Dur and Kao Cen. Maul is **Dathomirian**, so a
  Dathomirian tattoo pattern is filed in the Iridonian set. Mild — it is a tattoo-variant
  library, not a head — but it is exactly the confusion this entry exists to prevent, and it
  makes a Maul-like Iridonian one wrong pick away.
- ✅ **Correct, and worth recording as correct** — this is the cleanest of the five defs in this
  batch:
  - The **`<description>` is accurate, specific and canon-faithful**, uniquely among the five.
    (Three of the other four ship `.` or `e`.)
  - **`nameMaker` is `RSW_KoTOR_NamerIridonian`** — the right species' namer.
  - **`RSW_Headbone_zabrak` is a genuinely good gene.** Its art (`donor_current_sprite.png`) is a
    crown of **seven short blunt rounded nubs in an arc across the brow** — the "stumped"
    Iridonian horn, not a spike. And **five variants ship** (`Zabrak0`–`Zabrak4`), which matches
    canon's *"horn placement, length, and thickness varied enormously"* and Legends' *"subspecies
    distinguished by the number and pattern of horns."* Rare to find a def this well matched.
  - **`RSW_FacialRidges_iridonian`** matches the sourced facial tattoos and Eeth Koth's actual
    hairline-weight linework. ⚠️ One caution: the art is drawn in **very light grey at very low
    contrast** and may vanish entirely at RimWorld pawn scale — worth checking in game.
  - **`Body_Standard`** is right. Legends' 1.8 m and the human build in both images support it,
    and it avoids the invented body-size genes that mar the Kaleesh and Mimbanese defs.

## Must show
- [ ] Crown of short, blunt, cream-ivory horns (stumped cones, not tall spikes) arcing across the brow and around the head, distinctly paler than the surrounding skin
- [ ] Otherwise entirely human face structure (human nose, mouth, ears, eye placement) on pale tan/sallow yellow-ochre skin
- [ ] Fine, hairline-weight dark tattoo lines on the chin and lower cheeks in a symmetric pattern — not bold blocks
- [ ] Horns read as rigid, bone-coloured cranial projections rooted directly in the skull (real cranial projections, not skin growths or attachments)
- [ ] Hair may be long, straight and black (as on the canonical male Eeth Koth) OR bald — not forced bald on every male

## Engine limits
none known — every finding recorded for this def (forced male baldness, grey as the only hair colour, no second-heart gene) is a gene/def choice, not a rendering-pipeline constraint; the existing `RSW_Headbone_zabrak` horn gene and `RSW_FacialRidges_iridonian` tattoo gene are both recorded as well-matched art.

## Source URLs
- https://starwars.fandom.com/wiki/Zabrak — canon **species** article; rendered HTML is
  Cloudflare-walled, wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Zabrak&format=json&prop=wikitext`
  (38,602 chars, 2026-09-15). Tagged `{{Expand|all sections}}`; infobox has **no** height, mass,
  lifespan, skin, hair or eye colour.
- https://starwars.fandom.com/wiki/Iridonian — canon **subgroup** article, same API route
  (11,849 chars, 2026-09-15). Tagged `{{Species-stub}}`. **The source for Iridonian skin, hair
  and eye colours, and for the `class = Zabrak` containment.**
- https://starwars.fandom.com/wiki/Zabrak/Legends — Legends article, same API route
  (41,581 chars, 2026-09-15). **Source for height (1.8 m), lifespan (80 years), pain resistance,
  puberty-onset horns, and the explicit stumped-horn / human-featured description of the
  Iridonian group.**
- https://static.wikia.nocookie.net/starwars/images/4/4e/EethKothCardTrader.png
  (File:EethKothCardTrader.png, the **Iridonian** article's infobox →
  `wookieepedia_iridonian_eeth_koth.jpg`)
- https://static.wikia.nocookie.net/starwars/images/a/a4/Zabrak_DICE.png (File:Zabrak_DICE.png,
  the **Zabrak** article's infobox → `wookieepedia_infobox_zabrak.jpg`)
- https://static.wikia.nocookie.net/starwars/images/e/e7/EethKothSkeleton-TCWs2BR.png
  (File:EethKothSkeleton-TCWs2BR.png, *"The skeletal structure of Zabrak Jedi Master Eeth Koth"*
  → `wookieepedia_iridonian_skeleton.jpg`)
- https://static.wikia.nocookie.net/starwars/images/4/4c/DarthMaul-SWTLC.png
  (File:DarthMaul-SWTLC.png, *"Darth Maul, a Dathomirian Zabrak Sith Lord"* →
  `wookieepedia_dathomirian_maul.jpg`)
- NOT fetched this pass: no `starwars.com/databank` page for Zabrak was attempted. The canon
  article's density of colour and horn detail comes largely from
  `{{HelmetCollectionCite|79|Databank A-Z}}`, a print source not reachable online.

## Candidate images
- `wookieepedia_iridonian_eeth_koth.jpg` — 🔑 **the reference of record for this def.** The
  Iridonian article's own infobox: Eeth Koth, half-length, on white, photographic (practical
  prosthetic makeup). Settles the short blunt cream horn crown, the pale tan skin, the human
  face structure, the forehead nodules, the hairline-weight chin tattoos, and — importantly —
  **long black hair on a male.**
- `wookieepedia_infobox_zabrak.jpg` — the Zabrak article's infobox, a game render of a **female,
  bald** Zabrak. Independent confirmation of the horn crown and human proportions from a
  different medium and a different individual, and evidence that **bald is equally attested.**
  Game-engine art, so treat exact hue as the renderer's.
- `wookieepedia_iridonian_skeleton.jpg` — an in-show X-ray of Eeth Koth's skull. **The reference
  that settles that the horns are BONE**, rooted in the cranium. Low-fidelity, near-monochrome,
  and useful for structure only — not for colour, and it does not resolve the second heart.
- `wookieepedia_dathomirian_maul.jpg` — 🔴 **kept and labelled as a CONTRAST reference, not a
  reference for this def.** Darth Maul is a **Dathomirian** Zabrak — the other subspecies, which
  ships as its own xenotype (`RSW_RimMandrakeDathomirian`). Red-and-black skin, tall sharp horns,
  yellow-orange eyes, bold tattoo blocks: **none of this belongs on an Iridonian.** Present so
  the distinction can be checked by eye rather than remembered.
- `donor_current_sprite.png` — the mod's current art,
  `OR/OuterRim/Genes/Headbone/Zabrak0_south.png` (`RSW_Headbone_zabrak`, one of five variants).
  Greyscale, correct for runtime tinting. **A positive reference** — seven short blunt rounded
  nubs in an arc, which is the stumped Iridonian horn done right.
- `donor_current_sprite_iridonian_facialridges.png` — `SWX/Pawn/HeadAttachments/iridonian/iridonian_south.png`
  (`RSW_FacialRidges_iridonian`). A fine symmetric line-art tattoo pattern that matches Eeth
  Koth's idiom well. ⚠️ **Drawn at very low contrast in light grey** — check whether it survives
  at pawn scale, because on disk it is nearly invisible against a light head.

## ruling
(empty — owner has not reviewed this race yet)
