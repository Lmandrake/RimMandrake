# Page one — what LongShade would become

You live in a dry dayside desert where a low, fixed sun makes shelter the useful geography. Native animals rest in shade, dash across exposed gaps within their endurance, then rest again; you make routes with ordinary roofs and parasols while responding to ordinary heat. A Gloomcast carries real shelter through the landscape, while a Mirrak offers shelter that only looks real and can be identified before commitment.

Land: walkable sand, buildable ground, rock, sparse plants, dry weather and a fixed sunset, all under the shared geometric sun.

Life: the existing cast, real forage, feeding grazers, ground prey, hunters, scavengers and tameable stock; fictional flyers actually fly. No roster evictions or protected-art changes.

Signature: real or apparent shelter changes exposure, which drives crossings, recovery and the next refuge; ordinary construction changes those routes. Shipfall Commons lost as runner-up because staged wildlife attraction is another system, unnecessary to real ship shade.

These scope calls are mine, delegated by this pass, not new rulings from you. Your later colonist answer governs: people react when overheating; natives have evolved movement. Ordinary gear research remains available without lessons. Plain dung remains the already-accepted feeding sign, separate from seeding.

Next version, switched off:

- Moss competition and contact venom.
- Vorrel lethal fruit cycle and prepared dish.
- Study discounts and return-range overlay.
- Wreck road, local road salvage and crawler terminus.
- Long Carry remains and supplies.
- Shipfall attraction, departure dispersal and messages.
- Midden seeding, searching, Vrekka building/tending.
- Static clean-lair markers and Tollok infestation.
- Stampedes and Harrok’s special strip attack.
- Returning-clan tow and its required negotiation.
- Haze weather, heat sound beds, calls and distant footfalls.
- Welcome letter, if its historical caller still exists.
- Dung fertilisation, plant/young-animal seeding, vacstone output and special hide bonus.
- Exact-rim Sippra travel, scarp attack/corpse carrying, dung-only/hardpan-only plant gates.

Harrok remains an ordinary scavenger with body shade; Vrekka still feeds. Vorrel’s plant stays visible, but its fruit harvest/ingestion is unavailable at defaults. These decouplings need tests; they are not accomplished by this proposal.

Recommend retiring: the lure awning duplicates ordinary roof shelter; the chitin mast duplicates shelter tools and conflicts with your parasols-and-roofs ruling; haze’s shadow-length multiplier conflicts with pure geometry; Tazzok’s ash-only schedule depends on the already-cut ash act. Their code, defs and kept art stay dormant; retirement is yours.

Census: capabilities 67 inventoried, 33 kept; 30 next version and 4 recommended retirements. Locked old bars 0 and old live-only bars 0: the CASE has no tree leaves, although scripts exist. Proposed bars 8; live-only bars 2. Supporting work: 12 checks, 8 rules, 5 unknown meetings, 3 models, 44 tickets, 0 questions. The absent shared colonist response adds the capability and build ticket. These counts come from result.json and the proposal files, not a runtime acceptance.

# Page two — what to check

The consequential readings I took:

- “Currency” and “gamble”: shelter decisions and exposure, not money or random failure.
- “Nothing survives the sun”: conditional endurance, not instant death or despawn.
- “Low sun”: actual tile geometry, never a private angle, heat kind or offset.
- “Golden hour”: dayside stays fixed; weather remains unlocked.
- “Cooling”: removes sun exposure; hot air can still kill under a roof.
- “Strict dashing”: natives must visibly rest, dash, rest at shipped conditions, including mild sunlight; vanilla wandering fails even without injury.
- “Overheating”: the shared colonist response is absent. My contract interrupts ordinary work at Direct Sun overheating onset, before Serious Heatstroke, seeks the nearest reachable lower-exposure recovery cell including outdoor roofs/parasols, then resumes valid work; drafted, mental and lethal-air states are excluded. Your deeper Designer discussion is still owed.
- “No pursuit”: bounded local attack and retreat, never endless exposed chase.
- “Rim-only”: recruitment in a shade transition band; established plants do not teleport or instantly die when shade changes.
- “Followers”: intermittent, with ordinary needs; existing selected species stay selected.
- “False shade”: observation raises suspicion; safe inspection confirms even when the animal aligns with real shadows. No actual cooling; losses leave ordinary readable evidence.
- “Off”: jobs, effects, availability and saved resumptions stop, not just incident rolls. Shared engines still serve retained features and other biomes.
- “Built”: source presence, historical proof and current runtime acceptance remain separate.

Models, first to build first:

- Shelter geometry/exposure sweep: compare real masks, visible shade and heat, including movement, death and reload, against runtime reads.
- Situation/transition generator: enumerate native needs, hunting, followers and worker priorities; use actual runtime decisions where offline AI cannot be trusted.
- Whole-map season/food ledger: all retained mechanics on, extras off, weather and research unlocked, mid-way reload and reversed work order; calibrate growth, consumption, recruitment and losses before believing its predictions.

Still unsettled by argument: geometry agreement, competing job priorities, food supply, population stability and weather’s combined effects. Each has a model. Current source still declares legacy biome heat and sun clamps; I have specified compliance work, not presumed it done. Actual fixed-world climate might expose a conflict with the crossing experience. If it does, show the calibrated evidence; do not invent hotter LongShade sunlight.

Nothing is applied. No game was run and no current gameplay proof is claimed. The first reviewer refused the undefined colonist response and weakened dash promise; both are repaired here, with the independent second look pending; the existing owner hold remains in force. Nothing here changes the mod before you read these pages and say so.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- two bars, or a bar and a rule, that cannot hold together (design/concepts/LongShade/cleanse/definition.md, the colonist response contract (Kept mechanic contracts, bullets 1 and 2); tickets.md T44; bars.json B7 and B8). definition.md: response onset is when Direct Sun 'raises a conscious undrafted colonist's felt temperature above that pawn's comfortable maximum, while the local air alone permits recovery'; the pawn should 'rest until felt temperature is within the comfortable range and any Heatstroke has cleared; then return control to ordinary work selection'. Vanilla GenTemperature.SafeTemperatureRange = ComfortableTemperatureRange with max += 10 [measured, RimSage Source/Verse/GenTemperature.cs], so this onset fires about 10 C before any Heatstroke can build. On a fixed-sun map the sun term never goes away. If air is below comfort max and air plus sun is above it, the worker is interrupted, reaches a refuge where felt = air (already inside comfort), so recovery is met at once, resumes the job, steps back into the sun and is interrupted at the next poll. The contract has no hysteresis, no tolerated-exposure budget and no minimum work interval, so any exposed leg longer than one poll never finishes. B7 accept picture 1 is exactly such a haul between covered areas. This is the 'repeated job churn' that definition.md (Costs and failure signs) calls a whole-run failure, and it fails B8's 'stalled jobs' and T44's own 'no job churn'. In the other case, air alone above comfort max (hot desert air), 'air alone permits recovery' is false and the response never fires, so the hottest days get no response at all. Would pass: A contract whose onset and release leave room for exposed work to finish: either onset at the start of harm (felt temperature above the pawn's safe maximum, where vanilla Heatstroke starts building) or a tolerated-exposure budget like the animals' RangeCost, and release at a level below onset (for example Heatstroke falling and felt below onset) instead of 'within comfort and Heatstroke cleared'. Plus a B7 reject picture for the oscillation, so a judge can refuse it. Smallest fix: In definition.md and T44, change onset to 'felt temperature above the pawn's safe maximum (Heatstroke building), before Serious', and change release to 'felt below onset and Heatstroke not rising'. Define what 'air permits recovery' means in hot air. Add to B7 reject: 'A worker shuttles between a roof and an exposed haul and never completes it.' Add that oscillation to M2's planted defects.
- a figurative word unmarked (design/concepts/LongShade/cleanse/bars.json B6 says ('provides no cooling'); B1 says ('sparse living shelter', 'fixed sunset')). B6.meant.figurative is []. By the proposal's own reading (ambiguities.md item 6; owner_pages.md '"Cooling": removes sun exposure') and the Direct Sun ruling ('Ambient heat is normal Rimworld rules'), real shelter does not cool either. So 'no cooling' taken literally holds for real shade too, and the bar's meaning is 'no reduction in Direct Sun exposure'. B6's accept picture 2 says that in other words, but the word is never marked. B1.meant.figurative is [], but 'living shelter' can mean shelter made of plants or shelter where animals live; its accept picture shows shaded rocks, which are not alive. 'Fixed sunset' literally means a setting sun; it stands for a permanently low sun angle (ambiguities.md item 5). Would pass: Each of these words is listed in its bar's figurative entries with what it stands for and one accept picture that departs from the literal reading. Smallest fix: B6 figurative: {word: 'cooling', stands_for: 'reduction of Direct Sun exposure; air temperature is never changed', accept: 'A pawn on a Mirrak's apparent shade has the same sun exposure as the open cell beside it'}. B1 figurative: 'living shelter' (state whether it means plant casters or animal refuges) and 'fixed sunset' (a permanently low tile-derived sun, with the sky allowed to dim in weather).
- an extra left in the first version without its needed_by deletion argument (design/concepts/LongShade/cleanse/census.json row dewfringe_rim (fate 'signature', needed_by null); definition.md Kept mechanic contracts, bullet 3; bars.json R4). The census says 'Delete the spawn rim and the player loses the living boundary used to read established shelter', and definition.md says 'Deleting that gate makes the boundary vegetation generic and defeats its signature read.' But the signature as stated ('real or apparent shelter changes exposure, which makes native animals cross, recover and choose their next refuge while the colony can alter those routes') has no plant-border step, and no bar reads shelter through dewfringe. B1 reads shade from physical casters; B4 needs dewfringe only as forage, and the census row itself says 'toggles fall back to ordinary fertility/terrain spawning'. The gate is a plant with its own mechanic (a Harmony spawn postfix, RM_Patch_DewfringeWildSpawnGate.cs) and was kept on an argument no bar backs, while other owner-approved touches (Tollok, the Harrok strike, middens) were moved. Would pass: Either the rim gate moves to next version (switched off and labelled, with dewfringe spawning by ordinary fertility, so B4 forage is untouched), or a deletion argument names a kept bar or signature step that fails without the rim, with needed_by filled in. Smallest fix: Set dewfringe_rim to next_version with a switch-off ticket (acceptance: with defaults, dewfringe spawn candidates ignore shade fraction and the log is clean; with the setting on, rim recruitment returns). Delete or narrow R4, and drop the rim clause from definition.md bullet 3. Keep the plant and its sprig as life.
