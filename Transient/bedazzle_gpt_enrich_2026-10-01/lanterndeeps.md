**Verbs:** Demonstrate · Hoist · Baffle · Contract · Miswire — checked: none repeat.  
**Systems:** Production pedagogy · cross-map gravship logistics · acoustic map weather/room topology · persistent giant diplomacy/AI · Ideology ritual/maintenance — checked: none repeat.

## 1. Ithrix, the Bench That Remembers

- **Marks it serves:** 2 — discoverable technology.
- **The player's experience:** Exploring a mindstone gallery reveals stress-lines resembling a craftsperson’s hand movements and unlocks Ithrix tracework. At an RM_Ithrix bench, a skilled colonist demonstrates one chosen recipe while an assistant tunes a lanternstone plate. That bench can thereafter lend lesser workers a degraded version of the recorded skill for that recipe until the plate cleaves. The emotional beat is legacy: a dead specialist can leave behind one precious, imperfect lesson.
- **How it works in RimWorld 1.6:** `ResearchProjectDef`, `ThingDef`, `RecipeDef`, `JobDef`, `SoundDef`, and `CompProperties_IthrixTrace`. `CompIthrixTrace` saves teacher, recipe, demonstrated quality, uses and fracture state; the main Harmony hook is `WorkGiver_DoBill.JobOnThing`, with `GenRecipe.MakeRecipeProducts` enforcing a skill floor of teacher-minus-N and a quality ceiling below the demonstration. It reads pawn skill, recipe, illumination and plate condition; it writes one bench-bound recipe signature—never pawn memories or a new hediff. Settings: enable, recording cost, skill loss, quality cap and plate lifespan.
- **Readable signs:** The plate visibly gains branching blue lines, repeats the teacher’s tool rhythm in sound, displays its recipe and remaining impressions, and gives several cracking warnings before failure.
- **Drawn from:** [Caves of Qud’s Tinkering](https://wiki.cavesofqud.com/wiki/Tinkering), where data disks teach fixed schematics, and [Dwarf Fortress strange moods](https://dwarffortresswiki.org/index.php/Strange_mood), where one dwarf commandeers a workshop to make an artifact. Ithrix instead records a voluntary physical demonstration into one degradable living workstation; it grants neither a universal schematic nor an autonomous artifact.
- **Why it is unique here:** Unlike Contagion’s draftprints/bodyprints, Ithrix transmits one learned work gesture through piezoelectric crystal rather than copying bodies or converting a field.
- **Tier:** Free, `RM_`; it uses lanternstone alone and is a complete non-kyber technology.
- **Size:** M.

## 2. The Veyrline Keel Hoist

- **Marks it serves:** 6 — gravship touch.
- **The player's experience:** A gravship parked over a Deeps mouth can mount an upper Veyrline clamp while the colony builds a capstan below. The ship’s gravfield unloads the cable while an actual powered winch hauls sealed cargo cages through the existing shaft; it does not make them fly. This permits extraction of mining rigs, dead droid chassis and oversized power cells that ordinary carriers cannot negotiate through the mouth. The beat is hard-earned logistical relief, balanced by immobilizing the gravship while its keel is physically tethered.
- **How it works in RimWorld 1.6:** Paired `ThingDef`s, `JobDef`, `ResearchProjectDef`, `FleckDef` and `SoundDef`, plus `CompVeyrlineEndpoint` and a `WorldComponent` keyed to the two persistent map IDs. The main hook is `CompVeyrlineEndpoint.CompTick`; a Harmony prefix on `Building_GravEngine.TryLaunch` refuses takeoff until the line is reeled in. Cargo sits inside a serialized `ThingOwner` associated with a spawned cage marker at both endpoints; pawns and animals are forbidden cargo. Settings: enable, mass ceiling, transit time, power draw and breakdown frequency.
- **Readable signs:** A taut animated cable enters the mouth, shaft markers report exact depth, the cage remains selectable throughout transit, and jams produce grinding audio, a map letter and a recoverable cage position.
- **Drawn from:** [Oxygen Not Included’s Interplanetary Launcher](https://oxygennotincluded.wiki.gg/wiki/Interplanetary_Launcher), which packages resources into launched payloads, and Anomaly’s [pit gate](https://rimworldwiki.com/wiki/Pit_gate), which connects distinct maps through an expedition entrance. Veyrline is a persistent, mass-limited two-ended machine whose cargo remains physically accounted for and whose tether changes gravship readiness.
- **Why it is unique here:** The seas’ signature is taking the gravship itself to the sea floor; Veyrline keeps the ship aboveground and brings only winched material through a fixed throat.
- **Tier:** Free, `RM_`; no campaign material or lore is required.
- **Size:** M.

## 3. Nhal, the Standing Note

- **Marks it serves:** 8 — weather under the mountain.
- **The player's experience:** A Nhal condition begins with dust levitating into crisp bands and the ambient chorus resolving into one sustained note. Room shape, open doors and rotatable acoustic baffles determine quiet nodes and violent antinodes. Lanternstone accretes rapidly at antinodes but is dangerously easy to shatter there, while mining at a node is slow and controlled. The beat is tense spatial mastery: players remodel sound paths rather than waiting out a timer.
- **How it works in RimWorld 1.6:** `GameConditionDef` rather than sky-facing `WeatherDef`, plus `ThingDef` baffles, `SoundDef`, `FleckDef` and an overlay `DesignationCategoryDef`. A `MapComponent_NhalField.MapComponentTick` flood-fills room portals and combines distance phases from existing resonant masses; spawning, rotating or removing a baffle dirties the field. `Plant.GrowthRate` and `Mineable.TrySpawnYield` patches read the cell amplitude and modify only crystalline growth and existing lanternstone fracture odds. Settings: enable, duration, warning period, wavelength, growth multiplier and volatility.
- **Readable signs:** Vibrating grit draws the nodes on the floor even without the overlay; baffles visibly quiver, the hum beats near antinodes, and mineables show “stable” or “loaded” inspection text.
- **Drawn from:** [Oxygen Not Included’s Room Overlay](https://oxygennotincluded.wiki.gg/wiki/Room_Overlay), which makes enclosure geometry legible, and [The Long Dark’s Aurora](https://thelongdark.fandom.com/wiki/Aurora), which temporarily alters otherwise inert systems. Nhal computes live interference from architecture and player-placed baffles; it neither merely classifies rooms nor switches electronics on.
- **Why it is unique here:** Although Rust Cathedral owns a behaviour-answering hum, Cauldron owns phased weather and Stillsand owns listening for predators, Nhal is a spatial acoustic engineering puzzle governing crystal accretion and cleavage.
- **Tier:** Free, `RM_`; it expresses native crystal physics without campaign theology.
- **Size:** M.

## 4. Orun-Ghal, Last Shiftboss

- **Marks it serves:** 5 — the giant.
- **The player's experience:** A five-cell-wide mining exoframe rises, visibly carrying its dead operator, and walks toward the nearest Lantern colony. The Shard-Mind wearing it offers maintenance contracts through the suit’s cracked work terminal rather than attacking. Repairing one displayed system earns a mining warrant: the player paints one route, previews every affected cell, and Orun-Ghal cuts a broad tunnel—including special ancient stope faces—before returning to kneel beside the Lantern. The beat moves from giant-monster dread to uneasy compassion and cooperation.
- **How it works in RimWorld 1.6:** A unique `PawnKindDef`, mechanical race `ThingDef`, `BodyDef`, `JobDef`s, `DesignationDef` and linked hitbox `ThingDef`s. `CompGiantFootprint` reserves the full footprint; the main hook on `Pawn_PathFollower.TryEnterNextPathCell` validates the swept area and moves visible body sections together. `CompWorkCovenant` reads repairs and the painted permit, then writes a persistent trust/warrant ledger. Settings: enable, footprint, repair costs, mining width, work speed and hostility response.
- **Readable signs:** Each footfall shakes dust, its entire proposed route is outlined before confirmation, damaged limbs remain on-map, and disabling it leaves a salvageable giant wreck and operator’s nameplate.
- **Drawn from:** [Dwarf Fortress forgotten beasts](https://dwarffortresswiki.org/index.php/Forgotten_beast), subterranean megafauna with spectacular destructive bodies; [Kenshi leviathans](https://kenshi.fandom.com/wiki/Leviathan), immense nonhuman presences; and [VFE Mechanoids](https://steamcommunity.com/sharedfiles/filedetails/?id=2329011599), with mechanized industrial production. Orun-Ghal is instead one persistent, named, contractable multi-cell worker whose route the player negotiates.
- **Why it is unique here:** Unlike Forge’s giant-on-the-clock and the other biomes’ animal or plant giants, Orun-Ghal has no schedule or boss cycle—it is the well-provisioned dead turned into a spatial labor relationship.
- **Tier:** Free, `RM_`; Orun-Ghal is an invented, biome-exclusive entity with no franchise dependency.
- **Size:** L.

## 5. Zizzik’s Nine Faults

- **Marks it serves:** 9 and 2 — a taught Salvation rite and its research row.
- **The player's experience:** Nine repeated fracture marks in a gallery unlock research that Salvation interprets as Zizzik’s Nine Faults. Anywhere on the planet, worshippers surround one healthy, powered machine and deliberately miswire it until it suffers a controlled breakdown. Ritual quality grants a few “vented faults”: later natural breakdowns in that settlement are redirected into the consecrated machine, damaging it and consuming the charges while the original devices keep running. The beat is mischievous catharsis—choosing where inevitable malfunction is allowed to live.
- **How it works in RimWorld 1.6:** `ResearchProjectDef`, dormant `PreceptDef`, `RitualPatternDef`, `RitualOutcomeEffectDef`, `ThingDef` fault-board and `ThoughtDef`. `RitualOutcomeEffectWorker.Apply` records the vessel and charges in a `MapComponent_FaultLedger`; a Harmony prefix on `CompBreakdownable.DoBreakdown` redirects eligible faults and applies damage to the visible vessel. It reads ritual quality, machine value and settlement map; it writes no pawn hediff. Settings: enable, minimum vessel value, charge range, redirected-damage multiplier and eligible machine categories.
- **Readable signs:** Nine bulbs fail in sequence during the rite; afterward the vessel displays remaining faults, spits a visible arc whenever it absorbs one, and generates a letter when destroyed or exhausted.
- **Drawn from:** Ideology’s [ritual quality and outcome system](https://rimworldwiki.com/wiki/Rituals) and Against the Storm’s [Blightrot](https://against-the-storm.fandom.com/wiki/Blightrot), where industrial benefit creates corruption later burned by specialists. This rite redirects future random maintenance failures into a chosen sacrificial object instead of cleaning periodic industrial pollution.
- **Why it is unique here:** Unlike the Abyss’s darkness-gated rites or Nightside Ice’s Cold Ledger exchange, this fully lit rite vents Zizzik through settlement machinery and is gated only by learned inscription and a working machine.
- **Tier:** Campaign, `RUT_`; it explicitly belongs to the Jawa Salvation and its jealous god Zizzik.
- **Size:** M.

**1st — #1 Ithrix:** strongest Mark 2 answer, tightly scoped, immediately useful, and makes lanternstone culturally distinctive.  
**2nd — #3 Nhal:** turns the biome’s existing hum, rooms and volatile crystal into a replayable layout problem without adding creatures or another temperature system.  
**Order rationale:** together they establish the Deeps’ core promise—living light can remember skilled hands, while living stone makes architecture sing.