# BENCH_REBOOT_HANDOFF_202610051409 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610042206`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The art pipeline now has ONE lookup (`src/RimMandrake/Utils/art/subject.py` + `gametex.py`) and a canon check on every render (`artpipe/canon_check.py`); sheets are letter-stable across rebuilds (`c8954c1c7`). Before trusting any art/canon absence or rebuilding an owner-touched sheet, use those — the old per-tool name guessing produced every false "NO ART"/"no canon" the owner complained about. The art daemon `rm-artpiped` now runs from the BENCH clone with 5 workers via drop-ins in `~/.config/systemd/user/rm-artpiped.service.d/` (bench-workdir.conf, workers5.conf) — it loads code only at start, so restart it after any artpipe change.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- All 27 biome sheets are built and served; index with exact URLs: `Transient/biome_ffar/SHEETS_INDEX_2026-10-05.md`. Long Shade / Stillsand / Blue Desert are ready for a SECOND sitting (new renders added under new letters; his old picks unchanged).
- Calls made overnight for his veto (detail: `Transient/structural_rulings_progress_2026-10-05.md`, `Transient/structural_mechanics_progress_2026-10-05.md`, `Transient/structural_followups_progress_2026-10-05.md`): "our custom extreme desert" = RM_Stillsand; RSW_Khorrak kept (uncast) because it alone carries the steel-diet mechanic; Thraia rename is label-only (savegame planet uses JOE_Landopus); Great Devourer relabelled "sarlacc seeker"; Gloomcast now seeds maidenbloom, Long Shade forage gives dewfringe.
- RM_Ommok still also cast in RM_FloodedCanyon, RM_Vosska in RM_Abyss — he only said "move", evictions are on hold; ask.
- AA_Thunderbeast patch changes it EVERYWHERE it spawns (half size, new art, new description), not only Blue Desert.
- Qeshra: note asks for a tint, pick is the untinted A; tint candidate is set B.
- 24 renders sit in failed/ as failed_canon after one corrected retry — owner may want to see them (the gate false-failed his Thunderbeast pick once).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — 27 sheets served, 3 ruled once; NEXT: when he finishes a sheet, read its decisions JSON (notes as a group), stamp reviewStatus ruled, queue regens via fill_queue with canon + owner_note, file non-art rulings on an item.
- `ART_SUBJECT_RESOLVER_1` — phases 1–2 done (subject.py, gametex.py, sheet/census wired); NEXT: phase 3 — backfill old renders (byte matches, past picks, job-name conventions) and build the one binding review sheet for the rest.
- `ART_SUBJECT_RESOLVER_1` (daemon) — Thunderbeast v3 N/S can't render because derive_from points at a failed_canon job the owner accepted; NEXT: let derive_from accept a master the owner picked (art ledger ruling) regardless of its canon verdict, then requeue bluedesert_Thunderbeast_v3_{north,south}.
- `ART_SUBJECT_RESOLVER_1` (daemon placement) — rm-artpiped runs from the bench clone by drop-in because the foundry clone was dirty; NEXT: when foundry's clone is clean and pulled, delete bench-workdir.conf (keep or drop workers5.conf on the owner's word), daemon-reload, restart.
- `ART_VERSION_WRANGLING_1` — writers rewired + push guard live; NEXT: owner yes/no on also registering the PreToolUse texture hook in .claude/settings.json; MessyConduit's 77 unledgered PNGs will be refused at FOUNDRY's next push.
- `VOSSKA_SANDSWIM_GRAPHIC_WIRING_1` — art queued/rendered; NEXT: wire RM_Vosska's swimming graphic once its render is picked on the Stillsand sheet.
- `KHORRAK_STEEL_DIET_TIER_1` — NEXT: ask the owner whether RM_Khorrak gets the steel diet or it is dropped.
- `SARLACC_SEEKER_ROOTING_1` — design filed; NEXT: build the feed-then-find-water rooting on CompSarlaccSwimmer.
- `GIT_WORKFLOW_MIGRATION_1` — NEXT: on 2026-10-05 measure manual rebases/day and D:\ writes over 3 days, record in plan §4, close it.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- rm-artpiped runs stale code until restarted, and from whatever clone its WorkingDirectory names (filed: lessons)
- per-facing prompts containing "three facings" die as bad_job_file at render time; fill_queue now refuses them at filing (filed: lessons)
- art_sheet canon lookup was exact-name only; library absence is never a canon verdict (filed: lessons)
- rebuilding an owner-touched sheet re-lettered its sets until c8954c1c7 — verify letters against the ruled snapshotId before showing him a rebuilt sheet (see: src/RimMandrake/Utils/art/selftest_sheet_letters.py)
- requeuing a derived facing while its master's failed record exists fails it instantly as master_failed — requeue masters first and wait (see: this handoff)
- serve_sheet cookies are per-host not per-port; fixed by keying the cookie on the port (see: review-sheets e678a9e)
- question-card/sheet notes are not visible to block_forged_owner_said — cite the decisions file, never --owner-said a sheet note (see: this handoff)

## Closed since the last handoff (1)

- `LONGSHADE_SHEET_STRUCTURAL_RULINGS_1` — 68f708add09f3bb857d0562bd6055b0726c98413

## Filed and still open (4) — the next seat's queue

- `ART_SUBJECT_RESOLVER_1` — One shared art/canon resolver (subject.py) for every sheet, census and tool; jobs bind their target; backfill 2,860 old renders
- `SARLACC_SEEKER_ROOTING_1` — Sarlacc seeker (RSW_GreatDevourer) quests for food then water, then roots: wire CompSarlaccSwimmer + kill top-up + threshold
- `VOSSKA_SANDSWIM_GRAPHIC_WIRING_1` — Wire RM_Vosska's sand-swim graphic (swimmingGraphicData + RM_SandBuriedGraphicExtension, thraia precedent) once art job stillsand_RM_Vosska_sandswim_v
- `KHORRAK_STEEL_DIET_TIER_1` — RSW_Khorrak kept uncast as sole carrier of C# CompMetalEater after the Khorrak RM tier move: port the steel diet to RM_Khorrak or rule it dropped and 

## Commits

```
c8954c1c7 art_sheet: column letters append-only and stable against the RULED snapshot; ingest compares used letters only
a6db5089a GimmeSomeSlack: reel gets a free 'Choose style' gizmo (restyle in place; the hose follows the reel's look)
2427f3f98 GimmeSomeSlack: joiner halves mesh shoulder-to-shoulder (JoinerMesh 0.33) so the brass reads screwed together, not two couplings with a gap
f606e9129 GimmeSomeSlack proof: P1 reel-couples-to-tank is a declared SKIP when FlowWorks is not on the tier (RECORD is not an OK row, so modcheck recorded RED)
6772566b4 fill_queue: run common.load_job on each job before filing; bad facing prompts refused at filing
0cde4721c lesson: facing-set words in prompts kill per-facing jobs
0d65607fc FOUNDRY handoff 2026-10-05: Gimme Some Slack style-per-build + carried hose + dense proof; four items closed
2a5bb1292 GimmeSomeSlack proof_all live green 143 PASS + 1 RECORD (maze P1, FlowWorks not on tier); modcheck record RED on that row; report
bd68c1545 proof_all P3: colonists parked on the first standable cell near PARK (a fixed cell was unstandable on run 3's map)
478c731d6 GimmeSomeSlack B8: far-zoom LOD read at the camera's own maximum root (58 is Middle with the tier camera mod)
52e23f99d GimmeSomeSlack DLL built from 98399bd4e
98399bd4e GimmeSomeSlack: ConduitRuns map component kept out of saves (proof_all SL2 found it), floor-rule trim shared by SelfTest and probe, B8 waits for the zoom
f5cf241cc GimmeSomeSlack densification: proof_all.py one-session live proof, reduced 39-scene matrix, 33 human stations, walk M10-M13, stale offline checks fixed
a96c5ea83 GIMMESOMESLACK_RENAME_1 closed: rename report and ledger close
56408aefb Gimme Some Slack rename: mockup art/oracle scripts still wrote to the old MessyConduit folder (tuple-form paths); fixed, stray old oracle_scenes.json removed
1ad39d739 GimmeSomeSlack verification densification analysis: 259 -> 143 live rows, 15 -> 1 live runs, 47 -> 33 human stations
37a7f8dbb Rename MessyConduit to Gimme Some Slack (mandrake.rm.gimmesomeslack, RimMandrake.GimmeSomeSlack)
46d2475a0 Hose carry S4: DLL built from 234620b32, report and live screenshot proofs (carry follows the walk, drop, wind-in clip, cut-hose ghost retract)
234620b32 Hose carry S4: live drawing (carried hose follows the walked trail to the hand, retract clip, animated cut-hose retract, LOD), endKind in the census (CR5c), HoseEnds/HoseEvents, free-end port find, deployed reel art while carrying
dc17f699a validation_hose CR7: gizmo labels are 'DEV: lay hose instantly' / 'DEV: reel in instantly' (lowercase): match case-insensitively
... 215 more: git log --oneline f6809b497..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-05T08:45:20Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? conversations/   session transcript exports written by a hook; deliberately untracked, not BENCH work
```

