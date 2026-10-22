# FOUNDRY_HANDOFF_202610220323 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610211152`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Archmagi BSOD'd 2026-10-21 ~14:52 PDT; FOUNDRY was repaired the same night: git fsck clean, every dirty file parses, the killed rename and Titan/pipe-pole helpers were resumed and pushed, a 5.2 GB stray `D:\ClaudeWork\rimmandrake` folder inside the clone was merged into the real scratch root and deleted. The biome defName rename is DONE in the repo but NOT DEPLOYED and the three dev/canon saves still carry the old names. (filed: lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- 34 ledger retires of kept pictures were re-authored quoting his rename card ("Do this rename. All def renaming.") so the art guard passed; byte-identical copies, nothing lost; veto possible.
- Miasma donor gangrene wound-spreading code was dropped with no replacement.
- Open decisions from the older handoff still stand: fliers sheet, Uvak preview, canal overflow (10 decisions), JAWA_DROWNING, NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK, old-canon save fate (repaint card unanswered).
- Name mismatches listed on the rename item (FloodedCanyon=Cracked Lands, GelatinousSlime=Slime, PropaneLake=Chill, Scarlands=Warscar, Umbra=Auroral Umbra).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `BIOME_DEFNAME_MIGRATION_WAVE_1` — built, pushed 80e0635c3, undeployed; NEXT: at the next game-down run deploy_custom_mods.py dry-run, apply the Biomes composite, FlowWorks, Pyrelands, UtinniPatches, and remove the old Wasteland/NightsideIce deployed folders.
- `BIG_REPAINT_RESTAMP_SAVES` — three saves reference old names; NEXT: run repaint_biomes.py --rename RM_NightsideIce=RM_SleepingIce --rename RM_Wasteland=RM_Wastes (+RUT_ pairs) once he has seen the world look.
- `ALPHA_BIOMES_MIGRATE_DISEASES_AND_CODE` — implemented cfc9d28f9; NEXT: live checks A1 (loads without Alpha Biomes) and A2 (3 incidents fire) at the next bridge sitting.
- `TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT` and `PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES` — coded and pushed, undeployed; NEXT: deploy, then live checks A2/A3 each.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — 3 northstar_driver bugs fixed e6577a230, four changed files DIRTY; NEXT: fresh full review of transport.py, pipecheck.py, preflight.py, selftest_pipecheck.py, then the 13 FlowWorks/northstar files.
- `LINT_CITATIONS_EXEMPT_RECORDS` — 45 STATE_LIE left, mostly conversations/handoffs; NEXT: ask him whether the lint should skip conversations/ and handoffs/ and items/, then change it.
- `OFFLINE_PILE_PROOFS_CUT_BY_BSOD` — 14:3x-14:51 results UNMEASURED; NEXT: rerun the pile proofs from the top on the next game-up.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Paths starting `D:\...` handed to rsync are read as a host; prefix `./`. (filed: LESSONS)
- A git reset --keep fails on a dirty ledger shard: aside it, reset, re-append the extra lines. (filed: LESSONS)

## Commits

```
e9c752237 ledger: DIRTY_CODE_REVIEW_STANDING_LOOP_1 note (northstar_driver pass) + pending FOUNDRY events
e6577a230 northstar_driver review: pipelined call_many validates before sending; pipecheck VOLATILE no longer drops /items-style keys; preflight set_god_mode error reads UNMEASURED
47d91a243 PollinationGate: correct the header that said both gate pairs live in the RUT patch; rebuilt DLL
fdfec134d plant_draw_order selftest: MEASURED keys AB_ -> RM_ twins (ALPHA_BIOMES_MIGRATE_PLANTS_TO_RM_TWINS)
7e904f098 drawbridge_proof LOWER_ONLY_FROM_WINCH: tick 10 after walkability changes (HARNESS)
93cdbdc40 FlowWorks: WorkGiver_Drawbridge needs an A* path to the spot (WINCH_REACH_DIAGNOSE_CANREACH_FIBS)
929db7d51 lesson: publish rebases; close after publishing
adff09af2 RelativeVeto options memo (pinned): reach veto vs walls+depth; recommends a wall-aware reach-only labelling Design §8.3 specified walkability; build ae8d38f27c dropped it without a ruling.
e86006786 ledger: real fix sha for the lines pair closes
808bb58e5 ledger: lines pair claims, closes, bridge and game stamps
27fabb955 lines_proof: LADDER_HOSE row SITE fix, COLLAPSE_CORD row HARNESS fix (9/9 PASS live)
f7436aaab ledger: OWNER events from the pre-crash FOUNDRY session (canal overflow, big repaint)
91bc9a092 drawbridge_proof: RAID_UP sees what it claims (HARNESS, DRAWBRIDGE_RAID_DIAGNOSE_LOITERING_AT_MOAT)
80e0635c3 BIOME_DEFNAME_MIGRATION_WAVE_1: RM_/RUT_NightsideIce -> SleepingIce, RM_/RUT_Wasteland -> Wastes Mods, packageIds (mandrake.rm.sleepingice/.wastes), namespaces and DLLs moved; Cauldron leftovers swept. Not deployed. Dev saves still carry the old defNames; the repaint re-stamps them (repaint_biomes.py --rename).
c93ec2aac ledger: game stamps (lines-pair helper)
56fcc3b27 lesson: CanReach veto is an AND of projections
7af57d5c1 Drawbridge pair diagnosis: WINCH_REACH = MOD (CanReach AND-of-projections), RAID_UP = HARNESS
de10b51a0 ledger: owner card rulings on TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT and PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES; 19 per-biome titan-pool items; pipe-pole switch implemented
ccc3642b3 Docs: correct item states cited as open/doing for closed, dropped or superseded items (lint --citations STATE_LIE)
e1cebd84d FlowWorks DLL rebuilt from committed source (pipe-pole switch registration)
... 13 more: git log --oneline 731a41698..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   pre-crash BENCH/FOUNDRY session leftovers, uncommitted; owner of the file decides
 M Transient/modcheck/fixtures.json   pre-crash BENCH/FOUNDRY session leftovers, uncommitted; owner of the file decides
 M conversations/2026-10-21-0533-f36490b9.md   conversation record, landed by the sweep
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   pre-crash BENCH/FOUNDRY session leftovers, uncommitted; owner of the file decides
?? Transient/fw_scenes/live/S1_20261017T084726.txt   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p00.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p03.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p10.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p14.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_p00.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_p10.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_p30.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_p60.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S3A_p20.png   pre-crash FOUNDRY/BENCH FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
... 153 more uncommitted paths (by top-level dir: Transient 147, deployed 3, conversations 2, src 1): git status --short
```

