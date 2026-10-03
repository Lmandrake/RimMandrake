# UnfinishedLine — validation walk
subject: src/RimUtinni/UnfinishedLine  (packageId `mandrake.rut.unfinishedline`)
deps: mandrake.rsw.droidworks, mandrake.rut.droidrepairjobs; the two factions come from mandrake.rut.patches
list: campaign factions (mandrake.rut.patches) + Droidworks + Droid Repair Jobs + this mod + all DLC; a world holding one Enclave and one Hive settlement
status-hint: The Unfinished Line, the Hive/Enclaves droid-production quest chain (design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md). Built: the chain spine, beat 1 "The Count" and beat 2 "The Envoy" with the brokered truce; the site choice, beats 3-5 and the line in the world are filed items.

## must be true
- Loads with no error naming this mod's defs or classes. → load_clean.no_errors_naming_this_mod
- The chain, beat 1, its incident, and both factions resolve. → defs.all_defs_resolve
- The offer gates report whether the chain can be offered and why not. → gates.gate_report_reads
- "Enable The Unfinished Line" OFF closes the offer gate. → gates.disabled_chain_closes_the_gate
- Offering and accepting the chain starts its spine. → chain.parent_offers_and_accepts
- The first beat offered is The Count. → chain.first_beat_is_the_count
- Only one beat is offered or running at a time. → chain.one_beat_at_a_time
- The Count's three droids arrive broken, as the Enclaves' people, and can be operated on at a repair bench. → UNCOVERED: needs the child accepted and the walk-in to land; first poke: accept The Count, read the lodgers' faction and RUT_DroidJobFault.
- The Count is judged by the worst droid: two good parts and one worn part grade Shoddy (+5), and the fee is paid per droid. → UNCOVERED: needs a 6-day timer and a part installed on each droid; grade logic is DroidRepairJobs' QuestPart_DroidRepairJobOutcome with gradeAllDroids.
- After the last built beat (The Pattern Cores) succeeds the spine offers nothing further until the next beat is built, and logs nothing. → UNCOVERED: needs completed children; read ProofChain (current none, successes 2/5).
- A beat that fails more times than "failures allowed per beat" ends the chain with no verdict and a letter. → UNCOVERED: needs failed children; ProofChain shows broken.
- The brokered truce holds the Hive at goodwill 0 or better (Neutral) while it runs. → truce.truce_holds_hive_neutral
- "The Enclaves broker a truce" OFF: no truce starts. → truce.truce_off_does_nothing
- Accepting The Envoy starts the truce; the overseers and escorts arrive as lodgers and leave after 4 days, paying Hive +15 / Enclaves +10. → UNCOVERED: needs The Count succeeded first; first poke: ProofNextBeat after a forced Count success, accept, read ProofTruce and the lodgers.
- An envoy killed or arrested breaks the truce (Hive hostile) and fails the whole chain, not just the beat. → UNCOVERED: needs an accepted Envoy; kill an overseer, read ProofChain (CHAIN EndedFailed) and the Hive relation.
- The storyteller offers the chain only past day 30 with Enclave goodwill 20, shop repair researched, and both factions holding a settlement. → UNCOVERED: the gate logic is read by gates.gate_report_reads; the storyteller firing itself is never waited on.
- Wild droids in the foundry ruin are one pack: never hostile to each other, always hostile to you. → wild_pack.pack_does_not_fight_itself
- After two beat successes the spine offers The Pattern Cores. → cores.beat3_offered_after_two_successes
- With all three cores on a home map the 12-day timer stops and the Imperial broker's offer arrives. → cores.cores_home_raises_the_broker
- Selling the cores fails the whole chain (the beat tells the parent through QuestPart_RUT_SignalParent) and turns the Hive and the Enclaves hostile. → cores.selling_fails_the_chain
- Refusing the broker, or letting the offer lapse, sends the cores to an Enclave courier: Hive +10 / Enclaves +10, beat 4 next. → UNCOVERED: ProofCores refuse then ProofChain (successes 3/5).
- The ruin site holds a collapsed steel hall, the three cores inside, and 2 to the setting's maximum wild droids scaled by threat points. → UNCOVERED: needs a caravan to the site; first poke: accept the beat, send a caravan, screenshot the hall.
- A wild droid from the ruin captured and released without a restraining bolt pays Enclave goodwill; released bolted, nothing. → UNCOVERED: needs a capture; read the Enclave goodwill before and after the release.

## anti-guessing notes
- QuestPart_SubquestGenerator (decompiled 1.6) picks no order itself; Relic Hunt's subclass shuffles. Our spine walks `beats` by success count; failures are counted from the parent's subquests in EndedFailed.
- An IncidentDef with questScriptDef AND a non-zero rootSelectionWeight is a ConfigError (IncidentDef.cs:235), so the parent is isRootSpecial, weight 0.
