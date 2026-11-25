DebugSettings.enableRandomDiseases gates only StorytellerComp_Disease. A pawn whose trait degree has randomDiseaseMtbDays (vanilla: Immunity -1, Sickly, 30 days) still rolls its own disease in Pawn_HealthTracker with the storyteller off. A quiet test site must take the trait off (helpers.disease_traits_off), across every map, because modcheck's site hold runs before the chain makes its site current.
item: HARNESS_REPAIR_CAUSE_6236AE26_2
home: skills/live-debugging-proof-harness
