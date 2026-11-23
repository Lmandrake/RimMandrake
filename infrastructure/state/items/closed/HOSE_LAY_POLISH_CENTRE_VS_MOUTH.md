# HOSE_LAY_POLISH_CENTRE_VS_MOUTH

FlowWorks: hose lay edge cases (centre vs mouth range, refused feeder, bend radius)

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C7a-F2** PLAUSIBLE LOW — A refused (non-conducting) laid feeder still counts as feeding its receiver, changing the receiver's lay geometry. Hose/RM_MapComponent_Hoses.cs relay index adds every laid reel's far cell; IsFed(r) then suppresses r's outward lead-out. Live: obstruct A so its lay is null, rebuild B, compare B's geometry with A removed.
- **C8a-F4** CONFIRMED LOW — Install pre-check measures from the reel centre, routing from the mouth: a just-in-range western target is refused 'too far'. Hose/HoseMath.cs:1057 V2.Dist(reel.Centre, target.Centre) vs RoutePulled starting at reel.Mouth.
- **C8a-F5** PLAUSIBLE LOW — Polygonal fallback can accept a lay tighter than the minimum bend radius. HoseMath.LayOnce restores planPoints when the rounded pose clips; MinBend* is measured, never enforced. Visual; offline SelfTest over a tight corridor.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
