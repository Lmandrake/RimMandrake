# Census: what protected the owner's play, game or saves (2026-11-23)

Item `RIMMANDRAKE_ENACT_NOBODY_PLAYS_NO_OWNER_GAME_OR_SAVES_TO_GUARD`. The ruling and its words:
`design/RimMandrake/standing_rulings.md` §Nobody plays during development. Verdicts: KEEP guards a look at staged work or
a canonical world save, or is only a record. REWORD is a true rule with a false reason. DELETE is gone.
Method: a search by meaning (about 30 patterns) over the rules, roles, skills, hooks, specs, live items and code. Ledger,
handoffs, conversations, closed items and dated evidence were not read row by row: they are records.

## Rules, roles, skills

| where | what it said | verdict | done |
|---|---|---|---|
| `CLAUDE.md` §Facts, §There are several live games | ArchBig "is the owner's game", "ArchBig is his" | DELETE; the rule is stated, his hold now "guards a look" | yes |
| `standing_rulings.md` §There are several live games | "his game: his walks ..." | REWORD; new section holds his words | yes |
| `infrastructure/GAME_STATE_WORKFLOW.md` | never kill a game he is PLAYING; "his campaign session is not disposable"; the game that he plays | DELETE; his hold stays | yes |
| `LEXICON.md` (Archmagi) | "the game he plays" | REWORD | yes |
| `infrastructure/state/modlists/README.md` | restore the full list "before he plays" | REWORD (a look or a check that needs it) | yes |
| `roles/operations.md` | never touch the game while he plays | REWORD (while his hold or `pipe off` stands) | yes |
| `roles/conductor.md` | "his game" at three places | REWORD | yes |
| `skills/rimbridge`, `rimworld-load-round`, `rimworld-modding`, `using-rimflow` | ArchBig is his game | REWORD | yes |
| `skills/rimworld-deploy` §7 | never close a game that he is playing | REWORD (his hold guards a look) | yes |
| `skills/rimworld-debug-testing` §3 | a suspended rule that protects the campaign save when play starts | DELETE; canonical saves and his hold stay | yes |
| `skills/rimworld-live-review` §7 | "the campaign save is untouchable" | REWORD (canonical world saves) | yes |
| `skills/telemetry` | the tier is off in his campaign, for his 10 % budget | REWORD (a canonical save is loaded) | yes |
| `skills/rimbridge/references/traps/lifecycle.md`, `companion.md` | "the owner's real campaign map"; a raid on the colony he is playing | REWORD | yes |
| `skills/rimbridge-companion` + `references/extending-detail.md` | `--gm` is opt-in | REWORD (the default is in) | yes |
| `CLAUDE.md` §Options he must LOOK at, `saves_awaiting_review.txt` | review saves stay until he rules | KEEP (a look) | n/a |
| `CLAUDE.md` §The bridge is passed through one file (OWNER hold, 45 min, never focus or fullscreen) | guards a sitting | KEEP | n/a |
| `infrastructure/state/CANONICAL_SAVE.md` | canonical saves | KEEP | n/a |
| `WORLD_REMAKE_FINAL_STEP_1`, `V1_CHAIN.md` ("first play session", "before he starts his campaign") | the order of the last steps before release | KEEP (a plan of ours, guards nothing) | n/a |

## Bridge 2 design

| where | what it said | verdict | done |
|---|---|---|---|
| `07_for_the_owner.md` choices 2 and 3 | may a test stop a broken ArchBig; may a test remove things on his saves | DELETE (void); the rule is stated | yes |
| `07` table "Your game, ArchBig" | a CAMPAIGN column for a save of his | DELETE; a list of five rules | yes |
| `07` choices 1a and 1b | flight | KEEP: answered on the same cards, enacted elsewhere | n/a |
| `05` safety row, decision 6, "ArchBig never arms", the GPT round notes | the gate guards his game | REWORD: the gate guards a loaded canonical save only | yes |
| `06` and the four tickets (gates, calm profile, deviation record, game watcher) | CAMPAIGN refuses; ArchBig is reported | REWORD: refused with a canonical save loaded; a broken game is stopped at once. Check counts did not move | yes |
| `02`, `03`, `04` | "never destructive on his game", his saves, ArchBig never arms | DELETE or REWORD | yes |
| `00`, `01`, `census_sources/` | dated records and GPT answers | KEEP | n/a |

## Code and tool messages

| where | guard | verdict | done |
|---|---|---|---|
| `JawaBenchSafetyCore.Effective` (the CAMPAIGN profile) | with an old `expiresUtc`, the test tools were refused on any save; with no file, on a new game too | DELETE, test first: six rows red before (193 of 199; three are the refusal itself, three its words), 199 of 199 after. A listed canonical save, an unknown save with a list, and a loaded save with no readable list stay refused (rows green) | yes; live at each game's next companion deploy |
| `build.py` and the companion csproj: GM tools off by default | "the colony the owner is playing" | DELETE, test first (`gm_tools_by_default` red, then green); a bare build is now the full build | yes |
| `game`, `modlist_swap.py`, `cherrypicker_swap.py`, `biome_load_proof.sh` | "before he plays" | REWORD (a look, or a check that needs it) | yes |
| `testq/archmagi_phases.py`, `testq.py`, `steward.py`, `worker.py` | never deploys to, launches or stops "the owner's game" | REWORD. The lane is a borrower, off by default | yes; see the questions |
| `rimflow/cli.py` filing prompt | "the owner playing is the default validation" | DELETE the clause | yes |
| `game_names.py`, `game_instance.py`, `detached_helper.py`, `live_session.py`, `prove_draw_order_live.py`, `JawaBenchTpsSampler.cs`, `companion_grant.json` | comments: his game, his save, he is playing | REWORD | yes |
| `companion_handshake.md`, `bridge_system.md`, `bridge_debugging_system.md`, two boundary pages | his campaign | REWORD | yes |
| `save_guard.py`, `modcheck/saved_base.py` | no save overwritten in the Saves folder | KEEP: canonical saves and saves that wait for a look; a wrong-slot write cannot tell them apart | n/a |
| `saves_prune.py` | CANONICAL_* and awaiting review | KEEP | n/a |
| `save_played_tiles.py`, `w9_run.py` | the frozen canonical save's tiles | KEEP | n/a |
| `game_lock.py`, `owner_interaction.py`, `control.py` (OWNER hold, `pipe off game:`) | a look | KEEP | n/a |
| ArgGuard `lenient`, `artboard_stage`, `mod_settings_field set`, `health_profile` refusals in CAMPAIGN | act through the one profile | KEEP: they now bind only with a canonical save loaded | n/a |
| `prove_*.py` headers "never the campaign save" | the canonical save | KEEP | n/a |
| `sim/testpilot_sim.py`, `sim/loop_sim.py` | an "owner plays" chance in a simulation | KEEP (guards nothing; nobody runs it) | n/a |
| `art_sheet.py` `MIN_REAL_LIST`, `scale_panel.py` | "what the owner plays" in a comment | KEEP (no guard of play) | n/a |
| Retired-era design docs (`role_responsibilities`, `dispatcher_*`, `csuite`, `live_fixer`, `testpilot_merged`) | "never while he plays" | KEEP (dated records; no run reads them as rules) | n/a |

## Questions and what stays

1. The live `companion_profile.json` on Archmagi lists `CANONICAL_ASHKARR_START_2026-09-12, Ashkarr, Ashkarr autosave`.
   The current canonical start `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3` is not on the list, so CAMPAIGN does not
   guard it, and the two other names are no save on disk. Closed by
   `RIMMANDRAKE_LIST_CANONICAL_SAVES_IN_COMPANION_PROFILE_CURRENT_START_MISSING`: the list is compiled in from
   `CANONICAL_SAVE.md`.
2. `companion_grant.py`, `ensure_test_profile` and the ops alarm no longer read `expiresUtc`: removed 2026-11-24, once
   all four games loaded a companion with the new rule (`RIMMANDRAKE_REMOVE_GRANT_EXPIRY_CHECKS_ONCE_FOUR_COMPANIONS_REDEPLOYED`).
3. `testq/archmagi_phases.py` never stops or deploys to ArchBig, so a wedged ArchBig under that lane is reported, not
   stopped. The lane is off by default. Removal needs a deploy path that does not exist: not built.
