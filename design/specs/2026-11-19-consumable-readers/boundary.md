# BOUNDARY: the consumables' readers and `pipe set|add|reset|limit`, Design Version 0.1.0

Code: the readers named below, and `src/RimMandrake/rimflow/pipeline_control.py` (`RESOURCES`, the measures `pipe show`
prints). The accounts themselves live in the control store (`control.py`, `used`/`limit`/`set_account`/`set_limit`/
`undo`; its own page is `design/specs/2026-11-18-pipeline-control-surface/boundary.md`, promise
counts-and-limits-are-adjustments). Item: `RIMMANDRAKE_TYPE_SIX_MORE_CONSUMABLES_READERS_IN_LIVE_LANES`, written
2026-11-19. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_pipeline_control.py`; each test
was seen red on the code before this item, and turns red again under a deliberate break of its promise
(`python3 src/RimMandrake/rimflow/acceptance/consumable_readers_breaks_accept.py`, 8 of 8).

The fifteen consumables: six before this item (`granted_look`, `coverage_runs`, `coverage_not_covered`,
`coverage_malformed`, `blind_cycles_visit`, `blind_cycles_total`) and nine accounts for the six of this item:

| consumable | account | its reader | the pipeline's own limit |
|---|---|---|---|
| automatic in-game runs | `ingame_runs_visit` | `maturation_dispatch.decide_ingame` | `ingame_auto_runs_per_visit` |
| steward runs | `steward_runs`, `fixer_runs` | `maturation_autonomy._gate` | `steward_max_per_version` (both) |
| launch retries | `launch_tries` | `maturation_autonomy.tries_left` / `tries_most`, asked by every retry reader of the tick and of autonomy | `launch_tries` |
| chained design runs | `chain_runs_day` | `role_launch.chain_cap` (`chain_cap_view`, `chain_capped`, `chain_ask`), `maturation_autonomy.designer_chain` | `chain_max_per_day`, else `CHAIN_MAX_PER_DAY` |
| refusal counts | `refusals` (an item: `<Mod>@<version>` or an item id) | `refusal_contract.submit` (the item's alarm) | `ITEM_ALARM_AT` |
| the Test Pilot streak (added by `RIMMANDRAKE_TYPE_PILOT_STREAK_AS_ITEM_ACCOUNT_ALREADY_ORDERED`) | `pilot_streak` (an item id) | `testpilot_route.judge` (one item), `routed` (every open item, one store read: `control.subjects`) | `STREAK` |
| the stage spend ceiling | `spend_offline_build`, `spend_blind_challenge`, `spend_in_game`, in weighted tokens | `maturation_dispatch.stage_spend` (`ceiling_gate`, `refund`, `holder_cap`) | `stage_ceiling_tokens` |

## ACCEPTS (the only inputs the readers are built for)

- **an-account-by-mod.** A mod in the pipeline (`pipe` refuses another name with the nearest). A refusal account is an
  item the refusal counters hold, a `<Mod>@<version>` of a pipeline mod, or a mod, read as `<Mod>@<its version>`. A
  `pilot_streak` account is an item id (UPPER_SNAKE); `pipe` refuses a mod name, and takes an id the ledger does not
  hold yet (the account waits for it; `pipe show` measures nothing for it).
- **whole-numbers.** Every count and limit is a whole number; the spend accounts are weighted tokens,
  read as weighted tokens by the ceiling readers (a legacy dollar reading converts once, `role_launch.list_usd_to_weighted`;
  figures moved to weighted tokens 2026-11-26 at 250,000 per list dollar).
- **a-measure-pipe-can-see.** `pipe set` lands the count on N against the count `pipe show` measures. Where `pipe` has
  no measure now (the mod is not at that stage, its record cannot be read), it says so and pins the adjustment total
  instead (control.set_account).

## DOES NOT SURVIVE (not promised)

- **a-store-that-turns-unreadable-mid-tick.** The tick holds every mod when the store cannot be read (it reads the hold
  first). A store that turns unreadable between that read and a reader's raises out of the reader.
- **a-chain-count-on-an-unreadable-store.** `role_launch.chain_cap` reads the raw count and cap then; `chain_ask`'s
  owner hold read refuses on that store first, so nothing is chained, but ops_watch's stall reader sees the raw cap.
- **a-refusal-count-on-an-unreadable-store.** `refusal_contract.submit` alarms on the raw count and writes
  `control: UNMEASURED ...` into its result (the alarm tells and blocks nothing).
- **a-forgiven-refusal-in-a-window.** maturation_advance counts refusals over 24 h (FAMILY_TUNING). A negative
  adjustment outlives the window: once the forgiven refusals leave it, later ones are under-counted. Use
  `pipe limit`, or `pipe undo` the add, for a windowed family.
- **an-account-moved-for-a-past-stage.** A spend or launch-tries adjustment stays on its account when the mod moves on
  and comes back; a later visit to the stage reads it too.
- **one-launch-tries-account-per-mod.** `launch_tries` moves every failed launch of the mod at once (each counts its
  own tries); one launch cannot be given a try alone.
- **an-unreadable-maturation-record-reads-no-stage.** `pipeline_control.Ctx.stage` reads a mod's `record.json` through
  `maturation.load`, None for absent and unreadable alike, so `pipe show` prints stage `-` for an unreadable record
  (the record is written temp file + `os.replace`). Could-not-look lint read, 2026-11-19
  (`RIMMANDRAKE_READ_ONLY_FILES_THAT_FAILED_PILOT_FOUND_ZERO`); no fix (owner by card 2026-11-19).
- **a-refusal-subject-with-no-readable-version.** `reading` takes `refusal_subject`'s Refused (a mod whose version
  reads UNMEASURED) as "does not apply", so `pipe show` omits that mod's refusal row instead of printing it
  UNMEASURED. Same read, same ruling.

## PROMISES (each one is owed a test of the same name)

- **ingame-runs-read-the-store.** `pipe add|limit <Mod> ingame_runs_visit` changes whether `decide_ingame` reads the
  visit's automatic run spent; `pipe undo` and `limit default` put it back.
- **steward-runs-read-the-store.** `pipe add|limit <Mod> steward_runs` (and `fixer_runs`) changes whether `_gate` reads
  the mod's steward (fixer) runs spent.
- **launch-tries-read-the-store.** `pipe add|limit <Mod> launch_tries` changes whether a failed launch is retried, on
  the blind decision's path, autonomy's gate and the void sweep's (each entry's mod found by `entry_mods`); another
  mod's account is its own.
- **chain-runs-read-the-store.** `pipe add|limit <Mod> chain_runs_day` changes whether `chain_capped` holds the concept
  on the daily chain cap; the account is the concept folder's name.
- **refusals-read-the-store.** `pipe add|limit <item> refusals` changes whether `submit` raises the item's
  refused-verdicts alarm; an account the counters do not hold, and no pipeline mod, is refused.
- **stage-spend-reads-the-store.** `pipe add|limit <Mod> spend_<stage>` changes the ceiling gate at that stage (the
  offline build, the blind challenge, in-game) and a pilot holder's cap; one stage's account leaves the others; `pipe
  show <Mod>` prints it in weighted tokens.
- **pilot-streak-reads-the-store.** `pipe add|limit <ITEM> pilot_streak` changes whether `testpilot_route.judge`
  routes the item to a Test Pilot, and `routed` sees it too; another item's account is its own; `pipe undo` puts it
  back. An unreadable store routes by the derived count and the default limit only, and each streak verdict says the
  store is UNMEASURED.
- **every-limit-read-goes-through-the-store.** Every function in `rimflow/` and `Utils/` that reads one of the
  consumables' limit names (a constant, a settings key) calls `PC.used` or `PC.limit` for that consumable; every reader
  `RESOURCES` lists calls `PC.used`. The census counts what it saw, so a scan that saw nothing is not a pass.
- **one-line-each-with-its-undo.** For each of the nine accounts, `pipe set`, `add`, `reset` and `limit` are one line
  that prints at most 3 lines with its undo, and `pipe undo` takes the act back.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
