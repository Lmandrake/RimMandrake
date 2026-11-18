# Ambiguities settled by the Designer

Every disposition here is **delegated**, inferred from cited owner words, standing rulings and observed source. No new owner preference is claimed. One evidence-backed question, Q1 on the owner pages, is pending about the frozen outdoor-pocket requirement; the stated default applies meanwhile. Where evidence conflicts, the stated first-version default applies now; deferred mechanics retain their existing constraints. The fresh review supplied with this correction refused outdoor pocket consistency, undefined visual concealment, the unargued halo, the overstated owner experience and unmarked figures. Each is repaired below; no objection is disputed or knowingly left unresolved. A later review still decides whether these repairs are sufficient.

## Evidence and authority

`design/concepts/Abyss/` held no record, sheet, tree, log or next-version file before this proposal. The CASE explicitly says old bars are empty. Fallback: `design/RimMandrake/designer_codex_2026-11-09/Abyss/record.json`, `NOTES.md`, `QUESTIONS.md`; frozen world sheet `design/Jawa/worldbuilding/biomes/abyss.md`; owned-sheet rulings in `infrastructure/state/items/ABYSS_SHEET_DONOR_PORT_1.md`; all CASE open/closed Abyss items; source/defs/validation and named shared engines. The earlier record is an inventory and draft bank, not an approved tree. Its rule “present capabilities ... never offered for removal” is superseded for this proposal by the explicit cleansing delegation. Historical build/selftest claims are stale, not current gameplay measurements. No source test, build or live measurement was run on this pass.

Before defining scope I read CLAUDE.md and the CASE's ruling/lore files, with particular weight on biome_rulings, standing_rulings, architecture's amended tier/compose/settings sections, naming grammar, Ash'karr's temperature/hydrology/nightside history, the_one_map's fixed-world constraints and Alien_Bestiary's aspirational status. The older world documents contain mutually superseded tile/temperature statements; none becomes a new placement instruction or a runtime tuning constant. Local evidence controls what is built; the later owned sheet controls names/cuts. Zero owned tiles is not a finding.

## Protection: optical shelter or active invisibility?

Reading A: the Dark obstructs information and slows the existing campaign search. Reading B: a quiet ship is guaranteed invisible to raids and orbit until probes break a timer. Consequence: B needs a cover state, trade consumer, engine-start hook and scout gameplay. Default A in this version; B moves off with its full ruled constraints. Evidence: owner's 2026-10-20 sentence gives protection and nearby terrors; `ABYSS_HIDDEN_SHIP_PROBES_1.md` explicitly defines the additional stealth loop. Source search finds `IsCovered`/`CoverLevel` only in Abyss component/kernel/tests, while `EmpirePursuit/.../RuthlessPursuingMechanoids.cs:ShadowMultiplier` uses biome membership. Thus an internal covered meter cannot prove dynamic protection. Frozen “no orbital eyes” means no clean optical remote localization through the material; ordinary radio trade is not proof of seeing the ship. Trade isolation specifically belongs to the deferred active-cover system, not a substitute new first-version mechanic.

## “A tide” and “just as often”

A literal fluid front and equal beauty/terror event counts versus an enveloping condition that opens/closes and repeatedly changes how the place reads. Literal quotas would invent a tide engine and an attack scheduler. Take the latter for the first-version ambient opening/closing: the owner's 2026-10-20 imagery does not impose equal random counts, a sweeping linear wave or a monster per clearing. B8 requires the swift return to nearby danger when Unveiling ends through the retained Dark/light/feeder/predator chain. Only the long-stay nightmare-source dread is deferred with cryptid content; no equal-event quota or scheduled attack is added. Retain those interpretations in the bar's figurative glossary where the words occur; bar text otherwise uses physical language.

## “Light eaten in transit”

Palette plus endpoint sight penalties versus obstruction by the air between observer and target. Warm shooters could otherwise aim cleanly across the gunk; that violates the frozen no-clean-sensing ban. Take intervening air seriously for view/targeting, with the common density field. R2 specifies accumulated path density reducing effective sight and ranged hit chance through a weather-style modifier for every shooter, including colonists, other factions, animals and turrets. Dim silhouettes remain selectable and otherwise legal attack orders stay available. B2 rejects a negligible long-shot cost; numbers and sampling algorithm remain attackable rules within that effect form. `RM_MapComponentDark.cs` currently sets murk on the pawn and dims a source lamp, and WeatherDefs add a blanket accuracy multiplier. None of those alone proves intervening obstruction or restored warm-room aim. This is specified missing capability, not a passing source claim.

## “Pockets” and the thermometer

Reading A: spontaneous open-air clear patches remain, with a local temperature system still to build. Reading B: outdoor density follows the map's shared ordinary outdoor temperature, rooms follow their own temperatures, and spontaneous drifting patches are deferred off. Consequence: A commits the first version to outdoor microclimates that do not exist in the current game temperature model. Default to B pending owner-page Q1, rather than treating a lore conflict as a settled ruling. Frozen abyss.md §5 requires real, sharp-edged clear pockets unexplained in-world, while §3 says only a thermometer distinguishes them; RimWorld has one outdoor temperature, so that literal adjacent outdoor difference is unavailable. The default omits that required picture, and heated doorways or map-wide Unveiling do not fulfill it. If the owner keeps outdoor pockets in this version, T43 becomes signature work defining a lore-compatible mechanism and B1 gains an outdoor-pocket picture. Source: RM_MapComponentDark.cs:68–75 reads GetTemperature and adds the only spontaneous spatial variation via PerlinNoise; RM_AbyssLight.cs:147 reads OutdoorTemp directly. The retained fold lamp clears directional lanes after ambient density is computed. Cryptid pockets stay deferred. The frozen sheet's collapse mechanism remains ordinary-temperature-driven; this smaller version expresses clear/Dark boundaries at maintained heated rooms and map-wide outdoor thinning/closure, not at warm open-air edges. T43 gates the built offset, T31 specifies the retained query, and B1's doorway picture no longer promises an outdoor pocket. No new heat rule is invented.

## What “conceals” removes from the player's view

Reading A: a sky tint or density-scaled terrain tint leaves predators untouched. Reading B: Dark culls wild/hostile sprites and can make nearby threats completely invisible. Both were plausible under the earlier text, with materially different play. Take neither: local density reduces terrain/relief detail, dims buildings with outlines/footprints retained, and dims wild animals, hostile pawns and neutral visitors with discernible silhouettes. Player-owned colonists, tame animals and mechs stay fully drawn. Selection outlines, inspect access, controls and warning text stay readable. This delegated presentation choice supplies material local loss of detail without silent disappearance; existing silhouettes and close-attack tells keep danger perceptible. Nothing is completely hidden by Dark, and vanilla unexplored fog is unchanged. B1 now rejects both an unchanged predator and full sprite culling; T29 implements exactly this contract. The map-view silhouette does not grant simulated clean sight/aim through the same air.

## Warmth, light and crops

Any bright light clears the air versus warmth clears particles while living light can sustain sight/crops without clearing them. Take the latter: frozen sheet's collapse mechanism and `RM_AbyssLight.cs`/plant defs distinguish temperature from glow. A giant living lamp is not a heater. Warmth without light does not grow ordinary crops, and a crop lamp without warmth does not defeat vanilla winter growth. Dark-grown native life is not a free sunny field. The later lamp-crop ruling is a localized maintained-farm exception to the older nightside-not-farmable line, not permission to change the planet's biome belts.

## What must recover inside a warm room?

Removing murk but leaving global weather accuracy reduction versus actual sight/aim improvement when the intervening air is clear. The first is a lazy false success: the hediff disappears while shooting still has the same Abyss blanket penalty. Take local Dark impairment to clear with warm air; ordinary storm/weather penalties can remain when genuinely caused by Witchfire. Instrument effective attack/sight calculation with same geometry and actual consumers, not only hediff presence.

## Unveiling: sun, fog or particles?

A new solar day/unfog everything versus clear ambient particles and show explored country under a brighter presentation. Take the latter from frozen §4b plus Direct Sun geometry ruling. Actual sun angle, terrain temperature, unexplored fog and solar heat do not change merely because the palette clears. Current commonality/duration are checks; “rare/brief” means the opening interrupts a mostly Dark routine, not a permanent clear biome. M4 will settle recurrence/dwell regimes.

## Halo versus clearing: scope before geometry

Reading A: the frozen halo description forces a new carried-Dark/death-release system into this version. Reading B: it constrains the mechanic when built, while first-version ordinary nevarithia life remains intact without it. Consequence: A adds an unbuilt moving density source and lifecycle exceptions that the ambient signature does not need. Take B under the explicit smaller-first-version delegation. RM_Nevarithia.xml:8–10 says these mechanics are owed, not built; frozen abyss.md describes the knot even where ambient Dark cannot form, not its release schedule. Removing both leaves ambient Dark → warmth/living light → feeder pressure → grain/fuel whole; no species is evicted. T44/T45 preserve the future knot/release constraints, including no donor global eclipse. R8 is removed from first-version rules, and B2/M3/T31 no longer require any halo. Unveiling therefore clears all first-version Dark. This deferral changes no standing ruling.

## Which clauses of the owner's experience this version carries

Reading A: the swift beauty-to-nightmare turn needs cryptid content. Reading B: the kept Dark/light/feeder/predator chain can carry that turn, while discovery of the nightmare source remains deferred. Consequence: A would let a natural Unveiling end with no nearby change even when feeders and a predator are at the colony edge. Take B: B1 reveals etched relief; B8 requires its close to readably return danger through Dark, shrinking artificial light, krizzak feeding and an approaching ishvarith. Its paired pictures hold those nearby conditions fixed and reject a mere sky-tint change. Protection/nearby terror remains carried by B1/B2/B4/B7 and sustained in B8. Only the long-stay source dread moves with cryptid sites, phantom events, whispers/tales and dreams. Material erosion does not substitute for that dread; no new event system or attack scheduler is added.

## Figures in the remaining bars

“Hears stillness” means the absence of a steady wind bed between gusts, while colony/fire/combat sounds continue; it cannot mean total mute. “Runaway” residue means accumulation beyond ordinary hauling/refining capacity, not moving stacks. “Cascading” errors means exceptions that repeat or spread after a fault, not a literal cascade. B7/B8 now list each word, its operational meaning and a contrasting literal-departure accept picture. These are presentation/whole-run meanings, not added mechanics.

## “Reliable” living lamps

Absolute immunity to all light loss versus immunity to ambient Dark but edible by the native light feeder. Absolute immunity makes the krizzak meaningless; take resistance to ambient Dark only. Deepfire likewise retains its specifically ruled ambient-Dark exemption; no source makes it inedible to krizzaks. Ordinary glower paths and walls remain real. These are conditions, not promises of a lamp keeping a particular radius.

## Krizzak: “settles on” and what shrinks

Radius-only nearby feeding (even across walls) versus local unobstructed feeding at the emitting lamp/plant with actual useful light loss. Take the latter. `RM_CompKrizzak.cs` checks approach reachability only for distant targets, not nearby sight lines. A moth outside a sealed farm cannot feed through its wall. Power, hull and glower existence remain intact. The glow/overlight grid must agree with effective loss: dim art with fully productive overlight is a wrong build. Heat interrupts feeding via actual temperature; taming removes theft, not flight. Death/downing/despawn ends feeding and recovery follows. Reload may reset the unscribed feeder share as current code deliberately does, but cannot erase ambient Dark or another ledger share.

## Ishvarith: “a lit camp neutralises it”

Impassable light barrier/invulnerability versus a predator's interruptible retreat when in light with reachable darkness. The settings tooltip overclaims compared with `CompLightAversion`. Take the latter: observable useful deterrence, ordinary pathing and danger remain. A cornered beast can fight; a short cooldown is allowed. Light restoration must actually change a relevant approach/retreat, not a distant irrelevant animal. The first version does not add a temperature-aversion engine just because an old description mentions heated space.

## Ombrathia “before it lunges”

A warning on distant hunt-job assignment versus a readable close-attack tell before damage. Source records `lastJobId` and warns once at job start; a player may never see/hear that warning. Take close actionable tell; text stays useful under muffling. It does not reveal a hidden animal across the entire map or require a new ranged-quill ability. Job interruption/reload must not spam or suppress it forever.

## “Life” cannot hide secondary systems

Any custom behavior of a roster animal counts as life versus ordinary functioning diet/locomotion/attack/husbandry plus only signature-critical unusual behaviors. Take the latter. Gust feeding is gharrek's ordinary chemotrophic food source; real flight is krizzak locomotion; saevitha drain is its primary attack, not a stacked hazard. Sorter shared filth-foraging/vanilla haul training is its diet/utility. Extra Summ regeneration/UV, endless size escalation and bonded autonomous killing are separate husbandry systems and move off. Finite native age stages and the Summ roster stay. Species are never evicted to simplify implementation.

## Ordinary stock and missing donor abilities

Imported descriptions imply every donor ability already works versus definitions show only some attacks/products. The headers omit corpse-decay/disease, low-rest, custom blades, spine spray and digging/group-rage. Census separates these absent promises and defers them; it does not silently declare them built, nor demand a reconstruction of the donor engine. Native default descriptions must not promise active dormant mechanics. An old comment/body-size count is not a new bar. Shoulder blades on ysvaltha do not establish flight in fiction; krizzak explicitly flies and uses real Pawn_FlightTracker.

## Native plants, light and food

“Glowing” as tinted texture versus actual illumination; “grows here” as roster row versus a viable establishment/regrowth path. Glowing grass currently lacks CompGlower; globe has growMinGlow and paddle vine inherits fields. Take real low grass illumination and viable native growth without sky dependence, calibrated on resolved RM and campaign defs. This need not make every native plant sunlamp-strength. Wild starters cannot require a light cluster that their own establishment makes impossible. Light-shy flora in a description does not imply an unimplemented overlight-damage engine. Ordinary plant and soil rules determine growth; new hazards remain deferred.

## “Only in hollows”

Any fertile soil versus the actual etch-hollow substrate. `RM_Etchcap.xml:fertilityMin` is below `RM_ForsakenSand:fertility`, so the current threshold admits plain sand. Take an explicit substrate restriction for growth and planting. Static ordinary local hollows may provide initial habitat before long-term erosion creates more; the roster entry alone cannot conjure a legal substrate. No extra hollow-making job.

## “Ultima fibres” and gourmet produce

New premium fiber/meal multipliers versus ordinary local fiber and edible fungus with existing harvest/cook actions. Giant stalk's later owned description says its fibers cannot be worked; inherited TreeBase fields need resolution. Take that later boundary, no new premium resource. Etchcap stays an ordinary distinctive ingredient; cuisine machinery and lore lavishness are not needed to make food/lighting work. RawBerries are the existing bush product and remain ordinary abstract forage. T41 defines a mobile-light product for direct bush harvest in 0.1.0. T41 preserves ordinary food use while adding actual item/carrier illumination. Abstract forage should match native berries, not imply a missing agave field.

## Etchfall: rain, steel and rate

Water rain that damages everything outdoors versus chemical grains affecting unroofed natural rock and steel-stuff edifices only. Take the latter from the closed etchfall item and `Erodible`; roof immunity remains literal. Stone-built furniture is not natural rock. Exposed fixed-steel defs require resolved inspection, not an invented material category. Other ordinary deterioration remains distinct. Grain under Dark/storm and stronger under Unveiling is the existing allowed stochastic abstraction, not a claim to simulate atmospheric mass chemistry. No soak, acid pawn hediff or rain-fed explosive growth. How much rock/fuel remains after a season is **unknown**, to be decided by M2 calibration.

## Gusts: detecting or making wind?

A `GustCount` rise proves land's wind versus the actual wind history has stillness and brief pulses. The controller only reads vanilla speed and Witchfire multiplies wind. Take actual intermittent wind; detector/audio/feeding must agree, not cosmetic imitation. No new turbine is requested: lamp-crop item explicitly says the gust-turbine echo was cut. Nutrition vs prolonged low wind is another M4/M2 unknown; do not solve by forced proof gusts or starving native stock.

## Audio: mute, source or listener?

All sounds vanish versus placed map sounds lose high-frequency clarity according to Dark at the camera/listener, leaving UI useful and environmental events recognizable. Take the latter, per existing Sample.Update hook and recorded ship-on card. A gunshot whose source is in a warm room can still be muffled to a listener in Dark. A muffled UI alarm is a wrong build. No fresh owner approval is sought for the shipped default or listening waiver; later owner-present listening concerns the remaining sensory bar, never a repeat scope question.

## Built coupling and switches

“Off” stops new placement only versus no default player-facing activity or entry points. Take the latter under this brief. Owner-marked exception: observation-off retains its silent load grant for the kept fold lamp, while discovery checking, offers and letters stay off. Concrete traps for other deferred features: cairn memory ignores its placement switch; cryptid sites call Place directly; baneEnabled guards killing after hunger is added; ProbeTick precedes Applies; salvage/use recipes lack an independent default-off barrier. Tickets address each caller. Dark may call neutral disabled lane/phantom APIs; code reference is not need. Unveiling drops ring-specific look targets while keeping physical-clearance text.

## Reusing existing engines versus adding a signature

Every named dependency must invent an Abyss hook versus retain only the integration actually needed. Take existing behavior: no Abyss wetness call was found in ExplosiveGrowth and none is requested. Bones handles ordinary butchery, not great-bone retrieval. Wreckage handles normal ruins, not the finite rescue wreck. Taozin and its nest stay neighbour-owned, including their current consequences; deleting an external roster entry is prohibited. Acoustic payload stays under its all-biome ruling, with banded ambiguous readings; it does not justify reactivating sorter sites. The older inventory's world-swirl ownership was wrong: `BiomesShell/Source/RM_WorldLook.cs` supplies it.

## Fixed world and old names

Existing GetScore/rarity UI is an authorized feature versus prohibited residual worldgen. Take the latter: standing no-worldgen ruling overrides architecture's older generalized-planet prose. Recommend retirement, disable permanently now; never place worldgen on a next-version enable list. Local content placement on existing fixed-world tiles remains allowed. Latest roster owns black-kin names; old aspirational Bestiary clades do not add animals. RM_Lirrith also appears in Cracked Lands' patch; record multi-homing and move on. Do not reopen waived cut creatures/dusk-rat art or the accepted zero-tile consequence.

## Deferred expedition decisions are preserved, not reopened

“Glory” could mean redesign or condition repair; future default is repair only, with accepted/refused parts in plain words after the haul. “Lip” versus coils: item explicitly grants return-at-lip, while code checks near the mother; future spec must provide a real lip-return action, not silently narrow it. “Bone aboard” means the actual ship, not any disconnected substructure on the same map. “Never stops growing” means no terminal plateau; finite Elder/Ancient stages are not fulfillment. Lightfall is the place ambient Dark clears, so a later brood biology draft cannot make it perpetually opaque; carry local halo/roof effects only if compatible. Greed uses one meter; exact boundary may be learned by save/load under the existing owner waiver. No question repeats that waiver. These future constraints cannot affect this version while gates are off; the next-version spec tickets carry them before any enabling.

## Rejection attack, second pass

I tried the cheap build: ship dark sky colors, keep ordinary crop production, disable all unusual interactions and show one forced clearing. It fails the spatial land picture, warm-air/obstructed-ray bar, lamp-thief growth/predator bar and unforced season bar. I tried the opposite: count every donor description as ordinary life and keep the brood because its egg code calls Dark weather. That would preserve independent hazard/reward chains merely through code coupling; the census instead separates attack/diet from extra behavior. The kept loop still has unresolved geometry, recurrence and population/material feedback, explicitly named in meetings/models. No assertion of fun, tuned balance or current gameplay pass was invented to close those gaps.

## Old bars and legacy proof disposition

There is no concept tree or locked leaf to preserve: bars.json old_bars is exactly empty, as the CASE requires. The old validation.py chains are checks, not secretly old bars. Etchcap/gharrek/durrgak/freed-beasts/krizzak/etchfall/dark/predators/lamp-crops/soundscape/names def checks feed C1–C5 and C8–C14, with actual experience re-derived as B1–B7 from owner sources. Cover, cryptid and brood checks remain scoped to next-version opt-in, including their production-kernel fuzz and mutation tests; they must not require those features on for the first-version default run. Brood checks feed C6, never the new whole bar. Existing live chains largely resolve defs; ProofSigns actively places signs, ProofGust forces a gust, and exchange/phantom proofs force their effects. These remain diagnostic helpers and cannot be presented as unforced natural map/lifecycle or season evidence. T37A adds the missing instruments, with controls. No old owner bar was silently loosened or dropped.

## Owner-marked first-version light and fishery boundaries

The owner marks override the earlier delegated deferrals for fold_lamp, vine_turning and glowberry_item and add a fishery. Heat observation remains next version. Lamp availability could wait on a disabled observation or use the existing FinalizeInit off-state grant. Take the load grant, because the census explicitly records it and the owner kept the lamp while leaving observation off. T4 makes completion silent and idempotent before normal build availability.

For turning vines, a fixed decorative pose and actual source-responsive turning produce different plants. Take visible response to useful reachable light. My default strongest-source choice, stable ties and retained no-source facing are implementation rules recorded in T39. For berries, icon tint and useful carried illumination differ. Take actual item/carrier light with safe ownership and ordinary food use under T41.

For fish, loot-table entries alone and living swimming catch species differ in scope. The standing fishables ruling selects living moving counterparts. My RM_Veiljaw and RM_Suturefin designs, mineral-pool habitat and ordinary fishing action are delegated details implementing his creepy-dark-creatures mark. They introduce no new expedition or planetary placement mechanism. T51 verifies every catch mapping, living movement, pool food and ordinary acquisition. Empty, missing or invalid mappings fail the builder's manifest check.
