# Dev start save on the 374 list — tomorrow's setup proof (FOUNDRY live helper, 2026-10-20e)

**Tomorrow starts here:** IN PROGRESS — verdict pending.

Bridge taken 01:20 PDT (`rimflow bridge take --for "dev start save on 374"`). Game was DOWN; ModsConfig = owner's 374 (== FULL.LATEST, not edited).

## Status
- [x] bridge take
- [ ] cold load 374 (wall clock, first exception vs 2026-10-20b)
- [ ] load ASHKARR_DEV_START_2026-10-20.rws (time, exceptions by class)
- [x] save censuses (class / def / adoption) vs 374 — offline, done 01:28 (below)
- [ ] ~3000 ticks at speed 3, exceptions, TPS
- [ ] colonists / ship / Ikee bond
- [ ] FOUNDERS copy load
- [ ] screenshots
- [ ] end state + bridge release

## Offline save censuses against the live 374 ModsConfig (01:28)
Saves sha256 before any load: `dev_saves_sha_before.txt`. Files: `class_census_*.txt`, `def_census_*.txt`, `adoption_*.md`.

| save | class census | def census (things) | adoption check |
|---|---|---|---|
| ASHKARR_DEV_START_2026-10-20 | 0 unresolved class sites | 6786 things, **0 unresolved THING defs**; 73 other refs / 22 defs (Aptitude* passion-style names) | exit 1: **5 unresolved names**, 142 hits — Thing `Horax` x1 (Star Wars Animal Collection, a record ref), VSE `Major` x55 / `Minor` x84 / `Foreman` x1, `Paste` x1; kindDefs 31 distinct all resolve; world grids clean |
| ASHKARR_DEV_FOUNDERS_2026-10-20 | 0 | same 0 unresolved THING defs | exit 1: same 5 names, 133 hits |

On PAINT 83 the same START save had 96 unresolved names (Alpha Memes rituals, AA_Eyeling, ...); the 374 list carries
those mods, so the residue drops to 5. Exit 1 = the tool's "0 unresolved" bar, not a load blocker (record/passion names).
