A work bundle whose members are fixed at launch turns each new ready ticket of its home into a second bundle on the same files, started after the live one ends. The restart is already a fresh session from the state file, so it is the cheap place for the bundle to take those tickets: the lane writes them on the live record each applied tick (waiting), and the restart takes the ones still open. A ticket waiting when the bundle ends instead goes to the home's next bundle.
item: RIMMANDRAKE_FILL_BUNDLES_BY_HOME_HOLD_MEDIAN_ONE_TODAY
home: design/specs/2026-11-24-work-bundles/boundary.md
