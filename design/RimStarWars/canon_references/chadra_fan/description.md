# Chadra-Fan

**defName**: `RSW_RimMandrakeChadraFan`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Carries `combatPowerFactor 0.6` and a generic icon (`CustomXenotypeIcon7`) rather than
a bespoke one.

## ✅ INDEPENDENTLY RE-VERIFIED — 2026-09-20

Re-sourced from the live web by an agent **forbidden from reading this library**, so this is corroboration rather than an echo. Source: Wookieepedia **raw wikitext** via the Fandom API (the rendered pages sit behind a Cloudflare wall; wikitext gives the infobox and its `<ref>` citations verbatim), with the CANON and LEGENDS pages kept apart.

- canon infobox skin **gray / light / tan**, one named work per value — CONFIRMED verbatim.

⚠️ **Text only.** No infobox image was rendered or pixel-sampled, so any claim in this entry that rests on how a picture *looks* is untouched by this pass and remains unmeasured.

---

## Sourced text (Wookieepedia)
Chadra-Fan are a sentient species classed as **rodent** in the infobox and described
in the body as **rodent- or bat-like humanoids**, from the Outer Rim world of **Chad**.
Infobox: **height 1 meter** (Databank) — the one hard measurement, and the species'
defining constraint. **No mass and no lifespan are sourced.** Skin color: **gray**
(*Darth Vader* (2017) 18), **light** (*Trail of Shadows* 4), **tan** (*Star Wars: Card
Trader*). Hair color: **black, brown, gray, white**. Eye color: **black, brown, dark,
purple, red**. Distinctions begin with **large ears**.

*Biology and appearance*, in full substance: distinguished by their **large ears, flat
noses, and four nostrils**. Hair black, brown, gray or white; skin gray, tan or lightly
colored. **Possessing their oversized ears since childhood, Chadra-Fans also had
sensitive hearing.** **Chadra-Fans had two hearts and only needed to sleep about three
hours a day.** **Capable of producing many offspring, called fanlings.**

That is the entire canon biology section — there is **no** sourced statement about
nocturnality, dark vision, light sensitivity, mechanical aptitude, temperament, or
combat ability. Anything in that space is inference.

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**
The smooth stylised game-style render of Shortpaw (`wookieepedia_shortpaw_render.png`) was deleted. Added: a posed promotional costume photograph of Kabe from *A New Hope* (`wookieepedia_kabe_costume.png`), a live-action cantina still of Kabe (`wookieepedia_kabe_anh.jpg`), and Chris Trevas's realistic *New Essential Guide to Alien Species* painting (`wookieepedia_negas_legends.jpg`). The hyperlane-scout painting stays (realistic painted reference art).

All images agree on *shape*; colour is a range.

- **Enormous, tall, upright bat ears** — the largest feature on the body, roughly as
  tall as the skull itself, pale pink-lilac and thin, with visible internal ridging and
  darker veined edges in the costume photo. They stand up and outward like a leaf-nosed
  bat's. **This is what a Chadra-Fan is, visually.**
- **A short, flat, forward-facing snout ending in a broad pink pig-like nose-pad**, with the
  nostril openings on the pad's face, sitting proud of the fur.
- **A small mouth under the snout showing two prominent upper incisors** — clearly visible
  on the scout and on Kabe's costume.
- **Eyes**: the scout painting has big round **bright blue** eyes; 🔴 **live-action Kabe and
  the NEGAS painting have small, dark, beady eyes** sunk in the fur. The realistic sources
  favour the small dark eye; the big blue eye is one painting's take.
- **Full shaggy body fur, including the face**, longest as a ruff around the jaw and neck;
  bare skin only on the ears, the nose-pad and the palms/soles.
- **Hands and feet are long-fingered, wrinkled, dark and clawed** — Kabe's costume shows
  long pale claws on dark leathery fingers; the scout and NEGAS figures are barefoot with
  long splayed clawed toes.
- **Colour: warm mid-to-dark brown fur** in every remaining image (the scout, Kabe, NEGAS).
  The deleted Shortpaw render was the only **ash-grey** individual; grey stays a sourced
  colour (infobox "gray / tan / light") but no realistic image shows it.
- **Proportion: a stocky, short-limbed one-metre body with a proportionally huge
  head.** Dressed as competent adults — khaki field kit (scout), layered robes (Kabe,
  NEGAS) — not a comic-relief critter.

⚠️ **There is no `donor_current_sprite.png` in this directory** — no current mod art was
captured for comparison, so nothing here validates or invalidates what the mod renders today.

## Must show
- [ ] Enormous, tall, upright bat-like ears, roughly as tall as the skull itself, thin
  enough to read as translucent
- [ ] Short, flat, forward-facing snout ending in a broad nose-pad (not a human nose)
- [ ] Small mouth showing two prominent pointed upper incisors hanging over the lower lip
- [ ] Small dark eyes set forward in the face fur (live-action); large blue eyes only as a painted variant
- [ ] Full body fur, with bare skin only on the ears, nose-pad, and palms/soles
- [ ] Stocky, short-limbed body with a proportionally huge head relative to a roughly
  one-metre stature
- [ ] Realistic rendering: shaggy natural fur, thin veined skin on the ears, leathery clawed hands, natural lighting, no outlines, no cartoon shading

## Engine limits
none known

## Def-versus-canon (flagged)
- 🔴 **No dedicated head type gene.** The def builds the species from
  `RSW_Nose_SmallPig` + `Outland_Ears_Fleef` on `Body_Standard` — i.e. a human head
  with a pig nose and non-human ears. The canonical read is a **bat/rodent muzzle with
  ears as tall as the skull, huge round eyes and visible incisors**; the other species
  in this batch (Abednedo, Gand, Geonosian, Ithorian) each get an `RSW_*Head` gene and
  this one does not. **Verify what `Outland_Ears_Fleef` actually renders** — if it is
  not a very large upright bat ear, the species' single defining feature is absent.
- 🔴 **No skin-colour gene at all**, so the sourced **gray / tan / light** span is
  unrepresented; `Furskin` is doing all the work. Grey is a sourced colour (no realistic image of a grey individual remains).
- 🔴 **`RSW_lifespan_half` is unsourced.** The infobox lifespan field is **empty**.
  Nothing anywhere says Chadra-Fan are short-lived; this is invented and it is exactly
  the kind of number this library exists to stop.
- 🔴 **Sensitive hearing is sourced and prominent, and is not represented at all.**
  Along with the ears it is the species' signature; if any gene can carry it, it should.
- ⚠️ **Hair colour list is incomplete**: canon sources **gray** and **white** hair, and
  the def carries only `Hair_ReddishBrown`, `Hair_DarkBrown`, `Hair_DarkReddish`,
  `Hair_MidBlack` — no grey, no white. Combined with `Hair_BaldOnly` the practical
  effect is unclear; check which of these actually reaches the pawn.
- ⚠️ **`DarkVision` + `UVSensitivity_Mild` are inference, not canon.** Bat-like
  appearance does not equal an attested night sense; the canon article says nothing.
- ⚠️ **`AptitudeStrong_Mining`, `AptitudeStrong_Crafting`, `AptitudePoor_Animals`,
  `Mood_Sanguine` are unsourced** by the canon article. (Chadra-Fan tinkering ability
  is a *Legends*-era association; if that is the intent, it needs a Legends citation
  written down, not a silent gene.)
- ✅ Correct and canon-supported: **`LowSleep`** (sleeps ~3 hours a day — an unusually
  exact match), **`RSW_BodySizeGene_smaller`** (1 metre), **`Outland_AcceleratedPregnancy`
  + `Outland_AcceleratedMaturation`** (many offspring, "fanlings"), and the weak-combat
  cluster (`MeleeDamage_Weak`, `Delicate`, `AptitudePoor_Shooting/Melee`,
  `combatPowerFactor 0.6`) as a defensible consequence of one-metre stature.
- Not representable, recorded so nobody "fixes" it: **two hearts**, **four nostrils**.

## Source URLs
- https://starwars.fandom.com/wiki/Chadra-Fan (article HTML Cloudflare-walled; wikitext
  pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Chadra-Fan&format=json&prop=wikitext`,
  17,080 chars, 2026-09-15)
- File:Hyperlane_Scout_FDCR.png — the infobox image →
  `wookieepedia_hyperlane_scout_fdcr.png`
- File:Kabe-GalacticFiles2018.png → `wookieepedia_kabe_costume.png`; File:Kabe Databank.jpg →
  `wookieepedia_kabe_anh.jpg`; File:Chadra-Fan NEGAS.jpg → `wookieepedia_negas_legends.jpg`
- NOT fetched this pass: https://www.starwars.com/databank/chadra-fan (official
  Databank — the source of the 1-metre height and the "rodent" classification).

## Candidate images
- `wookieepedia_hyperlane_scout_fdcr.png` — the infobox image: a full-body Chadra-Fan hyperlane scout in khaki field kit with a red pack, realistic painted illustration (*Force and Destiny Core Rulebook*). Settles the tall translucent pink bat ears, the flat pink nose-pad, the two protruding upper incisors and the clawed bare feet; its big blue eyes disagree with the live-action dark eyes. File `Hyperlane Scout FDCR.png`.
- `wookieepedia_kabe_costume.png` — **live-action reference of record**: posed promotional photograph of the *A New Hope* Kabe costume, head and torso: shaggy brown fur, huge veined pink ears, pig-like nose-pad, incisors, dark clawed hands; file `Kabe-GalacticFiles2018.png` — https://static.wikia.nocookie.net/starwars/images/7/7e/Kabe-GalacticFiles2018.png/revision/latest?cb=20251223165557
- `wookieepedia_kabe_anh.jpg` — live-action *A New Hope* cantina still of Kabe reaching across the bar (dark, profile); file `Kabe Databank.jpg` — https://static.wikia.nocookie.net/starwars/images/2/27/Kabe_Databank.jpg/revision/latest?cb=20151107000426
- `wookieepedia_negas_legends.jpg` — realistic painted plate by Chris Trevas, *The New Essential Guide to Alien Species* (Legends), full body in robes holding a glass: dark brown fur, small dark eyes, big ears, clawed feet; file `Chadra-Fan NEGAS.jpg` — https://static.wikia.nocookie.net/starwars/images/9/9f/Chadra-Fan_NEGAS.jpg/revision/latest?cb=20061204211640

## ruling
(empty — owner has not reviewed this race yet)
