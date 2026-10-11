# 15 — project CLAUDE.md slim-down progress (2026-10-11)

Brief: fix false claims (CLAUDE.md, CHARTER), MOVE plan to ~35–40%, Compact Instructions, skills/README header, global CLAUDE.md drift report.

## Milestones
- [x] 1. false/stale claims fixed (CLAUDE.md + CHARTER) — PUBLISHED c71be9e55. Audit error found: NORTHSTAR_HASH_SCOPE_1 (dropped) and WALK_FEATURE_KEY_1 (done) DO have ledger events; only DLL_SOURCE_STAMP_GUARD_1 was a ghost (repointed to the hook).
- [x] 2. MOVE plan executed — PUBLISHED 4d287a5e3. 40/40 owner quotes verified present after the move (fragment search over CLAUDE.md + CHARTER + 6 destination docs).
- [x] 3. Compact Instructions section (in 4d287a5e3)
- [x] 4. skills/README header — 823d9385c on origin (carried by a peer's publish): four-seat table + POLICY.md pointer deleted, `.skill`-zip install claim replaced (editing skills/<name> IS installing), outside-repo table cut to 4 lines, counts re-measured (35 dirs; 34 wired + review-sheets). NOT mine, still false: `src/RimMandrake/Utils/package_skill.py` docstring repeats the zip-install claim.
- [x] 5. global CLAUDE.md drift — reported, nothing applied (below)

## Sizes
before: 73,114 B (CLAUDE.md), 11,311 B (CHARTER)  after: 20,695 B CLAUDE.md (28%), 10,938 B CHARTER

## Published shas
- c71be9e55 fixes (CLAUDE.md, CHARTER)
- 4d287a5e3 the move (+ Compact Instructions, DLC section, CHARTER worktree trim)
- 823d9385c skills/README header

## Global CLAUDE.md — proposed Lodestar source edits

`~/dev/Lodestar/bin/claudeconf.py check` (2026-10-11): live `~/.claude/CLAUDE.md` DIFFERS from the rendered
sources; 1 auto-memory file changed since snapshot. `preview`: 5 sections CHANGED (Machine, full paths,
Placard, Subagents, Messaging), 1 ADDED (question-card section), rest KEPT. Not applied — owner's file.

1. **Model ladder** — the SOURCE `claude/global/45-subagents.md` is already current (Sonnet 5 on GovCloud;
   `haiku` silently remaps to Sonnet 4.5). The LIVE file is stale ("Sonnet 5.5", "haiku dies with 400")
   only because nobody rendered. Fix = owner picks: `claudeconf.py adopt` (pull any live hand edit back)
   then `render`, or `render` straight.
2. **`claude/global/50-save-as-you-go.md` L28** "Merge in a private `git worktree` and push from there"
   collides with RimMandrake's worktrees-OFF ruling + `block_worktrees.py`. Proposed text: "Merge in a
   fresh clone (or a private `git worktree` where the project allows worktrees) and push from there."
3. **`claude/global/machines/archmagi.md` L16** "The `wsl-windows-plumbing` skill covers the rest." —
   no such skill exists (not in `~/.claude/skills`, `D:\Luke\dev`, or Machinist; python glob, probe 193
   paths). Proposed: delete the sentence, or point at the real home of the WSL keepalive notes.
4. Not mine but auto-loaded: MEMORY.md line "Model ladder … Haiku OS searches only" contradicts 45-subagents.md.

## Notes for the owner / other writers
- Project CLAUDE.md landed at 28% (20.7 KB), below the 35–40% target: everything left is a rule or pointer.
- Audit error: NORTHSTAR_HASH_SCOPE_1 (dropped) and WALK_FEATURE_KEY_1 (done) DO have ledger events.
- The ~/Desktop flight doc exists nowhere on this machine (find /); pointer deleted, its checklist kept in flight.md.
- Inbound refs to moved CLAUDE.md sections remain in items/src/design files (e.g. `bridge_system.md`, mod_audit briefs,
  `flowworks_shows_wiring_2026-10-01.md`); CLAUDE.md's pointer table routes them. `skills/rimworld-load-round/SKILL.md`
  still says ~25 min cold load (not my path).

