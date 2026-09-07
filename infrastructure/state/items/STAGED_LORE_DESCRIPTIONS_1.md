# STAGED_LORE_DESCRIPTIONS_1 — descriptions that change as the story is learned

Filed by BENCH from the Scarlands sitting, 2026-09-06. **Provenance, not
authorization** — the owner mused: *"I wonder if the scenario could actually
change its own terrain descriptions as Lore is revealed, wouldn't that be
amazing, depending on where they were in the story?"* This item answers the
wonder; whether to BUILD it is his ruling once feasibility is known.

## The question

Can biome/terrain/thing descriptions (and settle warnings, item flavor) swap by
campaign lore-stage — so the Scarlands reads as "inexplicable wasteland" until
the player learns the truth, then as what it is?

## Feasibility sketch to verify (not assume)

- Descriptions are def fields read at display time in most inspector paths —
  a Harmony postfix on the description getter keyed to a WorldComponent
  lore-stage is the likely cheap route; verify which UI paths cache strings.
- The reveal gates already exist as design: `the_scarlands.md` §GM ladder
  (neutral droids → Cathedral → educated factions → bastion record).
- Consumers beyond the Scarlands if it works: the Contagion, the Propane Lakes'
  war lab, the Webwork's not-native mystery — every §GM-partitioned biome.

Deliverable: a one-page feasibility verdict with the patch surface named, then
his go/no-go.
