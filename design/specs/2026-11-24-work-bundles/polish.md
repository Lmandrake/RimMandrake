# POLISH: work bundles (one line each, no ticket; beside `boundary.md`)

- `holder_bundle` does not mark an older `gated` record of the same mod `replaced` (`launch_bundle` does), so a stale gated block can stay on the page beside the new bundle.
- `group` bundles a `slots_full` row only when its system's lead row comes before it in the tick's rows.
- A `bundle_refused` stop row comes from any earlier bundle record of the member; whether `list_dispatch.py clear` lets the member run again is unchecked.
- `outcomes` reads `fixed` for any `done` close without checking that the close came after the bundle began (members are open at launch, so it is harmless today).
- not handled: `note_restart` sets `live` without checking that the bundle still reads `restarting`, so a step that starts after the bundle was gated or ended (an ambiguous kick that timed out but started, or `work_bundle.py end` on a bundle whose step waits for the account switch) makes it live again beside whatever the lane launched.
- `at_finish` decides "the kick started" by the text `kicked` in the kick's line, not by a field; a control refusal whose reason contained that word would leave the bundle `restarting`.
- `end_bundle` ends a bundle in any state, a `live` one with a running unit included; nothing checks that the unit is dead first.
