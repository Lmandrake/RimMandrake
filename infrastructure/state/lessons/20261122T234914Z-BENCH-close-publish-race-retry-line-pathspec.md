A rimflow close --publish that loses a push race leaves its local commit, and the retry line it prints fails: the closed item's prose has already moved to items/closed/, so './publish ... items/<ID>.md' stops on 'pathspec did not match'. Land the local commit instead: src/RimMandrake/Utils/land.sh <sha> <the paths the retry line names> (2026-11-22, sweep of ExplosiveKnockback; worked first time).
item: RIMMANDRAKE_SWEEP_KNOCKBACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE
home: skills/clone-landing-commits/SKILL.md
