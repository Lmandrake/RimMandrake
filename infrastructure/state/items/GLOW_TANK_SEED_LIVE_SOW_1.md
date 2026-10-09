# GLOW_TANK_SEED_LIVE_SOW_1 — glow tank seed culture consumed live

57536f0db made Building_GlowTank consume seed culture once established (ConsumeFuel previously ran only on blackout). Build OK; never run live.

## criteria
- [ ] A sown glow tank on a quicktest map consumes seed culture and glows, with the established flag set, and stops/behaves per spec without power blackout.

## verify

Bridge: spawn tank, sow, step ticks, read fuel and flag (L2). Origin: GLOW_TANK_SEED_CULTURE_1.

## Watch out

Filed by the 2026-10-09 upkeep pass: the originating item was closed `implemented --none-owed` with only offline evidence. Mechanism-never-seen line: the offline fix changed the harness/mod code path itself, and that path has not been observed running since.
