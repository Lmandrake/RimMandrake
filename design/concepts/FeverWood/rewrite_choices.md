# The Fever Wood: what the rewrite chose, what it lost, and why

Companion to `design/concepts/FeverWood/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, the crew are Jawa *"way in over their head"*, *"anything that takes seasons to observe will simply be
missed"*, and for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is
*"the overriding priority"*. So: a thing a crew meets inside a stop of days went early; a thing only a settled
colony would see went later, however good; nothing he had ruled was reversed, and where the lens argues against one
of his earlier picks the row says so and the design marks it `NEEDS HIM`.

**Words used in "what happened".** *kept*: in the design with its meaning intact. *kept, reshaped*: in the design,
changed as stated. *moved*: its scope bucket changed, from and to given. The older cleanse proposal
(`cleanse/definition.md`, 2026-11-17) used three buckets, "first version", "next version, switched off" and
"recommend retiring"; this design uses 0.1.0, 0.2.0, later, dropped. A cleanse "next version" item that lands in
"later" is counted as *kept in its bucket*, not as a move. *folded into shared machinery*: it is a shared engine's
job. *lost*: not in the design.

## The ones I would look at

1. **The Mooring** (the water wraps the ship's hull; launching tears a section off). He did not choose it on
   2026-10-02, before he had stated the ship lens. Under that lens it is the most direct answer anyone has written
   to *"What happens RIGHT AWAY when the ship arrives from the sky?"* The design uses only its quiet half (the
   landing is heard below) and asks him.
2. **The Lost Crawler** (the bait turns out to be pieces of one old Jawa sandcrawler, the clan's own). Not chosen
   2026-10-02. It is the only idea in any source that makes the bait personal to *this* crew. Lost; it also needs a
   long stay to collect the pieces, which is the honest reason it stays lost.
3. **The thieving bird.** The cleanse recommended retiring the promise. I moved it back in, to 0.2.0: a bird that
   robs a crew of professional scavengers is exactly the slapstick he asked for.
4. **The sap-drinkers' refusals.** The cleanse moved all three to "next version" as extras. I moved the seal and
   the swelling to 0.1.0 (built, deterministic, funny within minutes) and the scream to 0.2.0.
5. **The prison tank and everything that follows from it** (products, escape, the escapee growing into the real
   thing). *"That's why they're not farmed, they're imprisoned."* Beautiful, his, built, and a colony's story: it
   needs weeks of upkeep. Later. The one piece a travelling ship can use, returning a young for a great gift, is
   kept at 0.2.0.
6. **The reactive ant-hive dungeon.** His 2026-09-22 ruling made hives *"dungeons in their own right"*. Later,
   because a stop of days already has the pools competing for the same hours. If he wants one expedition per stop,
   this is the candidate to bring forward.
7. **The cistrel cup**, *"the only safe water in the Fever Wood"*. It should be early (water is what a stop is
   worth) and is at 0.2.0 only because the thirst service it needs is not in this checkout.
8. **Sink-mud.** *"The floor is the wall."* Unbuilt. It is the Fever Wood's real answer to an Imperial strike and
   to why small light Jawa do better here than armoured troopers. 0.2.0, and the first thing I would build there.
9. **Bog-timber.** The sheet's *"bog-timber and potter's clay"* lost its first half to the 2026-10-17 tree ruling
   (only true trees give wood). The tree stays as scenery. Nobody chose this loss for the Fever Wood in particular.

## Scope moves

One line per feature whose bucket changed against the cleanse proposal of 2026-11-17 (or against his earlier card,
where said). Each can be reverted by moving the line in the design's Scope section.

- **Vaulm seal and drommath swelling:** next version → 0.1.0. A crew sees them the first time it handles one.
- **Ollareth alarm:** next version → 0.2.0. Same reason, but what answers the scream is undefined (the old gap the
  coverage judge named), so it waits for that definition.
- **Thieving bird:** recommend retiring → 0.2.0. Slapstick against scavengers; costs one gated behaviour.
- **Lure stake and the two fronts:** next version → 0.2.0. "Who else attacks here" is one of his lens questions,
  and the staggered arrival can be pointed at an Imperial strike.
- **Oil boil:** next version → 0.2.0. His card of 2026-10-02; a weather event shows itself inside a stop.
- **Radioactive charge:** next version (question pending) → 0.2.0 (question carried over).
- **Ransom of the young (release and gift):** next version → 0.2.0. It rewards arriving with cargo, which only a
  ship does.
- **Summoning the eye:** next version → 0.2.0. A short stay needs a way to choose the moment.
- **Broken hives at the mirrors; the corvath spike as a placed tell:** next version → 0.2.0. Day-one evidence.
  (Corvath *appearing* after a feeding stays later.)
- **Wreck field; acoustic sounder readings:** next version → 0.2.0. Salvage is the crew's trade and the sounder is
  a ship part.
- **Sink-mud and the skimmel skin:** next version → 0.2.0.
- **Cistrel cup:** next version → 0.2.0.
- **Stayed "later" from the cleanse's "next version":** tank industry, escape and maturation, world-held-young
  pressure, the hive (all five parts), borer galleries, regrowth and sealant, moving routes, plennith soil, mirror
  break, arrival letter, grolth trail, the Sporefall display. Not moves.
- **New, not in any source:** the ship's landing as a noise the water hears (0.1.0); troopers seized like anyone
  else and trunks breaking the Empire's sightlines, stated as promises with scenes (0.1.0). Both are consequences
  of built behaviour; drop either by deleting its line.

## Every idea, row by row

Source names: *sheet* = `biomes/the_fever_wood.md`; *deep-and-mud* = `biomes/fever_wood_deep_and_mud_2026-09-23.md`;
*fauna roster*, *flora roster*, *cast proposal*, *syllable pass*, *bedazzle review* = the dated files of those names
in `design/Jawa/worldbuilding/biomes/`; *kit spec* = `biomes/kits/fever_wood_kit_spec.md`; *roster json* =
`biomes/rosters/the_fever_wood.json`; *names doc* = `biomes/noncanon_beast_names_propane_arid_forge_pyre_fever_greentide_rust_lantern_blue.md`;
*Designer sheet*, *plan*, *log*, *journal* = files in `design/concepts/FeverWood/`; *cleanse* = `design/concepts/FeverWood/cleanse/`
(definition, next_version, owner_pages, ambiguities, tickets, models, census); *walk* =
`design/validation_walks/RimMandrake/FeverWood.md`; *owner answers* = `design/RimMandrake/designer_codex_2026-11-09/FeverWood/ANSWERS_OWNER.md`;
*tenant digest* = `design/Jawa/campaign/fever_wood_tenant_digest_2026-10-10.md`; *rising* =
`design/Jawa/worldbuilding/sekkulaath_rising_crater_event_2026-11-01.md`; *fluff cuts* =
`design/RimMandrake/fluff_cuts_2026-10-23.md`; *experiences* = `design/RimMandrake/biome_experiences_2026-10-20.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Wood-roads through a living crown above black mirror pools | sheet header, §1 | kept | It is the picture the ship descends into. | |
| "The place where trees finally won" | sheet §1 | kept | Carried over word for word. | |
| The giant stillness; one wetland with the Miasma, which is everything in motion | sheet header | kept, reshaped: the stillness survives as the silence; the Miasma comparison is not restated | A crew at one stop does not compare two biomes. | Restate the pairing in a campaign-level document; free. |
| The thirsty-flora family (Greentide and Webwork drank a river; here the trees drank the chaos) | sheet header, §3 | lost from this design | World lore, not something seen at a stop. It belongs in a world document. | Keep one sentence here; harmless. |
| Measured tiles, sun, temperature, no rivers, no rain | sheet §0 | kept, reshaped: no rain and no flowing water kept as bans; tile counts dropped | A tile count is never evidence (standing ruling); the planet is painted once at the end. | |
| Donor inventory kept: marsh too soft for heavy structures | sheet §0, §6 ban 4 | kept | The land's first rule. | |
| Low ground animal density, the crown teeming | sheet §0, deep-and-mud §6p | lost as a mechanism (owner: *"Don't worry about this"*) | Declined 2026-09-23. | |
| Trunks much more than one tile wide, mineable, never falling | sheet §1, deep-and-mud §6a | kept | *"So you can just mine right through one."* Also why the ship's landing topples nothing. | |
| The trunk's two built defs (the mineable body and the one-cell marker) and their bark-edge art defect | deep-and-mud §6a, flora roster §2 | kept as a build fact, not design | Art debt, owned elsewhere. | |
| Byways that *"seem fixed and are not"*, slowly varying | sheet §1, §5; kit spec; Designer sheet "later" | kept in "later" | Nobody sees a road move in a week. | Bring forward: needs the encroachment engine. |
| Water from below, life from above; deep mud as the nutrient bank | sheet §3, deep-and-mud §6e | kept as the reason the animal does not need the crew | It is what makes the baiting chilling. | |
| The oils boiling gently to the surface | sheet §3 | kept, reshaped: a plant you harvest (seepril), per the 2026-09-23 card | His card. | Ground that weeps oil: declined then. |
| Verticality is paint, walk on and off, no climbing | deep-and-mud §6h | kept | His card; zero new mechanism. | |
| Bough-soil, a fertile terrain so the crown can grow | deep-and-mud §6b | kept | Built. | |
| Stilts for building on marsh | sheet §7b, kit spec | kept, reshaped: stated once, not promised as how the crew lives | The crew lives aboard; stilts matter to a colony. | |
| Base-building in trees and bore-cave rooms | sheet §7, §7b | kept, reshaped: rooms can be mined; living in them is not promised | Same. | |
| "A lamplit crown over black glass — giant stillness, twice inhabited" (art theme, palette, light, sound) | sheet §9 | kept as art direction; one line quoted | The Wildsteam's lamps are campaign-layer; the two registers stacked (loud crown, silent floor) are kept. | |
| Experience line: *"A world in the treetops above a black mirror nobody touches. You live on the branches, and the water remembers."* | experiences | kept, reshaped: "you live on the branches" becomes "you visit" | It was picked by card for a settled colony. *"The water remembers"* is kept exactly (the angered pool). | Keep the colony reading for a later version; free. |
| The owner's November answer: routes shape the day, *"and a little 3 when tentacles emerge from the water"* | owner answers; Designer sheet | kept, reshaped: under the ship lens the water moves from "a little" to the centre | He gave that answer to a question about making a home. The lens he stated on 2026-11-18 changes the question. | Hold the old weighting: the stop becomes about walking routes, which a crew of days barely uses. This is the reshaping he is most entitled to reverse. |

### The thing below

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The sekkulaath: ours, invented, one species; the dianoga mapped over it in the campaign | deep-and-mud §1, §1a | kept | His naming. | |
| Never enters the screen; only tentacles are drawn | deep-and-mud §1 | kept | *"so big it can't even enter the screen"*. | |
| The horror is scale, not mystery; *"shocking even to those who know them"* | deep-and-mud §1 | kept, quoted | | |
| The old ban on naming or showing it in ordinary play | sheet §6 ban 1 | lost (superseded by him, 2026-09-23) | | |
| *"Never killable, only driven off"* | deep-and-mud §1 | lost (superseded by his own ladder the same day: the eye can be killed for the map) | | |
| Canon facts that do mechanical work (colour change, hum that scares prey, hearing, water-bound, regrows limbs, strips victims, eyestalk) | deep-and-mud §1 table | kept, reshaped: hearing, water-bound, regrowing limbs and the eye are in the design; colour change and the hum are not promised | The free tier must be whole without canon; the two dropped facts have no scene. | Promise a pool that *looks* empty and is not: needs art and a test. |
| The pools are windows onto one water table | deep-and-mud §6e | kept | Why one kill clears a map. | |
| It farms on purpose; intent without communication | deep-and-mud §6e | kept, quoted | The whole joke with Jawa. | |
| Treasure as bait, a slow renewing trickle | deep-and-mud §2 | kept | | A depleting hoard: declined by card. |
| The rare visible deposit | deep-and-mud §2 | kept, reshaped: must be seeable within a stop by a crew that watches | *"If you live there, you might even see"* was written for residents. | Leave it rare: most crews never see the best image in the biome. |
| Six limb types as a pseudo-bestiary | deep-and-mud §2 | kept (five ordinary, and the opening one with the eye) | Built. | |
| The feeler, blind, searching after noise | deep-and-mud §2 | kept | | |
| The snare, the killer, with the rescue window | deep-and-mud §2, kit spec card 2 | kept | | |
| The lash at maximum reach | deep-and-mud §2 | kept | | |
| The porter, *"more slender and delicate than the others"* | deep-and-mud §2a | kept, quoted | | |
| Attacking the porter angers the pool and ends its gifts | deep-and-mud §2a | kept | | |
| The sentinel, motionless, and the silence | deep-and-mud §2, §4 | kept; also the first thing the ship meets | | |
| The bloom that exposes the eye | deep-and-mud §2 | kept as the set-piece | | |
| Drive-off ladder: hours, a day with a severed limb, a day map-wide for the eye, permanent kill | deep-and-mud §2b | kept; durations described, not pinned | A bar is an experience, not a number. | |
| Severed tentacle as the only renewable source of the animal's meat | deep-and-mud §2b | kept | A take-away. | |
| Canon product line (pie, spleen tea, cream) | deep-and-mud §2b, §6j | kept in the campaign layer only | Canon names route through the campaign tier. | |
| "Permanently on the map" is per map | deep-and-mud §2b | kept | | |
| The set-piece must actually arrive | deep-and-mud §2b | kept, reshaped: must arrive within a stop for a crew that works a great pool | The lens. | |
| Four triggers: base roll, provocation, accumulated pressure, deliberate summon | deep-and-mud §6d | kept; the summon moved (cleanse next version → 0.2.0) | Provocation and pressure are built and fit a greedy crew. | All four in 0.1.0: the summon is unbuilt. |
| No protection for an early colony | deep-and-mud §6i | kept | His card. The ship is the way out. | |
| Legibility instead: pool size, the silence, corvath, the town's pool list | deep-and-mud §6i | kept, reshaped: size, silence and a new reach overlay in 0.1.0; corvath in 0.2.0; the list dropped | The overlay (from the cleanse) teaches before the first grab. | |
| Reach scales with the pool | deep-and-mud §3 | kept | | |
| Mud only kills near water; mud and water one mechanic | deep-and-mud §3 | moved (cleanse next version → 0.2.0) | Unbuilt. | |
| Three-state ground: silt, sink-mud, mirror | deep-and-mud §3 | moved with it | | |
| Stick chance scales with weight; *"the floor is the wall"* | deep-and-mud §3, §6h | moved with it; *"do not weaken the weight-scaling"* is kept as written | Under the lens it is what the biome does to troopers. | 0.1.0: adds an unbuilt state machine to the first version. |
| Radioactive suppression; campaign salvage only; free tier from Uranium | deep-and-mud §2b, §6f | moved (→ 0.2.0), `NEEDS HIM` | The cleanse's open question, carried over. | 0.1.0: his ladder names it. Costs reagent jobs and tests in the first version. |
| Seep-oil and the Greentide sealant are not the suppressant | deep-and-mud §6f | kept as a ban | | |
| The tank teaches, produces, and can get out | deep-and-mud §6j | kept in "later" | A colony's industry. | 0.2.0: then a crew carries a live tank aboard, which is a good joke and a large test surface. |
| The tank is a prison; the escapee is tough, makes for water, establishes, matures | deep-and-mud §6m | kept in "later" | Stage 3 takes days to weeks by his November answer. | |
| Several days to maturity; only poison at that pool intervenes | owner answers | kept in "later" with the tank | | |
| "More generic creatures" in tanks, plural reading left open | deep-and-mud §1a | lost (still open, not this design's) | Do not invent a second species. | |
| The ransom of its young: world-held young embolden the pools; a returned young earns one great gift; Sporefall's display tank | bedazzle review §3, §8 (his card) | kept, reshaped, moved: release-and-gift at 0.2.0; world tally and the Sporefall bargain later | The gift suits a ship that arrives with cargo. The tally is a planet-wide system. | All later: loses the best reason to come *back* to the Fever Wood. |
| Varruth's Catalogue (a salvage house feeding debtors to the pools) | bedazzle review §5 | lost (not chosen 2026-10-02) | | A quest for a later campaign pass. |
| The Lost Crawler | bedazzle review §3 | lost (not chosen) | See "the ones I would look at". | Reopen it: a long-stay story; cost L. |
| The Wildsteam Drum (calls the whole animal once) | bedazzle review §3 | lost (held off the card; spends the plot reserve) | | |
| The whole animal rising | sheet §4, deep-and-mud §0, rising, tenant digest | kept outside the biome's versions | The campaign spends it once in the crater event. | |
| After the rising the region's pools stay savage for good | rising | kept outside the biome's versions | Campaign state. | |
| "The Tenant" as the kit's word for it | kit spec, tenant digest | lost as a name in prose | An internal label; the animal has a name. | |
| The terribly lost: big animals drink and are subtracted | sheet §4 | kept, reshaped: any non-native animal, the crew's own pets included, with a readable sign | Its dedicated creature was cut; the standing rule is that nothing vanishes without a sign. | |
| The mirror list sold by the town | sheet §8, kit spec, cleanse | lost (recommended for dropping; his to confirm) | The overlay gives the warning without a shop. | Keep it as a campaign trade good at Sporefall. |
| Mirror-break incident | kit spec, cleanse | kept in "later" | The sentinel already carries the moment. | |

### The crown's animals and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Thornbugs and the nectar deal; never yield under fear | sheet §4, ban 6 | kept, quoted | | |
| Fear radius: a far raid does not dry a sheltered herd | kit spec card 3 | kept, no number | | |
| Worked by Wookiees and Ewoks (the arboreal canton) | sheet §4, §8 | kept in the campaign layer only | Canon peoples. | |
| The guild of four; one rule, four refusals | deep-and-mud §6, §6g; fauna roster | kept | | |
| Vaulm seals in sap; lacquer | fauna roster | moved (cleanse next version → 0.1.0) | Built; an instant "did you see that". | Leave it out: 0.1.0's creature moments are then all the sekkulaath. |
| Drommath swells; burst for a one-time payout | fauna roster | moved (→ 0.1.0) | Same. | |
| Ollareth screams and the crown comes | fauna roster | moved (→ 0.2.0) | What comes is undefined. | |
| All four herdable; taming does not disarm them | deep-and-mud §6n | kept in "later" | Ranching is a colony's work. | |
| Refusals legible and avoidable, never random | fauna roster §7 | kept (it is the scene's control) | | |
| "Drops into the pool" as a defence | deep-and-mud §6 | lost (declined) | | |
| The guild as a perimeter decision against ant theft | fauna roster §2 | lost | The theft was cut 2026-10-23. | |
| Brathek, the grub that eats wood | fauna roster §3 | kept as an ordinary animal | | |
| Brathek's galleries advancing through a lived-in trunk | deep-and-mud §6q | kept in "later" | *"Slow and visible"* by ruling: slower than a stop. | |
| Brathek as a living excavation tool | deep-and-mud §6q | lost (unsettled then, unbuilt, a colony tool) | | |
| Kasselith (the renamed donor borer) | fauna roster rulings, roster json, names doc | kept as a roster row | Evictions are stopped. | |
| Silloch, the bark that waits | fauna roster §4 | kept, with its bounded strike | An "OMG" on a pet. | |
| Lommerel, the upside-down grazer | fauna roster §4 | lost (cut by him 2026-10-08) | | Art exists; restoring is a roster row. |
| Thavrik, the furred nest bird | fauna roster §5 | lost (cut 2026-10-08) | | Same. Note the validation walk still lists it as wired. |
| Nests worth raiding | deep-and-mud §6c | lost with the thavrik | | |
| Nemmel, the mud-shoed grazer | cast proposal | lost (cut 2026-10-08) | | |
| Gorrameth, the great placid wanderer, and its doomed-herd incident | cast proposal | lost (cut 2026-10-08); the incident with it | The most beautiful of the cut animals: *"built to look like it is about to kneel at the wrong pool"*. | Restore one row at trace rarity: a crew would likely never see it in a week, which is why it stays cut. |
| Grolth, the carrion mound | cast proposal | kept as an ordinary animal | | |
| Grolth's acid trail | cleanse | kept in "later" | Unbuilt. | |
| Chellow, tameable, *"a lamp with a bellows"* | fauna roster §5 | kept; also a take-away | | |
| Murrelith, ribbon plumes worth money; selling feathers shoots your alarm | fauna roster §5 | kept | The temptation works in a week. | |
| Skellick the thief | fauna roster §5; cleanse | moved (recommend retiring → 0.2.0) | See above. | |
| Birds must be alien, never parrots; all really fly | deep-and-mud §6c, fauna roster | kept | Standing rule on flight. | |
| The chorus is each animal's own noise added together | deep-and-mud §6k | kept, quoted | | |
| The crown is the loudest place on the planet, against the Webwork's silence | deep-and-mud §4 | kept | | |
| The crown goes quiet only for the water | deep-and-mud §4 | kept; the landing hush respects it (the water stirred) | | |
| Killing birds quiets the map; a tamed flock is a private alarm | deep-and-mud §6k | kept | Free consequences. | |
| Homeless canon fliers as injection candidates | deep-and-mud §4, fauna roster | kept in the campaign layer, unassigned | Not this design's to place. | |
| Canon and donor roster rows (urusai, gelagrub, nuna, longtail gorg, convor, whisperbird, fambaa, butterflies) | roster json, cast proposal | kept where the campaign patch puts them; not in the free design | Tier rule. | |
| Three Biomes! ports judged out of this campaign roster | bedazzle review §8 | kept | His card. | |
| Fauna names and the three renames | syllable pass, names doc, cast proposal | kept | | |
| One planet, one language; wetter and slower | deep-and-mud §6o | kept | | |
| Legibility matrices (every silhouette nameable) | fauna roster §6, flora roster §7 | kept as art direction; three lines quoted | | |
| Thulvane, the fused tower | flora roster | kept | | |
| Skethral, the tree that grows the roads | flora roster | lost (cut 2026-10-08) | | |
| Varnoth, standing in the water, *"a pier you must not walk to"* | flora roster | kept as scenery; its timber lost | Tree ruling of 2026-10-17. | |
| Plennith makes the crown's soil | flora roster | kept in "later"; the plant stays | Soil-making takes seasons. | |
| Ossagrel, the weeping cane; sap host of the guild | flora roster | kept as a harvest; the host dependency lost | The cleanse found no need for it. | |
| Cistrel, the only safe water | flora roster | moved (cleanse next version → 0.2.0) | See above. | |
| Maulith, *"a room with walls"*; concealment | flora roster | kept as a plant; concealment not promised | No scene shows it hiding anything yet. | Promise that it blocks sight: a real gain against the Empire's probe, and an engine check first. |
| Verrow gourds, the crown's fruit | flora roster | kept | | |
| Nubrith, the only light, never fungal | flora roster | kept | | |
| Halquin, the medicine | flora roster | kept | | |
| Ammeth, the roof panels | flora roster | kept as a plant; the building material lost | Tree ruling. | |
| Claithe and potter's clay | flora roster, sheet §7 | kept | | |
| Corvath, grows only where it has fed; *"a grave marker"* | flora roster | moved: placed tell at 0.2.0; appearing after a feed later | | |
| Sodderel and bog-timber | flora roster, sheet §7 | kept as scenery; the timber lost | Tree ruling. | |
| Seepril and the honest rainbow | flora roster, deep-and-mud §6s | kept | | |
| Skimmel, *"firm ground — which is the lie"* | flora roster | moved with sink-mud (→ 0.2.0) | | |
| Wanlith, the pale one | flora roster | kept | | |
| Tullick, the tuber | flora roster | kept | | |
| The ground layer is thin on purpose | flora roster §5 | kept | | |
| Dianoga's Kiss and the three canon plants | flora roster §6 | kept in the campaign layer | | |
| Giant leaf | roster json, walk | kept | | |
| Fast jungle growth | cleanse (engine) | folded into shared machinery | `ExplosiveGrowth`. | |

### Raiders, weather, the ship, the gods

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Two raiders from opposite directions who hate each other | sheet §4 | kept | | |
| The ants are a wild swarm, never a faction (hidden plumbing factions are fine) | sheet ban 2, kit spec card 1 | kept | | |
| Kurreth and skreth; the skreth as the free face of the Webwork brood | cast proposal | kept | | |
| Ants steal thornbugs alive; track the column, raid it back | sheet §4, bedazzle review §8 | lost (cut 2026-10-23) | | `git` restore is written in fluff cuts. |
| "Open the gates between them and stand back" | sheet §7b | kept, reshaped: the Empire can be one of the two | The lens. | |
| The lure: living bait, a gamble, staggered arrival | deep-and-mud §5, §6l | moved (→ 0.2.0) | | |
| No crafted decoy, ever | deep-and-mud §6l | kept as a ban | | |
| Whether the lure cares about the prey's quality | deep-and-mud §6l | lost (still unset) | | |
| The reactive hive dungeon | deep-and-mud §6r, cleanse, fluff cuts | kept in "later" | See above. | |
| Hive farm, guards, sealing corridors | cleanse, fluff cuts | kept in "later" with it | | |
| Hive parasite | fluff cuts | lost (cut) | | |
| Broken hives by the mirrors | deep-and-mud §6r | moved (→ 0.2.0) | | |
| No native chase predators | sheet ban 3 | kept | | |
| No fungal miracle, no flowing water, no rain, no Earth life | sheet bans 5, 7 | kept | | |
| The oil boil | bedazzle review §8 (his card) | moved (→ 0.2.0) | | |
| The closing crown (weather that shuts routes) | bedazzle review §5 | lost (held off the card) | | |
| The Mooring | bedazzle review §4 | lost as pitched; its quiet half kept; `NEEDS HIM` | Not chosen 2026-10-02. | See "the ones I would look at". |
| The berth that costs a road | bedazzle review §5 | lost (folded into the Mooring, which was not chosen) | | |
| The pressure wedge; bough-grafting | bedazzle review §4, §5 | lost (not chosen) | | |
| Rites: the Gate Between, Cutting the Stilts, the Last Customer | bedazzle review §6 | lost (*"none, move on"*) | | |
| A Fever Wood heat kind, "ambient" | bedazzle review §1, §8 | lost | One sun from geometry, 2026-10-19. | |
| Sporefall, the treetop town; herd-groves; the wood-roads as infrastructure; the war's edges | sheet §8 | kept in the campaign layer | The biome mod places no settlement. | |
| The Wildsteam prefer it here; it is their home canton and it is quiet | sheet §5 | kept in the campaign layer | Whether they fight the Empire is unsettled. | |
| Wreck field and sounder readings | cleanse, Designer sheet | moved (→ 0.2.0) | | |
| Natural placement scorer | fluff cuts | lost (cut; no worldgen) | | |
| Natives drink their own water | Designer sheet (his words 2026-11-01) | kept | | |
| Arrival letter | cleanse | kept in "later" | The landing teaches. | |
| Mod Settings per feature | cleanse, walk | kept | Standing rule. | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature: shore temptation, rescue, remembered consequences | cleanse definition, owner_pages | kept as the core of 0.1.0; reframed for a visiting crew | It was the right centre, stated for a home. | |
| The cleanse's rescue rules (carrying is rescue; touching is not; reload keeps the clock; victims do not reset each other) | cleanse definition | kept (the scene's controls) | | |
| "Show water reach" overlay | cleanse definition | kept | | |
| Forty-colonist holding, season's turn, day one hundred | cleanse definition | lost | Colony-scale stories. The crew is five to seven. | Keep as a later-version check. |
| Four offline models (situations, geometry, timing, season) | cleanse models | kept, reshaped: the first three still serve; the season model is later | | |
| Forty-seven tickets, mostly switch-offs | cleanse tickets | kept as they stand, except those whose feature moved (listed under scope moves) | This design files nothing. | |
| Twenty-three old bars and eight new ones | Designer sheet, cleanse bars | kept as history; the ten promises in the design are the proposal to re-argue from | | |
| The judge's six coverage gaps | coverage verdict | kept as lessons: each promise in the design names its scene and its control | | |
| Stage argument, plan, journal | log, plan, journal | kept as history | | |
| The must-be-true list | walk | kept | It describes the build. | |

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**28 source files, 162 rows**, of which **30 lost**, **18 moved**, **15 kept, reshaped** and 1 folded into shared
machinery. Every one of the 28 files is named in at least one row's source column (checked by the same script).
Three further rows keep a plant and lose only its timber; they are counted as kept.

Read whole: the sheet; deep-and-mud; both rosters; the cast proposal; the Designer sheet and journal; the cleanse's
owner pages, definition and next-version list; the owner answers. Read in part (the sections named in the rows):
the bedazzle review; the syllable pass; the validation walk's must-be-true list; the rising note. Read by heading,
or parsed: the kit spec; the roster json; the names doc (Fever Wood lines); plan; log; the cleanse's ambiguities,
tickets, models and census; the coverage verdict; the tenant digest; fluff cuts and the experiences table (Fever
Wood lines). Not read: `record.json`, `tree.json`, `scenes.json`, `exam.json` and the exam run folders (pipeline
records of the older design; they hold no idea the sheet does not), and the Designer-codex notes and questions
beyond their headings.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_fever_wood.md`, `fever_wood_deep_and_mud_2026-09-23.md`,
`fever_wood_fauna_roster_2026-09-23.md`, `fever_wood_flora_roster_2026-09-23.md`,
`fever_wood_rm_cast_proposal_2026-09-24.md`, `fever_wood_syllable_variety_pass_2026-09-24.md`,
`feverwood_bedazzle_review_2026-10-02.md`, `kits/fever_wood_kit_spec.md`, `rosters/the_fever_wood.json`.

Not for deletion: the shared names doc (other biomes use it); `design/concepts/FeverWood/` (pipeline records; the
`cleanse/` proposal there is superseded by this design and should be re-run from it, not applied); the validation
walk (it describes the build); the campaign's tenant digest and rising note.

Before deleting: `the_fever_wood.md` is cited by path from `src/` comments and from the Designer sheet's pruning
lines; `CAMPAIGN_ARC_GATHER.md` cites deep-and-mud. Those references need repointing in the same change.
