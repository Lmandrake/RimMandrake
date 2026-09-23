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
- 🔴 **Severe relationship hit with the Wildsteam Clan.** See §5; it is a sacrilege, not a penalty.
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
- ⚠️ **UNMEASURED:** whether a plant's growth rate can read adjacent terrain at all. See §7.

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

## 5. The Wildsteam Clan — a sacrilege with an atonement

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

## 6. ✅ What is ALREADY BUILT — measured 2026-09-23, six mechanisms

🔑 **This concept is far cheaper than it looks. Four of the six are shipped.**

| the need | what serves it | state |
|---|---|---|
| "how much has been removed" | `BoleRecord.footprint` (HashSet of cells) + `timers` (per-cell), both Scribed | ✅ computable today, no new tracking |
| the Shaking's warning, and the 60% crush | `RM_MapComponent_LivingRegrowth` — creak with sound, then a crush pulse pushing pawns out and destroying items | ✅ shipped; needs a whole-bole escalation |
| **permanent habitation** | `RM_ToxinSealant` (item, crafted from `RM_SapResin` at `TableMachining`) + `RUT_ToxinSealant` (terrain), and regrowth **already gates on the cell's terrain being it** | ✅ **shipped and wired** |
| grubs eat only fruit | `RM_EatCleanableExtension` — forages data-listed item defNames and consumes them, and deliberately **fires for wild pawns** | ✅ shipped; add the fruit to a list |
| grubs guard the fruit | `RM_ParentalEnrageExtension` + `RM_CompParentalEnrage` — proximity to a guarded thing triggers a scoped rage on that one intruder, **no warning** | ⚠️ shipped for guarding *young*; needs one axis widened to guard an **item** |
| tribble breeding + an anger curve | `RM_CompVerminBreeder` (interval spawner, lord-free) + `RM_MapComponent_VerminPopulation` (soft/hard caps, a meanness curve that ramps aggression between them) + `RM_Alert_VerminPopulation` (a player-facing alert) | ⚠️ shipped; **does not gate on food** — needs "breed only while a named food exists" |

### The genuinely new work, and it is a short list

1. The **threshold ladder** reading the footprint, and the three events.
2. **Widen the guard extension** from "guards young" to "guards a thing".
3. **Add a food condition** to the breeder, and the **Manhunter-on-famine** flip.
4. The **fruit item**, the **butcher recipes**, and the **three products**.
5. **Royal Rind's** protection mechanics, and the gear.
6. The **seed**'s water requirement and fast visible growth.
7. **Gorbeleth toxin** as the sealant's reagent (§8).
8. The **Wildsteam** goodwill hooks, both directions.

---

## 7. ⚠️ UNMEASURED — the Mac has no game, no def dump, no decompiler

⛔ Name no field, class or value for any of these from reasoning. Everything in §6 was read from our
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

---

## 8. Small ruled details

- ✅ **Gorbeleth toxin is the sealant's caustic reagent** — owner ruling. The sealant's own
  description already says *"cut and cooked with a caustic reagent"*, and the roster already wrote
  gorbeleth as *"the understory's ranged hazard. Its toxin is worth extracting, which means going
  close."* ⇒ **That is now true**: living permanently inside a greatbole requires going close to
  something that shoots at you. 🔑 Third time this session the roster had already said where a thing
  comes from — see also the wasps' hosts and the ant hive's farm.
- **Mod Settings**, per the standing every-mod-ships-settings rule: each of the three thresholds is
  exactly the "a number is the experience" case, plus toggles for the catastrophe and for the grub
  breeding.

## 9. Watch out

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
