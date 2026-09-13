
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §3 bullet 3. TOLERATED: first mission offers against the Assailant
register arrive via droid/enclave channels — never attributed to the
Cathedral (linter-enforced). VOUCHED: gravtech boons (plot-tier per
`03_deep_history.md`) open, each priced against **current Imperial Heat** —
when the Empire is looking, it does not act; boons suspend on the dark flip.
Surface: CQF quest/letter or bridge-injected letters (kyber §7 lane,
inheriting its CQF caveat); offers keyed off item 1's stage + Heat read.
Completion feeds Regard (item 1 input). Fallback text ships first; Oracle
upgrades voice only. NEW defNames (flag): quest/letter defs
`RUT_CathedralAssailantMission_*`, boon defs as the gravtech content pass
names them — coin the minimum, RUT_ tier.

## verify
Offer appears only at correct stage; quest-giver string passes item 3's
linter (no Cathedral attribution pre-stage-3); boon availability flips with a
shadow-mode Heat change; dark flip closes both; every beat completes Oracle-
absent; K2 anti-laundering: completing missions scrubs zero Heat.

## criteria
≥1 Assailant mission shape + the boon-offer gate live end to end on a
quicktest; Regard feedback observed in shadow logs.

**Depends on:** item 1; item 3 (linter); CQF-vs-thin-config reconciliation
(build_plan §6.1 — inherited caveat, assume CQF like kyber). **Waited on
by:** item 7 (VOUCHED must be reachably earnable). **Seat/needs:** FOUNDRY;
quest authoring (rimworld-quests skill) + bridge + quicktest.
