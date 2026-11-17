# Page one — the proposed mod

The Weeping Stones is bright stone country where black wet faces and green pools interrupt the dry ground. Native animals gather at protected water, while colonists forage, raise keeping crops and build on the dry shoulders. Its moisture farmers raise troublesome pool stock for food: tending preserves breeders, neglect or crowding can produce a vhorrin, and a deliberate cull lets the farm recover.

**Land:** dry pale stone, wet shaded faces, green pool margins and the explicit hot open-seep exception.

**Life:** the existing alien plants and animals, ordinary forage, medicine, keeping crops, timber, wild fishing and tame/caravan uses; real flight and the existing water truce. No roster evictions.

**Signature:** tending stocked pools preserves a renewable food source; mismanagement produces a farm-eating vhorrin and the need to cull and recover.

The runner-up was the walking condenser. It is a separate moving-oasis story, so I moved it rather than make the farm wait for terrain migration, a sale contract and quests. This is my scope decision under your cleansing instruction. Your earlier approval remains in its next-version design.

**Moved to the next version, off by default:**

- The unique condenser crab, moving pool and seasonal choices.
- Guiding, destination sale/delivery, extraction and flask production.
- Collector capture, keep-free hunters, quest claims and faction-slot effects.
- Cocoon-to-dewsilk manufacture; rendered huldu fat; special angling loot.
- Local plant research lessons; special animal auras, climbing and swarms.
- Animal-made basins, giant collision geometry, special species catch jobs and cooperative culling.
- Infrastructure progression, pilgrim/courtship choreography, annual farm lockout, additional food-belief events and unique oasis chords.
- The Refused Toll stays where you already put it: later.

I recommend retiring **ivvol's proposed absolute vhorrin immunity**: it removes the consequence of bad husbandry. Ivvol stays as a living creature and doubtful food; farmers can still tell stories about it. Nothing is retired by this proposal. The already rejected wind-hour and born-and-dying-water are not revived.

**Counts:** capabilities 68 inventoried before, 39 kept, 28 next version, 1 recommended retirement. Old bars 0; proposed bars 9, including 3 live-only bars. Before, there were 0 live-only bars [measured: the CASE has no old tree leaves]. The inventory includes dependencies and unbuilt promises; these are not counts of working features. Checks 13; rules 14; unknown meetings 10; models 3; tickets 24; questions 0. These are the counts in result.json.

# Page two — what to check

These are my defaults, not new words attributed to you:

- **“A pool”:** the named contiguous water pen the farmer selected; neighbouring zones keep separate histories, and edits/reload cannot erase feed debt.
- **“Sustainable”:** actual births and repeated surplus from retained breeders. Repeatedly capturing wild replacements is not a farm.
- **“Harvest is a choice”:** a small reserve/destination/harvest control. Current workers can automatically liquidate every breeder; that needs repair.
- **“Feed”:** permitted suitable nutrition must support actual animals as well as the care clock; safe bank delivery does not need cocoon waste.
- **“Read”:** visible productive, hungry/thin, crowded, empty and vhorrin cues before avoidable loss. Inspect text alone is insufficient; a fed crowded pen cannot reassure until the monster appears.
- **“Eats the farm”** now means a due pen-stock conversion leaving partly eaten remains and a named cue. I chose this route to preserve shared hunt suppression. Culling stops consumption, and save/load preserves the feeding deadline. The reviewer correctly found this route undefined.
- **“It escapes”:** a visible reachable route, no invisible wall-crossing teleport. Net success still follows landing coverage and target movement, as you ruled.
- **“Truce”:** the existing shared radius/guilty-hit law, tame predators included. Ordinary farm care must coexist with it; player gunfire gets no private exemption.
- **“Shade”:** the shared geometric Direct Sun rule. Current local heat fields and arrival advice contradict your later roof/parasol ruling and must be corrected.
- **“Weeping”:** the actual wet/dry habitat picture, without commissioning a water-budget simulator. Hot flat seep pools need no cliff.
- **“Native built”:** a def is insufficient. Mirrik's natural spawn route is unproven; shared dewshrooms still owe your distinct-variant rule. Neither finding authorises evictions.
- **“Doubt”:** actual eater/ingredient memories and callous-trait exceptions; no extra ideology, quality or colony ceremony system.
- **“Scarce timber”** means scattered gatherable trees whose local depletion limits wooden building. The life bar now rejects both treeless and forest-covered maps, addressing the reviewer's second finding.

**Models, first to build first:**

- **Whole-map husbandry season:** whether births, feed, work competition, growth, predators and harvest can sustain a farm without animal flooding or stripped habitat.
- **Situation and transaction generator:** edits, workers, moving nets, vhorrin feeding/cull ordering, remains, truce callbacks and saves, with animals/items accounted for.
- **Wet land and shade geometry:** actual wet faces, irregular green margins, open seep exceptions and accessible dry building/bank ground on existing authored tiles.

Each model specifies inputs, limits, real-game calibration and the decision its output changes. They are not measurements or completed instruments. The main unknowns are real breeding/residency, staffing/feed demand, stock-pressure/recovery, callbacks/save continuity and coherent habitat. Those unknowns are the first build work, not questions asking you to predict a test.

No game was started or source changed. This is a proposal awaiting fresh review and your reading before application; no reviewer verdict is claimed.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a contradiction with a standing ruling or the lore (bars.json B6 (third accept picture), B8 (meant, range), R14, meetings.truce_field; definition.md 'When it goes wrong' (R14 paragraph); ambiguities.md item 19). The ruled stocked-pool sheet (design/Jawa/worldbuilding/biomes/weeping_stones_stocked_pool_2026-09-24.md, Status RULED 2026-09-24) says in §1: 'The truce holds at the water (§4) — and the pen is not the truce. What happens inside a stocked pool is husbandry'. Its 'Pens and pool zones' paragraph adds 'the pen line is what keeps husbandry violence out of the truce's sight (§6, §4 both honored by geometry)'. The proposal does the opposite. It treats pen water as protected truce water ('Shared predator hunts remain suppressed at that same water'; B6: 'a predator hunt at that same protected water remains suppressed'; B8 range: 'a due vhorrin stock-feeding conversion at protected pen water while hungry wild/tame predator hunts remain suppressed'). It then builds R14's long-range bookkeeping conversion to get around a conflict that the lore had already settled by geometry. Neither meetings.truce_field nor the owner pages mention the sheet's line, and the owner pages state only 'the existing shared radius/guilty-hit law'. Would pass: The truce_field meeting and B6/B8 follow the sheet: designated pen cells are husbandry ground outside the truce, so the vhorrin feeds there by ordinary predation that leaves a readable carcass, while drinkers at the margin stay protected. Or the proposal keeps R14, cites the sheet line, argues why it departs from it, and puts that departure on page two as a question with its evidence. Smallest fix: Add a rule that stocked-pen zone cells are not truce water, as the ruled sheet says (the shared engine needs a narrow exclusion hook, named as a dependency need rather than a redesign). Rewrite B6's third accept picture and B8's range to match, and drop or shrink R14. Or keep R14 and list the contradiction with the sheet line as a question on owner_pages.md page two.
- a figurative word unmarked (bars.json B8 says ('does not turn the gathering against its handler') and B9 says ('lives among dry stone and wet native gatherings'); both figurative: []). B1 marks 'gathered' as figurative: 'Green clusters follow wet habitat rather than filling the whole map; not literal moving or social plants'. In B8 'the gathering' means the water wildlife (animals), a different sense. In B9 'wet native gatherings' could mean either the plant clusters or the congregated animals. Both are unmarked, so a builder and a judge can read different subjects into the same word. Would pass: Each bar's figurative list marks 'gathering(s)' and says what it stands for (B8: the wildlife standing at full water; B9: plant clusters at wet habitat, animal congregation at water, or both), each with an accept picture that departs from the literal reading. Smallest fix: Add a figurative entry for 'gathering' to B8 and for 'gatherings' to B9, or replace the words with the literal subjects ('the water wildlife'; 'wet native plants and animals').
- a figurative word unmarked (bars.json B4 says ('with handling risk confined to the catch'); figurative: []). Read literally, 'the catch' is the NET capture job. Yet census.json keeps harvest_injury as part of the signature ('risks minor scratches for skarrin/iaala'), and census row 'cull' keeps a cull that 'risks a bite'. The ruled sheet's HARVEST row says 'Handling injuries are real'. B8's reject picture mentions 'a farm handling scratch' during farm care. A builder holding the literal B4 would remove the harvest and cull injuries; a judge could then refuse for missing nastiness, or pass a build with the injuries left in, depending on reading. Only feeding is clearly meant to be safe (definition.md: 'feeding at the bank has no handling-injury roll'). Would pass: B4 marks 'the catch' as figurative for every hands-on contact with stock (net, bag, harvest, cull), as opposed to bank feeding, with an accept picture showing a harvest scratch or cull bite. Or the says sentence names the jobs literally. Smallest fix: Reword B4 to '...with handling risk confined to hands-on catching, harvesting and culling, never bank feeding', or add the figurative entry.
