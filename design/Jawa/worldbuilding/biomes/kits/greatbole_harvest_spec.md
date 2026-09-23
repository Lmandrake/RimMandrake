# The greatbole harvest — spec

**Status: DESIGN, ruled by the owner 2026-09-23 across two card rounds. Nothing built by this
document.** Item: `GREATBOLE_HARVEST_LADDER_1`. The greatbole itself:
`GREATBOLE_BARK_EDGE_ART_1`. The mature tree it seeds: `GREENTIDE_JUNGLE_TREE_ROSTER_1` row 22.

---

## 1. What this is

**The greatbole is a living thing you take from, and the amount you take is the entire mechanic.**
Three thresholds on how much of its footprint has been removed, each a louder answer from the tree,
and a harvest economy that outfits an expedition.

🔑 **The organising rule, and both of the owner's numbers fall out of it:** *below the line you mine
faster than it heals; above it, it heals faster than you mine.* The thresholds are where the race
changes hands.

| removed | what happens | the tree afterwards |
|---|---|---|
| 0–40% | you outpace the healing. Chambers hold; sealed ones are permanent | alive, harvestable |
| **40%** | **The Great Shaking** — fruit and grubs come down; structures inside damaged | alive, harvestable |
| **60%** | **The violent healing** — it closes on you, seals chambers, crushes what stays, and **keeps going back up to 100%** | alive, fully restored |
| **70%** | **The catastrophe** — falling trunk segments crush everything within 50 cells; map permanently altered | **dead. That is it.** |

### 🔑 The consequence nobody designed, which is the best thing in the ladder

Past 60% the wood heals faster than a miner digs. ⇒ **A pick cannot reach 70%.** The only way to
remove wood fast enough is **explosives**, which is exactly how the owner described reaching it.
**The mechanic makes the method compulsory without a rule saying so.** ⛔ Do not add a rule
saying so; the crossover already enforces it, and stating it as a restriction would replace an
emergent truth with an arbitrary one.

---

## 2. The three events

### 2a. 40% — The Great Shaking

An earthquake-like event: the tree answers. It **drops greatbole fruit and arboreal grubs**, both
from a canopy the player can never see or reach.

- **Structures inside take real damage and unlucky ones break. Pawns are staggered, not killed.**
  ⇒ Owner ruling. 🔑 The reason is load-bearing: a warning that costs nothing is not a warning, and
  this is the only per-harvest cost in a loop with no yield brake.
- ✅ **Half-built already:** `RM_MapComponent_LivingRegrowth` fires a **creak** (message + sound)
  before it crushes, for a cell about to regrow under something. The Shaking is that creak's louder
  sibling and should sound like it — same family, bigger.
- 🔑 **The grubs arrive WITH the harvest, not before it.** They live high up, so the player can only
  meet them by shaking the tree. ⇒ A creature that exists purely as a consequence of what the player
  chose to do.

### 2b. 60% — The violent healing

Regrowth flips from slow to **faster than a person can dig**. Chambers seal. Anyone inside is walled
in and crushed unless they cut their way out. **Everything built inside is consumed.**

**And it does not stop at 60% — it continues back up to 100%.** ⇒ Owner ruling, and it is what keeps
the loop alive: the bole is not lost, it is **reclaimed**. A player who over-reaches loses the
interior and gets a whole tree back to harvest again.

- 🔑 **This makes the tree's identity and its danger the same mechanic.** "It heals" is the greatbole's
  signature; at 60% that sentence becomes the threat. No other option on the card did that.
- ✅ **The crush path exists**: pawns pushed to the nearest open cell, items destroyed outright,
  buildings damaged and eventually destroyed, on a `crushIntervalTicks` pulse. The 60% event is that
  behaviour, unthrottled and map-wide within the footprint.
- ⚠️ **The warning must be unmistakable.** A colonist standing in the wrong chamber can die. The
  `creakWarningTicks` grace already exists per cell; at 60% the player needs a single unmissable
  signal for the whole bole, not per-cell creaks they may not be watching.

### 2c. 70% — The catastrophe

> *"An ultra-violent catastrophe, with huge logs smashing down destroying everything in its wake.
> Buildings, animals, anything gets crushed by all the falling debris."* — owner, 2026-09-23

- **Unsafe within 50 cells.** Anything in that radius is crushed by falling debris.
- **Normally reached by explosive attack**, because mining cannot outrun the healing (§1).
- **Yields a huge amount of wood, grubs and fruit** — the largest single payout in the biome.
- 🔴 **Severe relationship hit with the Wildsteam Clan.** See §8; it is a sacrilege, not a penalty.
- **The tree is dead. Once dead, it's dead.** No regrowth, no fruit, ever.

**What it leaves, permanently** — owner ruling, all three together:

1. A **sunken stump crater** where the footprint was, mineable.
2. A **field of enormous fallen trunk segments** that stay for good — cover, obstacle, slow harvest.
3. A **dead standing husk**: hollow, no healing, freely buildable inside.

⚠️ **This deliberately overlaps the sealant's prize, and the owner ruled the overlap is not real.** His
distinction, verbatim: *"The sealant only seals SOME areas, while the rest of the tree heals and
remains alive and harvestable. Once dead, it's dead."*

⇒ 🔑 **Sealing is a compromise with a living thing; the catastrophe ends the relationship.** A sealed
colony lives inside a tree that is still growing, still fruiting, still dangerous at its edges. A husk
colony lives in a corpse that will never give them anything again. ⛔ Do not "resolve" this as
duplication.

---

### 2d. Fruitfall — the non-destructive route, and the design's missing half

**A random event: one or two fruits simply fall, along with a few grubs.** Owner ruling 2026-09-23.

🔑 **This completes the economy, and it is the piece that makes the pilgrims survivable.** Without it
the *only* way to obtain fruit is to wound the tree — so any player who wants Royal Rind must commit
sacrilege (§8a). With it, the fruit has **two routes with opposite costs**:

| route | speed | cost |
|---|---|---|
| **Fruitfall** | slow, random, uncontrollable | none — the tree gave it |
| **The Great Shaking** | on demand, in quantity | interior damage, grub influx, and a visible wound the pilgrims will judge |

⇒ **Patience or sacrilege.** ⛔ Do not make Fruitfall generous enough to substitute for a harvest, and
⛔ do not make it so rare that shaking is the only real option — the whole point is that both are
viable and they cost different things.

⚠️ **Grubs come with Fruitfall too**, so even the peaceful route is a small fight. There is no way to
get this fruit without meeting what eats it.

## 3. The fruit and its three products

**Greatbole fruit** — huge, purple, brought to a **butcher table** and rendered out. One fruit, three
products, and they are **one economy rather than three perks**: food, gear and infrastructure all
answer *"how do you go somewhere terrible and come back"*, which is this campaign's whole question.

### 3a. Fruit steaks — ridiculously satiating

Expedition food. ⚠️ Tune against the biome's existing *"tremendous food abundance"* ruling
(`GREENTIDE_RISK_REWARD_EXCHANGE_1`, binding as of 2026-09-22) — abundance is intended here, so this
is not the thing to be timid about. Obvious cuisine input.

### 3b. Royal Rind — the gear material

⇒ **Named `Royal Rind` by the owner**, replacing "fruit leather", which in English already means a
dried-fruit snack and would have fought every apparel tooltip it appeared in.

**All three of its uses are ruled in** (owner: *"It's all three"*):

1. **Protection against our own killing biomes** — the Contagion, the Scald, the Miasma. 🔑 This makes
   the jungle the gateway to the rest of the planet, which is the strongest reason to brave it, and it
   needs no expansion.
2. **A vacuum/space garment**, gated behind the expansion that supplies that mechanic. ⛔ The
   franchise-free mod's protection must not *depend* on it.
3. **One of the most valuable luxury materials on the planet.** Apparel, trade, thrones.

🔴 **The price of the best material in the game is a genuinely nasty fight** — owner: *"those grubs are
NASTY to deal with."* That is the balance, stated: not scarcity, not a timer, difficulty.

### 3c. Seeds — the fast greatbole, and the loop closing

A seed plants **`RM_Greatbole`**, the mature fellable giant of the same species (roster row 22).

- **Adjacent water is REQUIRED** — no water, no growth at all. ⇒ Riverbanks become strategic ground.
- **Growth is stupendously fast and visibly so** — it climbs growth stages far faster than anything
  else on the map, and the player can watch it.
- ⚠️ **UNMEASURED:** whether a plant's growth rate can read adjacent terrain at all. See §10.

🔑 **The species becomes a closed loop the player can run end to end**, and nothing else in this
project does: mine the ancient bole → shake it → fruit → seed → plant by water → a giant grows fast →
fell it for hardwood → and by the owner's own life-stage ruling, in centuries a greatbole becomes an
ancient bole again.

---

## 4. The grubs

**Arch-backed spiny grubs, purple — the same colour as the fruit.** They dwell high up and come down
only with a harvest. The fruit is their **one and only** food source.

### 4a. What they do

- **Approach and consume fallen fruit immediately.**
- **Attack anyone who comes near the fruit**, to defend it.
- **They breed fast while there is fruit to eat** — *"tribble-like"*, growing into an angry population
  swiftly if left unchecked.
- 🔴 **When the fruit runs out, they go Manhunter.**
- **A fixed number drops per Shaking**, regardless of history. ⇒ The drop is predictable; the
  *population* is what escalates.
- **They are a resource too**: **edible bugflesh**, and **spines that are a valuable trade good.**

### 🔑 4b. The dilemma this creates, which is the sharpest thing in the whole design

**Take the fruit and you starve them into a manhunter swarm. Leave the fruit and you breed them into
an army.** Both choices are bad, the player picks one every harvest, and neither is a punishment for
playing wrong — they are the two halves of one honest trade.

⇒ **This is the loop's only brake**, and the owner chose it knowingly: with fruit paying food, gear and
the planet's best luxury material, and grubs paying flesh and spines, **no yield limits anything.**
Difficulty is the entire bound. ⛔ Therefore the grub fight must be genuinely hard, and the population
curve must be legible — a brake nobody can see is not a brake.

---

### 4c. The grubs are hard to tell from the fruit, and the fruit is hard to carry

Both ruled in 2026-09-23, and they are **one moment from two sides** — the reason they were offered
together.

- **A fruit is huge and awkward: heavy, slow, hauled one at a time**, never pocketed. ⇒ The grubs stop
  being a base-defence problem and become a threat to your **haulers**, and every single fruit is its
  own decision about whether to go back for another.
- **Purple grubs on purple fruit read alike at a glance.** A fallen pile and a waiting grub are the same
  colour by the owner's original design; lean on it.
- 🔑 **Together:** a slow hauler walking up to a pile that might not be only fruit *is* the ambush. The
  awkward carry creates the exposure the camouflage exploits, and neither half needs a mechanic the
  other does not already supply.
- ⚠️ **The tell must exist for a player who is paying attention.** Being beaten by a mechanic is fair;
  being tricked by graphics is not, and the difference is whether a careful look can distinguish them.

## 5. The song — the tree's voice is a diegetic progress bar

Owner ruling 2026-09-23, specified precisely. 🔑 **Many plants on this world hum** — this is a property
of Ash'karr, not a quirk of one tree (see also `RM_Thalquith`, `GREENTIDE_HUMMING_GROVE_1`).

The greatbole's own soundscape:

1. **Baseline: an ultra-deep bass that slowly drifts.** Unique to the greatbole.
2. **Each time wood is cut, the pitch RISES.** 🔑 Physically correct as well as legible — a hollower
   resonating body genuinely rings higher, so the signal is what the object would actually do.
3. **Near a threshold: two disharmonious sounds overlap.** Consonance breaks.
4. **The harmonious blend returns only when the tree restores itself** — so the healing is audible too,
   and a player who backs off *hears* forgiveness.
5. **Near breaking: a truly unpleasant beat frequency with non-harmonious notes.**

⇒ **This is the warning the percentage ladder could not otherwise give.** The owner accepted an
invisible 40% threshold as a cost (§1); the song removes that cost without changing the trigger. ⛔ It
cannot be the *only* warning — a player with sound off must still be told.

### What this needs from the component built 2026-09-23

`RM_MapComponent_ProximitySoundscape` + `RM_ProximitySoundscapeExtension`
(`mandrake.rm.creaturebehaviors`) already do the hard part: several authored `SoundDef`s at different
pitches, layered, count-driven, with de-escalation hysteresis and a minimum change interval.

⚠️ **One generalisation is owed:** that component drives its layer count from **how many tagged Things
are near the listener**. The greatbole needs layers driven by an **external scalar** — how hollow this
bole is. ⇒ Make the driver pluggable (nearby-count *or* a supplied 0–1 value) rather than writing a
second soundscape. 🔑 This is the component's second consumer, which is the moment to generalise it
rather than copy it — the same reasoning the owner applied to the reaction mechanism.

### 🔴 UNMEASURED, and one part may not be achievable as described

- **Dissonance is straightforward**: two overlapping sustainers at clashing authored pitches. Safe.
- **A true beat frequency is not.** Beating requires two tones a few Hz apart holding a phase
  relationship, and sound engines commonly randomise playback start phase. ⇒ If the engine will not
  sustain it, **bake the beating into a single authored sound file** rather than producing it from two
  live layers. Either route gives the unpleasant throb. ⛔ Do not claim the live two-layer version
  works until it has been heard.

## 6. Fire cannot excavate it — ruled 2026-09-23

The biome's fire ruling is that jungle plants take fire damage without igniting, which would otherwise
make burning a quiet third excavation route. ⇒ **The heartwood is too dense to burn out**: fire scorches
the surface and achieves nothing structural, consistent with wood described as *"packed tight enough to
dig into like rock."*

🔑 **Why this matters more than it looks:** a cheap slow burn route would have deleted the best emergent
detail in the design — that only explosives can reach 70% (§1). ⛔ Keep it closed.

## 7. Thermal sanctuary — why anyone would live in a thing that crushes them

**Chambers inside a greatbole hold a constant temperature: that of the deep ground.** Owner ruling
2026-09-23, with its own mechanism — *"all the water coursing through the tree's flesh upwards"* acts as
a permanent thermal blanket.

⇒ **The finest shelter on Ash'karr is alive and slowly trying to close on you.** That is the biome's
exchange in one object, and it converts "you can live inside" from a curiosity into the strategic prize
that justifies the sealant.

🔑 **And the water explains two things with one fact:** it is why the chamber holds deep-ground
temperature, and it is why a **seed requires adjacent water to grow at all** (§3c). Both ends of the
species' life run on the same sap column. ⇒ State it that way in the descriptions; it is the kind of
coherence a player notices.

⚠️ **Accepted cost:** this makes a greatbole the obvious best base site, so a player who understands the
mechanic will always want one. That is intended — but it means the crushing, the grubs and the pilgrims
are what keep it honest, and all three must bite.

## 8. The Wildsteam Clan — a sacrilege with an atonement

✅ **MEASURED from their own authored cast** (`design/Jawa/bridge/INHABITED_CAST_WILDSTEAM.md`, live,
authored 2026-08-20): the Wildsteam Clan's faith is **the Green Oath** — `Structure_Animist`,
`NaturePrimacy`, **`TreeConnection`**, `Collectivist`, `AnimalPersonhood` — and its **taboo is,
verbatim, "cutting a living tree."** They are *"the only faction that plants."*

⇒ 🔴 **The 70% catastrophe is not a diplomatic inconvenience. It is the worst act available to a player
in their eyes**, and it needs no new fiction to justify — their religion already forbids it.

⇒ ✅ **And the seed is the atonement — owner ruling 2026-09-23, a real diplomatic route.** Planting a
greatbole raises Wildsteam standing; a grown one raises it more. Planting is their own sacrament,
performed by an outsider.

🔑 **One fruit therefore contains both the atrocity and the apology**, and the whole relationship track
is built out of a taboo that already existed.

⚠️ **The stated cost, accepted:** goodwill becomes farmable if seeds are plentiful. ⇒ Cap the gain, or
tie it to the planted tree **surviving** — which also makes a player who plants and then fells look
exactly as cynical as they are.

---

## 8a. The pilgrims — and the tree's own body is the moral ledger

Owner ruling 2026-09-23. **Pilgrims arrive to see the greatbole.** In the campaign they are Wildsteam;
🔴 **without the Utinni scenario they are generic pilgrims**, so this is `RM_`-tier content with a
campaign skin, not campaign-only content. (Consistent with the tier ruling that the line is IP, not
flavour.)

**What they come for, in his words:** they revere the tree **not as a unique thing** — they travel *"from
one to another to learn the wisdom each teaches in its song."*

⇒ 🔑 **They come to LISTEN.** The song (§5) is the object of the pilgrimage, and the song is changed by
what the player did to the tree. **So the pilgrims judge the mining by its sound.** The hum stops being a
warning system and becomes the thing another faction travels across a planet to hear — which is the
single most satisfying connection in this design and it was not designed, it was noticed.

### Their reaction is a function of how much of the tree is missing when they arrive

And the distinction he drew is the important part:

| what they find | how they read it |
|---|---|
| **Rooms sealed with sap** | ✅ **Does not count against the player.** A closed cut is a healed thing the tree has accepted. |
| **Mined-out areas still trying to regrow** | 🔴 **Open wounds.** They are **furious, or even enraged.** |
| **Witnessing a Great Shaking** | 🔴 **They attack outright.** |

🔑 **The tree's own state is the moral ledger, and nothing else is.** Not a counter, not a hidden
reputation number — the pilgrims look at the wood. ⇒ Three consequences worth stating plainly:

1. **Sealing is morally as well as practically correct.** The Green Oath forbids *cutting a living tree*,
   and a sealed chamber is a cut that has stopped being one. A player who seals every room can live
   inside their god and be welcomed.
2. **Time launders sin.** An unsealed cut that has fully regrown is no longer a wound, so waiting for the
   healing is genuine atonement — the same mechanic that punishes greed at 60% forgives it at leisure.
3. **The worst thing a player can do is be caught mid-harvest.** Not the harvest itself — being *seen*.

⚠️ **UNMEASURED:** how a visiting group's disposition can be set from a map-state reading at arrival, and
how "witnessing an event" is detected while they are present. ⛔ Do not name a mechanism for either from
reasoning.

⚠️ **They must be announced far enough ahead** that a player can seal, stop, or hide — otherwise the
mechanic is a dice roll rather than a decision, and the whole point is that the player chooses what the
pilgrims will find.

## 9. ✅ What is ALREADY BUILT — measured 2026-09-23, six mechanisms

🔑 **This concept is far cheaper than it looks. Four of the six are shipped.**

| the need | what serves it | state |
|---|---|---|
| "how much has been removed" | `BoleRecord.footprint` (HashSet of cells) + `timers` (per-cell), both Scribed | ✅ computable today, no new tracking |
| the Shaking's warning, and the 60% crush | `RM_MapComponent_LivingRegrowth` — creak with sound, then a crush pulse pushing pawns out and destroying items | ✅ shipped; needs a whole-bole escalation |
| **permanent habitation** | `RM_ToxinSealant` (item, crafted from `RM_SapResin` at `TableMachining`) + `RUT_ToxinSealant` (terrain), and regrowth **already gates on the cell's terrain being it** | ✅ **shipped and wired** |
| grubs eat only fruit | `RM_EatCleanableExtension` — forages data-listed item defNames and consumes them, and deliberately **fires for wild pawns** | ✅ shipped; add the fruit to a list |
| grubs guard the fruit | `RM_ParentalEnrageExtension` + `RM_CompParentalEnrage` — proximity to a guarded thing triggers a scoped rage on that one intruder, **no warning** | ⚠️ shipped for guarding *young*; needs one axis widened to guard an **item** |
| the tree's song | `RM_MapComponent_ProximitySoundscape` + `RM_ProximitySoundscapeExtension` — layered authored SoundDefs at different pitches, hysteresis, minimum change interval | ⚠️ built 2026-09-23; driver must become pluggable (nearby-count **or** a supplied scalar) |
| tribble breeding + an anger curve | `RM_CompVerminBreeder` (interval spawner, lord-free) + `RM_MapComponent_VerminPopulation` (soft/hard caps, a meanness curve that ramps aggression between them) + `RM_Alert_VerminPopulation` (a player-facing alert) | ⚠️ shipped; **does not gate on food** — needs "breed only while a named food exists" |

### The genuinely new work, and it is a short list

1. The **threshold ladder** reading the footprint, and the three events.
2. **Widen the guard extension** from "guards young" to "guards a thing".
3. **Add a food condition** to the breeder, and the **Manhunter-on-famine** flip.
4. The **fruit item**, the **butcher recipes**, and the **three products**.
5. **Royal Rind's** protection mechanics, and the gear.
6. The **seed**'s water requirement and fast visible growth.
7. **Gorbeleth toxin** as the sealant's reagent (§11).
8. The **Wildsteam** goodwill hooks, both directions, and the **pilgrim visit** with its map-state reading (§8a).
9. **Fruitfall** as a random event (§2d), and the **awkward-haul** property on the fruit (§4c).
10. The **thermal blanket** holding chambers at deep-ground temperature (§7).
11. **Pluggable driver** on the soundscape component, plus the greatbole's own authored hum layers (§5).

---

## 10. ⚠️ UNMEASURED — the Mac has no game, no def dump, no decompiler

⛔ Name no field, class or value for any of these from reasoning. Everything in §9 was read from our
own source; everything here needs the Desktop.

1. **Whether a plant's growth rate can read adjacent terrain**, for the seed's water requirement. The
   single largest unknown, because §3c's whole appeal rests on it.
2. **How an earthquake-like event is presented** — screen shake, sound, letter — and whether a
   camera shake exists that is not tied to something else. (Our bridge calls
   `Find.CameraDriver.shaker.DoShake(...)`, which is evidence the capability exists; it is not
   evidence of how an event should use it.)
3. **How to crush everything in a 50-cell radius** — an explosion, a series of falling things, or a
   custom pass — and what that costs on a full map.
4. **How a pawn's race can be flipped to Manhunter conditionally**, and whether it can be flipped
   back when fruit returns.
5. **Whether "visibly grows fast" needs anything at all** beyond a short `growDays` — growth stages
   may already render it.
6. **How biome protection is expressed** for Royal Rind gear, per biome, and whether the Contagion,
   Scald and Miasma hazards are even stat-gated today.
7. **What a butcher-table recipe on a plant product looks like**, and whether one recipe can yield
   three distinct products in one pass.
8. **Whether a sustainer pair can hold a beat frequency**, or whether the beating must be baked into a
   single authored file (§5). The only part of the song that may not be achievable as described.
9. **How a chamber can be held at deep-ground temperature** (§7) — whether that value is readable and
   whether a room's temperature can be pinned to it rather than merely insulated toward it.
10. **How a visiting group's disposition is set from a map reading at arrival**, and how "witnessing an
    event" is detected while they are on the map (§8a).
11. **Whether hauling can be made deliberately awkward** per-item — a mass high enough to force one at a
    time without making the fruit unhaulable (§4c).

---

## 11. Small ruled details

- ✅ **Gorbeleth toxin is the sealant's caustic reagent** — owner ruling. The sealant's own
  description already says *"cut and cooked with a caustic reagent"*, and the roster already wrote
  gorbeleth as *"the understory's ranged hazard. Its toxin is worth extracting, which means going
  close."* ⇒ **That is now true**: living permanently inside a greatbole requires going close to
  something that shoots at you. 🔑 Third time this session the roster had already said where a thing
  comes from — see also the wasps' hosts and the ant hive's farm.
- **Mod Settings**, per the standing every-mod-ships-settings rule: each of the three thresholds is
  exactly the "a number is the experience" case, plus toggles for the catastrophe and for the grub
  breeding.

## 12. Watch out

- 🔴 **The 50-cell blast radius is larger than most players' whole base.** A colony built near a
  greatbole is inside it. ⇒ That is the intent — but it means the 70% threshold must be
  *unreachable by accident*, and the explosives-only route already helps.
- 🔴 **Regrowth state is Scribed and this is live shipped content.** Any change to the footprint,
  radius or def names risks existing saves. ⛔ Not a draft.
- ⚠️ **`FEVER_WOOD_MECHANICS_1` is blocked on `RM_MapComponent_LivingRegrowth`** (its F7, bore-caves /
  Greatbole reuse), and `RUT_FeverTrunkCore` is a sibling using the same machinery. ⛔ Everything added
  here must stay content-blind — the component names no bole, no biome and no Greentide today.
- ⚠️ **Three of the four widened mechanisms live in `mandrake.rm.creaturebehaviors`**, which ships zero
  content of its own on purpose. ⛔ Keep the grub's defs in a content mod; widen the generic behaviour
  only.
- ⚠️ **The grubs pay flesh, spines and the fruit pays everything.** If the fight is ever easy, this is
  the most profitable loop in the game. ⇒ Grub difficulty is not flavour; it is the feature's balance,
  and it should be reviewed by playing rather than by reading a table.
