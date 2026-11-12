# Done claim

This round ran in the offline lane (no game). The STATEMENT that `wc.py` setup wrote has no usable bullets: it holds
an empty bullet and a fragment of the item file's "Depends on" line. Its prose `## criteria` paragraph was dropped, and
that bug is filed as lesson `infrastructure/state/lessons/20261112T053641Z-CLAUDE_STEVEDESKTOP_OFFLINE1-wc-py-statement-md-for-item.md`.
The real bar is therefore the item's own criteria: "Descent playable start-to-bottom on a quicktest-loaded save;
reveal flag published to the blackboard; stage 3 entered by this beat and only this beat." Its verify section asks
for the dev-flag matrix, once-only, refused re-triggers, the string-surface diff, the linter, Oracle-absent, the site
present per slot read with `jawa/list_things`, and the A1 lore. Everything that can be shown offline is shown below.
The live half (walking the site in a quicktest, and the per-slot `jawa/list_things` read) is not, so neither line is
"true".

- cannot tell: - | evidence: `whittle/cathedral_descent_reveal_site_1/evidence/reveal_beat_selftest.txt` `whittle/cathedral_descent_reveal_site_1/evidence/site_selftest.txt`
- cannot tell: - *Depends on:** item 1 (VOUCHED + flags), item 2 (stage-3 hum register), | evidence: `whittle/cathedral_descent_reveal_site_1/evidence/reveal_beat_selftest.txt` `whittle/cathedral_descent_reveal_site_1/evidence/lint_reveal_text.txt`

## What is shown (offline, on published main `2b51bf3116`)
- The trigger (`evidence/reveal_beat_selftest.txt`, 44/44 checks). The ordinary-play fixture has a colony climb
  WARY → TOLERATED → VOUCHED by doing its missions:
  - VOUCHED without the restore flag: no opening.
  - The restore flag without VOUCHED: no opening.
  - Regard forced to 1000 with no missions: no opening.
  - Both: exactly one opening, on the first VOUCHED poll (63), and the reveal flag set once when the descent quest
    ends in Success (poll 67).
  - `effective_stage` is 3 from that poll on and on no poll before it.
  - Re-triggers are refused on every later poll.
  - Demote and re-climb: still one opening.
  - A dev-made descent quest is never doubled.
  - The game refusing the first opening: it re-arms, then exactly one quest is made.
  - Runs with no `claude` on PATH.
- The site (`evidence/site_selftest.txt`, `evidence/descent_layout_topdown.png`):
  - a per-slot audit of the generated 250×250 layout;
  - every symbol resolves to a real def;
  - the terminus is placed exactly once, inside the bottom chamber;
  - a walkable 1045-cell path from the arrival edge;
  - the production line spans the map, and the coolant channel is present.
- The text (`evidence/lint_reveal_text.txt`): the opening passes at stage 2, and the address and the site's labels at
  their stages. The same address held to the stage-2 rules fails, which shows the linter can tell the two apart.
- The string surface (`evidence/string_surface_diff.txt`): all 3864 faction-visible strings are unchanged across both
  landings of this item.
- A1 (`evidence/a1_lore_landed.txt`): the receiver lore is in `03_deep_history.md` and `06_the_ship.md`, and the
  arc spec's card now points at both.

## What I'm least sure about
- Whether KCSG places the 2 MB layout as the generator intends, including which edge is north. The gen step handles
  both orders, so the arrival may come out on the south edge.
- Whether the patrolling Sentinels really walk past the party: the escort rides the pass's HostileTo postfix on that
  map only, with no hediff.
- Whether a caravan's entry cell lands in the arrival gap.
- The look: the halls render as large pillared rectangles. "Canyon-scale" has to be judged in the game.
- The restore choice is a story flag only. The §4 restore site has no quest, so in ordinary play the flag must come
  from `--story-flags-file`.

## What I did not test
- Anything in the game:
  - firing `RUT_CathedralDescent_Opening` with the bridge;
  - walking a quicktest party from the arrival edge to the terminus;
  - seeing the 5-page address and the archived letter;
  - the reading of a completed descent quest through `jawa/quest_lifecycle`;
  - per-slot presence through `jawa/list_things`;
  - load-time def errors.
- Leaving the site and coming back.
- Turret or splash damage on a Sentinel.
- A stale dispatch, where the opening is queued while the colony is demoted.
