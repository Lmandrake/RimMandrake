# 02 — CLAUDE.md levels and agent specs (audit 2026-10-11)

Auditor dimension: every CLAUDE.md level, the agent specs, `.claude/settings.json` and `.claude/hooks/`.
Everything below was measured by a script run in this pass unless it is marked UNMEASURED.

## 1. Size table and auto-load cost

MEASURED with a python byte and line count. Tokens are estimated as bytes/4, which undercounts the emoji-heavy files. No real tokenizer was run, so the token figures are an ESTIMATE.

| file | bytes | lines | ~tokens | auto-loaded in a bench session? |
|---|---:|---:|---:|---|
| `~/.claude/CLAUDE.md` (GENERATED from `~/dev/Lodestar/claude/global/*.md`) | 26,520 | 422 | 6.6k | YES, in every session and every subagent |
| `/home/mandrake/rm/bench/CLAUDE.md` | **73,114** | 980 | **18.3k** | YES, in every session and every subagent |
| `~/.claude/projects/-home-mandrake-rm-bench/memory/MEMORY.md` | 22,144 | 163 | 5.5k | YES (all 163 lines; it was delivered to this subagent too) |
| `~/dev/Lodestar/CLAUDE.md` | 32,293 | 465 | 8.1k | no (only when cwd is in Lodestar) |
| `src/RimMandrake/Utils/artpipe/AGENTS.md` | 5,719 | 93 | 1.4k | no (Codex) |
| `infrastructure/agents/CHARTER.md` | 11,311 | 184 | 2.8k | read on instruction (every seat) |
| `infrastructure/agents/BENCH.md` | 3,591 | 63 | 0.9k | read on instruction |
| `infrastructure/agents/FOUNDRY.md` | 11,523 | 182 | 2.9k | read on instruction |
| `infrastructure/agents/Agent_Policy.md` | 9,602 | 146 | 2.4k | read on instruction |
| `infrastructure/agents/{POLICY,BUILD,CHECK,DECIDE,REP}.md` | 230–473 each | 5–8 | — | tombstones since 2026-08-27 |
| `infrastructure/agents/CODEX_PROPOSAL_*.md` (3 files) | 70,619 total | 1,524 | 17.7k | no; 1–2 inbound refs each |
| `.claude/settings.json` | 15,732 | 614 | — | harness |
| `.claude/hooks/*.py` (46 files) | 413,402 total | — | — | harness |

**Per-session auto-load ≈ 121.8 KB ≈ 30k tokens (ESTIMATE),** paid by every BENCH/FOUNDRY window and every subagent spawned from one. The project CLAUDE.md is 60% of it.

**Growth (MEASURED from git history):** project CLAUDE.md was 6,251 B on 2026-09-01, 15,255 B on 2026-09-15, 74,098 B on 2026-10-01 and is 73,114 B today. That is **12× in one month**, across 139 commits. `CHARTER.md` opens with "This file does not grow: a new line must delete the line it replaces". It was 5,954 B at adoption and is 11,311 B now (**1.9×**).

## 2. Redundancy

Hit counts come from a regex sweep across global, project, CHARTER, BENCH, FOUNDRY, Agent_Policy, Lodestar, GIT_WORKFLOW, 198 memory files, 78 SKILL.md files and 299 lessons (the script is at `<scratchpad>/dup.py`).

| rule | where it is stated now | single home (KEEP) | elsewhere becomes |
|---|---|---|---|
| Correctness outranks seat ownership (owner 2026-09-19, verbatim quote) | full section in project CLAUDE.md L741-760, full section in CHARTER L90-110, bullets in BENCH and FOUNDRY | **CHARTER** (it is process; CHARTER already cites the hook) | CLAUDE.md: one line with the verbatim quote plus a pointer. BENCH/FOUNDRY: delete the bullet (they already "read CHARTER") |
| Inaccurate material is DELETED (owner 2026-09-09) | CLAUDE.md L761, CHARTER "Rules and lessons" and the Correctness section | **CHARTER** | CLAUDE.md: one line |
| How we debug / debug_process.md (owner 2026-10-01) | CLAUDE.md L13, CHARTER L138, BENCH, FOUNDRY | **`design/RimMandrake/debug_process.md`** | one pointer line in CHARTER; delete it from CLAUDE.md, BENCH and FOUNDRY. CHARTER's copy is also FALSE (see §4) |
| Worktrees OFF (owner 2026-10-02) | CLAUDE.md Git, CHARTER Git, GIT_WORKFLOW, 10 memory files, 16 lessons, hook `block_worktrees.py` | **hook + GIT_WORKFLOW.md** | CLAUDE.md: half a line. Delete the CHARTER paragraph. Memory: one file |
| Commit explicit paths, never `git add -A`, push at once | global "Commit and push", CLAUDE.md Git, CHARTER Git, GIT_WORKFLOW, 4 memory files, 3 skills, hook `block_blanket_git_stage.py` | **global** (the general rule) + **GIT_WORKFLOW.md** (the repo mechanics) + hook | CLAUDE.md Git section shrinks to 4 lines of pointers. CHARTER says CLAUDE.md owns git, and CLAUDE.md points at GIT_WORKFLOW, so there are three hops for one rule |
| `./game --said` | global (RUN IT YOURSELF), CLAUDE.md Tools, CHARTER, BENCH, FOUNDRY, 4 memory files | **CHARTER "Game state and the bridge"** | Tools table keeps its one row. Delete it from BENCH and FOUNDRY |
| Bridge one-driver / take / release | CLAUDE.md L939-973 (2.1 KB), CHARTER, FOUNDRY, 3 memory files, 2 skills | **CLAUDE.md** (CHARTER already defers to it), cut to 6 lines; mechanics go to the `rimbridge` skill | CHARTER: pointer only (already the case) |
| No paste / run it yourself / full native path | global ×2 sections, CLAUDE.md (bridge section tail plus a Stop hook), CHARTER Posture item 6, BENCH, 8 skills | **global** | delete the CLAUDE.md L972-973 restatement; CHARTER keeps the one Posture clause |
| HANDOFF READY ritual | global (2 sections), CHARTER Windows (long, with Mac-laptop history), FOUNDRY L67-108, handoff skill | **handoff skill + global pointer** | CHARTER: 2 lines. FOUNDRY: delete the duplicate ritual and keep only the wave-boundary trigger |
| Model ladder | global (stale render, see §4), Agent_Policy, `~/dev/Lodestar/claude/global/45-subagents.md`, MEMORY.md line "Haiku OS searches only", Lodestar CLAUDE.md §6 | **`45-subagents.md`** (Agent_Policy itself names it the source of truth) plus Agent_Policy for seat policy only | MEMORY.md line: delete or repoint (it says the OPPOSITE of the current ruling). Agent_Policy L17-56: cut the 40-line haiku correction narrative to 3 lines |
| Never scan, use `measure` | CLAUDE.md, hook `block_blind_scan.py`, skill `measuring-large-artifacts` | **hook + skill** | CLAUDE.md: one line |
| Biome with zero tiles is not a defect, and the tiles CSV is a record | CLAUDE.md L35-79 (2.8 KB), 4+5 memory files, 2 skills | **CLAUDE.md** (it is an owner ruling said repeatedly), cut to 5 lines | memory: merge into one file |
| Flyer: never live-test unattended | CLAUDE.md L602-730 (7.9 KB), 2 memory files, 1 skill, 2 lessons | **CLAUDE.md**: the 3-line rule with the verbatim quote | animation mechanics go to the skill (§3) |
| Question-card click is not owner-said | CLAUDE.md, FOUNDRY, 2 memory files, using-rimflow skill, hook | **hook + using-rimflow skill** | CLAUDE.md: one line |
| Cold-load time | CLAUDE.md "~15 min, MEASURED", CHARTER "~25 min", load-round skill "~25 minutes" | **CLAUDE.md engine facts** | fix CHARTER and the skill (§4) |

## 3. MOVE list (project CLAUDE.md → docs)

Section byte sizes were measured by heading. The target is ≤ 29 KB (40% of 73 KB). Every owner ruling keeps its verbatim quote in the one-line rule left behind, and the full prose moves with git as provenance.

| CLAUDE.md lines (bytes) | content | action | destination | one-line rule left behind | risk if wrong |
|---|---|---|---|---|---|
| 126-245 (10,210) "Instruments that return a confident wrong number" | 17 trap bullets (ledger `id` vs `item`, `get_defs` string, CRLF, `grep -c`, northstar dict, `ls\|wc` zero, zsh word-split, ModsConfig `<li>`, About.xml sweep, existence≠identity, `*south*` mask glob, RM_ twin patch rosters, canon_references ls, briefed numbers) | MOVE + PROMOTE | general shell traps (CRLF, `grep -c`, `ls\|wc`, zsh, `grep -F` wrap, existence-vs-identity, briefed numbers) go to the global `~/.claude/skills/confident-wrong-numbers`. RimWorld-specific ones go to new `infrastructure/state/facts/instrument_traps.md`, linked from `measuring-large-artifacts` | "A count that is round, zero or alarming is a query bug until a sanity probe proves the instrument can see; traps: `facts/instrument_traps.md`." | a session hits a trap it would have read about. The hook already enforces the worst one (blind scan) |
| 246-292 (4,254) "Tools with surprising side effects" | Player.log first exception, hooks added mid-session, Agent 600 s death, two PreToolUse gates, card label, csproj compile list, handoff.py two BENCH windows, `modcheck run` rewrites ModsConfig | MOVE | `facts/tool_traps.md`. Agent-600s goes to the global `efficient-subagents` skill. csproj goes to the `rimworld-modding` skill | keep 2 lines: "`modcheck run` REWRITES ModsConfig (expensive list)." and "Read the FIRST exception in Player.log." | low |
| 293-388 (8,574) "Design process and biome/roster rulings" | search-before-filing, greatbole 3 defs, one-biome-per-animal + evictions stopped, sea floor + catch, ship-only diving, animalDensity, sheet cut scoping | MOVE | `design/RimMandrake/biome_rulings.md` (new, holding the verbatim quotes) or the existing `biome_mod_architecture.md` §7 | five one-liners: "Search `src/` before filing or designing; we keep having built it." · "One biome per animal unless there is an in-game reason; evictions STOPPED, per-biome sittings only ('This is a human review process issue')." · "Sea species: floor def + catch def; 'ship or nothing'; ship flies to `RM_SeabedLayer`." · "Every BiomeDef with a roster sets `animalDensity`." · "A sheet's `cut` is scoped to that sheet's biome." | medium: these are rulings, so the quotes must survive verbatim in the destination |
| 602-700 (≈6,900 of the 7,925) flyer animation mechanics | Locust XML, flip-book PawnKindDef XML, Spastic reversal narrative, FIREHAWK history | MOVE + DELETE stale | `skills/rimworld-sprite-facings` (already cites flight) or a new `rimworld-flight` skill | keep: "If it flies in fiction it flies in game ('we make flyers flyers when we can'). Flight is the `MaxFlightTime` STAT. Animation is a whole-body flip-book. NEVER live-test flight unattended ('For the third time…')." | low; the skill is read before touching a flyer |
| 708-730 (≈1,700) DLC rulings | filed under the FLYER heading by accident | MOVE within the file | own `## Every DLC is assumed — owner 2026-09-25/26` section, 3 lines with both quotes | — | none |
| 404-450 (4,085) "North-star validation state" | counts and states, much of it stale (§4) | DELETE the state and MOVE the rule | state belongs to `modcheck floor --all`, never prose. The hash rule goes to `design/RimMandrake/debug_process.md` or the modcheck README | "North-star hash covers the whole section: correct false prose, then re-validate on his word the same sitting ('Change no code — you just re-validate when prose is corrected')." | low; the instrument exists |
| 451-476 (1,976) Patch/def behaviour | MayRequire-on-Operation incident narrative | MOVE | `skills/rimworld-modding` (5 skills and 6 lessons already cover MayRequire) | "`MayRequire` on a top-level `<Operation>` is ignored; guard with FindMod/Conditional. A composed member id never loads." | low |
| 82-125 (3,365) Engine facts | cold load, ModsConfig path, RimSage-on-Mac, Plant TickLong, Wookieepedia API | PARTIAL MOVE | Plant TickLong goes to `rimworld-modding`. Wookieepedia goes to `rimworld-canon-references`. RimSage-on-Mac goes to the Lodestar machine file for the laptop | keep the 4 lines about the game folder, cold load, ModsConfig and "never guess a defName" | low |
| 477-504 (1,834) LLM via `claude -p` | spec narrative | MOVE | `design/RimMandrake/llm_ingame_wiring_spec.md` §1 | "In-game LLM = `claude -p` subprocess, never an API key ('…without any API key')." | low |
| 532-564 (2,659) Star Wars naming Q11a | already ruled in `biome_mod_architecture.md` §7 Q11a | MERGE | that doc | 2 lines plus the quote | low |
| 772-786 (2,581) Git | duplicate of GIT_WORKFLOW | MERGE | `design/RimMandrake/GIT_WORKFLOW.md` | 4 lines | low; hooks enforce most of it |
| 787-819 (2,082) Code review | full procedure | MOVE | the docstring and README of `code_review_status.py` | "Every file is DIRTY until `code_review_status.py check` says CLEAN." | low |
| 910-938 (1,868) existing art check | incident narrative | MOVE | `art_ledger_design_2026-10-04.md` and `generating-rimworld-sprites` | "Search `artpipe_state.py find` and sheet `.decisions.json` before queuing art." | low |
| 939-973 (2,143) Bridge | | TRIM | `rimbridge` skill | 6 lines | low |
| 389-403 (990) Doc rot | narrative examples | DELETE the examples | — | "A gate cited by NAME outlives its item; check the item's state." | none |
| 505-522 pit, 523-531 heat, 565-601, 731-771, 820-909 | owner rulings and pointers | KEEP, tightened | — | — | — |

**Projected size:** about 24–27 KB (33–37%). That is ESTIMATED by summing the kept one-liners plus the untouched short sections. It was not drafted.

## 4. Stale / false content

**Path check (scripted):** 114 path-like tokens were extracted from project CLAUDE.md. After removing noise (globs, git refspecs, flags, `…/` placeholders), these are the real misses:

| cited path | status |
|---|---|
| `~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md` (CLAUDE.md flyer section, "read it before touching any flyer again") | **MISSING.** Not in `~/Desktop`, not on `C:\Users\Mandrake\Desktop`, not in git. A must-read pointer to nothing |
| `src/RimMandrake/Pits` | missing, as the text itself says (merged into FlowWorks), but the section still lists Pits as VALIDATED |
| `RUT_Bitumen_KorvethSource.xml`, `RUT_ThrummelSeepwax_RosterSource.xml` | no longer in git. These are incident-narrative evidence; delete with the MOVE |
| `.claude/hooks/*`, `./bridge`, `./publish`, `./game`, `./mirror`, `modcheck/cli.py`, ModsConfig, `validate-question-card.py`, `_artpipe` | OK |

**False or stale claims (each one verified):**

| file:line | claim | measured reality | action |
|---|---|---|---|
| CHARTER.md L147 | "🔴 **BUILD PAUSE, in force**" | lifted 2026-10-02. BENCH.md L37, FOUNDRY.md L46 and CLAUDE.md L17 all say *"Build pause is lifted."* The binding charter contradicts both window files | DELETE the paragraph (top risk: a fresh FOUNDRY reads CHARTER first and refuses content work) |
| CHARTER.md L20 and `skills/rimworld-load-round/SKILL.md` L14 | cold load ~25 min | CLAUDE.md L86 MEASURED ~15 min on 599 mods and says it supersedes 25 | fix both |
| `~/.claude/CLAUDE.md` (rendered 2026-10-02) | "Sonnet 5.5"; "a `haiku` spawn dies with 400" | the source `45-subagents.md` (2026-10-07) says Sonnet 5 on GovCloud and that haiku SUCCEEDS, silently remapped to Sonnet 4.5. `claudeconf.py check` reports **drift**; `preview` shows 5 sections CHANGED and 1 ADDED (question-card section) not yet rendered | run `claudeconf.py render` (owner question 1: 1 changed line in the live file may be a hand edit, so `preview` first) |
| `~/.claude/CLAUDE.md` L338 | "Merge in a private `git worktree` and push from there" | project ruling 2026-10-02 "Worktrees are OFF" plus the hook refuses `git worktree add`. The global file instructs exactly what the project hook blocks | global: scope the line to "projects that allow worktrees", or change it to "merge in a fresh clone" |
| MEMORY.md L"Model ladder" | "Haiku OS searches only" | struck 2026-10-01 | delete or rewrite the line |
| MEMORY.md, 9 lines | session-scoped orders: subagent cap until 09-30, no subagents 10-05, cap RESCINDED, AFK nights 10-07, 10-08 ×2, 10-10 ×2, 10-11 | all expired. They are auto-loaded every session (~1.3 KB) | DELETE the index lines and files. The current night's order lives in the handoff |
| CLAUDE.md L404-450 | "FlowWorks, Graffiti and Pits are VALIDATED; WreckedMachines REVERTED TO DRAFT"; "3 of 35 validation.py carry `shows=`"; "NORTH_STAR_PIT_PILOT_1 … has never run" | walk headers today read **FlowWorks `state: DRAFT`**, **WreckedMachines `state: VALIDATED`**, Graffiti VALIDATED, and Pits.md is deleted (the exact inverse for 2 of 4). `shows=` is in **4 of 133** `validation.py` (git ls-files). NORTH_STAR_PIT_PILOT_1 was SUPERSEDED 2026-10-02 ("Premise dead … Pits.md was deleted") | DELETE the state prose. `modcheck floor --all` is the instrument (it was not run here, so live hash status is UNMEASURED beyond the header lines) |
| CLAUDE.md L190-193 | "98 live rows across 11 biome files still name the donor … 73 ported creatures spawn nowhere (`MLIE_ABSORPTION_BIOME_WIRING_1`)" | item CLOSED 2026-09-26: "55 genuine bare-donor rows retargeted … 3 remain no-port" | DELETE the sentence |
| CLAUDE.md L699-704 | "⛔ FIREHAWK_FLIGHT_BEHAVIOR_1's BodyDef/Spastic wiring needs replacing" | `RM_PyrelandsFauna.xml` L40/L186 say the Spastic overlay was "reverted-and-deleted", and L197 already wires `flyingAnimationFramePathPrefix` FireHawk_Flying_. The item is CLOSED | DELETE |
| CLAUDE.md L349-351 | "`RM_SeaDiveHatch` is a leftover … retirement is `SEA_DIVE_HATCH_RETIRE_1`" | that item was closed 2026-10-03 as a split. The successor is **SEA_DIVE_HATCH_REMOVE_1**, gated on SEABED_DESCENT_ASCENT_1 and SEABED_FLOOR_GENERATORS_1. The hatch def still exists (`DivingInteraction/Defs/ThingDefs_Buildings/RM_SeaDiveHatch.xml`) | repoint to the successor |
| CLAUDE.md L233, 558, 823 | canon_references "holds 137 entries — 45 creatures, 69 species, 23 droid chassis" | **214 entry dirs + 4 md + 3 other = 221** (python listdir) | replace with "a growing set; count it" (never a number) |
| CLAUDE.md L88, 195, 249, 459 | 599 / 631 / 629 / 630 active mods | live ModsConfig parses to **550** active today, and BIOME_MOD_UNIFICATION_1's close says 631→614 | delete the inline counts; the rule "parse it, never cite a number" already exists |
| CLAUDE.md L501 | ORACLE_EXPERIMENT_SPIKE_1 "client rewrite owed" | item CLOSED | repoint or delete |
| CLAUDE.md L36 | "BIOME_MOD_UNIFICATION_1" merge "NOW" | CLOSED 2026-10-09, all 3 waves cold-load-proven | change it to past tense, one clause |
| CLAUDE.md North-star | `NORTHSTAR_HASH_SCOPE_1`, `WALK_FEATURE_KEY_1`, `DLL_SOURCE_STAMP_GUARD_1` | **no ledger event, no item file** (0 shards). Cited as items, they resolve to nothing | delete the IDs (keep the rulings) |
| CHARTER.md header | "This file does not grow" | 5,954 → 11,311 B | owner question 4 |
| `infrastructure/agents/CODEX_PROPOSAL_*.md` (70 KB) | proposals filed in the binding-spec directory | 1–2 inbound refs each, from 2026-10-04 | MOVE to `design/RimMandrake/proposals/` (agents/ should hold only binding specs) |
| `infrastructure/agents/{POLICY,BUILD,CHECK,DECIDE,REP}.md` | tombstones | 8–32 inbound refs each, mostly historical items | KEEP (cheap, they absorb old links) |

## 5. Global vs project

**Project → global (general, not RimWorld). PROMOTE to `~/dev/Lodestar/claude/global/` or a global skill:**

| rule now in project CLAUDE.md or memory | proposed home |
|---|---|
| CRLF from `python.exe`, `grep -c` prints 0 and exits 1, `ls\|wc -l` on a missing dir, `grep -F` and line wrapping, zsh no word-split, existence ≠ identity, round numbers are query bugs, briefed numbers come back, sanity probe on every sweep | `~/.claude/skills/confident-wrong-numbers` (it already exists and is global) |
| A backgrounded Agent dies at 600 s silent with nothing on disk; brief a skeleton-file-first approach; prefer an inline script for mechanical censuses | `efficient-subagents` (global skill) or `45-subagents.md` |
| A PreToolUse hook added mid-session does not fire until a new session | `plugin-dev:hook-development` / `update-config` notes, or a Machinist knowledge file |
| `pkill -f` kills your own shell (memory) | global. **Reproduced in this very audit:** `pkill -f RIMWORLD_…` killed the calling shell (exit 144) |
| Correctness outranks ownership; delete inaccurate material, don't annotate | global doc-hygiene section (it applies to every multi-agent repo) |
| "When questions each add a clause to a procedure, stop: it's review work" and "ask whether the CATEGORY is needed before adjudicating inside it" | global (a judgement pattern, not RimWorld) |

**Global → project/machine (specific to one place, sitting in the global file):**
- `~/.claude/CLAUDE.md` "Machine" names RimMandrake clones. That is fine because it is the per-machine fragment (`machines/<key>.md`). KEEP.
- Global L338 "merge in a private `git worktree`" conflicts with the RimMandrake ruling (§4). Make the global line conditional.

## 6. Hook inventory

**Project hooks (`.claude/settings.json`), MEASURED by a script that parses the settings:**

| event / matcher | hook | enforces |
|---|---|---|
| PreToolUse Bash | `block_blind_scan` | no grep/wc/strings counts on large artifacts |
| " | `block_blanket_git_stage` | no `git add -A/./-a` |
| " | `block_shared_tree_merge` | no merge in a shared checkout |
| " | `block_dll_source_mismatch` | pushed DLL matches its `.srchash` |
| " | `block_ledger_lint` | ledger shards lint before push |
| " | `warn_unclosed_queue_item` | `Closes:` trailer |
| " | `warn_close_live_proof_owed` | close names its live-proof successor |
| Bash **and** Write/Edit | `queue_lint` | only rimflow writes the ledger; cross-seat item edit warns |
| Bash | `block_canon_contradiction` | design docs vs canon |
| Bash | `block_forged_owner_said` (+ library `owner_said_provenance.py`) | `--owner-said`/`--said` must be his typed words |
| Bash + Write/Edit | `block_transcript_tamper`, `block_ledger_shard_write` | no transcript or shard writes |
| Bash | `block_unledgered_texture` | textures go through the art ledger |
| Write/Edit/Bash | `warn_skill_unwired`, `block_forged_validation`, `block_hand_edited_sheet` | — |
| Agent + Bash + WorktreeCreate | `block_worktrees` | worktrees OFF |
| Bash | `block_tmpfs_clone` | no clone into /tmp, /dev/shm or /run |
| SendMessage | `block_peer_messages` | only your own subagents |
| Agent | `block_agent_without_model` | explicit `model` |
| SessionStart / UserPromptSubmit | `set_session_title`, `bench_mode`, `src/RimMandrake/Utils/pulse/hooks/im_back_hook.py` | session title, mode, "I'm back" |
| Stop | `block_paste_handoff` | no `!`-paste handed to the owner |

**Global hooks (`~/.claude/settings.json`):** `validate-question-card.py` (AskUserQuestion), `placard_read_guard.py` (Read), `route-agent-spawn.py` (Agent|Task, refuses a model the gateway can't serve), Lodestar `conversation_record.py` (SessionEnd), placard SessionStart, and `detect-prose-decision.py` (Stop).

**Health (MEASURED):**
- All **21/21 hook selftests pass**.
- Serial cost of the 18 Bash-matched hooks on `ls src` is **0.38 s** in total, so cost is not a reason to cut any.
- `owner_said_provenance.py` is not wired, and correctly so: it is a library imported by `block_forged_owner_said.py`. KEEP.
- 16 hooks are wrapped `2>/dev/null || true`. They deny via JSON stdout, so blocking still works, but **a crashing hook (ImportError, syntax error) fails OPEN silently**. The selftests are the only guard. Propose: let `run_selftests.py` run at SessionStart, or drop `|| true` and accept a visible error.
- **Redundancy:** none harmful. `block_agent_without_model` (project: model present) and `route-agent-spawn` (global: model servable) are complementary. `queue_lint` runs twice on Bash and on Write by design.
- **False positive MEASURED this session:** `block_forged_owner_said` refused a read-only `python3 - <<EOF` census because a *dict literal* contained the substring `--said'` followed by a quoted string. It reads heredoc bodies as flags. Fix: skip quoted heredoc bodies, or require `--said` as a separate argv token.

**Policies stated as 🔴 or "said N times" that have NO enforcement:**
1. **CLAUDE.md/CHARTER growth.** CLAUDE.md is 12× in a month, and CHARTER's "does not grow" is broken. Propose `warn_claudemd_growth.py` (PreToolUse Write/Edit and commit): warn when `CLAUDE.md` exceeds a byte budget (e.g. 30 KB) or CHARTER grows without a matching deletion.
2. **"A biome with zero tiles is not a defect"** (it cost 3 reconciliation passes). A Stop hook could flag a reply that pairs an `RM_` BiomeDef with "0 tiles". Cheap, and it addresses the repeated failure directly.
3. **Unattended flyer live-testing** ("said THREE times"). A hook could warn on `take_screenshot`/`step_game_ticks` bridge calls when the session's recent text names a flyer. It is hard to make precise, so it is optional.
4. **`pkill -f` / `pkill` by pattern** (memory rule, violated in this audit). A Bash PreToolUse could deny `pkill -f`/`killall`. Trivial and precise.
5. **"Search `src/` before FILING"** (4 of 6 mechanisms already built, twice). `rimflow file` could print the top `git grep` hits for the subject words before it accepts. That is a tool change, not a hook.
6. **Expired session orders in memory** (9 lines). Nothing ages them out. Propose an `expires:` frontmatter field that the memory index ignores past its date.

## Top 10 actions, ranked by value

| # | target | action | why | risk if wrong |
|---|---|---|---|---|
| 1 | `infrastructure/agents/CHARTER.md` L147-149 | DELETE "BUILD PAUSE, in force" | the binding charter contradicts the owner's 2026-10-02 lift | none; the lift is quoted in BENCH and FOUNDRY |
| 2 | `CLAUDE.md` | MOVE per §3 (instruments, tool traps, biome rulings, flyer mechanics, north-star state, patch, git, review) to the named docs and skills, leaving one-liners with verbatim quotes. Target ≤ 29 KB | saves ~12k tokens per session and per subagent | a moved trap is read less often. Mitigation: the destination is named in the one-liner |
| 3 | `CLAUDE.md` stale rows in §4 (north-star states, MLIE 98 rows, FIREHAWK, SEA_DIVE_HATCH pointer, 137 canon, mod counts, missing Desktop doc, ghost item IDs) | DELETE or correct | 9 measured false statements in an auto-loaded file | low; each was verified |
| 4 | `~/.claude/CLAUDE.md` | `claudeconf.py preview`, then `render` | the live global file teaches a superseded haiku/Sonnet ladder and lacks the question-card section | 1 CHANGED section may hold a hand edit (preview first) |
| 5 | MEMORY.md + 9 memory files | DELETE expired AFK/cap orders and the haiku ladder line | they are auto-loaded every session, and one contradicts current policy | none; they are session-scoped by their own text |
| 6 | Global L338 vs project worktree ban | edit `~/dev/Lodestar/claude/global/50-save-as-you-go.md` to "merge in a fresh clone (or worktree where the project allows)" | the global and project rules collide | none |
| 7 | CHARTER/BENCH/FOUNDRY | MERGE the duplicated Correctness, debug_process, HANDOFF and `./game` sections into CHARTER (one home each). BENCH and FOUNDRY keep only seat-specific behaviour | 4-way restatements drift (proved by #1) | low |
| 8 | new `.claude/hooks/warn_claudemd_growth.py` | PROPOSE | the only durable fix for 12× growth | warn-only, none |
| 9 | `block_forged_owner_said.py` | fix the heredoc false positive | it refused a read-only census this session | the guard loosens slightly. Keep the argv-token check |
| 10 | `infrastructure/agents/CODEX_PROPOSAL_*.md` | MOVE to `design/RimMandrake/proposals/` | 70 KB of proposals in the binding-spec directory | 1–2 inbound links to repoint |

## Questions only the owner can answer

1. **The global CLAUDE.md is out of sync with its Lodestar sources** (5 sections changed, 1 added). (a) Render from the sources now, overwriting the live file · (b) First pull the live file's differences back into the sources (`claudeconf.py adopt`), then render · (c) Leave it until the next Lodestar curation.
2. **Where should the owner rulings moved out of CLAUDE.md live?** (a) One new `design/RimMandrake/OWNER_RULINGS.md`, with each quote verbatim and dated · (b) Spread across the topical docs (biome_rulings, debug_process, art ledger) · (c) Keep the rulings in CLAUDE.md and move only lessons/incidents (which ends near 45% rather than 40%).
3. **Size cap for the project CLAUDE.md?** (a) Hard 30 KB with a hook that warns · (b) Soft cap reviewed at each weekly cleaning · (c) No cap, curation passes only.
4. **CHARTER's "does not grow" law, now at 1.9×:** (a) Re-baseline at today's size and enforce it with the growth hook · (b) Cut back to ~6 KB by moving the handoff/worktree/queue prose to their docs · (c) Drop the clause.
5. **Expired session orders in auto-memory (AFK nights, caps):** (a) Delete them at each weekly cleaning · (b) Add an `expires:` field and have them age out automatically · (c) Keep them as history.
6. **The missing flight reference `~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md`:** (a) It is on another machine, so copy it into `skills/` · (b) It is gone, so drop the pointer (the CLAUDE.md XML is the reference) · (c) Regenerate it from the Core chicken/duck defs.
