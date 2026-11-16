## spec
- The live half of RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME, UNRUN at its close (2026-11-15 23:25 PST): no pilot mod had a `session.id` yet.
- Wait for `python3 src/RimMandrake/rimflow/modledger.py resume-plan --mod ExplosiveKnockback` to say `"action": "resume"` (DISPATCH records `session.id` when a pilot run ends).
- The dispatcher's next EK holder launch carries `--resume <sid>` (its run record has `resume_session`); `systemctl --user kill <that unit>` mid-stage; then `python3 src/RimMandrake/rimflow/maturation_dispatch.py tick --apply`.

## verify
Acceptance test: none, a live systemd run (its offline twin is `python3 src/RimMandrake/rimflow/selftest_holder_resume.py`, ALL PASS).

## criteria
- `run.end` status killed in EK's DISPATCH.jsonl; `resume-plan` shows reconcile true; the new launch's brief opens with the resumed and "Reconcile first" lines and resumes the same session id; the resumed holder chases no refuted cause and re-asks no answered question.
