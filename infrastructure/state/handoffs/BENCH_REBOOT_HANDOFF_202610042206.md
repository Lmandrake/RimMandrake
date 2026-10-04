# BENCH_REBOOT_HANDOFF_202610042206 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610042057`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The Biome FloraFauna Art Review (`BIOME_FLORAFAUNA_ART_REVIEW_1`) is BENCH's priority and is scoped to **Baroque Biomes only** (RM_ BiomeDefs of `src/RimMandrake/Biomes.compose.json`). The first three sheets are BUILT and pushed (`f37050f28`) but **not yet served to him**: `Transient/biome_ffar/{desert,deep_desert,blue_desert}_sheet_2026-10-04.html`. Rebuild (picks up new renders): `python3 src/RimMandrake/Utils/art/art_sheet.py --refresh --biome first3 --date 2026-10-04`. His rulings for this wave are on the item note (order LongShade → Stillsand → BlueDesert → rest; sheet reaches him only when every row has art; canon and non-canon are SEPARATE linked rows; desert sitting 1 picks are prefill, not applied).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Whether the RSW_ (Star Wars) halves of RM_ stand-ins belong on the Baroque sheets: 14 on RM_LongShade alone (e.g. RM_Ommok ↔ RSW_Ommok) show only as "related, not in this biome" — so no linked pairs appear yet. That is his call; ask before serving the desert sheet.
- Blue Desert sheet still has 2 NO-ART rows (AA_Thunderbeast — he ruled "replace" 2026-09-20; Vapaad) — so by his rule it is not ready.
- 21 droid render jobs `desert_gap_*` were queued under the pre-correction (vanilla Desert) scope; likely not on any Baroque roster — wasted renders, nothing installed.
- Art register is NOT yet automatic: artpipe collect / port scripts / per-mod art scripts still write Textures directly, and no commit guard exists. He was offered this lane (did not answer yet).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — LongShade (75 rows, 34 canon) and Stillsand (28) sheets have every row arted; NEXT: ask him the RSW_-twin question, click-test one of each control in a real browser, then serve the desert (LongShade) sheet to him with its full native path.
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — Blue Desert has 2 NO-ART rows; NEXT: queue canon/donor-briefed artpipe jobs for AA_Thunderbeast replacement and Vapaad at priority 10, then rebuild with `--refresh`.
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — remaining 25 Baroque biomes; NEXT: run gap-fill per biome in order from `Transient/biome_ffar/census.json` (verify by name against artpipe, not census no-art count) and add each biome to `art_sheet.py --biome`.
- `ART_VERSION_WRANGLING_1` — ledger built, writers not rewired; NEXT: ask him to green-light the lane that routes artpipe collect/port/per-mod scripts through `art install` and builds the commit-blocking art guard.
- `GIT_WORKFLOW_MIGRATION_1` — NEXT: on 2026-10-05 measure manual rebases/day and D:\ writes over 3 days, record in plan §4, close it.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- census marks NO ART on rows whose renders exist by name (filed: LESSONS)
- "our biomes" = Baroque Biomes RM_ defs, never vanilla/RUT_ (filed: LESSONS)
- a helper's uncommitted `infrastructure/state/art/events/BENCH.jsonl` blocks every other pull --rebase in the clone; `./publish` got through (see: design/RimMandrake/GIT_WORKFLOW.md)

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (1) — the next seat's queue

- `BIOME_FLORAFAUNA_ART_REVIEW_1` — Biome FloraFauna Art Review: one sheet per biome covering every flora+fauna row, >=1 art version each, canon refs + Must show on every canon creature,

## Commits

```
13385c5f1 ledger: BIOME_FLORAFAUNA_ART_REVIEW_1 note (sheet rebuild command)
f37050f28 art_sheet.py --biome: per-biome flora/fauna art sheets (LongShade, Stillsand, BlueDesert)
4c8449f73 ledger: FOUNDRY and OWNER shards for the MessyConduit review window
9848cbfc1 FOUNDRY handoff 2026-10-04 PM: MessyConduit Northstar checkout, human review map, style-per-build design; four lessons
f3bf4d8fc MessyConduit Northstar: round-2 runs at 8a8a6a00ba47 - matrix GREEN (109/109 scenes; catalog regenerated after B17), core REFUSED on 4 scope rows, aerial GREEN
797aba07e Trio gap-fill: no in-scope gaps (desert/deep_desert RUT-only; blue_desert RM_ rows had art or donor art)
3857b33aa biome_census.py: rescope to the Baroque Biomes RM_ defs (from Biomes.compose.json), per-row layer
7b5eceb89 ledger: BIOME_FLORAFAUNA_ART_REVIEW_1 scope is Baroque Biomes only
5f5682c4e ledger: MESSYCONDUIT_REVIEW_ROUND1_1 round-2 note
daa4a7af6 MessyConduit validation: strip rows read the Modern look (owner B1), Modern span expected black (owner B12); human_review --shot (game render, no window focus)
11c42922e biome_census.py: per-biome flora/fauna art + canon census (BIOME_FLORAFAUNA_ART_REVIEW_1)
e7f9f25a6 Desert gap-fill: 7 droid art jobs queued at priority 10; 10 of 17 no-graphic rows already had art
0f59d02b9 MessyConduit round 2 T5-T9: one wire per measured insulator tip, cast span shadow, hookups in the look's cable, deployed-reel switch (stand-in), one Mod Settings entry with tabs, roofless review shed
24950e8b1 MessyConduit style-per-build design: record owner decisions (B, largest run wins, free restyle button, per-run cord colour incl. random mixture)
c8ae1923f MessyConduit: design pass for choosing art style at build time (per-run style, 3 architectures, owner questions)
0a14ee45d ledger: BIOME_FLORAFAUNA_ART_REVIEW_1 rulings note
8ac23ee0f MessyConduit round 2 live fixes: hose fittings drawn bare under the wrap, aged wrap tint, open-end wrap to the cut; review map settles power before freezing (T4), --sub close framing, spare N bracket outside
e7d0b7946 MessyConduit: modern wall bracket art wired (v2; its north/south renders were drawn for the opposite wall, swapped)
6ebc84361 MessyConduit round 2: one-piece fallen wire to the break, span fan to insulators, hose binding wraps, per-facing bracket art, st.9 lamp inside shed
f37d7f6f5 ledger: owner event for BIOME_FLORAFAUNA_ART_REVIEW_1
... 2 more: git log --oneline 15535d8bb..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-04T22:03:13Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? conversations/   session transcript exports written by a hook; deliberately untracked, not BENCH work
```

