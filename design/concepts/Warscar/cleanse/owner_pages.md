# What the Warscar now is

You scavenge a cursed cratered plateau where shattered floors and stripped defenses show a last stand whose enemy remains unexplained. Crust grazers, living munitions and carrion cleaners survive here, untreated wild plated grazers eventually turn dangerous, and prolonged salvaging leaves a mental scar. Calm brings toxic dust and visible movement records, returning wind lifts both away, and ordinary shelter makes expeditions possible.

**Land** comprises sterile contaminated floors, slag and craters, stripped defenses, already opened and destroyed ancient dangers, dry sky, native-map harmless tracking guns and the lingering mental cost of residence.

**Life** keeps the existing roster, crust forage, ordinary feeding/weapons/taming, readable remains and warned grazer onset. Medical cure remains possible under ordinary scaria restrictions.

**The signature** is the calm, toxic fall, ground record and wind-driven lift cycle.

Hospice recovery was my runner-up. Its repair, chemistry, research and history chain serves a separate experience. Your earlier fabulous-technology answer remains a future promise, with accepted memories, permanent lacquer and broad usefulness preserved. These scope choices are mine under the cleansing instruction.

**Next version, switched off**

- Wall-colossus encounter.
- Invisible hunter, drag clues and lacquer cloaks.
- Dust harvesting/uses and buried-shell minesweeper.
- Mark trade bonuses and privileged panel caches.
- Manuals, transcriptions and premium buyers.
- Hospice, histories, repair, walk-ins and rewards.
- Reaction pools, reagents, taps and dissolution.
- Turret refits, projectors, screens and shielding upgrades.
- Bileworm mood aura and scanner discoveries.
- Campaign kits, lore integrations and the previously deferred Open Boast.

Bare mark accrual, mood, nightmares and the lasting floor stay. Removing them would erase the frozen sheet’s explicit promise that salvagers return marked in mind. Their trade rewards remain independently switched off.

I recommend retiring the plate-dye veto because ordinary hide needs no separate aesthetic restriction, and the legacy planet-rarity control because worldgen is permanently excluded. Existing shared screen services remain available to neighbours.

The inventory has 81 capabilities, with 42 kept, 37 next version and 2 recommended retirements. Before this cleansing pass there were 0 concept bars and 0 live-only concept bars, as the CASE records. After repair there are 10 bars and 7 live-only bars. The proposal contains 11 checks, 10 rules, 5 unknown shared meetings, 4 models, 45 tickets and 0 questions. These counts match result.json and its source files. Kept includes shared and development dependencies.

# What to check

These are my decisions after reading the reviewer’s refusals and their cited sources.

- **Mad grazers** means every untreated wild chatrak remaining here eventually progresses, including initially clean arrivals. Medical cure cancels pending onset and exempts that animal from automatic reinfection. The frozen sheet requires inevitability. The clean-animal build criterion came from an agent. Vanilla scaria taming restrictions stand.
- **Cursed in mind** keeps the bare mark and lasting mood cost. Leaving ends mark-origin nightmares, returning restores eligibility, and roofs do not stop accrual. The current ungated nightmare route requires repair under the existing permanence ruling.
- **Spent dangers** includes Odyssey ruin payloads. Sprung clusters and cracked-open vaults lie destroyed beside ordinary sealed salvage. A dormant sealed threat that wakes on opening fails the land bar.
- **Poisoned forever** means a saved native source. Renewal writes ordinary pollution only where neither a player floor nor a roof covers native ground. Coverage pauses renewal, existing pollution needs cleanup, and removing coverage restores the source. Source inspection and the pollution overlay show what happened.
- **Native food** requires pollution-tolerant crust flora on clean and polluted native substrate. Their current missing tolerance would kill the grazer food supply. The plant-field check and establishment ticket now require that repair.
- **Natural recurrence** requires the unlocked season itself to complete calm, fall, returning wind and lift at shipped defaults. A missing cycle is a stall. Inconclusive evidence stays unmeasured for another natural run. Forced replay supplies diagnosis only.
- **Silent guns** track on Warscar by default. The current def-wide comp needs a biome gate. Off-biome tracking requires the existing unsupported opt-in, switched off, and its selected-map predicate.
- **Bodies, traces and reload** require physical remains/recoverable gear, actual recent crossings, coupled film/record clearing and resumed saved behaviour. Field equality alone cannot establish these experiences.

**Models, in build order**

- Situation and transition generator tests gates, treatment, coverage, mark departure and saved transitions.
- Whole-map season model tests natural recurrence, exposure, food and colony work together.
- Geometry and trace sweep tests boundaries, cover, threat payloads, track capacity and coupled clearing.
- Food-web and onset ledger tests feeding, remains, inevitable onset, cure and warning-to-retreat paths.

The models specify game calibration and the decisions their outputs change. They remain unbuilt. Combined presentation still needs a live look/listen. Seasonal exposure, ecological turnover, coupled save recovery and default gates remain unproved. Campaign implementation is unknown in this checkout. The earlier reviewer refused the proposal. These repairs await its second look and owner reading before application.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a contradiction with a standing ruling or the lore (bars.json W8 range and control; R8; tickets.md T23; census.json cross_biome and silent_guns). standing_rulings.md:133-140 (owner, 2026-10-15): "We can't guarantee they will work in other biomes beyond our framework. They should… but we're not going to validate that at this time." The same ruling adds that no new mod builds a cross-biome switch. census cross_biome says the existing opt-in's coverage is 'Settling and WreckLichen only', yet the proposal extends it: 'T23 also gates existing def-wide gun tracking through this same off-biome opt-in'. W8 range includes 'existing unsupported opt-in off/on', and T23's acceptance test requires 'Enabling the existing opt-in permits tracking only on its selected maps'. That gives an unsupported switch new coverage and makes a cross-biome validation part of passing. Would pass: Gun tracking is gated on Warscar membership plus the master and feature switches, with no off-biome route. W8 and T23 check only that tracking is absent on an unrelated biome at defaults. Smallest fix: Delete the opt-in route from R8, T23 and the census cross_biome/silent_guns text. Strike 'opt-in off/on' from W8 range and the opt-in-on sentence from T23's acceptance test.
- a sourced core promise omitted or weakened (definition.md 'Evidence boundary and reading receipts' paragraph; owner_pages.md (whole)). ANSWERS_OWNER.md:3 and :9, owner write-in 2026-11-10, verbatim: "it's the story of radiation seeping in but fabulous technology too". The pages tell him the technology half was deferred. The radiation half is reinterpreted silently: definition.md says 'the specific radiological Warscar text are not grounds for an adapting-bioweapon simulator … the land uses conventional toxin paths', and the word radiation appears nowhere on his pages. The_scarlands.md §3 ('Million-year nuclear decay chains — heat and radiation') backs the same promise. Would pass: The definition says what carries 'radiation seeping in' in 0.1.0 (for example: fallout dust and self-renewing ground deliver it through ordinary toxic buildup, named as such in player text). Page two lists that reading as a settled ambiguity, beside the technology deferral. Smallest fix: Add one ambiguity entry and one page-two line: 'radiation seeping in' is read as the dust fall plus native renewal through vanilla toxic buildup, and the label/description text says so. Drop the strawman about an adapting-bioweapon simulator.
- a figurative word unmarked (bars.json W3 says ('readable remains'), W6 says ('readable until wind…'), W9 meant.figurative). W3 and W6 both use 'readable', which is the very word ambiguity 10 argues over ('any vanish with a log?' versus remains in the world), yet neither bar marks it. W9 carries a figurative entry for 'read', but W9's says does not contain that word, so the entry seems to have been attached to the wrong bar. Would pass: W3 and W6 each mark 'readable' (W3: a physical remains/gear sign in the world, not a log line; W6: a direction a player can follow at play zoom), each with an accept picture. W9's stray entry is removed. Smallest fix: Add the two figurative entries and delete W9's.
- evidence that cannot tell success from a plausible false pass (bars.json W2 accept[2]; W5 accept[1]). W2 accept 'Imported meals and powered hydroponics serve a sheltered colony while the surrounding native floor remains sterile' is fully satisfied by a build with no renewal at all, which is W2's own lazy reject ('exposed native ground stays harmless'). W5 accept 'The transition still happens while attention is elsewhere and ordinary toxic weather also runs' is satisfied by W5's lazy reject ('Dust appears but health never changes'). A cold reader who accepts either picture accepts the false pass. Would pass: Each accept picture contains the element that separates it from the lazy build. Smallest fix: W2: '…while exposed native floor beside the hydroponics bay regains pollution after cleanup.' W5: '…the unattended transition still doses an exposed worker and spares the roofed one while toxic weather also runs.'
- a contradiction with a standing ruling or the lore (tickets.md T23 ('Correct shipping label to the later house form "the Warscar"'); ambiguities.md item 25; bars.json C8). biome_mod_architecture.md:567-570 records a 2026-09-26 card ruling 'the Warscar'. But warscar_turn3_development_2026-09-30.md §0 line 23 records a later card (2026-09-30, volley turn 2): 'the label is "Warscar", with no article'. RM_Warscar.xml:14 and :60 also carry no article. The proposal calls the 2026-09-26 form 'later' without addressing the 2026-09-30 record. Would pass: Either the label is left as built, or the conflict between the two dated cards goes on his pages as a question, with both sources and the default taken. Smallest fix: Remove the relabel from T23 and C8. Add a page-two question citing both cards, defaulting to the later record (no article).
