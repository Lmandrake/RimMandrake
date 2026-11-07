# RIMMASTER_SETTLE_HANDOFF_CULL_AGE_TWO_RULINGS_DISAGREE

Two rulings set how old a superseded handoff must be before it is culled:

- `src/RimMandrake/Utils/handoff.py` `CULL_DAYS = 30`, citing the owner's ruling of 2026-09-18 ("delete at 30 days, git is the archive").
- Lodestar's `handoff` skill (`~/dev/Lodestar/docs/handoff/SKILL.md`, "The cull rule"): 7 days after supersession, owner card
  2026-10-19 ("7 days after superseded"); a per-repo `.handoff.json` may override.

The 2026-11-07 spring clean culled 97 handoffs at 7 days on the Conductor's brief (7143c0704d); the project constant was left at 30.

**Done when** one rule stands for this repo: either `CULL_DAYS` becomes 7 (or reads the repo's `.handoff.json`) with its comment citing
the 2026-10-19 card, or a `.handoff.json` / comment records why this project keeps 30; and `handoff.py --cull` and the handoff skill agree.
