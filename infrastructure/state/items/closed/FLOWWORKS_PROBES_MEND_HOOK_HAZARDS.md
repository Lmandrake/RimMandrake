# FLOWWORKS_PROBES_MEND_HOOK_HAZARDS

FlowWorks proof hooks: map-switch mailbox, destructive filltank, overflow guard, census tex

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C8b-F1** CONFIRMED LOW — HARNESS: HoseProbe's static mailbox runs a queued command on whichever map is current when serviced. Hose/HoseProbe.cs:36 checks Find.CurrentMap == map at service time; the request carries no map.
- **C8b-F2** PLAUSIBLE LOW — HARNESS: RM_LiquidLookProof.Show assigns a new surfaceLook to a lookless fluid/liquid def just by reading it. RM_LiquidLooks.cs Find() writes f.surfaceLook / l.surfaceLook. Live: read surfaceLook ref before/after Show on a lookless fluid.
- **C8b-F3** CONFIRMED LOW — HARNESS: filltank / ProofTank empty the tank before the refill can be refused (stock lost on a bad request). Hose/HoseNetProbe.cs:57 TryRemoveLiquid(all) before TryAddLiquid; RM_NorthstarProofs.cs:79-83 same order. Proof surfaces only.
- **C8b-F4** PLAUSIBLE LOW — HARNESS: tuning an inherited look rebuilds only the named member's terrains. RM_LiquidLookProof.Tune -> FluidMembers(f) only. Live: tune a canal fluid that inherits its liquid's look; compare pond material.
- **C8b-F5** PLAUSIBLE LOW — HARNESS: individual look tuning bypasses the official-terrain protection Members() applies. RM_LiquidLooks.Members filters Owned(); Tune calls Apply directly. Offline def census for adopted vanilla terrains first.
- **C8b-F6** CONFIRMED LOW — HARNESS: ProofFluidRow's area guard overflows (65536x65536 -> 0) and accepts negatives. RM_PromotionProofs.cs:204 'w * h > 400' unchecked int.
- **C8b-F7** CONFIRMED LOW — HARNESS: census reelTex says stored art while carrying; the graphic draws deployed art. Hose/HoseProbe.cs:403 needs r.laid; Graphic_HoseReel.MatAt also accepts carry != Stored.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
