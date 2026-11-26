# BOUNDARY: a Stage 8 walk that does not pass is recorded and sent back with its findings, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`walk_result`, `read_walk_result`, `walk_items_open`, the `walk-result`
verb, `owner_event(may_refuse_pass=True)`, the `walk_items_closed` clause of the move to `his_walk`) and
`src/RimMandrake/rimflow/maturation_autonomy.py` (`adopt_walk_road_back`, the `walk` fixer brief). Item
`RIMMANDRAKE_ROUTE_FLOWWORKS_WALK_TWO_FINDINGS_BACK_ELEVEN_FILED`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_walk_result.py`.

The case (2026-11-22, FlowWorks 0.1.0): the owner walked the mod at Stage 8 and ended the walk with "Ok, release my
FlowWorks walkthrough." It did not pass. The pipeline had no record for a walk that does not pass:
- `rimflow walk done FlowWorks` refused, because that verb is for items, not mods.
- `maturation.py advance --to <road back>` wrote no findings and read none of his words.
- The tick opens a road back only for a steward run that it launched itself. Stage 8 has no such run, so the tick would
  never have launched a fixer on his findings.
- The move to `his_walk` read only the walk brief. So the mod reached his walk again while his findings of 2026-11-20
  were open (walk brief arrival 2, "What I noticed first", point 5).

## ACCEPTS

- **a-record-at-his-walk.** The stage record stands at `his_walk`. `pre_human_arrivals` is N, the walk brief arrival
  that he walked.
- **his-event.** `--owner-said OWNER:<tsn>` names his event on the OWNER shard that ends the walk. Its words may refuse
  the pass. A Conductor decision (`--conductor-decision`) is also accepted, for a road back that the Conductor orders
  before he walks.
- **named-items.** `--fix`, `--pick`, `--scene` and `--next` each take rimflow item ids, comma-separated. `--group`
  takes `A+B` (one fixer run for both), repeatable.
- **a-drawn-road.** `--to` is a road back that `ROADS_BACK["his_walk"]` draws.

## DOES NOT SURVIVE (not handled)

- **a-walk-at-another-stage.** An early look while the mod is at another stage is not a Stage 8 walk. Record it on its
  items with `rimflow note`, as before.
- **a-walk-result-edited-by-hand.** The result file is written once by the verb. A hand edit is read as written.
- **an-item-renamed-after-the-walk.** The walk gate reads the ids written in the result. A superseded item is closed.
- **a-tick-state-from-before-this-page.** A tick road back opened before this change is replaced only when the walk
  move is newer than it.

## PROMISES (each one is owed a test of the same name)

- **walk-result-records-not-passed.** `walk_result` writes `version/walk_brief/walk_<N>_result.json` and
  `walk_<N>_result.md` once, with `verdict: not_passed`, his event, and each list. It moves the record from `his_walk`
  to `--to` in the same locked write. The move's `confirmed.walk_result` names the json file.
- **walk-result-refuses-off-stage.** At any stage other than `his_walk`, `walk_result` writes nothing and says why.
- **walk-result-refuses-unknown-item.** When a named id has no ledger event, `walk_result` writes nothing and names the
  id.
- **walk-result-refuses-second-write.** When `walk_<N>_result.json` exists, `walk_result` writes nothing.
- **road-back-takes-his-refusing-words.** `walk_result` accepts his event even when his words refuse the pass. A move
  to `passed` on the same event is still refused on `owner_said`.
- **road-back-takes-conductor-decision.** `walk_result` with a Conductor decision and no event of his is accepted;
  with neither it writes nothing. A move to `passed` with only a Conductor decision is still refused on `owner_said`.
- **walk-gate-holds-on-open-item.** The move `pre_human` to `his_walk` refuses on clause `walk_items_closed` while an
  item of the last walk result's `fix`, `pick` or `scene` list is open, and names each open item. It passes when each
  one is closed, dropped or superseded. `next` items do not hold it.
- **walk-gate-unreadable-result-refuses.** A walk result file that cannot be parsed refuses `walk_items_closed`, and the
  observed text names the file. It never reads as no items.
- **tick-adopts-walk-road-back.** When the record's last move is from `his_walk` with a `walk_result` and the tick
  state has no road back, or an older one, `adopt_walk_road_back` sets `road_back` to `{caused_by: <the result's item>,
  at: <move time>, from: his_walk, cited: <fix + scene ids>, walk_result: <path>}`. `pick` and `next` ids are never
  cited, so they get no fixer run.
- **tick-runs-no-fixer-on-pick-or-next.** The open items of a walk road back are its `cited` ids only. An item filed
  with `caused_by` the route item that the result does not list in `fix` or `scene` (a pick, a next-version item,
  another mod's ticket) is not returned and gets no fixer run. The case: the route run of FlowWorks walk 3
  (2026-11-25) files every ticket of the walk with `caused_by` the route item.
- **tick-books-a-live-run-on-a-cited-item.** When an open item of the road back has a detached run that is launching or
  running, the tick books that run as the item's one fixer run and starts no second run on it, while it runs or after
  it ends. When every open item is booked and one still runs, the row reads `live` and names the run. The case: the
  Conductor launched the water drill of FlowWorks walk 3 before the walk result named it.
- **tick-adopts-once.** A second call on the same move changes nothing. After the tick pops that road back (every item
  closed), the same move does not open it again.
- **walk-fixer-never-drops-his-finding.** The fixer brief of a walk road back says that the item is his finding,
  forbids a drop as "not worth the touch", and names the group partners to fix in the same run.
