# Page one — what I propose

You enter a flat metal maze whose corridors lead past salvage, recognisable toxic pools and machine-held ground. Taking ordinary scrap is useful, but cutting marked shortcuts, disturbing canal life or damaging protected works changes the hum and draws living bolts toward the offending work. Stop and withdraw after minor disturbance; sacred damage requires material repayment and costs Enclave goodwill, while deep intrusion brings machines against the drill.

Land: deliberate corridors on polluted deck plate, stationary damaging pools with sulfuric-looking edges, ordinary salvage, dry bright weather, coolant channels where authored, wrecks and cooked approach corpses. Pools stay as land: the owner set them alongside garrisons and sacrilege; deleting their harm removes a ruled cost. Their implementation is absent, and now ticketed.

Life: cleaning roaches, patterned bolts, canal-bound eels and the peaceful worn borehulk. Existing campaign fauna remain; no roster evictions. No green native forage.

Signature: extraction provokes the Cathedral; sound and bolts locate trouble, restraint limits it, and concrete repayment clears lasting damage.

Runner-up: restoring and owning or freeing the borehulk. Its separate mining reward is deferred; expensive repair and keep/free outcomes remain intact for later. The worn peaceful animal stays.

Next version, switched off:

- Borehulk repair, yard, ownership, service, favours and political rewards.
- Hull pets, boarding, spying, return consequences, marks, dilemma and mood memories.
- Hum literacy, primers and droid commentary.
- Machinery pause and the giant's duplicate mood freeze.
- Curiosity shedding and pickup charges.
- Coolant-load chemistry and random fishing shock.
- Passive standing loss at the worst mood.
- Campaign stage shaping, progression, offers, survey and descent/reveal.
- Self-repairing pattern hull.
- Mending Weld and Stranger's Overhaul, already deferred by your ruling.

I recommend retiring alternate-planet scoring/rarity because it contradicts no-worldgen; disable it regardless of deletion. Leave wall flitting dropped: it adds movement work without improving the warning. Neither recommendation deletes anything.

Counts from result.json: capabilities 68 before scope selection; kept capabilities 32, next-version capabilities 34, recommended retirements 2. Bars 0 before and 7 proposed; live-only bars 0 before and 3 proposed. The old tree is empty. Checks 14; rules 12; unknown meetings 6; models 3; tickets 43; questions 0. Capabilities include dependency interfaces and needed warnings. These counts certify no gameplay.

# Page two — what to check

These are my decisions and corrections, not new words attributed to you:

- **Maze/free salvage:** useful connected corridors; loose fragments are free, visibly marked structural shortcuts can anger the hum. Guardians in existing chambers supply the trap; no random-trap system.
- **Pools:** existing toxic/irradiated terrain supplies stationary harm; sulfuric edges supply the acid look. No true acid mechanic. Safe public routes and repayment approaches avoid them. Canal-free maps still have pools. Historical provider names must be resolved before building.
- **Warnings:** bolts indicate actual disliked work; a basic work-site cue covers absent or blocked bolts. No reader or plot unlock. The fishing reading must first show an attributed rise above calm, then compare cancellation with continued fishing; always calm cannot pass recovery.
- **Sacred currency:** I corrected my local-ledger substitution. Your August ruling uses real Free Droid Enclave goodwill and its isolation consequence. Sacred receipts and payments persist across Cathedral tiles and reload; local hum standing only mirrors them. The permanent-enemy Arsenal is a different faction.
- **Unpaid access:** my delegated rule keeps the hum above calm while any sacred receipt remains unpaid, including below diplomatic hostility. Multiple debts add pressure. Enclave hostility closes actual contact without expanding guard pursuit or summoning an army. Repayment removes its receipt; future contact returns when the real relation recovers. Past prisoners and cancelled trades are not undone. Ordinary gifts can restore diplomacy sooner, but leave the unpaid material receipt and warning.
- **Repayment:** ordinary silver delivery against a visible replacement-value bill, from the public side. Twice replacement value is my proposed price [guess: starting material cost for the season model], not your price ruling. Partial deposits and destroyed-site receipts persist globally; no credit farming or ritual.
- **Defence/life:** guards hold ground; drill forces lose interest when their actual drill violation ends. Eels traverse water; roaches stay outside hum mechanics; the worn giant stays peaceful with its quest off.
- **Defaults:** a real mechanics master replaces rarity-as-master. Off stops pending custom effects and preserves creatures/receipts; it cannot reset actual diplomacy. Pool placement off affects new local maps only. Shared Direct Sun stays geometric.

Models, first to build first:

- Situation and transition generator: actions, transactions, real Enclave relation callbacks, cross-map receipts, pool exposure and reload; calibrated against actual jobs and saved state.
- Local geometry sweep: corridors, pools, eel/bolt paths, guards and public-side repayment together; checked against game paths, terrain and visibility.
- Whole-mod season/workload model: concurrent work, pool exposure, debt, residents, Enclave isolation and reordered actions with a midway reload; checked against a matching game trace.

The unknown meetings remain geometry, defence, warning timing, residents, attitude and continuity. Models must resolve them before acceptance; sensory readability still needs a real look and listen.

The first reviewer refused omitted pools, substituted sacrilege currency, undefined access cost and an always-calm fishing false pass. This revision addresses each; second review remains pending. No questions await you. Nothing applies until review and your approval; this pass changes only the proposal.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a sourced core promise omitted or weakened (bars.json B2 (says, reject, lazy)). The owner-picked experience in design/RimMandrake/biome_experiences_2026-10-20.md:21 is "A maze built by minds you'll never meet, still guarded by their machines. Salvage paradise with a temper." The 2026-08-19 ruling in design/Jawa/worldbuilding/the_forgotten_war.md:228 reads: "The ordinary metal is mineable rock the player strips freely — the whole map really is the reward." The November answer (ANSWERS_OWNER.md:3) qualifies that premise only for cutting shortcuts. B2 promises only "useful metal from loose plate and richer dead smartsteel" and claims "lazy: none". Consider a build where only scattered rubble is free and every corridor wall of the maze is a marked divider. It satisfies B2's words and B1's, yet it turns the paradise into a scrap trickle. He would refuse it. Would pass: B2 says the bulk of the metal a crew can see and reach is free salvage, and that marked dividers and sacred works are the exception. A reject picture then catches the scarce build. Smallest fix: In B2.says, change "recovers useful metal from loose plate" to "strips most of the metal in sight freely", and mark "most of the metal in sight" as figurative (no ratio pinned). Add the reject picture "Only scattered rubble is free; nearly every corridor wall is a marked divider, so salvage means trespass."
- a figurative word unmarked (bars.json B2 says ("loose plate"); figurative: []). The free bulk the census calls bulk_salvage is src/RimMandrake/RustCathedral/Defs/ThingDefs_Buildings/RM_CathedralDeckPlate.xml. That file uses ParentName="RockBase", isNaturalRock and mineableThing Steel, so it is mineable wall rock, not loose items. B2 says "loose plate" and its figurative list is empty. One builder will read "loose" as scattered chunks or items. Another will read it as unmarked deck-plate wall. The two readings give different maps and different passes. Would pass: "loose" is either removed or marked figurative, standing for deck-plate wall and rubble that is not a marked route divider or a sacred work. It comes with an accept picture of a worker mining an unmarked corridor wall without offence. Smallest fix: Add a figurative entry for "loose" in B2 with that meaning and the one accept picture.
- a contradiction with a standing ruling or the lore (definition.md, Costs and recovery ("Sacred player damage/claim creates one game-level offence receipt per original protected structure ... Destruction updates that receipt"); R3; R5; C3). The ruling at the_forgotten_war.md:230 reads: "−15 per sacred structure, applied through QuestNode_AddTag + QuestNode_ChangeFactionGoodwill on the shipped <tag>.Destroyed signal". Line 231 counts "five strips before −75". The proposal takes the full Enclave debit on the first damaging hit. A conduit that is chipped but still standing therefore costs what a strip costs. In a B5 firefight inside held ground, stray player fire on several conduits can tip the Enclaves hostile when nothing was stripped. The definition presents this trigger as the ruled economics, and owner_pages does not list it as a departure. Would pass: The Enclave debit fires on destruction or strip of a sacred structure, as ruled (claim may count as a strip). First damage short of that raises only fast irritation and the warning. Alternatively, keep the first-hit trigger but list it on page two as a proposed change to the ruled trigger, citing :230. Smallest fix: In R3, R5, C3 and definition.md, change the debit trigger to destruction or claim. Add a B6 range arm "sacred work damaged but standing", which must not move Enclave goodwill.
- a kept mechanic with no definition (bars.json R3 (unpaid-sacred floor "across all Cathedral maps") with R6 and B4; definition.md, at a 40-colonist scale and Costs and recovery). R3 holds the hum and bolts at least at their first non-calm warning on every Cathedral map while any sacred receipt is unpaid, including a neighbouring map with no marker on it. R6 sends bolts only to "active reachable causes". The definition says "Public inspect text reports observable activity and mood, never its hidden cause." Nothing says what the bolts do, or what any cue points at, when the floor is the only cause. B4 promises the player can "locate the offending work", and B4's intent rejects "location cues pointing at innocent work". A newcomer who hears an uneasy hum on arrival has no defined way to tell an old bill from current work, and may cancel innocent jobs hunting for it. Would pass: A defined floor-only behaviour. Bolts hold non-calm stiffness without gathering at any work. One observable cue (a hum inspect line or arrival notice) states that an unpaid damage bill stands and on which Cathedral tile. B4's range gains a floor-only arm: no active cause, on the origin map and on a neighbouring map. Smallest fix: Add one sentence to R3 and R6 defining the floor-only cue and the bolts' behaviour under it. Add the floor-only arm to B4's range, and a reject picture to B6: "An inherited uneasy hum sends bolts toward innocent haulers."
