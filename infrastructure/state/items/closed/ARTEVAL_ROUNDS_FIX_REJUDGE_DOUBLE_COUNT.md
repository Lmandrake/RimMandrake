# ARTEVAL_ROUNDS_FIX_REJUDGE_DOUBLE_COUNT

RM_Mullgoth reached ESCALATE after only two renders. Its live art (same shas) was judged in two batches, fauna_leaningscrub_01 and fauna_cauldron_01 (it is listed in both biomes); both said REGEN and each bumped the global regen_rounds counter. r1 was recorded as round 3 and the next job was named r3; no r2 was ever drawn, and the subject escalated to the owner early.
He then kept the live art and pooled both renders (owner_escalations_cauldron_sheet_2026-10-24), so the early escalation cost nothing this time.

Fix: a round should count once per (subject, judged image sha set), not once per run that judged it. Re-judging the same pictures in a second batch must not advance the counter. Selftest: two runs judging identical shas -> one round.
Evidence: infrastructure/state/art_eval/runs/fauna_leaningscrub_01 and fauna_cauldron_01 decisions.jsonl (RM_Mullgoth); tuning table D:\ClaudeWork\rimmandrake\pipeline_tuning\cauldron.md observation 5.
