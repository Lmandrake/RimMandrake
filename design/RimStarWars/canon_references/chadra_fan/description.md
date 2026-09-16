# Chadra-Fan

**defName**: `RSW_RimMandrakeChadraFan`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Carries `combatPowerFactor 0.6` and a generic icon (`CustomXenotypeIcon7`) rather than
a bespoke one.

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
Two canon images, and they disagree about *colour* while agreeing completely about
*shape* — so shape is the fact and colour is the range.

- **Enormous, tall, upright bat ears** — the largest feature on the body, roughly as
  tall as the skull itself, pale pink-lilac and thin enough to read as translucent,
  with visible internal cartilage ridging. On the scout they stand up and outward like
  a leaf-nosed bat's; on Shortpaw they are set lower and flare sideways. **This is
  what a Chadra-Fan is, visually.** A merely large-eared human head does not get there.
- **A short, flat, forward-facing snout ending in a broad pink nose-pad**, not a human
  nose — pig-like or bat-like, with the nostril openings on the pad's face. It sits
  proud of the fur.
- **A small mouth directly under the snout showing two prominent pointed upper
  incisors** hanging over the lower lip. Rodent teeth, always visible.
- **Big, round, forward-set eyes filling much of the face** — a juvenile/neotenous
  proportion. The scout's are **bright saturated blue**; Shortpaw's are small and
  **black**. Both are canonically sourced colours, so eye colour genuinely varies.
- **Full body fur, including the face**, thickest as a ruff around the jaw and neck.
  Bare pink skin only on the ears, the nose-pad and the palms/soles.
- **Bare feet with long claws** and furry hands — the scout is barefoot with visible
  claws on splayed toes.
- 🔴 **The two individuals are completely different colours: warm mid-brown fur
  (scout) versus cool ash-grey (Shortpaw).** Both are sourced. Do not settle on one.
- **Proportion: a stocky, short-limbed one-metre body with a proportionally huge
  head.** They read as a child's build with an adult's bearing, and both are dressed as
  competent adults — khaki field kit with a red pack and headband on the scout, olive
  fatigues with a beige tactical vest and a **cybernetic left hand** on Shortpaw. That
  costuming contrast (explorer vs. crime lord) is useful: the species is not a
  comic-relief critter in either image.

⚠️ **There is no `donor_current_sprite.png` in this directory** — unlike the other
races in this batch, no current mod art was captured for comparison, so nothing here
validates or invalidates what the mod renders today.

## Must show
- [ ] Enormous, tall, upright bat-like ears, roughly as tall as the skull itself, thin
  enough to read as translucent
- [ ] Short, flat, forward-facing snout ending in a broad nose-pad (not a human nose)
- [ ] Small mouth showing two prominent pointed upper incisors hanging over the lower lip
- [ ] Big, round, forward-set eyes filling much of the face
- [ ] Full body fur, with bare skin only on the ears, nose-pad, and palms/soles
- [ ] Stocky, short-limbed body with a proportionally huge head relative to a roughly
  one-metre stature

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
  unrepresented; `Furskin` is doing all the work. Grey is what the on-screen Shortpaw
  actually is.
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
- Shortpaw, the *Biology and appearance* inline image (a Chadra-Fan crime lord in the
  Anoat sector) → `wookieepedia_shortpaw_render.png`
- NOT fetched this pass: https://www.starwars.com/databank/chadra-fan (official
  Databank — the source of the 1-metre height and the "rodent" classification).

## Candidate images
- `wookieepedia_hyperlane_scout_fdcr.png` — **the reference of record.** The infobox
  image: a full-body Chadra-Fan hyperlane scout in khaki field kit with a red pack,
  transparent background, high detail. Settles the tall translucent pink bat ears, the
  flat pink nose-pad, the two protruding upper incisors, the huge round blue eyes, the
  warm brown face-and-body fur, and the clawed bare feet. Painted illustration, so
  brushwork is the artist's; the anatomy is the thing to trust.
- `wookieepedia_shortpaw_render.png` — Shortpaw, an Anoat-sector crime lord: a second
  individual in **ash grey** with small black eyes and a cybernetic hand, in olive
  fatigues and a tactical vest. Its value is proving the head plan recurs while fur and
  eye colour shift completely, which is what makes the *shape* canonical and the
  *colour* a range.

## ruling
(empty — owner has not reviewed this race yet)
