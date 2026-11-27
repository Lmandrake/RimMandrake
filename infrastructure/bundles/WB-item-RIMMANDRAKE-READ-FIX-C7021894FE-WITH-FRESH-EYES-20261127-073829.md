# WB-item-RIMMANDRAKE-READ-FIX-C7021894FE-WITH-FRESH-EYES-20261127-073829

State: DONE (one member, one group).

## Member RIMMANDRAKE_READ_FIX_C7021894FE_WITH_FRESH_EYES (fresh read of c7021894fe)
- Red: `fresh_reader.py holds c7021894fe ...` rc=1 (all three files DIRTY).
- StylePickMemory.cs, StylePickerCore.cs: no Problem found; marked READ-CLEAN at fe8d1680e2. The claim in the doc comment
  "vanilla builds each Architect button once" was checked against DesignationCategoryDef.ResolveDesignators (startup only).
- RM_SuspensionProofs.cs ProofUnsetLook: Problem (a promise could break and no test would go red): it read PASS when no
  part stored any look (bridge styles unregistered, or the god build dropping the look), a blind pass. Fixed test first at
  fe8d1680e2: own=M/N for the first bridge; the verdict reads FAIL under N/N and UNMEASURED HARNESS with no own= reading.
  The file is FLAGGED (no third read).
- Pipeline defect hit on the way: `fresh_reader.py holds` never held for a FLAGGED file (`check --record` reads DIRTY
  on a flagged file by design). Fixed test first at db08359a3e; two planted faults seen red.
- Readers filed: RIMMANDRAKE_READ_FIX_DB08359A3E_WITH_FRESH_EYES, RIMMANDRAKE_READ_FIX_FE8D1680E2_WITH_FRESH_EYES.
- Live: UNRUN (ArchBig and ArchSmall held by other BENCH runs, 2026-11-27 00:20 PST). Command: deploy FlowWorks
  (`deploy_custom_mods.py --mod FlowWorks --apply`), then `python.exe src/RimMandrake/FlowWorks/northstar/unset_bridge_look_live.py`.
- Polish (no page, so in the report): StylePickerCore.Register logs every accumulated Missing entry on each call, and
  PipeLook.Core is registered up to six times, so one missing style def logs up to six times.
