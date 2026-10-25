# FOUNDRY_HANDOFF_202610252223 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610241937`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, 2026-10-25): up to four subagents, full belt, offline, ends when he next writes. Tooling fixes pushed so BENCH benefits: 22 items fixed/closed across enact, deploy planner, art_eval/shadow, art_sheet, fauna_drive, artpipe cancel, art_guard delegated installs. (filed: ledger)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing for the owner beyond the still-open canon.yml repoint and TunnelSnake B / Vurra B asks in the 202610241937 handoff.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `ENACT_STALE_KEY_FIX_UNREVIEWED` — enact.py (2411 lines) needs a full-file review, its follow-ups are closed; NEXT: spawn one rm-builder to review it and mark-clean.
- `ART_EVAL_SIZEJUMP_TUNE_OVERBLOCK` — blocked, thresholds cannot separate; NEXT: work ARTEVAL_JUDGE_LIVE_HEAD_TO_HEAD.
- `ARTEVAL_STRICTNESS_TUNE_KEEPS_REDRAWN` — 15 false rejects remain; NEXT: run a live round 2 when the bridge is free.
- Older pointers in FOUNDRY_HANDOFF_202610241937 unchanged; NEXT: reread them.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Helpers' `rimflow close` ledger edits sit uncommitted until someone commits the shard; check `git status` for FOUNDRY.jsonl after each helper (filed: this handoff).

## Commits

```
5ac449033e ledger: enact stale-key items closed/dropped; prose moved
92dc88fc01 enact: RSW_/RM_ swap is no alias when the census lists the other as its own row; undrawn-lane regression test (ENACT_ALIAS_FIX_SWAP_SEPARATE_DEF, ENACT_UNDRAWN_LANE_FIX_ORPHAN_INSTALL)
21dfe92359 ledger: owner cards on ice yield, ice melt, raider dig speed
68310906b6 ledger: close ARTEVAL_STRICTNESS_TUNE_KEEPS_REDRAWN, block ART_EVAL_SIZEJUMP_TUNE_OVERBLOCK
6e03a6d8b6 art_sheet: newest artpipe job wins a family/facing; --recommend persists in the census; sibling_keeps case-insensitive (ART_SHEET_FIX_NEWEST_JOB_WINS, ART_SHEET_HARDEN_RECOMMEND_ON_REFRESH)
d285057a7e ledger: close the six enact items
d0d945d10f ledger: note WORK_PRIORITY_FIX sha
60f4dc2b2b ledger: note WORK_PRIORITY_FIX
736a9cd094 artpipe: cancel_jobs.py takes pending jobs out of the queue, spares running ones (ART_SERIES_WIRE_STOP_AND_CANCEL)
9f3704cf78 enact: an older same-row keep from another decisions file releases his X like an older alias keep (ENACT_PURGE_FIX_ALIAS_ASYMMETRY)
b889d6b9c3 work priority: runners force manual priorities on and assert the bar read-back (UNMEASURED if it did not take)
324dc5230f art_guard: a delegated install (--why 'delegated: art <verdict file>') passes when the file exists and no kept picture is displaced (ART_GUARD_FIX_REFUSES_THE_DELEGATE)
e804493765 enact: date his pick by decidedAt / slot at, not the row's last touch (ENACT_KEEP_AGE_FIX_DECIDED_AT)
f3de01f533 scale_panel: runtime_size reduces a 3-axis drawOffset to (x,z) and refuses other lengths (SCALE_PANEL_FIX_THREE_AXIS_OFFSET)
dd046ccce4 enact: named refusal for a missing or empty snapshot (ENACT_MISSING_SNAPSHOT_HARDEN_NAMED_REFUSAL)
7c29f6d343 ledger: close 5 art_eval items; move SHADOW_SHEET_WIDEN_REPLACED_KEPT_ART prose
ca0010afc2 jawa/review_sign: description and def-missing Fail name RM_StationSign as well as Novel (REVIEW_SIGN_FIX_DOC_NAMES_NOVEL)
3510cd8c44 enact: ticked variants get the picks' clicked-sheet lane guard (ENACT_VARIANT_TICK_FIX_MOVED_LANE)
89ed48b095 art_eval shadow.build: show the owner-kept art a redraw replaced beside the row as a reference (SHADOW_SHEET_WIDEN_REPLACED_KEPT_ART)
ca98473873 rimflow lane: a bad flowworks_lane.json (bad JSON, non-object, bad regex) raises LaneFileError naming the file (RIMFLOW_LANE_HARDEN_BAD_JSON)
... 177 more: git log --oneline bea502c83c..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/fw_scenes/live/S1_20261017T084726.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S1_p00.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S1_p03.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S1_p10.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S1_p14.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S2_p00.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S2_p10.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S2_p30.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S2_p60.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S3A_p20.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S3B_p06.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S3B_p16.png   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S3_20261017T084854.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
?? Transient/fw_scenes/live/S3_20261017T084938.txt   (FOUNDRY/BENCH FlowWorks scene captures, untracked Transient, not mine to commit)
... 117 more uncommitted paths (by top-level dir: Transient 113, conversations 3, infrastructure 1): git status --short
```

