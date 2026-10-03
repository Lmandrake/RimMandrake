# BENCH_REBOOT_HANDOFF_202610030757 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609210912`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner's decision queue is the bottleneck, not design: 17 card sittings are ranked in `Transient/bench_owner_queue_2026-10-03.md`, and 13 of them are pre-built as validated AskUserQuestion cards in `Transient/bench_owner_cards_2026-10-03.json` (sittings 9 and 10, the desert sheet and the 18 triage questions, plus 15-17 added later, are not yet carded). Start his next bench session by putting those cards, sitting 1 first (sound sourcing unblocks audio in six biomes). Do not generate more designs until he has worked the pile down.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Build pause lifted** (owner, typed, 2026-10-02); recorded in CLAUDE.md, BENCH.md, FOUNDRY.md, debug_process.md (`6f2c76eec`).
2. **Every pitched rite accepted** ("Accept all rites for now."). The audit (`design/Jawa/salvation_rites_unification_audit_2026-10-02.md`) found 0 of 42 found rites built, and if design-doc rites count toward the cap, Rekko, Ohm and Ozzik sit at six.
3. **Both sea-floor sittings ruled** (Chill, Scald); none of it reaches a player until `SEABED_PER_SEA_FLOORS_1`: every sea's floor is still one empty placeholder.
4. **The Atlas is built** (`src/RimUtinni/Atlas`, all 12 files code-review CLEAN, mock suite GREEN); with FOUNDRY for its live run. Its 24 riddle/hint/lore texts want his writing sitting.
5. **Defects filed from read-only findings, not seen in game:** `MINERAL_BIOME_LEAKS_1`, `SILTTRAP_TERRAINS_UNBUILT_1`, `GRAFFITI_WALL_LINKED_CROP_1` (one screenshot settles it).
6. **`D:\Luke\dev\MandrakeAudio` exists** (Sonniss 2024 zipped, Kenney CC0, synth toolchain) and no item knew it.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `BENCH owner queue` — 17 sittings drafted; NEXT: put `Transient/bench_owner_cards_2026-10-03.json` cards to him, sitting 1 first, and file each sitting's build to FOUNDRY as it is ruled.
- `UTINNI_DISCOVERY_ACHIEVEMENTS_1` — built, reassigned to FOUNDRY; NEXT: hold a writing sitting with him on the 24 drafted entries once FOUNDRY's live run is green.
- `LONGSHADE_BEDAZZLE_CONTENT_1` — fills + gloomcast built (FOUNDRY item, blocked); NEXT: when artpipe job `RM_Shadespire_c` renders, copy it over `RM_Shadespire_a.png` and show him.
- `DROID_CANON_LIBRARY_1` — infobox sources exhausted; NEXT: ask him whether article-prose extraction is worth doing, else close it.
- `GIT_WORKFLOW_MIGRATION_1` — waiting on its date; NEXT: on 2026-10-05 measure manual rebases/day and Claude writes to D:\ for 3 days, record in the plan §4, close it.
- `NORTHSTAR_ISHKO_PILOT_1` — with FOUNDRY; NEXT: when FOUNDRY releases the bridge, check its live_session run recorded GREEN.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Two gpt_consult runs at the same moment can cross answers; run them one at a time with a subject guard. (filed: lessons)
- A review subagent ran mark-clean after a diff-only check of its own fix; the full re-review found a real miss. (filed: lessons)
- `rimflow unblock` refuses on another seat's item; the owner's `--owner-said` is the override, a note is the default. (see: CLAUDE.md "Correctness outranks seat ownership")

## Closed since the last handoff (2)

- `WORLDVIEW_MISLABEL_FALLOUT_1` — 9f795164d
- `NARRATIVE_DICTIONARY_PILOT_1` — 32e980c1b

## Filed and still open (2) — the next seat's queue

- `MINERAL_BIOME_LEAKS_1` — Our biome minerals leak planet-wide (read from defs 2026-10-02): Webwork silk knot scatters on every rocky map; deep drilling anywhere can hit lantern
- `GRAFFITI_WALL_LINKED_CROP_1` — Graffiti wall marks may draw only a 1/16 crop of their art: wall-linked graphics treat a texture as a 4x4 atlas and ours are single centred images (re

## Commits

```
f67c90a5d Event traces design noted; file GRAFFITI_WALL_LINKED_CROP_1; owner queue updated
4a0238edc EVENT_TRACE_PROPS_LIBRARY_1: design for 19 event traces, carriers engine-checked, build plan + 4 owner questions
eda351324 ledger: close NARRATIVE_DICTIONARY_PILOT_1 (blind test PASS)
32e980c1b narrative dictionary pilot: blind run scored, verdict PASS
72a77c044 Stillsand: solar still and wringing still on the sun code, water ledger, 3 settings (offline; RM_Brine has no source yet)
41bc6751f Abyss: the Dark, the Unveiling, storm call, Murk hediff; real grain replaces etchfall stand-in (offline; RM_Summ spawn untested)
4fd6ed3c3 MessyConduit: live matrix 109/109 PASS incl. 9 hose scenes; M9 removal check PASS; contact sheets regenerated
2e036b8c7 narrative dictionary pilot: 45-row prop table, 8 vignettes, 4 dressings, blind packet, GAPS.md
c4f7aed27 narrative dictionary pilot: pre-register the bar before any dressing exists
6bba8a947 code review: droid_canon_fill.py clean after full re-review
c5f4a0381 droid_canon_fill: infobox regex missed the Droid_series spelling (33 pages); re-run from cache filled nothing new
4d9a74dbc code review: droid_canon_fill.py clean
a83b7101e droid_canon_fill: never cache transient API errors as MISSING; atomic cache/index writes; utf-8 curl
11fc6b31e ledger: Long Shade block reasons mostly cleared
61ae44e1a code review: Scavenger's Atlas 12 files clean
ece1567eb Atlas review: hediff trigger lit lamps for fogged pawns; detection_off test could pass vacuously
1cecde3c4 Venomvine pitch noted; owner queue updated
12aa60316 LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1: six further venomvine forms pitched, recommend sworn/rearing/hoard
430f295e4 Sweetline name register noted; owner queue updated
742e259b3 LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1: draft sweetline tree name register + namer vocabulary
... 15 more: git log --oneline 9f795164d..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : UP
- Bridge: for     NORTHSTAR_BLAND_TILE_1 bland tile generate

Working tree clean apart from untracked `Transient/`.

