# The Chill — routes into the ancient war lab (spec, 2026-09-27)

Status: DESIGN SPEC — commissioned by `CHILL_WARLAB_ROUTES_1`. Prose-first; build items
spawn from this spec, not from the item. Written against the frozen origin sheet
(`the_propane_lakes.md`), the flora pass
(`the_propane_lake_flora_pass_2026-09-27.md`), and the three mechanism items this
plugs into: `CHILL_FIRE_BAN_1`, `CHILL_WORLD_CRATER_1`, `CHILL_GARDEN_DEFENSE_1`.
The biome is **the Chill** (owner, 2026-09-27); defNames below are proposals in the
tier grammar and rename with `CHILL_RENAME_FULL_1` like everything else.

## The commission

The owner's route map, typed 2026-09-27, is LAW and is quoted here once:

> "There are several ways already established depending on the plot trajectory
> of the player. Some of the terribly reactive guts of the dead sarlacc used
> for trash disposal by the Junkers can be carried there to trigger a massive
> explosion with the lake, turing it into a world-scale crater. An archotech
> bomb can be provided by the rust cathedral intelligence to blast into the
> place. The Helix faction should have another option, perhaps a compressed
> oxygen bomb (air fuel bomb, the inverse of a fuel air bomb). But there
> should be more peaceful ways too if the player tries harder. Maybe the
> Junkers would have a drill-based solution that could be installed to make an
> approach shaft in one of the tiles, or similar solution from the Deepwater
> faction."

Card rulings layered on it, same sitting (recorded on the item; restated here so this
spec stands alone): **three blast tiers** — sarlacc guts take the whole lake
(world-scale crater, `CHILL_WORLD_CRATER_1` owns the world-map build); the archotech
bomb is surgical, one clean wound; the oxygen bomb is a zone-scale burn leaving a
dead glass scar with the lake surviving. **Price and provider match brutality.**
**The drill routes leave a small wound**: Iliss-tier arc harassment at the work site,
a thin permanent scar, no Tarnn wake — and the drill occasionally cuts a buried
AuroraGlass vein. And the governing physics, owner-typed and total
(`CHILL_FIRE_BAN_1`): there is no oxygen at the bottom of the Chill, so **fire is
impossible below** — which means every violent route works by *bringing* the
oxidizer or the archotech exotica, and **destruction can never happen by accident.**
The choice is always deliberate, always carried down by hand, always paid for first.

Why the floor is beautiful at all, owner typed: the whole garden aesthetic exists
*"so that the player really feels the choice later to blow it up or not to get to
the ancient war lab."* This spec is that choice, itemized.

House frame, binding on every route: **ship-only access to the floor** — the
gravship and its `RM_SeaDiveHatch` are the only way down and the only way back; no
pawn dives, ever. All DLC assumed present. No worldgen: the crater is a scripted
in-save wound to THE map. Where this spec names an engine mechanism it says so and
marks it; nothing below is XML.

## The door

What four routes end at and one route erases: the lab's entrance, on the deep floor
over the Impact Site, under the island crag (tile 5873 — the lab's access standing
above the fuel, ruled a place, not an accident).

Nobody has seen a door there in ten thousand years. What the player's floodlights
find is a **hill of the garden at its oldest and most magnificent**: eldspar gardens
centuries deeper than anywhere else on the floor, grown shoulder to shoulder with
tarnn lattice until no instrument the colony owns can say where monument ends and
colony begins — the lake floor's standing dispute, at its cathedral scale. Ghostpane
sheets glaze the hollows between spars. Stillbloom precipitates in the lee of the
hill on quiet nights, dozens at once. The frost between the crystals carries the
electrojet's ground currents, and the Iliss patrol it in slow circuits, the only
things moving.

The reading the scrapers arrive at on their own, and the true one: **the garden is
the scar tissue of the old war.** The stillest place on the planet has spent a
hundred centuries growing closed over the wound the war left, molecule by molecule,
the way the sea does everything — patiently, beautifully, and without any interest
in whether someone might one day need the wound open again. The accretion is not a
lock and not a guardian. It is healing. Every route below is a way of tearing it.

Beneath the accretion, the lab itself: shielding intact, amazingly (frozen sheet
§8), and the door it protects still LOCKED — by the frozen gate ruling
(amendment 2026-09-12), the **Rakatan command codes held in the Spire are the only
way through the shielding**, on every route. This spec reads all five routes as
solving the *ground* — the lake, the crust, and centuries of accretion between the
player and the door — never the door itself. The war lab remains a two-key dungeon:
a route opens the ground; the Spire's codes open the door. (See Contradictions for
the one ambiguity in this reading.)

What the player sees before choosing, then, is exactly what the owner built the
floor to make them see: the oldest living structure on Ash'karr, delicate,
entrancing, precious — with a weapons lab underneath it, and five quotes in hand
for the demolition.

## Route 1 — the Throat casks (Junkers; apocalyptic)

**The payload.** In the Wasteland stands the Glowing Throat: the dead sarlacc the
Junkers have used for trash disposal for ages, down which so much hideousness has
gone that an unholy glow rises from it and the ground trembles — not alive, not
undead, just ages of the worst casks *mingling, changing, reacting* into something
the wasteland sheet already calls potentially explosive and potentially able to
poison a sizeable part of the world (`wasteland.md`, the Glowing Throat). The guts
of that dead sarlacc are the one substance on the planet terrible enough to
detonate a fuel sea: a self-mingled hoard of oxidizers, radiologics and worse,
compiled by decades of the Junkers throwing away everything nobody should ever
have made. It brings its own oxygen the way it brings its own everything.
Proposed defs: **RUT_ThroatCask** (the sealed unit, hauled in numbers), and the
delivery is just cargo — no device, no elegance. You do not aim this. You deliver
it and leave.

**Acquisition.** The Junkers are hostile on sight, bribable, no caravans — a loot
source, not a market — so this is not a quest and nobody shakes hands. It is a
transaction at the toll gates, in the Junker register: the player pays, in fuel
and scrap, for the privilege of *hauling the Junkers' worst garbage away for
them.* To the Junkers this is the funniest deal ever struck — some offworlder
paying good fuel to take the casks even they will not touch, the ones the Throat
crews winch up on dares and lose fingers to. The monetary price is almost
insultingly low; that is the ruling working as intended, because price matches
brutality and the price of this route was never money. Hauling the casks across
the world is its own campaign: they are heavy, they leak dose, no other faction
will let the convoy near a settlement, and every jolt is a dice roll the fiction
takes seriously even if the mechanics stay gentle.

**Trigger.** The casks go down the hatch and onto the floor — anywhere on the
floor; a world-scale detonation does not need placement precision, which is why
this is the one violent route that never has to walk the garden to the door. Set
the reaction (a deliberate, multi-step arming — never a bump, never a fire spread,
per the no-accidents law) and get the ship out. What follows is
`CHILL_WORLD_CRATER_1`'s build: the guts detonate WITH the lake — the reacting
mass supplies what the sea never had, and the sea supplies everything else — and
the Chill's world tiles swap in-save to the crater biome. Everyone on the planet
notices. The fiction owes the player one clean sentence beforehand, in whatever
mouth delivers it: *this is the only route you cannot take back, and the only one
that kills the garden without ever waking it.*

## Route 2 — the Lucent Charge (Rust Cathedral; surgical)

**The payload.** An archotech device the size of a coffin and the temperature of
the lake, produced from some reserve the Cathedral has never admitted having.
Proposed def: **RUT_LucentCharge**. It does not explode in any chemistry the
colony can parse — no oxidizer, no fuel, nothing the fire ban even has an opinion
about; Rakatan exotica, the same lineage as the shielding it is tuned to stop
short of. One clean wound, exactly at the door, exactly as deep as the accretion:
the garden loses a circle the width of the entrance hill's crown and nothing
else. The lake never knows it happened.

**What the intelligence wants.** The Cathedral is a slumbering Rakatan mind that
survives by looking dull, hates the Helix from the moment they side with the
Assailants, and tolerates the player's clan only because the Utinni vouches for
them — every boon it grants is a risk it takes by being seen to act
(`03_deep_history.md`). It does not sell the charge and it does not name a price,
because a price could be met and this is not that kind of arrangement. It grants
the charge as a *favor*, delivered through the Enclave congregation's hands so no
organic ever watches the Cathedral move — and the strings are these, stated
plainly by its droid intermediaries and non-negotiable:

1. **The specimens die.** The lab holds live Assailants under containment — the
   study subjects, still trapped, still being studied by nobody (frozen sheet §8).
   The Cathedral's charge opens the ground on the condition that what is contained
   below is *ended*, not harvested. The clan's standing mission against the
   Assailant is what proves the Utinni's value; this is that mission's oldest
   theater.
2. **The Helix never touch it.** If the player has dealt with the Helix over the
   lab — or deals with them after — the favor is withdrawn, retroactively if it
   must be: the Cathedral's hatred of the Helix transfers in full to whoever
   opens the Assailants' larder to them. This is the one route that closes
   another (see Quest shape).

What the intelligence wants, in one line: **the war it was built for, finished
quietly, by hands that cannot be traced to it.** The surgical bomb is surgical
because the Cathedral is hiding; a crater visible from orbit is precisely the
attention it has spent ten thousand years avoiding, and its intermediaries say so
with something close to distaste for Route 1.

## Route 3 — the Long Gasp (Ascendant Helix; zone burn)

**The payload.** The owner's device, in his words: a compressed oxygen bomb — *"air
fuel bomb, the inverse of a fuel air bomb."* Everywhere else in the galaxy you
disperse fuel into air and light it; at the bottom of the Chill the entire world
is fuel and the bomb's whole job is to *bring the air*. Proposed def:
**RUT_GaspCharge**, though the Helix retrieval teams call it the Long Gasp with
their usual clinical wit: cryo-compressed oxidizer in a shaped release vessel,
which on triggering exhales a zone-scale breath into the fuel and lights it. The
burn is bounded by its own oxygen budget — physics as containment, the fire ban
working *for* the design: the flame front dies the instant the brought air is
spent, so the lake survives by arithmetic, not by luck. What the burn zone leaves
is a **dead glass scar** — floor life flash-burned and the melt refrozen into a
sterile pane where nothing will grow again.

**Acquisition.** The Helix do not raid; they retrieve — and they have wanted into
this lab since before the player's clan existed, because the living residue of
the Assailants' craft is the only surviving specimen of it and the lab is the
original archive (`04_factions.md` §9, the Overdrive). They cannot walk the floor
themselves: no Helix gravship, no hatch, no way down — the player's ship is the
first key anyone has had in centuries, and the Helix know it before the player
does. So the offer arrives unbidden, immaculate, and expensive in the only
direction that matters: the charge is sold at obscene-wealth prices (they can
afford to charge; the player can be made to afford to pay), **plus a retrieval
share** — Helix specialists ride down after the burn and take their pick of the
containment archive. Not everything; a share. Their contracts are precise,
honored to the letter, and drafted by people who have been buying unread
antiquities at a premium for years.

**Trigger and placement.** Unlike Route 1, the Gasp must be *placed* — the zone
has to cover the entrance hill, so the carry crosses the garden to the door with
the device on a sledge, under Iliss harassment the whole way (placement is
directed offense; see Defense response). Then the ship stands off and the floor
breathes in, once, for the first and last time.

## Route 4 — the Chewer (Junker drill shaft; peaceful, loud)

**The fiction.** A salvaged deep-mining rig out of the Junker yards, sold as-is,
no warranty, delivered in pieces by a waste caravan that overcharges for the
detour and leaves before the crates are open. Proposed def: **RUT_BoreRig**; the
Junkers who welded it call it a chewer, because that is what it does — it chews.
Installed on one of the Chill's tiles (the owner's own siting: *"an approach
shaft in one of the tiles"*), it grinds a shaft down through crust and bedrock,
skirting the liquid entirely, toward the lab's approach galleries. Weeks of work:
the rig runs loud, breaks down in Junker fashion (components, colonist labor,
coarse improvisation), and every meter is bought with somebody's shift in the
worst cold on the planet.

**The cost shape** — and this is where 4 and 5 divide: the Chewer is **paid in
full, up front, and then it is yours** — a big one-time price in fuel, scrap and
components through the same toll-gate channel as Route 1, and afterward nobody
owes anybody anything, because the Junkers do not do favors, do not do stakes,
and do not come back. Everything after the sale is the player's problem: the
breakdowns, the shift roster, the arcs. It is the route for a colony rich in
material and labor and unwilling to owe a living soul.

**The wound and the finds.** Ruled: the drilling agitates — **Iliss-tier arc
harassment at the work site** for the duration, arcs walking up the shaft through
the conductive frost, stinging and eerie and survivable; **no Tarnn wake**; and
the finished shaft leaves a **thin permanent scar** on the floor map, a single
hairline through the garden's margin. And ruled: the drill occasionally cuts a
**buried AuroraGlass vein** — the planet's prettiest treasure, paid out in small
honest lots to the route that tried harder (the same substance the eldspar
hearts carry; the veins are where ancient gardens were buried, which the
description should let a careful reader work out and mourn a little).

## Route 5 — the Stillbore (Deepwater caisson; peaceful, patient)

**The fiction.** The Deepwater Compact are the planet's deep-pressure engineers —
the people who hold the aquifers and know what liquid under cold and weight
actually does. Their solution is not a drill but a **caisson**: a sealed
descending pressure-bore, proposed def **RUT_PressureCaisson**, sunk by a
contracted Deepwater crew with the unhurried competence of a people whose
doctrine is the Balance and whose wardens dehydrate off-water and know it. Same
destination as Route 4, same wound class — the shaft is quieter in fiction but
the ruling does not distinguish: Iliss-tier harassment at the site, thin
permanent scar, no Tarnn wake, and the same occasional AuroraGlass vein. What
differs is everything around the hole.

**The cost shape.** Modest payments on schedule rather than a fortune up front —
Deepwater sells to everyone and their contracts are prompt, capped and
unsentimental — but the Compact does not sell *out* of the arrangement at the
end. Two strings, both very Deepwater:

1. **Clean hands to sign.** The Compact's one absolute is that interrupting
   ANYONE's water costs their goodwill; a player whose record shows cut supply
   lines or poisoned wells is not offered the contract at any price. The patient
   route is gated on having played patiently.
2. **A stake in the floor.** The lake floor holds the only water on it — the
   stonewater brakes, whose skeletons are ice because ice is the local granite
   (flora pass §6). Deepwater's surveyors noticed before the player did. The
   contract grants the Compact **standing survey and claim rights on the Chill's
   stonewater fields**, metered through their own instruments on the caisson: a
   permanent, polite, entirely legal Deepwater presence at the bottom of the
   world. The favor owed is not a debt to discharge; it is a neighbor acquired.

**4 versus 5, in one breath:** the Junker route is *buy the machine, own the
problem, owe nothing* — front-loaded cost, ongoing breakdowns, no strings. The
Deepwater route is *hire the professionals, spread the cost, gain a permanent
partner with a claim* — gated on clean hands, smoother in the doing, and never
entirely yours afterward. Same hole; opposite relationships to it.

## Price and provider match brutality — the ladder

Ruled at the sitting; here is the ladder it produces, most brutal first. The
pattern to preserve in every build decision: **as brutality rises, the monetary
price falls and the real price grows** — the worst option is nearly free and
costs the world; the gentlest options cost steady money and honest work and
leave you owing or owning relationships.

| route | provider | money price | the real price |
|---|---|---|---|
| 1 · Throat casks | Junkers | insultingly low — you are hauling their trash | the lake, the garden, the biome, the planet's fuel tank, and a wound visible from orbit, forever |
| 2 · Lucent Charge | Rust Cathedral | none — not for sale | obligation to a hiding god: the specimens die, the Helix are locked out, and the favor can be withdrawn |
| 3 · Long Gasp | Ascendant Helix | obscene, and paid in full | complicity: a retrieval share of the Assailant archive walks out in Helix hands, and the Cathedral's hatred follows you |
| 4 · the Chewer | Junkers | heavy, up front | weeks of labor, breakdowns, Iliss arcs, a thin scar — and nothing owed after |
| 5 · the Stillbore | Deepwater | moderate, on schedule | clean hands required, and a permanent Deepwater claim on the floor's water ice |

## Defense response per route

The garden's immune system is `CHILL_GARDEN_DEFENSE_1`'s build — tiered, Iliss
first, then Tarnn, both overcomable by ruling. What each route meets:

- **Route 1 (casks): nothing.** The detonation preempts the defense absolutely —
  the garden dies without ever waking, Iliss, Tarnn and all. This is deliberate
  and should be legible in the fiction: the apocalyptic route is also the only
  one the garden never gets to answer, which is part of what makes choosing it
  feel the way the owner wants it to feel. No fight, no warning, no witness.
- **Route 2 (archotech): preempted locally, then a vigil.** The wound is faster
  than any wake — one instant, one circle. No Tarnn fight occurs *if the player
  takes only the wound*: the charge is surgical in the defense sense too. In the
  days after, the Tarnn colonies muster at the scar's rim and stand — scenery
  that has stood up and now simply watches. They fight only if harm continues.
  The eeriest of the five aftermaths, and the cheapest in blood.
- **Route 3 (oxygen): the wake, at the margin.** The burn zone's defenders die in
  the burn, but a zone is not the floor: at the flame front's edge, sustained
  destruction on exactly the scale the defense item names wakes the surviving
  Tarnn — the hard skirmish, several at once, sized like a hard fight and NOT a
  raid, converging on the scar and whoever stands in it (the Helix retrieval
  team's escort problem is the player's problem; the contract says so). The
  placement carry beforehand runs under Iliss arcs the whole way — hauling a
  bomb through the garden is directed offense from the first cell.
- **Routes 4 and 5 (shafts): Iliss tier only, ruled.** Arc harassment at the work
  site for the weeks of the bore — through the conductive frost topside and up
  the shaft itself — stinging, eerie, survivable, never escalating. **No Tarnn
  wake** on either shaft, by card ruling: trying harder is not free, but it is
  never punished at scale.

Calibration inherited whole from the defense item: *"shocking when it can
actually defend itself but quite overcomable"* — a prepared expedition beats
either tier without a wipe, on every route where a tier fires at all.

## Aftermath states

Five endings for the floor; each is a permanent state of THE map, never a
regeneration. (Seabed-layer caveat from the flora pass carries: floor maps
re-roll between dives today; the scars below are authored as terrain/biome
truth so they persist through that, and the crater is world-tile truth.
Engine shape per state is the build's problem; feasibility bars live on the
items named.)

1. **The world crater** (Route 1 — `CHILL_WORLD_CRATER_1`'s build). The Chill's
   world tiles swap in-save to the crater biome: dead glass, no life, its own
   world-map color — the planet visibly wounded from orbit, forever. On the
   ground: a massive fresh crater and a ripped-open ancient lab, shielding
   intact, amazingly (frozen sheet §8's image, now one route among five). The
   campaign loses things it can never buy back: the garden, every species and
   flora def whose only home this was, the fuel-by-pipe-length economy of the
   planet's one fuel tank, the stonewater ice, the AuroraGlass gardens — and it
   gains the only route-aftermath everyone on the planet reacts to, because
   everyone on the planet noticed.
2. **The surgical wound** (Route 2). One clean circle of absence at the entrance
   hill, edges fused smooth — archotech leaves no rubble. The garden otherwise
   intact; the Tarnn vigil ringing the scar; the lake and surface unchanged, and
   no other faction ever learns how the ground opened unless the player tells
   them. Campaign state: the Cathedral's favor is on the books, with both its
   strings live.
3. **The glass scar** (Route 3). A zone-scale pane of refrozen melt — sterile,
   flat, faintly beautiful in the wrong way, a dead mirror inside the living
   black one. Nothing regrows on it, ever; the wildPlants of the burn zone are
   gone as terrain truth, not as a setback. The lake survives by arithmetic.
   Campaign state: a Helix retrieval share has left the lab, Helix instruments
   remain politely bolted near the scar, and the Rust Cathedral knows.
4. **The drill scar** (Route 4). A thin permanent hairline through the garden's
   margin plus the shaft-head on its tile topside — Junker steel rusting in the
   fuel snow, kept running by the colony or abandoned picturesquely. The shaft
   is a standing second door to the lab approach (a built portal in the
   `RM_SeaDiveHatch` family is the obvious engine shape — that hatch is a
   MapPortal subclass; the shaft-as-portal reading is a proposal, UNVERIFIED
   against engine behavior). AuroraGlass lots in the ledger; nothing owed.
5. **The caisson** (Route 5). The same thin scar and standing shaft, but sealed,
   silent, professionally lit — and metered. Deepwater instruments on the
   headworks, Deepwater surveyors booked onto the colony's dive schedule,
   Deepwater claim-markers on the stonewater fields. The gentlest aftermath and
   the only one that adds a permanent second flag to the bottom of the world.

Across all five: the door itself, once reached, still wants the Spire's codes.
No aftermath state includes an open lab.

## Quest shape

Prose-first; no QuestScriptDef XML here, and the four offers below are shapes,
not node trees. The owner's own gating law does the routing: *"several ways
already established depending on the plot trajectory of the player."* Read that
as: **each route is unlocked by the relationships the player's play has kept
open**, never by a tech node or a single flag — the routes ARE a readout of how
the campaign was played.

- **The Junker channel (Routes 1 and 4)** is commerce, not questing — the
  Junkers are hostile on sight, bribable, a loot source not a market, so both
  offers live behind the toll-gate bribe economy the waste-caravan roads already
  imply. The hook arrives as rumor down those roads: the Junkers have casks even
  they want gone, and rigs even they cannot sell. Gating: a standing bribe
  channel (the player has paid tolls and kept paying); no goodwill mechanism,
  because there is none to have.
- **The Cathedral's offer (Route 2)** is never asked for and cannot be. It
  arrives through Enclave droid intermediaries — whispered-voices channel, the
  congregation acting for the god that will not be seen — only when the plot
  trajectory has proven the clan: the Utinni's vouching intact, the clan's
  standing missions against the Assailant actually run, and no Helix dealings
  over the lab on the record. It is the plot-gated route in the strictest sense:
  a favor from the concealment arc's most reluctant actor, and it can be *lost*
  — struck from the table, permanently, by one Helix contract (below).
- **The Helix offer (Route 3)** finds the player, not the reverse. The Helix
  have always known where the lab is; what they lacked was a way down, and the
  player's gravship is the first in centuries. The offer arrives once the
  player's interest in the Chill is legible (dives logged, a shaft priced, an
  agent's report) — immaculate, contractual, riding the same lanes as their
  antiquities buying. Gating: contact and commerce with the Helix at all, and
  the stomach for the string. **Mutual exclusion, both directions:** signing
  with the Helix withdraws the Cathedral's charge forever and earns its
  transferred hatred; taking the Cathedral's charge locks the retrieval share
  out and the Helix — who do not raid, and retrieve — respond in their own
  register instead.
- **The Deepwater contract (Route 5)** is the plainest shape in the set: walk
  in and ask, and be told yes or no by the record. Gated on goodwill and on the
  clean-hands absolute (no water interrupted, anyone's, ever); offered promptly,
  capped, unsentimental, with the survey-stake clause read aloud.

**What stays open, and for how long:** the two shafts foreclose nothing — a
player can bore the patient way down, stand in the garden at the door, and
*still* choose to buy a bomb; the choice the floor was built to pose stays live
until a blast tier actually fires. Any blast forecloses the other blasts
(there is nothing left to blast surgically after a crater, and no lake left to
save after the guts). The two-key rule shapes every route's back half: reaching
the door is this spec; opening it is the Spire's codes and `ANCIENT_WAR_LAB_1`.

## Contradictions with the frozen origin sheet

Checked line-by-line against `the_propane_lakes.md` (frozen 2026-09-07; amendments
add detail, never change rulings — the newer owner rulings below therefore
supersede where they collide, and the collisions are recorded here rather than
papered over):

1. **"The ending is guaranteed" vs "the choice is the point."** The sheet's §8
   amendment (plot sitting, 2026-09-12) has the crater as THE ending — multiple
   player triggers, *"automated ways for it to occur"* if the player never fires
   one, a cut-scene no one will miss, *"guaranteed to happen and guaranteed to
   be seen."* The 2026-09-27 rulings make the crater ONE tier of a five-route
   choice, with the entire floor aesthetic built so the player *feels the choice
   to blow it up or not* — and an automated fallback that fires regardless would
   delete that choice. The newer ruling wins as far as it reaches; whether the
   automated fallback survives at all is genuinely open (Open questions, Q1).
2. **"Ignition from anything extremely hot" vs "destruction can never happen by
   accident."** The sheet (§8 and hard ban 4's framing) treats spacecraft
   interaction or any hot source as a live crater trigger. The fire-ban physics
   (owner, 2026-09-27: no oxygen below) plus the routes card (every violent
   route brings its own oxidizer or exotica; no accidents) supersede this for
   the floor. A surface-side hot-source story may still exist above the crust,
   where the atmosphere is — but the crater-as-accident is dead, and this spec
   treats hard ban 4 as satisfied by construction: every trigger below is a
   deliberate, chemical-or-archotech, hand-carried source.
3. **Not a contradiction, held deliberately:** the two-key gate (crater opens the
   ground, Spire codes open the door) is frozen amendment text, and the owner's
   route paragraph says the archotech bomb is provided *"to blast into the
   place"* — readable as breaching the shielding itself. This spec keeps the
   frozen gate: all five routes open the ground only. If "into the place" meant
   through the door, that is Q2.

Nothing else collided: the ten hard bans are untouched (no kyber, no visibility
penalty, no rain, no tanker economy, no roads in the Umbra, no icy analogs, the
war-legacy split holds — the lab's contents stay study subjects on every route,
and no route puts weapon-fauna in the biome), and the island, the pipes, the tap
and the Slurrypede are all left exactly where the sheet put them.

## Open questions for the owner

Three, and only where the record genuinely runs out:

1. **Does the automated crater fallback survive the routes ruling?** The
   2026-09-12 plot amendment guarantees the ending (*"if they fail to do so,
   there may be automated ways for it to occur too"*); the 2026-09-27 rulings
   build the whole floor around the player feeling free NOT to fire it. Is the
   crater now strictly player-fired, or does some late automated trigger remain
   — and if it remains, does it wait on the player having seen the garden first?
2. **Do the blast routes touch the door itself?** Your route paragraph has the
   archotech bomb *"blast into the place"*; the frozen gate ruling keeps the
   shielding locked behind the Spire's Rakatan codes on every path. This spec
   assumes all five routes open only the GROUND and the two-key rule stands —
   confirm, or the Lucent Charge becomes a shielding-breacher and the two-key
   dungeon loses a key.
3. **May the Helix retrieval share include a living specimen?** Route 3's string
   is a share of the containment archive. Residue and dead material is one
   campaign; a live Assailant walking out under Helix escort is the Overdrive
   handed its missing piece, and probably a plot trigger in its own right.
   Where is the line on what their contract may name?

---

*Sources: `CHILL_WARLAB_ROUTES_1` (commission; owner paragraph and card rulings),
`the_propane_lakes.md` (frozen sheet), the flora pass 2026-09-27,
`CHILL_FIRE_BAN_1` / `CHILL_WORLD_CRATER_1` / `CHILL_GARDEN_DEFENSE_1`,
`reconciled_lore/03_deep_history.md` (the Cathedral's mind),
`reconciled_lore/04_factions.md` (Junkers §12, Deepwater §7, Helix §9),
`wasteland.md` (the Glowing Throat). Engine claims marked UNVERIFIED are
proposals; everything else mechanism-honest against those files.*
