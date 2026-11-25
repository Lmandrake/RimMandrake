When ./publish refuses with a tree check that is 'red on origin/main too … not proved pre-existing', run ./sync before repairing it: publish runs the checks on the clone's own stale base, and another run may already have landed the fix (2026-11-24: boundary_check.py was fixed by a second run while this one repaired the same page, and the replay then conflicted).
item: RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY
home: skills/clone-landing-commits
