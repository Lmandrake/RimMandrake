# BAROQUE_BEDAZZLE_PROGRAM_1 — the bedazzle program: eleven biomes raised to the Baroque bar

Commissioned by the owner, typed 2026-09-27. His definition, verbatim:

> *"Bedazzle means we take what's there and review, fill the flora/fauna roster,
> then start ideating what could be REALLY awesome/unique mechanics. You tell me
> a bunch of ideas, I respond with refinement, enrichment, and signification
> addition. You do the same back to me, I respond one more time... and then we
> ticket it out, commission the art, and have a truly Baroque Biome."*

This item is the program: the ritual, the bar, and the order. One biome at a
time (his standing law — no sweeping changes between unfinished and nearly
finished biomes). Each biome's sitting gets its own child item
(`<BIOME>_BEDAZZLE_SITTING_2`-style) filed when its turn arrives, never all at
once.

## The ritual — four movements

1. **Review what's there.** Source, roster, frozen sheet, ledger — read before
   inventing (the standing law: this project keeps having already built it).
   An Opus design pass (backgrounded subagent) writes the review + gap census.
2. **Fill the roster.** Flora and fauna holes filled with NEW invented
   creatures (never a neighbour's — one biome, one home), names in the biome's
   own accent, collision-proven on both instruments.
3. **The volley — four turns, fixed shape.** BENCH lays out a slate of
   candidate mechanics (aimed at the bar below, ranked, with trade-offs). The
   owner returns **refinement, enrichment, and significant addition**. BENCH
   develops the enriched slate back — deeper, wired to engine reality. The
   owner rules once more. *Two full exchanges, then the ideas are done being
   talked about.*
4. **Ticket and commission.** The ruled slate becomes FOUNDRY build items and
   artpipe jobs in the same sitting; renders come back as a review sheet.
   The biome is then a **Baroque Biome**.

## The Baroque bar — nine marks

Every biome that passes carries **at least one of each**:

| # | Mark |
|---|---|
| 1 | A **unique mechanic** — something no other biome does |
| 2 | A **discoverable technology** — the biome teaches you something you keep |
| 3 | **Unique resources** — something you can only get here |
| 4 | **Surprising creatures** — at least one that makes the player say what |
| 5 | A **GIANT beast** — the biome's colossus |
| 6 | A **gravship touch** — the biome modifies, marks or threatens the player's ship in its own voice |
| 7 | An **interesting soundscape** — the biome heard with eyes closed |
| 8 | **Interesting weather** — sky effects that belong to nowhere else |
| 9 | A **relationship to the gods** — the biome's place in the ideoligion/lore layer |

**Rites as well as tech (owner, typed, 2026-10-01 10:08 PDT):** *"I am starting to love the idea
that you don’t just discover tech in the biomes you discover new rites."* So every sitting asks,
beside mark 2: what rite does this biome teach the Salvation, which god does it appease, and in
what way no other rite already does? The rite is found in the biome, learned on the Rites tab's
"found rites" row, held anywhere afterwards, and lives in `mandrake.rut.rites`. A biome may answer
"none", but the question is asked and recorded. Register and mechanism:
`design/Jawa/salvation_rites_2026-10-01.md` (`SALVATION_RITES_UNIFICATION_1`).

The bar is also the **design gate**: a biome — including one grandfathered
below — ships only once a review has scored it against these nine and the
owner has ruled the misses acceptable or filled.

## The order

| # | Biome | Content today (1–5, MEASURED 2026-09-27) | Notes |
|---|---|---|---|
| 1 | Contagion | 3 | |
| 2 | Wasteland | 2 | |
| 3 | Blue Desert | 2 | prior sitting closed; this pass upgrades it to the bar. Joining the full list (ruled today) |
| 4 | Flooded Canyon | 2 | hard-deps FlowWorks |
| 5 | **The Cauldron** (was Poison Forest) | 2 | 🔴 RENAME ruled 2026-09-27, owner-typed — execute at its sitting (live-tile check before any defName change) |
| 6 | The Forge | 2 | |
| 7 | Leaning Scrub | 2 | holds the Blurrg reservation (Long Shade ruling) |
| 8 | Long Shade | 1 | 2026-09-27 sitting covered movements 1–2 + part of 3; this pass runs the full volley to the bar |
| 9 | Stillsand | 1 | same — sitting + fill-out done; volley to the bar owed |
| 10 | Warscar | 1 | |
| 11 | **Abyss** (was the Forsaken Crags, then Black Crags) | 1 | sitting `BLACKCRAGS_BEDAZZLE_SITTING_1`, done; rename executed `a534284e4` (ABYSS_FULL_RENAME_1) |

## Grandfathered — already bedazzled, gate still applies

By the owner's word, every other biome mod counts as bedazzled today:
**The Rot, Fever Wood, Greentide, Gelatinous Slime, Weeping Stones, The Sump,
Miasma, Webwork, Rust Cathedral, Lantern Deeps, Pyrelands, Nightside Ice** —
and the four seas (Twilight, Grey, Scald, Propane Lake), which ride their own
floor-pass track (`GREYSEA_FLOOR_PASS_1` shape; Scald and Propane passes still
owed). Any of these **may be re-reviewed against the nine-mark bar as a design
gate before it ships** — that review is a scoring sitting, not a rebuild, and
it files only what the owner rules missing.

## Relationship to the rest of the machinery

- **Packaging is orthogonal**: all of these compose into "RimMandrake: Baroque
  Biomes" per §7 Q17 (`BIOME_MOD_UNIFICATION_1`) regardless of bedazzle state.
- **The repaint stays terminal**: bedazzling touches content, never tiles;
  worldmap faces are `WORLDMAP_BIOME_APPEARANCE_1`, after the repaint.
- Art rides artpipe per sitting; review sheets per the standing loop.

## verify
- Eleven biomes each have a closed bedazzle-sitting child item recording the
  full four-movement ritual, and score 9/9 on the bar (or carry the owner's
  explicit waiver per miss).
- Both renames executed (Cauldron, Abyss) with live-tile checks logged.
- No grandfathered biome shipped without its gate review recorded.
