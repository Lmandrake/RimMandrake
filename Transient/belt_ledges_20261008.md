# BELT: CRACKEDLANDS_LEDGES_OF_MERCY_1 (2026-10-08)

## Steps
- claimed (lease FOUNDRY.pid14551.13a3ca64). Read RM_LedgeRefuge.cs, RM_RefugeKernel.cs, RM_FossilStrata.cs (face-finding precedent).
- KCSG: FloodedCanyon has NO VEF dependency (RM tier, Harmony+FlowWorks only). "KCSG-style structure cut into cliff" built as our own C# GenStep carving into natural-rock faces (same pattern as RM_GenStep_FossilStrata) - no KCSG/VEF dependency added.
- artpipe find ledge/carving/chime/inscription/offering/mercy/canyon: no ledge, carving, chime-anchor or offering art for this subject. Art not approved (item Q4 open) -> NOT queued; placeholders ship.
- built: Source/RM_MercyLedges.cs (carver + GenStep + carving comp), Defs RM_MercyLedges.xml (ledge/carving/anchor), ThoughtDefs/RM_MercyCarving.xml (+4/2d PROVISIONAL), GenStepDef order 245 + MapCommonBase register patch, 2 settings toggles, debug action "Carve mercy ledges now", report gains carvings=/carvingReaders=.
- inscriptions draft: Transient/ledges_inscriptions_draft_20261008.md. Item prose rewritten (form ruled by card, built, owed). validation.py STATIC PASS, selftest 0 failures, build OK.
