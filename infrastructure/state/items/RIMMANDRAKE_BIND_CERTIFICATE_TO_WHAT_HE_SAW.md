# RIMMANDRAKE_BIND_CERTIFICATE_TO_WHAT_HE_SAW

## spec
`concept_tree.owner_event_problem` (737-754) accepts any ownerSaid/byCard event on the item newer than the verdict;
`certify` (802-832) can replay it after a tree edit; `owner_certificate_problem` binds only (judge run, verdict, gap
count). Source: skeptical review 2026-11-15
(`D:\ClaudeWork\rimmandrake\conductor\maturation_gpt_review_20261115\claims_checked.md` B2-B4, A14;
`design/RimMandrake/maturation_pipeline.md` §9 item 11).

## decision (2026-11-15, Evidence-for-Ask, delegated)
Taken under RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME (no evidence against the obvious answer).

1. The owner certificate binds to what he was shown: the exact gap ids and gap text on the card, plus the tree.json
   hash and the sheet hash at the time he answered.
2. It is replay-proof: a tree edit after his event voids the certificate unless a newer OWNER event of his covers the
   edited tree.
3. Exception, for consistency with his card "Do you certify ExplosiveKnockback's tree with the container now thrown a
   short way? -> Certify, and fix the rule" (2026-11-15 13:13Z,
   RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT): an edit made under his own recorded card (the edit
   event cites that card) carries the certificate forward. Build the two together or this one after it.

Sources: his card 2026-11-13 00:29Z "EK coverage, 4 gaps -> Show me the 4 gaps, then I certify" (a certificate is of
the gaps he saw); as-built doc §5. Evidence against: none found; no ruling of his lets a certificate cover a tree he
did not see.

Builder also owes: update `design/RimMandrake/maturation_pipeline.md` §9 item 11 in the same commit.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_concept_owner_certify.py`, new
cases: a certificate with different gap ids refuses; a tree edit after his event refuses; an edit citing his card
carries; his newer event after an edit certifies.
