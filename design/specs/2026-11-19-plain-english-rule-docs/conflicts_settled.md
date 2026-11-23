# Conflicts and stale lines: settled

Item: `RIMMANDRAKE_SETTLE_REWRITE_CONFLICTS_DELETE_STALE_LINES_NOW`. Run of 2026-11-23. Source: the "Conflicts" list and the
stale lines of each file in `results/` (21 result files; index: `undefined_terms_and_conflicts.md`, table 3).

**Rules:** 1 the code or the live tool · 2 his later ruling · 3 root `CLAUDE.md` or `GUIDING_PRINCIPLES.md` · 4 the thing
is gone · 5 for him (or the obvious answer, recorded).

**Commits:** A = `3c98eed8162c` · B = `032f29fdc8ce` · C = `131dbbc5a6a8` (and the commit that lands this file). "Earlier" names the commit of another run that settled
the row before this run reached it.

The Conductor-act ruling id (`--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`) is refused to a detached
helper by `conductor_acts.check`. So the ledger notes of this item carry the Conductor's brief as `--why`, under seat BENCH.

## CHARTER and Agent_Policy

| conflict (side 1 / side 2) | decision | rule and evidence | commit |
|---|---|---|---|
| Deleting others' work: CHARTER "only with the owner's word" / root `CLAUDE.md` | the Conductor may, with `lost:` and `undo:` | 2: his five acts, 2026-11-19 | A |
| Loosening a bar: CHARTER "stays his" / root `CLAUDE.md` | the Conductor, as a mindful act | 2: same; also `flyer_truth_set.md` | A, C |
| Re-freeze of the `official` dump: CHARTER, GAME_STATE, `canon.yml`, `dumps/README.md`, `refresh.py` docstring "only the owner" / root | the owner or the Conductor's recorded act | 1: `refresh.py` takes `by="conductor"`; 2 | A |
| v2 ideas: CHARTER "straight to `V2_DREAMS.md`" / Design Version rule | a mod's next-version idea is a ticket; an idea of no mod may go to `V2_DREAMS.md` | 2: his Design Version rule, 2026-11-13 | A |
| Helpers the Conductor launches: CHARTER two / Agent_Policy five | CHARTER points at Agent_Policy | 1: `block_unbounded_agent.py` enforces the five | A |
| Fable blank-page design: the Fable row / "does not do design in-window", design to Opus | a whole mod from a blank page is a detached Fable run; other design is Opus | 2: ladder 2026-11-12 and his card 2026-11-18; 1: `detached_helper.py --model fable` | A |
| Where the ladder lives: root "nowhere else" / Agent_Policy's "source of truth" | Lodestar holds the fleet ladder; Agent_Policy is its only home in this repo | 3 | A, C |
| The Conductor's model: Fable / check F7 opus | window Fable, headless quick checks Opus | 1: `dispatcher_schedule.json` | A |
| CHARTER "does not grow" / batch plan "can grow" | CHARTER gains no rule; more words are allowed | 5, obvious answer: the header is about new rules | A |

## Conductor files and roles

| conflict (side 1 / side 2) | decision | rule and evidence | commit |
|---|---|---|---|
| The daily digest: "a program builds it, never by hand" / "Build his daily digest" | the second line is deleted | 1: `delegated_digest.py` | B |
| `--for BENCH` / "Type CONDUCTOR" | `--for CONDUCTOR` | 1: `cli.py` reads CONDUCTOR as the key BENCH | B |
| `CONDUCTOR.md` four start commands / role file five | `queue CONDUCTOR --owed` added | 1: the role file is the one source | B |
| Background commands: end with the window / hold the restart | they end on a goodbye; they hold every other restart | 1: `seat_restart.conductor_holds`, `_goodbye` | B |
| The wake lists his late text "once" / "until a window has answered" | until answered | 1: `seat_restart.answered` | B |
| Session "no helper limit" / 20 min, then two | one line points at Session mode | 1: `slot_rules.json` `conductor_window`; his words 2026-10-29 | B |
| A cut list "goes to him" (conductor 3c, producer, operations) / the Conductor decides | the Conductor decides | 2: his five acts | B |
| Who sets `enabled: false`: "(the owner's)" in four role files and `conductor.md` / root | the owner or the Conductor's act | 2 | B; Innovator: below |
| Operations: "a bar cut is always his" / "The Conductor decides it" | the Conductor | 2 | B |
| Operations: "Restoring a band is the owner's" / root | his or the Conductor's act | 2 | Earlier: the run `RIMMANDRAKE_CHECK_HIS_QUOTED_RULINGS_FOR_IMPRECISE_WORDS_TOO` holds that line |
| Two helpers across ALL roles (Operations, Auditor, Innovator) / the pool of 16 clones | the two-helper pool is deleted; the spawn hook holds the limit | 4: `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` was dropped 2026-11-01; 1: `block_agent_over_slots.py` | B |
| Producer: list distressed "if an entry is closed" / `priority_list.py` | a closed entry drops; distressed when none is open | 1: `ops_watch.py`, `priority_list.py` | B |
| Auditor: D1(b) "a close needs a pass" / a close with no verdict passes | a close with no pass goes, recorded `uncheckedLifted` | 1: `cli.py` (2026-11-20); also `using-rimflow` "unchecked" | B |
| Innovator: waits on two dropped items; "His, always"; silencing; off switch; helper limit (5 rows) | the role is retired | 2: the owner, 2026-11-23, *"Role is retired."* | Earlier: `f1f47631e6` |
| Role rows' note "claude --max-budget-usd" / no agent is told its spend | the note names `spend_watchdog.wrap` | 1: `role_launch.py` | C |
| `criteria_fixer.md`: "a second reader" / guard takes a card too / spec "GPT" | a second reader or a card; the GPT limit is deleted from the spec | 1: `refusal_contract.py diffguard` | B |
| `criteria_fixer.md`, guard text, spec: an owner bar "goes to him as a card" / root | the Conductor's recorded act | 2 | B |
| `fable_rescue.md` "not shown beyond Slack" / the Knockback rescue | the measured case is named | 1: `RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX` (certificate 16 of 16) | B |

## Delegation, debug, Designer, judges, subagents

| conflict (side 1 / side 2) | decision | rule and evidence | commit |
|---|---|---|---|
| `debug_process.md` §6 "only his validate binds" / `delegation_policy.md` | three routes bind | 1: `block_forged_validation.py`; 2 | A |
| Long game-time runs: "possible but risky" / "No more long runs" (both 2026-10-13) | no long runs; the earlier quote moved to `CLAUDE.history.md` | 2: ledger 02:02Z against 04:34Z | A |
| A live session ends with a check / a look defect is stored, not wired | both: the script is not a ladder stage. "Until the ladder is regenerated" became "at its mod's preflight" in `debug_process.md` and `validation_map_and_rules.md` Rule 12 | 2: his card 2026-11-14, "Per mod, as it advances." | A |
| Old section numbers in dated records (`Contagion`, `CARDS_ENFORCE_DELEGATED_CLASSES_STOP`) | no edit: the numbers were true on the date of the record | 5, obvious answer | none |
| `designer_grounding.md` "Certify with him" / `designer.md` | him or the Conductor window | 2 | C |
| `tier_reason` for live only / lint | every tier but `offline` | 1: `concept_tree.py` | C |
| `designer.md` "quote those answers word for word" | the sentence says that the copy is the brief's text, and his words are in the cards | 1: OWNER ledger 2026-11-17T06:24:09Z | C |
| The art brief has no stopping level | no false line: the open item `RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN` owns it | the item reads proposed | none |
| `judge_cli.py` comment names a section that does not exist | polish, not touched: the file is in a calibration row, and an edit of a comment resets it to UNTESTED | test 1 | none |
| The scene calibration tests the code's prompts, not the scene brief | polish, not touched: the row's cases name `scene_look_calibration.py`, so the record says what ran | test 1 | none |
| Test Pilot "restore the list, game down" / "never restore" | leave the game as found; no restore | 2: his words 2026-10-24; 3 | B |
| Test Pilot "Keep the game up" / "game down" | up during a sitting; at its end, as found | 5, obvious answer | B |
| `rm-judge.md`: a skill for art / root: `art_judge_brief.md` for art and cosmetic | the brief for both; the skill for the art-evaluation pipeline | 3; `delegation_policy.md` §4.3 | B |
| A program's output: scratch (shared block) / `/tmp` (root) | scratch under the agent storage root | 2: his 2026-10-19 storage rule is later than the 2026-08-27 line | C |

## Git, game state, spec, rulings

| conflict (side 1 / side 2) | decision | rule and evidence | commit |
|---|---|---|---|
| GAME_STATE "a 45-minute idle hold is simply taken" / root | a live holder holds; a dead one is free | 1: `game_lock.py` | B |
| GAME_STATE "`take --force` always works" / root | never his OWNER hold before 45 min | 1, 3 | B |
| GAME_STATE: who reaches `broadcast.py` | the owner, or the Conductor's act | 1: `broadcast.conductor_broadcast`; 2 | B |
| Bare assent: `conductor_closeout.py`, `using-rimflow`, `docs/AGENTS.md` "refused" / `cli.py` | recorded | 1: `_check_owner_said` | B |
| One writer per clone / two windows share a clone | the window and its helpers share the clone | 3 | B |
| "Revert" acts on what (root / `standing_rulings.md`) | the pool | 3 | Earlier: `de63778138` |
| "degrades gracefully" / "a game that still works" | one demand; the line says both | 3 | C |
| Spec: SteveDesktop's queue takes only offline-proved tests (three lines) / 18c | any mod's token-free test | 2: his words 2026-11-17 | C |
| Spec: "the two games" / root | four games, by name | 3 | C |
| Full-list load 15 min / 25 min (spec, load-round, its traps "disputed") | ~15 min is the newer measurement; both dates stay | 1: measured 2026-09-07 against 2026-08-19 | C |
| Spec intake exit "asked of him then" / decision 8 | no ask | 2: his order 2026-11-15 | C |
| Spec five / four mods | two sets: the five of 2026-11-13 and the four advancing | 1: `VERSION.json` lock dates | C |

## Fact files, traps, structure

| conflict or stale line | decision | rule and evidence | commit |
|---|---|---|---|
| Facts README "Append, never rewrite" / `operations.md` replace; `biome_rosters.md` "Append only" | a false entry is corrected; a true fact is never dropped | 2: correctness, 2026-09-19 | C |
| `instrument_traps.md`: a zero-tile biome is not done / root | root | 3 | Earlier: `ff6dc8e491` |
| "glob errors loudly" / `glob.glob` swallows | `ls <dir>/*.json` is named; Python's glob is the exception | 1: run in bash | C |
| "The shell here is zsh", "`grep` here is ugrep" | each entry names its shell and date | 1: measured 2026-11-23 | C |
| 132 − 3 − 2 = 129 | 132 − 3 = 129; the 2 hooks are outside the 132. Today: 135 match, 130 are harnesses | 1: `git ls-files` | Earlier: `0627d76e69` |
| `steve_fault_diagnosis.md`: 3898 cycles over rows that sum to 2326 | 3898 (3792 + 106 temperature samples) is deleted from the head of the table; the table says five boots, 2326 cycles, and names `watch_per_boot.tsv` | 1 | C |
| Soak reader exit codes 0-3 | 4 and 5 added | 1: `soak_read.py` | C |
| Vendor drivers "hypothesis under test" / Result | head says tested and falsified; the cause line names the driver | 1 | C |
| `operations.md` `cli.py:255`; dead mode words | `_ctx`; read as `belt` | 1 | C |
| `operations.md` findings on deleted files; pulse checkout and its two debts; Ralph loop units | deleted | 4: `b28e0d6975`; folder absent; units absent | C |
| "The one live game is the bottleneck" | dated 2026-10-26; several games now | 3 | C |
| BUILT 343, 496, 521; net 567 / 609 | each set is named; 1,531 − 922 = 609 | 1: `csuite\evidence.md` Q6, Q4 | C |
| Canary recovery: `down/init/up` / RUNBOOK | RUNBOOK | 3 | C |
| Root and `standing_rulings.md` point five topics at `tool_traps.md` | each topic points at its real home | 1: `git grep` | C |
| `pgrep -f artpiped.py` / `pgrep` trap | `systemctl --user is-active rm-artpiped.service` | 1: run, reads active | C |
| `system_screenshot.py` always allowed / refuses under WSL | both true; the trap says so | 1 | C |
| `show.sh` opens / selects | trap entry is right; `~/.claude/CLAUDE.md` is outside this repo | 1 | none (see below) |
| `./pipe why` entry under Simulators | moved to Ledger, rimflow | 5, obvious answer | C |
| `taskkill /IM RimWorldWin64.exe` (5 files), `Select -First 1` (7) | deleted: no such code is left, two games run | 4: `git grep` finds only the selftest mutants | C |
| `STRUCTURE.md`: `skills/` gated on the owner; which skill to load is `CLAUDE.md`'s job; V1_CHAIN is the authority; worldgen checklist "for world creation"; only `MANIFEST.json` tracked; ~430 MB | each corrected | 2, 3, 1 (154 tracked files, 0 `MANIFEST.json`) | C |
| `STRUCTURE.md`: his promotion test (`Jawa/`) / three tiers | three tiers; his quote moved to `CLAUDE.history.md` | 2, 3 | C |
| `STRUCTURE.md` root table has no row for some folders | no conflict: the file now says so itself | none | none |
| `infrastructure/README.md` (five symlinks, four seats) | deleted; its two inbound rows corrected | 4 | C |
| Minimal list 19 / 13 mods | 22 s is the 13-mod list of 2026-08-19; the file held 27 mods on 2026-11-23, its time UNMEASURED | 1: parsed `ModsConfig.MINIMAL.xml` | C |
| Five tiers / seven `LEVELS` | no conflict: two counts of two things (tiers of a ladder, words of a verdict) | 1: `model.py` | none |
| `LEXICON.md` SteveDesktop "a game" | two games | 3 | C |
| `LEXICON.md` minimal list "proves nothing" / tier lists | no conflict: a tier list is not the minimal list | 3 | none |
| `jawa/get_defs` "scalar-only" | unless `deep=true` | 1: `JawaBenchTerrainTools.cs` | C |
| `naming_inventory.md`: `CLAUDE.md` says "the Second Hand"; serves a rename to come | past tense; the rename is done | 1, 4 | C |
| `distress_signals.md`: the score goes to REP | BENCH (the Conductor) | 4 | C |
| `biome_paint_list.md`: 61 BiomeDefs, 25 twins, donor item owed, the dropped fauna law | 36 (34 + 2), twins gone, owed line deleted, evictions stopped | 1: `src/`; 4 | C |
| `clone_memory_peak.md` `min_mem_available_gb` and the 3 GB host stop line | both deleted | 4: no code holds either | C |

## The skill `clone-landing-commits`

| conflict | decision | rule and evidence | commit |
|---|---|---|---|
| `land.sh` "when you must not move HEAD" / `land.sh` runs `seat_sync.py` | `LAND_SYNC=0` is named | 1: `land.sh` lines 12, 100 | the commit of this file |
| "run `git add` first" / `./publish` adds | `./publish` adds it; `land.sh` needs it | 1: `publish.py` line 222 | the commit of this file |
| `references/traps.md` quotes old refusal texts | today's texts | 1: `seat_sync.py`, `publish.py` | the commit of this file |

## For the owner (rule 5)

None. No listed conflict was left open by rules 1 to 4 and turned on two of his rulings with no later one.

One line is outside this repo, so this run reported it and did not edit it: `~/.claude/CLAUDE.md` says that
`./Utils/show.sh <path>` opens a file. `show.sh` selects the file in Explorer; it does not open it.
