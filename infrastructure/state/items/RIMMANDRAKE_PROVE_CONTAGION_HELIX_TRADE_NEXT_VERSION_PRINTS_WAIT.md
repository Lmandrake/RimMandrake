## spec
Contagion Design Version 0.2.0 (Divergent), Helix trade: draftprints (the scan of a living Unfinished), Helix contracts
that buy a matching print for silver and an optional device by drop pod, and the Helix Curators caravan. Moved out of
0.1.0 by his ruling (owner 2026-11-16 ~07:12 PST, OWNER:1794842455892769878): *"Defer Helix trade to next version."* Counted in: draftprints, because a print exists to
answer a Helix contract (the leaf prints_pay said so). The code stays built; 0.1.0 is to ship `draftprintsEnabled`
default false (no scan option, no contract; owed build RIMMANDRAKE_BUILD_CONTAGION_DEFERRED_SWITCHES_OFF_SUITE_OPTS_IN). The curator trader def `RM_HelixCurators.xml` ships; its faction attachment is the
campaign patch's (`mandrake.rut.patches`), outside this mod's switches.

## verify
When 0.2.0 opens: the Designer writes prints_pay and sc_helix_trade back, the coverage judge finds neither gap below.

## criteria
Acceptance test: the Contagion coverage judge's would_pass text, verbatim, from verdict rm-coverage-judge-1794821839:
- g19 (`draftprints, helix_contracts`, scenes.json sc_prints_pay): The expect reads the Monstrous flag, extreme stat and failure in the print's inspect text, the label unchanged after a save-reload, the provocation chance (or a forced provoke), and the device drop pod when the contract offers one.
- g25 (`helix_trade`, scenes.json sc_helix_trade): The start asserts the campaign patch's packageId is in the active list (else UNMEASURED), or spawns RM_HelixCurators directly and says so.
Not runnable at filing: live scenes with no script yet (watched fail: not possible offline).
