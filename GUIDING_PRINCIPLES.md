# GUIDING_PRINCIPLES — what is always true of this game

Version 0, 2026-11-21. This file says what is always true of the product, above any one mod, biome or feature.
`LEXICON.md` says what our words mean. This file says what the game is. Process rules (how agents work) stay in
`CLAUDE.md` and `infrastructure/agents/CHARTER.md`. A ruling that is a case of a principle points here.

Each entry has: the sentence; his words and their date; one example that honours it and one that breaks it; its scope
and what stays biome data; how it is checked; what makes us review it. An entry marked RULED binds. The section
"Proposed, not ruled" binds nothing: it holds the questions for his next card. The format and the authority of this
file are not ruled yet beyond this draft.

## 1. A mechanic reads conditions, never the place (RULED 2026-11-21)

**The sentence.** A biome's mechanics are universal. The code of a mechanic reads only physical conditions (sun
angle, heat, water, fire, ground, roof, food, and the like). It never reads which biome it is in. A biome keeps only
its data: its plants, animals, terrain, weather odds and map generation. A biome depends on a mechanic, showcases it,
or holds the materials or sources to make it or make it shine.

**His words, 2026-11-21** (the item `RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES`; full text in
the ledger and in `design/RimMandrake/standing_rulings.md` §Biome mechanics are universal): *"Biome mechanics in general
do NOT stay confined to the biome of origin: they are universal, but that biome depends on them, showcases them, or
has the materials or sources to make them or make them shine."* By card, the same day: "Conditions, never the place";
"Home only, as ruled in October"; "New work now; old mods as they advance".

**Honours it.** His Rot floor, as he describes it: *"The Rot features a living floor covering that heats rooms and keeps life alive in the
cold through food consumption. It works anywhere, but it's native to the Rot and must be tended and carried
elsewhere."* The Rot is its source. Food, tending and (by his ask, a ticket not yet built) Direct Sun limit it, not a
biome check. The code is not there yet: today the mat is gated by `IsRotBiome` and `RM_WarmGroundExtension` (code
census rows 14 and 15).

**Breaks it.** The ashwallow dives from fire only on a Pyrelands map: `RM_JobGiver_BurrowOnFire.cs` asks
`burnLine.IsPyrelandsMap`, a list of biome defNames (code census row 2). The fire is the condition; the map's biome is
not. Also the sun-heat effects of `RM_MapComponent_ShadeGrid.cs`, which run only on a biome that carries
`RM_SunHeatExtension` (row 29), against his example: *"the Stillshade has nothing "special" about its long shadows and
intense sun exposure effects: those should be planet-wide."*

**Scope.** All new design and code from 2026-11-21. Each existing mod converts when it next advances, as a planned
change for its next Design Version. No current version's bars move. Pyrelands 0.1.0 is not reworked. The per-mod list
of what converts: `design/specs/2026-11-21-guiding-principles/conversion_list.md`. Biome data stays per biome: which
plants, animals, terrain and weather a biome has, and its map generation.

**How it is checked.** In game, only the home biome is tested (his ruling of 2026-10-15, kept by card on 2026-11-21).
No foreign-map in-game check is owed. A converted mechanic has one OFFLINE test: hold the conditions constant, change
only the biome name, and the result does not change.

**Review when** a mechanic cannot be written as conditions; when the same exception is asked for twice; when he rules
on the open questions below; at a MAJOR Design Version.

## 2. A visible effect with no meaning is removed, not confined (RULED 2026-11-21)

**The sentence.** A visible effect with no meaning is removed. It is not kept and confined to one biome.

**His words, 2026-11-21:** *"I didn't mind the steam so much, but the meaningless pale region around steamgeysers I
definitely did."*

**Honours it.** The swirling steam over a geyser stays. He did not mind it. Decorative atmosphere is not banned.

**Breaks it.** The constant pale marked region round each steam geyser. Commit `d07e03a938` confined it to The Forge
(`RM_ForgeSkyPastures.cs`, code census row 1) instead of removing it.

**Scope.** Every visible effect of every mod: a mark, ring, tint, glow or overlay with no meaning in play.

**How it is checked.** The art and cosmetic judge (`design/RimMandrake/art_judge_brief.md`) and the reads-as floor line
(`src/RimMandrake/rimflow/concept_floor.json`, `reads_as`) read each such effect against what it means.

**Review when** an effect is kept with no meaning, or a player reads a meaning that is false.

## Proposed, not ruled

These bind nothing. Each waits for his card. The source is the Conductor's draft
(`design/specs/2026-11-21-guiding-principles/concept_draft.md`) and the GPT review (`gpt_review.md` beside it). After
each, the GPT review's strongest objection, in one line.

- **A biome earns a mechanic in one of three ways, and says which** (depends, showcases, source). Objection: the three
  overlap and describe a link; they are not a test of good gameplay, and "must be carried" excludes natural spread.
- **A limit in the world, never a limit in the code.** Objection: taken literally it bans settings and simulation
  budgets; decide whether it means "prevent unaided spread" or "prohibit expansion".
- **What a biome owns is its data, not its laws.** Objection: data can encode laws (a terrain def can grant fire
  immunity), so the line between data and law does not settle ownership.
- **Every visible effect means something the player can read and act on.** Objection: this would remove atmosphere
  and invent chores to justify decoration; entry 2 keeps only the ruled part.
- **A visible effect that implies a consequence tells the truth and is readable** (the GPT review's rewrite of the
  last one). Objection: none in the review; it is an extension of his geyser words, not his words.
- **A new mechanic, not only a converted one, owes the offline test** (same conditions, only the biome name changed).
  Objection: none in the review; he required the test at conversion only.
- **Universal mechanics justify their combined burden** (the principle the GPT review says is missing). Objection, its
  own: a dozen universal mechanics can become unreadable, compulsory upkeep or too costly per tick.
- **Open questions** that this file does not answer: the six "Enable outside this biome" switches; whether a
  dangerous mechanic is on by default on every map; whether the Scald's steam clock is an exception or physics; third-
  party and vanilla biomes; the format and authority of this file.
