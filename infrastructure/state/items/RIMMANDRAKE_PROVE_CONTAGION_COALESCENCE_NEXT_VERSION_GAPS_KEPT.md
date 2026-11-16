## spec
Contagion Design Version 0.2.0 (Divergent), the Coalescence: formation, growth and absorption, the manhunter emission and
its map-wide cap, the waiting pressure (his certified d_efa_q08), the Burn-collapse payoff into Monstrous samples, and
touched exposure from Coalescence contact. Moved out of 0.1.0 by his ruling (owner 2026-11-16 ~07:12 PST, OWNER:1794842455892769878): *"Everything about the
Coalescence is next version."* The code stays built (`Building_RM_Coalescence.cs`, `RM_CoalescenceKernel.cs`); 0.1.0
is to ship it switched off (`coalescenceEnabled`
default false, owed build RIMMANDRAKE_BUILD_CONTAGION_DEFERRED_SWITCHES_OFF_SUITE_OPTS_IN). The moved leaves, scenes and rows are listed in
`design/concepts/Contagion/later_version.md`; the scenes are recoverable from git at `e620e75af1`
(`design/concepts/Contagion/scenes.json`: sc_coalescence_grows_and_breaks, sc_waiting_costs_more, sc_coalescence_forms).

## verify
When 0.2.0 opens: the Designer writes these back as leaves and scenes, the coverage judge finds none of the gaps below,
and the live scenes run on the bridge (UNRUN until then).

## criteria
Acceptance test: the Contagion coverage judge's would_pass text, verbatim, from verdict rm-coverage-judge-1794821839:
- g1 (`coalescence_payoff, coalescence_grows_and_breaks`, scenes.json sc_coalescence_grows_and_breaks): sc_coalescence_grows_and_breaks (or a new scene) expects: the second Coalescence, destroyed by gunfire, leaves less mulch than the Burn-collapsed one and zero Monstrous samples; and one Coalescence collapses in a natural Burn with samples.
- g2 (`coalescence_threat, coalescence_grows_and_breaks`, scenes.json sc_waiting_costs_more, sc_coalescence_grows_and_breaks): A scene arm runs emission until the count reaches the cap (for example a stage-3 Coalescence held long) and reads that the count equals the cap and stays there for N emissions.
- g3 (`waiting_costs_more`, scenes.json sc_waiting_costs_more): The start asserts N colonists ordered to the site at each stage, and the action reads their touched severity and the manhunters' reach toward them at stage 1 and at stage 2.
- g24 (`coalescence_formation, coalescence_growth`, scenes.json sc_coalescence_forms, sc_coalescence_grows_and_breaks): A second formation-clock jump forms no second Coalescence, and the inspect string names mass and stage, matching the comp.
Not runnable at filing: every arm is a live scene on a Contagion map, and its script does not exist yet (watched fail:
not possible offline; the scenes left the 0.1.0 tree in this change).
- g7, its Coalescence half: a colonist adjacent to a Coalescence gains the touched hediff.
