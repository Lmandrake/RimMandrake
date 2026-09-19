# FOUNDRY_REBOOT_HANDOFF_202609130316 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609122103`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The entire `src/` tree now has at least one recorded code-review entry (0 files
left in `code_review_status.py list --show-untracked`'s src/ pool) — a genuine
first-pass milestone this session finished via 12 parallel review waves. It
found 6 real bugs, one of them safety-relevant: `jawa/transporter_launch`'s
`dryRun` flag didn't gate the "existing transporter" branch, so a documented
dry-run call could trigger a real launch (fixed, `f69955e42`; a follow-up
audit of all 61 bridgetools files found no second instance). The loop is
still "standing" — new DIRTY content will accumulate again — but the backlog
that existed before this session is now cleared. Full bug list and commits in
"Commits" below and in `LESSONS_INBOX.md`.

## What the owner should see

- `RUT_UMBRA_ROADS_RULING_1` (filed, open): `BIOME_WORLD_SWITCH_WAVE_1`'s tile
  repaint made 34 tiles' roads invisible under `RUT_Umbra`'s `allowRoads=false`,
  with no sheet ruling behind that flag (unlike `RUT_ExtremeDesert`'s 205, which
  IS owner-ruled and quoted in the def). Nothing was deleted — a one-line def
  flip restores them if he says so.
- The biome world-switch itself (`f90d660ae`): 17,667 tiles repainted from 22
  donor/vanilla BiomeDefs onto owned `RUT_` defs, world_commit'd, canonical
  save backed up first (`BIOME_WORLD_SWITCH_WAVE_1_2026-09-12.rws`). Tile 17007
  now reads `RUT_ExtremeDesert` — his original "why does this still say
  GRiNDTerra" complaint is answered. He may want to look at the world map.
- The transporter `dryRun` bug (above) is fixed and deployed, but if he ran any
  manual "preview" tests against an existing transporter before this fix
  landed, those calls actually launched for real — worth knowing if a
  transporter's whereabouts don't match his expectation from an earlier session.
- `CORRECT_GIDDYUP_NULLKEY_1` (filed for BENCH, open): fix already applied and
  deployed for the dead `GR_Mantistanis` reference; just needs BENCH to
  claim/close its parent item `GIDDYUP_NULLKEY_CRASH_1`, which I couldn't
  close myself (it's filed under BENCH's lane, not FOUNDRY's).

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `BIOME_WORLD_SWITCH_WAVE_1` — tile switch itself is DONE and verified
  (17,667 tiles, fresh export confirms zero donor defs remain painted). Still
  owed, in order: (1) `RUT_UMBRA_ROADS_RULING_1`'s owner answer; (2) a scope
  call on `fall_line.json`'s bare donor-biome host names before the wildBiomes
  eviction patch can ship clean (its rename would need to happen alongside
  whatever HORRORS_RAIDING_FACTION_1/HORRORWASTES_BIOME_DISSOLVE_1 decide,
  since fall_line's registers are entangled with that — don't rename it blind);
  (3) worldmap biome icons for all 20 new RUT_ defs need a manual authoring
  pass (owner's icon-set call, no script exists — `WORLDMAP_BIOME_ICONS_REGEN_1`
  already said so in 2026-09-07, re-confirmed here); (4) a full-list cold load
  + per-batch quicktest (this item's third verify line) — deliberately NOT run
  solo this session per "batch game-up work before restarting"; do it alongside
  whatever else needs a restart next, not as its own trigger. (5) the links CSV
  was deliberately not rebased — a 152-edge pre-existing drift needs its own
  look, separate from this item. Next action: wait on (1), then decide (2).
- `FASCINATING_WORLD_JUNK_1` — Phases 1 (CENSUS) and 2 (IDEAS) are DONE and
  committed (`design/Jawa/worldbuilding/junk/junk_census_2026-09-13.md`).
  Phase 3 (ROSTER) explicitly needs the owner's own creative call per the
  item's spec ("Let's get creative!") — deliberately not attempted by any
  agent. Phase 4 (art/text authoring) is untouched, blocked on Phase 3. Next
  action: an owner sitting to pick the roster from Phase 2's mined ideas,
  then Phase 4 can be built.

## Traps learned

(All filed to `LESSONS_INBOX.md` too.)

- Two `artpiped.py -N 3` daemons were running concurrently at session start
  (one 31.5h old, one a 6.5h-old orphaned wrapper) — no lock stops a second
  daemon from starting, and both fought over the same default `w0/w1/w2`
  codex-worker slots, producing "no rollout file found" `worker_error`
  failures that look like a codex bug but are daemon-count contention. Killed
  the younger one by PID (never `pkill -f` — matches your own shell). Check
  `pgrep -af artpipe` for >1 PID before trusting a run of failures.
- Concurrent agents committing in this shared tree throw transient
  `.git/index.lock` errors regularly — always `ps aux | grep '[g]it'` before
  touching the lock; remove it only when NO real git process holds it, wait
  and retry otherwise. Happened repeatedly tonight, never caused a lost commit
  because every agent checked first.
- `code_review_status.py list --show-untracked` is the only view that shows
  the true never-reviewed pool; bare `list` silently omits it, and CLEAN-entry
  counts can exceed file counts (repeat `[x2]` marks) — don't judge remaining
  work from bare `list`.
- `biome_wildbiomes_evictions.py`'s `painted_defs()` treats `injection_layer`
  rosters (`fall_line.json`) the same as painted-biome rosters, so its bare
  donor-biome host names read as false eviction pairs after a repaint wave —
  this is a tool/scope mismatch, not staleness; don't rename `fall_line.json`
  to silence it without a scope ruling (see "half-done" above).

## Closed since the last handoff (5)

- `LIGHTFALL_CHASM_AUTHORING_1` — 89dbfd0a0f31e66d5cd8f8c1908e4c794354727a
- `ART_REGEN_WAVE10_QUEUE_1` — a4bb92cddd581261c409f40ef6e936fe6b11ff01
- `RIMDRIVE_LIBRARY_BUILD_1` — 5e7f3ced5c5e58e1e745d59a744c898769e7c836
- `MOD_VALIDATION_RUNNER_1` — bfd45d8b6d38915c3d09604c0699be2c2b88aaa2
- `MOD_VALIDATION_PIT_PILOT_1` — bfd45d8b6d38915c3d09604c0699be2c2b88aaa2

## Filed and still open (2) — the next seat's queue

- `RUT_UMBRA_ROADS_RULING_1` — RUT_Umbra forbids roads (allowRoads=false) with no sheet ruling behind it -- 34 tiles' roads went invisible in BIOME_WORLD_SWITCH_WAVE_1; RUT_ExtremeD
- `CORRECT_GIDDYUP_NULLKEY_1` — GIDDYUP_NULLKEY_CRASH_1's null key is GR_Mantistanis (dead ref), not the RSW_ Wave-C names; fix applied, needs claim+close

## Commits

```
6a9499a1b code-review: mark-clean 12 re-dirtied files (diff-scoped review)
bfa7c2f92 code-review: mark-clean 24 files (rimdrive/modcheck L1-L4a, RimUtinni FOUNDRY untracked wave)
d1c393c02 fix: modcheck runner truncation operator-precedence bug on finding names
bdf1b9a39 code-review: mark-clean remaining 20 RimStarWars files (Mlie Wave C defs, 16 SWBestiary animal ThingDefs_Races)
032461ff4 code-review: mark-clean 30 RimStarWars files (Settings/.cs, Sarlacc Defs+About, StructureInjectionsSW GenStep/TileMutator pairs)
c4858101e code-review: mark-clean 5 dev-tool Python files (Pits validation, art_zoom_sim, artpipe verdict sheet/apply)
aa2e63220 code-review: mark-clean GravshipLanding/LiquidTypes About.xml + LiquidTypes defs, biome dupe generator
bda42ac64 code-review: mark-clean 18 RimMandrake Mod Settings/GenStep/bridgetools files
f69955e42 fix: jawa/transporter_launch ignored dryRun for an existing transporterId
d85b7103f code-review: mark-clean 39 RimUtinni files (last-third batch)
18e1ab1b6 code-review: mark-clean 10 DivingInteraction/FloodedCanyon/FluidCanals files
d8a0b9b7d code-review: mark-clean 14 DivingInteraction/FloodedCanyon files
47ae589d5 fix: LiquidCorrosionMapComponent apparel-corrosion loop skipped items on removal
58720b3c2 code-review: mark-clean 5 Mod Settings files (WeatherSuite/RimProperty/Greentide/ProximityHatch)
311d90fc5 code-review: mark-clean 6 RustCathedralHum/Sarlacc gameplay files
e0f4ffdc7 fix: CompSarlaccSwimmer reserve refill was gated on prey survival, not kill
2f1e3946b code-review: mark-clean artpiped.py and selftest_artpipe.py
c8e2d629a BIOME_WORLD_SWITCH_WAVE_1: rename 19 stale roster defNames to RUT_; eviction still noisy
d24bf1961 BENCH reboot handoff 202609130215: carry-forward (two-fix Mantistanis op, one regen-fragile), four owner decision decks, traps filed
4843d58ae CAMPAIGN_ARC_GATHER: close the last two doubts (G77 tones confirmed GAP, G85 kyber clean) — doubt ledger fully resolved, Phase B unblocked
c5676331a CAMPAIGN_STORY_SITTING_1 Phase A: the arc GATHER (71 entries, 20/20 quote spot-check) + mod keep-or-cut analyses
3acb4e6ba code-review: mark-clean 4 files (game_focus, selftest_sound_paths, rimbench/core, artpipe/fill_queue)
6b81019d0 BIOME_WORLD_SWITCH_WAVE_1: wildBiomes eviction ran (no ship, stale rosters found); icon regen has no script
a183faa48 ledger sync: GIDDYUP_NULLKEY_CRASH_1 diagnosis+deploy, DUNGEON_SETPIECE_TEXT_1 redraft, CAMPAIGN_STORY_SITTING_1 Phase A launch
e50e62143 lesson: LoadFolders-gated defs defeat owning-mod MayRequire (GIDDYUP_NULLKEY_CRASH_1)
43cfd4427 DUNGEON_SETPIECE_TEXT_1: redraft the 18 narrator silent-god readouts into the butler register
5091a9bda selftests green 50/50: exempt vanilla packed clips in sound_paths; fund gemini explicitly in artpipe tests
3703a4f0c FASCINATING_WORLD_JUNK_1: Phase 2 (IDEAS) complete — donor shapes mined
76541ba62 code-review: mark-clean 5 files (ChewAnchors, FrontCreep, DiveHunt, ScatterMineshaftPortal, canon_consistency.py)
7f2ff5541 selftests: flip canon water case to DENY (planet frozen 2026-09-12); route liquid-suite dump path through game_paths
1f222320b GIDDYUP_NULLKEY_CRASH_1: guard GR_Mantistanis, the real live null-key source
f90d660ae BIOME_WORLD_SWITCH_WAVE_1: repaint 17,667 Ash'karr tiles onto the owned RUT_ biomes
90d58be79 GIDDYUP_NULLKEY_CRASH_1: gate VGE Megafauna hybrids on Spino.Megafauna in the biome cast
f46d1345d FASCINATING_WORLD_JUNK_1: Phase 1 CENSUS complete
a7dc3f029 mark-clean: modcheck cli/floor/report/status, rimdrive verify
534c8feba code review: fix case-sensitive exclusion in modcheck.mod_hash; catch a second Reconnected during rimdrive.verify's idempotent retry
d434f1e8f rimflow: close MOD_VALIDATION_RUNNER_1 + MOD_VALIDATION_PIT_PILOT_1; update RETROFIT_1's status
bfd45d8b6 MOD_VALIDATION_PIT_PILOT_1: live run GREEN (3/3) after enabling Pits and fixing five real bugs
d27b960be artpipe template: bake downscale-legibility direction into every sprite prompt; default+warn resolution to 256 (frostmite pilot, 2026-09-12)
270c52a14 Enable mandrake.rm.pits for MOD_VALIDATION_PIT_PILOT_1's live proof (owner: "Take control, change the list, and keep going!")
47ffd6b92 MOD_VALIDATION_PIT_PILOT_1: record that Pits isn't enabled in the live mod list
4a16b143d rimflow: close RIMDRIVE_LIBRARY_BUILD_1
5e7f3ced5 RIMDRIVE_LIBRARY_BUILD_1: fix Session._ticks() (measured live), run the full live chain
2c8a9d471 Resolution parameter proof: frostmite v2 at 512/256/128 source, downscaled to on-screen tiers
e3d2b573f Frostmite redraw pilot: v2 (blue keyline, amber core, bold claws, no red) passes zoom gate
9bb9fbf5d MOD_VALIDATION_RUNNER_1 + PIT_PILOT: build modcheck on rimdrive, draft the pit mod's validation.py
43f865899 art_zoom_sim.py: downscale legibility test vs vanilla control; 2026-09-12 frostmite/lockjaw sheets
10b6cddda RIMDRIVE_LIBRARY_BUILD_1: build rimdrive L1 (Session) + L2 (verify), extract rimbench.core onto it
d22a07bc5 rimflow: close ART_REGEN_WAVE10_QUEUE_1
a4bb92cdd ART_REGEN_WAVE10_QUEUE_1: queue 14 more art:improve creatures, wave 9's named remainder
a976ff6a3 Art review sheet 2026-09-12: 148 validated creature renders for owner grading (keep/redraw/cut)
882c6d92f rimdrive ruled (owner, 2026-09-12): new package, UNVERIFIED-taint for channel-less writes, RIMDRIVE_LIBRARY_BUILD_1 filed ahead of modcheck
99785cb6e GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1: file the missing prose, record live proof the fix is incomplete
89dbfd0a0 LIGHTFALL_CHASM_AUTHORING_1: rename the existing tile-9023 chasm landmark to Lightfall
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-13T01:31:34Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/art_review_2026-09-12/decisions.json
 M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 D infrastructure/artpipe/pending/dactillion_v1_east.json
 D infrastructure/artpipe/pending/dactillion_v1_north.json
 D infrastructure/artpipe/pending/dactillion_v1_south.json
 D infrastructure/artpipe/pending/fanback_v1_east.json
 D infrastructure/artpipe/pending/fanback_v1_north.json
 D infrastructure/artpipe/pending/fanback_v1_south.json
 D infrastructure/artpipe/pending/grank_v1_east.json
 D infrastructure/artpipe/pending/grank_v1_north.json
 D infrastructure/artpipe/pending/grank_v1_south.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_north.json
?? infrastructure/artpipe/done/ashrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_east.json
?? infrastructure/artpipe/done/bilespawn_v1_east.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_south.json
?? infrastructure/artpipe/done/bilespawn_v1_south.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/corronip_v1_east.json
?? infrastructure/artpipe/done/corronip_v1_east.manifest.json
?? infrastructure/artpipe/done/corronip_v1_north.json
?? infrastructure/artpipe/done/corronip_v1_north.manifest.json
?? infrastructure/artpipe/done/corronip_v1_south.json
?? infrastructure/artpipe/done/corronip_v1_south.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/direwail_v1_east.json
?? infrastructure/artpipe/done/direwail_v1_east.manifest.json
?? infrastructure/artpipe/done/direwail_v1_north.json
?? infrastructure/artpipe/done/direwail_v1_north.manifest.json
?? infrastructure/artpipe/done/direwail_v1_south.json
?? infrastructure/artpipe/done/direwail_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_east.json
?? infrastructure/artpipe/done/fumeback_v1_east.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_north.json
?? infrastructure/artpipe/done/fumeback_v1_north.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_south.json
?? infrastructure/artpipe/done/fumeback_v1_south.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_east.json
?? infrastructure/artpipe/done/gorewalker_v1_east.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_north.json
?? infrastructure/artpipe/done/gorewalker_v1_north.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_south.json
?? infrastructure/artpipe/done/gorewalker_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_east.json
?? infrastructure/artpipe/done/huskrunner_v1_east.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_north.json
?? infrastructure/artpipe/done/huskrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_south.json
?? infrastructure/artpipe/done/huskrunner_v1_south.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_east.json
?? infrastructure/artpipe/done/mireflit_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_north.json
?? infrastructure/artpipe/done/mireflit_v1_north.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_south.json
?? infrastructure/artpipe/done/mireflit_v1_south.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_east.json
?? infrastructure/artpipe/done/miremoth_v1_east.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_north.json
?? infrastructure/artpipe/done/miremoth_v1_north.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_south.json
?? infrastructure/artpipe/done/miremoth_v1_south.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_east.json
?? infrastructure/artpipe/done/oozemaw_v1_east.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_north.json
?? infrastructure/artpipe/done/oozemaw_v1_north.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_south.json
?? infrastructure/artpipe/done/oozemaw_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_east.json
?? infrastructure/artpipe/done/rotscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_north.json
?? infrastructure/artpipe/done/rotscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_east.json
?? infrastructure/artpipe/done/sporehulk_v1_east.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_north.json
?? infrastructure/artpipe/done/sporehulk_v1_north.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_south.json
?? infrastructure/artpipe/done/sporehulk_v1_south.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_east.json
?? infrastructure/artpipe/done/wastewing_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.manifest.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.manifest.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_north.json
?? infrastructure/artpipe/failed/wastewing_v1_north.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_south.json
?? infrastructure/artpipe/failed/wastewing_v1_south.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

