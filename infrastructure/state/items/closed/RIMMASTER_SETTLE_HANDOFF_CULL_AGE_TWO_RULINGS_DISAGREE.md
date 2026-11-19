# RIMMASTER_SETTLE_HANDOFF_CULL_AGE_TWO_RULINGS_DISAGREE

Two rulings set how old a superseded handoff must be before it is culled:

- `src/RimMandrake/Utils/handoff.py` `CULL_DAYS = 30`, citing the owner's ruling of 2026-09-18 ("delete at 30 days, git is the archive").
- Lodestar's `handoff` skill (`~/dev/Lodestar/docs/handoff/SKILL.md`, "The cull rule"): 7 days after supersession, owner card
  2026-10-19 ("7 days after superseded"); a per-repo `.handoff.json` may override.

The 2026-11-07 spring clean culled 97 handoffs at 7 days on the Conductor's brief (7143c0704d); the project constant was left at 30.

**Done when** one rule stands for this repo: either `CULL_DAYS` becomes 7 (or reads the repo's `.handoff.json`) with its comment citing
the 2026-10-19 card, or a `.handoff.json` / comment records why this project keeps 30; and `handoff.py --cull` and the handoff skill agree.

## What the card said

<!-- answered 2026-11-19T00:34:59Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** A handoff is the note a closing agent window leaves for the next one. Two of your rulings give different ages for deleting old ones: the project says 30 days (2026-09-18), your cross-project tool says 7 days after a newer handoff from the same window replaced it, lessons filed (card, 2026-10-19). 63 handoff files sit in this project; git keeps every deleted one. Nothing is deleted until tonight's Crystallize pass has run. Which age should this project use afterwards?
**Picked:** 7 days after replaced (Recommended)
**Its description:** Why: one rule on every machine, and it is your newer ruling. Buys a short handoff folder that agents read faster. Costs: an old handoff leaves the folder sooner, so reading one after a week means a git lookup. Recommended because only replaced, harvested files go.
**Other options:** Keep 30 days here · Decide after Crystallize
