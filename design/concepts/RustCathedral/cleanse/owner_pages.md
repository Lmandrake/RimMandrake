# Page one — what I propose

You enter a flat metal maze whose corridors lead past salvage, recognisable toxic pools and machine-held ground. Taking ordinary scrap is useful, but cutting marked shortcuts, disturbing canal life or damaging protected works changes the hum and draws living bolts toward the offending work. Stop and withdraw after minor disturbance; sacred destruction or claim requires material repayment and costs Enclave goodwill, while deep intrusion brings machines against the drill.

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

- **Maze/free salvage:** useful connected corridors; the bulk of reachable metal, including unmarked corridor walls, is free; marked dividers and sacred works are exceptions, and cutting marked shortcuts can anger the hum. Guardians in existing chambers supply the trap; no random-trap system.
- **Pools:** existing toxic/irradiated terrain supplies stationary harm; sulfuric edges supply the acid look. No true acid mechanic. Safe public routes and repayment approaches avoid them. Canal-free maps still have pools. Historical provider names must be resolved before building.
- **Warnings:** bolts indicate actual disliked work; a basic work-site cue covers absent or blocked bolts. No reader or plot unlock. The fishing reading must first show an attributed rise above calm, then compare cancellation with continued fishing; always calm cannot pass recovery.
- **Sacred currency:** I corrected my local-ledger substitution. Your August ruling uses real Free Droid Enclave goodwill and its isolation consequence. Sacred receipts and payments persist across Cathedral tiles and reload; local hum standing only mirrors them. The debit fires on destruction/strip or claim, per the August destruction ruling; damage while standing and unclaimed raises only fast irritation and warning. The permanent-enemy Arsenal is a different faction.
- **Unpaid access:** my delegated rule keeps the hum above calm while any sacred receipt remains unpaid, including below diplomatic hostility. Multiple debts add pressure. With no active cause, bolts stay stiff without gathering at work; the hum inspector identifies unpaid bills and their originating Cathedral tiles, including on neighbouring maps. Enclave hostility closes actual contact without expanding guard pursuit or summoning an army. Repayment removes its receipt; future contact returns when the real relation recovers. Past prisoners and cancelled trades are not undone. Ordinary gifts can restore diplomacy sooner, but leave the unpaid material receipt and warning.
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

- the converge fix broke an entry it changed (the verifier's words) (bars.json bars/B2). B2.accept now reads "A worker mines an unmarked deck-plate corridor wall and hauls its steel without offence; the surrounding ordinary walls are also free salvage". Its figurative accept reads "A crew mines ordinary corridor walls freely across the maze while leaving marked shortcut dividers ... intact". B1.says (bars.json:5) promises the crew can "choose an open route or a visibly marked trespassing cut". ambiguities.md entry 2 rejects reading A because it "makes every maze route optional without cost". Nothing in B2 says what happens when mining a free, unmarked corridor wall connects two routes. A build where most corridor walls are free and unmarked, and mining one opens a shortcut with no consequence, passes B2's new accept pictures. That same build empties B1's route choice: every marked cut has a free unmarked bypass. B2 and B1 now cannot hold together on that build. Would pass: B2 says that free unmarked wall is wall mass that does not join two routes when removed (backing, thick wall bulk, outer facades, worked-out spurs). Any wall whose removal would open a route between corridors or into held ground is a marked divider, visible before designation. A reject picture catches a free unmarked wall that opens a costless shortcut. Smallest fix: In B2.meant.figurative "most of the metal in sight".stands_for, add "free walls are wall mass whose removal joins no two routes; a wall whose removal opens a route is a marked divider". Add to B2.reject: "Mining an unmarked corridor wall opens a shortcut between routes with no warning or consequence, bypassing the marked cut." Add that arm to B2.range.varies.
