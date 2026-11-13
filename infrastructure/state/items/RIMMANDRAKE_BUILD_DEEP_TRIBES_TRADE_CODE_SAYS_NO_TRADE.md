# RIMMANDRAKE_BUILD_DEEP_TRIBES_TRADE_CODE_SAYS_NO_TRADE

## spec
Owner, 2026-11-13 (on RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES, walk_season_on_the_pyre): *"But then the Deep Tribes come: learning to watch rather than confront. Offer trade and leave them their share, and you'll
be ok."*

Partial (read 2026-11-13 at a68d89e622). Exists: the fire rite (`src/RimUtinni/PyrelandsMechanics/Source/PyrelandsFireRite.cs`,
`LordJob_RUT_FireRite.cs`: arrive, light, harvest, leave with the fruit), the flame-harvest visit (`IncidentWorker_FlameHarvest.cs`)
and arson-justice raids for the colony's own burns (`IncidentWorker_FireRaid.cs`). Missing, in the code's own words: "No trade, no
quest hook, no scorch-fruit handout" (`IncidentWorker_FlameHarvest.cs:29`, deferred to ECONOMY_TRADE_SWEEP_1 (what is sold where
and when)). Nothing tracks "their share": the colony stripping a rite burn first costs nothing, and attacking a rite party only
makes it walk off (vanilla goodwill is the whole cost). Owed: (1) Designer pass: what the Tribes trade (a trader on the rite or
harvest party, what they buy and sell, which may need ECONOMY_TRADE_SWEEP_1), what "their share" is and what taking it costs,
what confronting them costs beyond vanilla goodwill; (2) the build; (3) Mod Settings per the superb-settings rule.
Census and walk criteria: `D:\ClaudeWork\rimmandrake\conductor\cards_20261113_am\walk_season_criteria.md`.

Acceptance test: none, the trade stock and the share rule are design not yet argued out; the Designer's spec writes the
red-first test (a kernel row on the share-taken goodwill change, a def row on the party's trader kind).
