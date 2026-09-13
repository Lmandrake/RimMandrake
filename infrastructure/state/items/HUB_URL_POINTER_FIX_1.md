
## spec
The dashboard hub artifact was deleted (discovered 2026-09-13); BENCH rebuilt
it at **https://claude.ai/code/artifact/ec893765-f01c-4cd8-a0b2-58e5b0bf2257**
(all 5 tabs + sheets republished, lamps green at publish). The old URL
`d066e619-b84d-479c-842f-a81b0182511c` is dead. BENCH already updated
`src/RimMandrake/Utils/artpipe/artreg.py`, `DASHBOARD_HUB_ARTIFACT_1.md`, and
the memory note — but `HUB_TAB_PUBLISHER_MIGRATION_1.md` is FOUNDRY's item and
the cross-seat guard refused BENCH's edit. Replace the old URL with the new one
in that item (and anywhere else FOUNDRY-owned that carries it).

## verify
`grep -rn d066e619 infrastructure/ src/` returns no hit outside dated handoff
records (BENCH_REBOOT_HANDOFF_* are historical, leave them).

## criteria
No live instruction tells a seat to republish against the dead URL.
