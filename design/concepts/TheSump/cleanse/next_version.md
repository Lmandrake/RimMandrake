# Next version, switched off

Designer decisions for Design Version 0.1.0. These preserve future lore and owner rulings; they do not activate anything. All built entries name a default-off consumer/producer ticket. Recommended retirements await the owner; prohibited worldgen never gets an on switch.

### placement worker — recommended retirement
What: Existing tile-score worker and rarity slider for alternative-world generation; retained as built evidence, outside the campaign/player promise.
Why: Designer decision (delegated): Recommend retiring active biome scoring and the rarity UI because producing alternative planets contradicts the standing no-worldgen ruling. Hard-disabled in every version, never placed on a next-version wishlist; retain inert type only if load compatibility requires it.
Ticket: T1

### retired mutator ports — recommended retirement
What: Authored RM_TarLakes TileMutatorDef and LandmarkDef, with tar patches; these are compatibility content, not authority to generate a new planet.
Why: Designer decision (delegated): Recommend retiring active tar-lake world placement/landmark hooks for the same no-worldgen reason. Saved identifiers may remain inert; nothing here authorizes changing the fixed planet.
Ticket: T2

### poured moat
What: Buildable slow tar floor, Chemfuel cost placeholder, burned spent terrain and ability to re-pour.
Why: Designer decision (delegated): A buildable defence perimeter is a separate military system; natural tar and ordinary fire already make land and signature whole.
Ticket: T3

### fuse post
What: Player ignition queues connected poured/natural tar terrain and starts vanilla Fire at a staggered rate; not the same mechanism as the gate-aware liquid front.
Why: Designer decision (delegated): Command ignition is a military action, not required to cross, work or clean natural tar.
Ticket: T4

### legacy burn support
What: TimedTerrainBurn and smoke-column support were built for the old TarBlaze. TheSump has no TarBlaze def/consumer now; code presence does not make a smoke wall.
Why: Designer decision (delegated): A bespoke smoke wall consumer is not necessary for ordinary ground; shared support remains owned by EnvironmentalHazards.
Ticket: T5

### belch flood
What: Tar-pit incident selects tar epicentre, releases a real tar flood and letter; FlowWorks owns spread and cooled front, TheSump redirects cooling to Glasswalk.
Why: Designer decision (delegated): A special incident rewrites familiar routes independently of ordinary exposure. The colony loop works without a scripted flood.
Ticket: T6

### duckboards — recommended retirement
What: Cheap fast clean wood floor, flammable and slow when tar filth accumulates; Brindeth no longer yields WoodLog despite old comments.
Why: Designer decision (delegated): Recommend retiring the separate duckboard buildable: vanilla wood flooring already supplies its fast-when-clean, foulable, flammable route behaviour. Until the owner decides, park it switched off as next-version content; preserve its ruled behaviour if restored.
Ticket: T7

### glasswalk slips
What: Shared slippery-walkway watcher applies damage-free stun to moving/hauling pawns, with toggle and chance.
Why: Designer decision (delegated): Random harmless falls add an independent interruption beyond the permanent route travel cost; deletion leaves the route tradeoff readable.
Ticket: T8

### vault seal
What: Normal-ticking shelf scans held things, disables rot, forbids items and scribes its seal ledger.
Why: Designer decision (delegated): Perfect preservation is a storage system beyond route/exposure/recovery; ordinary shelves and refrigerators cover current food storage.
Ticket: T9

### vault extract
What: Menu consumes one weak/strong solvent per stack administratively from anywhere on map, unseals original in place; no solvent destroys/replaces it with ruined goods.
Why: Designer decision (delegated): Solvent-gated release/ruined goods belongs to the deferred preservation system; basic cleaning must not call it.
Ticket: T10

### kethrel shell
What: Real ThingOwner shell with mass thresholds, armour/speed hediff stages, whole-body directional graphics, saved contents and inspect tab.
Why: Designer decision (delegated): Wearable stolen scrap creates an equipment ecology beyond ordinary animals; the seated kethrel remains a plain animal.
Ticket: T11

### kethrel pickup
What: Rare-tick searches weapons/listed scrap near tar, respects forbidden/value/home-area checks and sends an idle animal toward reachable distant scrap; close pickup has no reach/LOS check.
Why: Designer decision (delegated): Scrap seeking/ownership transfer is the producer of that deferred shell system, not a need for ordinary fauna.
Ticket: T12

### kethrel molt
What: Automatic loaded molt, player coax command with best able Animals colonist/charge chance, and death/despawn release of carried items.
Why: Designer decision (delegated): Automatic/coaxed molt and handling charge exist only to release shell contents. Safe release for old saves is compatibility, not permission to run the extra.
Ticket: T13

### capstan combat
What: Powered host, turning top and shared tether pull for visible enemies, one-cell reel, mass/size/struggle snap, damage and line cues.
Why: Designer decision (delegated): A powered tether weapon is a separate combat mechanic. Deleting its player behaviour does not remove tar resistance.
Ticket: T14

### capstan rescue
What: With no enemy, shared tether can acquire downed colonists and pull them toward the powered turret.
Why: Designer decision (delegated): Automatic friendly towing adds a rescue system; vanilla carrying already serves ordinary casualties.
Ticket: T15

### drawjoint learning
What: Deep strata yield preserved draw-joints; study two consumes them and unlocks capstan research, plus shared analyzable grants traction-lance research; ordinary and pit-rigged material variants.
Why: Designer decision (delegated): Artifact-driven research is a second progression loop, and removing it cannot gate retained bitumen, solvent or routes.
Ticket: T16

### salvage winch
What: Ordered unpowered hook drags wrecks, corpses and downed beasts along ground; refuses standing/too-heavy targets and cannot lift; own research after capstan.
Why: Designer decision (delegated): Ground towing is a separate salvage interaction owned by the shared tether engine; ordinary hauling suffices for current goods.
Ticket: T17

### dig lottery
What: Manual Mining work, progress/depth persistence, four weighted strata, increasing trap weight and deep-dig wake signal; most loot is vanilla salvage placeholders plus real draw-joints.
Why: Designer decision (delegated): Excavation with strata/treasure is the runner-up signature; it loses to the owner experience sentence about ordinary resistance.
Ticket: T18

### dig disarm
What: Fuse countdown, deterministic Mining threshold and failure detonation; automatic disarm WorkGiver does not prefilter skill. Weight/whole-body-remains ConfigErrors are built.
Why: Designer decision (delegated): Timed traps and qualified disarm only exist to support deferred excavation.
Ticket: T19

### beast dormancy
What: Deep-tar set-piece places bulge; stock damage/construction wake, lottery relay and working deep-drill proximity emerge actual tar beast.
Why: Designer decision (delegated): Hidden wake causes launch the deferred catastrophe system, not ordinary wildlife or land.
Ticket: T20

### beast station eater
What: Body size 9, slow pace, reachable dense-building selection, timed crushing bites, filth trail, stagger nearby pawns, mound/letter, satiation/timer and sink to new deep-tar bulge.
Why: Designer decision (delegated): A station-eating evacuation event is an additional system; no roster entry is evicted because this is a caused set-piece.
Ticket: T21

### solvent weapon
What: Ordered solvent haul/pour, explicit danger confirmation, hiss/splash, pending wake record, permanent manhunter attempt/retry and letter; optional Ninefold deltas.
Why: Designer decision (delegated): Deliberately waking a manhunter is a weapon, not necessary for solvent cleaning. Keep solvent itself.
Ticket: T22

### mouse tracks
What: Tameable mouse opts into dread-avoiding wander destinations and deposits tracks on shallow tar; bulge/awake beast register dread.
Why: Designer decision (delegated): Tracks and dread avoidance are a route-information system tied to hidden dangers. The mouse keeps ordinary movement and taming without those claims.
Ticket: T23

### gaslight chemistry
What: Bitumen plus weak solvent crafts stackable tar gas at machining bench behind research; own resource, not a Helixien pipe-network implementation.
Why: Designer decision (delegated): Collectable gas and its research/fuel production add a separate industry. Keep solvent recovery without bottled gas.
Ticket: T24

### warbling lamp
What: Fueled/flickable lamp, warm hue/radius pulses and room-beauty reward via shared warbling-glow comp.
Why: Designer decision (delegated): A bespoke pulse/beauty/fuel lamp is not necessary for dusk to be readable; ordinary lamps supply light.
Ticket: T25

### living map
What: Shared hourly diff queues soffeth rings, delays mouse dread on fresh RM_TarGlass and migrates mirrelin; settings and saved responder queues exist.
Why: Designer decision (delegated): Delayed plant rings and fresh-crust mouse reroutes add changing ecological clues. Static habitat and normal growth remain whole without this queue.
Ticket: T26

### tar sealed food
What: Optional ColdStorage vat and bills seal meat/fish/eggs/produce with bitumen; 30-day pitch aging, bad-cook ruin chance, sealing failures and preserved-taste data; independent of shelf vault.
Why: Designer decision (delegated): Food sealing, cooking failure and pitch aging duplicate a preservation progression beyond the chosen signature.
Ticket: T27

### acoustic payload
What: Optional AcousticScanner patch identifies dormant bulge, still hunter, brood and hidden caves, with Sump-specific readings.
Why: Designer decision (delegated): Scanner-specific hidden readings are an optional instrument for deferred hazards, not the player warning retained tar exposure needs.
Ticket: T28

### arrival letter — recommended retirement
What: Biome extension gives first-arrival surface-reading advice; Utinni patch supplies campaign voice.
Why: Designer decision (delegated): Recommend retiring this arrival letter: it teaches absent mouse/crust/gas tells and ordinary inspect text can teach the retained tar cost. Until decided, keep the letter gated off, with corrected text before any opt-in.
Ticket: T29

### false floor behaviour
What: Pallick body is built; false-floor collapse and mouse avoidance specifically over pallick are absent in inspected src.
Why: Designer decision (delegated): Pallick collapse is a separate hidden trap. Keep its roster body as harmless crust cover with honest text until this opts in.
Ticket: T30

### species ecology
What: Custom thrummel mound/guard radius/queen ends hive; dredgel dig-attraction; moving skarrid dread are not wired onto current native bodies.
Why: Designer decision (delegated): Mounds, guarded radii, dig attraction and moving dread are bespoke ecosystems beyond ordinary diets/combat/products.
Ticket: T31

### indicator placement
What: Initial soffeth gas-seep and tolleth rich-find placement, reliably cooled-ground-only mirrelin/pallick and margin-only flora are not implemented by these plant defs.
Why: Designer decision (delegated): Gas/treasure/false-floor indication needs deferred underlying states. Ordinary tar-margin, pool and glass habitats are a separate kept requirement.
Ticket: T32

### prewake warning
What: Ordinary disturbance's day-ahead room-sized bubble/ring warning not located; instant solvent weapon is deliberately separate.
Why: Designer decision (delegated): The warning is indispensable WHEN the beast returns, but no beast runs in this version. Preserve day-ahead warning and evacuation constraints then.
Ticket: T33

### natural flame discovery
What: Natural seep flames plus first-flame/geyser encounter discovery and first-tar technology trigger not located; current gaslight/rendering are ordinary research rows.
Why: Designer decision (delegated): Discovery-triggered technology and seep flames are a progression system. Existing manual research covers retained rendering.
Ticket: T34

### special archive finds
What: Lore-specific bones/hides/casings and live ancient-machine/Assailant dig-wake outcomes not authored in current Sump lottery; existing draw-joint is real.
Why: Designer decision (delegated): Ancient finds and exceptional live excavation outcomes belong to the deferred archive system, with partial-remains bans intact.
Ticket: T35

### moat wall integration
What: Current actual fuse-post path has no TarBlaze consumer establishing promised impassable long-burning smoke wall and column.
Why: Designer decision (delegated): Impassable long-burning smoke wall belongs to the deferred military moat; support code alone is not its implementation.
Ticket: T36

### tar rain removed — recommended retirement
What: Sump precipitation/tar-rain feature removed by later owner card; not future work.
Why: Designer decision (delegated): Already removed by the recorded later no-precipitation card, not a new retirement decision or a future candidate. Maintain exclusion.
Ticket: none; already removed historical content, no current producer found.

### wick and brommet removed — recommended retirement
What: Historical built wick crop/stem and brommet/wool are absent from current Sump bodies/products; biome comments record owner sheet cuts. They must not demand showcase scenes.
Why: Designer decision (delegated): Already cut on the owner sheet per current biome comments; no new eviction or renewed question. Maintain exclusion and preserve the evidence row.
Ticket: none; already removed historical content, no current producer found.

### nine rites v2
What: The Sinking and Mob'Unloo effigy rite are deferred outside v1 by explicit owner retarget; no current Sump effect implementation found.
Why: Designer decision (delegated): The Sinking and effigy rite were already moved by the owner. This is an acknowledgement, never a renewed request or waiver.
Ticket: T37

### inhabited future
What: Campaign faction weighting, expedition ruins, attempted refineries and moisture farmers belong to the Inhabited pass; no installed Sump-specific injection chain verified.
Why: Designer decision (delegated): Junker ruins, refinery attempts and faction injections are campaign inhabited content, not ordinary ground/life/tar maintenance.
Ticket: T38

### titan passage neighbour
What: Ledger-only native/visiting giant question exists; dormant tar beast set-piece is not automatically a HugeThings passage candidate.
Why: Designer decision (delegated): A visiting giant is additional encounter content. Existing HugeThings behaviour is not redesigned or inferred from the tar beast.
Ticket: T39

### gas byproduct
What: Collectable gas emitted by successful pawn scrubbing
Why: Designer decision (delegated): Collectable fuel is deferred industry; recovery must finish without granting or loading a lamp.
Ticket: T42
