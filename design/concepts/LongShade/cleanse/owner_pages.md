# Page one — what LongShade would become

You live in a dry dayside desert where a low, fixed sun makes shelter the useful geography. Native animals rest in shade, dash across exposed gaps within their endurance, then rest again; you make routes with ordinary roofs and parasols while responding to ordinary heat. A Gloomcast carries real shelter through the landscape, while a Mirrak offers shelter that only looks real and can be identified before commitment.

Land: walkable sand, buildable ground, rock, sparse plants, dry weather and a fixed sunset, all under the shared geometric sun.

Life: the existing cast, real forage, feeding grazers, ground prey, hunters, scavengers and tameable stock; fictional flyers actually fly. No roster evictions or protected-art changes.

Signature: real or apparent shelter changes exposure, which drives crossings, recovery and the next refuge; ordinary construction changes those routes. Shipfall Commons lost as runner-up because staged wildlife attraction is another system, unnecessary to real ship shade.

These scope calls are mine, delegated by this pass, not new rulings from you. Your later colonist answer governs: people react when overheating; natives have evolved movement. Ordinary gear research remains available without lessons. Plain dung remains the already-accepted feeding sign, separate from seeding.

Next version, switched off:

- Moss competition and contact venom; dewfringe rim gate (plant and sprig stay).
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

Census: capabilities 67 inventoried, 32 kept; 31 next version and 4 recommended retirements. Locked old bars 0 and old live-only bars 0: the CASE has no tree leaves, although scripts exist. Proposed bars 8; live-only bars 2. Supporting work: 12 checks, 8 rules, 5 unknown meetings, 3 models, 45 tickets, 0 questions. The absent shared colonist response adds the capability and build ticket. These counts come from result.json and the proposal files, not a runtime acceptance.

# Page two — what to check

The consequential readings I took:

- “Currency” and “gamble”: shelter decisions and exposure, not money or random failure.
- “Nothing survives the sun”: conditional endurance, not instant death or despawn.
- “Low sun”: actual tile geometry, never a private angle, heat kind or offset.
- “Golden hour”: dayside stays fixed; weather remains unlocked.
- “Cooling”: removes sun exposure; air above comfort may permit recovery below the safe maximum, but hotter air can still kill under a roof.
- “Strict dashing”: natives must visibly rest, dash, rest at shipped conditions, including mild sunlight; vanilla wandering fails even without injury.
- “Overheating”: the shared colonist response is absent. My contract responds to harmful Direct Sun above the safe maximum, before Serious Heatstroke, seeks the nearest reachable recoverable roof/parasol refuge, then resumes valid work after recovery to a lower injury threshold; work must progress across repeated cycles; drafted, mental and lethal-air states are excluded. Your deeper Designer discussion is still owed.
- “No pursuit”: bounded local attack and retreat, never endless exposed chase.
- “Rim-only”: the planting gate moves to next version; dewfringe/sprigs remain ordinary forage with fertility/terrain recruitment.
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

- the converge fix broke an entry it changed (the verifier's words) (tickets.md T44: Build the shared colonist onset-of-overheating response). T44 says 'air above comfort but below the safe maximum can qualify'. Its acceptance test requires 'Repeat with air between comfort and safe maxima and verify refuge recovery and useful work'. Vanilla Verse/HediffGiver_Heat.OnIntervalPassed [measured, RimSage] raises severity only when ambientTemperature > SafeTemperatureRange().max. It lowers severity only when 'firstHediffOfDef != null && ambientTemperature < floatRange.max', where floatRange is ComfortableTemperatureRange. Between the comfortable and safe maxima, Heatstroke neither rises nor falls. The T44 release needs 'severity reaches the lower recovery threshold', so in that air a sheltered worker never reaches it and waits in the refuge indefinitely. That is a stalled job, which T44's 'no job churn' and B7/B8 refuse. The only way out is to change vanilla recovery, which the Direct Sun ruling ('Ambient heat is normal Rimworld rules') forbids. The acceptance arm can therefore never pass truthfully, and the contract and B7 cannot hold together in that air band. Would pass: The contract matches vanilla recovery. Either a refuge qualifies for full release only where protected felt temperature is below the comfortable maximum, so Heatstroke actually falls, or a refuge in the comfort-to-safe band holds severity steady and has an explicit release rule that cannot stall (for example release once severity is not rising and is below the intervention threshold). The acceptance arm then tests the behaviour that rule produces in that band. Smallest fix: In T44, replace 'air above comfort but below the safe maximum can qualify' and the 'verify refuge recovery' arm. State that in vanilla, felt temperature between comfort and safe maxima freezes Heatstroke. Then either exclude such cells from recovery targets when a below-comfort cell is reachable, or define release there as 'severity not rising and below the intervention threshold'. Add a planted defect: a worker parked forever in a comfort-to-safe refuge.
- the converge fix broke an entry it changed (the verifier's words) (bars.json meetings). The heat meeting (holds_together 'argued') now says 'Recovery needs protected felt temperature below the pawn's safe maximum and falling Heatstroke, not air below comfort; hot air between comfort and safe maxima can qualify.' Under vanilla HediffGiver_Heat [measured], Heatstroke falls only below the comfortable maximum. Felt temperature below the safe maximum together with falling Heatstroke therefore implies felt temperature below comfort. The 'can qualify' clause is false, so the construction argument rests on a recovery path that cannot occur. Would pass: The heat meeting's argument states the vanilla recovery band correctly (severity falls only below the comfortable maximum and is frozen between comfort and safe maxima) and resolves the frozen band without claiming recovery there. Smallest fix: Rewrite the clause as: 'Heatstroke falls only when felt temperature is below the comfortable maximum; between comfort and safe maxima it is frozen, and the release rule must not stall there.'
- the converge fix broke an entry it changed (the verifier's words) (definition.md Kept mechanic contracts and deletion arguments). Bullet 1 says 'air above the comfortable maximum still permits recovery if protected felt temperature is below the safe maximum and Heatstroke falls'. It releases only when 'severity has reached the lower recovery threshold'. By vanilla HediffGiver_Heat [measured], the 'Heatstroke falls' condition is never met above the comfortable maximum, so the sentence describes an empty case while implying such refuges work. Nothing covers a worker who reaches a comfort-to-safe refuge with severity above the release threshold. It cannot release and cannot re-arm, so it stalls; the record's R1 gap of 'Define what air permits recovery means in hot air' is left with a wrong definition. The same false claim was copied into ambiguities.md 'Reviewer repair: the missing colonist contract' ('Air above comfort can still permit recovery when protected felt temperature is below the safe maximum') and owner_pages.md 'Page two — what to check' ('air above comfort may permit recovery below the safe maximum'). Would pass: The contract defines recovery-capable destinations by the vanilla rule (felt temperature below the comfortable maximum for falling severity) and gives a non-stalling outcome for refuges in the frozen band. Smallest fix: Replace the 'air above the comfortable maximum still permits recovery' sentence with the vanilla bands. Add a non-stalling release for the frozen band, or exclude that band from recovery targets. Correct the copied sentences in ambiguities.md and owner_pages.md in the same change.
