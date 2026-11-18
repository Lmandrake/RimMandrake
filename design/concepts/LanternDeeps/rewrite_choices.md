# The Lantern Deeps: what the rewrite chose, what it lost, and why

Companion to `design/concepts/LanternDeeps/design.md`, written 2026-11-18 by the same pass. Its job is to let the
older files be deleted without fear: every distinct idea found in any source has a row saying what became of it.
Nothing has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien things at close range is *"the
overriding priority"*. And his later test: *"you should always look for solutions that make you say Very Jawa."*

The Deeps bent to the lens in one large way and several small ones. The large one: **the ship cannot go down**, so
the stop is a ship parked on a frozen surface with its crew underground, and the cleanse proposal's colony that
"returns" over seasons becomes a crew that descends many times in one stop and may land here again. The Deeps were
also already the most Jawa place on the planet without anyone having said so: a cave full of the finest abandoned
equipment in the world, guarded by its own stock. The cleanse of 2026-11-17 chose its signature well (light draws
attention; the dead machines reveal minds; greet or rob) and this design keeps it whole. What changed is what
surrounds it: the cleanse switched off nearly every animal's special behaviour to keep one signature, and under the
lens the animals' behaviours *are* the "did you see that", so the funniest built ones come back in at 0.1.0 or
0.2.0.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The cousins who talk.** *"They may talk to the player, asking for help and defense against 'the insane
   enslaved one'"*, the Rust Cathedral. It is the owner's own plot, the best idea in the sheet, and it is the
   direct answer to his lens question "who else hates the Empire and might fight them?" turned sideways: here is
   somebody who hates someone else. It stays in "later" because its canon rulings make it late-game knowledge
   (*"nobody in-world... knows the Cathedral is alive"*). A first-version hint would cost one line of text from a
   studied suit and would break that knowledge gate.
2. **Crew droids that stop and listen.** *"Living droids act strangely or simply stop near mindstone and avoid the
   Deeps at all costs."* For a crew of droid dealers this is the first-descent moment. Built. I moved it only to
   0.2.0 because a fresh review refused it as a default (it also halts a player's mechanoids). Asked as `NEEDS HIM`.
3. **The kyber trade.** Selling kyber is *"extremely illegal to the Empire"* and raises its attention with every
   sale. Under the lens it is a dial on the pursuit clock that the player turns for money: very Jawa. It is a
   campaign device blocked elsewhere, and it stays "later".
4. **The Creep.** *"Grows over what sleeps near it."* A crew that naps at the shaft bottom and wakes half crusted is
   slapstick with a rescue in it. Built, never proven, failed its last live check. 0.2.0, not 0.1.0.
5. **The galuush's roof.** The proposal's full trade is *"one spark during the kill collapses the landmark on
   everyone under it."* I moved the detonation into 0.1.0 and left the forced roof fall in 0.2.0, which halves the
   set-piece. If the half reads tame, move the roof in with it; the cost is one more thing the first version must
   prove fair.
6. **Sowing lanternstone**, *"a light that grows home with you"*. It is exactly what a ship carries away, and
   growing a crystal is a colony's pace. "Later"; the sale of a standing Lantern carries the trade for now.
7. **The forty-colonist home and the "season's turn" story** of the cleanse. Lost as a frame: nobody in the
   campaign lives here. Its good parts (the same injured animal, the excavated face, depletion staying visible)
   are kept as the persistence promise.
8. **The deeper giant** that makes the party *"find another route"* (his answer of 2026-11-10). No candidate was
   ever chosen, so there is nothing to place; it is "later" and still his.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Drifter and galuush ignition when killed hot:** next version → 0.1.0. Built, and its two live checks passed on
  2026-10-05 (the only animal behaviours that did). It is the stop's best slapstick and it has counter-play: use a
  blade.
- **Galuush blast forcing its roof down; formations that explode when damaged:** next version → 0.2.0.
- **Hush, sipper, tapper, pooler, slick:** next version → 0.2.0. Each attacks one thing a visiting crew carries
  (a lone walker, lamps, batteries, heaters, a clean corridor). They are creature moments, not colony systems.
- **Drinker's wrong-blood death; soulchime's powers:** next version → 0.2.0.
- **Knocker's drumming and the tame knocker's longer warning:** next version → 0.2.0.
- **Creep engulfing; Cleavers splitting:** next version → 0.2.0.
- **Aurora surge:** next version → 0.2.0, and it waits on a host storm that does not exist yet.
- **Shoal's shared wounds; scanner echoes; bonus study rewards:** next version → 0.2.0.
- **Crew droids stop and listen:** next version → 0.2.0 (see above).
- **Stayed "later" from the cleanse's "next version":** the psychological Chorus, crystal maturation, the mindstone
  and the Kindled, droid departure, the cousins' story, the kyber trade, the Answering, the passage giant, added
  minerals, the warm-wax reaction, the orange crystal. Not moves.
- **New, not in the cleanse:** the keel hoist's line and tether lock as a 0.1.0 promise of this place (built in its
  own mod; first pictured at a Deep mouth). The cleanse's edge list said only "no underground gravship transfer",
  which stands.
- **New, not in any source:** the split of cover into the ship's (the host's dark) and the crew's (a mountain); the
  Empire's arrival catching part of the crew below with the cable down; leaving a party behind in a persistent
  cave. All three are readings of built behaviour and none adds a mechanic.

## Every idea, row by row

Source names: *sheet* = `biomes/the_lantern_deeps.md`; *review* = `biomes/lanterndeeps_bedazzle_review_2026-10-01.md`;
*fauna proposals* = `biomes/rosters/lantern_deeps_repopulation_proposals.md`; *flora names* =
`biomes/lantern_deeps_flora_names.md`; *roster json* = `biomes/rosters/the_lantern_deeps.json`; *names doc* =
`biomes/noncanon_beast_names_propane_arid_forge_pyre_fever_greentide_rust_lantern_blue.md`; *scores* =
`biomes/grandfathered_bedazzle_scores_2026-10-01.md` (all under `design/Jawa/worldbuilding/`); *cleanse* =
`design/concepts/LanternDeeps/cleanse/`; *owner answers* = `design/RimMandrake/designer_codex_2026-11-09/LanternDeeps/ANSWERS_OWNER.md`;
*mechanics review* = `design/RimMandrake/special_mechanics_review_2026-10-22.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*hoist design* = `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md`; *hoist walk* =
`design/validation_walks/RimMandrake/KeelHoist.md`; *ladder* = `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "A blue lantern burning under the mountain, and a dead miner's suit walking toward it" | sheet header, §9 | kept, quoted | | |
| Thematic handle: light that is alive | sheet header | kept | It is why a lamp costs something. | |
| Not a world-map biome; an injected underground layer | sheet header, ban 1 | kept; stated first, as the kind of place | The brief asked each biome's kind to be checked. | |
| Injection only under hosts at −40 °C or colder | sheet §0, ban 2 | kept | | |
| Measured tiles and the re-homing of the old highland | sheet §0 | lost | A tile count is never evidence; the planet is painted at the end. | |
| Donor inventory (calm weather, densities, the fungal carpet, growing crystals) | sheet §0 | kept as build facts, not design | | |
| Slow cold crystallisation grows big; the voids are the Deeps | sheet §1 | kept | | |
| "Nothing here has a body in the ordinary sense... they wear what the dead brought down" | sheet §1 | kept, quoted | | |
| "Nobody reaches this place without excellent technology; that is why the caverns are full of it, walking" | sheet §1, §3 | kept, quoted; made the crew's reason to come | Finest salvage on the planet, guarded by itself: very Jawa. | |
| Energy from the aurora's ground currents; matter from seeping solutions | sheet §2 | kept as lore | | |
| Piezoelectric nerves, accretion, cleaving as birth, photonic metabolism, resonance, the shatter | sheet §3 | kept as lore; no simulation | The cleanse reached the same call. | A crystal energy simulator: large, and invisible in a visit. |
| "Your lamps are a feast... we are blazing beacons begging to be messed with" | sheet §3 | kept, quoted | | |
| Darkness as the standing condition; no free light | sheet §4b, ban 6 | kept | | |
| Calm only; the hum | sheet §4b | kept | | |
| Collapse with dust trails, sand piles, the grumble | sheet §4b | kept (roof warnings, 0.1.0) | | |
| Geonosian sonic does not trigger collapse | sheet §4b | lost from this design | A cross-reference to another faction's weapon; no visit shows it. | Keep as a build note; free. |
| Persistent: the same cavern every visit, never regenerated | sheet §5, ban 5 | kept, reshaped: "every visit" is every descent in a stop, and every later landing | The ship leaves; the cave does not. | |
| Lanternstone glows; kyber is quiet; the mindstone is aware | sheet §5 | kept for lanternstone; the other two are "later" | | |
| The Rakata mined here; later parties tried; the Junkers usually fail | sheet §5, §8 | kept, reshaped: the crew is the next party to try | It is the textual basis for "in over their head" here. | |
| "Maybe a very rare Junker with a death wish" | sheet §8 (legends) | kept, quoted | | |
| No poorly equipped remains | sheet ban 7 | kept, as the fake that rules out the loot promise | | |
| The two mouths: the open geode and the shaft in ruined works | sheet §8 | kept | | |
| "Every crystal mouth leads to a Lantern Deep" | sheet §0 | kept; each mouth has its own Deep | The cleanse settled it that way. | |
| Recognisability rule; the vulptex protected and not imported | sheet ban 8 | kept as a build constraint | | |
| Art theme: light, palette, silhouettes, sound | sheet §9 | kept as art direction; three lines quoted | | |
| Experience line: "A deep wondrous cavern... Mineral riches for kings, until you realize they are both alive and intelligent." | experiences, mechanics review | kept, quoted | His typed line. | |
| "Riches for kings" as temptation, not a price | cleanse definition | kept | A bar is an experience. | |
| A steady room temperature under a killing surface | review §1, cleanse | kept as ordinary air temperature | One sun from geometry; no heat of its own. | |
| The Deeps under each host tuned for density and kyber richness | sheet §0 | lost | Per-host tuning is a number, and kyber is later. | |
| Host selection setting, unsupported outside the cold hosts | cleanse definition | kept (settings) | | |

### Light, the dead and the minds

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Carried light draws a native predator to the brightest person | sheet §5, review §1 | kept | The signature's approach. | |
| The draw recruits only an existing reachable hunter; a readable quiet cave if none | cleanse owner_pages, definition | kept | Nothing appears from nowhere. | |
| Risk inspectable as quiet, building, drawn, cooling | cleanse definition | kept | | |
| On the free tier the light drew nothing (the predators' names were campaign-only) | review finding 1 | kept as history; the port it asked for is done | | |
| The Lantern: the only safe light; "light now" against "light later, sold" | sheet §4, review slate 2 | kept, quoted | Selling the one safe lamp is the most Jawa decision in the cave. | |
| "Safe" means only exempt from the light draw | cleanse ambiguity 11 | kept | | |
| Real occlusion and mixed sources decide, not nominal radius | cleanse ambiguity 12 | kept, in the promise's "fake" column | | |
| A naturally placed Lantern a first party can find | cleanse ambiguity 13 | kept | Sowing is a colony's route. | |
| Sowable lanternstone | scores, cleanse | moved (cleanse first version → later) | Growing a crystal to size is not a visit. | Keep in 0.1.0 as a thing to carry off and plant: cheap, and unseen. |
| The well-provisioned dead placed along galleries and shaft bottoms | sheet §3, review finding 3 | kept | The loot the stop is for. | |
| The Working Dead: chassis that stand, work and turn to light | sheet §8 (legends), review slate 1 | kept | Proven inside a placed Deep, 2026-10-05. | |
| They worry at rock without mining it | cleanse ambiguity 19 | kept | *"I don't think the crystals are too keen mining."* | |
| The Shard-minds: immobile, aware, speaking through electronics | sheet §4 | kept as the aware crystals; "speaking" is by bodies, not dialogue | No first-version dialogue reveals the campaign story. | |
| Control through the crystal network within a finite reach | cleanse ambiguity 15 | kept | | |
| Crystals defend themselves with remote droid bodies | owner answers 1 | kept, quoted | His words; unbuilt; the largest piece of 0.1.0 work. | |
| The protected gallery: marked on selection, provoked only by extraction or damage | cleanse owner_pages | kept | Counter-play before the first block. | |
| The protected lanternstone must be an expedition-worthy prize | cleanse owner_pages | kept as "the prize worth the trip"; no value pinned | | |
| Defenders stay with their gallery; the retreat stays open | cleanse owner_pages, ambiguity 18 | kept | | |
| A friend of the suit is warned the same as a stranger | cleanse definition | kept | | |
| Orun-Ghal: the living mining suit with the skeleton in it | review §5 (his words) | kept, quoted | | |
| Never a miner, boss, worker or recruit | review §5, cleanse | kept | | |
| Studied by real visits; acquaintance belongs to the colony | cleanse ambiguities 20, 21 | kept, reshaped: it belongs to the crew | | |
| The greeting and chosen company | owner answers 2 | kept, quoted | Unbuilt. | |
| Drawn huge on an ordinary footprint | review §5 | kept as a build note | | |
| Living droids stop and listen near a mind | sheet §8 (legends), mechanics review | moved (cleanse next version → 0.2.0); `NEEDS HIM` | See "the ones I would look at". | |
| Droids that leave exit mind-wiped and go rogue | sheet §8 (legends) | kept in "later" | Campaign. | |
| The Chorus: a hum with a psychological effect | sheet §4 | kept in "later"; the sound stays | Unbuilt as an effect. | |
| The servo click and the shatter as sounds | sheet §9, review §1 | kept as art direction | | |
| The Creep | sheet §4, review slate 4 | moved (→ 0.2.0) | | |
| The Cleavers, moving by fracture; "the caverns' true danger" | sheet §4 | kept as a plain predator in 0.1.0; splitting moved (→ 0.2.0) | | |
| Cleaving as birth: formations that mature and shed offspring | sheet §3, cleanse | kept in "later" | Unbuilt; slow. | |
| Volatile formations that blast when damaged | review §1, cleanse | moved (→ 0.2.0) | A second hazard for miners; fair only with the knocker and warnings proven. | |
| Lanternstone as blasting material | sheet §7 | kept as a trade description; no recipe promised | Not found built as a product. | |
| The aurora storm as a feast day | sheet §3, review slate 5 | moved (→ 0.2.0) | Needs the host's storm. | |

### Animals and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Crystals AS creatures"; no crystal-studded animals | sheet §0, ban 3 | kept (dropped list) | His ruling. | |
| "More truly alien hydrocarbon-based life forms... utterly different than anything on the dayside" | fauna proposals (his words) | kept | It is what "never THIS close" looks like for a desert crew. | |
| The house register: pale blue skin, yellow hydrocarbon fluids | fauna proposals, review §3 | kept as art direction | | |
| All twelve admitted, every one a hydrocarbon organism | review §3, §7 | kept as bodies; powers by bucket below | | |
| Hydrocarbon animals are not food | fauna proposals premise 3 | kept | Ruled 2026-10-01. | |
| Older insect ports keep their own biology | cleanse ambiguity 24 | kept | | |
| Galuush: the ceiling sun, one per Deep | fauna proposals §9 | kept, quoted | | |
| Galuush as a methane bomb | fauna proposals §9 | moved (ignition → 0.1.0; forced roof fall → 0.2.0) | | See above. |
| "The yolk is now called galuush" | review §3 (his words) | kept | | |
| Drifter: explodes if killed by fire or spark | fauna proposals | moved (→ 0.1.0) | | |
| Candler: milked for cold wax | fauna proposals §3 | kept, quoted | The fuel ruling of 2026-11-18. | |
| Cold wax softens, spoils and ignites when warm | fauna proposals §3, premise 2 | kept as a described cost; the reaction itself is "later" | Whether it is built is unknown to the cleanse. | Promise it in 0.1.0: needs the missing wax definition found first. |
| Hush | fauna proposals | moved (→ 0.2.0) | Failed its last live check. | |
| Knocker | fauna proposals | moved (→ 0.2.0) | | |
| Sipper | fauna proposals | moved (→ 0.2.0) | | |
| Tapper: drains batteries; tame, gives aurora charge back | fauna proposals | moved (→ 0.2.0) for the drain; tame charging is "later" | Charging waits on the storm. | |
| Pooler | fauna proposals | moved (→ 0.2.0) | | |
| Blinker's flash | fauna proposals, fluff cuts | lost (removed 2026-10-23); the plain animal stays | | |
| Chiller: a freezer with no power | fauna proposals, cleanse | lost (retired with the early ports) | The census lists it removed. | Bring it back as the cold hold's animal: the candler's natural partner, and a new build. |
| Slick's fuse trail | fauna proposals, fluff cuts | moved (→ 0.2.0) | Fluff cuts kept it as a real decision. | |
| Shoal's shared circulation | fauna proposals | moved (→ 0.2.0) | | |
| The ecology chains (sipper to shoal to hush; candler with chiller) | fauna proposals summary | kept as intent for 0.2.0; the candler-chiller pair is lost with the chiller | | |
| Noise draws the Deep as light does | fauna proposals premise 6 | lost | Never ruled, never built. | A second attention channel: doubles the signature's test surface. |
| Animals that drink light | fauna proposals premise 5 | kept (the sipper, 0.2.0) | | |
| Drinker: the pale moth that drains; flight | review §1 | kept | The light draw's hunter. | |
| Drinker's wrong-blood poison and death | cleanse next_version | moved (→ 0.2.0) | | |
| Soulchime: stun, soothe, shard armour | review §1, cleanse | moved (→ 0.2.0); the dormant body stays | | |
| Gembug, megapleura, moss grub | review §1, roster json | kept as plain residents or dormant definitions | No restoration or eviction (evictions are stopped). | |
| Glowbulb, grabber, shatterjaw (early local ports) | review §1, cleanse | lost (already retired) | | |
| Glowbulb also in the Fever Wood | review §1 | kept as a note for that biome's sheet | Evictions are stopped. | |
| The grabber as the largest animal before the galuush | review §2 | lost with the grabber | | |
| Roster json's three host names and two import rows | roster json | kept as build facts | | |
| No fish; no standing water to speak of | roster json | kept | | |
| Moth and beetle names | names doc | kept | | |
| New names for the fungi, "in the style of Star Wars", no canon lookup | flora names (his words) | kept | | |
| Thrakk cap, ossk bramble, vellok reed, prenna lace, mycelium, nurrik gill, quorr fern, zivvit taper, kuvra spout, brellik bulb | flora names | kept | | |
| The twitching puffer: "a big swollen ball with small tentacles growing out of it" | flora names (his words) | kept | | |
| "The squirming bowl that is not alive" | flora names | kept, quoted | A crew dinner joke. | |
| A torn puffer puffs a stinging spore cloud | flora names | kept as fiction; not promised | Not found built. | |
| Dulcis leaves the Deeps | flora names (his words) | kept (dropped list) | | |
| Cuisine roles for each fungus; the cantina's Deep lane | flora names | kept in "later" | The combining kitchen is not a stop. | |
| Deep flora regrows in play | review §1, cleanse | kept | | |
| The rename's execution notes and grep census | flora names | lost | Done work. | |

### Minerals, plot, rites and the ship

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Kyber: "the reason the Rakata came"; mineable formations | sheet §3, §7 | kept in "later" (campaign) | Franchise minerals stay off the free tier. | |
| Kyber is crafting material only; no Force route | sheet ban 4 | kept (dropped list) | | |
| Selling kyber is extremely illegal to the Empire; the Hutts' interest rises | sheet §7, §8 | kept in "later" | See "the ones I would look at". | |
| The "alleged" Jedi and the donation smuggled offworld | sheet §8 | kept in "later" | Campaign plot with its own spec. | |
| The orange glowing crystal from an import | sheet §7 | kept in "later"; its source is unidentified | | |
| Stygium and pyrinth scatters | review §1, cleanse | kept in "later" | | |
| Off the Deep, drills give steel instead of lanternstone | mechanics review | kept as a build fact | | |
| The mindstone: a droid mind made of it is a new race | sheet §4, §8 | kept in "later" | | |
| The mechanoid origin: wild cousins, "the insane enslaved one" | sheet §8 | kept in "later" | See above. | A hint in 0.2.0: breaks the knowledge gate. |
| The facility's trickle, the secret caches, "To use them is to risk them" | sheet §8 | kept in "later" | | |
| The Kindled have never been made | sheet §8 (legends) | kept in "later" | | |
| The knowledge gate: nobody knows the Cathedral is alive | sheet §8 (legends) | kept; it is why the cousins stay silent in these versions | | |
| The Answering rite | review §6 | kept in "later" | He tabled rites on 2026-10-03. | |
| Nine Faults inscription found here | review §5 | kept where it is specified (another document) | | |
| Rites not taken (a vigil before the mindstone; the dead's gear) | review §6 | lost (not taken) | | |
| GPT's other three ideas | review §5 | lost (not taken) | | |
| The keel hoist, first pictured at a Deep mouth | review §5, hoist design | kept; folded into shared machinery and promised here | Built since. | |
| The tether lock: no launch with the cable down | hoist walk | kept | It is the Deep's whole relationship with the ship. | |
| Downed beasts ride the cable restrained | hoist walk | kept | A candler in a sling is how the cow reaches the hold. | |
| "Ship: nothing. A gravship cannot enter a pocket map." | review §1 | kept, quoted; no hull wear invented | The ruling says find it in the sources. | Invent a Deep hazard that reaches the ship: against the brief. |
| "Gods: nothing" | review §1 | kept | | |
| The scanner's echoes and hidden voids | cleanse | moved (→ 0.2.0) | | |
| The deeper giant: find another route | owner answers 3 | kept in "later" | | |
| Probe sight is short on unlit ground | ladder, pursuit source | kept as the reason the host's dark matters | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (light draws attention, machines reveal minds, greet or rob) | cleanse owner_pages, definition | kept whole as the core of 0.1.0 | | |
| Its runner-up, a managed light economy | cleanse definition | kept in 0.2.0 as the sipper and friends | | |
| "Returning with consequences still there" | cleanse owner_pages | kept, reshaped: descents within a stop, and a later landing | | |
| A colony of forty; the season's turn; the ordinary week | cleanse definition | lost | Colony scale. | |
| Its four stories | cleanse definition | kept, reshaped into the visit sections | | |
| Its 32 delegated decisions | cleanse ambiguities | kept; twelve are cited above | | |
| Its 40 tickets and the switch-offs | cleanse tickets | kept as they stand, except where a feature moved | Not read. | |
| Its eight proposed bars, four models, review and convergence records | cleanse bars, models | kept as history; the twelve promises in the design are the proposal to argue from | Not read. | |
| Retiring the donor renaming and eviction compatibility patches | cleanse owner_pages | kept as a recommendation, his to confirm | | |
| The scorecard of nine marks | review §2, scores | lost | A scoring frame from an earlier programme; its findings are kept row by row. | |
| "Everything at once" (his turn-1 build order) | review §7 | kept, reshaped: everything is in a bucket, not all in the first | The cleanse was authorised to choose a small first version. | |

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**15 source files, 142 rows**, of which **14 lost**, **20 record a move** (whole or in part), **6 kept, reshaped**
and 1 folded into shared machinery. Where a moved row has no reason beside it, its reason is its line under
"Scope moves". Every source is named in at least one row's source column (checked by the same
script; the cleanse files count under the one name "cleanse").

Read whole: the sheet; the review; the owner answers; the cleanse's owner pages. Read in part, with what was
skipped: **the fauna proposals** (`rosters/lantern_deeps_repopulation_proposals.md`: read the header, the candler,
the galuush, the summary table of all twelve and premises 1 to 8; not read: the other ten animals' full sections
and premises 9 onward); **the flora names** (`lantern_deeps_flora_names.md`: read the rulings, the names table and
the puffer's fiction; not read: the def and art briefs, alternates, execution notes); **the cleanse definition**
(`cleanse/definition.md`: every paragraph's first 700 characters; the tails of long paragraphs were cut);
**the cleanse next-version list** (`cleanse/next_version.md`: the first seven entries, each cut at 330 characters;
the rest taken from the owner pages' list and the census); **the cleanse ambiguities** (`cleanse/ambiguities.md`:
the 32 numbered decisions, each cut at 260 characters; not read: the three closing sections); **the cleanse
census** (`cleanse/census.json`: every row's name, built, proven and fate; not its evidence text); **the mechanics
review** (its Lantern Deeps table, rows cut at 420 characters); **the hoist design** (first 40 lines); **the hoist
walk** (its must-be-true list); **the names doc** and **the scores doc** (their Lantern Deeps sections, first
lines); **the roster json** (first 80 lines); **the ladder** (sections 1 to 4); experiences and fluff cuts by
search. **Not read at all:** `cleanse/tickets.md`, `bars.json`, `models.md`, `review.json`, `converge.json`,
`fixes.json`; the Designer record and notes in `design/RimMandrake/designer_codex_2026-11-09/LanternDeeps/` other
than the owner answers; and the documents the sheet points to for the campaign story
(`underground_caverns_deep_design.md`, `kyber_trade_plot_spec.md`, `mindstone_arc_legends.md`,
`RUT_mechanoid_origin_canon.md`, the Nine Faults rite), whose content this design leaves in "later" untouched.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_lantern_deeps.md`, `lanterndeeps_bedazzle_review_2026-10-01.md`,
`lantern_deeps_flora_names.md`, `rosters/the_lantern_deeps.json`.

Hold this one until the 0.2.0 animals are built and proven, because it is their only full specification (visual
briefs, niches, trades): `rosters/lantern_deeps_repopulation_proposals.md`.

Not for deletion: the shared names doc and scores doc; `design/concepts/LanternDeeps/cleanse/` (superseded by this
design, never applied; it should be re-run from this file, not applied); the campaign story documents listed above;
the hoist design and walk.

Before deleting: `the_lantern_deeps.md` §8 is the frozen home of the mechanoid-origin and kyber-trade rulings and
is cited by the Rust Cathedral's sheet and by the campaign canon files. Those rulings should be confirmed present
in `RUT_mechanoid_origin_canon.md` and `kyber_trade_plot_spec.md` first (not checked by this pass).
