scene.judge decides from the contract (exposure, played ticks), not from the PASS/FAIL rows a scene prints after its session: a planted run whose rows went red still judged SUCCESS (ExplosiveKnockback, 2026-11-25), and the judge writes that SUCCESS to scene_runs.jsonl. Until a scene's checks are contract conditions, its verdict for Stage 6 is the row it records with maturation.py live-row, not the judge's outcome.
item: RIMMANDRAKE_PROVE_KNOCKBACK_SIX_NEW_SCENES_LIVE_ARCHSMALL_SAT_FREE
home: src/RimMandrake/Utils/scene.py help (judge.md, contract.md)
