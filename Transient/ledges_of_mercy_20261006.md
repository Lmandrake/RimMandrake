# CRACKEDLANDS_LEDGES_OF_MERCY_1 — progress 2026-10-06

## Status
DONE offline, UNCOMMITTED (brief forbids commit). Live chains never run.

## Spec read
Item + GPT_ENRICHMENT §1 + MECHANICS_BUILD §6 read. Physical form of a ledge + inscription lines are OWNER's (item open Q1/Q2). Build form-agnostic: DefModExtension marks a refuge ledge / chime anchor; seek-refuge hook; flood skips refuge cells; chimes snap to anchors.

## Existing code
Probe: RM_MapComponent_CanyonFlood found in 7 Source files; ledge/refuge/anchor: only comments (CanyonFlood.cs:400 names this item). Hook points: MapComponentTick phases, Eligible(), ChimeCell().

## Shipped
- Source/RM_LedgeRefuge.cs (new, in csproj): RM_RefugeLedgeExtension + RM_ChimeAnchorExtension (DefModExtension markers, form-agnostic); RM_MapComponent_LedgeRefuge: refuge cells = standable cells of any thing carrying the extension + debug cells; Sweep() sends neutral humanlike visitors + player trained animals (any learned trainable) Goto(Sprint) nearest reachable refuge cell (prefers empty), holds those on it with Wait; PROVISIONAL consts 250/12/500.
- CanyonFlood: sweeps at Herald entry, Warned entry, every 250 ticks while not Dry; Eligible excludes refuge cells; ChimeCell snaps to nearest anchor; report adds refugeFlooded=.
- Settings: ledgeRefugeEnabled, chimeAnchorsEnabled (PROVISIONAL numbers in tooltip); maxOneColumn=true per cfdba9344.
- Debug actions: Report ledge refuge / Mark debug refuge ledge at map centre / Clear debug refuge ledges / Teach player animals Obedience.
- validation.py: chain ledge_refuge (trained_animal_runs_for_ledge, refuge_off_sends_nobody); UNMEASURED ledge_refuge_neutral_visitor, chime_anchors_used; static _ledge_refuge_findings (mutation-tested red). Walk lines added.

## Deferred
- Ledge ThingDef + GenStep placement (owner Q1: physical form). Chime-anchor ThingDef (same).
- Carvings, inscriptions (owner Q2 lore lines), one-shot memory ThoughtDef + trigger (numbers ours, but nothing to attach to until the carving's form exists).
- Swale campaign lock: not touched (blocked on ruling).
- required_checks.json regen (outside FloodedCanyon).

## Art owed
artpipe find ledge/mercy/chime/refuge/carving/offering + canyon-scoped sweep (probe veqma=1): no ledge, worn-figure, offering or chime-line art exists. ALL OWED; none generated.

## Validation
winbuild FloodedCanyon 0 warn/0 err; validation.py STATIC PASS; selftest_floodedcanyon_static 0 failures; modcheck lint 0 FAIL; validate_patch both Patches OK (unchanged).
