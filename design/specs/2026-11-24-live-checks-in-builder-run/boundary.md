# BOUNDARY: a builder or fixer runs its in-game check in the same run when a game is free (maturation.py `brief_text`, `LIVE_IN_RUN_RULE`, `record_early_row`, `record_unrun`, `read_ingame_exit`, `ingame_to_run`, `unclassed_lines`; build_match.py `carried_rows`, `check_runs`, `early_rows`; maturation_autonomy.py `OFFLINE_CLOSE`, `STAGE6_ROAD`, `fixer_brief`), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py`, `src/RimMandrake/rimflow/build_match.py`,
`src/RimMandrake/rimflow/maturation_autonomy.py`. Tests of the same names:
`src/RimMandrake/rimflow/selftest_live_checks_in_builder_run.py`. Item:
`RIMMANDRAKE_RUN_LIVE_CHECKS_IN_BUILDER_RUN_WHEN_GAME_FREE`.

The failure (2026-11-24): FlowWorks visit 11 had four faults. Four runs fixed them between 9:00 and 9:56 PM PST. Each
run recorded its in-game check UNRUN for Stage 6, because its brief said "never run here". ArchBig and ArchSmall read
FREE for most of that hour. A builder then wrote six live scenes and left them unrun while ArchSmall was free. The
owner, 2026-11-24 about 11:00 PM PST: *"Was a game available? Because it so, that builder should have deployed it and
tested it right away in the same context."*

The question: when a builder or fixer at an offline stage changes something that an in-game check reads, who runs that
check, and does the run count for Stage 6?

## ACCEPTS (the only inputs these parts are built for)

- **an-early-row.** One run of a stage-6 in-game check that a builder or fixer made outside a visit, given to
  `maturation.py live-row` as the row a Stage 6 driver writes in `rows.jsonl` (`test`, `verdict`, `outcome`, `game`,
  `mod_sha`, `command`, `evidence`, `site_checked`, `held`, and the fields `build_match.py identity` prints).
- **a-stage-record.** The mod's `version/stage_record.json`: its stage and its moves into `in_game`.
- **a-visit-record.** The rows of the visits on disk (`version/in_game/visit_<N>/rows.jsonl`).

## DOES NOT SURVIVE (not handled)

- **a-row-made-up.** The tool cannot see that the run happened. A row is the run's word, as a Stage 6 driver's row is.
- **a-game-on-steve-desktop.** `record_unrun` reads the games of this machine only (ArchBig, ArchSmall). The test lane
  for Steve1 and Steve2 is not read; the row says so.
- **a-pipeline-defect-fixer.** The fixer of a pipeline defect (`fix_for` `blocked`) changes pipeline machinery, which
  has no in-game check of a mod. Its brief keeps its game ban.

## UNCHANGED

- The Stage 3 exit still accepts an in-game check recorded UNRUN with its command (`every_bar_has_a_check_that_runs`),
  so a busy game never blocks a build.
- The Stage 6 exit still needs each in-game check run on a commit that holds its change, through the same build match
  and change relation. An early row is one more row of a visit, never a pass by itself.
- A game-only road-back item is still Stage 6 work (`game_takeable`, `STAGE6_ROAD`).

## PROMISES (each one is owed a test of the same name)

- **the-builder-brief-runs-touched-checks-on-a-free-game.** The Stage 3 builder brief tells the builder: when its change
  has an in-game check, read `game_lock.py query all`; when a game is free, take it, deploy the mod's small list, run the
  in-game checks that the change touches, class and fix a non-pass in the same sitting, and record each run with
  `maturation.py live-row`. It records UNRUN with the command only when no game could take the check, and names which run
  held each game. It no longer says "you never run one" or "Offline only: no bridge, no game".
- **every-fixer-brief-runs-touched-checks-on-a-free-game.** The road-back, version and walk fixer briefs that close on an
  offline test say the same, and none says "Never take the bridge or a game". The Stage 6 router's road-back text no
  longer says that the fixer records the check UNRUN for Stage 6.
- **each-brief-keeps-the-bindings.** Each of those briefs says that his OWNER hold and `./pipe off game:<name>` bind,
  that a game is never put in fullscreen or focus, and that no raid is staged while the raid pause is on.
- **a-live-row-carries-what-a-visit-row-carries.** `live-row` refuses a row that lacks `test` (a stage-6 check of the
  table), `verdict` (PASS, FAIL or UNMEASURED), `outcome` (one of the seven), `game`, `mod_sha`, `command`, `evidence`,
  `site_checked`, `held` (a list), `mod_hash`, `game_build`, `active_mods`, or `tier` or `full_list`. The refusal names
  each missing field and the command that prints the identity fields. A refused row writes nothing.
- **a-live-row-belongs-to-the-next-visit.** An accepted row is stamped with `item`, `by`, `at` and `before_visit`: the
  number of the next visit to open, or the open visit's number while the mod is in in-game acceptance and that visit's
  driver has written nothing (no folder, or only the test lane's rows).
- **an-early-row-counts-as-a-row-of-its-visit.** `carried_rows` and `check_runs` read each early row as a row of the
  visit that it precedes, before that visit's own rows. The Stage 6 exit of visit N reads the early rows of visit N as
  its own rows. `ingame_to_run` counts an early PASS whose check the change since its commit does not touch, so visit N
  does not run that check again; at visit 1 too.
- **a-change-the-check-reads-owes-it-again.** When a commit after the early row's `mod_sha` touches a file that the check
  reads, `ingame_to_run` runs the check again.
- **an-early-row-meets-its-unrun-row.** An UNRUN row is met by an early row of its check on a commit that contains the
  UNRUN row's commit, as by a visit row.
- **an-early-failure-holds-as-a-visit-failure.** An early row that reads UNRESOLVED holds its check under a later PASS, and
  is listed for classing in the next visit's brief, as a visit row is.
- **an-unrun-row-names-who-held-each-game.** `record_unrun` stamps `games`: one line per game of this machine from
  `game_lock.py`, who held it and for what, or the cause when it could not look. SteveDesktop's games are named as not
  read.

Later lists beside this page: `polish.md`.
