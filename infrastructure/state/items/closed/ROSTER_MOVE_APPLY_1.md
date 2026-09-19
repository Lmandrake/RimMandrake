# ROSTER_MOVE_APPLY_1 — the ruled moves never reached the rosters

## spec
MEASURED 2026-09-11 (BENCH spot-verified): of the 169-row move table in
`design/Jawa/worldbuilding/review/round2/move_mapping_v2.md`, 114 rows resolve to
a live roster move and **0 of 114 are present in the target roster**
(`design/Jawa/worldbuilding/biomes/rosters/*.json`); 18 are additionally still
listed in their origin roster. Example: Hssiss — owner-ruled "stays Sump"
(f28f12b4) — absent from `the_sump.json`, still in `the_greentide.json`. The
round2 pipeline (0198c6f9→684f0a8d) wrote only the decision-tracking files; no
commit writes the roster fauna arrays.

The work:
1. Extend `design/Jawa/worldbuilding/review/apply_assignment_verdicts.py` to take
   the mapping table (or a JSON derivative of it) as the move-target source
   instead of free-text note parsing — the notes are owner vocabulary the
   resolver cannot parse (113 blocking errors today); the mapping already
   resolves every row, owner-validated nickname table included
   (ocular→the_contagion, Crystal caverns→the_lantern_deeps, Not here→OUT).
2. Rows resolving to OUT / OPEN / GROUP:* / RESERVED are not roster moves — skip,
   they are handled by the disposition apply and reserved-group drafts.
3. 🔴 3 rows target `the_lantern_deeps`, which has NO roster JSON (BMT_Gembug,
   BMT_CrystalCrab, BMT_FacetMothLarvae) — create the roster file or escalate;
   do not drop them silently. Wampa's "VISITOR-DYING, never native" needs a
   visitors field `nightside_ice.json` does not have; Blarth's dual-listing
   ruling likewise never landed — both bit KeyErrors once already (LESSONS_INBOX).
4. Remove moved creatures from origin rosters in the same pass (18 still-in-origin).
5. Then `rosters/_validate.py --cross` green, then the regeneration commands it
   prints (cast, patches, flora) rerun and committed.
6. Every ruling lands in THREE files together or the deck lies:
   `decisions_propagated.json` + `move_mapping_v2.md` + `biome_findings.md`
   (standing rule from BENCH_REBOOT_HANDOFF_202609110230).

Flora is NOT in scope: its 15 move rows have no structured targets yet — 6 need
an owner card (BENCH owes it).

## verify
- [ ] Re-run the reconciliation: every live mapping row present in target, absent
      from origin; count reported MEASURED.
- [ ] `_validate.py --cross` green; regeneration commands rerun and committed.
- [ ] Commit message does not overclaim past a mid-script error (the Wampa/Blarth
      lesson — verify the write landed, per row, before claiming N applied).
