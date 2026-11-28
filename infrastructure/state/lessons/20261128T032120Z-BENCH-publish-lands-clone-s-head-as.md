./publish lands the clone's HEAD as it stands when the publish takes its tree-check slot, not when it starts: a publish started before a rebase lands the rebased commits. So a second ./publish from the same clone is a duplicate, and stopping the older one as stale stops the one that carries the new commits (seen 2026-11-27: the one stopped was in its pipeline checks, 45 min of line lost). Run one ./publish per clone at a time; to change what lands, change HEAD before the slot is taken.
item: RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS
home: skills/clone-landing-commits/SKILL.md
