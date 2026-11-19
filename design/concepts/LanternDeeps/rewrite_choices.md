# The Lantern Deeps: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A second reader, who did not write the design or this page, read every source to its end and checked the design
against it (item `RIMMANDRAKE_RECHECK_LANTERNDEEPS_TO_RUSTCATHEDRAL_CHOICES`).

**Rows added: 91**, in the section "Added by the second reader" below. The page now has 233 rows.

**The three most valuable things the first read missed**

1. **The fuel goes off in the cave.** The first pass and the cleanse both said the candler's wax item could not be
   found. It is the Blue Desert's wax, shared and built: safe only below freezing, and when it spoils it lights
   its own fuse. The cave is seventeen degrees. As built (read from the definitions, not seen live) fresh wax left
   in the cave has a couple of hours. Nobody chose this. It is now the design's `NEEDS HIM` 4, and the "milk run"
   is rewritten as a run for the cold.
2. **The Empire has been here, and the kyber trade is built.** His ruling of 2026-09-11 (card K1, in the kyber
   spec, which the first pass did not open): *"certainly the Empire is aware of it and could have mined some on an
   expedition."* Some of the well-provisioned dead are Imperial. And the kyber trade the first pass called "blocked
   elsewhere" was built on 2026-11-11: each sale raises the visibility number the search runs on.
3. **His own best lines about this place were in files nobody opened.** The legends he wrote on 2026-09-11 (*"it
   hums a half-beat after you speak — never with you, always after, like something learning the shape of your
   voice"*; droids that *"refuse in every language they own"*; the wiped droids that walk out), and the caverns
   note that named the lens two months early (*"Underground, it isn't in the building"*). They are quoted in the
   design now.

Also found: the hull-wear frame the ruling asked for exists and fits this place exactly (a ship at forty below
wears unless its cryo envelope is up; one field at a time; the envelope is meant to glow); the three GPT ideas
nobody took are named, from git history; the moment the first pass listed as "new, not in any source" (the Empire
arriving with the cable down) is the hoist design's own starred moment.

**What the second reader changed in the design, and why**

- *Timber removed.* The design sent the crew home with thrakk wood. Thrakk and vellok have given no wood since his
  card of 2026-10-17 (*"stop giving wood"*). Only the puffer is table food as built; the line that listed nurrik
  and brellik as food is corrected.
- *Fuel rewritten* around the built wax item (above), with `NEEDS HIM` 4.
- *Hull wear rewritten* to cite the built frame (`src/RimUtinni/ShipShields/`) and his shield rulings of
  2026-09-02 instead of pointing at the host. Nothing was invented. `NEEDS HIM` 5 asks whether the envelope's glow
  breaks the dark's cover.
- *The galuush's crowd taken out of the promises.* No gather-under-it behaviour is built.
- *"Built" corrected in two places:* the light draw today makes new drinkers beside the party (the walking hunter
  is owed); the host test is a list of biome names, not a temperature.
- *The kyber trade* moved from "blocked" to "built in the campaign layer, not seen live".
- *Carried in:* his K1 ruling on who came before; his full lines on light, collapse and persistence; the legends
  lines; the caverns note's two lines; the hoist's Open Line meter (its consequence here is `UNSETTLED`) and the
  Open-Line Raid; what the dead carry as built; the expedition loadout; the tame candler marked `UNSETTLED`.
- *Scope:* collapse as a tool, the wiped droids and the Open Line added to "later"; the dropped list gains the
  contracted-miner Orun-Ghal and the two legends he cut.

**One thing the second reader could not settle.** The grabber, the glowbulb, the shatterjaw and the chiller are
recorded as retired (cleanse census; they are absent from source). Three of them were his own remakes of
2026-09-18, with his words. The ruling that cut them was not found in the ledger or the items (the only trace:
`LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1` says he kept five other residents on a sheet of 2026-10-05, a sheet that is
no longer on disk). Their rows say "lost" and quote him.

**Ship ideas he declined or cut:** none found in these sources. The keel hoist was pitched here and he took it.

**Measured counts** (script: every table row under "Every idea, row by row"; outcome words counted in the "what
happened" column; an invented source name is reported missing, which shows the check can see absence): **233 rows,
91 added by the second reader, 29 lost, 20 record a move, 11 reshaped, 2 folded into shared machinery; 29 named
sources, each named in at least one row; 74 source files read in full.** Read in part only: the mechanics review
of 2026-10-22 (its Lantern Deeps section and table, whole; the other biomes' sections not), the scores doc and the
names doc (their Lantern Deeps sections), the shield source (three files whole, three by their header comments),
the Blue Desert source (the wax definition and the comp that sets it off). Not read: the kyber trade's source
(taken from its item and spec), and the sixty-odd other files under `design/` that mention the Deeps in passing
(mineral, art and migration records); none of them is one of the files proposed for deletion.

DELETE-READY: yes

That line covers the four files listed at the end of this page (the sheet, the review, the flora names, the roster
json), each now read to its end with a row for every idea found. The fauna proposals stay on hold as the first
pass said. Nothing has been deleted.

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
   campaign device and it is built (`src/RimUtinni/KyberTradePlot/`, 2026-11-11, not yet seen live): a sale raises
   the same visibility number the search runs on. It is outside these free-tier versions, so it stays "later"
   here, but in the campaign it is already a way to shorten a Deeps stop for money.
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
- **New, not in any source:** the split of cover into the ship's (the host's dark) and the crew's (a mountain), and
  leaving a party behind in a persistent cave. Both are readings of built behaviour and neither adds a mechanic.
  (The Empire arriving with the cable down is not new: it is the hoist design's starred "Open-Line Raid".)

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
| Cold wax softens, spoils and ignites when warm | fauna proposals §3, premise 2 | kept as a described cost; the reaction itself is "later" | It is built, in the Blue Desert's wax item (see the second reader's row and `NEEDS HIM` 4). | |
| Hush | fauna proposals | moved (→ 0.2.0) | Failed its last live check. | |
| Knocker | fauna proposals | moved (→ 0.2.0) | | |
| Sipper | fauna proposals | moved (→ 0.2.0) | | |
| Tapper: drains batteries; tame, gives aurora charge back | fauna proposals | moved (→ 0.2.0) for the drain; tame charging is "later" | Charging waits on the storm. | |
| Pooler | fauna proposals | moved (→ 0.2.0) | | |
| Blinker's flash | fauna proposals, fluff cuts | lost (removed 2026-11-02 under his "I cut, you veto" card); the plain animal stays | | |
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
| Its 40 tickets and the switch-offs | cleanse tickets | kept as they stand, except where a feature moved | | |
| Its eight proposed bars, four models, review and convergence records | cleanse bars, models | kept as history; the twelve promises in the design are the proposal to argue from | | |
| Retiring the donor renaming and eviction compatibility patches | cleanse owner_pages | kept as a recommendation, his to confirm | | |
| The scorecard of nine marks | review §2, scores | lost | A scoring frame from an earlier programme; its findings are kept row by row. | |
| "Everything at once" (his turn-1 build order) | review §7 | kept, reshaped: everything is in a bucket, not all in the first | The cleanse was authorised to choose a small first version. | |

### Added by the second reader, 2026-11-18

Rows for ideas the first pass had no row for, found by reading every source to its end. "Carried in" means the
second reader put it into `design.md`. More source names: *caverns design* =
`design/Jawa/proposals/underground_caverns_deep_design.md` (his rulings of 2026-09-02 are its table); *legends* =
`design/Jawa/worldbuilding/mindstone_arc_legends.md` (authored with him, 2026-09-11); *origin canon* =
`design/Jawa/worldbuilding/creatures/RUT_mechanoid_origin_canon.md`; *kyber spec* =
`design/Jawa/kyber_trade_plot_spec.md`; *shield design* = `design/Jawa/proposals/ship_shields_deep_design.md`;
*shield source* = `src/RimUtinni/ShipShields/`; *GPT consult* =
`Transient/bedazzle_gpt_enrich_2026-10-01/lanterndeeps.md` as it stands in git at `2c725462a0` (untracked since);
*verdicts* = `infrastructure/state/items/closed/DEEPS_FAUNA_VERDICTS_1.md`; *items* = the other ledger items named
in the row; *Designer notes* = `NOTES.md`, `QUESTIONS.md` and `record.json` beside the owner answers; *wax def* =
`src/RimMandrake/BlueDesert/Defs/ThingDefs_Items/RM_ColdWax.xml`; *flora def* =
`src/RimMandrake/LanternDeeps/Defs/ThingDefs_Plants/RM_DeepFlora.xml`; *scoping* =
`biomes/caverns_replacement_scoping.md`; *old walk* = `design/validation_walks/RimUtinni/LanternDeeps.md`.

#### The ship, the clock and the Empire

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "THE SHIP STAYS ON THE SURFACE — the design's soul": "No shields, no ship guns, no home-turf advantage... Everywhere else the Utinni is the answer to 'we're in trouble.' Underground, it isn't in the building." | caverns design §1 | kept, quoted; carried in | It is the lens, written two months before he named it. | |
| "Underground is the only place on Ash'karr where secrecy is free." | caverns design §0 | kept, quoted; carried in | It is the crew's half of the cover section in one line. | |
| The expedition loadout as its own decision: what the party carries down is everything. His note: "Air should only be needed when going into vapor-filled areas, or special mask filters." | caverns design §1 and ruled table | kept; carried in (the first day) | The Deep has still, breathable air; no air gear is promised. | |
| No power or supply link to the surface (the stated break from DeepRim): "Every trip down is a commitment, not a supply run" | caverns design §1 | kept, reshaped: the keel hoist is the one link, and it is paid for with the launch | The hoist was ruled a month after this line. | |
| Collapse as a tool: a deliberate collapse seals a pursuer behind the party or opens a shortcut, for good | caverns design §7; his row "collapse-hazard-tool", moved by him from v2 to v1 | kept in "later"; named in `NEEDS HIM` 1 | Unbuilt, and his note praises the warning half. | 0.2.0, as the crew's answer if the Empire ever comes down a shaft: one new job and a permanent hole in a saved map. |
| His words on collapse: "natural caverns that grumble and moan are great tension. Regions of instability should have animated bits of dust trailing down to warn the player, as well as some piled sand accumulating below." | caverns design ruled table | kept, quoted; carried in | The design had the paraphrase only. | |
| His whole line on light: "Light is what we bring because we need it, but in such great abundance compared to the local creatures we are like blazing beacons begging to be messed with." | caverns design ruled table | kept, quoted; carried in | The design had the last clause only, from the sheet. | |
| His words on persistence: "We don't want regenerating re-visit dungeons. If the game gets bogged down because of savegame size, we'll handle that later as its own issue. (and that will be pruning, collapsing mines, etc...)" | caverns design ruled table | kept, quoted; the save-size remedy is "later" | | |
| More kinds of mouth: animal burrows, lava tubes, "Weird cryotubes on the night side" | caverns design ruled table | lost from this design | They are other places' doors; of the Deeps' two he said "that's probably enough for now". | A cryotube mouth on a nightside host: a third entrance to build and dress. |
| Map chains, depth-banded ecology, the aquifer layer, underground settlements (heat refugees, droid enclaves, "something older"), new vault kinds, the cavern that is one organism ("Kinda feels like a sarlacc") | caverns design §3 to §6 | lost from this design | He ruled them dream or they belong to other sites; the cleanse adds no map chain. | |
| The flooded dungeon you pump out: "pump out the water, then go in to collect its eggs and other treasures from its lair" | caverns design ruled table | lost from this design | Another site's mechanic; nothing in a Deep is flooded. | |
| The hull-wear frame: one shield generator, one field at a time (heavy, thermal veil, light screen, cryo envelope); an unshielded ship on a map at forty below takes steady wear on its own structures; the cryo envelope answers it and slowly chills the inside | shield design (his rulings of 2026-09-02); shield source | kept; carried in, cited | His ruling says find the wear in the sources. Every Deep host is, by the injection rule, a map past the tracker's cold line. | Invent a Deep hazard that reaches up: against the brief, and against "Ship: nothing." |
| The cryo envelope glows: "allows the shields to start glowing with red-orange black body radiation" | shield design ruled table | kept as `NEEDS HIM` 5 | The glow is unbuilt, and the ship's only cover here is darkness. | |
| One field at a time: a ship set against the cold has no heavy field up | shield design, loadout row | kept; carried in (when the Empire arrives) | | |
| "Slow pressing things move through all shields is long-standing canon, including the crew." | shield design ruled table | kept as a rule the design leans on: no field stops a cable, a crew member or a pooler | | |
| The Open Line meter: a counter that climbs while the cable is down and brings a site's own trouble (noise, hostile interest, instability) | hoist design §2d, §7b | kept; carried in as `UNSETTLED` | The counter and its readout are built; "Consequences are wired per site later", and nobody has said what the Deep's is. | Wire it to the cave's attention in 0.2.0: the longer the line hangs, the more the cave looks up the shaft. |
| The Open-Line Raid: "reel in an incomplete load, defend a split expedition, or abandon cargo to save people" | hoist design §7a (starred moment 6) | kept; carried in | The first pass listed this as "new, not in any source". It is in the hoist design, starred. | |
| "throwing a dependable rope into an unknowable dark ... every use declares, 'We are staying here until this line comes back.'" | hoist design §7a | kept, quoted; carried in | | |
| The Last Descent: "an elder asks to be lowered into the Deeps with a treasured machine; a wall mark records it" | hoist design §7a (moment 28) | lost | Kept on the hoist's "worth keeping" list and never adopted. | A 0.2.0 crew moment: one request, one manifest line, one mark on a wall. Cheap, and it would be remembered. |
| The hoist first found dead inside the ship; "The Jawas own its culture (tallies painted on the drum, Ohm invoked before opening the line)" | hoist design §7a, §7b | lost from this design | It is the hoist's own opening, not the Deep's. The "Drumkeepers" layer was declined by an agent, not by him. | |
| What the cable carries: mass sets the cycle; power while it runs; colonists may ride awake (his ruling); downed strangers arrive prisoners and downed beasts arrive restrained | hoist design §2b, §6; hoist walk | folded into shared machinery | | |
| "Just have to be careful we don't get caught in endless animation development." | hoist design §1 (his brief) | kept as a build constraint | | |
| The first hoist pitch: a clamp above, a capstan below, hauling "mining rigs, dead droid chassis and oversized power cells that ordinary carriers cannot negotiate through the mouth"; no pawns or animals | GPT consult §2 | kept, reshaped by him into the campaign-wide hoist that carries both | Whether a slumped chassis can ride the cable as cargo is `UNSETTLED`: as built the Working Dead are buildings. | |
| Who came before: "a Helix expedition vessel could easily have explored it, and certainly the Empire is aware of it and could have mined some on an expedition. A rare Junker expedition might actually survive too." | kyber spec, card K1, ruled 2026-09-11 | kept, quoted; carried in | Some of the well-provisioned dead are the Empire's. It answers "who is down there" and bears on `NEEDS HIM` 1. | |
| The kyber trade is built: a sale raises the crew's visibility to the Empire (the one meter the search runs on), raises Hutt interest, can bring three farmers asking questions, and can open the donation | items (`KYBER_TRADE_PLOT_1`, built 2026-11-11, `src/RimUtinni/KyberTradePlot/`); kyber spec | kept, reshaped: the design now says it is a built campaign device, not seen live | The first pass called it "blocked elsewhere", from the review of 2026-10-01. | |
| The alleged Jedi who "never claims it"; the donation with "no reward, no Heat, no Rebellion"; "The reward *is* the register"; "they lost, that's it" | kyber spec §5, §6 | kept in the campaign layer, as built | | |
| The Empire's own traders never buy kyber; Hutt interest "is not friendship" | kyber spec §3, §4 | kept in the campaign layer | | |
| Selling a mindstone: the same heat as kyber, "plus the wild cousins' permanent text-register grudge" | origin canon §2; kyber spec §1 | kept in "later" | | |
| A mindstone found on the dead, "a prior expedition's find, still in its case", or given by the cousins; three to five in a campaign; "Holding one is holding a person who has never had a body." | origin canon §2 | kept in "later", quoted | Campaign. | |
| The cousins speak "through electronics: the player's own droids, a dead suit's speakers, a comms console carried into a Deep" | origin canon §3 | kept in "later" | It is how the first-version silence would one day break. | |
| The sentry factory is a site inside a Lantern Deep; restore it or refuse; a restore means "more anomaly for Imperial survey — a slow heat tick"; a Helix expedition follows | origin canon §4 | kept in "later" | Campaign; nothing here builds it. | |
| "The Rakata did not build minds; they grew them." The mechanoids "are grown minds in armor"; the Cathedral holds the wild kin "in the same regard a plantation holds a forest" | origin canon §1 | kept as campaign lore, quoted here only | Game-master register; no first-version text may say it. | |
| His words on the trickle: "To use them is to risk them, so it's kept at the most basic level that actually is slowly winding down. Especially now that the Empire is so close. There has ALWAYS been someone dangerous too close..." | origin canon §5 | kept in "later", quoted | | |
| The three kinds of machine (droid, mechanoid, Kindled); a mindstone head cannot be wiped or spiked; the names Forgotten Sentinels and the Kindled | sheet §8; origin canon §5 | kept in "later" | | |
| "Restore its 'true children' and it might no longer love its Free Droids quite so much." | sheet §8 (his words) | kept in "later", quoted | | |
| The ladder's own open questions (what a new landing resets, whether a rung may touch the ship, whether the bombardment destroys buildings) | ladder §8 | kept where they are | The pursuit's, not the Deep's. | |

#### The legends he wrote

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Dig deep enough under the Lantern Deeps and the stone begins to listen... it hums a half-beat after you speak — never with you, always after, like something learning the shape of your voice." | legends, entry I | kept, quoted; carried in | The best line written about this place, and the first pass never opened the file. | |
| Droids "turn at the shaft mouth and refuse in every language they own"; "Whatever the stone is listening for, the machines seem to fear it might be them." | legends, entry I | kept, quoted; carried in with the 0.2.0 droid moment | | |
| "Now and then one walks out. What crosses back into the light remembers nothing... the free camps are full of droids with no history and a habit of facing away from the nightside when they power down." | legends, entry II | kept in "later", quoted in the design | For a crew of droid dealers, stock that walks out of a hole with no owner is the most Jawa thing in the cave. | A wiped droid at the mouth in 0.2.0: needs the departure and the wipe, neither built. |
| "Nobody who tells this story got it from the droids. They got it from counting what comes out of a place nothing was sent into." | legends, entry II | kept, quoted here | | |
| The Working Dead "do not defend themselves. They mine." | legends, entry II (2026-09-11) | lost | His later words win: "I don't think the crystals are too keen mining" (2026-10-01) and the crystals "defend themselves with droid bodies" (2026-11-10). | |
| "The stone is afraid."; "Some swear the stone asks... plain as a beggar: *help us*. What you answer is your own business." | legends, entry IV | kept in "later", quoted here | Held by the late-game gate, in his words: "absolutely cut that the Junkers know the rust cathedral is alive or wants the crystals." | |
| The Forgotten Sentinels and the Making War | legends, entries III and V | kept where they live | Other places' stories. | |
| "speak like a traveler, not like Claude"; every entry re-voiced for whoever tells it; the table of who knows what | legends, header and scoping | kept as the rule for any later text here | | |
| No legend of the Kindled ("never made") and none of the True Children ("pure in-play discovery") | legends, scoping; items (`MINDSTONE_LEGENDS_ENTRIES_1`) | kept (dropped list) | Cut by him. | |

#### Animals and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The grabber in his words: "A small room-sized blob of pale yellow substance with a glass-like carapace, many small legs, and one large pincer-ending arm. Truly alien... Hold someone with its pincer and slowly crush them each round." | verdicts (2026-09-18) | lost, quoted | The census records it retired. The second reader could not find the ruling that cut it (see the note at the top). | Bring it back as the Deep's close-quarters horror: built once, hold and crush never fired live. |
| The shatterjaw: "A shiny black beetle, strangely conventional and out of place in this alien tunnel system." | verdicts | lost, quoted | As above. | |
| The glowbulb: "Make it actually glow." | verdicts | lost | As above. | |
| The soulchime in his words: "builds armor out of crystal shards it collects along the ground. Emits a powerful psychic stun on anyone that gets too close and alarms it. Taming one produces a soothing effect on those around it." | verdicts; items (`DEEPS_FAUNA_MECHANICS_1`) | kept dormant, quoted; powers 0.2.0 | The armour is built as a timer, not as collecting. | |
| The drinker in his words: "sacks that it uses to store drained body fluids. Strangely, if it drains any day-side races with normal warm iron blood, it becomes poisoned and rapidly dies." A killed drinker drops what it had drained. | verdicts; items (`DEEPS_FAUNA_MECHANICS_2`) | kept; the drop is a built product the design now names | | |
| The gembug: "Strangely beautiful rounded-jewel-like body with crab-like legs and eye-like spots around its body like a starfish"; a drafted new name, quozzik: "reads as a chip of the wall until it moves, weeps paraffin" | verdicts; names doc batch 5h | kept as a plain resident; the rename is a draft nobody ruled | | |
| The moss grub "oozing and curling along the tunnels"; the megapleura | verdicts | kept as dormant definitions | | |
| His art notes of 2026-10-05: "remove eyes" (drinker, soulchime, megapleura, moss grub); the gembug's "pale blue gems"; the blinker "three arms radiating out, legless and clumsy" | items (`LANTERNDEEPS_SHEET_ART_REDO_1`) | kept as art direction | | |
| A lamp the sippers have drunk is a smaller beacon: a crew that tolerates them is harder to find | fauna proposals §1 | kept with the sipper (0.2.0) | | |
| A tame string of drifters, "lanterns on a string", walked into a tunnel and shot | fauna proposals §2 | kept in "later" | A herd-bomb is a colony's weapon; it needs taming and time. | 0.2.0: very Jawa, and it would work on troopers. |
| The hush is "the one thing down here that does not glow": the lamp that calls the cave is also the only thing that shows it | fauna proposals §4 | kept with the hush (0.2.0), quoted in the design | It is the one animal that makes light a hard choice both ways. | |
| The tame pooler: "the only safe fire brigade in a cave full of methane" | fauna proposals §7 | kept with the pooler (0.2.0) | | |
| Follow a slick's trail to its warren; mop the slicks up as fuel "by anyone with a bucket and the patience"; a slick and a drifter in one tunnel | fauna proposals §11 | kept with the slick (0.2.0); the mopping was a stretch goal and is not built | | Fuel by bucket in 0.2.0: very Jawa, and one small job. |
| Under the galuush the fungi are fat and the animals gather | fauna proposals §9 | kept, reshaped: the lit chamber is promised, the crowd is not | Designer notes: no gather-under-it behaviour is built, and it is nearly still, not pinned to the roof. | |
| A lone shoal lozenge dies within the day; the joining filaments | fauna proposals §12 | lost | Never built (Designer notes). | |
| The knocker as a guide to which tunnels are safe to mine | fauna proposals §5 | kept with the knocker (0.2.0) | | |
| Do tamed Deep animals live away from the Deep? "tameable only in the Deep or in a Chiller's room, which is a stronger and stranger trade" | fauna proposals premise 12; review §3 ("the build's to measure, not to assume") | kept as `UNSETTLED`; carried in | The first pass promised a tame candler aboard without saying nobody has measured it. | |
| The proposals' other premises (an animal can tap the aurora, hear a roof, live in the seep, hang from a ceiling, be dark on purpose) | fauna proposals premises 7 to 11 | kept as lore | | |
| The candler's wax is the Blue Desert's wax: one item, spoiled above freezing and set off when it spoils; the cave is seventeen degrees | wax def; `RM_LanternDeeps_Hydrocarbon_Wave1.xml` header; census | kept, reshaped; carried in as `NEEDS HIM` 4 | The first pass and the cleanse both called the item missing. It is built, and as built the milk goes off in the cave's own air. | See the question. |
| Thrakk and vellok give no wood | flora def (his card of 2026-10-17: "stop giving wood"); census | lost; the design is corrected | The first pass sent the crew home with thrakk timber. | |
| Only the puffer is table food as built; "ossk tips", nurrik broth and candied brellik are dishes somebody would still have to make | flora names; flora def | kept in "later"; the design is corrected | | |
| Things a ship would carry off: the dried kuvra cone as "the cantina's glowing cup", zivvit as the table candle ("the way other people use flowers, or candles"), a lit bar-front of vellok, thrakk plate ware | flora names | kept in "later" | None has a harvest today. | A glowing cup to sell in 0.2.0: one item and one recipe, and exactly Jawa stock. |
| Brellik "draws animals to eat it": the sweet one, animal bait, feed for a live tank | flora names | lost | Never built as bait. | Bait for luring a candler to the cable: small, and a crew would use it. |
| The puffer "has no more mind than a heart valve"; a torn ball puffs; cut the tendrils and leave the ball; a bowl read three ways, "reverent, indifferent, revolted" | flora names | kept, the first quoted in the design | | |
| Quorr: "what the Deeps have instead of undergrowth" | flora names | kept as flavour | | |
| The naming rules and the two alternates for every plant | flora names | kept as a record | A reason to keep that file's table if a name is ever challenged. | |
| The puffer's ball as the one rounded shape in a cave of facets; paint blue and let the tint make violet | flora names, art brief | kept as art direction | | |

#### What is built, and what the other readers found

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The host test as built is a list of biome names in the settings, not a temperature | items (`LANTERNDEEPS_RM_MOD_BUILD_1`, false-statement finding); cleanse ticket T24 | kept as a build fact; the design now says so | | |
| The Deep as built: a pocket 66 cells square, seventeen degrees, six ordinary diseases | census; items (`LANTERNDEEPS_RM_MOD_BUILD_1`) | kept as build facts | | |
| The loot as built: aged mercenary corpses, components, plasteel, medicine, chemfuel, slumped chassis; one old soldier and rubble at a shaft; a wreck field of nightside hulls, tanks and rigs | census | kept; carried in | Honest about what a first party finds today. The Imperial and Helix dead of his K1 ruling are not dressed. | |
| The light draw as built makes one or two new moths beside the party | census; cleanse review | kept as a build fact; the design's scope line is corrected | The design promised a hunter on a real route and called it built. | |
| Sealing a mouth: the base game's own command, with its warning that people and things below are lost | census | kept | | |
| A deep drill inside the Deep takes lanternstone without touching a wall, so it goes round the gallery's defenders | cleanse review ("missed capability") | kept as `UNSETTLED`, with a default | It is how a Jawa would do it. | Let it stand as the clever way round: the gallery stops being a choice. |
| A glowing animal that wanders into Lantern light makes it ordinary light | cleanse review | kept as `UNSETTLED` | | |
| With the wrong-blood death on, every drinker that feeds on the crew dies, so lamp work empties the cave of its only hunter | cleanse review | kept as a caveat on that 0.2.0 item | | |
| Whether animals ever come back to a pocket map | cleanse review | kept as `UNMEASURED` | | |
| The Answering was built on 2026-10-09 and then moved to the next version by him; its found sign is a chassis scratching "the cousins' terms, half-legible" into a wall; its good outcome is a droid's log holding "one line it did not write" | items (`LANTERNDEEPS_ANSWERING_RITE_BUILD_1`); review §6 | kept in "later", quoted | | |
| The Nine Faults inscription: "a dead droid with nine wires crossed" | review §5; GPT consult §5 | kept where it is specified | | |
| The three GPT ideas nobody took, by name: Ithrix, the bench that remembers ("a dead specialist can leave behind one precious, imperfect lesson"); Nhal, the standing note (a hum that draws its own shape in the dust, steered with baffles); Orun-Ghal as a contracted miner whose route the player paints | GPT consult §1, §3, §4 | lost | Not taken; the third he turned down in words ("it might not just mine"). The first pass could not name them. | Ithrix in 0.2.0 would give lanternstone a use no other stone has; a medium build. |
| "An underground weather could be air that changes: cold breath, crystal-song surges"; a vigil in the dark before the aware stone | scores | lost | Never taken. | |
| The nine questions drafted for him, and the first scene nobody picked (the dead stand, then the suit; or the galuush and a roof; or a settled camp) | Designer notes | kept as history | The design's first minutes are the first of the three. | |
| The suit's draft lore that "the minds welcome the colony" | Designer notes | lost | An agent's draft, never his. | |
| The cleanse's small print: a crowd does not multiply the light risk; a destroyed crystal visibly lets its shells go; the greeting never interrupts urgent work; what the crew used up stays readably used up | cleanse definition; cleanse bars | kept | | |
| The mindstone gallery and the two recipes that make a mindstone head exist in the campaign layer | Designer notes; items (`MINDSTONE_MATRIX_KINDLED_BUILD_1`) | kept in "later", as built | | |
| Whether the five old Star Wars-tier copies of the residents are deleted or kept | items (`LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1`) | kept as an open item | | |
| The donor years: the borrowed Caverns biome, its parity build, the two tiers colliding in one folder, the first predator being a cave spider | items (`CAVERNS_PARITY_BUILD_1`, `LANTERNDEEPS_TIER_COLLISION_1`, `LANTERN_DEEPS_INJECTION_1`); scoping; old walk | lost | Done work. The old walk describes the retired mod. | |

## Sources read by the first pass, and its count

(The second reader's reading and counts are at the top of this page. What follows is the first pass's own record:
what it read in part is why the second reading was needed.)

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

Also his to call (the second reader's addition): `design/validation_walks/RimUtinni/LanternDeeps.md`, a walk that
its own header marks RETIRED because it describes the mod before it was rebuilt. And one loss to know about
before `lantern_deeps_flora_names.md` goes: its table of two alternate names per plant has no other home but git.

Hold this one until the 0.2.0 animals are built and proven, because it is their only full specification (visual
briefs, niches, trades): `rosters/lantern_deeps_repopulation_proposals.md`.

Not for deletion: the shared names doc and scores doc; `design/concepts/LanternDeeps/cleanse/` (superseded by this
design, never applied; it should be re-run from this file, not applied); the campaign story documents listed above;
the hoist design and walk.

Before deleting: `the_lantern_deeps.md` §8 is the frozen home of the mechanoid-origin and kyber-trade rulings and
is cited by the Rust Cathedral's sheet and by the campaign canon files. The second reader checked: the
mechanoid-origin rulings are in `RUT_mechanoid_origin_canon.md` (§0, §3, §4 and the ruled cards of §5, with his
words), and the kyber law and its two ruled cards are in `kyber_trade_plot_spec.md`.
