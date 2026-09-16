# Nautolan

**defName**: `RSW_RimMandrakeNautolan` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Its `<description>` is lifted near-verbatim from the Wookieepedia *Biology and
appearance* section, so it is accurate as far as it goes — the gaps are in the genes,
not the prose.

## Sourced text (Wookieepedia)

The Nautolans were a **humanoid species** from the planet **Glee Anselm**. They were
**amphibious**, and **adapted to survive in harsh environments**. Nautolan society was
largely peaceful, but they were **at odds with the Anselmi**, a related species also
native to their home planet. Infobox: class **amphibian**; **skin colour blue, green,
purple, gray, yellow, orange**; **eye colour black, brown, red**; distinctions **"head
tentacles capable of detecting chemicals"**; habitat **aquatic**; language **Nautila**.
**Height, mass and lifespan are blank — do not invent them.**

**Body and senses.** Nautolans were **amphibious, capable of breathing both air and
water**. They were **known to be capable of surviving in extreme environments**. Their
skin could be green, blue, gray, purple, orange or yellow, **with red or green blood**.
🔑 **One of their most notable features were their large, dark eyes, which were a
product of evolution; through these eyes, they could spot details in lightless
oceans.**

🔑 **The headline ability, and it is thoroughly sourced.** *"Another notable detail
were their **long tendrils, which grew from their heads**. These tendrils contained
**highly-sensitive olfactory receptors that were chemical-sensing**, and most notably
used to **detect pheromones**, allowing them to perceive expressions of emotion and
other subtle changes in the body. Nautolans could **translate pheromones emitted by
other beings into an understanding of a being's emotional state**."* And the limit that
makes it interesting: **"These head tresses could be severed, and were incapable of
growing back."**

In-universe statement of the same thing, from Captain Finial Bright: *"Green skin, big
black eyes, what else would I be? What you might not know is that these tentacles of
mine let me pick up pheromones from other beings, which I translate into an
understanding of their emotional states. That's how I know you two… are terrified."*

## Visual brief

**The prose is right but flat; the images add three things it doesn't say — the
tendrils are patterned, the skin is yellow-green rather than green, and the eyes are
not solid black in every case.**

**`wookieepedia_kitfisto_detail.png` is the reference of record** (the canon infobox
image: Kit Fisto, full body, transparent background, live-action costume/makeup):

- **Skin is a pale, sallow YELLOW-GREEN** — closer to olive-khaki than to a saturated
  green. This matters because the gene list's greens are sage/viridian, i.e. bluer.
- 🔑 **The eyes are ENORMOUS, oval, and read as solid glossy BLACK** with no visible
  sclera or pupil — they occupy a large fraction of the face and are the single
  loudest feature. This is the "large, dark eyes" text, and it is correct here.
- 🔑 **The tendrils sprout from the CROWN AND BACK OF THE SKULL** — not from the jaw
  or neck — and sweep **down over the shoulders and chest**, thick at the base and
  tapering to points. There are **many of them (on the order of a dozen)**, not two or
  four. They read as a heavy hanging mane of fleshy tentacles.
- 🔑 **The tendrils are PATTERNED** — rows of darker olive spots/blotches run along
  their length. Flat unpatterned tentacles are the wrong answer.
- **The face has NO NOSE and no external nostril structure** — a smooth expanse
  between the eyes, then a small, wide, thin-lipped mouth. The skull above the eyes is
  smooth and slightly bulbous.
- **Otherwise an ordinary humanoid body**: normal shoulders, arms, long-fingered
  greenish hands, and feet that fit ordinary boots.

**`wookieepedia_zattfull_cgswg.png`** (Zatt, a male Nautolan **youngling**, *Clone
Wars* CGI) is the second reference of record and **corrects two things**:

- 🔑 **The eyes here have a visible RED-AMBER IRIS around a dark pupil**, not solid
  black. That matches the canon `red` eye-colour cite. **So "solid black" is one
  option, not the rule** — and the def currently expresses neither colour.
- **The tendrils are SHORTER and FEWER** than Kit Fisto's, reaching only to the
  shoulder. This is a **youngling**, so tendril length plausibly reads as age —
  useful, and consistent with them growing from the head and not regrowing if cut.
- Same yellow-green skin, with **dark olive spot mottling on the tendrils and
  shoulders and freckle-like speckling on the cheeks and forearms** — confirming the
  spotting is a species trait rather than one costume's paint job.
- **Bare feet are visible**: broad, four-toed, with flat nails. Not flippers.

**`wookieepedia_nautolan_vengeful_waves.jpg`** is a painted *Myths & Fables*
illustration, kept as a third independent rendering; treat its line and palette as the
artist's.

**`donor_current_sprite.png`** is the repo's greyscale art for
**`RSW_Headbone_nautolan`** — an *attachment*, not a head — and it is a reasonable
start that misses the two things the images make loudest. What it gets right: a crown
of tapering tendrils rooted at the top of the skull and sweeping outward and down.
What is wrong:
- ⚠️ **It reads as a symmetrical five-lobed crown or wig**, evenly spaced and
  flaring outward like a headdress, rather than **many heavy tentacles hanging down
  over the shoulders and chest**. The canonical mass hangs *down and forward*; this
  flares *out and up*.
- ⚠️ **No spot patterning at all.** Being greyscale is correct and expected (the game
  tints at runtime), so the *hue* findings above do not apply to this file — but a
  **pattern** can live in a greyscale mask, and this one has none.
- The tendrils are too short to reach the shoulder, so it renders the youngling
  proportion for every Nautolan pawn.

**Xenotype-versus-canon findings:**

- 🔴 **Amphibiousness is entirely absent from the gene list.** The species' *class* is
  `amphibian`; the def's own description says "amphibious, capable of breathing both
  air and water"; the habitat is `aquatic`. **No gene expresses any of it.** (The
  same gap exists on `RSW_RimMandrakeMonCalamari` — see that entry. Whatever solution
  is chosen should probably serve both.)
- 🔴 **`MinTemp_SmallIncrease` + `MaxTemp_SmallDecrease` narrow the comfortable
  temperature band at BOTH ends — the opposite of canon.** The article says twice that
  Nautolans were **"adapted to survive in harsh environments"** and **"capable of
  surviving in extreme environments."** A species defined by environmental hardiness
  should not be *less* tolerant than a human in both directions. This is the clearest
  mechanical contradiction in this def.
- ⚠️ **The pheromone sense is under-served.** `Outland_FamiliarScent` is the only
  scent-adjacent gene, and it is about the pawn's *own* familiarity, whereas the
  canon ability is **reading other beings' emotional states from their pheromones** —
  a social-perception power. `DarkVision` by contrast is an ✅ excellent, exactly-right
  match for "through these eyes, they could spot details in lightless oceans."
- ⚠️ **Skin set under-covers the actual images.** Canon lists **gray** and **yellow**;
  neither is in the gene list (`Outland_Skin_PaleOrange`, `PaleSage`, `DeepViridian`,
  `DeepAzure`, `Azure`, `DeepPurple`, `RSW_Skin_SelkathBlue`). **Both reference images
  show a yellow-green/khaki**, which the sage and viridian greens do not reach.
- ⚠️ **No eye-colour gene.** `RSW_Eyes_Big` correctly captures the size, but canon
  gives **black, brown, red** — and the two images show one solid-black case and one
  red-irised case. Eye colour is doing real work for this species.
- ⚠️ **`AptitudePoor_Construction` and `AptitudePoor_Mining` are unsourced.** Nothing
  in the article suggests either. The one sourced characterisation of the species is
  that **Nautolan society was largely peaceful**.
- ⚠️ **`Outland_EggLayer` and `Outland_DeceleratedPregnancy` are unsourced** — the
  article says nothing about Nautolan reproduction at all. (Contrast Mon Calamari,
  where spawning *is* explicitly sourced.)
- ⚠️ **`WoundHealing_Fast` is unsourced, and cuts against the one regeneration-adjacent
  fact there is**: severed head tresses **were incapable of growing back**.
- ⚠️ `Turn_Gene_Duelist` reads across from Kit Fisto, an individual Jedi duellist, to
  the whole species. Weak.
- ✅ Correct and well-sourced: `RSW_Headbone_nautolan` (the head tendrils exist and
  are the species distinction), `RSW_Eyes_Big`, `DarkVision`, `Hair_BaldOnly` +
  `Beard_NoBeardOnly` (the infobox has no hair-colour field at all), `Body_Standard`,
  `Outland_SvelteHead`.
- **Not representable, and worth recording rather than hiding**: red-or-green blood,
  tendril spot patterning, tendrils as a permanent severable body part, and tendril
  length as an age cue.

## Source URLs

- https://starwars.fandom.com/wiki/Nautolan (canon article; direct HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Nautolan&format=json&prop=wikitext`,
  30,438 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/b/b7/VengefulWaves.jpg → `wookieepedia_nautolan_vengeful_waves.jpg`
- `wookieepedia_kitfisto_detail.png` corresponds to `File:Kitfisto_detail.png` (the
  canon infobox image) and `wookieepedia_zattfull_cgswg.png` to
  `File:ZattFull-CGSWG.png`. Both were already on disk from an earlier pass and were
  verified against the article's own file list this pass.
- NOT fetched this pass: https://www.starwars.com/databank/nautolan (the article's
  `{{Databank|nautolan}}` citation, and the source of the amphibious, black-eye and
  Glee Anselm claims). Print sources cited by the article and not read:
  *Star Wars Character Encyclopedia: Updated and Expanded* (the "head tentacles
  capable of detecting chemicals" distinctions line) and
  *The High Republic: Light of the Jedi* (the lightless-ocean vision line and the
  Finial Bright pheromone quote).
- A `/Legends` variant was **not** fetched for this species — the canon page is
  substantial (30k chars, with a full Biology section), so the stub trap that applies
  to Nagai does not apply here. Recorded as not-checked rather than as absent.

## Candidate images

- `wookieepedia_kitfisto_detail.png` — **the reference of record.** The canon infobox
  image: Kit Fisto, full body, transparent background. Settles the sallow yellow-green
  skin, the enormous solid-black oval eyes, the noseless face, and the **many
  crown-rooted, spot-patterned tentacles hanging over the shoulders and chest**.
- `wookieepedia_zattfull_cgswg.png` — **second reference of record.** Zatt, a Nautolan
  youngling, *Clone Wars* CGI, full body. Corrects two things: **the eyes can have a
  red-amber iris rather than being solid black**, and **tendril length varies with
  age**. Also the best view of skin speckling and of bare four-toed feet.
- `wookieepedia_nautolan_vengeful_waves.jpg` — a painted *Myths & Fables*
  illustration. A third independent rendering in a different medium; stylised, so
  treat line and palette as the artist's.
- `donor_current_sprite.png` — the repo's greyscale `RSW_Headbone_nautolan`
  attachment. Gets the crown-rooted tapering tendrils; **flares them outward like a
  headdress instead of hanging them down the chest, renders them at youngling length,
  and carries no spot pattern.**

## ruling

(empty — owner has not reviewed this race yet)
