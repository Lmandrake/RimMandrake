# HOSE_OFF_MEND_SLEEPWALKING_RETRACT

FlowWorks: hoses switched off still reroute/retract on obstacles

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C7a-F4** CONFIRMED MEDIUM — Hoses switched OFF still run obstacle rerouting, trail deletion and automatic retraction. MapComponentTick (Hose/RM_MapComponent_Hoses.cs ~430-470, r.Retract(why) at :468) has no RM_HoseSettings.enabled guard; only drawing exits (:520). Building over an invisible hose retracts it; design keeps ends through off/on.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
