You are reviewing a design study and two Claude Code skills for a RimWorld 1.6 (all DLC) total-conversion
campaign: a fixed crew of ~6 Jawa-like scavengers on ONE hand-made frozen planet (no worldgen, no random
settlements), ship-centred travel, scarcity, "qualitative danger, never stat inflation", vanilla Randy storyteller.
The owner is retiring several third-party event/crew mods and ordered us to extract their design wisdom so we can
write our own small custom incidents/quests. The attached files are: the study doc, and both skills (SKILL.md plus
references). Engine claims marked VERIFIED were checked against decompiled 1.6 source; others are UNVERIFIED.

Please, with high rigour and concretely (cite class/method/field names you are confident exist in RimWorld 1.6;
mark anything you are not sure of as "unsure"):

1. CRITIQUE AND FILL GAPS in the study: wrong or overstated claims, missing mechanisms, missing failure modes,
   and missing engine facts that matter for writing incidents/quests (e.g. Storyteller.TryFire vs
   IncidentWorker.TryExecute semantics, IncidentQueue, letters/ChoiceLetter timeouts, Dialog_NodeTree pausing and
   saving with a modal open, WorldPawns GC/KeepForever, lords, quest signals).
2. CHECK THE RECIPES FOR ENGINE PITFALLS: QuestScriptDef/Slate usage, IncidentWorker gating (CanFireNow vs
   CanFireNowSub, forced, bypassStorytellerSettings), save/load (Scribe, statics, closures), storyteller
   interaction (category weights, population intent, refire tags, RecordIncidentFired), Harmony targets
   (GeneratePawns postfix with an iterator, FactionCanBeGroupSource), FloatMenuOptionProvider in 1.6.
3. EXPAND THE IDEA CATALOGUE with 8-12 more ideas that fit this scenario (each: situation, mechanism sketch, cost
   S/M/L, which studied pattern it reuses), and flag any existing idea that violates the rulings above.
4. IMPROVE THE SKILLS' WORDING AND STRUCTURE: descriptions (triggering), section order, what to cut, what is
   missing from the recipe/traps, and any trap that is mis-stated. Give concrete replacement text where useful.

Output format: Markdown with sections 1-4, each a numbered list of findings; for each finding say SEVERITY
(high/medium/low), WHERE (file + section), WHAT is wrong or missing, and the PROPOSED TEXT or change. End with a
"Top 5 changes" list in priority order. Be concise; no preamble.
