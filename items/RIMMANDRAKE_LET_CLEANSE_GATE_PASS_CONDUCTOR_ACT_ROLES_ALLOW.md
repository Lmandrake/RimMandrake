## spec
Mandrake's card of 2026-11-28 2:17 AM PST ("Cleanse role text vs gate code" → "Change the code (Recommended)"). The
role files (designer_cleanse.md:49, :151, :324, :344; designer.md:142, :209) say the Conductor may retire or apply a
cleanse proposal as its recorded act; `cleanse_plan.plan_check`, which `designer_cleanse._gate` reads, accepted only his
plan `design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.json`. Change the code, not the text.

Contract: `design/concepts/CLEANSE_CONDUCTOR_ACTS.json` = {"schema": 1, "mods": {<Mod>: {"approved_digest", "act"}}}.
plan_check answers APPROVED for a mod whose owner's-plan answer is PLAN_MISSING, NOT_IN_PLAN, CHANGED_SINCE_APPROVAL or
AWAITING_REVIEW when the acts file names it, the digest is current and OWNER.jsonl holds an event on the act item with
perRuling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS. EXCLUDED, MARK_*, PLAN_MALFORMED and COULD_NOT_LOOK
stand. A named act with no such event is CONDUCTOR_ACT_UNRECORDED; an unreadable acts file or shard is COULD_NOT_LOOK.

## verify
Acceptance test: `python3 design/specs/2026-11-28-cleanse-gate-conductor-act/case_conductor_act.py`, expect
`cases 20 wrong 0`, exit 0. Watched red on base ba29ec7283: `cases 20 wrong 14`, exit 1, each wrong for want of reading
an acts file, the no-plan no-act `_gate` control right. Also `selftest_cleanse_plan.py` (48 checks) and
`selftest_designer_cleanse.py` (292 checks) stay green, and `cleanse_plan.py check --all` on the live plan reads the
same 23 lines before and after.

## criteria
A1 L0: case_conductor_act.py reads cases 20 wrong 0.
A2 L0: selftest_cleanse_plan.py and selftest_designer_cleanse.py read 0 failed.
