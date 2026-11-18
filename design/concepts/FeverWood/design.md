# The Fever Wood: the design, seen from the ship

**Status:** the one design document for the Fever Wood biome (`RM_FeverWood`, source `src/RimMandrake/FeverWood/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the older
definition sheets, rosters, reviews and the cleanse proposal as the place to read; those files are listed, with what
happened to every idea in them, in `design/concepts/FeverWood/rewrite_choices.md`. Nothing has been deleted yet.
The Fever Wood is one of the six biome mods HELD BY OWNER: this is a design document only and it launches nothing.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/FeverWood/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet; the locked `sheet.md`, `tree.json` and `scenes.json` beside it still describe the
older settled-colony design and would be re-argued from this one when the hold lifts.

**How to read the tags:** `NEEDS HIM` marks a question only the owner can settle, with the real answers and the
default this document was written on. `UNSETTLED` marks a fact the sources do not fix. `UNMEASURED` marks an engine
fact nobody has checked. "Built" means the census of 2026-11-17 (`cleanse/census.json`) found it in source; it does
not mean it has passed anything.

---

## What this place is

> *"wood-roads twisting through a living crown, high above black mirror pools that nothing sane touches."*
> (`the_fever_wood.md`, header)

The place where trees finally won. Trunks wider than houses rooted the backswamp still, and their limbs grew together
into roads of living wood above shallow, perfectly black pools that never ripple. The crown is the loudest place on
the planet: alien birds, nectar herds, things clamped to bark. The floor is dim, wet and nearly empty. Under all of
it, under one water table that every pool is only a window onto, lives the **sekkulaath**: one animal, too big ever
to be seen whole, that reaches up with tentacles, takes what comes near, and sets its victims' gear out at the
water's edge as bait.

> *"It's the classic Star Wars beast that is so big it can't even enter the screen, but it can reach up with
> tentacles to lash out, grab, pull under."* (owner, 2026-09-23)

> *"Perhaps it literally strips loot of its victims and scatters it near the pools to attract you: treasure to
> lure."* (owner, 2026-09-23)

**Seen from the ship, the Fever Wood is one joke told very well: a crew of scavengers has landed beside a monster
that fishes with scrap.** Jawa cannot walk past salvage. The sekkulaath does not need them (the mud feeds it); it
baits them *"because it can, not because it is hungry"*. Everything in the first two versions serves that meeting,
plus the one sound nobody forgets: the whole crown going silent at once.

The crew are small, hooded, skittish, weak in a brawl and at home in dry heat (`reconciled_lore/05_the_clan.md`).
The heat here is the one familiar thing. The wet, the height, the noise and the water are not.

## The clock on any stop

The crew does not settle here. The Empire's search restarts at every landing, and its timing is fixed in
`src/RimUtinni/EmpirePursuit/` (owner's cadence ruling of 2026-08-28: *"around every 5-8 days, keep 'em running"*)
and in the escalation ladder (`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, whose own
numbers are marked provisional):

- First contact, a probe droid, five to eight days after landing. Then a scout team with a spotter, then the first
  real fight (a strike team), then an ion cordon on the ship, a breaching assault, and last an orbital bombardment
  whose letter reads *"This cannot be fought. Leave."*
- Each step comes only if the one before it succeeded for the Empire, and a loud, visible crew halves every wait
  while a hidden one doubles it.

**UNSETTLED: how long a visit really lasts.** The sources fix the first contact (five to eight days) and the last
step (leave), not the total. This document assumes: the first week is nearly free of the Empire; the first fight
comes in the second or third week; nothing lets a crew stay much past a month. A season is fifteen days, so
**anything that needs a season to show itself is not in 0.1.0 or 0.2.0 here.**

---

## The first minutes

The ship comes down through the green ceiling. The trunks cannot fall (the crown is interlocked; *"so you can just
mine right through one"*), so nothing topples: the ship settles between towers onto wet floor, and the marsh that
refuses every heavy building takes the hull because the hull is its own foundation. (UNMEASURED: whether Odyssey's
landing check honours the marsh's building refusal. If it does, the fallback is that only bough-soil and causeway
clearings are legal landing ground, which the landing picker must show.)

On the way down the player hears the crown at full voice: every bird makes its own call and the noise is only their
sum (*"Each animal literally makes its own noise and just adds together"*, owner). The birds really fly, and they
scatter from the descending hull.

Then the landing is heard below. The sekkulaath has excellent hearing; noise near a pool calls it. At the pools
nearest the ship a motionless limb rises and stands, and **the whole crown goes silent**. The ruling is that the
crown goes quiet only for the water, so this silence means exactly one thing, and the crew learns what it means in
their first minute: the hatch opens onto the quietest moment the Fever Wood ever has.

> *"crown-life constant and easy; ground-level none — then a ripple, and everything above goes silent to watch."*
> (`the_fever_wood.md` §9)

And from the hatch the crew can already see why they will not simply stay aboard: gear, glinting at the margin of
the nearest pool.

*New in this rewrite:* the landing counting as a noise the water hears. The hearing, the standing limb and the hush
are all built; only the landing as a source is new, and it is small. It is not the hull-snaring "Mooring" the owner
declined on 2026-10-02 (see `NEEDS HIM`, below).

## The first day

- **The bait.** Stripped gear lies at the pool margins and keeps arriving. A crew that watches a pool sees, sooner or
  later, the slender tentacle that brings it: *"a rare moment of a tentacle coming up and placing a new item"*. It is
  drawn *"more slender and delicate than the others"* so the player can tell it apart before anyone shoots.
- **The first grab.** A Jawa collecting at the margin is taken by a thick fast limb and dragged toward the water. He
  is not dead: he is down in the shallows on a clock, and a companion who was near enough carries him out. The
  owner's words for the distance: *"A nearby companion should have a fair chance. Shore work rewards bringing help;
  someone across the settlement may arrive too late."* The crew learns to go to the water in pairs.
- **Reading the water.** A small pool reaches a little way; a great one reaches far inland. Clicking any pool shows
  its reach on the ground before anything has happened there (the "show water reach" overlay), so the first grab is
  a risk the player took, never a trick.
- **The roads.** The crew walks onto the living-wood routes wherever they touch the ground. Height is paint: nothing
  climbs, nothing is gated. The routes are where the fruit, the nectar herds and the dry footing are, so ordinary
  errands follow them.
- **Shooting the wrong one.** Someone shoots the delicate limb. It vanishes; that pool never gives again and is
  angrier from then on. The next pool over does not hold the grudge.
- **Fighting back.** A hurt limb withdraws and the pool is quiet for some hours. A limb cut through before it can
  withdraw leaves a severed tentacle to butcher and buys a day.

## The first week

- **The nectar deal.** Thornbugs, great thorn-shaped insects clamped to the bark, give sweet nectar to an ordinary
  gathering job, and only while calm. *"The dairy is the alarm system, and every raid costs nectar before it costs
  blood."* A fight near a herd dries it; a fight on the far side of the map does not.
- **The margin's honest goods.** Seep-oil from a squat barrel plant sitting in its own rainbow slick; potter's clay
  from a root-plate; resin medicine scraped from bark. The oil and the clay stand inside some pool's reach. Reward
  and hazard are the same walk. (The leaning half-dead tree that *"looks like a wreck and is not one"* is still
  here to look at, but it gives no timber: since the tree ruling of 2026-10-17 only true trees give wood.)
- **Working a pool hard.** Every encounter at a pool, every item taken and every loud fight at the margin pushes
  that pool toward its big one. At a great pool the big one is the set-piece: many limbs and **the eye itself**.
  Hurting the eye drives every tentacle on the map off for a day. Killing it before it withdraws ends the water's
  danger on this map for good. There is no protection and no minimum crew: the legibility (pool size, the overlay,
  the silence) is the fairness, and the ship is the way out.
- **A crew that has been greedy for a week has probably met the eye.** That is intended. The set-piece is the
  Fever Wood's climax and it has to be reachable inside a stop; pressure from the crew's own salvaging is what
  brings it within days instead of seasons.

## "OMG did you see that?"

Each of these can happen inside the visit. Each says what is on screen.

1. **The crown goes silent.** *On screen:* birds wheeling and calling, then a tall still limb standing out of a
   pool, and every call stops together. *Why it lands:* the loudest map in the game has an off switch, and it is
   not the player's.
2. **The gift-giver.** *On screen:* a thin, almost dainty tentacle lifts a blaster rifle out of black water and sets
   it carefully on the mud, then withdraws. *Why it is funny:* a Jawa is already walking toward it.
3. **The grab and the tug-of-war.** *On screen:* a hooded figure hauled feet-first toward the water, a second
   hooded figure sprinting the boughway, picking him up and carrying him clear. *Why it is alarming:* the clock is
   real, and the one who went alone does not get the second figure.
4. **Shooting the gift-giver.** *On screen:* the delicate limb is hit, snaps under, and the pool's inspect line
   changes for good. *Why it is funny:* it is the single wholly self-defeating act at a mirror, and a trigger-happy
   crew will do it once.
5. **The bark bites.** *On screen:* a pet trots along a trunk and a flat piece of bark unfolds two hooked arms and
   holds it. The silloch *"must read as bark"*; it strikes once from where it sits and does not chase, so the pet
   that breaks free gets away.
6. **The sac that will not come off.** *On screen:* a Jawa tries to handle a grey sac on the bark and it inflates
   under his hands until it cannot be detached. Next to it an amber bead floods its own shell and sets hard.
   *Why it is funny:* the crew's instinct is to pry things loose and take them, and here the things refuse.
7. **The eye.** *On screen:* a great pool erupts in many limbs and one eye on a stalk, the crown silent, the crew
   deciding in that moment whether to run for the ramp or aim for the eye. The owner's phrase for the animal:
   *"shocking even to those who know them."*
8. **The trooper in the pool** (see the Empire, below). *On screen:* a white-armoured figure taken off the shore by
   the same limb that took the Jawa on day one, and nobody runs to carry him out.

## When the Empire arrives

The Fever Wood does not take sides. It does to the Empire what it did to the crew, and the crew has had a week to
learn the rules the Empire has not.

- **The water takes anyone who is not native.** Troopers who cross a pool's reach are seized like anyone else. A
  strike team dropped at the map edge has to cross ground the crew has already mapped pool by pool.
- **Noise calls it.** Blaster fire at a margin brings feelers and raises the standing limb, so a firefight near
  water is fought in the silence, with a third party. A crew can choose where the fight happens.
- **The probe and the spotter need to see the ship.** Solid trunks block sight. A ship parked among towers offers
  few long sightlines, and the ladder's own rule is that a spotter with no line to the ship fails his call. This is
  a consequence of two built things, to be shown in a scene, not a new mechanic.
- **The herd goes dry.** A strike near the crew's thornbugs costs nectar for days. Small, true, and the player
  notices.
- **The eye is no ally.** A crew that has killed the eye has also removed the pools' help against the Empire. That
  trade is real and the design keeps it.
- *0.2.0 adds the floor.* Sink-mud catches by weight (*"heavy things sink"*), so armoured troopers bog down where
  light, small Jawa cross. *"The floor is the wall."* And it adds the lure (next section).

## Who else attacks; who hates the Empire

- **Two raiders, from opposite directions, who hate each other more than anyone:** the kurreth (a wild ant swarm,
  never a faction) and the skreth (the free-tier face of the Webwork's spider brood; the campaign patches the canon
  spider over it). Both are permanent enemies of everyone, each other and the Empire included. They arrive from
  off the map; neither lives here.
- **The lure (0.2.0).** *"Both enemies like helpless prey chained down and wounded."* Staking live bait spares the
  crew and raises the chance a raid comes at all, and *"if only one comes, that's not so good... they might look
  around."* They never arrive together: *"One comes, there's tension, then maybe the other arrives too."* Seen from
  the ship this is the crew's best trick against a strike team: the oldest rule here is *"when both come at once,
  open the gates between them and stand back"*, and it does not say who the two have to be.
- **Nobody here fights *for* the crew.** The Wildsteam's treetop town of Sporefall is campaign lore, placed by the
  campaign layer and not by this biome; they are friendly at home and the sources do not say they fight the Empire.
  `UNSETTLED`, and not this document's to invent.
- **No native chases.** The crown's own animals wait or graze. Pursuit comes only from off the map. That ban stands.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The eye at a great pool, arriving on the crew's own greed, with no protection. A crew that cannot face it leaves.
- An angered pool beside the ship (someone shot the gift-giver) that makes the nearest salvage not worth it.
- *0.2.0:* the oil boil. On the hottest still days the seep-oil lifts into a low rainbow haze; oil gathering pays
  double; *"one spark (a gunshot, a torch, dry lightning) flashes fire along the haze, and a burning pool edge wakes
  the deep."* A crew that fights in it burns its own camp.

**Stay, longer than the Empire would like:**
- Broken sightlines among the trunks (above).
- Pools the crew has learned and the Empire has not.
- *0.2.0:* a crafted radioactive charge fouled into a pool suppresses the water for several days without a fight
  (owner: *"Fouling the water with specific poisons or radioactive material will cause it to be supressed for
  several days as the material diffuses away."*). In the campaign only genuinely dangerous radioactive salvage
  works; outside it the charge *"can be crafted from Uranium"*.
- `NEEDS HIM`: whether the closed crown hides the ship from orbit (below). As built, it does not.

## What the crew takes away

- **The bait itself:** the gear of everyone the water ever took (the built table gives silver, gold, seep-oil, clay
  and sap). Salvage with a story on it.
- **Severed tentacle:** meat from the one animal that cannot be hunted. In the campaign it is dianoga, with a canon
  kitchen behind it.
- **Nectar**, the crown's trade good, *"priced in the herd's peace"*.
- **Seep-oil:** *"scent, slick, and flame"*. Whether it feeds the ship's fuel line is `NEEDS HIM`.
- **Resin medicine, ribbon plumage** sheared from the murrelith, **potter's clay**.
- **A chellow**, if someone tames one: a beakless bird with a throat like *"a lamp with a bellows"*, and a private
  alarm that still goes quiet for water anywhere the ship lands near it.
- *0.2.0:* **one great gift from the bottom** for a returned young (below), and wreck salvage.

## The promises of 0.1.0, and the scene that would show each one broken

A promise here is something a player sees. None of them is a number.

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ship's landing silences the crown and raises a standing limb at the nearest pool. | Land beside a pool with a living flock; read the calls and the limb. | The same landing on a map with the water switched off: the birds scatter and keep calling. |
| Gear arrives at pool margins and can be collected. | Leave a pool alone; a deposit appears on a free cell and a pawn hauls it home. | A hit on the bringer: it vanishes, nothing is left, and that pool gives nothing afterwards while a second pool still does. |
| A seized crew member can be carried out by a companion who was near, and is lost if nobody comes. | Two pawns at the margin, one seized; the other carries him clear. Save and reload mid-clock. | A helper staged far away arrives late; a helper who only touches the victim rescues nobody. |
| A bigger pool reaches farther, and the reach can be read before any attack. | Stand pawns at the same distance from a small pool and a great one; open the overlay on both. | A solid trunk between pawn and pool: no strike. |
| Hurting a limb earns hours; severing it earns flesh and a day. | Light damage, then heavy damage, on fresh limbs. | Quiet stops gifts as well as attacks: no risk-free farming window. |
| Working a great pool brings the eye; killing the eye ends the water's danger on this map. | Raise the pool's pressure by ordinary collecting and fighting until the set-piece comes; fight it both ways. | A small pool under the same pressure never shows the eye; a second map is untouched. |
| Thornbugs give nectar calm and none frightened; a far fight does not dry them. | Gather; stage a threat near one herd and far from another. | The frightened herd recovers only after the threat is gone. |
| Imperial troopers are seized like anyone else. | Walk a trooper squad across a mapped reach. | A native animal on the same cells is left alone. |
| The bark ambusher strikes once and does not chase. | Small prey passes a silloch; prey that breaks free flees. | The silloch stays at its trunk. |
| The vaulm seals and the drommath swells when hurt or mishandled, every time, never at random. | Hurt each; hit again inside and after its recovery. | An untouched one beside it does nothing. |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary safe swamp
(standing rule, every mod).

## Shared machinery

**Featured here** (the Fever Wood is where each is vital and should be proven):
- **Water that seizes, with a rescue clock** (in `EnvironmentalHazards`, the component the code calls the Tenant).
  Any biome with a thing in its water can use it; this is its home.
- **The hush** (`RM_MapComponent_SilenceCue` in `CreatureBehaviors`): a living chorus that one event can silence.
  The Webwork owns silence as a place; the Fever Wood owns it as an alarm.
- **Calm-gated gathering** (`RM_CompGatherableCalmGated`): an animal that yields only while it feels safe.
- **Ground that refuses heavy building, and painted causeways** (`RM_GroundRefusalBiomeExtension`,
  `RM_GenStep_RootCauseways`).
- **Mineable living trunks**, the sibling of the Greentide's greatbole body. Here they never fall and never regrow
  in 0.1.0.

**Merely active here:** the one sun from geometry, with the crown as tree shade (no Fever Wood heat of its own);
fast jungle growth (`ExplosiveGrowth`); natives drinking their own water (`FlowWorks` thirst, where present); real
flight for anything that flies; bone from butchery (`Bones`); wreck salvage (`Wreckage`); the ship's acoustic
sounder; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- The land: solid mineable trunks that cannot fall; static living-wood routes and bough-soil; marsh that refuses
  heavy building, with stilts; still black pools. (built)
- The landing heard below: a standing limb and the hush on arrival. (new, small)
- The bait and its bringer; the pool that remembers being shot at. (built)
- The ordinary limbs: the blind feeler after noise, the grab with its rescue clock, the barbed lash, the standing
  sentinel. (built; the reload of a live rescue clock is a known defect to fix)
- Reach by pool size, with the read-before-you-go overlay. (overlay unbuilt)
- Driving it off: withdraw, sever, flesh. The eye at a great pool, brought on by the crew's own pressure; the
  map-wide kill. (built)
- The chorus as the sum of living, flying birds, and its silence. (hush built; per-bird calls unbuilt)
- Thornbug nectar on the calm deal; ordinary harvests (fruit, tuber, resin medicine, seep-oil, clay, cordage,
  cane sap). (built)
- The bark ambusher that does not chase; the carrion mound; the wood-eating grub as an ordinary animal. (built)
- The vaulm's seal and the drommath's swelling. (built; moved in, see `rewrite_choices.md`)
- The water takes troopers too; trunks break the Empire's sightlines. (consequences of built things; scenes owed)
- Natives are never seized and drink their own water. Every loss shows a sign.

**0.2.0, the stop with company**
- Sink-mud that catches by weight and never harms by itself, and the too-even green skin that hides it (*"firm
  ground — which is the lie"*). (unbuilt)
- The lure: live bait, staggered raiders, the two fronts. (built)
- The oil boil. (built; owner's card of 2026-10-02)
- The radioactive charge that quiets a pool without a fight. (built; `NEEDS HIM`, below)
- The ransom of its young: a juvenile bought or carried from elsewhere, released into a pool, earns *"one great
  gift from the bottom"*. (built; owner's card of 2026-10-02) The cask is cargo; the gift is a reason to come back.
- The ollareth, which *"screams, and the crown comes"*: its alarm, once what answers it is defined.
- The thieving bird (the skellick: *"This creature is a thief."*), where the Property mod is loaded.
- Summoning the eye on purpose with noise or an offering, so a prepared crew can pick its moment.
- Broken ant hives at the mirrors (*"the ants tried the water, and it took them"*) as day-one evidence and loot;
  the indicator spike (corvath, *"a grave marker"*) standing at pools that have fed, placed when the map is made.
- The Fever Wood's wreck field and the acoustic sounder's readings here.
- The crown's only safe water, the cistrel cup, once the thirst service it needs is in the build.

**Later (a crew that stays, or a colony)**
- The prison tank as an industry: products, teaching, neglect, escape, the escapee establishing in a pool and
  maturing over days.
- The reactive ant-hive dungeon, its farm, guards and sealing corridors.
- Borers that extend their galleries through a trunk someone lives in; trunks that regrow and crush; sealant.
- Routes that slowly move; plennith that makes the crown's soil; corvath that appears only after a feeding.
- Ranching the four sap-drinkers; nests worth raiding; the doomed-herd incident.
- The mirror-break incident; a bespoke arrival letter; the grolth's acid trail.

**Dropped (already cut or declined by the owner; listed so nobody revives them by accident)**
- Ants carrying thornbugs off alive, and the raid-back quest (cut 2026-10-23).
- The hive parasite (cut 2026-10-23). Any rite (*"none, move on"*, 2026-10-02).
- A sap-drinker that drops into the pool; a crafted bloodless lure; any protection against the eye; split crown and
  floor animal densities; climbing or gated ascent (all declined 2026-09-23).
- A Fever Wood heat kind (the one-sun ruling of 2026-10-19 replaced the "ambient" reading of 2026-10-02).
- The lommerel, thavrik, nemmel, gorrameth and the arch-throwing tree (cut from this roster 2026-10-08, *"no longer
  needed"*).
- **Recommended for dropping, not yet his:** the consumable mirror-list (the overlay does its job).

**Outside the biome's versions**
- The whole animal rising. It is the campaign's, spent once, in the crater event
  (`sekkulaath_rising_crater_event_2026-11-01.md`).
- Sporefall, the herd-groves, the dianoga's name and kitchen: campaign layer, mapped over a free tier that is whole
  without them.

## NEEDS HIM

1. **Does the crown hide the ship from orbit?** His 2026-08-05 ruling is that dark or covered tiles pause the
   orbital clock; only the Abyss is on the built list of such biomes. *No* (as built, and this document's default):
   the Fever Wood is an ordinary five-to-eight-day stop. *Yes, like the Abyss:* it becomes a refuge, and its own
   dangers must then be what time the exit. *Partly:* one visibility band quieter while the ship sits under canopy.
2. **Does the water touch the ship?** *Noise only* (default): the landing wakes it and the crew meets it at the
   margins. *The Mooring as pitched 2026-10-02 and not chosen then:* a limb wraps a hull edge and launching tears
   that section off into the pool, to be set out as bait weeks later. *Nothing:* the landing is silent to the deep.
3. **The no-fight charge: 0.1.0 or 0.2.0?** The cleanse asked this on 2026-11-17 and it is unanswered. Default
   here: 0.2.0. His September ladder names it, so keeping it out of 0.1.0 is a real narrowing.
4. **Is seep-oil ship fuel?** The sheet says *"perfumes, lubrication, and fuel"*. *Trade good and lamp fuel only*
   (default). *Refines toward the ship's fuel:* then the Fever Wood is a fuel stop and the margin's danger prices it.
