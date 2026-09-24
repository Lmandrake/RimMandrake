# SUMP_GASLIGHT_1 — the gaslight economy: tar + acid → green gas → the warbling light

Owner rulings 2026-09-24, typed in chat at the Sump sitting. The founding ruling,
verbatim (answering a proposal to offset filth mood with burning-wick lamplight):

> "Yes but beef not up. Burning tar doesn't sound great for smoke and stink and
> there are many other oils. So the tar should be easily processed into a special
> oil with unusually beautiful properties. I'm thinking more gas here. There are
> green gas geysers that have their own economy already present in this mod stack.
> They were supposed to be present near the terminator right where the sump tends
> to be. So perhaps we can leverage that. Gaslight from the green gas geysers has
> the property you are speaking of. And tar, processed a certain way, can make this
> gas. Ah! By reacting it with some acid, the same as used for cleaning. That's how
> the cleaner works. So mixing a bit of the two in a lamp produces an unusually
> beautiful light. And we should implement that light too. A dancing, pulsing,
> beautifully warm light that warbles between adjacent colors. Nice! One could
> imagine not just lamps for this but a line of statue art driven by artistic skill
> where the flames come out of various parts of the statue and are shown. I'm
> really liking this. That could be a holy act to the evil sun god. There should be
> places in the map where this is happening naturally, little dancing beautiful
> flames to inspire the characters to realize this. Perhaps a technology they
> realize upon first meeting one of these flames."

Follow-ups, same sitting, typed: the green gas is Helixien (Vanilla Helixien Gas
Expanded, adopted 2026-08-10 — `design/Jawa/proposals/tar_pits_deep_design.md`
§3B(5)) and **the free mod may require it** — *"It is ok for the free mod to
require other mods. It is free of the utinni scenario and Star Wars entanglement
that's all. But the utinni layer should rename it to our own form of gas. Let's
call it Sumpgas."* (rename is `SUMP_UTINNI_LAYER_1`'s). Discovery scope: *"Yes
pilot here (the flickering light or geyser both can teach) and some specific tech
will unlock when meeting tar. I should not say unlock trees that may be, but often
it will just be specific technologies."* Statues/worship split ruled by card:
flame statuary ships RM-tier; the holy-act-to-the-evil-sun-god meaning is an
Utinni ideoligion patch (`SUMP_UTINNI_LAYER_1`).

## spec

1. **The reaction**: tar + acid → green gas (Helixien-compatible). One acid, three
   uses — this reaction IS how the cleaner works (cleaning tar converts it to
   gas), it is how vault extraction works (`SUMP_TAR_VAULT_1`), and a small
   tar+acid mix in a lamp is the light. Weak acid renders from thrummel seepwax —
   ruled generous: *"one raid should give you a lot. Not meant as a starvation
   mechanism."* Strong acid arrives by trade (Poison Forest,
   `BIOME_NUISANCE_NORMALIZATION_1`).
2. **The warbling light — implement the light itself**: dancing, pulsing,
   beautifully warm, warbling between adjacent colors. A glower whose color/
   radius animates (small comp; check `BiomeGlowMultiplierExtension` and existing
   glower patterns in `mandrake.rm.environmentalhazards` before new C#).
3. **Gaslight lamps**: fueled by the mix; the biome's mood answer — warm lamplight
   offsetting the squalor a Sump colony cannot escape.
4. **Flame statuary**: an art line driven by artistic skill where flames issue from
   parts of the statue — quality scales the fire show. RM-tier, secular.
5. **Natural flames**: map features where seep gas burns on its own — little
   dancing flames. These and the geysers are the discovery triggers.
6. **Discovery pilot**: witnessing a natural flame or geyser unlocks the gaslight
   chemistry tech; first meeting tar unlocks a specific tar tech. Specific
   technologies, not trees (his ruling). Engine shape: hidden research +
   discovery comp (Anomaly's encounter-unlock is the precedent). Planet-wide
   generalization is GATED: `INDIGENOUS_TECH_REVISIT_1`.
7. **Ship-buildable** (`BIOME_SHIP_CONTRIBUTIONS_1`): the lamps and statues are
   buildable aboard the gravship — the burning statues are one of the owner's two
   named ship gifts from this biome.

## verify

Quicktest: the reaction recipe runs; a lamp casts visibly animated warm light that
warbles; a statue's flame display scales with art quality; a natural flame exists
on Sump maps and its first witness fires the tech unlock letter; all
feature-gated in Mod Settings.

## criteria

The Sump's answer to permanent dusk and permanent filth is the most beautiful
light on the planet — made from its two nastiest substances.
