DRY RUN — Wasteland / The Wastes Designer, stages 0 and 1

All proposed prose, interpretations and guesses are agent-authored. The only owner quotation copied into the deliverables is the existing Wasteland experience sentence, with its supplied experience-file source. root is null; root_draft is an agent proposal. The eight asks remain draft. No approval, waiver, stage result, new item or ledger entry has been created.

Identity and reading boundary

The requested src/RimMandrake/Wasteland directory exists but contains Source/obj build leftovers. The actual mod is src/RimMandrake/Wastes, with packageId mandrake.rm.wastes and namespace RimMandrake.Wastes; it ships composed inside mandrake.rm.biomes. The requested Wasteland.md walk is absent; design/validation_walks/RimMandrake/Wastes.md is present and was read. The October 21–22 rename is recorded at OWNER:1792637163737194094. The later “Wasteland ORPHANED” ledger note is a naming trap, not evidence that the mod or script disappeared.

Read the requested role core and packets in order, designer_examples.md, the HugeThings example's questions/record/notes, then the mod's source and its matching walk. Mod-specific design sources include wastes.md, wasteland_survivor_cast_2026-09-28.md and rosters/wastes.json. Searched design and item prose for Wasteland/Wastes, read the dedicated live/closed WASTELAND item files and relevant enrichment/fluff-review material, and read matching frozen/sharded ledger events. Direct neighbour interfaces were searched/read to resolve named implementation uncertainties. Broader world-history and unrelated references are not a claim of a full campaign audit.

record.json accounts for built gameplay, settings, integration data, assets, script support and relevant campaign counterparts, with impl/proof/scope kept separate. File accounting is not a full-file code-review certificate. Existing designer.log and designer_brief.md were left alone.

What could not be verified

- No running assembly, deployment, active mod list, settings, game, save, art, sound, tick cost or human experience was verified. No build, selftest, bridge, live scene or flight was run. No inventory proof is current.
- Latest located live evidence is mixed: November 6 at 55447a92b0d3 records PASS for the Middenshell incident-OFF component and the tipping offer-OFF component. At 72d15cb85a85, flora harvest A2 records PASS, processor A1 records FAIL, and the combined gripper/brine A3 records FAIL. The ledger also identifies a processor fixture's unpinned AnimalGatherYield roll and an earlier brine receiver drowning. Those are evidence to preserve, not permission to call every failure a mod defect or every feature accepted. Raw /home/mandrake/rm/relentless/live logs are not in this mirror.
- Closed items retain old “unbuilt/interim/owed” text. The campaign battery's discharge comp and legacy radiothermal heat/spacing/cook machinery now exist. RM_Excretor moved into Wastes and uses ordinary shearing. These must not be proposed as wholly unbuilt from the old prose.
- The Middenshell is a custom 20x20 Building. It does not use the HugeThings pawn engine or Large Pawns; old specification/review dependency claims are stale. Dedicated procession remains distinct from the open generic native-titan passage pool item. Twenty-cell width is not reopened.
- No authoritative owner approval of the newly proposed root, experience bars or flagship was found. The supplied experience file is explicitly accepted as the source of his chosen sentence. Earlier BENCH/FOUNDRY relays have not been relabelled OWNER. OWNER tsns used here were checked against the actual OWNER.jsonl shard.
- The old roster JSON and cast bible contain superseded donor names, vanilla rows and early register language. Current owned XML plus WildAnimals_Wastes.xml were read. The later experience word “victims” was not treated as authority to undo the earlier survivor register or create aggressive animals. No roster eviction or new renaming question was drafted.
- Actual dosimeter growth, deep sequestration/vault consequences, cross-family near-zero rot and redistribution of existing contamination were not established. Exact-name src C#/XML searches found no plant-specific runtime consumer for radmoss/vault-root/wartshrub. The flora defs have descriptions and ordinary growth/yields; they do not supply those mechanisms themselves. Broader global patches and all climate effects have not been ruled out, so preservation stays unknown.
- Cinderwire's effects are built but a natural occurrence path is absent in the bounded exact-name search. The terminator-only boundary is already ruled, so there is no question asking him to choose a technical biome gate. Its weather sandRate and MovingDunes transport may act before the warning controller releases dose/fall; the “quiet warning” experience needs an interaction check.
- MovingDunes binding now names both Moving Dunes and Baroque Biomes. The walk's old dead-FindMod diagnosis is stale. Binding fields do not establish completed burial/reveal, pollution transport or honest post-storm route information.
- Soot bricks have flammability and trade values, but a useful fuel consumer was not located by the exact-name src search. Do not infer chemfuel-equivalent refuelling from “burns” in prose. Pusberry yields ordinary berries despite “raw is a lesson” text. These are source/description mismatches to resolve from existing intent, not new owner approvals.
- RM_Smolderback and legacy RUT_Radiothermal share the label hessekh but have different mechanics and current residency. RUT_Radiothermal is not added by the current Wastes campaign roster patch. Its spacing/cook behaviour is not proof of RM hessekh's room-dose trade.
- The actual launch refusal, bay processing, illegal reburial job, complete tipping deliveries/rewards/evidence/finance, full Middenshell crossing/exit, tentacle protection, carcass mining/dose, new milk/shear output and scanner pulse lack sufficient Wastes-specific acceptance in the suite. Built data and OFF default pins do not close these promises.

Top five correctness risks from the source (static findings; no live reproduction)

1. src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:514 — Existing processingEnabled bays continue converting casks after caskProcessingEnabled is switched off; the global flag only hides the command at line 649.
2. src/RimMandrake/Wastes/Source/Kernel/RM_StormKernel.cs:101 — Turning named-storm warnings off suppresses TickStorm's EMP/lightning too, while the settings promise immediate storm effects with cues skipped.
3. src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:521 — Bay LeakPulse ignores its casks argument and never drains stored dose, allowing intact casks in failed containment to generate leaks indefinitely without depletion.
4. src/RimMandrake/Wastes/Source/RM_WasteCaskBay.cs:497 — The master switch does not gate bay heat evolution or PushHeat, so wastesEnabled=false can still warm an occupied room.
5. src/RimMandrake/Wastes/Source/RM_MiddenshellProcession.cs:193 — A blocked warned entrance can be replaced by another random edge at arrival, with no new preparation interval before danger appears there.

Proof-scene audit

The per-chain audit is in record.json.scene_audit. It covers all declared chains, including read-only checks and settings roundtrip. The suite has valuable present/absent, ON/OFF and room controls and several real instrument repairs. It does not yet implement the scene contract's asserted recovery/hold lifecycle.

The most consequential proof holes are these:

- The named-storm no-dose warning arm is about 460 ticks inside a shortened 625-tick warning, while the script documents a 3451-tick dose cadence. A broken hold can look correct when no dose was due. Its mock supplies the expected timing independently, so a mock mutant does not settle that runtime issue.
- Processor growth is inferred from inspect text, then fullness is forced. A gather result can fail from ordinary worker yield chance or merge into an existing output stack. This is not a measured sustained refinery rate.
- scatter_at bypasses the terrain validator. Reading mineableThing is not completing a mining job. Cask launch acceptance reads patch presence, not a real launch refusal and successful safe control.
- Clearing/teardown deletes things, leaves pawns, resets most settings to shipped defaults and locks Clear weather; it does not restore original terrain, pollution, gas, quests, map/world edits or storyteller. The accepted tipping quest survives pad cleanup. A scratch-map instruction needs an asserted disposable-save boundary and confirmed restoration/reload before it satisfies recovery.
- A filth count does not prove the permanent track/exit scar, and seam count does not prove a rewarding, dosed quarry expedition. Body size from the body's own inspect pane needs independent occupancy/interaction evidence.
- There is no ordinary-use or interaction acceptance for the colony living through storm, return, salvage, herd work and waste handling together. Separate feature scenes remain necessary even after a flagship is chosen.
- No live flight was staged here. Future state-only Grimewing fixtures should prevent accidental autonomous flight while other chains advance time, unless the owner is present under the standing flyer rule.

Dry-run adaptation and checks

There was no injected run ID, persisted stage, packet hash, alias list or budget. I did not fabricate stage.json, result.json, a tree, a gate result, a first-touch certification or a handoff to Relentless. A real launch must regenerate its exact built_evidence packet and compare that with built_reviewed; the local ledger search is not the launcher's replay.

The role calls for fresh author-independent review before questions are sent. This rehearsal has a local evidence/wording review only, matching the HugeThings draft boundary; no fresh reviewer, pass verdict or token charge was invented. QUESTIONS.md is the requested draft bank for that review, not a protocol-approved sent turn. The first two are clearly marked; no question offers a built capability for removal, asks for an already-readable fact, or treats a guess as his answer. If a reply turns into a choice about actual appearance or movement, show a labelled mock or exploration before binding a visual requirement.

The role's system-item and lessons filing instructions cannot be executed under this explicit no-ledger dry run. Source faults, stale notes and adaptation limits are recorded here without altering anyone's code, queue or rulings.

Local artifact checks cover JSON parsing, unique IDs, inventory enums/fields, real source paths and OWNER tsns, ask-to-inventory references, all mod-file accounting and declared-chain audit coverage. They are not gameplay or launcher acceptance. rg is unavailable on PATH; reads/searches used PowerShell. A PowerShell -Include search unexpectedly included nonmatching files under -LiteralPath; it was stopped and repeated with an explicit Extension filter. The source mirror refreshes externally; MIRROR_HEAD is a recorded reading, not an atomic snapshot.
