# Yoda's species ("Yoder")

**defName**: `RSW_RimMandrakeYoderForceGremlin`, label `Yoder`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
⚠️ **Matrix tier `—`**: the def ships but its
`race_faction_assignment.prefill.json` entry is **empty `{}`** — no faction spawns
it, and `factionlessGenerationWeight` is `0`, so as shipped this xenotype cannot
appear in a game.

🔴 **"Yoder" and "Force Gremlin" are both inventions, and one of them is worse than
the other.** The species has **no canonical name at all** — deliberately. The
Wookieepedia article is titled **"Yoda's species"** and carries a `{{Conjecture}}`
banner, meaning even that title is the wiki's placeholder rather than a canon term.

- **"Yoder" appears nowhere in canon or Legends.** It is a coinage, presumably from
  "Yoda" + a species suffix. Nothing sources it. It is also the label shown to the
  player and the string in `RSW_KoTOR_NamerYoder`.
- **"Force gremlin" *is* traceable, but only as the def's own fiction**: the def's
  `<description>` says the species was *"nicknamed 'force gremlins' by at least one
  group of humans"* — i.e. the description is written to make its own invented term
  diegetic. That is a legitimate authoring move, but it is not canon and should not be
  mistaken for one. **Nothing found in canon uses "gremlin"** for this species. The
  sourced in-universe epithets are quite different: Luke Skywalker calls Yoda a
  **"little swamp frog"**, and the noble Ramil says he looked like a **slime-gnome**.
- 🔑 **This namelessness is authorial intent, not a gap in the wiki.** *"Star Wars
  creator George Lucas chose to keep the name and background of Yoda's species a
  mystery."* Both Yoda's and Yaddle's official `starwars.com` Databank entries list
  their species as **"Unknown."** Dave Filoni confirmed the homeworld would never be
  revealed, because *"giving such an answer would ruin a major part of the fun."*
  So a shipped name is a **deliberate divergence from canon**, and the owner should
  know he is making one rather than filling a blank.

## Sourced text (Wookieepedia)

### What canon establishes
*"The species to which the Jedi Grand Master Yoda belonged was ancient and shrouded
in mystery. Members of this species were rarely seen anywhere in the galaxy. The few
members of this species seen in the galaxy were all Force-sensitive, and the species'
homeworld and name were unknown."*

Appearance, verbatim: *"Members of the species were **small in size, roughly
comparable to that of a human child**, with **green skin, large eyes, and long
pointed ears**. Their **three-fingered hands ended in claws**."*

- Infobox distinctions: **"Long ears, three-fingered hands and three toes on the
  feet"** (*Revenge of the Sith*). So **tridactyl on both hands and feet, clawed.**
- Infobox **skin colour: green** — one value, no range.
- Infobox **hair colour: auburn** (Yaddle, Databank) and **white** (Yoda, *Revenge of
  the Sith*). Body text: *"Members of the species were capable of growing **thin
  hair**, with shades varying from auburn to white being documented, **females having
  longer and thicker hair than males**."* 🔑 A sourced sexual dimorphism, and the
  *only* one canon gives.
- Infobox **eye colour: green-gold** (Yoda, *Dark Disciple*) and **brown** (Grogu,
  *The Mandalorian*). ⛔ **Black is not a sourced eye colour.**
- **Diet: omnivorous.** Sourced by example at both ends: Grogu *"caught and devoured
  live amphibians whole"*; Yoda *"made rootleaf stews."*
- 🔑 **"Their ears were expressive, curling and unfurling in accordance with their
  emotions."** A behavioural/animation trait, and a good one.
- **Both male and female genders** exist (Databank: Yoda male, Yaddle female).
- **Language**: capable of **Galactic Basic Standard**; Yoda's inverted syntax is his
  own idiolect, not the species' — the article attributes the *distinctive syntax* to
  Yoda specifically.

### Size — sourced, but for individuals only
🔴 **The species article's `height` and `mass` infobox fields are BLANK.** There is
no species-level figure. What is sourced is the individual:

- **Yoda: height 0.66 meters** (`starwars.com` Databank, cited by the article) and
  **mass 13 kilograms** (*The Empire Strikes Back: So You Want to Be a Jedi?*).
- The species-level statement is the qualitative one: **"small in size, roughly
  comparable to that of a human child."**

0.66 m is the number to build against. It is **very** small — well under half a
RimWorld human's height, and 13 kg is roughly an 18-month-old human infant's mass on
a fully-grown adult of another species.

### Lifespan and maturation — the species' defining oddity, fully sourced
- **"The species had a very long life expectancy, spanning at least several
  centuries."**
- **Yoda "lived nearly a thousand years before dying of old age"**; born ~896 BBY,
  died 4 ABY.
- 🔑 **"They aged very slowly, remaining in infancy for at least fifty standard
  years."** (Grogu is fifty and an infant: *"Wait. They said fifty years old." /
  "Species age differently. Perhaps it could live many centuries."*)
- 🔑 **"Despite their slow aging for the first five decades of life, members of the
  species reached maturity by their hundredth year"** — Yoda began training other
  Jedi at about 100.
- **Middle-aged at 514**, per Yaddle (Yoda's age during *Cataclysm*).
- So the curve is: **infant for 50+ years → adult by 100 → middle-aged around 500 →
  dead of old age near 900.**

### Unusual abilities
- **Every member of the species ever seen in the galaxy was Force-sensitive.** That is
  a stronger claim than any other species in this batch gets, and it is stated flatly.
- 🔑 **Even at the infant stage, Force-sensitive individuals could use telekinesis and
  Force healing**, and were *"capable of complex thought processes, and could
  understand speech and communicate via the Force at this age."* An infant of this
  species is a functioning telekinetic.
- The species is **rare** — *"rarely seen anywhere in the galaxy"* — and **ancient**.

### What canon leaves blank — record as UNSOURCED, do not invent
**Species name. Homeworld (an article exists only as "Yoda's homeworld: Unknown").
Species-level height. Species-level mass. Population. Society, culture and
government** — the Society section contains only the rarity, the mystery and the fact
they can speak Basic. **Nothing about family structure, technology, settlements or
politics exists.**

## Visual brief

**`wookieepedia_yoda_infobox.jpg`** (`File:Yoda_TPM_RotS.png`, 540×720, full-body on
transparent background) is the **reference of record**, and it corrects the def in
two specific ways:

- **Skin is a mid, slightly desaturated SAGE GREEN** with a distinctly **yellow-olive
  cast**, not a bright lime and not a deep forest green. It is warmer and duller than
  a text prompt produces from the word "green."
- **The scalp, forehead and the backs of the hands are covered in a dense network of
  fine wrinkles and low ridges.** The head is the wrinkliest surface on the body — the
  quoted description is *"Small, green, and wrinkly with pointy ears."*
- 🔑 **The ears are enormous, broad-based, and held nearly HORIZONTAL**, sweeping out
  and slightly back — wider than the head is tall. Not upright elf ears. They taper to
  a fine point and are thin enough to read translucent at the edge.
- 🔴 **The eyes are NOT large, and NOT black.** They are **modest in size, heavily
  hooded under thick wrinkled lids, brownish-green with a clearly visible iris, pupil
  and white sclera** — an old man's eyes. Set wide and low on a broad flat face.
- **A sparse tuft of thin, wispy WHITE hair** on the crown and at the ear roots —
  translucent, barely covering the scalp. Not a hairstyle; a few strands.
- 🔑 **Three thick, stubby fingers per hand, each ending in a dark horn-coloured
  claw**, and **three broad clawed toes per bare foot.** The hands are proportionally
  large and the fingers short and fat.
- **Very short legs relative to the torso**, a slight forward stoop, and a plain
  walking stick. Costume: layered coarse brown Jedi robes.

**`wookieepedia_grogu.jpg`** (`File:Grogu-SWI216.png`, 1300×1550) is the **infant**
and it is the single most useful image in this entry, because it is almost certainly
where the def's face came from:

- 🔴 **Grogu's eyes ARE huge and near-black** — enormous dark-brown irises filling
  most of the eye with almost no visible sclera, dominating the face. **This is an
  infant trait.** The adult has small hooded green-gold eyes. **The mod's
  `RSW_Eyes_Big` gene ("large, black eyes") models the fifty-year-old baby, not the
  species.**
- **Grogu's skin is a much PALER, cooler grey-green** than Yoda's warm sage. The
  species article gives only "green," so this is real variation the entry should carry:
  **infant = pale grey-green, adult = warm sage-olive.**
- **Ears are proportionally even larger** relative to the head, and held more upright
  and forward.
- **Very few wrinkles** — the fine wrinkle network is the adult's, not the infant's;
  only faint forehead creasing.
- **Three fingers with small dark claws**, already present.
- Wispy pale hair, sparse. Wrapped in a coarse robe.

**`wookieepedia_yaddle.jpg`** (`File:YaddleJediCouncil.jpg`, 768×432, a *Phantom
Menace* frame) is the **female** reference and confirms the one sourced dimorphism:

- 🔑 **Long, thick, dark auburn hair falling well past the shoulders** — visibly a
  full head of hair, in flat contrast to Yoda's few white wisps. This is the *"females
  having longer and thicker hair than males"* line, and it is a large visual
  difference, not a subtle one.
- **Same green skin, same wrinkle network, same broad flat face**, but the ears read
  slightly more upswept and less horizontal than Yoda's, and the muzzle is a little
  longer.
- **Three-fingered clawed hands** clearly visible resting in her lap.
- Seated in a Council chair, robed — so no full-body height reference.

**`wookieepedia_yoda_episode1.jpg`** (`File:Yoda_Episode_I_Canon.png`, 1920×816) is
the widest frame and is the best available **scale** reference, showing the adult in a
built environment against other species.

⚠️ **No `donor_current_sprite.png`.** The xenotype renders from mod genes with no
species art in this repo: `RSW_Eyes_Big` draws
`SWX/Pawn/HeadAttachments/bigeyes/bigeyes` at `drawSize 0.2`, plus
`Outland_Ears_BigEars` and `Hands_Pig`. Those textures live in the deployed mod folder
under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, not here.
Nothing in this repo compares canon against the sprite the player sees.

## Must show
- [ ] Adult skin is a mid, slightly desaturated sage-green with a yellow-olive cast — not bright lime, and not the infant's paler cool grey-green
- [ ] Adult scalp, forehead and backs of the hands carry a dense network of fine wrinkles and low ridges
- [ ] Ears are enormous, broad-based, held nearly horizontal (sweeping out and slightly back), wider than the head is tall, tapering to a fine point
- [ ] Eyes are modest in size (not huge or black), heavily hooded, brownish-green with a clearly visible iris, pupil and white sclera
- [ ] Three thick, stubby fingers per hand ending in dark horn-coloured claws, and three broad clawed toes per bare foot
- [ ] Females (per the Yaddle reference) show long, thick hair falling past the shoulders, in contrast to males' sparse wispy white hair

## Engine limits
none known — there is no `donor_current_sprite.png` for this species (it renders from generic mod genes whose art lives only in the deployed mod folder outside this repo), so there is nothing on disk here to test against a rendering-pipeline constraint.

## Def-versus-canon (flagged — not fixed)

`RSW_RimMandrakeYoderForceGremlin` is, on the mechanical side, **the best-aligned def
in this batch** — the lifespan, maturation, psychic and size genes all point the right
way. The problems are naming and face:

- 🔴 **`RSW_Eyes_Big` — "Carriers of this gene have large, black eyes."** Canon eye
  colours are **green-gold** and **brown**; **black is not sourced**, and the adult's
  eyes are **small and hooded**, not large. The gene models **Grogu's infant face** and
  applies it to every adult. This is the clearest appearance defect in the def and
  exactly the class of error this library exists to catch.
- 🔴 **`Hands_Pig`.** Canon is explicit and repeated: **three-fingered hands ending in
  claws, and three toes on the feet.** A cloven/trotter hand is not a tridactyl clawed
  hand. No gene expresses the sourced extremity, on hands or feet.
- 🔴 **`Hair_DarkBrown` is the only hair gene, for both sexes.** Canon gives **auburn**
  (Yaddle) and **white** (Yoda) and states **females have longer and thicker hair than
  males** — the species' only sourced dimorphism, and the def expresses neither the
  colours nor the dimorphism. Nothing renders the adult's characteristic **sparse wispy
  thin** hair either.
- 🔴 **Naming, per the top of this entry**: `Yoder` and `ForceGremlin` are both
  inventions on a species Lucas deliberately left unnamed, and both are baked into the
  defName, the label, the icon path (`Xenotype_ForceGremlin`) and the namer
  (`RSW_KoTOR_NamerYoder`). Owed under `XENOTYPE_CANON_CORRECTION_1` — flagged, not
  renamed. Recording it because "the def has no canon name to be wrong about" is the
  wrong conclusion: canon's position is that the name is *withheld*, which is a fact
  the def contradicts by supplying one.
- ⚠️ **`RSW_BodySizeGene_smaller`** is `SM_Cosmetic_BodySizeOffset -0.5`, and its
  `<description>` is literally **`jawa size`**. Canon: **0.66 m and 13 kg** against a
  ~1.7 m human — this species is *much* smaller than a Jawa (Jawas are ~1 m). The gene
  is the right instinct and the wrong magnitude, and it is a **cosmetic** offset, so it
  is unclear whether it affects anything but the sprite.
- ⚠️ **`RSW_lifespan_nine` (900-year lifespan, `LifespanFactor 9.0`)** is a genuinely
  good call — Yoda died near 900 of old age, so this is well sourced. ✅ Paired with
  `Outland_DeceleratedMaturation`, it captures the sourced curve about as well as
  RimWorld allows. Recorded as **correct**, since the entry should say what is right as
  well as what is wrong.
- ⚠️ **`Skin_Green`, `Outland_Skin_DeepGreen`, `Outland_Skin_DeepLime`.** Canon gives
  **green**, unqualified. The images give a narrow band — **warm sage-olive (adult) to
  pale cool grey-green (infant)**. **Deep lime is outside that band in both
  directions**, and nothing sources a pale grey-green skin gene, which is the one an
  infant would need.
- ⚠️ **`KindInstinct` and `Turn_Gene_MotivationLow`** — unsourced. Yaddle is described as
  *"very kind and quiet"* by one in-universe artist, which supports kindness for **an
  individual**; low motivation has no source at all and sits oddly against a species
  whose only known members are Jedi Masters.
- ⚠️ **`AptitudeStrong_Melee` and `Turn_Gene_Duelist`.** Yoda's lightsaber duelling is
  a **Jedi Master's training**, not a species trait, and the species has exactly three
  documented members. Attributing melee aptitude to the species is inference.
- ⚠️ **`DiseaseFree` and `Outland_LowFertility`** — unsourced. (Low fertility is a
  plausible read of "rarely seen anywhere in the galaxy," but the article attributes the
  rarity to their absence from the galaxy, not to their breeding.)
- ⚠️ **No omnivore/diet gene and no expressive-ear feature.** Both are sourced;
  expressive ears *"curling and unfurling in accordance with their emotions"* is the
  most charming sourced trait the species has and nothing carries it.
- ✅ Well sourced and correctly present: `PsychicAbility_Enhanced`,
  `Turn_Gene_LatentPsychic`, `Turn_Gene_FastNeuralHeat`, `Turn_Gene_MeditationNeed`,
  `RSW_statgene_PsyHarmonize` (*"the few members of this species seen in the galaxy were
  all Force-sensitive"*, and infants already use telekinesis and Force healing),
  `RSW_lifespan_nine`, `Outland_DeceleratedMaturation`, `Outland_DeceleratedPregnancy`,
  `Outland_Ears_BigEars`. The `<description>` is also accurate on substance — long life,
  fifty-year infancy, universal Force sensitivity — apart from the invented nickname.

## Source URLs
- https://starwars.fandom.com/wiki/Yoda%27s_species — wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Yoda's%20species&format=json&prop=wikitext`,
  51,060 chars, 2026-09-15. Canon article, tagged **`{{Conjecture}}`** — the title
  itself is the wiki's placeholder.
- https://starwars.fandom.com/wiki/Yoda — same API route, 269,883 chars, 2026-09-15.
  Source of the **0.66 m** height, **13 kg** mass, white hair, green-gold eyes, green
  skin, and the 896 BBY–4 ABY lifespan.
- `https://www.starwars.com/databank/yoda` and `https://www.starwars.com/databank/yaddle`
  — cited *by* Wookieepedia as the source for Yoda's 0.66 m height and for both entries
  listing the species as **"Unknown."** ⚠️ **Not independently fetched this pass**;
  taken from the article's citations.
- https://static.wikia.nocookie.net/starwars/images/c/c3/Yoda_TPM_RotS.png → `wookieepedia_yoda_infobox.jpg` (540×720)
- https://static.wikia.nocookie.net/starwars/images/f/f9/Grogu-SWI216.png → `wookieepedia_grogu.jpg` (1300×1550)
- https://static.wikia.nocookie.net/starwars/images/0/02/YaddleJediCouncil.jpg → `wookieepedia_yaddle.jpg` (768×432)
- https://static.wikia.nocookie.net/starwars/images/7/7e/Yoda_Episode_I_Canon.png → `wookieepedia_yoda_episode1.jpg` (1920×816)

## Candidate images
- `wookieepedia_yoda_infobox.jpg` — **the reference of record.** Full-body adult on
  transparent background. Settles: warm sage-olive green skin, dense fine wrinkle
  network on scalp and hands, **enormous near-horizontal broad ears**, **small hooded
  brownish-green eyes with visible sclera and pupil**, sparse wispy white hair, **three
  stubby clawed fingers and three broad clawed toes**, very short legs, forward stoop.
- `wookieepedia_grogu.jpg` — 🔑 **the infant, and the source of the def's face.** Huge
  near-black eyes, pale cool grey-green skin, proportionally larger and more upright
  ears, almost no wrinkling. Kept as a **positive reference for the infant stage and a
  negative reference for the adult** — using it for an adult is precisely the error
  `RSW_Eyes_Big` makes.
- `wookieepedia_yaddle.jpg` — the **female** reference. Confirms the one sourced
  dimorphism: long thick dark-auburn hair versus Yoda's few white wisps. Same skin,
  wrinkles and clawed tridactyl hands; slightly more upswept ears. Film frame, seated,
  so no height reference.
- `wookieepedia_yoda_episode1.jpg` — widest frame available; best **scale** reference
  against a built environment and other species.

## ruling
(empty — owner has not reviewed this race yet)
