arena_tasks.arena_lock(p) (flock on <arena>/arena.lock) is the contract: freeze holds it from the assign check through its appends. Every other arena event writer (assign, result, the event-log module) must append under the same lock or the 'frozen before assigned' guarantee is void.
home: src/RimMandrake/Utils/arena/arena_tasks.py
