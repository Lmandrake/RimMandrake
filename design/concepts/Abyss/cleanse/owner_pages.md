# Page one — what the Abyss would ship

**My proposed Design Version 0.1.0**, under your cleansing delegation. These are my scope calls and interpretations, not new words attributed to you. Nothing changes in the mod until you have read these pages and said so; the supplied review is repaired here, pending its second look.

You settle among obsidian crags where material Dark dims the country and nearby predators, and shortens artificial lamplight. You cultivate living lamps, warm a shelter and roof exposed work while the same Dark settles into corrosive grain that can feed your heaters. When the air clears you can read the country around you; when it closes, the light you tended is your way home.

**Land:** black etched highlands, buildable dark sand, chemical grain, sudden gusts between stillness, brief Unveilings and the existing swirling world face.

**Life:** the current native roster stays, including the campaign Taozin: forage, grazing, predators, timber, fiber, milk, pack animals and actual moth flight. No evictions.

**Signature:** the Dark makes living light and warmth necessary, its light-feeders threaten that refuge, and its fallen grain becomes corrosive wear and recoverable heater fuel.

Your protection/nearby-terror clause remains; Unveiling offers a visual reveal of etched relief. The swift “twist into nightmares” and staying long enough to find their source are deferred with cryptid content. Erosion does not fulfill that dread.

The runner-up was the hidden gravship/probe loop. It needs a separate stealth game; the existing sensor-shadow slowdown and local obscuration already supply protection. The brood expedition is another independent chain. Both move to next version with their existing rulings intact.

**Next version, switched off:**

- Outdoor drifting pockets; nevarithia carried Dark and death release.
- Active ship cover, searching probes, dynamic pursuit/trade isolation.
- Lightfall brood, greed/wake meter, egg theft/return and home storms.
- Great bones, imprinting, beast hunger/killing, lifelong growth.
- Rescue-wreck salvage and ship-restoration fittings.
- Summ regeneration and UV injury.
- Scheduled storm-call Summ arrivals.
- Fold-lamp, observation research and discovery letter.
- Sorter rings, memories, stocked dens and caches.
- Cryptid sites, exchanges, phantom pockets, whispers, tales and dreams.
- Campaign darkness rites and chemistry seep works.
- Missing corpse/disease, low-rest, blade, spine-spray and digging/rage mechanics.
- Globe poison, new spore hazard, turning vines and harvested berry lights.

**Recommend retiring:** gill-ash fuel husbandry duplicates the kept tholin/refinery loop; unused compatibility weather duplicates the active owned weather; biome placement/rareness controls contradict the permanent no-worldgen ruling. Code/defs stay pending your decision. Worldgen is never a future enable option.

Counts: **96 capabilities inventoried; 54 kept; 39 next version; 3 recommended retirements. 8 bars; 3 live-only bars.** There are 15 checks, 11 rules, 7 unknown shared-state meetings, 4 models, 50 tickets and 0 questions. Checks never decide passing.

Before: 76 capabilities in the earlier bounded inventory [measured: `design/RimMandrake/designer_codex_2026-11-09/Abyss/record.json`, inventory length]. This pass separates omitted promises and dependencies. Before: 0 locked bars and 0 locked live-only bars [measured: CASE’s empty old_bars; no concept tree present]. After: the kept scope and proposed bars above. This is a reduction in release scope, not a claim the current build passes.

# Page two — what to check

The important defaults I took:

- “Tide” is opening/closing material air, not a new fluid-wave system; beauty and terror have no equal-event quota.
- Outdoor density follows the shared outdoor temperature; rooms follow room temperature. Clear edges are heated doorways, not spontaneous outdoor pockets.
- Clear shooters cannot aim cleanly through intervening Dark. Losing a murk icon alone proves too little.
- Dark dims terrain, buildings and wild/hostile/visitor creatures, retaining silhouettes; colony pawns stay fully drawn. Nothing is hidden completely; controls and warning text stay readable.
- Unveiling clears all first-version Dark, not unexplored fog or solar geometry. The unbuilt beast halo/release are deferred; the grazer stays.
- Living lamps resist ambient Dark but remain edible to krizzaks. Feeding requires local access, never through a sealed wall.
- Restored light deters an ishvarith; it does not guarantee invulnerability. The quill warning must precede the close attack.
- Light grows crops only with ordinary warmth. Maintained farms do not make a naturally farmable nightside.
- Etchcap requires actual hollow substrate; fertility alone currently admits plain sand.
- Gusts must be real intermittent wind, not cosmetic sound over steady wind.
- Muffling stays shipped on under your existing card; interface sounds and warning text stay usable.
- “Off” suppresses effects and offers, not just placement. Existing toggles leave hunger, research or buildable tools active in several cases.

Models, first to build first:

- **Situations and transitions:** enumerate lifecycle, defaults, reload and alternate action orders using existing kernels.
- **Dark geometry and composition:** sweep warmth, walls, sight paths, lamps, feeders and rendering classes against actual game queries.
- **Wind/weather timing:** replay natural wind, feeding and sound; distinguish real stillness from a detector’s pulse.
- **Whole-map season:** couple food, light, predators, erosion, fuel and ordinary work; calibrate against game histories before trusting predictions.

Remaining measurements: useful-light/path geometry, natural wind/feeding recurrence and season-long food/material recovery. The models decide these; I have not guessed their outputs. Visual readability and sound still need bounded live judgment, with the existing owner-present sound condition. No question asks you to predict those measurements. The supplied review’s objections are addressed; the second look has not judged these repairs.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a contradiction with a standing ruling or the lore (definition.md 'Physical boundaries and transitions'; bars.json R1 and B1; next_version.md 'outdoor drifting pockets'; owner_pages.md page two). The frozen sheet design/Jawa/worldbuilding/biomes/abyss.md §5 'Always true' says: 'The Dark is present, material, and temperature-structured; clear pockets are real, sharp-edged, and unexplained to everyone in-world.' §1 says it 'parts without warning into pockets of impossibly clear air'. The proposal removes every outdoor pocket for 0.1.0. R1 says 'no outdoor microclimate is promised', so clear air exists only inside heated rooms, which a heater explains, or map-wide through Unveiling or a change in the shared outdoor temperature, which is not a pocket. Page two lists this only as a default ('Clear edges are heated doorways, not spontaneous outdoor pockets'). It never says the change breaks an Always-true lore line, and result.json reports questions: 0. Would pass: Either keep sharp-edged, unexplained outdoor clear pockets in 0.1.0 as part of the signature, with a definition and a bar picture, or state on his pages that the lore and the engine conflict. That statement names the §5 line, the engine fact that RimWorld has one outdoor temperature (so 'only a thermometer can tell' cannot hold literally), and the default taken. It is asked as a question carrying that evidence, as brief step 4 and the Evidence-for-Ask rule require. Smallest fix: Add one question to owner_pages.md page two: the §5 'clear pockets are real' line against the single outdoor temperature, the default (no outdoor pockets in 0.1.0, built offset off under T43), and what changes if he says keep them (T43 becomes a signature item and B1 gains an outdoor pocket picture). Set result.json questions to 1.
- a kept mechanic with no definition (census.json row dark_optical_paths (built: absent, fate: signature, ticket T31); bars.json B2 says and R2; tickets.md T31). This kept signature mechanic is unbuilt and only stated in outline. R2 says 'clear endpoints do not bypass intervening Dark'. T31 says 'rays through outdoor Dark remain obstructed'. B2 says 'a clear position cannot grant clean sight'. ambiguities.md leaves the 'sampling algorithm' as an attackable rule. Nothing says what obstruction does to a shot. It could lower hit chance by the density along the path, cap the range, or block targeting entirely. Nothing says whether raiders, turrets and animals are affected the same way as colonists. Nothing says what happens when B1's still-visible dim silhouette can or cannot be ordered attacked. 'Clean' is unmarked, so a token 1% penalty passes B2 as written. Would pass: R2 or definition.md states the form of the effect. For example: accumulated Dark along the line lowers sight and hit chance the way vanilla weather accuracy does; it never removes the target from selection; it applies to every shooter, raiders and turrets included. B2 gains a reject picture that separates a negligible path penalty from real obstruction, without pinning a number. Smallest fix: Add one sentence to R2 naming the effect form and who it applies to, and add one B2 reject picture: 'intervening Dark costs a long shot almost nothing compared with the same shot through clear air'.
- a figurative word unmarked (bars.json B2 says ('A visitor in the Abyss loses usable sight and aim')). B1 says, R2 and definition.md use 'neutral visitors' to mean pawns of other factions, as distinct from colonists. B2 uses 'visitor' for whoever carries murk. The census row 'murk' gives that as every humanlike: 'Humanlike sight/aim/melee hediff follows local Dark'. abyss.md §2 uses 'visitors' to mean outsiders, the colony included. B2's figurative list is empty, so a builder who applies murk only to neutral guest pawns passes B2 by the B1 meaning. Would pass: B2 names its subject literally (a colonist or any other non-native humanlike), or marks 'visitor' as figurative with what it stands for and an accept picture showing a colonist impaired. Smallest fix: Change B2 says to 'A colonist or other non-native pawn in the Abyss loses…', or add {word: 'visitor', stands_for: 'every non-native humanlike, colonists included'} to B2 meant.figurative.
- evidence that cannot tell success from a plausible false pass (bars.json B3 sees.control and sees.start). B3 says native food, grazing, timber and fiber plants 'persist without real sky light'. The control lists only 'Fertility, artificial sunlamps or inventory injections' and 'remove other glowers'. It never records or excludes sky glow. No Abyss source touches sky glow (searched [measured]: only RM_CompSummHide reads skyManager.CurSkyGlow, and it expects it to reach 0.5 'under bright open sky'). B1's range assumes 'day/night palette slots for the same fixed solar geometry'. So on any map whose solar geometry gives daytime sky glow, a native plant kept alive by daylight passes the 'persist without real sky light' reading. Abyss sheet §6 ban 6 ('No sun-dependent resident life') is exactly that false pass. Would pass: The B3 instrument records the sky-glow contribution at every sampled plant and plot. Persistence and establishment are read with sky glow attributed or excluded, for example night-phase readings or growth eligibility traced to glow source, so daylight cannot stand in for living light. Smallest fix: Add to B3 sees.control: 'record sky/sun glow at each sample; a native plant counts as persisting without sky light only where its growth eligibility holds with the sky contribution removed'.
- a sourced core promise omitted or weakened (owner_pages.md line 13; definition.md 'Why a player reaches for it'; bars.json B1 and B8 meant). His 2026-10-20 experience (design/RimMandrake/biome_experiences_2026-10-20.md): 'Wonders emerge just as often for moments of transcendent beauty, only to twist into nightmares just as swiftly.' The proposal defers 'the swift twist into nightmares' 'with cryptid content'. Yet the kept mechanics already make that turn. Unveiling (the wonder, B1) ends, the Dark returns (R1), lamps shrink (R3), krizzaks feed (B4) and the ishvarith closes in as light fails (B4). That is a 'terror close by' with no cryptid system. No bar or picture asks for that sequence, so a build where Unveiling's end changes nothing nearby passes every bar. The clause is dropped without an argument that the kept mechanics cannot carry it. Would pass: An accept picture in B8 or B1 in which Unveiling's close readably brings nearby danger back to the colony's edge through the kept Dark, light and predator chain, with a reject picture where the clearing ends and nothing nearby changes. Alternatively, an argument with evidence for why the kept chain cannot carry the clause. Smallest fix: Add one accept and one reject picture to B8 (no new system), and narrow the page-one deferral to the source-of-nightmares dread only.
