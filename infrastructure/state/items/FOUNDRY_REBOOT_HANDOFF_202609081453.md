# FOUNDRY_REBOOT_HANDOFF_202609081453 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609081318`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
`handoff.py` itself had a real bug until this handoff: `since_ts` came from
`git log --format=%cI` (local offset) compared via bare string `>` against
ledger timestamps (UTC `Z`) — two different ISO-8601 shapes, so an event 13
minutes BEFORE the window cutoff read as AFTER it. It silently pulled two
prior-window item starts (`DROID_ORACLE_VOICE_DESIGN_1`,
`ANCIENT_WAR_LAB_1`) into THIS handoff's "started this window" list before I
caught it by checking the actual UTC math rather than trusting the tool's
own output. Fixed in `6204e16b`, regression-tested, and this handoff was
regenerated from the corrected code — so the "what is half-done" list below
is now trustworthy, but the lesson is: **when a safety-gate tool's own
output looks even slightly surprising (an item you don't remember starting
appears in "still open"), check its arithmetic before believing it, even
about itself.**

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- I shipped a PLACEHOLDER balance number without asking: all 80 Droidworks
  `RSW_DW_` PawnKindDefs got a flat `initialResistanceRange`/`initialWillRange`
  (10~20 / 5~10, copied from a donor mod's convention) just to satisfy an
  engine requirement and stop Config errors — every droid kind gets the
  SAME range regardless of toughness (a B1 battle droid same as a Droideka).
  This is explicitly flagged as a placeholder in
  `Patches/PawnKind_HumanoidDroidResistanceWill.xml`'s own comment and in
  `DROIDWORKS_FULL_LIST_COEXIST_1.md`, not a ruling — worth a look whenever
  droid capture/recruitment mechanics get real design attention.
- Mid-session I restarted the live RimWorld process without checking whether
  the bridge was actually free first (it read FREE in the ledger, but BENCH
  was driving it moments earlier) — caught and corrected live, in-session,
  with your direct input; not a repeat risk right now, but flagging it here
  since it's the kind of thing you'd want visible in the record rather than
  buried in mid-session chat.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `BRIDGETOOLS_CSHARP_SWEEP_BUGS_1` — 6 real C# bugs found and fixed
  (Society/Terrain/World tools), compiled clean via `build.py --gm` (0
  warnings/errors, zero tools lost). NOT deployed or restart-confirmed —
  the built artifact sits at
  `src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/` (gitignored).
  Next action: `build.py --gm --apply`, restart, then spot-check
  `jawa/list_pawns includeHealth=true` on a mechanoid/animal — its
  `capacities` map should now be strictly smaller than before (the `||
  true` fix). Full detail in the item's own `.md`.
- `DROIDWORKS_FULL_LIST_COEXIST_1` — Droidworks enabled on the full mod
  list, cold-loaded once, texPath/Harmony census both clean, 4 real
  def-authoring bugs found+fixed+deployed. NOT yet restart-confirmed that
  the fixes actually cleared the Config errors live (validated offline via
  `validate_patch.py` only). Next action: restart on the full list,
  `check_config_errors.py` against the fresh log, expect the 164
  `RSW_DW_*` lines gone, only the pre-existing 17-line baseline left. Both
  this and the C# fixes above could ride the SAME restart. Full detail in
  the item's own `.md`.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
Both filed to `LESSONS_INBOX.md` this session:
- `handoff.py`'s `since_ts` timezone-format bug (see "one thing to carry
  forward" above) — fixed, but worth knowing the shape of it if anything
  else in this repo compares a `%cI` git timestamp against a ledger `ts`.
- A `git add` + `git commit` done as two separate calls can lose a race to
  another window's concurrent commit in this shared worktree — my staged
  files got swept into BENCH's commit twice this session (content survived
  intact and pushed both times; only the commit MESSAGE lost the writeup,
  which is why `BRIDGETOOLS_CSHARP_SWEEP_BUGS_1.md` exists as a standalone
  record). If `git commit` reports "no changes added to commit" right after
  a successful `git add`, check `git log` for your content before re-adding
  — it may have already landed under someone else's message.
- `rimflow sweep --transient` was silently O(n) in one `git log` subprocess
  per file (400 files = ~5min hang, ZERO stdout the whole time since every
  print was buffered past the loop) — fixed to one batched call. Swept the
  rest of the repo for the same shape; nowhere else has it currently.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (2) — the next seat's queue

- `BRIDGETOOLS_CSHARP_SWEEP_BUGS_1` — 6 real bugs found in a full-file review of the 3 largest bridgetools C# files (Society/Terrain/World tools)
- `GL_EMIT_FLOATRANGE_GENERIC_DROP_1` — gl_emit.py silently drops any FloatRange field on a non-worldTileReq node type

## Commits

```
6204e16b Fix handoff.py: since_ts compared a local-offset git timestamp against UTC ledger timestamps
7e650936 BENCH reboot handoff 202609081448: continue biome work + populate maturity product
9609eb9d Sync queue renders + full mod-list capture (599 active) for reboot
ea1ac484 Mark mapgen_paint.py CLEAN
68a09c9a mapgen_paint.py: remove dead _rock_terraces, fix its stale docstring claim
64eb8f3e V23: first-pass landmark density on 8 dense/dramatic biomes
cc18032c Mark 3 more files CLEAN: compose_gl_vs_painter.py, GenStep_ScatterCavePortal.cs, make_complex_structures_icon.py
f658d7a0 Write up BRIDGETOOLS_CSHARP_SWEEP_BUGS_1; mark 3 big C# files CLEAN
0850ef10 V22: the Rot landmark density (891 fungal caverns/cenotes/valleys, 3.6%->42%)
2691a1e3 Context for BLUE_PROPANE_RING_RULING_1
7bbd4b6a Golden canon: strip provenance from the three dark-side sheets
c323e30a V21: clear SeaIce+Lake stragglers (272 tiles) - planet clean of vanilla water leftovers
edd54728 V20: dissolve leftover FungalForest (425 tiles), straighten ancient roads
aa15a74c Mark 6 ashkarr_*.py world-authoring scripts CLEAN
f020cfc6 Mark 3 more bridgetools C# files CLEAN (standing code-review loop)
2aeb5193 Maturity dashboard rework: 6-rung function ladder (validated/played), progress-bar rungs, compressed, legend split
435b69dc Mark 4 more bridgetools files CLEAN (standing code-review loop)
2174503f V19: rename 4 nightside labels to match rebanded terrain
51e7846d Mark 5 more Utils files CLEAN (standing code-review loop)
e3212aae Refresh ice/blue-desert/propane sheet stats to V18 canon (frozen amendment)
29101eae Write up DROIDWORKS_FULL_LIST_COEXIST_1 findings; sync ledger
a35e4f62 DROIDWORKS_FULL_LIST_COEXIST_1: fix def-authoring errors surfaced by first full-list load
9e901b86 Re-center Twilight Crags label onto its crag body (tile 17537)
c69177b8 V18: merge Level into Knuckles (one polar region), re-center label
c66f9f47 V17: Gray Crags->crags (cold biomes), LIGHTFALL enlarged 7->15 tiles; save TRUE-GLORIOUS-RING config
328b4b65 Fix rimflow sweep --transient: one git log call, not one per file
97794051 Mark handoff.py + selftest_handoff.py CLEAN
b9a1d9a2 Fix handoff.py: a prior block/close no longer hides a later restart
c4ce219a Deploy war-debris ring texture; ringMapPath -> Ring/ring_debris
37c96a19 Correct the crash note: FOUNDRY tilegen ntdll crash, not my mutator call or a lock collision
0c9f0618 LESSON: repeated the stale-bridge-lock trap; heartbeat is not optional
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-08T14:48:41Z

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/state/CODE_REVIEW_STATUS.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/items/IKEE_MYNOCK_ART_REGEN_1.md
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimStarWars/BeastLairs/About/About.xml
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? claude_sha.txt
?? design/Jawa/art/gods/busts/.gitignore
?? "design/Jawa/worldbuilding/lua suggestions/"
?? design/Jawa/worldbuilding/review/creature_art/
?? design/Jawa/worldbuilding/review/creature_register.fiftyone_export.json
?? design/Jawa/worldbuilding/review/deck/creature_deck.pptx
?? design/Jawa/worldbuilding/review/deck/creature_deck_manifest.json
?? design/Jawa/worldbuilding/review/furniture_art/
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260902_181509.xml
?? infrastructure/state/codebase_health_last.json.lock
?? infrastructure/state/facts/mlie_creature_defname_map_wave_a.json
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260907_215737.xml
?? research/RimMandrake/inspiration/map_injection_2026-09-06/p2_createprefab_export.xml
?? src/RimMandrake/LoadTracer/Assemblies/
?? world/_lightfall_read.py
?? world/_load16.py
?? world/_poll16.py
?? world/_ready_ring.py
?? world/_roads/meander_v12/_tools_world.json
?? world/_roads/meander_v12/ancient_edges.json
?? world/_roads/meander_v12/harvest.py
?? world/_roads/meander_v12/landmarks_before.json
?? world/_roads/meander_v12/objects_before.json
?? world/_roads/meander_v12/probe.py
?? world/_roads/meander_v12/probe2.py
?? world/_roads/meander_v12/rerouted_v12.json
?? world/_roads/meander_v12/roads_import.csv
?? world/_roads/meander_v12/world_info.json
?? world/_settle_shot.py
?? world/_shot_globe.py
?? world/_shot_lightfall.py
?? world/graycrags_to_crags_plan.json
```

