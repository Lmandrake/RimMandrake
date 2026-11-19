# RIMMANDRAKE_MOVE_IMAGE_SKILLS_TO_WORKFLOWS_GPT_TOOL_BORROWS selftests at 97fd9a31edfacf279a9f615b8f2f52975c71d0a2 (2026-11-19 13:40 PST)

| test | rc | last line |
|---|---|---|
| `src/RimMandrake/Utils/selftest_image_skills.py` | 0 | OK: 0 failure(s) |
| `src/RimMandrake/Utils/selftest_skills_by_work.py` | 0 | PASS: 0 failure(s) |
| `src/RimMandrake/Utils/selftest_gpt_consult_codex_finder.py` | 0 | OK: 0 failure(s) |
| `src/RimMandrake/Utils/selftest_codex_side.py` | 0 | ok |
| `src/RimMandrake/Utils/selftest_gpt_consult_rounds.py` | 0 | ALL PASS |
| `src/RimMandrake/Utils/selftest_gpt_consult_verdict.py` | 0 | ALL PASS |
| `src/RimMandrake/Utils/selftest_codex_advice.py` | 0 | PASS: selftest_codex_advice (0 failing) |
| `src/RimMandrake/Utils/selftest_review_identity.py` | 0 | ALL PASS |
| `src/RimMandrake/Utils/selftest_sprite_reference_crisp.py` | 0 | RESULT: PASS |
| `src/RimMandrake/Utils/artpipe/selftest_artpipe.py` | 0 | all checks passed |
| `src/RimMandrake/Utils/artpipe/selftest_artpipe_codex_blip.py` | 0 | all checks passed |
| `skills/generating-rimworld-sprites/scripts/selftest.py` | 0 | all 12 cases behaved as specified |
| `skills/generating-rimworld-sprites/scripts/selftest_rule_canvas.py` | 0 | OK: 0 failure(s) |
| `src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py` | 0 | RESULT: PASS |

Failed on base: selftest_gpt_consult_codex_finder 3/3 FAIL; selftest_image_skills FAIL (folders and 5 readers present); selftest_gpt_consult_rounds and _verdict FAIL on base for stale expectations (fixed in c03c9ab31f).
Live: gpt_consult.py "say ok" answered ok in 7 s; rm-artpiped restarted 13:32 PST, synced to baa9de69b, codex sandbox preflight ok; validate_sprite.py ran on FoldLamp_south.png (REJECT byte-identical, the correct verdict for self-vs-self); Cauldron mutant sweep baseline 0, 16/16 RED.
MandrakeWorkflows: selftest_codex_image all checks passed, selftest_codex_pwset_retry ALL PASS, queue_runner 21/21, grumpiness 12/12, codex_image.py probe rc 0, tests/test_skills.py test_every_skill_is_valid PASS.
UNTESTED: a real art job (image generation) on the moved worker.
