# TANK_CONTENTS_SALVAGE_ON_DECONSTRUCT

FlowWorks: deconstructing a stocked tank / converter / drill silently deletes contents

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F1** CONFIRMED MEDIUM — Converter pending products / adapter carry lost on deconstruct. CompLiquidConverter has no PostDestroy/PostDeSpawn; pendingCount scribed but never settled on destroy (CompLiquidConverter.cs:79,347). Carry loss is sub-unit.
- **C2-F5** CONFIRMED MEDIUM — Deconstructing/destroying a stocked tank silently deletes its contents (drill pending too). Building_LiquidTank has no Destroy/DeSpawn override (only GetGizmos/GetInspectString/ExposeData); no patch elsewhere. Hoses spill on despawn (CompHoseReel.PostDeSpawn); tanks do not.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
