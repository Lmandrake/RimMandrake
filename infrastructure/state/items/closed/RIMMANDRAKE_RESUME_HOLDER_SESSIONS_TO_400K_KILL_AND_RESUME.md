# RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME

Plan step 6 (`design/plans/2026-11-15-holder-pipeline-fusion-build.md`; spec `design/specs/2026-11-15-holder-pipeline-fusion.md` Option B and §3.4). His card 2026-11-15: "Resumed session per mod (Recommended)" ·
"Try 400k first." His addition: "a mod holder should be handing off to its next version with context of what has
happened before. Even into judging phases." The dispatcher resumes one holder session per mod (`claude -p --resume`) for
its stages and through the judging phases, rotates it at the first boundary past `holder_context_ceiling_tokens`
(modledger.json, 400000), reconciles after a forced stop before it resumes, and falls back to the packet.

## spec

- `modledger.resume_plan(root, mod)` as the acceptance test's contract says; the holder records `session.id` with its
  context size; a version.open does not end the holder.
- maturation_dispatch.py resumes through it with `--resume`; a spend cap per mod and stage replaces the per-run cap for
  holders (spec Option B build effort); the per-stage USD 100 ceiling stays.
- Kill-and-resume test: kill a holder mid-stage; the next launch reconciles, resumes, avoids a refuted cause and does not
  re-ask an answered question. Offline half below; the live half (a real resumed detached systemd run) is UNRUN until run.
- Falsifiers to read on the pilots (spec §4): a refuted cause chased again or an answered question re-asked (target 0);
  cost per stage against an A run (drop to A above ~1.5x).

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_resume_accept.py` — expected `PASS 8/8`.
Watched failing at filing on 6a171f08f2: `FAIL 7 of 8` (no resume_plan; the packet clause already holds).

## criteria

- the acceptance test passes; the live kill-and-resume run is recorded, or named UNRUN with its command.
