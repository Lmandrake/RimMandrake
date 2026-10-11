# 14 — night-shift-orchestration skill + memory prune (progress)

Writer: BENCH subagent, 2026-10-11. All steps done.

| step | state | PUBLISHED |
|---|---|---|
| A skill night-shift-orchestration | done — global, `~/dev/Lodestar/docs/night-shift-orchestration` (beside `handoff`), declared in Lodestar `claude/skills.md`, linked at `~/.claude/skills/night-shift-orchestration` | Lodestar `e1bff9cc` |
| B0 memory backup | done — `~/.claude/backups/weekly_cleaning_2026-10-11/memory.tgz` (199 entries) | n/a (no git) |
| B memory prune + MEMORY.md rewrite | done | n/a (no git) |
| C orchestration memories -> skill | done (11 files deleted, index points at the skill) | n/a |
| link check | done — 135 links, 0 missing, 0 unindexed, 0 empty | |

## A — skill
- Home: global skills are symlinks into ~/dev repos; `handoff` already lives at `~/dev/Lodestar/docs/handoff`, so this sits beside it and is wired through Lodestar's `claude/skills.md` manifest (machines: all).
- Files: `SKILL.md` (generic shift: record the order in-session not as memory, slot loop, paste-every-time brief block, one live-resource driver, lessons-as-learned, idle-compaction ritual, morning summary); `references/rimmandrake.md` (bridge lock + owner quotes, Full belt pointer to FOUNDRY.md, ledger_sync, side-effect files); `scripts/compaction_check.py` (finds the last compact_boundary in the session transcript, checks for a write-mode handoff.py call before it, `--extract` dumps the lost segment + harness summary). Tested on 4 real transcripts: HANDOFF_WRITTEN, HANDOFF_MISSING, NO_COMPACTION x2.
- efficient-subagents absorbed by pointer only; model ladder by pointer (Agent_Policy.md + Lodestar `claude/global/45-subagents.md`).
- Trigger eval: `evals/trigger_evals.json` (13 queries). skill-creator's `run_eval` returned trigger_rate 0.0 for every query AND for a sanity probe ("prepare for agent reboot" against the installed `handoff` skill) — the instrument is blind in this environment, so triggering is **UNMEASURED**, not failed.
- Not done (outside my paths): no pointer added in FOUNDRY.md/BENCH.md; skills/README.md not touched (the skill is global, not a project roster row).

## B/C — memory (`~/.claude/projects/-mnt-d-Luke-dev-RimMandrake/memory`)
- **Before:** 197 topic files + MEMORY.md (163 lines, 22,144 B), 1 empty file, 17 unindexed.
- **After:** 135 topic files + MEMORY.md (65 lines, 11,124 B), 0 empty, 0 unindexed, 0 missing links (script-verified, with a known-present sanity probe).
- Deleted 67: 15 expired session orders (incl. gss-build-then-hose-port-program); 11 orchestration memories now covered by the skill (foreground-only x2, push-line, fork x2, mark-clean side files, belt floor, one-bridge-driver, parallel-bridge, never-assume-bridge, keep-bridge-busy — owner quotes kept verbatim in the skill's RimMandrake overlay); 17 merged into 6 new files (model-ladder, gpt-consult, cherry-picker, queue-hygiene, game-said-flag; save-states folded into map-state-is-disposable-debug); stale: rimworld-current-phase (start save + tile 17007 moved to rimworld-ashkarr-map), agent-role (into redesign-4), github-mirror, art-lawset, ashkarr-authoring-state, ashkarr-audit-artifact, creature-art-register, quicktest-crashes-full-modlist; CLAUDE.md/skill duplicates: worktrees-off, zsh word-split, flyer testing, RC drops, system screenshot, foundry restart auth, shortest-path, files-must-shrink, rimflow close-sha / cli-quirks / ledger-local, biome-mod-split Q12-15, proposals-suite, fable x2, foundry-window-collision, two-blind-arms (in efficient-subagents).
- Rewritten/fixed: model ladder now pointer-only (no Haiku); gpt default gpt-6.1-sol/high; key-paths (old D:\Luke\dev\Rimworld paths gone, ~15 min); minimal-modlist (~15 min); ashkarr-map (CSV is a record, never ashkarr_paint, worldview command); redesign-4 (seat clones, queue views on read); liquids gate clause dropped; world-remake second half cut (now CLAUDE.md); spring-cleaning "tonight's work" + conflicting drain count removed; owner-modes paths fixed; empty northstar-seed file rewritten from its index line; 18 files' wikilinks retargeted to merge targets.
- **Kept, not moved (other owners):** the 6 git-trap memories (12_git_tooling_progress.md has "GIT_WORKFLOW Traps" still todo — left for that agent); question-card / confident-wrong-numbers / verify-before-you-escalate / nemotron clusters (promotion into those global skills not done, so they stay indexed); build-designs-its-own-verification, rimworld-tag-and-money-audit, worldmap-docs-pass-owed (their audit "MOVE" targets are repo files outside this brief).
- 17 dangling `[[wikilink]]` targets remain inside topic files (mostly skill names; pre-existing dead memory names).
