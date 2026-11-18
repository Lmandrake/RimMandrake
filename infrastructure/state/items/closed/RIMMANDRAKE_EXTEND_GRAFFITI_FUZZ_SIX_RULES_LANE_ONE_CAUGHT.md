# RIMMANDRAKE_EXTEND_GRAFFITI_FUZZ_SIX_RULES_LANE_ONE_CAUGHT

## spec
Graffiti 0.1.0 blind cycle 1 (design/concepts/Graffiti/version/blind_challenge/cycle_1/) planted six faults in
`src/RimMandrake/Graffiti/Source/Kernel/RM_GraffitiKernel.cs` that no builder offline suite catches (only the blind lane 1
does): FitBudget unbounded (a mood tax), VisitCharge recharging past the 12 cap, a numb (psychopath) temperament keeping
its good multiplier, CraftBeauty(Normal) non-zero, a scrawl's craft ceiling raised to Good, and a confront fight chance
above zero from nothing. T_FUZZ (`selftest_graffiti_fuzz.py`, SelfTest/GraffitiFuzz.cs) supports art_skill, temperament,
stories_not_tax, visitors and fights_reasons but pins none of these rules. Polish: T_FUZZ decides no bar.

## verify
Acceptance test (from the clone root, ~3 min):
`head -1 design/concepts/Graffiti/version/blind_challenge/cycle_1/lane2/planted_results.jsonl > /tmp/fz.jsonl && python3 design/concepts/Graffiti/version/blind_challenge/cycle_1/lane2/plant_faults.py --append --no-lane1 --expect-caught --out /tmp/fz.jsonl --only PF_K_BUDGET_UNBOUNDED,PF_K_VISIT_CAP_RECHARGES,PF_K_PSYCHO_FEELS_GOOD,PF_K_CRAFT_NORMAL_NONZERO,PF_K_SCRAWL_CEILING_GOOD,PF_K_FIGHT_FROM_NOTHING`
exits 0 (6 of 6 caught by a builder suite). Watched failing on base 8c4bced9e (rc 1, "EXPECT CAUGHT: FAIL, missed:" all six).
Expected: 1 pass. Fix: add these six properties to GraffitiFuzz.cs (the blind lane-1 rows mood_budget_conserved,
visit_goodwill_capped, temper_psycho_sensitive_ordinary, craft_beauty_both_ways, craft_ceiling_scrawl_poor,
fight_chance_bounded are the oracles), never weakening an existing assertion.

## criteria
- Each of the six planted kernel faults turns a builder offline suite red; no existing assertion weakened.
