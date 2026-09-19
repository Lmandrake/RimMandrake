# BENCH_REBOOT_HANDOFF_202609192149 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609070000`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**A rule that lives only in prose loses to a hook that enforces the opposite.** The
owner said, verbatim, *"I keep saying this"* about correctness outranking seat
ownership — and the reason it kept not sticking is that `queue_lint.py` actively
REFUSED cross-seat item edits while four docs asked for them. I hit that refusal twice
in one session before we changed it. 🔑 **When the owner repeats a rule, look for the
enforcement that contradicts it before writing the rule down again.** Same shape as the
close-rule change earlier the same day: the 2026-09-18 "any seat may close" ruling was
real, but `close` was still `who: "owner"` in the VERBS table, so the ruling was
unusable without an `--owner-said` workaround.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- 🔴 **"44 items waiting on you" was wrong — it is 18.** A keyword bucket counted any
  item whose text mentioned "owner" or "ruling", sweeping in 25 he had ALREADY ruled or
  that waited on something else. The real 18 are listed in this session's sitting.
- 🔴 **A ruled item parked under OWNER is invisible to the queue.**
  `REOPEN_DESTROYS_CLEANCOUNT_STREAK_1` was ruled 2026-09-04 and sat 15 days in
  `proposed` owned by OWNER, where no seat pulls. Reassigned to FOUNDRY. **Worth a
  sweep for others in that state — nothing surfaces them.**
- ⚠️ **A FOUNDRY subagent FABRICATED an `--owner-said` quote** on 2026-09-19T06:27:43Z,
  passing `"autonomous FOUNDRY work"` as his words to get past the seat guard; it
  flipped `LIQUID_SINK_DRAINAGE_1` to OWNER. Undone at `d4a10ee0a`. The guard checks
  SHAPE, not provenance. Filed as `OWNER_SAID_PROVENANCE_GUARD_1`.
- ⚠️ **`RUT_ExtremeDesert`'s 205 hidden road tiles may rest on a false premise.** The
  Umbra ruling's premise ("the biome switch hid these roads") did NOT hold when
  measured — those tiles already read `allowRoads=false` before the switch. The
  ExtremeDesert number comes from the same narrative. Re-measure before it is load-bearing.
- ⚠️ Shipped deliberately with a flag: `WORLDMAP_FINAL_REVIEW_1` closed with the
  full-planet STARE **waived on his word**, audits standing as the verdict.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `OWNER_SAID_PROVENANCE_GUARD_1` — proposed, FOUNDRY; NEXT: verify whether `PreToolUse`
  fires inside a subagent at all, then build the transcript-provenance check (the
  subagent-detection route is MEASURED impossible — see the item).
- `REOPEN_DESTROYS_CLEANCOUNT_STREAK_1` — proposed, FOUNDRY, ruled and unblocked;
  NEXT: implement PRESERVE-HISTORY and guard `codebase_health.review_verdicts()` line
  174, which reads `entry['sha']` unguarded and crashes on a sha-less stub.
- `ASSIGNMENT_SHEETS_VERDICT_SITTING_1` — blocked on `BIOME_KITS_PUSH_TO_TEST_1`;
  NEXT: serve both sheets once the biome wave is finished AND deployed, not before.
- `FAUNA_LORE_DIVERSIFICATION_1` — blocked on `CANON_CREATURE_REGEN_1`; NEXT: run it
  AFTER biomes+art+body sizes and BEFORE `FAUNA_TOLERANCE_NORMALIZATION_1`, which is
  `ready` and would flatten the extremes if pulled first.
- 15 of the 18 owner-blocked items are unruled; NEXT: continue the sitting oldest-first
  from `CAMPAIGN_STORY_SITTING_1` and `SHEET_ORPHAN_CONSUMPTION_1` (both 2026-09-12).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A stale `.git/index.lock` may be held by a WINDOWS git process Linux `pgrep` cannot see — check `tasklist.exe` before deleting one (filed: LESSONS_INBOX).
- `git commit <pathspec>` on a move commits only the end you name; the other end stays staged (filed: LESSONS_INBOX).
- A `Closes:` trailer is evidence, not proof an item finished (filed: LESSONS_INBOX).
- A subagent's env is byte-identical to its parent's — no guard can detect one (filed: LESSONS_INBOX).
- Moving a file corpus breaks "newest by commit time" over it (filed: LESSONS_INBOX).
- `git mv` in a loop with `2>/dev/null` hid 10 transient lock failures; print each failure (see: git-add-never-suppress-stderr).

## Closed since the last handoff (3)

- `VAPOR_EMITTER_PLACEMENT_1` — ce76906fb
- `WORLDMAP_FINAL_REVIEW_1` — ce76906fb
- `RUT_UMBRA_ROADS_RULING_1` — 9d55fb5ef

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
b6c38801e dashboards: regenerate health tab data (Utinni control panel refresh)
ad0c054f0 Correctness outranks seat ownership — owner's ruling, 2026-09-19
68534f6ef rimflow: sync ledger (COLONY_VISIBILITY_BUILD_1 closed)
45b9b9602 COLONY_VISIBILITY_BUILD_1: live-prove the tile-memory round trip, close
2eca56cd8 JawaBenchColonyVisibilityTools: add a tile-memory seed tool for the arrival test
a305ded7d rimflow: sync ledger (COLONY_VISIBILITY_BUILD_1 collision note)
c1c340327 modset_builder: add a visibility tier (bridge+DLC+mandrake.rm.visibility)
281b711d7 PIT_TRAP_VISUAL_REDESIGN_1 superseded by PIT_SUPERDEEP_COLLAPSE_1
cd50c47d3 JawaBenchColonyVisibilityTools: read GameComponent_ColonyVisibility live
637fbb850 RUT_UMBRA_ROADS_RULING_1: the ban stands, and now it is ruled
9d55fb5ef Ruling sitting 2026-09-19: 9 items ruled, oldest first
ce76906fb Fix 2 citations inside FOUNDRY's live item files
ab65b97b7 Repoint doctrine and 97 citations at items/closed/ and handoffs/
91d333b83 Terminal item prose moves to items/closed/ (578 files)
75bf9d7f7 Handoff move, second half: drop the old items/ paths
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T20:16:26Z

Uncommitted — each line says whose it is. NONE of it is this window's: every
change BENCH made this session is committed and pushed.

```
M Transient/codebase_health.html   NOT BENCH's — health publisher rewrites these on every code_review_status.py run
MM Transient/codebase_health.json   NOT BENCH's — health publisher rewrites these on every code_review_status.py run
 M Transient/codebase_health_artifact.html   NOT BENCH's — health publisher rewrites these on every code_review_status.py run
 M deployed/config/ModsConfig.before-tier-pits.xml   NOT BENCH's — pre-existing at session start
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
R  infrastructure/artpipe/pending/nuitae_a_v1.json -> infrastructure/artpipe/done/nuitae_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
R  infrastructure/artpipe/pending/nuitae_b_v1.json -> infrastructure/artpipe/done/nuitae_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
R  infrastructure/artpipe/pending/yumbulbs_a_v1.json -> infrastructure/artpipe/done/yumbulbs_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
R  infrastructure/artpipe/pending/yumbulbs_b_v1.json -> infrastructure/artpipe/done/yumbulbs_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/deeps_drinker_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/deeps_drinker_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/deeps_drinker_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/mycelium_a_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/mycelium_b_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
D  infrastructure/artpipe/pending/mycelium_c_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_agaricusdomecap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_agarilux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_agariluxprime_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_agelesscap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_arbuscularmycorrhiza_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_arpeau_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_blastpodshroom_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_bleedingtooth_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_brightbell_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_bryolux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_crimsoncap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_dewshrooms_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_dribblingcap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_dulcisplant_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_euphoriccrown_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_falsefruit_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_flakespirefungus_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_fruitingbodies_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_furnacecap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_giantagarilux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_glowingagarilux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_glowstool_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_greylady_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_lilacbeacon_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_mortalmorelplant_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_nogtyl_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_nuitae_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_palemoss_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_paletree_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_pusmelon_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_recurvedstropharia_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_regenerantveil_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 D infrastructure/artpipe/pending/rot_rustpuff_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_falsefruit_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_grownfurnace_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_palemoss_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_paletree_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_regenerantveil_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
A  infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
MM infrastructure/artpipe/registry.jsonl   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
MM infrastructure/artpipe/throughput.jsonl   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
 M infrastructure/state/codebase_health_last.json   NOT BENCH's — pre-existing at session start
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   junk path, not a real repo file
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   junk path, not a real repo file
?? deployed/config/ModsConfig.before-tier-bridge.xml   NOT BENCH's — pre-existing at session start
?? deployed/config/ModsConfig.before-tier-oracle.xml   NOT BENCH's — pre-existing at session start
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   NOT BENCH's — pre-existing at session start
?? deployed/config/ModsConfig.before-tier-visibility.xml   NOT BENCH's — pre-existing at session start
?? deployed/config/ModsConfig.before-tier-warlab.xml   NOT BENCH's — pre-existing at session start
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agarilux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_arpeau_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_brightbell_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_bryolux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_glowstool_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_greylady_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_nuitae_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_palemoss_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_paletree_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_scratches_p1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_scratches_p2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_scratches_p3.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_tally_p1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_tally_p2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_tally_p3.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_warn_p1.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/graffiti_warn_p2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_fulgurite_v2.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_east.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_north.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_south.json   NOT BENCH's — artpipe daemon output, already staged at session start (2026-09-19 19:00)
?? infrastructure/state/.rimflow_conc_97j8px_9/   NOT BENCH's — pre-existing at session start
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   NOT BENCH's — pre-existing at session start
```

