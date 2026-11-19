# Page one — what the mod now is

Visit alien sea floors by gravship: the Scald boils, the Grey grows salt, the Chill holds dark fuel, and the Twilight shelters gardens beneath living glass. Their native plants, prey and predators belong to those liquids, and the fish caught at the beach have living counterparts below. In the Twilight, harvestable banks tempt you beside a current that can carry a careless worker into a sink, so routes, warnings and rescue shape the visit.

**Land:** distinct floors, materials, visibility and ordinary weather; beach steam above, submerged Scald bubbles below.

**Life:** existing native rosters, forage, prey, predators, moving light and environmental survival; no evictions.

**Signature.** Twilight banks offer the floor’s best forage, drawing workers away from even the lit gardens to a current whose warned surges can carry them to a findable, rescuable sink.

My delegated choice: keep the ruled sea bundle with that current chain as its signature. The cultivated-light economy loses as runner-up because it adds another progression system. Natural temporary wells and the living protected gardener stay under the frozen roof laws. Campaign inhabitants move: removing the reveal defeats neither land, native life nor the signature.

Next version, switched off:

- Steam-catch production, steam-exposure clock and suit research.
- Steam devils, vent flashes, staged sail/walker appearances.
- Wreck-colonising sponge interaction.
- Falling panes, deck accumulation and launch obstruction.
- Suulk feeding, vaulisk ambush and lure-organ reward.
- Cargo floats and harsher sink outcomes.
- Portable light cages, clipped lamps and cultured sunlight.
- Grey hull crust, lamp-response encounters and elder treasures.
- Reactive crowns, contact venom and sentinel squirts.
- Chill growers, extraction and fuel/drug processing.
- Hesuun extrusion, fuselight explosion and tarnn wake.
- Twilight plant charge, wilt and event spreading.
- Lab-ending receiver and theatrical lid-dark events.
- Chill warmth defence and harvestable aurora surges.
- Inhabited campaign holdings and automatic Compact weir dressing.
- Twilight silt-trap fertility upgrade and the optional Scald vent-pool idea.
- Gardener grazing and rim overgrowth, spent-rim patching, and interactive ceiling routing.

Species remain rostered when attached extras stop. Existing code/defs stay behind labelled settings; tickets test default absence, opt-in presence and safe switch-off.

**No retirement recommendations.** The 2026-10-15 card keeps existing cross-biome controls off by default and labelled “Unsupported: may work outside our biomes, not tested”.

**Counts.** Capabilities 77 inventoried, 39 kept. Next version 38. Recommend retirement 0. Bars 0 before, 8 proposed. Live-only bars 0 before, 2 proposed. The CASE provides the empty old-bar set. The proposal census supplies the capability counts. Checks 11, rules 12, unknown shared meetings 8, models 5, tickets 46, questions 1.

# Page two — what to check

My consequential defaults:

- “Sea surface”: floor or neighbouring beach only; ship-only travel, no hatch.
- Scald “perched/outflow”: stale prose; retain the terminal basin, change no world.
- “Scald comfort and cost” means the beach boil both burns and comforts. The cool margin offers bathing without burns. Both stay undrinkable. The floor has hot mineral ground and ambient heat.
- “Clean steam” means freedom from the lake’s fouling. Shared rules handle hot air.
- “Solitary” applies to Grey animals and shore wildlife. Niim and noolim form actual shoals under the Twilight lid. Test both arrival groups and sustained movement.
- “Productive bank” means visibly better forage than even the lit gardens away from the current. In calm, workers choose banks under ordinary orders. The dry-looking bed, surge stakes and warnings make the risk readable.
- “Safe arrival/rescue”: protect hull access from surge; rescue means outside dangerous water in safe shelter/carriage, never merely roofing the sink.
- “Gardener” means the living protected giant swimming far overhead wherever the waveglass stands.
- “Temporary light” means years-scale wells with decreasing countdowns. Ordinary departure keeps the floor and its aging wells. Explicit abandonment ends that floor.
- “Inhabited ark”: the sheet historically promises an initial reveal. Under this later cleansing card I defer it, preserving the promise and peaceful-holdings doctrine; RM bars no longer require campaign content.
- “Off”: stop availability, dispatch, ongoing effects and reload reassertion while preserving saved bodies and contents.

Q1. May 0.1.0 use the shipped week-scale clock for Twilight wells? The current kernel rolls five to nine game days [measured from RM_WellKernel.Lifespan and twilightDriftCadence]. That pace could show turnover during the working season. My default follows the frozen sheet’s years scale. A yes would change the shipped clock and add natural turnover to the season proof. At the years scale, the well turnover bar starts near expiry and follows normal updates until the old light ends and a new well opens. The season keeps ordinary, unedited ages.

Models, first to build first:

- **Situation and transition generator:** actions, gardener protection, transfers, rescue, settings, reload and floor identity on return.
- **Channel and landing geometry:** boundaries, crossing phases, banks, sinks and ship reservations.
- **Whole sea season model:** all kept systems together, including accessible gardens, bank work and advancing well clocks.
- **Liquid and native physiology replay:** beach burns, bathing comfort, drinking denial, ambient floor heat and native survival.
- **Light habitat and food-chain model:** temporary light, replacement wells and viable gardens without the light economy.

Open work includes channel-bed terrain, real hull reservations, the living gardener, composed travel and shore delivery, and a campaign-tier harvest binding. The dependency sources and floor-retention contract are identified. Gameplay evidence is still owed.

The reviewer’s findings are addressed in this revision. The proposal awaits fresh review and your approval before application.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- the converge fix broke an entry it changed (the verifier's words) (bars.json bars/B2). B2 changed in this fix (accept 3, range.left_out and range.varies were rewritten for the far-overhead gardener). Its sees.control still reads 'Pair the visual sort with T43’s ceiling-plane state and overlapping ground-path trace.' The ceiling plane was R13, which is removed. census.json X39 'Selectable ceiling-water plane with cell routing' is now next_version under T52, and the rewritten tickets.md T43 has no ceiling-plane state: it gives a far-overhead animal 'outside the floor’s movement and interaction space'. So a kept bar's evidence still relies on a moved extra (moved_extra_relied_on), and the instrument it names will not exist in 0.1.0. Would pass: B2's control pairs the visual sort only with instruments that exist in 0.1.0: T43's saved living-gardener identity and far-overhead presentation state, with ground paths independent. Nothing in B2 refers to a ceiling plane. Smallest fix: Replace the last sentence of B2 sees.control with: 'Pair the visual sort with T43’s saved living-gardener identity and far-overhead presentation read, and confirm floor paths are unchanged beneath it.'
