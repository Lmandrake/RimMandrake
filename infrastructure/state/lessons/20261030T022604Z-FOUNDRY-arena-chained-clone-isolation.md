arena_tasks: an arm clone whose base_sha already contains another pool task's fixed test blob is flagged as a leak (census also rejects such a chain item). Arms must get one clone per task at that task's base, and tasks whose bases descend from another task's fix cannot share an arm concurrently.
home: src/RimMandrake/Utils/arena/arena_tasks.py
