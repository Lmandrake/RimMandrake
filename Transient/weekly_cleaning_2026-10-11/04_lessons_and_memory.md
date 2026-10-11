# 04 — Lessons store and auto-memory (weekly cleaning 2026-10-11)

## 0. Measurements (all MEASURED by python scripts run 2026-10-11)

- **One memory store, three names.** `~/.claude/projects/-home-mandrake-rm-bench/memory` and `-home-mandrake-rm-foundry/memory` are both symlinks to `~/.claude/projects/-mnt-d-Luke-dev-RimMandrake/memory` (created 2026-10-02 00:20). BENCH and FOUNDRY share ONE auto-memory: 197 topic files + `MEMORY.md`. Every prune applies to both windows at once.
- `MEMORY.md`: 163 lines, 21,784 bytes, 177 markdown links + 4 `[[wikilinks]]`. **0 index lines point at a missing file.**
- **17 topic files exist but are not indexed** (listed in §1.D).
- **1 topic file is empty (0 bytes) but indexed**: `northstar-seed-with-guesses-dont-wait-for-human.md` (index line "Northstar: seed with guesses").
- **27 distinct `[[wikilink]]` targets inside topic files resolve to no memory file** (40 source references). Most name skills (`rimworld-load-round`, `rimworld-savegame`, `measuring-large-artifacts`, `confident-wrong-numbers`, `efficient-subagents`, `frozen-artifacts`, `rimworld-debug-testing`, `verify-before-you-escalate`, `rimworld-content-moderation`), which is harmless but unresolvable as a memory link. Genuinely dead memory targets: `rimworld-project-orientation` (5 referrers), `no-agent-to-agent-messaging` (2), `rimworld-drive-move-complete`, `one-subagent-while-afk-2026-10-07`, `ashkarr-planet-map` (2), `bridge-silent-failures`, `rimworld-savegame-anatomy`, `deciding-and-superseding-is-propagation`, `art-legibility-gate`, `frozen-artifacts-and-regeneration`, `jawa-sea-monsters`, `rimmandrake-moniker-for-mods`, `never-hand-a-task-without-the-command`, `thruster-instabuild-substructure-trap`, `worldmap-desert-band-repair-owed`; plus two item IDs written as wikilinks (`BRIDGE_MAPGEN_STALE_FINALIZE_1`, `MODCHECK_SUITE_CORRECTIONS_1`).
- **`wsl-windows-plumbing` is not a global skill.** `~/.claude/CLAUDE.md` says "The `wsl-windows-plumbing` skill covers the rest", but it exists only at `~/dev/Hestia/.claude/skills/wsl-windows-plumbing` (no copy or symlink in `~/.claude/skills/`), so RimMandrake sessions cannot load it. Any "PROMOTE to wsl-windows-plumbing" below first needs it symlinked into `~/.claude/skills/`.
- `efficient-subagents` is a **project** skill (`skills/efficient-subagents/`), not a global one; `git-efficiency`, `question-card` and `confident-wrong-numbers` are global (`~/.claude/skills/`).
- Other projects with memory: `-mnt-d-Luke-dev-Hestia` (11 files), `-mnt-d-Luke-dev-hestia` (3; a case-variant duplicate project dir of Hestia, last written 2026-09-12), `-mnt-g-My-Drive-JPL-dev-Nemotron` (5), `-mnt-g-My-Drive-Personal-Rimworld` (2: an old GDrive-era copy of `jawa-patches-deploy-path.md` whose content differs from ours). No cross-project duplicate of a RimMandrake memory except that one.
- `~/.claude/projects/` totals **7.3 GB**: `-mnt-d-Luke-dev-RimMandrake` 4.1 G, `-home-mandrake-rm-foundry` 1.8 G, `-home-mandrake-rm-bench` 1.2 G (session logs, not memory). **79 `-tmp-nsjudge-*` project dirs** (about 42 MB, all with an empty `memory/`) are debris from northstar-judge runs launched in `/tmp`. Flagged for the disk dimension.
- Lessons store: **298 lesson files + README.md** in `infrastructure/state/lessons/` (the brief's 299 includes README). 105,258 bytes total, median 307 B, max 1,058 B. By seat: FOUNDRY 132, BENCH 128, UNSEATED 35, MACBENCH 3. By date: 21 files predate the 2026-09-23 drain (2026-09-11 to 09-23); 277 filed since; **37 on 2026-10-11 alone**, and 24 to 30 per day on 09-24..09-26.
- `src/RimMandrake/Utils/lessons.py`: 121 lines; verbs `add` / `render` / `list` only. No `fold`, `drop`, `stats` or age reporting.
- **Drain-count conflict:** `infrastructure/state/lessons/README.md` says "Last drained 2026-09-23 (308 of 337 entries folded…)"; memory `spring-cleaning-rulings-2026-09-23.md` says "326 of 337 … 11 homeless remain". One is wrong and neither is re-measurable now (the inbox was a single file then). Keep one sentence and delete the other.

## 1. Memory prune list

All paths are under `~/.claude/projects/-mnt-d-Luke-dev-RimMandrake/memory/` (the BENCH and FOUNDRY memory dirs are symlinks to it). Native: `\\wsl.localhost\Ubuntu\home\mandrake\.claude\projects\-mnt-d-Luke-dev-RimMandrake\memory\`. Risk applies per row; the general risk is that the memory dir is not in git, so a DELETE there has **no git provenance**. Back up the dir (`tar czf`) before acting.

### 1.A Expired session orders: DELETE (15 files)

Each of these is a concurrency or priority order scoped to one night, one session or one date that has passed. Together they make up 7.6% of the files and about 10% of the index lines, and they get loaded into every session as noise. Two of them contradict each other on the same night (2026-10-08 says "up to four" and "at least one, max 3").

| file | why dead | risk |
|---|---|---|
| `afk-night-2026-10-07-two-subagents.md` | the night passed | none |
| `afk-night-2026-10-08-four-subagents.md` | the night passed; also conflicts with the next row | none |
| `afk-night-2026-10-08-one-subagent-minimum.md` | the night passed | none |
| `afk-night-2026-10-10-three-subagents.md` | the night passed | none |
| `afk-night-2026-10-10-two-subagents.md` | the night passed | none |
| `afk-night-2026-10-11-three-subagents.md` | "ends when he returns"; he has returned (the 2026-10-11 cleaning order) | none |
| `no-subagents-night-2026-10-05.md` | expired 2026-10-06 | none |
| `one-subagent-max-rest-of-2026-10-07.md` | expired 2026-10-07 15:00; unindexed | none |
| `subagent-cap-four-until-thursday-2026-10-08.md` | its own text says RESCINDED | none |
| `subagent-concurrency-cap-until-2026-09-30.md` | expired 2026-09-30 15:00 | none |
| `thin-orchestrator-three-subagents-2026-10-08.md` | "session-scoped" | none |
| `two-subagents-keep-bridge-busy-2026-10-10.md` | session-scoped; its "keep bridge busy" half is already `keep-the-bridge-busy-multitask.md` | none |
| `keep-four-validation-builders-running.md` | paused 2026-10-07 17:40 by the owner ("dont start new") and overtaken by the GSS/hose program | low: if he wants the validation-builder loop back, he re-says it |
| `code-review-loop-paused-until-2026-09-23.md` | expired; unindexed | none |
| `gss-build-then-hose-port-program-2026-10-10.md` | its own status line: "ALL 8 STAGES DONE"; the open Q1 to Q6 are in `infrastructure/state/handoffs/BENCH_HANDOFF_202610111523.md` | none |

**Structural fix (PROMOTE):** stop writing session-scoped orders as memories. They belong in the session (or in one overwritten file such as `current-standing-order.md` that carries its own expiry line). Add a rule to the auto-memory guidance: *a memory whose name carries a date that has passed is deleted at the weekly cleaning.*

### 1.B Contradictions and stale facts: UPDATE or DELETE

| file | finding (evidence) | action |
|---|---|---|
| `model-ladder-opus-sonnet-haiku.md` + `fan-out-cheap-by-default.md` (+ the MEMORY.md line "Haiku OS searches only") | Both say "haiku for OS-level searches". `~/.claude/CLAUDE.md` says "DO NOT PASS `model: haiku`", with sonnet for searches. `infrastructure/agents/Agent_Policy.md:39` says the haiku alias resolves (now to Sonnet 4.5) and works. Repo `CLAUDE.md`: "the ladder lives in Agent_Policy.md and nowhere else; never restate a model choice outside it." | **MERGE into one `model-ladder.md`, pointer only:** "The ladder lives in `infrastructure/agents/Agent_Policy.md` (repo) and `~/.claude/CLAUDE.md` (global); never restate it. Always pass `model`. Owner 2026-09-25: *"Please fan out efficiently from now on, only use expensive models when required."* Prefer one inline python script to any agent for mechanical work." Risk: none. **Also escalate:** the global CLAUDE.md ("haiku 400s") and Agent_Policy.md ("haiku works") disagree with each other. The CLAUDE.md dimension should resolve it. |
| `gpt-consults-need-high-effort-and-sol.md` | Says "gpt_consult.py defaults to gpt-5.5 if -m is omitted". **False now:** `src/RimMandrake/Utils/gpt_consult.py:23` defaults to `gpt-6.1-sol`, and `:54` defaults `--effort high`. | DELETE (merged below) |
| `gpt-consult-route-authorized.md`, `gpt-consult-via-codex-cli.md` | Both say "no consult tool exists yet". It exists: `gpt_consult.py`, already listed in repo CLAUDE.md "Tools". | **MERGE all three into `gpt-consult.md`:** "Authorized, owner 2026-09-27: *"You may use the GPT consult route … It is Fable class."* Run `python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>…` (defaults: gpt-6.1-sol, high effort). Grade its output like any delegate's." Risk: none. |
| `quicktest-crashes-full-modlist-use-cheap-mechanism-list.md` | Repo CLAUDE.md "Tools with surprising side effects": `start_debug_game_ready` is "VERIFIED on the full 629-mod list, 2026-09-27"; the crash came from three bugs in our own content. The memory's premise is now false. | DELETE. The "mechanism tests use a minimal list" advice is owned by `skills/rimworld-load-round` and `rimworld-debug-testing`. Risk: low. |
| `rimworld-key-paths.md` | The project is `D:\Luke\dev\Rimworld` (now `/home/mandrake/rm/<seat>`, with `D:\Luke\dev\RimMandrake` as the mirror); "cold load ~23 min at 562 mods" (repo CLAUDE.md: ~15 min at 599). Links to two dead memories. | UPDATE: keep only the `Player.log` / `Player-prev.log` / `Config\Mod_*.xml` / `Data\` paths; point to CLAUDE.md for Mods/ModsConfig/cold-load. Risk: none. |
| `rimworld-minimal-modlist-regime.md` | "~25 minutes" for a full load; CLAUDE.md measured ~15 (2026-09-07). | UPDATE the number to "~15 min (CLAUDE.md, MEASURED 2026-09-07)". |
| `rimworld-current-phase.md` | Dated 2026-09-13: "590 active", "active track: worldmap editing", "COMMISSION BUILD wave". The index line says "593 mods". All stale. | DELETE. Move the one surviving fact (the canonical start save is `CANONICAL_ASHKARR_START_2026-09-12.rws`, tile 17007) into `rimworld-ashkarr-map.md`. Risk: low. |
| `agent-role-is-set-per-window.md` | "Several Claude windows share one working tree" (false since 2026-10-02, when seat clones landed); path `D:\Luke\dev\Rimworld\infrastructure\agents`; links to two dead memories. | MERGE into `redesign-4-two-windows.md`. |
| `redesign-4-two-windows.md` | "queue views render on every rimflow write". Repo CLAUDE.md says they are "gitignored caches since 2026-10-02 … rendered on read". It also cites `Fable_Review/` under the old D:\ path. | UPDATE: absorb the row above, fix both facts, and drop the dead `[[no-agent-to-agent-messaging]]` link (messaging is allowed since 2026-09-26 per global CLAUDE.md). |
| `belt-mode-fanout-minimum.md` | It declares itself SUPERSEDED; the canonical text is `infrastructure/agents/FOUNDRY.md:128` "Full belt". Its index line still teaches the dead "≥3 queue agents, ≥1 art regen" floor. | DELETE. Risk: none. |
| `github-issues-mirror-live.md` | The name says "live" and the body says RETIRED; the scripts it warns about are deleted. | DELETE. |
| `art-lawset-and-canon-push.md` | The description is "REVERSED"; the one surviving law (the canon library) is in repo CLAUDE.md "Art is judged against the canon library". | DELETE |
| `ashkarr-authoring-state.md` | "WHICH ONE IS CANONICAL IS UNDECIDED". Decided 2026-09-12 (CANONICAL_ASHKARR_START). It is a 2026-08-26 session record, and `world/audit_2026-08-26/` is the durable record. | DELETE. Risk: low; the audit dir keeps the detail. |
| `ashkarr-audit-artifact.md` (unindexed) | Source at `D:\Luke\dev\Rimworld\TRANSIENT_ashkarr_audit.html`, a path that no longer exists as a repo. | DELETE |
| `creature-art-register-retired-2026-09-11.md` | Names `round2/decisions_propagated.json` as the live authority. Since 2026-10-04 the art ledger plus `infrastructure/state/art_rulings/` are the authority (repo CLAUDE.md). UNMEASURED whether `decisions_propagated.json` is still read. | UPDATE after a one-line check, or DELETE |
| `liquids-framework-ruled.md` | The index says "gate FLOOD_ENGINE_CORRECTIONS_1"; repo CLAUDE.md "Doc rot" says those flood defects were fixed and closed at `747b0025`. | UPDATE: drop the gate clause |
| `owner-modes-bench-belt-afk.md` | Cites `queue/HUMAN.md` and `bench_mode.py`. UNMEASURED whether they still exist. | KEEP; verify the two paths |
| `world-remake-is-the-last-step.md` | Its second half ("0 tiles is not a defect", the tiles CSV is a record) is now verbatim in repo CLAUDE.md. | UPDATE: cut that half, keep the remake rule, the three carried artifacts and the "move the rule to what the breaker reads" lesson |
| `northstar-seed-with-guesses-dont-wait-for-human.md` | **0 bytes**, but indexed. | UPDATE: rewrite from the index line ("build provisional northstar work, human refines later; never self-validate"), or DELETE the file and its index line |
| `gimmesomeslack-flowworks-first.md` | Links to the dead `afk-night-2026-10-11…`. | UPDATE the link; KEEP while GSS/FlowWorks is the focus |

### 1.C Duplicates of CLAUDE.md, GIT_WORKFLOW.md or a skill: DELETE or MERGE

| file | already owned by | action |
|---|---|---|
| `worktrees-are-off.md` | repo CLAUDE.md "Git" (🔴 Worktrees are OFF) + `block_worktrees.py` | DELETE |
| `zsh-does-not-word-split-unquoted-vars.md` | repo CLAUDE.md "The shell here is zsh…" | DELETE |
| `no-unattended-flyer-live-testing.md` | repo CLAUDE.md "NEVER live-test a flyer's flight…" (a much fuller version) | DELETE |
| `remote-control-drops-are-logins.md` | `~/.claude/CLAUDE.md` Remote Control section + `claude-remote-control` skill | DELETE |
| `system-screenshot-always-ok.md` | repo CLAUDE.md Tools (`system_screenshot.py`, "always OK… no asking first") | DELETE |
| `rimworld-foundry-restart-authorization.md` | repo CLAUDE.md "a REBOOT is yours to call" + "Holding the bridge is blanket authorization"; launch details in `skills/rimworld-load-round/SKILL.md:365-375` | DELETE |
| `game-state-is-one-command-now.md` + `game-tool-said-flag-is-owner-quotes-only.md` | repo CLAUDE.md Tools `./game --said` | MERGE into one 3-line `game-said-flag.md` (the "self-initiated reboot uses bare form" half is not in CLAUDE.md) |
| `shortest-path-first-comments-after.md` | `~/.claude/CLAUDE.md` "Report the outcome, not the journey" | DELETE |
| `files-must-shrink-git-is-provenance.md` | repo CLAUDE.md "Inaccurate material is DELETED" | DELETE |
| `rimflow-close-sha-head-literal.md` (unindexed) | `skills/using-rimflow/SKILL.md:111-124` (still true: `src/RimMandrake/rimflow/cli.py:1694` stores `args.sha` verbatim) | DELETE |
| `rimflow-cli-quirks.md`, `rimflow-item-files-live-under-state-items-not-queue-items.md`, `rimflow-redesign-built-validated-leases-2026-10-07.md`, `rimflow-ledger-writes-are-local-not-auto-committed.md` | `skills/using-rimflow/SKILL.md` covers `--to`, `reassign`, `state/items`, leases, `implemented`, local ledger | DELETE (check each one's single unique line first) |
| `biome-mod-split-rulings-2026-09-23.md` | `design/RimMandrake/biome_mod_architecture.md` §7 Q12 to Q15 | DELETE |
| `proposals-suite-2026-08-31.md` (unindexed) | `design/Jawa/proposals/README.md:4` "COMPLETE (2026-09-02, 124 rows)" | DELETE |
| `belt-mode-fanout-minimum.md` | FOUNDRY.md | (see 1.B) |
| `fable-final-sitting-2026-08-31.md`, `fable-handoff-sprint-2026-08-30.md` (unindexed) | `design/Jawa/OPUS5_HANDOFF.md` (exists) | DELETE |
| `foundry-window-collision-202609130445.md` (unindexed) | one incident from before seat clones; repo CLAUDE.md now has the "`handoff.py` cannot tell two BENCH windows apart" trap | DELETE |
| `build-designs-its-own-verification.md` (unindexed) | DECIDE/BUILD seats retired 2026-08-27; CHARTER does not carry the rule (grep for "self-grad\|risk for speed" in `infrastructure/agents/CHARTER.md` gives 0) | MOVE the owner quote *"It's ok, I'll take the risk for speed and efficiency."* into FOUNDRY.md as "FOUNDRY writes its own verify", then DELETE |

**Not duplicates (KEEP; GIT_WORKFLOW lacks them).** `design/RimMandrake/GIT_WORKFLOW.md` has 0 hits for `2>/dev/null`, `update-index`, `index.lock`, `git rm` and `pathspec`. So the git-trap memories are the only home of those traps. **PROMOTE** them (see 1.E).

### 1.D Unindexed files (17): disposition

`ashkarr-audit-artifact` DELETE · `ashkarr-render-and-review-sheets` MOVE (the worldview.py command into `rimworld-ashkarr-map.md`; the sheet-persistence pattern into the global `review-sheets` skill) · `build-designs-its-own-verification` MOVE→FOUNDRY.md · `code-review-loop-paused-until-2026-09-23` DELETE · `dashboard-hub-artifact` KEEP + index (`infrastructure/dashboards/hub/` exists) · `fable-final-sitting-2026-08-31` DELETE · `fable-handoff-sprint-2026-08-30` DELETE · `foundry-window-collision-202609130445` DELETE · `gpt-consult-route-authorized` MERGE→`gpt-consult.md` · `one-subagent-max-rest-of-2026-10-07` DELETE · `parallel-subagents-must-not-all-drive-bridge` MERGE→`one-bridge-driver-at-a-time.md` · `proposals-suite-2026-08-31` DELETE · `rimflow-close-sha-head-literal` DELETE · `rimworld-tag-and-money-audit` MOVE into the docstring of `src/RimMandrake/Utils/weapon_tag_audit.py` (exists), then DELETE · `spring-cleaning-rulings-2026-09-23` KEEP + index (its "CLAUDE.md: regroup, cut nothing" ruling binds **this** cleaning pass); cut the "Tonight's work" paragraph and fix the drain count · `two-blind-arms-doc-audit` PROMOTE to a section of `deciding-and-superseding` or a new doc-audit skill · `worldmap-docs-pass-owed` → file as a rimflow item (owed owner work is not a memory, per `frozen-sheet-owed-lists-are-not-filed-work.md`), then DELETE.

### 1.E Merges inside the store (same lesson in several files)

| merge these | into | why |
|---|---|---|
| `one-bridge-driver-at-a-time`, `parallel-subagents-must-not-all-drive-bridge`, `never-assume-bridge-unavailable`, `keep-the-bridge-busy-multitask` | `bridge-discipline.md` | one subject: check `bridge who`, one driver, brief every live agent to `take`, never idle it |
| `subagents-must-run-commands-foreground`, `subagent-background-wait-deadlock-brief-line`, `background-agent-push-instruction-must-be-explicit-every-time`, `subagent-mark-clean-forgot-status-file`, `forks-act-on-the-whole-session-not-just-the-prompt`, `fork-inherits-seat-autonomy-overrides-task-scope` | **PROMOTE to the project skill `skills/efficient-subagents/`** as a "brief checklist" section (foreground only, explicit push line, check ledger + code_review files after, forks inherit autonomy); leave one pointer memory | these are cross-project, and every brief needs them |
| `git-add-never-suppress-stderr`, `hook-refusal-kills-whole-bash-call`, `git-commit-scope-is-the-whole-index-not-your-add`, `pathspec-commit-takes-worktree-not-index`, `rimworld-concurrent-agents-share-the-repo`, `shared-worktree-remeasure-before-acting` | **PROMOTE to a "Traps" section of `design/RimMandrake/GIT_WORKFLOW.md`** (the generic ones also to the global `git-efficiency` skill) | the owner named git as a recurring challenge; today those traps live only in memory, which subagents never load (see `world-remake-is-the-last-step.md`'s own root-cause paragraph) |
| `instruments-that-lie-with-a-number`, `instrument-read-the-generator-not-its-output`, `zero-rows-is-a-failure-not-a-footnote`, `strings-misses-dotnet-utf16-constants`, `rimworld-def-dump-blind-spots`, `def-dump-has-no-statbases`, `census-requested-vs-actual-kind`, `defname-denylist-misses-retextures`, `game-probe-reports-ignorance-as-silence` | **PROMOTE to the global `confident-wrong-numbers` skill** (the spring-cleaning ruling 2026-09-23 says "Route future 'instrument lied' lessons there"); keep RimWorld-specific instances as examples | 9 files of one failure class |
| `cherry-picker-cuts-invisible-to-dump`, `cherrypicker-has-three-cut-sources`, `cherrypicker-cut-name-is-any-type`, `cherry-picker-is-a-bridge-not-a-doctrine` | `cherry-picker.md` | one tool |
| `queue-items-decay-verify-first`, `check-for-later-items-before-acting-on-a-note`, `verify-open-questions-against-ledger`, `decay-sweep-closes-cross-seats` | `queue-hygiene.md` (or the `using-rimflow` skill) | the index already groups them on one line |
| `ask-with-question-cards`, `cards-simple-language-clear-trades`, `explain-fully-never-assume-he-remembers`, `offer-choices-not-unanswerable-questions` | **PROMOTE to the global `question-card` skill** | owner preferences that hold in every project |
| `map-state-is-disposable-debug`, `save-states-cover-live-testing` | `map-state-is-disposable-debug.md` | same ruling |
| `nvidia-free-tier-workforce`, `cheap-fanout-workers-are-live` | the global `nemotron-delegate` skill | cross-project; the Nemotron project has its own memory dir |
| `subagent-verdicts-are-evidence-not-findings`, `dramatic-findings-need-a-second-look`, `one-negative-is-not-a-mechanism`, `read-the-mechanism-before-filing-the-fix`, `flagging-a-wrong-thing-is-not-a-safeguard` | the global `verify-before-you-escalate` skill (one section "claims from one observation") | one discipline |

### 1.F Cross-project

- `owner-likes-70s-brown-palette.md`, `owner-identity-connected-accounts-are-stevens.md`, `owner-likes-powerful-tech.md` and the question-card cluster describe the **owner**, not RimMandrake. PROMOTE to `~/.claude/CLAUDE.md` (one line each) or to the `artifact-design` / `question-card` skills. Risk: none; other projects currently cannot see them.
- `-mnt-g-My-Drive-Personal-Rimworld/memory/` (GDrive-era RimWorld project; 2 files). DELETE the dir's memory, since its `jawa-patches-deploy-path.md` is an older variant of ours. Risk: none if that project is dead (Q3).
- `-mnt-d-Luke-dev-hestia/` vs `-mnt-d-Luke-dev-Hestia/`: case-variant duplicate project dirs. The lowercase one holds 2 lessons (`python-installs-need-break-system-packages`, `wsl-headed-browser-for-logins`) that are machine-wide WSL facts. PROMOTE those to `~/.claude/CLAUDE.md` "Machine" or the `wsl-windows-plumbing` skill; merge the dir into `Hestia`.
- 79 `-tmp-nsjudge-*` dirs: DELETE (debris; empty memory). Fix at the source: the northstar judge should run `claude -p` with a fixed cwd, or clean its dir. Risk: none.

## 2. Proposed consolidated MEMORY.md

Applies §1. Files marked **(NEW)** are the merge targets named in §1.B/§1.E; every other link was checked by script against the live memory dir (result line under the block). Down from 163 lines and 21.8 KB to 69 lines. Items promoted to skills leave the index entirely.

```markdown
# RimMandrake auto-memory (shared by BENCH and FOUNDRY windows)
Rules live in CLAUDE.md, the CHARTER and skills. This index holds owner preferences, rulings with no other home, and traps no skill owns yet.

## Windows, roles, modes
- [Two windows (redesign #4)](redesign-4-two-windows.md) — BENCH + FOUNDRY; role named in the first message; read CHARTER + your window file.
- [Modes: BENCH, BELT, AFK](owner-modes-bench-belt-afk.md) — BENCH suspends paperwork; "tell me only the exception".
- [BENCH work that turns live goes to FOUNDRY](bench-work-that-turns-live-goes-to-foundry.md)
- [Delegated picks name a stream](delegated-pick-names-a-stream-not-a-build.md)
- [Ask before large autonomous builds](ask-before-large-autonomous-builds.md)
- [Current priority: GSS/FlowWorks first](gimmesomeslack-flowworks-first.md) — owner 2026-10-11.
- [Model ladder](model-ladder.md) (NEW) — pointer only: Agent_Policy.md + global CLAUDE.md; always pass `model`.
- [GPT consult](gpt-consult.md) (NEW) — authorized; `gpt_consult.py`, defaults gpt-6.1-sol high.

## Talking to the owner
- [Owner is Lukas; connectors are Steven's](owner-identity-connected-accounts-are-stevens.md)
- [Biome sheets are a conversation loop](biome-sheets-are-a-conversation-loop.md)
- [Owner design loop: mockups first](owner-design-loop-mockups-first.md)
- [Owner likes powerful tech](owner-likes-powerful-tech.md) · [70s brown palette](owner-likes-70s-brown-palette.md)
- [Visuals reviewed in game](visuals-reviewed-in-game-not-browser-sheets.md) · [Check own graphics first](screenshot-own-graphics-before-human-review.md) · [Review tiers](review-tiers-and-review-environments.md)
- [Dashboard hub artifact](dashboard-hub-artifact.md)

## Game, bridge, live testing
- [Key paths](rimworld-key-paths.md) — logs/config only; CLAUDE.md owns the rest.
- [Minimal modlist regime](rimworld-minimal-modlist-regime.md) · [Batch game-up work](batch-game-up-work-before-restarting.md) · [Launch via Steam](launch-rimworld-via-steam-not-bare-exe.md)
- [Bridge discipline](bridge-discipline.md) (NEW) — check `bridge who`, one driver, brief every live agent to take, keep it busy.
- [Game --said flag](game-said-flag.md) (NEW) — his words only; self-initiated uses the bare form.
- [Map state is disposable](map-state-is-disposable-debug.md) — incl. save states cover live testing.
- [Bridge silent failures](rimworld-bridge-silent-failures.md) · [Click fails silently](rimbridge-click-fails-silently-use-real-os-click.md) · [Stale modal](stale-modal-blocks-every-later-call.md) · [Zombie game state](rimworld-zombie-game-state.md) · [Idle menu ≠ stall](idle-menu-looks-like-load-stall.md)
- [Generated map culled unless home](generated-map-culled-unless-home.md) · [Spawn many](spawn-many-for-bridge-tests.md) · [Kill hostiles on review maps](kill-hostiles-on-review-maps.md) · [Static boring test worlds](static-boring-test-worlds-upgrade-northstar-on-every-interference.md)
- [Visitors: record, remove, no redo](validation-visitors-record-remove-no-redo.md) · [Campaign bridge stays; 10% budget](campaign-bridge-stays-monitoring-off-10pct-budget.md)
- [Northstar: seed with guesses](northstar-seed-with-guesses-dont-wait-for-human.md) (rewrite: currently 0 bytes) · [Northstar tests economical](northstar-tests-must-be-economical.md) · [Live check must be proven needed](live-check-must-be-proven-needed.md)
- [Don't fullscreen the game](dont-fullscreen-or-focus-the-game.md) · [Fog: CAI strips it](real-fog-of-war-and-cai.md) · [JawaBench init is lazy](jawabench-init-line-is-lazy.md) · [Modcheck wave split](modcheck-wave-platform-split.md)

## Mods, defs, deploy
- [Deploy paths: mods AND .rid](jawa-patches-deploy-path.md) · [Deploy tool needs unique names](deploy-tool-mod-folders-must-be-unique-across-tiers.md) · [Texture binds by texPath](texture-binds-by-texpath-not-defname.md)
- [Silent def-loss traps](rimworld-custom-loader-li-trap.md) · [Inherited li unpatchable](inherited-list-items-cannot-be-patched-away.md) · [modExtension eats the def](modextension-missing-type-discards-def.md) · [Config errors invisible to validate_patch](config-errors-are-invisible-to-validate-patch.md)
- [Cherry Picker](cherry-picker.md) (NEW) — 4 files merged; a temporary bridge, three cut sources, any-type names.
- [ModsConfig describes the NEXT load](modsconfig-describes-the-next-load.md) · [Fingerprint, not timestamp](currency-fingerprint-not-timestamp.md) · [Three def data sources](rimworld-live-def-dump.md)
- [C# toolchain](rimworld-csharp-toolchain.md) · [Skills are symlinked](rimworld-modding-skill-is-user-installed.md) · [Galactic Empire is reskinned vanilla](galactic-empire-is-reskinned-vanilla.md) · [Ceiling fields](ceiling-fields-break-when-doubled.md)
- [Liquids framework ruled](liquids-framework-ruled.md) · [Bazaar ruled](bazaar-trade-window-ruled.md)

## World and biomes
- [Ash'karr map](rimworld-ashkarr-map.md) — incl. canonical start save and worldview.py. · [Local features, not repaints](ashkarr-local-features-not-repaints.md) · [Sun angle is the instrument](ashkarr-sun-angle-is-the-biome-instrument.md) · [Map representation ≠ measurement](map-representation-is-not-measurement.md) · [River direction](river-direction-is-riverdist.md)
- [World remake is the last step](world-remake-is-the-last-step.md) · [BiomeDef deletion needs live-tile check](biome-defname-deletion-must-check-live-tiles.md) · [Donor retirement: save check](donor-retirement-mod-check-not-save-check.md) · [Sheet "Owed" lists are not filed work](frozen-sheet-owed-lists-are-not-filed-work.md)
- [Spring-cleaning rulings 2026-09-23](spring-cleaning-rulings-2026-09-23.md) — CLAUDE.md: regroup, cut nothing.

## Art
- [No donor art kept](no-donor-art-kept.md) · [Prove art missing first](prove-art-missing-before-generating.md) · [Generated art is not disposable](generated-art-is-not-disposable-test-output.md) · [Loose PNG beats AssetBundle](loose-png-beats-assetbundle-donor-art.md)
- [Art downscale legibility](art-downscale-legibility-and-resolution.md) · [Material palettes](material-palettes.md) · [Colour with material](colour-with-material-not-paint.md) · [Render from live captures](render-offline-from-live-captures.md)
- [Artpipe reference= trap](artpipe-reference-triggers-reskin-validate.md) · [Artpipe daemon invisible to tasklist](artpipe-daemon-invisible-to-tasklist.md) · [Artist tile is the daemon](artist-tile-is-the-daemon-not-a-seat.md) · [Local imagegen parked](local-imagegen-track-parked.md)
- [Sheet enactment is one pass](sheet-enactment-one-pass.md) · [Followed sheet notes cleared](followed-sheet-notes-must-be-cleared.md) · [Creature art register retired](creature-art-register-retired-2026-09-11.md) (verify against art ledger)

## Claims, numbers, delegation (skills own the doctrine)
- [Queue hygiene](queue-hygiene.md) (NEW) — items decay; check later items, ledger, cross-seat closes.
- [Owner rules must be data](owner-rules-must-be-data-not-prose.md) · [Nothing learned is dropped](nothing-learned-is-dropped-for-space.md) · [Patch curated artifacts](patch-a-curated-artifact-never-reallocate.md) · [Generators lie in headers](generators-lie-in-their-headers.md) · [Verify what you displaced](verify-what-you-displaced.md)
- [Behavioural test one-route](behavioural-test-one-route-is-still-a-namelist.md) · [Patched collisions need the capture](patched-collisions-need-the-capture.md) · [Grade the answer](grade-the-answer-not-the-exit-code.md) · [First-party CLIs bridge subscriptions](first-party-clis-bridge-subscriptions.md)
- [Don't delete suspected duplicates](dont-delete-suspected-duplicates-mid-flight.md) · [Heavy ML kills the window](heavy-ml-in-seat-cgroup-kills-window.md) · [Warn hooks invisible to me](warn-hooks-are-invisible-to-me.md) · [Owner screenshots location](rimworld-screenshot-location.md)

## Shell and git (until promoted to GIT_WORKFLOW / wsl-windows-plumbing)
- [Git traps](git-traps.md) (NEW) — 6 files merged: no `2>/dev/null` on add, hook refusal kills the whole call, pathspec scope, worktree-vs-index, re-measure origin.
- [python.exe misreads WSL paths](windows-python-misreads-wsl-absolute-paths.md) · [drvfs stale reads](drvfs-stale-reads-mimic-revert.md) · [pkill -f kills my shell](pkill-f-matches-my-own-shell.md)
```

Link check (python, 2026-10-11): 102 links; 95 point at existing files (**0 missing**); 7 are the NEW merge targets. Block: 69 lines. Not indexed by design (to delete or promote per §1): the 15 expired orders, about 20 duplicates of CLAUDE.md or skills, and the clusters promoted to `efficient-subagents`, `confident-wrong-numbers`, `question-card`, `verify-before-you-escalate` and `nemotron-delegate`.


## 3. Lessons store (`infrastructure/state/lessons/`, 298 lessons)

**Method.** Each lesson is cited below as `[n]`, its line number in a sorted listing. (Regenerate with `ls infrastructure/state/lessons | grep -v README.md | nl`; `[1]` is `20260911T002159Z-UNSEATED-per-biome-fauna-cast-joins-two.md` and `[298]` is `20261011T142704Z-BENCH-full-list-log-budgets-are-blind.md`.) I read all 298. A python first-match keyword pass gave the coarse split (bridge/live 80, git 67, art 47, deploy 22, instruments 16, engine 15, subagents 14, owner-quote guard 12, rimflow 8, design 8, shell 3, other 6). I then hand-assigned the clusters below. Promotion check: a python token-presence pass over 502 skill/CLAUDE/agent/workflow docs (7.5 M chars; sanity probes `index.lock` 10, `block_forged_owner_said` 3, `Bridge token` 4 hits). It found 156 lessons ≥60% token-covered, 78 at 30-60% and 64 under 30%. Token presence only shows that a doc **mentions** the lesson's identifiers, not that it carries the lesson, so treat it as a ceiling on "promoted".

### 3.0 The headline: no curation since the shape changed

- `git log --since=2026-09-24 --diff-filter=D -- infrastructure/state/lessons/` returns **0 deletions**. Under `lessons.py`'s own contract (curation = deleting the file), **nothing has been curated since the 2026-09-23 drain**, and the one-file shape (`aefcca607`, 2026-10-02) has never been drained at all.
- Only **19 of 298** name a proposed home ("Proposed home:", "Home:", "Target skill"), even though README.md says "say which home you propose". 44 say filed, fixed or homed in any form.
- Inflow is 10-37 per day (37 on 2026-10-11). At zero outflow the inbox grows about 100 a week.

### 3.1 Clusters (hand-assigned), with home, duplicates and stale entries

| # | cluster | lessons | size | proposed home | duplicates / near-duplicates (MERGE) | stale (DELETE: fix landed or mechanism retired) |
|---|---|---|---|---|---|---|
| A | **Git landing from seat or scratch clones** | 3, 21, 24, 25, 30, 32, 37, 66, 85, 87, 89, 106, 107, 109, 111, 113, 114, 122, 127, 132, 134, 140, 147, 153, 154, 157, 159, 160, 168, 172, 173, 174, 230, 232, 233, 243, 245, 252, 258, 259, 260, 274-279, 288, 295, 296 | ~50 | a new **"Traps" section in `design/RimMandrake/GIT_WORKFLOW.md`**, plus generic items to the global `git-efficiency` skill | {30, 37, 127, 140} "pathspec commit refuses an untracked path / dir pathspec skips new files" (**4 copies**); {259, 295} "pre-push ledger hook judges HEAD before a compound command"; {252, 258, 260} dirty shared bench clone + `./publish` autostash; {122, 174} index.lock from a peer or a background reader: retry, never rm; {243, 288} land.sh usage | **Worktrees are OFF since 2026-10-02:** 31, 66, 106, 154, 157, 159, 160, 111 (worktree mechanics; `block_worktrees.py` refuses them now). **`shared_sync.py` has no caller** in `src/`, `skills/`, `.claude/`, CLAUDE.md or GIT_WORKFLOW.md (last touched 2026-10-02), so 109, 114, 132, 134, 147, 153 describe a dead tool. 32 (fixed: health publisher refuses mid-rebase). 172's mirror half: `D:\Luke\dev\RimMandrake` has no `.git` now. 278 fixed `dcb08c809`. **And file `shared_sync.py` as a DEAD-FILE candidate.** |
| B | **Owner-quote guard (`block_forged_owner_said.py`) refuses genuine quotes** | 22, 26, 36, 40, 81, 124, 137, 169, 197, 251, 257 (+154 second half) | 12 | ONE paragraph in `skills/using-rimflow/SKILL.md` (it mentions owner-said 11 times but has 0 hits for "mid-turn" or "/clear") | **All 12 are one lesson**: the guard cannot see (a) the `/clear`-opened first message, (b) a mid-turn message, (c) question-card free text, (d) a quote ending in `?` or stitched from several answers; its regex also fires on the flag's spelling in prose. Exit: drop the flag, record under your own seat, quote him in the note text. | none stale. **Also PROMOTE to a tool item:** 12 refusals in 17 days is a guard defect, not an agent habit. Teach it to read mid-turn and card-typed text. |
| C | **Subagent briefing** | 16, 23, 38, 78, 105, 112, 118, 145, 177, 181, 182, 231, 248, 253, 297 | 15 | the project skill `skills/efficient-subagents/`, as a single **brief checklist** | {38, 105, 145} background-wait deadlock (**3 copies**, plus 2 memories); {23, 118} fork/child-spawn misbehaviour; {182, 248, 253} "verify a subagent's claimed result" | 16 is now verbatim in repo CLAUDE.md ("the `Agent` tool refuses without an explicit `model`"): DELETE |
| D | **Full-list live proofs and validation harnesses** (the telemetry cluster) | 6, 7, 8, 9, 167, 186, 187, 188, 189, 201, 209, 239, 261, 263, 264, 266, 267, 268, 269, 280, 281, 282, 291, 292, 293, 294, 298 | ~27 | **a NEW skill: `live-proof-harness`** (see 3.3) | {189, 298} Verse.Log stops at 10,000 messages (298 is the fuller one; MERGE 189 into it); {263, 298} the bridge journal ring hides early lines; {280, 281} full-list map is not calm | 201 is a one-off confession; keep its rule only ("never hand-edit a result JSON") |
| E | **Bridge tool contracts** (param names, defaults, silent no-ops) | 13, 35, 59, 60, 62, 63, 64, 65, 70, 72, 82, 83, 135, 136, 149, 151, 152, 163, 164, 165, 166, 190, 191, 192, 194, 195, 222, 225, 227, 242, 255, 262, 270, 271, 272 | ~35 | `skills/rimbridge/references/traps.md` as a **per-tool table**; better, fix in the client's declared-param check and tool docstrings | {164, 13} damage does not kill → use incapacitate or a `dead:true` loop; {70, 72} current-map/world-UI drift | Measured gaps (0 skill files mention): `dismiss_letter`/`letterId` [65], `destroy_bulk` [166], `name_colony` [192], `StopLoggingAtMessageCount` [189/298]. These are **unpromoted**. |
| F | **Map culling and fixtures** | 71, 150, 161 (+ memory `generated-map-culled-unless-home.md`) | 3 | `skills/rimworld-debug-testing` | **all three plus the memory are one lesson** | none |
| G | **Player.log "Bridge token" false-ready after relaunch** | 39, 56, 265 (+200 launch timeout, 239 log silence ≠ hang) | 5 | `skills/rimworld-load-round` | **39, 56 and 265 are the same lesson, filed three times** (09-24, 09-25, 10-11), which shows it was never promoted | none |
| H | **Deploy, modlist and DLL drift** | 11, 12, 29, 51, 54, 67, 74, 77, 102, 104, 116, 117, 126, 143, 144, 155, 180, 184, 220, 223, 229, 241, 253 | ~23 | `skills/rimworld-deploy` and `skills/rimworld-start-prep` | {74, 143, 220} the mod list was not restored after a tier swap (**3 copies**); {184, 223} the composed biomes deploy is a separate command; {104, 117, 229} a stale DLL fails silently; {11, 67} a full-tree deploy under-reports | 241 is now repo CLAUDE.md verbatim ("A composed member … has no packageId at runtime"): DELETE. 155 is superseded by 241/CLAUDE.md. |
| I | **Artpipe, art ledger, review sheets** | 34, 43, 49, 52, 55, 84, 97, 99, 100, 101, 115, 121, 146, 196, 198, 203, 205, 206, 207, 210, 212, 218, 219, 236, 237, 238, 240, 246, 247, 249, 250, 256, 283, 284, 287 | ~35 | split out of `generating-rimworld-sprites` into a NEW **`artpipe-operations`** skill (daemon, job validity, queue, enact, sheets); sheet UI items to the global `review-sheets` skill | {34, 115, 207} "camera/facing words in a prompt → `bad_job_file`, and the queue LOOKS done" (**3 copies**); {219, 240} followed sheet notes (+ memory `followed-sheet-notes-must-be-cleared.md`) | fixed: 247 (`ab6bed31a`), 249 (`7c623ab47`), 287 (refresh_sheets fix). Keep the general rule from each in one line, then DELETE. |
| J | **Owner art and naming rulings filed as lessons** | 120, 130, 208, 234 | 4 | **MOVE to `infrastructure/state/art_rulings/`** (art) and the naming doc (208, the Abyss sibilant-name family). Per memory `owner-rules-must-be-data-not-prose.md`, a generator never reads the lesson inbox. | none | none. **These are the highest-risk unpromoted lessons:** verbatim owner rulings that no generator reads. |
| K | **RimWorld engine and def facts** | 57, 61, 68, 86, 88, 90, 91, 92, 119, 128, 185, 193, 226, 244, 245, 254, 290 | 17 | `skills/rimworld-modding` (a `references/engine-facts.md`); 185 to `skills/rimworld-quests` validator (its own text says so) | none | none. All RimSage-measured, durable, and low-coverage in the token pass (8 of 15 in the engine bucket under 30%). |
| L | **Instruments and censuses** | 1, 2, 4, 5, 15, 20, 44, 45, 46, 94, 95, 96, 99, 100, 103, 125, 129, 139, 148, 204, 217, 285, 286 | ~23 | the global `confident-wrong-numbers` skill (per the 2026-09-23 ruling), RimMandrake specifics as examples | {129, 139} a biome under two names; {45, 46} Wookieepedia search controls | **20, 94, 95, 96 each say "(filed: CLAUDE.md)" and are in repo CLAUDE.md:** DELETE. 19 likewise (Wookieepedia API is in CLAUDE.md). |
| M | **rimflow and handoff tooling** | 33, 48, 53, 75, 79, 108, 131, 156, 168, 178, 228 | 11 | `skills/using-rimflow`, the `handoff` skill | 156 duplicates memory `rimflow-close-sha-head-literal.md` and `using-rimflow` §close | 33 (a note that the skill was corrected): DELETE |
| N | **GPT / Codex consult** | 138, 162, 170, 177, 179, 289 | 6 | the docstring of `src/RimMandrake/Utils/gpt_consult.py`, or a small `gpt-consult` skill (memory says none exists) | {162, 170} | 162 says `-m gpt-5.6-sol`; superseded by 170 and the script default `gpt-6.1-sol`: DELETE |
| O | **Shell / OS / WSL / processes** | 10, 18, 42, 98, 133, 141, 142, 183, 202, 211, 212, 216, 235, 274 | 14 | **PROMOTE out of the project** to the global `wsl-windows-plumbing` skill (named in `~/.claude/CLAUDE.md`): cross-project machine facts | {183 + memory `pkill-f-matches-my-own-shell.md`}; {211, 216, 235, 274} /tmp, tmpfs, OOM and clone sizing (235 is the enforced mechanism; 216 is subsumed) | 216 is subsumed by 235 (hooks enforce it). 18 and 133 are Mac-only, so tag them MACBENCH. |
| P | **Flyer / ambient-visual verification** | 47, 69, 73 | 3 | repo CLAUDE.md already holds the flyer ban | 69 is superseded by 73 (73's own text says so) | 47 and 69: DELETE. **73 is an owner ruling verbatim** (*"stop this live testing. It's wasting time…"*) and repo CLAUDE.md has 0 hits for "stop this live testing". MOVE it into the CLAUDE.md flyer section or `debug_process.md` before deleting. |
| Q | **Design-content checks** | 27, 28, 41, 50, 76, 175 | 6 | the biome review-sitting checklist (`design/RimMandrake/biome_mod_architecture.md`, or the review-sheet template) | none | none |
| R | **Leftovers** | 17 (question-card header limit: in CLAUDE.md, DELETE), 176 (card length: to the `question-card` skill), 199 (profile per-call first: to `rimbridge/references/performance.md`), 213, 214, 215 (`rimworld-live-review` 8d already, per its own text: DELETE) | 6 | as stated | | |

**Counts.** The duplicate sets above hold **about 45 lessons collapsing to about 15**. Stale or already-promoted lessons I can name with evidence: **at least 40** (A 15, C 1, H 2, I 3, L 5, M 1, N 1, P 2, R 2, plus the 8 worktree ones in A). A curation pass that only merges duplicates and deletes the proven-stale ones takes the inbox from **298 to about 225 without writing a single skill line.**

### 3.2 Never promoted anywhere (evidence-backed)

The token pass flags 64 lessons under 30% identifier coverage. By cluster: art 15, git 9, engine 8, bridge/live 8, design 4, rimflow 2, subagent 2, other 4. Read by hand, the ones that matter most and have **no** home today:

1. **Owner rulings sitting only in the inbox:** [120] realistic not cartoonish, [130] palette variety, [208] the sibilant-name family and the four yellow eyes, [234] no geometric placeholder ever selectable, [73] "stop this live testing". A generator or sheet builder never reads `lessons/`.
2. **Cluster B (owner-quote guard):** 12 lessons, 0 mentions of mid-turn or `/clear` in `using-rimflow`.
3. **Cluster G ("Bridge token" false-ready):** filed 3 times, which is itself the evidence it never landed.
4. **Cluster D (live-proof harness):** Verse.Log 10k cap (0 skill hits for `StopLoggingAtMessageCount`), the bridge journal ring, tick-vs-wall-time caches, `len(env.running)` tier truth, live perf vs modelled perf.
5. **Cluster K engine facts:** 17 decompiler-measured facts, none in `rimworld-modding`.
6. **Bridge contracts with 0 skill hits:** `dismiss_letter`/`letterId`, `destroy_bulk`, `name_colony`.

### 3.3 Clusters big enough to be a skill, or a section of one

| proposal | from | why |
|---|---|---|
| **NEW skill `live-proof-harness`** (or a large new section of `rimworld-debug-testing`) | D (27) + G (5) + F (3) + parts of E | Largest unhomed cluster, and it is exactly the owner's telemetry ask: every lesson is "the instrument went blind and read as PASS" (log cap, ring buffer, stale Player.log, tier mislabel, modelled perf, map not calm). Its spine: a run-start checklist (Log.Clear + sentinel, `RunInBackground`, calm the map, assert `len(env.running)`, `name_colony`), a run-end checklist (sentinel read back, lost-entry count, UNMEASURED not PASS), and a perf rule (time the production function live with `jawa/map_comp_timing`). |
| **NEW skill `artpipe-operations`**, split from `generating-rimworld-sprites` | I (35) | job validity, daemon restart after code change, queue-vs-renders, enact/ingest/sheet staleness. The sprite skill stays about the art itself. |
| **"Traps" section in `GIT_WORKFLOW.md`** + the global `git-efficiency` skill | A (~50, after deleting about 15 stale: about 35) | the owner named git as a recurring challenge; the six git-trap memories (§1.E) join it |
| **`efficient-subagents` brief checklist** | C (15) + 6 memories | one list pasted into every brief: foreground only ("any command you background", verbatim), no sub-spawning, explicit push/no-push line, verify claimed results via `git status`, commit the ledger and code_review files, never close on a failed live verify |
| **`rimbridge/references/tool-contracts.md`** (per-tool table) | E (35) | one row per tool: param names, defaults (`dryRun=true`, `waitTicks`), silent failure shape, verified fallback |
| **`rimworld-modding/references/engine-facts.md`** | K (17) | durable RimSage-measured engine facts |
| **PROMOTE out of the project:** global `wsl-windows-plumbing` | O (14) | machine facts that bite every project on Archmagi |

## 4. Is lessons.py's one-file-per-lesson shape working? Cadence and "drained"

**Filing works, curation does not.** The shape solved the problem it was built for: 298 files, no merge conflicts, O_EXCL creation, 4 seats filing concurrently. But it has made the inbox write-only:

- 0 curation deletions in 19 days (§3.0), while inflow ran 10-37 a day.
- The **same lesson gets filed again** because nobody reads the inbox before filing: Bridge-token ×3, pathspec ×4, background-wait ×3 (+2 memories), owner-quote guard ×12, camera words ×3.
- Only 19 of 298 name a home. With no home, the curation pass has to re-derive every one.
- Lessons and auto-memory now **overlap**: at least 8 lesson/memory pairs say the same thing (followed sheet notes, close --sha, background wait, map culling, pkill, verify-open-questions, ...). Agents choose between the two stores ad hoc. Memory loads into one window only and subagents never see it (`world-remake-is-the-last-step.md` names this as root cause).

**Proposed changes to `src/RimMandrake/Utils/lessons.py` (small):**
1. `add` **requires `--home <skill|doc|NONE>`** and prints the 3 most similar existing lessons (simple token overlap over the filenames and first line) before writing. That cuts refiling.
2. `stats`: count per home and age buckets; the oldest undrained lesson's age is the health number.
3. `fold <file> --into <path> [--sha]` deletes the lesson file and appends one line to `infrastructure/state/lessons/FOLDED.log` (`date, lesson slug, destination, sha`), so "never promoted" becomes measurable instead of inferred.
4. `render` groups by `--home`.

**Weekly cadence (Sunday, inside the existing weekly cleaning):**
1. `lessons.py stats`, then fan out one sonnet agent per home cluster. Each folds its lessons into the named skill or doc (proposals as diffs for the curation pass, per policy) and runs `lessons.py fold`.
2. Duplicates: keep the newest or fullest, delete the rest.
3. Stale: delete when the fix sha or the mechanism retirement is cited.
4. Owner rulings found in the inbox go to their DATA home (art_rulings, design doc) the **same day**, not weekly.
5. The same pass does the memory sweep: delete date-expired memories and run the index/orphan script from §0.

**Definition of "drained":** (a) no lesson older than 7 days remains; (b) every remaining lesson has a `home:`; (c) 0 lessons duplicate one another or a skill/CLAUDE.md line (spot-checked); (d) owner-ruling lessons count = 0. "Drained" is **not** "the count is small": the 2026-09-23 drain was declared at 11 homeless (or 29; the two records disagree, §0), and 19 days later the inbox is 298.

## Top 10 actions, ranked by value

| # | action | target | type | why | risk |
|---|---|---|---|---|---|
| 1 | Move the 5 owner rulings stranded in the inbox ([120], [130], [208], [234], [73]) to their data homes | `infrastructure/state/art_rulings/`, the naming doc, the CLAUDE.md flyer section | MOVE | verbatim owner rulings that no generator reads; the "rediscovered rule" failure in the making | low; quotes are copied verbatim |
| 2 | Delete 15 expired session-order memories (§1.A), and adopt "no dated session orders as memory" | memory dir | DELETE + rule | 10% of index lines are dead orders that contradict each other | none (tar the dir first, since it has no git) |
| 3 | Fix the model-ladder contradiction: one pointer memory; resolve global-CLAUDE vs Agent_Policy on haiku | `model-ladder-opus-sonnet-haiku.md`, `fan-out-cheap-by-default.md`, `~/.claude/CLAUDE.md`, `infrastructure/agents/Agent_Policy.md` | MERGE / UPDATE | three sources give three answers on haiku | low |
| 4 | Create the `live-proof-harness` skill from clusters D+G+F (about 35 lessons) | `skills/live-proof-harness/` | PROMOTE | largest unhomed cluster; it is the owner's telemetry ask; it stops PASS-on-blind-instrument | medium: a new skill must trigger; use skill-creator evals |
| 5 | Git "Traps" section from cluster A + 6 git memories; delete ~15 stale worktree/shared_sync lessons; file `shared_sync.py` as dead | `design/RimMandrake/GIT_WORKFLOW.md` | PROMOTE / DELETE | the owner named git as recurring; today the traps live only where subagents cannot see them | low |
| 6 | Collapse the 12 owner-quote-guard lessons into one `using-rimflow` paragraph and file a guard fix (read mid-turn and card-typed text) | `skills/using-rimflow/SKILL.md`, `.claude/hooks/block_forged_owner_said.py` (item) | MERGE + item | 12 refusals in 17 days | low |
| 7 | `efficient-subagents` brief checklist from cluster C + 6 subagent memories | `skills/efficient-subagents/SKILL.md` | PROMOTE | background-wait deadlock filed 5 times across two stores | low |
| 8 | Add `--home`, `stats`, `fold` and a dedupe hint to `lessons.py`; adopt the weekly cadence and the "drained" definition (§4) | `src/RimMandrake/Utils/lessons.py`, `infrastructure/state/lessons/README.md` | UPDATE | 0 curation in 19 days; refiling is common | low |
| 9 | Apply the §1.B/§1.C corrections and merges, replace MEMORY.md with §2, fix the empty file and the 17 unindexed files | memory dir | UPDATE / DELETE / MERGE | 21.8 KB index down to 8.3 KB (measured); every line true and resolvable | low |
| 10 | Promote cross-project items out: shell/WSL lessons (cluster O) and owner-preference memories to global; delete `-tmp-nsjudge-*` (79 dirs) and the `Personal-Rimworld` memory | `~/.claude/` (first symlink `~/dev/Hestia/.claude/skills/wsl-windows-plumbing` into `~/.claude/skills/`) | PROMOTE / DELETE | other projects on this machine hit the same traps | none |

## Questions only the owner can answer

1. **Session-scoped orders** ("AFK tonight, keep N subagents"). Where should they live?
   (a) Nowhere persistent: the session only, and gone at the next session. (b) One overwritten `current-standing-order.md` memory carrying an expiry line. (c) A `MODE`-style state file the seats read, like `infrastructure/state/MODE`.
2. **Auto-memory vs. the lessons inbox.** Which one is the home for agent-learned traps?
   (a) Lessons only; auto-memory keeps owner preferences and pointers (subagents never see memory). (b) Both, deduped weekly. (c) Auto-memory only; retire the inbox.
3. **The GDrive-era `Personal-Rimworld` project and the lowercase `hestia` project dirs.** Are they dead?
   (a) Yes, delete both memory dirs. (b) Keep `hestia`, merge it into `Hestia`. (c) Keep both.
4. **New skills.** Which do you want created this cycle?
   (a) `live-proof-harness` only. (b) `live-proof-harness` + `artpipe-operations`. (c) Neither: add sections to the existing `rimworld-debug-testing` and `generating-rimworld-sprites` instead.
5. **The memory directory has no git history.** Should a delete there be preceded by a backup?
   (a) Yes: tar to `~/.claude/backups/` before each weekly cleaning. (b) Put the memory dir under git (a private repo). (c) No backup; deletions are fine.
