A default sparse scratch clone (scratch_clone.py clone) lacks src/RimMandrake/contracts/, so code_review_status.py mark-clean crashes with FileNotFoundError contracts/jsonl.py. Fix in the clone: git sparse-checkout add src/RimMandrake/contracts (or add it to scratch_clone's default sparse set).
home: .claude/skills/clone-landing-commits
