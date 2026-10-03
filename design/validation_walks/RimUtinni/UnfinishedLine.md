# UnfinishedLine — validation walk
subject: src/RimUtinni/UnfinishedLine  (packageId `mandrake.rut.unfinishedline`)
deps: mandrake.rsw.droidworks, mandrake.rut.droidrepairjobs; the two factions come from mandrake.rut.patches
list: campaign factions (mandrake.rut.patches) + Droidworks + Droid Repair Jobs + this mod + all DLC; a world holding one Enclave and one Hive settlement
status-hint: The Unfinished Line, the Hive/Enclaves droid-production quest chain (design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md). Built: the chain spine and beat 1 "The Count"; beats 2-5 and the line in the world are filed items.

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
- After The Count succeeds the spine offers nothing further until beat 2 is built, and logs nothing. → UNCOVERED: needs a completed child; read ProofChain (current none, successes 1/5).
- A beat that fails more times than "failures allowed per beat" ends the chain with no verdict and a letter. → UNCOVERED: needs failed children; ProofChain shows broken.
- The storyteller offers the chain only past day 30 with Enclave goodwill 20, shop repair researched, and both factions holding a settlement. → UNCOVERED: the gate logic is read by gates.gate_report_reads; the storyteller firing itself is never waited on.

## anti-guessing notes
- QuestPart_SubquestGenerator (decompiled 1.6) picks no order itself; Relic Hunt's subclass shuffles. Our spine walks `beats` by success count; failures are counted from the parent's subquests in EndedFailed.
- An IncidentDef with questScriptDef AND a non-zero rootSelectionWeight is a ConfigError (IncidentDef.cs:235), so the parent is isRootSpecial, weight 0.
