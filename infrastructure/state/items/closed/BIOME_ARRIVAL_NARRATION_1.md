# BIOME_ARRIVAL_NARRATION_1 — one letter when the ship first lands in a biome

Filed on the owner's card decision (2026-09-24, "Yes, file it"), from his own
prompt earlier the same sitting, typed: *"I'm wondering if the narrator should
announce each biome when the ship lands to give some hints."*

## spec

- **RM-tier machinery**: each biome mod ships one arrival letter — fired at the
  first gravship landing in that biome per save, never repeated. Content: that
  biome's survival reads, drawn from its sheet. The Sump's: watch the mice —
  where the lines bend, the tar lies; an unbroken pale crust no line touches is
  a lie; a soffeth ring means gas below.
- **Utinni voice**: the campaign narrator's voice is a patch OVER the RM letters
  (flavor replacement, not new machinery) — the free biome mods speak plainly,
  the campaign speaks in character.
- Shared mechanism, not per-biome C#: one small letter-on-first-entry component
  the biome mods all use (natural home: the shared kit assembly; check
  `src/RimMandrake/GravshipLanding` for an existing landing hook before writing
  a new one).
- Complements, not duplicates, the discovery techs (`SUMP_GASLIGHT_1` §6,
  `INDIGENOUS_TECH_REVISIT_1`): the letter teaches reads; discovery unlocks tech.
- Each future biome sitting writes its letter text as part of the sitting.

## verify

Quicktest: first landing in a biome fires exactly one letter naming that biome's
reads; a second landing fires nothing; with the Utinni layer active the same
letter arrives in the narrator's voice.

## criteria

Every biome introduces itself once, at the moment its lessons start mattering.
