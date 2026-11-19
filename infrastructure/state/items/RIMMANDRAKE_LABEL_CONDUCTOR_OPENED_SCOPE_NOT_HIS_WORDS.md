## spec
DESIGN DECISION 2026-11-18 (settles the scope_source question on RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS, review-1 finding 2 and review-2 finding 8): a Conductor event MAY open a built thing's scope, and it is never stored under his name.
- `scope: opened_by_owner` needs `scope_source` `OWNER:<tsn>` with at least one cited event carrying his words (`ownerSaid` or `byCard`). An OWNER-shard event with none of his words no longer opens it.
- New `scope: opened_by_conductor` needs `scope_source` `CONDUCTOR:<tsn>`, each an OWNER-shard event whose `perRuling` is `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` and which carries none of his words.
- Both let a removal ask through (`ask_errors`, designer_stage.py:840) and both are in scope (`UNIT_SCOPES`, :946). Found, not found in a read ledger, and ledger unread stay three answers.
- roles/designer.md line 115, roles/designer_dialogue.md line 67 and roles/designer_scene_contract.md line 68 name the new value.
- Existing records are not newly refused: 29 `opened_by_owner` inventory entries under design/concepts, 0 cite a missing event, 0 cite only word-less events [measured 2026-11-18 at 29dc91cd2].

## refs
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/roles/designer.md
file: src/RimMandrake/rimflow/roles/designer_dialogue.md

## criteria
- The acceptance test passes 28 of 28; selftest_designer_stage.py and selftest_designer_review_findings.py stay green; `designer_stage.py check` gives the same answer before and after on every design/concepts/*/record.json.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/scope_source_authority_accept.py` (28 checks; on 29dc91cd2, watched: 18 red, 10 green). Covers his typed words, his card, mixed and legacy citations, relayed words, a Conductor event, another ruling's event, an event with no ruling, a missing event, a wrong prefix, no source, an unread ledger, an empty ledger, the two constants and the removal ask for each scope.
