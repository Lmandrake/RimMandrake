# SW_SEA_MONSTERS_ART_1 — sea-monster art pass with the owner

Tier: RimStarWars (`mandrake.rsw.*`, prefix `RSW_`). Source roles:
`design/Jawa/worldbuilding/depths_concept.md` §5, sized under beast-normalization
Laws 3+4 — no retrofit, born normalized.

## spec

Owner ruled 2026-08-31: **all six §5 roles**, and the three predator roles are the
**canon Naboo trench trio**:

| Role | bodySize | Creature |
|---|---|---|
| Silt ambusher | 1–2 | **Opee sea killer** (canon) |
| Harpooner | 2–4 | **Colo claw fish** (canon) |
| Leviathan | 12–20 | **Sando aqua monster** (canon) |
| Shoal grazer | 0.1–0.5 | original, Naboo-flavored |
| Scavenger swarm | 0.2 | original |
| Colossal neutral | 30+ | original filter-feeder |

Process: owner's mockup loop — offline PNG options per creature, he picks, then
palette passes; only then facings + validator + def work. Mockups live in
`Transient/sea_monsters_mockups/` (review-once material).

**Round 1 CLOSED by owner ruling, 2026-08-31: ALL 18 mockups kept, each its own
creature** — *"it's all so good I want you to keep all of them and make them each
their own creature. You pick how they align... Don't get rid of any of them."*
The roster (BENCH's alignment, on his word) is
`design/Jawa/worldbuilding/sea_beasts_roster.md`: 3 species per role — canon
trio + variants, canon scalefish (mee/faa/laa), yobshrimp + originals, three
original colossi. Mockups are now KEEPERS, committed at
`src/RimStarWars/SeaBeasts/art/mockups/` (6a02f477); palette passes skipped.
Generation prompts remain banked at
`src/RimStarWars/SeaBeasts/art/gen_sea_mockups.py`.

## verify

Final art closes only with a validator pass per facing and a PROVE/EXPECT/LIES
plan committed beside each PNG.

## criteria

18 creatures per the roster doc; sprite-skill contract honored (128 px/cell,
chroma-key alpha, silhouette-first at display size); defs sized per the roster
table under beast-normalization Laws 3+4.
