**Verbs — checked, no repeats:** tune; bargain; ballast; compare; reconcile.  
**Systems — checked, no repeats:** audio/recreation; living-terrain morphology; gravship cargo/stress; research/reverse-engineering; Ideology/faction obligations.

## 1. The Kharu Breath-Choir

- **Marks it serves:** 7, plus the heat law.
- **The player's experience:** Mining exposes sealed, air-filled bores squeezed by the creeping ice. Colonists install stops along them, then tune the notes by opening particular chambers and routing ordinary heated air through the gallery; the exterior remains utterly windless. A consonant choir provides recreation and a small sleep bonus, but sustaining it raises the existing heat dial. The emotional beat is dangerous wonder: making this dead place sing means announcing yourself to it.
- **How it works in RimWorld 1.6:** `ThingDef` resonators and stops, `JobDef` tuning, `SoundDef` loops, `ThoughtDef`, and `CompProperties_Resonator`. `MapComponentTick` reads connected bore length, stop states, room temperatures, and airflow through doors/vents; it writes pitch layers, recreation gain, and tuning quality. All transferred heat remains vanilla temperature and therefore feeds the existing breach system. Settings: enable toggle, choir volume, mood strength, tuning difficulty, and heat-dial multiplier.
- **Readable signs:** Audible individual pipes before the chord forms, frost dust pulsing from each stop, inspectable note/pressure values, and red heat-ledger contribution. Cracking makes a pipe visibly and audibly fall out of tune rather than silently failing.
- **Drawn from:** [Dwarf Fortress’s generated, multi-part musical instruments](https://dwarffortresswiki.org/index.php/Musical_instrument), [Oxygen Not Included’s temperature-driven automation sensors](https://oxygennotincluded.wiki.gg/wiki/Thermo_Sensor), and [Dubs Bad Hygiene’s central-heating networks](https://steamcommunity.com/sharedfiles/filedetails/?id=836308268). None turns a colony’s real heat transport into a spatial instrument whose performance carries ecological risk.
- **Why it is unique here:** Unlike Stillsand’s Listening/geophone or Forge’s four voices, the Choir detects nothing and predicts nothing—it is a deliberately played, thermally expensive cultural instrument.
- **Tier:** Free (`RM_`); Kharu is invented and the complete music/heat bargain needs no campaign lore.
- **Size:** M.

## 2. Vhal, the Ridge That Bargains

- **Marks it serves:** 5.
- **The player's experience:** Three catalyst mouths reveal that an entire ridge is one Vhal organism, with a finite, inspectable chemical reserve. The player offers specified minerals at one mouth and lays a directional pattern of warm and cold cells around another; Vhal may spend centuries of savings to retract one empty lane and extrude a defensive ridge elsewhere. It will not move into occupied cells, and repeated requests become progressively dearer. The emotional beat is uneasy reciprocity: the landscape understands the offer but never becomes tame.
- **How it works in RimWorld 1.6:** `ThingDef` ridge plates, mouths, and catalyst sockets; `TerrainDef` heaved/receded ice; `JobDef` tending; and `MapComponent_VhalBody`. Its `MapComponentTick` reads connected plates, deposited resources, and vanilla cell temperatures—never a new cold resource—and writes queued terrain conversions plus reserve and familiarity values. Growth pauses if a pawn, building, item, or hull occupies the previewed cells. Settings: feature toggle, starting reserve, cells moved per season, price escalation, and minimum temperature contrast.
- **Readable signs:** A planning overlay shows every proposed cell; dark chemical veins fill toward the destination over several hours; deep knocks count down each movement. Rejected bargains return the offering and leave a permanent white scar explaining why.
- **Drawn from:** [Anomaly’s Fleshmass Heart and connected infestation](https://rimworldwiki.com/wiki/Fleshmass_heart) and [Timberborn’s constructed terrain blocks](https://timberborn.wiki.gg/wiki/Terrain_Block). Vhal is neither hostile map-spread nor inert terraforming: it is a bounded organism performing a paid, negotiated morphological act.
- **Why it is unique here:** Unlike Forge’s clock-bound giant, Greentide’s greatbole, or Fever Wood’s six-limbed elder, Vhal is map topology with agency—not a boss, harvest node, or encounter pawn.
- **Tier:** Free (`RM_`); Vhal is invented, biome-locked, and mechanically complete.
- **Size:** L.

## 3. The Keel-Press

- **Marks it serves:** 6, plus calving and perfect preservation.
- **The player's experience:** A landed gravship can deploy four press gauges around its real hull footprint. The player ballasts its quadrants by hauling cargo, water-ice, or machinery aboard; the changing centre of mass selects which arc of deep ice is loaded. Hold an imbalance long enough and a visible stress fan calves up a narrow seam of preserved wreckage—but the powered ship remains the hemisphere’s brightest thermal target throughout. The emotional beat is industrial audacity under siege.
- **How it works in RimWorld 1.6:** A ship-compatible `ThingDef`/`CompProperties_KeelPress`, `IncidentDef` calving result, `ThingSetMakerDef` inclusions, and `MapComponent_KeelStress`. The component reads the actual landed Odyssey hull cells, `StatDefOf.Mass` of onboard things, grav-engine state, and the existing heat dial; it writes quadrant stress, crack overlays, and a chosen calving arc. A Harmony postfix on the 1.6 gravship landing/launch transition starts or cancels the press; no simulated hovering or fake flight occurs. Settings: toggle, press time, yield, crack radius, threat multiplier, and cargo-mass sensitivity.
- **Readable signs:** Four gauges, a centre-of-mass reticle, groaning that pans toward the loaded arc, widening cracks, and a countdown letter. If launched early, stress visibly relaxes over hours; nothing or nobody disappears.
- **Drawn from:** [Odyssey’s customizable travelling gravship](https://rimworldgame.com/odyssey/), [Dwarf Fortress’s controllable cave-ins](https://dwarffortresswiki.org/index.php/Cave-in), and [Below Zero’s modular Seatruck](https://subnautica.wiki.gg/wiki/Seatruck). Those supply mobile-base configuration and load-induced terrain failure, but not cargo placement as a directional archaeological press.
- **Why it is unique here:** Unlike the Abyss’s hidden ship, Stillsand’s ship-taking dunes, Blue Desert’s heat sink, or the seas’ gravship dive, the craft stays visible and grounded while its mass—not stored cold—exhumes one selected arc.
- **Tier:** Free (`RM_`); it is a full gravship activity without franchise content.
- **Size:** L.

## 4. The Sevren Witness Method

- **Marks it serves:** 2, plus perfect preservation and calving.
- **The player's experience:** Calving can return pristine Sevren witnesses: manufactured objects tagged by function and historical era. At a comparison frame, the player places two ancient versions of one mechanism beside a colony-made example, then assigns an intellectual pawn to identify what changed and what did not. The first valid trio reveals a hidden research row; mastering it makes comparative reverse-engineering available on any later map. The emotional beat is revelation: the ice preserved technological evolution itself, not merely loot.
- **How it works in RimWorld 1.6:** `ThingDef` witnesses with `CompProperties_EraWitness`, `ThingCategoryDef` principle tags, `ResearchProjectDef RM_SevrenMethod`, `RecipeDef` comparison proofs, and a dedicated `JobDriver`. Completion reads matching function tags, distinct eras, quality, and researcher skill; it writes bounded progress to one associated unfinished `ResearchProjectDef` and records used lineages in a save-persistent `GameComponent`. Settings: toggle, samples required, insight percentage, failure damage, and per-project cap.
- **Readable signs:** Every witness lists era, principle, eligible partners, provenance, and prior use. The comparison table displays the target project and exact insight before commitment; failure cracks but does not erase a sample.
- **Drawn from:** [Caves of Qud’s Tinkering and recipe-bearing data disks](https://wiki.cavesofqud.com/wiki/Tinkering), [Royalty’s project-specific techprints](https://rimworldwiki.com/wiki/Techprint), and [VFE Ancients’ vault recovery](https://steamcommunity.com/sharedfiles/filedetails/?id=2654846754). Those grant recipes or recovered advantages; Sevren requires a three-object historical proof and teaches a reusable research practice.
- **Why it is unique here:** Unlike Cracked Lands’ read-the-land survey, this reads preserved manufacturing lineages and permanently changes how the colony learns.
- **Tier:** Free (`RM_`); Sevren is invented, and the archaeology loop stands alone.
- **Size:** M.

## 5. Mob’Unloo’s Ninth Account

- **Marks it serves:** 9, emphasizing under-served Mob’Unloo.
- **The player's experience:** Some calved dead carry an explicit ledger tablet naming what they owed, to whom, and why death did not close the account. A believer may loot and disclaim it, leave it unresolved, or inherit the debt as a concrete quest: deliver equivalent goods, repair an inherited machine, ransom someone, or aid the creditor faction. Completion closes both entries and turns an anonymous frozen corpse into remembered history. The emotional beat is guilt becoming chosen responsibility, not divine punishment.
- **How it works in RimWorld 1.6:** `PreceptDef RUT_MobUnlooDebt`, tablet `ThingDef` with `CompDebtRecord`, `QuestScriptDef` obligation families, `HistoryEventDef`, `ThoughtDef`, and a ledger `GameComponent`. The calving-spawn hook reads the corpse’s name, faction, skills, relations, and grave goods; accepting writes a visible quest and named account, while completion writes goodwill, belief memories, and a closed-ledger history event. Settings: toggle, occurrence chance, value range, deadlines, allowed obligation families, and goodwill scale.
- **Readable signs:** Physical tablet, corpse inscription, ledger tab, creditor letter, carried tally token, map-visible destination, and explicit consequences before acceptance. The corpse remains until handled normally.
- **Drawn from:** [Ideology’s belief-driven social consequences](https://rimworldgame.com/ideology/) and [Against the Storm’s optional Orders with stated objectives and rewards](https://hoodedhorse.com/wiki/Against_the_Storm/Orders). Neither generates an inheritable obligation from a specific dead person’s procedural biography.
- **Why it is unique here:** Unlike the Abyss’s offerings or Wasteland’s Rite of Tipping, this is a persistent named social debt spanning factions and maps, not a sacrifice or weather rite.
- **Tier:** Campaign (`RUT_`), because Mob’Unloo and Jawa Salvation belong exclusively there.
- **Size:** M.

**1st — #4, Sevren Witness Method:** it converts perfect preservation into the biome’s clearest discoverable technology and has strong value after departure.  
**2nd — #1, Kharu Breath-Choir:** it gives the dead-still interior an instantly recognizable sound identity while deepening the existing heat law.  
**Why these two:** together they establish intellectual discovery and dangerous beauty before committing to the larger ridge and gravship frameworks.