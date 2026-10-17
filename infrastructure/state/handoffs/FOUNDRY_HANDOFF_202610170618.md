# FOUNDRY_HANDOFF_202610170618 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610161835`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Every FlowWorks 'independent' check (Python oracle, fuzz generators) shares the kernel author's assumptions, so a green offline run is weak evidence: the shallow-rim, pump-mouth and canal-mouth bugs all passed 3000/3000 until a test ran at SHIPPED settings. Run `python3 src/RimMandrake/Utils/vv_shipped_matrix.py` (about 6 min) after any kernel change, and treat the live suites (validation_v2 61/0/0, river 20/0/1) as the real gate.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Water scenes: `design/RimMandrake/vv_methods/water_scenes_for_approval_2026-10-16.md` awaits his approve/change/strike on six scenes (about 10 min) and four NEEDS-A-RULING questions (S3.Q1 drill/tap pour, S4.Q1 water trapped under a re-shut gate, S5.Q1 four or five canal cells per pond square, S6.Q1 reload equivalence per pulse or at end).
- FlowWorks canal fixes (shallow rim, pump mouths, mouth top-up) are live-proved by one helper: trench full at tick 2002 vs 3753; screenshots in Transient/fw_water_live_20261016/ and fw_mouth_live_20261016/. He chose: agents run live checks and send pictures; first V&V piece only (not the 27-hour programme).
- Ratchet: FlowWorks calm 61/0/0 and river 20/0/1 live; settings window L1 pass. He said earlier FlowWorks was NOT signed off ('still need to resolve items'); he has not yet signed it.
- ExplosiveGrowth master-switch scope and Cauldron dry-thunderstorm weather need his ruling (skipped consult items).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `BIOME_SPRINT_ROUND3` (no item) — rounds 1-2 green only for Cauldron (73/0/0); LeaningScrub 77/0/8, Contagion 76/1/3, ExplosiveGrowth 54/0/5 all SITE/HARNESS-classified; harness fixes 2a86ba165, b38b7d496, d9bcd6357 not yet proven live; NEXT: take the bridge and run LeaningScrub, Contagion and ExplosiveGrowth suites on biomes_sprint, then `modcheck record` the full runs.
- `GPT_EDGE_CASE_ITEMS_25_OWE_LIVE` — 39 of 52 consult items fixed, 25 implemented owing live checks (converter, reactor, Cauldron 3, Contagion 6, LeaningScrub 10); NEXT: batch their live criteria into the next biome round and `rimflow verify` each.
- `V_AND_V_NEXT_PIECES` — pilot 1 done; NEXT: after he approves the water scenes, have a blind agent write properties from scenes.json (sealed sha 5244a13e) and a third agent classify failures; also file KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER work.
- `DONOR_SAVE_ICONS_RENAME_IKEE_STILL_SULKING` — 6 icon refs renamed in a save copy (D:\Luke\dev\_rmscratch\p6\...donorfree2.rws), ikee 7 rows held; NEXT: load the copy on the full list, then the ikee swap.
- `FLOWWORKS_CHANGELOG_AND_SIGNOFF` — CHANGELOG DLL hash line is stale again (DLL changed after c3dbac22); NEXT: refresh the hash line from the final DLL and ask him to sign FlowWorks off.
- The 9 older pointers (ART_QUEUE_DRAIN_AND_SHEETS, PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS, ALPHA_BIOMES_CENSUS_THE_REST_OF_IT, SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE, DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS, ZISSKA_FIRESPIT_PROVE_LIVE, ARTPIPED_BENCH_CLONE_PULL, DHOGGUR_STATUS_REPORT_SWOLLENART) were not touched this session; NEXT: wake them one by one from FOUNDRY_HANDOFF_202610161835.md.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A helper force-took the bridge from a stale-looking BENCH lock while BENCH's loadwalk.py was live; never `--force`, check bridge_calls.jsonl for foreign clients first. (filed: LESSONS)
- `modset_builder --restore` refuses once the bridge is released; restore ModsConfig before releasing, or copy the backup (owner list = 547 mods, md5 1f7122ea...). (filed: LESSONS)
- Stale bin/obj under D:\Luke\dev\_rmbuild gives old results after a put-the-old-code-back control run; clear them. (filed: lessons/)
- ledger lines stranded in the clone block ./publish; `ledger_sync.py --seat OWNER --seat-clone $PWD --apply`, then `git checkout --` the two shard files. (see: Utils/ledger_sync.py)

## Commits

```
13ba24c7d ledger: CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME verified L2 and closed
fedce072d CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME live: validation_v2 61/0, river 20/0/1, headline trench full at tick 2002 (was 3753)
846b07e97 ExplosiveGrowth: the ruled rewrite (explosive_growth_ruled_spec_2026-10-16 D1-D22)
7a146b287 ledger: CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME verdict, needs deploy
333b115cb FlowWorks kernel: the source tops up a water mouth that passed its unit on (CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME)
d893ad30c LeaningScrub: venomvine islands (15%), own capped downwind creep (22%), rooms, tree-tall, EG-exempt
fe4addc7d EnvironmentalHazards: contact venom gains minGrowth (young plants unarmed; default 0)
5c2c4d32d venomvine tall-canvas re-render job list (48 jobs, tallvv_*)
b5474f6a8 LeaningScrub venomvine: install existing artpipe renders over the shared placeholder via art ledger (owner Q4 card)
69e5544de FlowWorks ford stones: draw our RM_FordStones texture, not vanilla Flagstone (owner by card)
eb0c40d9f V&V pilot 1: shipped-flag matrix with uncapped rates, flag lint, single-off runs
e21a136de ledger: owner card rulings (VFE boost scope, VFE pump, dry crop rate)
ee8ead04e Designs: VFE boost removed only in our biomes, VFE head needs a pump; dry vanilla crops grow and age at x0.1 (owner by card)
a8c13cee2 ledger: FlowWorks pump and sluice L1 verified live
1dfad138d FlowWorks water fixes: live check green (validation_v2 61/0, headline pond+trench, pump D=1, sluice)
dd62e4689 V&V: six water scenes for owner approval, plus sealed scenes.json twin
e58367453 Ledger: rescue 8 stranded OWNER event(s) from the seat clone
5ff62b8e3 Ledger: rescue 2 stranded FOUNDRY event(s) from the seat clone
a29cc220b design: propagate 2026-10-16 owner card rulings into six design docs
6cf29701d lesson: --owner-said/--by-card events land in the OWNER shard; handoff line corrected
... 131 more: git log --oneline b0b1c8c65..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/abyss_sheet_2026-10-04.html   generated/other (sheet tooling or another seat; not mine)
 M Transient/biome_ffar/aiwha_wingfirst_sheet_2026-10-15.html   generated/other (sheet tooling or another seat; not mine)
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated/other (sheet tooling or another seat; not mine)
 M Transient/biome_ffar/scale_ground_measured.json   generated/other (sheet tooling or another seat; not mine)
 M Transient/mc_human_review/KEYSHEET.md   generated/other (sheet tooling or another seat; not mine)
 M Transient/mc_human_review/keysheet.html   generated/other (sheet tooling or another seat; not mine)
 M Transient/modcheck/fixtures.json   generated/other (sheet tooling or another seat; not mine)
 M Transient/phase0_p6_save_renames.md   generated/other (sheet tooling or another seat; not mine)
 M conversations/2026-10-16-0549-c453ca3a.md   generated/other (sheet tooling or another seat; not mine)
 M conversations/2026-10-16-1218-9a5985c9.md   generated/other (sheet tooling or another seat; not mine)
 M infrastructure/state/ledger/events/OWNER.jsonl   generated/other (sheet tooling or another seat; not mine)
?? Transient/ModsConfig.owner.547.bak   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/0052887ea95ee55cb4ce_full.png   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/012c446f56fabd4bd893_full.png   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   generated/other (sheet tooling or another seat; not mine)
?? Transient/biome_ffar/img/0172b49133d12ef1a9d8.webp   generated/other (sheet tooling or another seat; not mine)
... 1426 more uncommitted paths (by top-level dir: Transient 1417, deployed 5, src 2, (root) 1, infrastructure 1): git status --short
```

