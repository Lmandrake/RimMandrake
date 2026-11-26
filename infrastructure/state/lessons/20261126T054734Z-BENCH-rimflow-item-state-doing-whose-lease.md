A rimflow item in state doing whose lease lapsed or was released is not held: rimflow next lists it in NEXT, and list_dispatch.py marks only a live lease as claimed (line 916). So a pile of doing items with no run does not stop the Workshop Pipeline; their dated waits decide when they start. Before a sweep of doing items, read their waits, not only their state (measured 2026-11-25: 49 BENCH doing items, 47 with a lapsed or released lease or none).
item: RIMMANDRAKE_SWEEP_SEAT_DOING_ITEMS_SIXTY_NINE_SIT_IN_DOING
home: skills/using-rimflow/SKILL.md
