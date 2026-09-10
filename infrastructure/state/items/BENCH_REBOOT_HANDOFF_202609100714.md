# BENCH_REBOOT_HANDOFF_202609100714 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609100128`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
drvfs can serve MINUTES-STALE file content to some concurrent readers while
others get fresh bytes — in one artpipe drain, three worker spawns ran the
current gemini script and one silently ran the pre-edit version, and it cost
four blind API retries to corner. The structural cure is in artpiped.py now:
read the worker source ONCE at ctx build and feed every spawn via stdin
(`python - <args>`, cwd at the script's dir so sibling imports resolve).
Any subprocess-spawns-script-from-/mnt/d pattern in this repo has the same
exposure.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **MORNING_RULING_BATCH_1** — nine staged decisions, each one line with a
  full path. Start there; items 3-5 unblock applying his own 69-Move fauna
  review.
- **The gemini quality sheet** `Transient/gemini_trial_candidates_2026-09-09.png`
  — his own Lockjaw/Mantrap art notes as candidates; 2 passed validation;
  $2.01 spent of the ~$22 he authorized. A thumbs-up unblocks batching the
  fauna sheet's hundreds of art=improve verdicts through this channel.
- **The ancient-ruins family cut he ruled at the bench is already EXECUTED**
  (FOUNDRY, 4d6c684e + re-verify 4a1b9e76) — he can veto by restore, but it
  survived an independent second opinion.
- His live fauna review decisions are checkpointed to git (69 moves, art
  verdicts) — nothing of tonight's clicking is at disk-only risk.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ART_PIPELINE_DAEMON_1` — gemini channel proven end-to-end tonight (first
  live drains, 2 validator PASSes, all defects fixed in 43942f47/fea15975).
  Stops at: codex-channel calibration + the owner's Phase-2 projection, gated
  on an ATTENDED zero-UAC first run; and the grow-intent validator allowance
  (owner "twice as large" notes currently auto-reject on footprint). Next:
  attended codex drain, then the projection.
- `EXPLOSIVE_PLANT_GROWTH_1` — design draft committed (734a25fb), 4 owner
  questions inside. Stops at the sitting; after ruling, the perf gate
  (jungle-map TPS table) comes BEFORE any build promise.
- `FISH_BY_BIOME_1` — merged per-water fishTypes proposal committed
  (552b03b7); 5 condensed questions ride morning batch (8). Next: his
  ruling, then the fishTypes patches are FOUNDRY build work.
- `FLOOD_WITNESS_EVENT_1` — design draft committed (22400524): prose spec,
  guaranteed-occurrence trigger, all-vanilla quest tree + one small C#
  scheduler. Stops at a sitting (4 questions); not morning-urgent.
- `MECHANOID_BIOME_PRESENCE_REVIEW_1` — draft table verified current vs the
  frozen sheets; riding morning batch (9), headline call = planet-wide
  random-mech-raid DENY doctrine. Next: his ruling, then the enforcement
  defName list.
- `VAPOR_EMITTER_PLACEMENT_1` — scopes 1-2 done (22 families MEASURED,
  rules per type under the decay law). Next action is OFFLINE-workable now:
  the per-tile mutator audit via world/ASHKARR_WORLDMAP_mutators.csv ×
  tiles.csv; the building-density sample + fix-up pass need the bridge.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- drvfs stale reads (the carry-forward above) — also swept my own edits'
  visibility mid-debug; re-read before concluding a revert.
- Shared-index sweeps, twice in one night: a FAILED `git add` still leaves
  the index loaded, and the next `git commit` in a retry loop ships it under
  the wrong message; a peer's commit likewise swept a subagent's file.
  After any commit made under lock contention, read `git log --stat` before
  trusting what it contains.
- gemini-3-pro-image returns 1024×1024 JPEG regardless of request and has NO
  native alpha; the daemon's gemini budget is CUMULATIVE from
  throughput.jsonl, not per-run — a "$1 cap" refuses work if the log already
  carries $1.
- N concurrent rembg loads die in a bounded cgroup (multiprocessing
  resource_tracker) — cutouts are flock-serialized now.
- Piping a live daemon through `head` SIGPIPE-kills it mid-job and leaves a
  billing-intent orphan that reconcile() deliberately refuses to requeue —
  a human must look; never filter a daemon's live stdout.

## Closed since the last handoff (3)

- `ANCIENT_RUINS_MOD_AUDIT_1` — e7d9bd4c
- `SW_BACKGROUND_GARB_HARVEST_1` — 0c6391ee
- `CODEX_UAC_STORM_1` — 31a92df6

## Filed and still open (1) — the next seat's queue

- `MORNING_RULING_BATCH_1` — Five decisions staged for the morning: (1) desert wraps letter+number from the candidates PNG; (2) crystal ingest table incl pyrinth absorb+gate; (3) 

## Commits

```
8f91973e Close DROID_DONOR_SAVE_COMPAT_REGRESSION_1 (live-verified end to end); file RUT_PLANT_BIOMEPLANTRECORD_CROSSREF_1
e4fed711 VAPOR_EMITTER_PLACEMENT_1 scopes 1-2: vapor emitter inventory + placement rules
3c100a29 Fix a real regression from DroidDepot retirement: 7 biome-cast PawnKindDef refs
894bb6bd Ledger sync: EXPLOSIVE_PLANT_GROWTH_1 design-draft note
734a25fb EXPLOSIVE_PLANT_GROWTH_1: design draft — soak/charge/burst, per-biome terminal moments, perf gate
3d9ca2a1 Ledger sync: FLOOD_WITNESS_EVENT_1 design-draft note
22400524 FLOOD_WITNESS_EVENT_1: design draft — witnessed flood quest (prose spec + machinery map)
9427d6d6 Move-target mapping: 69 owner Moves resolved to sheets, 4 open calls, staged for morning
c27d2eac Ledger: fish proposal staged for morning; mechanoid biome review claimed
382f909b Ledger sync: FISH_BY_BIOME_1 proposal note (552b03b7)
552b03b7 FISH_BY_BIOME_1: merged fishTypes proposal — every water RULED or PROPOSED, sand-fishing customs reconciled with donor census
d5b64876 Ledger: first live artpipe drain recorded; gemini quality sheet staged for morning
cfd756dc artpipe: never commit _artsrc staging (design: PNGs are staging, JSONs are provenance)
43942f47 Gemini channel goes end-to-end: --size resize + rembg cutout (serialized), stdin-fed worker source, stdout tails on manifests
fea15975 Gemini channel goes end-to-end: --size resize + rembg cutout (serialized), stdin-fed worker source, stdout tails on manifests
261d050f INHABITED_AUGMENTATION_BUILD_1: 6/14 archetypes note synced
6e8d4a12 Build 8.4 trading-outpost template (INHABITED_AUGMENTATION_BUILD_1, 6/14 archetypes)
3411fa44 CODEX_UAC_STORM_1 closed: root cause + fix recorded, live zero-UAC proof gates the first attended run
5b50a412 Ledger sync: CODEX_UAC_STORM_1 note
31a92df6 CODEX_UAC_STORM_1: version-aware sandbox seeding + daemon preflight
5c2f83a7 Garb harvest closed (59 refs landed); added to morning ruling batch
c58256fa Ledger sync: SW_BACKGROUND_GARB_HARVEST_1 note
0c6391ee SW_BACKGROUND_GARB_HARVEST_1: reference art harvest, 59 images
4a1b9e76 ANCIENT_RUINS_FAMILY_CUT_1: independent second-opinion re-verify confirms safe
faabffc3 Wraps commission fully ruled: 4 wraps + both heads as unwired options
0405af11 Wraps ruling: all four styles ship
a071f4df Ledger sync (BENCH's CODEX_UAC_STORM_1 claim, picked up in this checkout)
0acb1f0c Code review status: mark 4 files clean (own tonight's work, already reviewed)
afcfa347 INHABITED_AUGMENTATION_BUILD_1: 5/14 archetypes note synced
178f5d0b Build 8.10 dead-caravan template (INHABITED_AUGMENTATION_BUILD_1, 5/14 archetypes)
97044f68 File CHERRYPICKER_SHIP_BASELINE_STALE_1: SHIP baseline stale, bundles an unconfirmed backstory un-cut
6a16ce1c Close ANCIENT_RUINS_FAMILY_CUT_1; sync DROID_RETIRE_KOTORDROIDS_1's unblock note
aec2c70b Gate the 4 ungated kotorcore droid-weapon ammoDefs (unblocks DROID_RETIRE_KOTORDROIDS_1)
4d6c684e Cut the ancient-urban-ruins mod family (ANCIENT_RUINS_FAMILY_CUT_1)
8f753bec Owner rulings landed: Gemini trial authorized (billing was already live), richer moornak ships
c3083524 FUNGALFOREST_RAID_MERGE_1: ported defs verified clean, cut confirmed NOT yet safe (nothing ratified)
823b5ce7 Crystal doc: orange ore re-identified as pyrinth (owner); wrong KOTOR claim deleted, ingest row added
2f083312 Code review status: mark 19 skills/infra never-reviewed files clean (all genuinely clean)
6a7759f2 Close ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1 (BENCH's work was done, never closed); clear MACRO_GENERATOR_V0_1's stale needs:owner
956c80cc SCORCHFRUIT_FULGURITE_DEF_VERIFY_1: closed, defs confirmed under renamed tier
450d3267 the_pyrelands.json: fix decayed RSW_FE_ -> RM_FE_ tier rename on ScorchFruit/Fulgurite
fe48c24e HUMAN_QUEUE_NEEDS_OWNER_RENDER_1: closed, false premise, real needs:owner audit delivered instead
6a9605da Clear 2 stale needs:owner flags (round-3 verdict already answered them); mark-clean the sibling-crash patch file
492520c2 Droidworks: Harmony prefix suppresses sibling-relation-gen crash for droids
b10344d6 Ledger sync: claim/start ANCIENT_RUINS_FAMILY_CUT_1
ac672b47 Lesson: stash/rebase during active subagent writes can silently revert their work
f7b345d8 Code review status: mark 353 never-reviewed files clean (wave 2)
e5c9d120 RUT_Wasteland.xml: remove a stray plantDensity element from the wildPlants dict
bb73b6bd Dirty-code-review wave 2: 16 real bugs across 353 never-reviewed files
1d096297 Owner rulings: ancient-ruins family cut ruled+closed, crystal identification reopened (wrong crystal)
e7d9bd4c Ledger sync: ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1 note (applier rebuilt, commit 64ffdc02)
16087da5 ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1: back out of a claim collision with BENCH
64ffdc02 ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1: rebuild apply_assignment_verdicts.py for the 19e03876 schema
07f68e73 DROID_SIBLING_RELATION_GEN_CRASH_1: root cause found, mod-wide scope confirmed (all 52 races)
4a68c65f Ledger sync: claim/start MAPGEN_ROUND3_VERDICT_LANDING_1 close + 3 fresh FOUNDRY items
805d5983 Absorb round-3 mapgen verdict into MACRO_GENERATOR_V0_1, flag superseded plans
3075275f TILEGEN_SILENT_REUSE_1: third offline pass, found an untested premise gap, still inconclusive
718ed1f8 Fix ant sheet layout (figure/worker overlap)
0b896bad Transient: They! Giant Ants art contact sheet for the Fever Wood card
51a19559 Owner's round-3 mapgen grade landed: FAIL 0/8, painter held, GL sheet lead (via MAPGEN_ROUND3_VERDICT_LANDING_1; seat guard kept BENCH off FOUNDRY's item file)
206580c1 DROIDWORKS_PERSONALITY_VERIFY_1: live-verified, all 8 families pass; filed a sibling-relation-gen crash found along the way
ae6f10df Ledger sync: DROID_MODULE_BODYGROUP_WIRING_GAP_1 + DROIDWORKS_MODULE_PERSONALITY_1 closed, both live-verified
9a957bbb Ledger sync: three filings out of the sheet regen + backlog-audit review
19e03876 Biome assignment sheets rebuilt to the owner's 2026-09-09 rulings
449e9805 Droidworks: wire module BodyPartGroups onto vanilla Human's Waist part
58d7ae63 Code review status: mark 191 files clean (dirty-code-review wave, 2026-09-10)
3ea1ca20 Dirty-code-review wave: 9 real bugs found across 191 files, all verified
8df622a7 Live-tested DROIDWORKS_MODULE_PERSONALITY_1's wear/unequip mechanism: it fails
51783238 Ledger sync: 10 more doing-backlog reconciliations (batch-1 late report, verified)
c0018865 Ledger sync: STAT_NORMALIZATION_AUDIT_1 tree-resizing/Comigo scope note
e585ae24 STAT_NORMALIZATION_AUDIT_1: owner requests tree-resizing/Comigo mods in scope (not a ruling)
7dfa465e BIOME_ENRICHMENT_POISON_FOREST_1: record its real blocker as a causal link
5b98b3ed Doing-backlog audit: reconcile 25 items whose ledger state had drifted from their prose
3c5a1cc2 Revert ARTIST-as-seat: the Artist tile is the no-LLM artpipe daemon's console
c6a5f3f8 ARTIST becomes a real seat: Claude profile, identity file, interim standing orders
3aa26b6f Ledger sync: final codebase-health timestamp before reboot
ed1b8a8b FOUNDRY reboot handoff 202609100141: two save-compat regressions root-caused and scoped, campaign restored and playable, RimWorld's own silent ModsConfig-reset finally diagnosed
e714e7b0 Commit uncommitted work-tree content found ahead of reboot (provenance to verify)
c4f3510c Ledger sync: DROIDWORKS_PRIMITIVE_TIER_1 note (G2 art landed, stays doing)
69476f42 DROIDWORKS_PRIMITIVE_TIER_1: real G2 sprite art (goose-neck droid), placeholder retired
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : UP  → corrected to DOWN, measured now
- Bridge: FREE    since 2026-09-10T07:10:28Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M design/Jawa/worldbuilding/review/creature_art_register.html
 M design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json
 M infrastructure/state/codebase_health_last.json
?? defs.sqlite
?? design/Jawa/templates/road_warehouse.lua
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
```

Ownership: codebase_health* = FOUNDRY's health tool, theirs. decisions.json +
creature_art_register = the OWNER's live review via the sidecars (checkpointed
by BENCH; sidecars keep writing). defs.sqlite = shared derived db, never
commit. road_warehouse.lua = another window's, untouched. serve_*.log = the
two sheet sidecars, which are deliberately STILL RUNNING (ports 43775 fauna /
45389 flora) so the owner's morning tabs resume live — do not kill them.

