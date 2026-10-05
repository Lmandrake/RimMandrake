# GimmeSomeSlack north-star seed notes (2026-10-05)

## Findings
- `modcheck floor --all` (the only mode; `--all` is required) counts bars only for a VALIDATED section; a DRAFT
  section reads "no bar" by design (floor.triage, runner.visual_floor). So floor cannot show "bar met" for a DRAFT;
  the pre-validation check is the same join (floor.uncovered_shows / floor.orphan_shows) run in memory against the
  DRAFT ids -- done below, read-only.
- status.mod_hash excludes ONLY validation.py, human_review.py, northstar/, __pycache__. Editing validation_hose.py,
  validation_aerial.py, validation_style*.py or proof_all.py would change the mod hash and make the running
  proof_all result STALE (record refuses). => all shows= wiring goes in validation.py only.
- The modcheck suite in validation.py declares components per row id (_report_rows, declare lists); `modcheck
  record` judges proof_all's rows. Row ids from hose/aerial/style blocks are produced by proof_all, not by the
  suite's own chains.

## Bars written
17 must-show + 2 cannot-show, DRAFT, blank validated-hash, appended to
design/validation_walks/RimMandrake/GimmeSomeSlack.md. Groups: floor cords 5, overhead 2, hoses 7, styles 3.
One (change) line: hose_plumps_only_from_powered_pump (UNBUILT: no FlowWorks pump). No motion bars (his ruling).
northstar.parse: state DRAFT, 17 must / 2 cannot.

## Coverage wiring
validation.py only (mod_hash-excluded): ROW_SHOWS {row id -> bar ids}, passed as shows= in _report_rows;
live_battery declares CORE_SHOW_IDS too; new chain proof_all_only_rows declares the 31 proof_all-only row ids
(UNMEASURED on a live `modcheck run`, never PASS) + NS_hose_plumps_only_from_powered_pump (UNBUILT).
In-memory join vs the DRAFT ids: uncovered [] / orphans [] / cannot-show unclaimed []; probe id zz_probe comes back
uncovered (gate can fail). Every claimed row id exists in proof_all_20261005T082415.json (all PASS) or OFFLINE_IDS,
except the new UNBUILT pump row.
floor --all: GimmeSomeSlack DRAFT 0/0 "no bar" (DRAFT binds nothing by design); FlowWorks/Graffiti/Pyrelands bar met;
no REFUSED row. doctor: GSS only WARN WALK_WITHOUT_CAPABILITY (pre-existing). lint 0 FAIL. selftest_northstar passes.

## Open questions
- Owner: replace the relayed (non-verbatim) 2026-10-05 paragraph with his own words, then validate.
- proof_all.py does not emit NS_hose_plumps_only_from_powered_pump, so `modcheck record` never sees the UNBUILT
  bar; adding it means editing proof_all.py, which changes mod_hash (do after the running proof is recorded).
- reel_offers_choose_style is claimed by CR7, which RECORDS the gizmo labels ("Choose style" present) but asserts
  nothing about them; an assert would be a proof_all-side (hash-changing) edit.
- Pre-existing: floor's [S]-step regex misses the walk's "X. [S]" line (reads "-"); toggle floor lists 16 settings
  no row flips (not wired into runs, spec section 7).

(progress) Row ids taken from northstar/proof_all_20261005T082415.json (live, 144 rows, all PASS but P1 SKIP) plus the
suite's offline ids (O1-O6, in validation.OFFLINE_IDS). Owner 2026-10-05 findings found verbatim on disk only for the
reel ("reels don't have a choose style option", Source/Hose/CompHoseReel.cs:583) and hostiles (human_review.py:1381);
brass joiner / reel nozzle / deflated-unless-pump exist on disk only as agent paraphrase (HoseMath.cs:560,
HoseSelfTest.cs:562) -> marked as relayed paraphrase in the section, owner to replace.
"Kill all hostiles on review maps" is a harness rule (proof_all P3, human_review sweep_hostiles), not a mod look -> no bar.
