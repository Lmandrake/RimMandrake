arena vet: the cache key hashes arena_judge.py, so a full re-vet (~200 tasks, ~35 min at budget 200 per 411 s pass, load 15) is invalidated by any concurrent arena_judge edit; on 2026-10-30 it churned three ids mid-run. Vet the tasks that matter with `vet --task <RP_ids>` (seconds), and run the full vet only when no one is editing arena_judge.
home: src/RimMandrake/Utils/arena/arena_tasks.py
