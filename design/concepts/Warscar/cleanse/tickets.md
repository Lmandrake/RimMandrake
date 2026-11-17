# Warscar proposal tickets

Design tickets only. No code, game, bridge, ledger or neighbouring tree changed. Built extras keep code and defs. Each switch below is labelled “Next version”, defaults off on a fresh settings profile, and gates every creation and effect route. Existing saves preserve identities and owned things; switching off cancels/refuses new extra work with a reason, never deletes a pawn. A fresh-map absence read counts active/spawned things and reachable recipes/jobs/letters/incidents, not mere loaded DefDatabase entries. “On” evidence uses the named preconditions, not an accidental random roll. All tests include all DLC, current source/runtime fingerprints, all kept mechanics on, ordinary weather unlocked, and a clean-log reading. These are acceptance tests for tickets and regressions, not additional passing bars.

## T01: The wall-colossus encounter

Scope: totchak.

Work: totchakEnabled=false; block its genstep, wake triggers, gnaw/sleep jobs and waking letter. Preserve the pawn/defs; do not substitute a new wildAnimals row. When enabled, preserve ruin-before-player wall choice and the ruled permission to eat player walls.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no wall-colossus spawned, wake/gnaw/sleep jobs or letter on a fresh Warscar map; on: an eligible ruin gap generates a dormant animal and demolition starts its ruled wake/feeding loop. Read the log in each branch and require no new exception/warning storm.


## T02: chotrix

Specific disposition: chotrix — One/two genstep hunters, stock cloak, strike reveal, lone-prey search, night humanlike gate, one-attack hunt jobs, hurt-after-strike flight and target company revalidation. huntJob is explicitly unsaved, so post-load protection is a risk, not proven.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_Chotrix.cs; independently read current file. RM_ChotrixOnMap genstep -> CompChotrix ticks and hunt/flee think-tree; strike Harmony hooks; registry reset.

Scope: chotrix chotrix_signs lacquer_cloak.

Work: chotrixEnabled=false, chotrixDragEnabled=false, lacquerCloakEnabled=false; block genstep, invisibility/hunt/drag/shimmer/silence, lacquer output and tailoring access. Keep generic invisible-walker prints. Never shorten the ruled permanent lacquer lifetime.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no generated chotrix, hunt/drag jobs, moving silence, lacquer butchery output or reachable cloak recipe; on: an eligible hunter produces clues, attacks eligible lone prey, and lacquer cloak route works without a time expiry. Read the log in each branch and require no new exception/warning storm.


## T02a: chotrix signs

Specific disposition: chotrix_signs — Settled-film race print override via shared grid, camera-local tick suppression via choir, moving heat shimmer, fresh-kill carry job to cover, drag surface marks and held-corpse cleanup. Kill association is unsaved; no claim that every post-load kill is dragged.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_ChotrixSigns.cs; independently read current file. Chotrix strike/kill hooks -> drag giver/job and shimmer; GeigerChoir.Silenced -> CompChotrix.All; film race override -> shared track writer.

Scope: chotrix chotrix_signs lacquer_cloak.

Work: chotrixEnabled=false, chotrixDragEnabled=false, lacquerCloakEnabled=false; block genstep, invisibility/hunt/drag/shimmer/silence, lacquer output and tailoring access. Keep generic invisible-walker prints. Never shorten the ruled permanent lacquer lifetime.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no generated chotrix, hunt/drag jobs, moving silence, lacquer butchery output or reachable cloak recipe; on: an eligible hunter produces clues, attacks eligible lone prey, and lacquer cloak route works without a time expiry. Read the log in each branch and require no new exception/warning storm.


## T02b: lacquer cloak

Specific disposition: lacquer_cloak — Permanent lacquer output and craftable cloak: still, unseen, awake-hostile LOS/radius, light-ledger exclusion, unequip reveal. Apparel ticker repaired to Normal; effect is not time-limited and does not cloak ships.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_Chotrix.cs:266; independently read current file. RM_Chotrix.xml butcher product -> RM_CloakLacquer.xml crafting -> apparel comp ticker -> stock invisibility; LightLedger denial.

Scope: chotrix chotrix_signs lacquer_cloak.

Work: chotrixEnabled=false, chotrixDragEnabled=false, lacquerCloakEnabled=false; block genstep, invisibility/hunt/drag/shimmer/silence, lacquer output and tailoring access. Keep generic invisible-walker prints. Never shorten the ruled permanent lacquer lifetime.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no generated chotrix, hunt/drag jobs, moving silence, lacquer butchery output or reachable cloak recipe; on: an eligible hunter produces clues, attacks eligible lone prey, and lacquer cloak route works without a time expiry. Read the log in each branch and require no new exception/warning storm.


## T03: war dust

Specific disposition: war_dust — Sweep workgiver/job converts film thickness to dust, larger crater yield and direct toxic handling dose; does not treat a dome as protection against touching dust.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_Settling.cs:647; independently read current file. RM_SettlingJobs.xml sweep workgiver -> JobDriver_RM_SweepWarDust in RM_Settling.cs -> dust product and handling dose.

Scope: war_dust dust_uses.

Work: warDustEnabled=false and warDustBlightCureEnabled=false; gate workgiver, jobs, products and both recipes. Vanilla cleaning still removes film; it yields no dust and no handling dose. Toxic film does not require harvesting.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: ordinary cleaning yields no RM_WarDust, dust jobs or dust recipes, and cures no blight; on: designated film sweeps give dust and its three stated uses are reachable. Read the log in each branch and require no new exception/warning storm.


## T03a: dust uses

Specific disposition: dust_uses — Grower haul/dust job cures blight while retaining plant and doses handler; XML tox-gas shell and dye-stretch recipes.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_WarDustUses.cs; independently read current file. RM_WarDustRecipes.xml recipes; RM_WarDustUses.cs blight workgiver/job and vanilla blight interception; no signature caller needs them.

Scope: war_dust dust_uses.

Work: warDustEnabled=false and warDustBlightCureEnabled=false; gate workgiver, jobs, products and both recipes. Vanilla cleaning still removes film; it yields no dust and no handling dose. Toxic film does not require harvesting.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: ordinary cleaning yields no RM_WarDust, dust jobs or dust recipes, and cures no blight; on: designated film sweeps give dust and its three stated uses are reachable. Read the log in each branch and require no new exception/warning storm.


## T04: Buried-shell minesweeper

Scope: ordnance.

Work: Set ordnancePerMap=0 and add an explicit next-version master; gate hidden cell placement, RevealCheck, messages, shell commands, jobs and loot. A disabled hidden cell cannot suppress film. Preserve real-weapon triggering when enabled.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: buried list empty, no shell thing, reveal message, command, job or loot; forced former shell coordinates receive ordinary film. On: eligible buried cell is revealed by film and commands/jobs exist. Read the log in each branch and require no new exception/warning storm.


## T05: mark

Specific disposition: mark — Hourly map accrual, severity fade and saved permanent floor, staged mood and Wander_Sad, excludes other family marks; interval floor fix is present. Mental-state givers in XML have no off-biome gate, unlike the earlier ruling that nightmares end on departure.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_WarscarMark.cs; independently read current file. RM_MapComponent_WarscarMark -> accrual and floor comp; HediffDefs mentalStateGivers; snap depends on static biome lookup, not the hediff.

Scope: mark mark_trade loosened_panels.

Work: markEnabled=false, markFloorEnabled=false, markTradeBonusesEnabled=false, loosenedPanelsEnabled=false; gate accrual, startup stat edits, mental states, cache generation, commands and work. Keep RM_WarscarMark.Warscar as a biome lookup for snap; move lookup to neutral helper if necessary, never require mark accrual. Preserve permanent floor/no stacking when enabled; repair off-biome nightmare discrepancy before enabling.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: fresh pawns gain no Warscar mark, stat bonus, nightmare, panel/cache, panel job or letter, while wild scaria chatrak still arm; on: mark accrues, no-stack/permanent floor works and caches open for the marked pawn; leaving ends nightmares as previously ruled. Read the log in each branch and require no new exception/warning storm.


## T05a: mark trade

Specific disposition: mark_trade — Hacking/mech-butchery/smelting stage offsets; restart-only bonuses toggle; a benefit attached to the retained mark, not another separate XP system.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Defs/HediffDefs/RM_WarscarMark.xml; independently read current file. RM_WarscarMarkStartup edits mark hediff stage offsets; no independent XP engine.

Scope: mark mark_trade loosened_panels.

Work: markEnabled=false, markFloorEnabled=false, markTradeBonusesEnabled=false, loosenedPanelsEnabled=false; gate accrual, startup stat edits, mental states, cache generation, commands and work. Keep RM_WarscarMark.Warscar as a biome lookup for snap; move lookup to neutral helper if necessary, never require mark accrual. Preserve permanent floor/no stacking when enabled; repair off-biome nightmare discrepancy before enabling.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: fresh pawns gain no Warscar mark, stat bonus, nightmare, panel/cache, panel job or letter, while wild scaria chatrak still arm; on: mark accrues, no-stack/permanent floor works and caches open for the marked pawn; leaving ends nightmares as previously ruled. Read the log in each branch and require no new exception/warning storm.


## T05b: loosened panels

Specific disposition: loosened_panels — Genstep replaces spaced ruin-wall slots with visible panels holding saved cacheDef; deepening-mark refusal/menu and work job; open spawns the assigned sealed-crate type. Cache object/contents are created on opening, not physically pregenerated behind the wall.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_LoosenedPanel.cs; independently read current file. RM_LoosenedPanels genstep -> panel building CanWork -> RM_WorkPanelLoose job -> cached crate Def on completion.

Scope: mark mark_trade loosened_panels.

Work: markEnabled=false, markFloorEnabled=false, markTradeBonusesEnabled=false, loosenedPanelsEnabled=false; gate accrual, startup stat edits, mental states, cache generation, commands and work. Keep RM_WarscarMark.Warscar as a biome lookup for snap; move lookup to neutral helper if necessary, never require mark accrual. Preserve permanent floor/no stacking when enabled; repair off-biome nightmare discrepancy before enabling.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: fresh pawns gain no Warscar mark, stat bonus, nightmare, panel/cache, panel job or letter, while wild scaria chatrak still arm; on: mark accrues, no-stack/permanent floor works and caches open for the marked pawn; leaving ends nightmares as previously ruled. Read the log in each branch and require no new exception/warning storm.


## T06: old tongue

Specific disposition: old_tongue — Intellectual-gated, once-only analyzable panels, chalk mark, 2/3/3 panel analysis sets and research flags, map-spanning unread-panel tooltip, skips completed sets at placement. Read panels unlock research prerequisites; they do not instantly finish research or advance campaign lore.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_OldTongue.cs; independently read current file. RM_InscribedPanels genstep -> CompInscribedPanel analyze -> RM_OldTongue research flags; hospice/pool callers read those flags; research tooltip hook.

Scope: old_tongue rest_transcriptions transcription_premium.

Work: oldTongueEnabled=false; block analyzable panels, rest rewards/finds, transcription drops, trade premium and research unlocks. Close unlocked/free build routes in the downstream screens/pools/hospice as well. Do not erase learned research from old saves.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no new panel, analysis job, transcription, premium, research reward or discovery message; on: eligible analysis grants its own prerequisites and transcription through ordinary work; no free completed research. Read the log in each branch and require no new exception/warning storm.


## T06a: rest transcriptions

Specific disposition: rest_transcriptions — Rest panels feed selected research, every-Nth game-wide read reveals a nearby crate/chassis, saved read count, physical transcription after reads; campaign Antiquities supplies artifact treatment.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_OldTongue.cs:148; independently read current file. Inscribed rest panel analysis -> ReadRestPanel -> RevealFind and DropTranscription -> RM_OldTongueGame saved count.

Scope: old_tongue rest_transcriptions transcription_premium.

Work: oldTongueEnabled=false; block analyzable panels, rest rewards/finds, transcription drops, trade premium and research unlocks. Close unlocked/free build routes in the downstream screens/pools/hospice as well. Do not erase learned research from old saves.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no new panel, analysis job, transcription, premium, research reward or discovery message; on: eligible analysis grants its own prerequisites and transcription through ordinary work; no free completed research. Read the log in each branch and require no new exception/warning storm.


## T06b: transcription premium

Specific disposition: transcription_premium — Data-driven faction buy-premium extension and PlayerSells-only Tradeable postfix, with gift/currency/session guards. Free tier has the hook; named premium buyers come from the campaign patch.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_OldTongue.cs:238; independently read current file. Tradeable price Harmony postfix -> RM_FactionBuyPremium extension; named campaign buyers unknown locally.

Scope: old_tongue rest_transcriptions transcription_premium.

Work: oldTongueEnabled=false; block analyzable panels, rest rewards/finds, transcription drops, trade premium and research unlocks. Close unlocked/free build routes in the downstream screens/pools/hospice as well. Do not erase learned research from old saves.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no new panel, analysis job, transcription, premium, research reward or discovery message; on: eligible analysis grants its own prerequisites and transcription through ordinary work; no free completed research. Read the log in each branch and require no new exception/warning storm.


## T07: hospice rings

Specific disposition: hospice_rings — Kneeling rings around ancient-wall centroid, slagged/posed deconstruction and chance cores, 0..cap intact minified chassis; random history/name saved on intact machines.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_Hospice.cs:521; independently read current file. RM_KneelingRings genstep -> kneeling chassis comp, saved name/history and deconstruction/core routes.

Scope: hospice_rings deserter_histories hospice_revival hospice_failure deserter_walkin.

Work: hospiceEnabled=false, hospiceWalkInEnabled=false; gate kneeling-ring genstep, cradle construction and loading/feeding, staged ticks, memory/failure letters, failed-chassis study, salvage cores and walk-in incident including pursuers. Histories remain saved data, never rewrite accepted memory text. Switching on restores named repair/wake/failure branches with prior permission in the repair order.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no kneeling machine, offered cradle/repair/study job, memory/failure letter or walk-in incident/pursuer; on: set eligible chassis/cradle and trigger an eligible incident to observe both routes with preserved name/history. Read the log in each branch and require no new exception/warning storm.


## T07a: deserter histories

Specific disposition: deserter_histories — Accepted deserter histories, damage/oddity/memory text and modification hediffs retained through cradle and waking; high-Intellectual quiet-tone reading. Current modifications/text are not evidence of ongoing spoken lines or new personalities.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Defs/RM_DeserterHistoryDefs/RM_DeserterHistories.xml; independently read current file. RM_Hospice.cs chassis/cradle/wake/failure -> RM_DeserterHistories.xml; accepted memories and modification hediffs.

Scope: hospice_rings deserter_histories hospice_revival hospice_failure deserter_walkin.

Work: hospiceEnabled=false, hospiceWalkInEnabled=false; gate kneeling-ring genstep, cradle construction and loading/feeding, staged ticks, memory/failure letters, failed-chassis study, salvage cores and walk-in incident including pursuers. Histories remain saved data, never rewrite accepted memory text. Switching on restores named repair/wake/failure branches with prior permission in the repair order.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no kneeling machine, offered cradle/repair/study job, memory/failure letter or walk-in incident/pursuer; on: set eligible chassis/cradle and trigger an eligible incident to observe both routes with preserved name/history. Read the log in each branch and require no new exception/warning storm.


## T07b: hospice revival

Specific disposition: hospice_revival — Five saved stages over days, components/optional etchant/core inputs through haul workgiver, slower riskier etchant-free stage, protocols benefit, lights, memory letters and possible lash-out. Wakes named, modified player servitor with no overseer comp; campaign kind extension is separate. Proof skips stage time and feeding jobs.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_Hospice.cs:219; independently read current file. Hospice cradle tick and load commands; RM_HospiceHaul workgiver/job; RM_OldTongue protocols; optional etchant -> stages -> named servitor.

Scope: hospice_rings deserter_histories hospice_revival hospice_failure deserter_walkin.

Work: hospiceEnabled=false, hospiceWalkInEnabled=false; gate kneeling-ring genstep, cradle construction and loading/feeding, staged ticks, memory/failure letters, failed-chassis study, salvage cores and walk-in incident including pursuers. Histories remain saved data, never rewrite accepted memory text. Switching on restores named repair/wake/failure branches with prior permission in the repair order.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no kneeling machine, offered cradle/repair/study job, memory/failure letter or walk-in incident/pursuer; on: set eligible chassis/cradle and trigger an eligible incident to observe both routes with preserved name/history. Read the log in each branch and require no new exception/warning storm.


## T07c: hospice failure

Specific disposition: hospice_failure — Failed chassis retains unit/history, cradle resets, recipe consumes it for current-project research or ordinary smelting. Actual placement failure is not safely recovered.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_Hospice.cs:410; independently read current file. Cradle stage failure -> failed named chassis -> RM_HospiceRecipes.xml study and smelting; placement rollback unresolved.

Scope: hospice_rings deserter_histories hospice_revival hospice_failure deserter_walkin.

Work: hospiceEnabled=false, hospiceWalkInEnabled=false; gate kneeling-ring genstep, cradle construction and loading/feeding, staged ticks, memory/failure letters, failed-chassis study, salvage cores and walk-in incident including pursuers. Histories remain saved data, never rewrite accepted memory text. Switching on restores named repair/wake/failure branches with prior permission in the repair order.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no kneeling machine, offered cradle/repair/study job, memory/failure letter or walk-in incident/pursuer; on: set eligible chassis/cradle and trigger an eligible incident to observe both routes with preserved name/history. Read the log in each branch and require no new exception/warning storm.


## T07d: deserter walkin

Specific disposition: deserter_walkin — Cradle-gated incident, nonhostile named walker, let-come/refuse letter, intact kneeling on arrival or posed refusal, optional hostile pursuer. Can occur outside Warscar where a cradle exists. Successful A4 uses ordinary movement but suppresses pursuer.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_Hospice.cs:584; independently read current file. IncidentWorker in RM_Hospice.cs checks cradle -> choice letter -> walking job -> arrival/refusal and optional pursuer.

Scope: hospice_rings deserter_histories hospice_revival hospice_failure deserter_walkin.

Work: hospiceEnabled=false, hospiceWalkInEnabled=false; gate kneeling-ring genstep, cradle construction and loading/feeding, staged ticks, memory/failure letters, failed-chassis study, salvage cores and walk-in incident including pursuers. Histories remain saved data, never rewrite accepted memory text. Switching on restores named repair/wake/failure branches with prior permission in the repair order.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no kneeling machine, offered cradle/repair/study job, memory/failure letter or walk-in incident/pursuer; on: set eligible chassis/cradle and trigger an eligible incident to observe both routes with preserved name/history. Read the log in each branch and require no new exception/warning storm.


## T08: pools

Specific disposition: pools — FlowWorks shallow/deep liquor blobs, saved independent phase clock and holds, tint/icons, per-phase draw outputs, game journal, phase-reader skip-bloom control, catalyst fuel/held double yield, bloom hand burn/direct toxic dose; terrain contact harm belongs to FlowWorks. Placement finds open ground, not specifically crater bowls.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_ReactionPools.cs; independently read current file. RM_ReactionPools genstep -> pool controller/map component -> phase clock/tint/icon; tap WorkGiver -> draw and journal; FlowWorks terrain is external contact hazard.

Scope: pools pool_reagents pool_remains.

Work: poolsEnabled=false, catalystEnabled=false; gate genstep, phase clock, journal, taps/jobs, reagents and pool-specific corpse dissolution. Do not disable FlowWorks terrain engine for neighbours. Corpse clocks may not consume bodies on legacy terrain while off. New maps retain ordinary poisoned-water dressing, without a phase/tap/reagent system.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no special pool controller/phase icon/tap/reagent, draw job, journal discovery or corpse consumption by this component on a fresh map; on: eligible pool advances phases and draw job/journal/products function. Check legacy pool terrain separately for inert off state. Read the log in each branch and require no new exception/warning storm.


## T08a: pool reagents

Specific disposition: pool_reagents — Gel refuels screens, etchant is used by cradle and turret cost, medical coagulant is medicine data, bloom liquor is valuable trade data. No special instant blood-stopping routine inferred from herbal-tier medicine.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Defs/ThingDefs_Items/RM_PoolReagents.xml; independently read current file. Phase.ReagentDef -> draw products -> screen gel fuel, cradle etchant, old-line turret costs, medicine/trade defs.

Scope: pools pool_reagents pool_remains.

Work: poolsEnabled=false, catalystEnabled=false; gate genstep, phase clock, journal, taps/jobs, reagents and pool-specific corpse dissolution. Do not disable FlowWorks terrain engine for neighbours. Corpse clocks may not consume bodies on legacy terrain while off. New maps retain ordinary poisoned-water dressing, without a phase/tap/reagent system.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no special pool controller/phase icon/tap/reagent, draw job, journal discovery or corpse consumption by this component on a fresh map; on: eligible pool advances phases and draw job/journal/products function. Check legacy pool terrain separately for inert off state. Read the log in each branch and require no new exception/warning storm.


## T08b: pool remains

Specific disposition: pool_remains — Saved corpse exposure clock, dissolution after a day on extant pool terrain, gear/inventory dropped and bone filth remains; leaving a pool clears the clock.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_ReactionPools.cs:180; independently read current file. MapComponent_ReactionPools tick -> corpseSince -> corpse consumption/gear drops/bone filth; not gated by a new drawing order.

Scope: pools pool_reagents pool_remains.

Work: poolsEnabled=false, catalystEnabled=false; gate genstep, phase clock, journal, taps/jobs, reagents and pool-specific corpse dissolution. Do not disable FlowWorks terrain engine for neighbours. Corpse clocks may not consume bodies on legacy terrain while off. New maps retain ordinary poisoned-water dressing, without a phase/tap/reagent system.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no special pool controller/phase icon/tap/reagent, draw job, journal discovery or corpse consumption by this component on a fresh map; on: eligible pool advances phases and draw job/journal/products function. Check legacy pool terrain separately for inert off state. Read the log in each branch and require no new exception/warning storm.


## T09: Old-line turret refit

Scope: turret_refit.

Work: turretRefitEnabled=false; gate refit gizmo, blueprint conversion, construction/trade/research routes and startup damage/cooldown edits. Keep the broken guns and their harmless tracking. No extra weapon is needed to read a dead battlefield.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: tracking works but no refit command, old-line blueprint or construction job; on: eligible refit order reaches a valid constructed firing turret, with cancellation preserving value. Read the log in each branch and require no new exception/warning storm.


## T10: screen building

Specific disposition: screen_building — Minifiable/ship-placeable ordinary screen building, 400 W, gel fuel, radius, plasteel/advanced-component/core cost and analysis-gated research. Current art borrows turret base/etchant; no live flight/next-tile protection accepted.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Defs/ThingDefs_Buildings/RM_AerosolScreen.xml; independently read current file. RM_AerosolScreen.xml build/research/refuel -> core; dependency paths via OldTongue and gel.

Scope: screen_building ring_research ring_salvage ship_wakes_line calibration_engine glower_shielding.

Work: Introduce a Warscar next-version technology gate, default off, distinct from exported aerosol API availability. Gate ring placement, analysis, salvage/repair, GravEngine wake, screen/shield construction and apparel, calibration and local hum. Retain core types, defs and external APIs. Do not use aerosolScreenEnabled=false globally to disable neighbour screens. Roof shelter remains the kept signature response. Glower plate XML stat offsets must be inert/inaccessible while off, not just its room comp.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no Warscar ring, screen/shield build option, ring job, analysis unlock, calibration pass or local-tech hum; a neighbour-owned screen still registers/protects by its own settings. On: eligible ring/site and research expose salvage, screen and shielding routes; deferred calibration wiring stays explicitly unmeasured until T15. Read the log in each branch and require no new exception/warning storm.


## T10a: ring research

Specific disposition: ring_research — Live/dead projector set pieces with saved rolled condition/evaluation, first placed ring forced working, nonconsuming humming-ring analysis unlock and live-only interaction.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_WarscarRings.cs; independently read current file. RM_WarscarRings genstep -> live/dead comp and CompAnalyzable -> research unlock.

Scope: screen_building ring_research ring_salvage ship_wakes_line calibration_engine glower_shielding.

Work: Introduce a Warscar next-version technology gate, default off, distinct from exported aerosol API availability. Gate ring placement, analysis, salvage/repair, GravEngine wake, screen/shield construction and apparel, calibration and local hum. Retain core types, defs and external APIs. Do not use aerosolScreenEnabled=false globally to disable neighbour screens. Roof shelter remains the kept signature response. Glower plate XML stat offsets must be inert/inaccessible while off, not just its room comp.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no Warscar ring, screen/shield build option, ring job, analysis unlock, calibration pass or local-tech hum; a neighbour-owned screen still registers/protects by its own settings. On: eligible ring/site and research expose salvage, screen and shielding routes; deferred calibration wiring stays explicitly unmeasured until T15. Read the log in each branch and require no new exception/warning storm.


## T10b: ring salvage

Specific disposition: ring_salvage — Crafting-gated evaluate, uninstall/strip, minified preserved condition, installable self-powered ring, failing salvaged ring repair with components and chance core from dead ring. Existing shelter disappears on extraction.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_WarscarSalvage.cs; independently read current file. Ring gizmos -> RM_EvaluateRing/RM_SalvageRing/RM_RepairRing jobs -> minified condition/core; removes local active shelter.

Scope: screen_building ring_research ring_salvage ship_wakes_line calibration_engine glower_shielding.

Work: Introduce a Warscar next-version technology gate, default off, distinct from exported aerosol API availability. Gate ring placement, analysis, salvage/repair, GravEngine wake, screen/shield construction and apparel, calibration and local hum. Retain core types, defs and external APIs. Do not use aerosolScreenEnabled=false globally to disable neighbour screens. Roof shelter remains the kept signature response. Glower plate XML stat offsets must be inert/inaccessible while off, not just its room comp.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no Warscar ring, screen/shield build option, ring job, analysis unlock, calibration pass or local-tech hum; a neighbour-owned screen still registers/protects by its own settings. On: eligible ring/site and research expose salvage, screen and shielding routes; deferred calibration wiring stays explicitly unmeasured until T15. Read the log in each branch and require no new exception/warning storm.


## T10c: ship wakes line

Specific disposition: ship_wakes_line — Nearby spawned GravEngine wakes dead rings within 40 cells, updates on rare tick and ends without engine. Implementation tests engine presence, not a separate proof of landed-versus-constructed origin.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_WarscarRings.cs:79; independently read current file. Ring IsScreenLive/rare tick -> NearbyEngine scans spawned GravEngine; no constructed-versus-landed provenance gate.

Scope: screen_building ring_research ring_salvage ship_wakes_line calibration_engine glower_shielding.

Work: Introduce a Warscar next-version technology gate, default off, distinct from exported aerosol API availability. Gate ring placement, analysis, salvage/repair, GravEngine wake, screen/shield construction and apparel, calibration and local hum. Retain core types, defs and external APIs. Do not use aerosolScreenEnabled=false globally to disable neighbour screens. Roof shelter remains the kept signature response. Glower plate XML stat offsets must be inert/inaccessible while off, not just its room comp.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no Warscar ring, screen/shield build option, ring job, analysis unlock, calibration pass or local-tech hum; a neighbour-owned screen still registers/protects by its own settings. On: eligible ring/site and research expose salvage, screen and shielding routes; deferred calibration wiring stays explicitly unmeasured until T15. Read the log in each branch and require no new exception/warning storm.


## T10d: calibration engine

Specific disposition: calibration_engine — Built calibrated-only ToxGas scrubbing and random-cell unpollution pass with its setting, plus old-tongue calibration research flag. No shipped caller activates calibrated=true; keep implementation distinct from usable upgrade.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_AerosolScreen.cs:150; independently read current file. RM_CompAerosolScreen tick -> DoCalibrationPass only if Props.calibrated; no active true caller established.

Scope: screen_building ring_research ring_salvage ship_wakes_line calibration_engine glower_shielding.

Work: Introduce a Warscar next-version technology gate, default off, distinct from exported aerosol API availability. Gate ring placement, analysis, salvage/repair, GravEngine wake, screen/shield construction and apparel, calibration and local hum. Retain core types, defs and external APIs. Do not use aerosolScreenEnabled=false globally to disable neighbour screens. Roof shelter remains the kept signature response. Glower plate XML stat offsets must be inert/inaccessible while off, not just its room comp.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no Warscar ring, screen/shield build option, ring job, analysis unlock, calibration pass or local-tech hum; a neighbour-owned screen still registers/protects by its own settings. On: eligible ring/site and research expose salvage, screen and shielding routes; deferred calibration wiring stays explicitly unmeasured until T15. Read the log in each branch and require no new exception/warning storm.


## T10e: glower shielding

Specific disposition: glower_shielding — Strongest panel in an indoor room adds toxic environment resistance and scales ordinary toxic damage; wall placement gate, stat-part patch and plate apparel offsets. Own toggles and readable inspect/stat explanation.
This ticket owns this capability's switch-off; the shared gate implementation may land with sibling tickets. Evidence/callers: src/RimMandrake/Scarlands/Source/RM_GlowerShield.cs; independently read current file. Room shield comp/stat-part Harmony patch; XML plate ToxicEnvironmentResistance offset bypasses comp off switch.

Scope: screen_building ring_research ring_salvage ship_wakes_line calibration_engine glower_shielding.

Work: Introduce a Warscar next-version technology gate, default off, distinct from exported aerosol API availability. Gate ring placement, analysis, salvage/repair, GravEngine wake, screen/shield construction and apparel, calibration and local hum. Retain core types, defs and external APIs. Do not use aerosolScreenEnabled=false globally to disable neighbour screens. Roof shelter remains the kept signature response. Glower plate XML stat offsets must be inert/inaccessible while off, not just its room comp.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no Warscar ring, screen/shield build option, ring job, analysis unlock, calibration pass or local-tech hum; a neighbour-owned screen still registers/protects by its own settings. On: eligible ring/site and research expose salvage, screen and shielding routes; deferred calibration wiring stays explicitly unmeasured until T15. Read the log in each branch and require no new exception/warning storm.


## T11: Warscar campaign integrations

Scope: campaign_kit_data campaign_kit_wiring campaign_lore campaign_wake_swap ship_vermin_neighbour.

Work: Keep campaign lore/camps, grave-wards, special kits, wake swaps and Warscar-specific hull-infestation routes outside this version. In the full source checkout add/inspect a Warscar integration switch, default off and labelled next version. Do not disable ShipVermin/CreatureBehaviors globally or remove any existing patched roster species. Rewire neither legacy mark nor scaria conditions over the retained RM snap sweep.

Reason: A separate interaction, technology, reward or campaign system; deleting its player-facing behaviour leaves the defined battlefield, ordinary food web and Settling cycle whole.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: full-source campaign profile has no Warscar camp/journal discovery, grave-ward integration, extra mark/scaria condition, hospice swap effect or Warscar-specific infestation injection; existing roster species and shared ship-vermin behaviour elsewhere remain. On: each integration actually available in that profile is staged by ordinary eligible entry points, not by adding unknown defs. Read the log in each branch and require no new exception/warning storm.


## T12: Undyeable plate restriction

Scope: plate_no_dye.

Work: Gate only the DesiredColor setter veto in RM_WarscarPatches_ChatrakPlateNoDye; normal chatrak hide and apparel stay. Recommend retirement: the special dye veto adds no battlefield, animal-feeding or dust-cycle decision.

Reason: An aesthetic veto with no necessary player decision; recommend retirement, with behaviour off pending owner decision.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: plate hide still yields/crafts as normal and styling accepts dye; on: the veto returns and a dye request is refused without spending dye. Read the log in each branch and require no new exception/warning storm.


## T13: Bileworm mood aura

Scope: bileworm_stench.

Work: Split a next-version stench toggle from bilewormGasEnabled; gate only Stench and new/renewed memories. Corpse decay, drinking, body notices, dropped gear and bile remain. A mood radius is independent of how the slug feeds.

Reason: The gas/feeding loop works without a separate mood aura.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: the worm still decays/drinks a body, drops its gear and leaves bile/notice, but no new/renewed stench memory; on: nearby eligible colonists acquire the stench memory without stacking. Read the log in each branch and require no new exception/warning storm.


## T14: Retire planet-rarity capability

Scope: rarity_legacy.

Work: Recommend retirement under the standing permanent worldgen ban, never park this in a future version. Until the owner applies retirement, hide/disable the rarity slider and its BiomeWorker GetScore postfix behind a retained inert legacy gate, default off; never expose a planet-generating control. Local-map construction on the fixed planet is unaffected.

Reason: Alternative-planet insertion contradicts the permanent no-worldgen ruling; no future version is proposed for it.

Callers and decoupling: see the explicit source call ledger in definition.md for these capabilities. Do not gate an exported engine merely because its local content is deferred.

Acceptance test: At shipped defaults on a fresh map, off: no planet-rarity UI or active score multiplier while the fixed-world biome and local map steps still load; legacy gate-on regression may call the worker with synthetic existing-tile inputs only, never generate a planet. No player-facing worldgen mode is accepted. Read the log in each branch and require no new exception/warning storm.


## T15: Specify the reachable calibration upgrade

Next version, not a kept-bar dependency. Current getter ProjectorCalibrated and a calibrated-only pass do not form a usable upgrade. Before building, specify the actual player order, research prerequisite, power/material cost, saved calibrated state, cancellation/refund behaviour, minify/reinstall/reload and UI. Preserve the prior powerful/broad-screen ruling; do not narrow scope to balance it. Caller search: RM_OldTongue.cs getter and RM_AerosolScreen.cs DoCalibrationPass/Props.calibrated; no activator found. A later full-source search precedes implementation.

Acceptance test: With technology off, fresh map has no calibration order, pass, job, letter or research effect and a clean log. With future technology/research enabled and the specified order completed, the actual built screen reports saved calibration and performs its ordinary scrubbing pass through reload; cancelling preserves input accounting. No forced Props.calibrated setter can substitute for the usable route.


## T16: Reconcile deserter action specifications

Next version. The developed history table already names distinctive post-wake actions; he was not being asked whether interesting deserters are wanted. Read the adopted table versus actual full-source callers and define only the missing counting/cache/gardening/listening/boundary actions, their trigger, stop conditions, save state and readable result. Preserve accepted memories verbatim. The 2026-11-10 repair answer gives prior permission via existing order controls and explicitly questions etchant quirks: default later design is an ordinary repair order with disclosed risk, not a newly compulsory special reagent.

Acceptance test: Publish an action-to-source/spec matrix with every adopted action either located or given trigger/state/cost/sign/stop/reload definition; no invented owner approval. Future hospice off yields no action/job/letter; once on, an eligible revived history actually produces its specified action, with a matched nonmatching-history control. A missing external caller remains unknown, never a false absent finding.


## T17: Lasting native poison and sterile ground

Needed by land/W2, not optional. No renewal writer was found: RM_PollutedBiomeExtension and RM_PollutionSense only detect. Specify and implement the smallest ordinary pollution-source renewal on the saved native-substrate mask, with actual crop/terrain/growth exclusion and visible inspection of source versus temporarily cleared surface. No new radiation heat/damage system, crop device ban, planet pollution edit or engine redesign. Ordinary roofs/buildings work. Resolve contamination footprint/cadence with the whole-map model before trusting a guessed balance. Include settings and off/save semantics; no repeated alarm per cell.

Acceptance test: The situation generator drives each actual cleanup/water/terrain/growth entry route; native ground cannot become soil farmland, cleared exposed source renews ordinary contamination while constructed shelter remains usable, and nonnative control ground behaves ordinarily. Game calibration shows a real attributed hazard/source, not just a marker. Complete season/long-tail model and game traces show no unharvested food-web desert; off stops new local scripted renewal without deleting saved masks or pawns. No recipe or art change substitutes for this evidence.


## T18: Complete shipped settings and safe transitions

Needed by floor. RM_WarscarMod has many switches but no complete proposed master/gate profile, and major kept floor/film/readability coverage must be explicit. Add master and missing feature coverage, true next-version labels/defaults, effect-time notes and no planet-rarity UI. Preserve current searchable groups/reset, partner status and off/unsupported opt-in. Source search found startup-only trade offsets, static plate offsets, independent incident and recipe routes: changing a comp tick alone is insufficient. Decouple local technology gates from exported aerosol settings.

Acceptance test: A fresh settings profile/reset yields exactly the proposed active-route matrix; master all-off generates/loads ordinary terrain/life and produces no new scripted local hazard/job/letter, logs clean. Switch off midfall, midlift and midincubation: no harmful shutdown pulse, new arming or orphan callback; harmless cleanup completes, already active ordinary mental states follow the existing rules. Re-enable resumes eligible work without duplicate objects/conditions. Each UI label's promised now/new-map/restart timing matches state reads. Neighbour-owned screens and bodies are not deleted or globally disabled.


## T19: Actual weather and dose-attribution driver

Needed by W5. validation.py's calm/start/end, roof/toxin and lift rows are explicit UNMEASURED placeholders. Extend those existing rows with the situation generator and game driver; do not add a separate green script that leaves formal proof blind. Capture ordinary wind first and use a labelled replay through the actual map tick. Expose source-attributed dose events/counters and actual fall/film state, not ProofStart/instant stage setters. Every test writes the offline counterpart and live callable procedure when built.

Acceptance test: A deliberately broken counter/roof/dose route is detected by its corresponding control; ordinary counter-driven start/end and matched roofed/exposed source increments satisfy W5 while other kept hazards/weather run. Restored halfway counters lead to the same next transition. Missing current runtime/fingerprint/site input returns UNMEASURED with cause, never a biological fail/pass. Teardown restores wind/settings and all force flags.


## T20: Cure, warning and onset driver

Needed by life/W4. Retain current RM_ChatrakSnap sweep/hediff/render components and pure Warscar lookup, independent of disabled mark gameplay. Specify treatment success cancels any remaining delayed onset; inspect actual taming/cure route before editing. Blocked circle paths must not stop disease. Provide ordinary-time onset, retreat and cured/healthy control traces; current direct ProofStage calls cannot prove warning time or cure correctness. This does not reopen staged onset or chosen names.

Acceptance test: Matched healthy, untreated wild-scaria and cured-after-arming animals show only the eligible untreated progression/rage; able nearby worker on the declared open exit can withdraw after visible change before first attack. Repeat state walk through save, blocked circling, death, despawn and successful tame/cure, with no stale job or hidden onset. All kept mechanics run and no mark accrual/bonus occurs. Actual scheduler interval and timing path are recorded, not guessed.


## T21: Film loss and real movement-record instrument

Needed by signature/W6. Verify actual production Pawn cell-entry surface selection, record/style/bearing and independent film removal paths. Generic cleaning, scar-roach feeding and new flooring must clear the corresponding shared-grid records. Search current CreatureBehaviors erasers before adding a narrow existing-API call; never fork the grid or redesign capacity. Preserve invisible-grounded-walker recording even though the custom hunter is deferred. Disabled buried cells must not suppress film.

Acceptance test: Geometry sweep plus real-game calibration compares tagged crossing/uncrossed paths, visible/invisible/crawling species, cap boundaries and serialization. Removing film by each ordinary consumer during calm leaves no floating record; new eligible traffic still records when the pool is full. A deliberately missing surface/erase/writer control is rejected. The state witness and W8 look agree; no pile of decorative decals passes.


## T22: Coupled sweep restore and shutdown proof

Needed by signature/W7. The map component saves sweepActive/per-step state/liftHit; the shared grid separately saves trackSweepPos/angle/active. Existing validation reload field equality misses whether subsequent callbacks progress. Extend it to capture both owners, film/record arrays and dose-call identities. Queue a fresh fall behind unfinished cleanup; an off transition may clean but never create an extra damaging front. No engine change unless a demonstrated restore defect requires its existing contract to be fixed.

Acceptance test: Uninterrupted versus saved/restored first/middle/last-batch branches produce the same order and final masks, no duplicate front dose for a tagged pawn, no lost new arrivals or callbacks to dead/despawned bodies; square/diagonal/rectangle geometry covered by model. New calm during lift cannot reset the cursor. Toggle-off completes harmless cleanup and ends exposure. Missing grid is a dependency refusal/UNMEASURED environment, not a passing instant-wipe fallback.


## T23: Combined look and sound protocol

Needed by land/readability W1/W4/W8/W9. Supply a repeatable natural-layout normal-play look/listen with source, camera, wind, turret-target and cue metadata, and muted UI fallback. Do not commission art, reopen accepted textures or demand new grains. Tetchik clicks and wind are ordinary life/land; deferred hum/boil/moving silence are absent with those sources off. Worsening grazer cues must be visible at its actual life-stage scale. Correct shipping label to the later house form “the Warscar,” and descriptions that currently promise deferred rewards.

Acceptance test: With every kept system on, observe dry falling dust, readable workers/trails, actual plate warning, source-local clicks, cessation of wind layer and harmless tracking at normal play zoom. Empty source, stationary/dead/out-of-range turret target and map-switch controls rule out arbitrary soundtrack/motion; no absent-extra layer plays. Muted sound retains the condition/protection explanation. State-only sound density is insufficient; describe actual observed accept/reject pictures and classify unreadable evidence UNMEASURED.


## T24: Inspect donor defense geometry before building alignment

Needed by land/W1. Current BiomeDef references Odyssey gensteps, but this checkout supplies no actual donor layout geometry proving common approaches or spent ancient-danger dressing. Export/inspect actual natural local layouts first, including sealed salvage versus pre-opened threats. If they already satisfy the picture, keep them. Otherwise define a minimal local-map arrangement of existing emplacements/cover and pre-opened danger state; no new treasure/dungeon engine or world-site authoring. Campaign Sentinels remain outside defaults, with defend-only law unchanged.

Acceptance test: Geometry export covers supported layout/terrain regimes and locates defense facings, entrances, shared approaches, stripped surface and sealed rewards; natural-layout look sorts W1's pictures. Old enemy evidence and intact unsealed prizes are absent; dangerous ordinary creatures need not be removed to make a ruin look spent. No planet, painted tile or campaign ladder state changed. A plausible random-scatter control fails the composition reading.


## T25: Switch off optional Warscar scanner discoveries

Built extra: Patches/RM_AcousticPayload_Scarlands.xml adds an AcousticPayloadExtension when the scanner exists. It references shells, kneeling machines, panels, wrecks and hidden caves. Gate this optional biome payload behind a “Next version” switch, default off; keep shared scanner API/other biome payloads and its prior restoration contract. No need to remove defs/strings. Already absent deferred targets cannot be reported as existing discoveries.

Acceptance test: On a fresh default Warscar map with scanner installed, no Warscar-specific discovery payload/result/letter/job is offered, and log is clean; with the switch on and actual eligible targets present, the appropriate banded reading appears. Targets absent at pulse time produce no false target. Shared scanner and other biomes' payloads still work; no new planet scan/worldgen capability is added.


## T26: Honest native food, products and body remains

Needed by life/W3 and land/W2. Verify actual native glower/scorched-stars establishment/growth on AncientMegastructure rather than assume wildPlants entries overcome fertility minima; lichen's existing bounded anchor seeder stays. Keep native growth data specific to these crusts without making soil fertile. Caravan RawBerries has no resident source: remove unsupported forage availability/text, not add an Earth food plant. Human food is carried or hunted. Ordinary crust harvest stays raw trade goods; remove claims of nonexistent fuel/pigment/radiological handling recipes without reviving the previously cut glower-black feature. Pallbearer's final ingest must leave actual remains and recoverable carried items: inspect vanilla route, add only a narrow shared-consumption sign if absent. Bones butcher products cannot certify this. Ordinary electric attacks and feasible taming are game-state checks, not redesign opportunities.

Acceptance test: Ordinary species establish/feed/use their weapons on actual default native habitat, with all kept toxin and weather effects running; humans cannot conjure berry forage and tetchik give no edible meat. Native crust support does not allow general soil crops. Final consumption of a known colonist/animal body accounts for remains and gear/quest items and a colony-readable sign; repeated/reloaded feeding cannot duplicate or erase carried items. Whole model/game calibration shows viable unharvested food web, without pinned rates or a self-sufficient colony requirement.


## T27: Whole-season model and actual complete-run driver

Needed by sole whole bar W9 and all unknown meetings. Build the ordered instruments in models.md and consolidate the corresponding offline/live cases into the existing functional script. Natural primary run plus labelled complete-cycle replay, midpoint save and reversed action order must retain every kept system, ordinary AI/cell effects and other weather. No forced clear sky, frozen creatures, injected future shelters, debug completed jobs, or model output presented as a game measurement. Record model calibration and instrument boundaries.

Acceptance test: Current full-profile live evidence satisfies W9 range/start/control, with attributable health/film/record/food/body/job/log and actual feature-on ledgers; midway restore and changed work order agree on causal behaviour, and a separate prolonged native-ground reading reaches day 100. Deliberately stalled counter, stale record and missing food-route controls are detected. Missing current proof returns UNMEASURED, not success. A red regression is attributed to the implementation or instrument and assessed against its experience bar; it is not an independent refusal criterion.
