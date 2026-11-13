## spec
Owner fix C (card: "Twice the item's cap, then park"): a judge-and-rework loop (the coverage judge round trip at
stage 5 and the rework runs between rounds) parks as waiting_owner with the same one-page summary once its spend
reaches 2x the item's cap. The count takes every stage run, retry, helper, consult, unmeasured reservation and judge
run since the loop began. Building work keeps advisory limits (ruling 2026-11-04).

Authority: owner ruling OWNER tsn=1794527688430451936 and card tsn=1794527885746395760 on RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS; Conductor brief 2026-11-12 (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). Already landed before this: 5e1fb090e736 (third-refusal stop), 40fde3bc437f (refusal_contract.py). Context: EK overnight loop, design/concepts/ExplosiveKnockback/stage.json; spec design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md.

## Done when
A selftest replaying EK's charges parks the loop at 8M (cap 4M) and launches no judge after; under the ceiling it
does not park; a building (stage 0-4) overspend stays advisory.
