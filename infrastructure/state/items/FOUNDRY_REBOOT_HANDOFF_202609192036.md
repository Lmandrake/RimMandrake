# FOUNDRY_REBOOT_HANDOFF_202609192036 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609191928`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The owner reset the codex art-gen quota this wave (~20:20Z) after it had blocked
several items (`ROT_ART_WAVE_1`, `FIREHAWK_FLIGHT_BEHAVIOR_1`'s flip-book, and
others filed by other seats) since 2026-09-19 09:38. `requeue_quota_failures.py`
was run once and moved 124 quota-failed jobs from `failed/` back to `pending/`;
the daemon (PID 605, `artpiped.py`) is actively working through the combined
backlog now (100+ jobs queued across several items sharing one lane) but it is
slow — over this wave it only reached ~10 jobs. **Do not assume a filed job has
failed again just because it is still sitting in `pending/`**; check
`infrastructure/artpipe/done/` and `failed/` for its specific id before
concluding anything, and re-run `requeue_quota_failures.py` if a NEW batch of
quota failures shows up (it only handles the specific "hit your usage limit"
sentence, and is safe to re-run any time — it no-ops on jobs that failed for a
real reason). Whoever finishes `ROT_ART_WAVE_1` and `FIREHAWK_FLIGHT_BEHAVIOR_1`
should check this queue first before filing anything new into it.

## What the owner should see

- A debug-fired quest, "Deep-Sand Contract" (`RUT_LongHungerContract`), is
  sitting live in the canonical campaign — I generated it via a debug action
  to prove the quest→incident wiring works (`LONGHUNGER_QUICKTEST_1`) and
  deliberately left it rather than force-decline it (it's an ordinary
  declinable quest with a normal expiry, same as anything the storyteller
  would generate). If he sees an unexplained "Deep-Sand Contract" offer, that's
  why — safe to ignore or decline.
- FireHawk currently flies with **no wing-flap animation at all** (plain
  static sprite while airborne) — the broken Spastic wing-render-tree from a
  prior pass was retired this wave (owner's own live test found it broken:
  no flap, misaligned wing), and the real flip-book replacement is blocked on
  the art queue above. Flight itself (`MaxFlightTime` etc.) is unaffected and
  correct. Not a regression to be alarmed by if he flies one and it looks
  plain — that's the deliberately-safer interim state, not a new bug.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ROT_ART_WAVE_1` — 1 of 22 landed clean (EuphoricCrown), 1 rejected on quality
  and requeued as `rut_agelesscap_v2` (v1 rendered as a flat gray sketch, no
  color), 19 still generating; NEXT: as each job in
  `Transient/rot_art_jobs_20260918.md`'s list completes, eyeball it against
  `rut_euphoriccrown_v1.png` for real color/shading (don't deploy on a clean
  manifest alone — validator/legibility are `skipped` for all of these, no
  automated QA runs on new-art jobs), give it its own folder+texPath off
  whatever shared placeholder it's currently on, validate, deploy.
- `FIREHAWK_FLIGHT_BEHAVIOR_1` — broken wing-render-tree retired and deployed;
  15 flip-book art jobs filed (5 frames x 3 facings) and requeued after the
  quota reset, still generating; NEXT: once all 15 land in `done/`, eyeball
  each for a genuinely different wing pose across the frame sequence (not a
  repeated/static image), place at
  `Textures/.../FireHawk/FireHawk_Flying_<N>_<direction>.png`, add the
  `flyingAnimation*` block to `RUT_FireHawk`'s PawnKindDef (exact XML already
  written in the item file, just needs re-pasting), then **live-verify** —
  step ticks to an actual takeoff, not a standing screenshot, since whether
  the engine degrades gracefully with fields-present-but-frames-missing was
  never actually confirmed and shouldn't need to be if all 15 land anyway.
- `LIQUID_SINK_DRAINAGE_1` — left `ready` (not formally claimed/started this
  wave, so not a hard requirement here, but worth flagging): the code is
  already built and twice offline-verified by earlier passes, the only real
  gap is a live proof that digging a channel into the map-edge band actually
  drains it. I checked and there is no cheap bridge-readable observable —
  `SinkTransferredTotal`/`fillGrid` are private `MapComponent` state with no
  `DebugAction` exposing them, so this needs either a colonist-dug canal from
  a source to the edge (real labor + wait) or an admin excavation shortcut
  plus figuring out how fill is rendered (no rendering code in
  `RM_MapComponent_Excavation.cs`, must live elsewhere) — genuine rig-building,
  not a quick check. NEXT: budget it as its own slot rather than a filler.

## Traps learned

- A file `git rm`'d and staged alongside others in a multi-path commit stays
  silently staged-uncommitted forever if it's left out of that commit's
  explicit pathspec — no error, no warning, just sits there through however
  many later commits until something notices (filed: LESSONS_INBOX).
- The donor Sandworm mod (`chezhou.creature.sandworm`) silently no-ops
  `T: Destroy` for a grace window right after spawn (`success: true`, nothing
  changes, the real signal is buried in `effects.logs`), and it self-relocates
  every stepped tick regardless of pause state (see:
  `skills/rimbridge/references/silent-failures.md`).
- `rimworld/jump_camera_to_cell` under the `jawa/` namespace silently no-ops
  (camera doesn't move, `success: true` anyway) — the real tool is
  `rimworld/jump_camera_to_cell`, already documented in
  `references/traps.md` line 80 but easy to mistype the namespace on (see:
  rimbridge skill).
- Graphic_Random's `texPath` in this codebase is the FOLDER, not a filename
  prefix — `validate_patch.py` gave a real ERROR (not a warning) pointing this
  out when I first got it wrong on `RUT_EuphoricCrown` (filed: none needed,
  the validator already catches it; just don't guess the convention, check a
  sibling def first).

## Closed since the last handoff (3)

- `EMBERSCYTHE_PYRELANDS_REHOME_1` — b88357f6ecf8ebe46358702a3fbbaffdb60efb09
- `PYRELANDS_FACING_REGRESSION_1` — ac578546e5552be2966f7e9af617bd3ccdddfa98
- `LONGHUNGER_QUICKTEST_1` — b680469950b6cf9db43148236230b4a8eee8cae6

## Filed and still open (1) — the next seat's queue

- `OWNER_SAID_PROVENANCE_GUARD_1` — --owner-said must be provable against the transcript: a fabricated quote rewrote an item's ownership under the owner's name

## Commits

```
fd93d3b25 rimflow: sync derived health dashboard
1ef2e1e3f LESSONS_INBOX: staged-but-uncommitted files from an incomplete pathspec
cc93574e0 FIREHAWK_FLIGHT_BEHAVIOR_1: actually commit the RenderTree deletion
bdd12c05f rimflow: sync ledger (ROT_ART_WAVE_1 claimed/started)
726608f79 ROT_ART_WAVE_1: land EuphoricCrown art, reject+requeue bad AgelessCap render
687860063 rimflow: note (LIQUID_SINK_DRAINAGE_1 -- live-proof needs a dig rig, deferred)
a62a12907 rimflow: sync ledger (LONGHUNGER_QUICKTEST_1 closed)
b68046995 LONGHUNGER_QUICKTEST_1: close all 7 criteria, live-verified
05d2dbcb4 OWNER_SAID_PROVENANCE_GUARD_1: file the fabricated-quote guard
d4a10ee0a rimflow: undo a fabricated --owner-said ownership flip
25341f171 rimflow: sync ledger — PYRELANDS_FIRE_RITE_TAKE_TUNING_1 closed
9dbb36e32 PYRELANDS_FIRE_RITE_TAKE_TUNING_1: the rite's take is a slider now
71c010f96 FIREHAWK_FLIGHT_BEHAVIOR_1: defer flyingAnimation* wiring, quota-blocked art jobs
cabf07592 rimflow: sync ledger (PYRELANDS_FACING_REGRESSION_1 closed)
ac578546e PYRELANDS_FACING_REGRESSION_1: live spawn-check Barbslinger/Flamefang, close
b1b82823c FIREHAWK_FLIGHT_BEHAVIOR_1: retire the broken Spastic wing-render tree
5a79d10e6 rimflow: sync ledger (EMBERSCYTHE_PYRELANDS_REHOME_1 closed)
b88357f6e EMBERSCYTHE_PYRELANDS_REHOME_1: move RUT_Emberscythe out of RotSporeKit into UtinniPatches
14dc4c533 rimflow: queue decay sweep — 5 of 200 open items ended
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    (confirmed at handoff time, 2026-09-19T~20:55Z)

Uncommitted (each line below states whose it is — yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   derived health dashboard, regenerated as a side effect of my own rimflow commands -- already committed (fd93d3b25), this line is stale
 M Transient/codebase_health.json   derived health dashboard, regenerated as a side effect of my own rimflow commands -- already committed (fd93d3b25), this line is stale
 M Transient/codebase_health_artifact.html   derived health dashboard, regenerated as a side effect of my own rimflow commands -- already committed (fd93d3b25), this line is stale
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/nuitae_a_v1.json -> infrastructure/artpipe/done/nuitae_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/nuitae_b_v1.json -> infrastructure/artpipe/done/nuitae_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/yumbulbs_a_v1.json -> infrastructure/artpipe/done/yumbulbs_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/yumbulbs_b_v1.json -> infrastructure/artpipe/done/yumbulbs_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaricusdomecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agariluxprime_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agelesscap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_arbuscularmycorrhiza_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_arpeau_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_blastpodshroom_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_bleedingtooth_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_brightbell_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_bryolux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_crimsoncap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dewshrooms_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dribblingcap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dulcisplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_euphoriccrown_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_falsefruit_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_flakespirefungus_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fruitingbodies_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_furnacecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_giantagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_glowingagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_glowstool_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_greylady_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_lilacbeacon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mortalmorelplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_nogtyl_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_nuitae_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_palemoss_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_paletree_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_pusmelon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_recurvedstropharia_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_regenerantveil_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_rustpuff_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_falsefruit_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_grownfurnace_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_palemoss_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_paletree_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
MM infrastructure/artpipe/registry.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
MM infrastructure/artpipe/throughput.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 M infrastructure/dashboards/hub/data/health.json   derived health dashboard, regenerated as a side effect of my own rimflow commands -- already committed (fd93d3b25), this line is stale
 M infrastructure/state/codebase_health_last.json   derived health dashboard, regenerated as a side effect of my own rimflow commands -- already committed (fd93d3b25), this line is stale
D  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_FireHawkRenderTree.xml   mine -- was staged-uncommitted since b1b82823c (see Traps learned); committed cc93574e0, this line is stale
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   stray debug artifact from an earlier bridge tool call, not mine, safe to delete
?? deployed/config/ModsConfig.before-tier-oracle.xml   pre-existing modset_builder.py auto-backup, not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   pre-existing modset_builder.py auto-backup, not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   pre-existing modset_builder.py auto-backup, not mine
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arpeau_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_brightbell_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bryolux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowstool_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_greylady_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nuitae_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_palemoss_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_paletree_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_scratches_p1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_scratches_p2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_scratches_p3.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_tally_p1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_tally_p2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_tally_p3.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_warn_p1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_warn_p2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_fulgurite_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_east.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_north.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_south.json   mine -- requeued from failed/ after the owner reset the codex quota this session; still generating behind ~100 other jobs
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency scratch dir, not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
```

