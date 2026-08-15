# spending-a-load.md — the three habits, in full

The headlines are in `SKILL.md` §2. This is the reasoning behind each — open it
when you are actually planning a load: deciding what can ride along in a batch, or
deciding what to harvest once the game is up.

## Verify everything verifiable offline, first

Defs, About.xml, ModsConfig.xml and the whole Workshop tree are ordinary files
sitting on disk right now. Run `scripts/validate_patch.py`, parse every XML you
touched, confirm the load order in `ModsConfig.xml` rather than trusting the
manager's UI, and cross-check def references by grepping the mods themselves.
Anything you can establish from files, establish from files. A restart should be
confirming a prediction, not conducting an experiment.

## Batch by risk, not by count

The one-change-at-a-time rule exists to keep attribution possible when something
breaks — it is about *ambiguity*, not about quantity, so batch anything whose
effects are distinguishable. Config-level changes (load order, mod settings,
un/subscribes) carry near-zero attribution risk and should always ride along. A
pure-XML patch that validated clean and has named log strings to check is also
safe to include, because you know exactly what evidence would convict it. Keep
genuinely ambiguous changes solo: a new C# assembly, a mod that patches broadly,
or two changes that touch the same system. Say out loud which bucket each pending
change is in before proposing a batch.

## Harvest the whole log, not just your change

After a restart, read the entire `Player.log` and update the triage list — the mod
that just broke unrelatedly, the new unresolved reference, the count that moved.
You paid for a full load; a single yes/no answer is a poor return on it. Keeping a
running "next restart" queue between loads is what makes this cheap: changes
accumulate in a list, and each load clears the list and refills the evidence.

*(Triage order once you have the log: `references/player-log-triage.md`.)*
