# balance_paradigm.md — why we would change any number in this game

_Started 2026-08-10. The decision framework for normalising, cutting and
re-skinning the 562-mod stack. Companion to `concept.md` (pillars),
`desert_world_design.md` (the world), and `observed/2026-08-13/inventory/` (the measured data)._

**Status:** paradigm, not a work order. Every measured claim below is from
`observed/2026-08-13/inventory/animals.csv` + the live def dump, 2026-08-10.

---

## 0. The prime directive

> **The player must be able to read the world at a glance, and be right.**

Every change we make serves one of three readabilities:

1. **Silhouette** — you can tell *what* something is without clicking it.
2. **Signal** — you can tell *how dangerous* it is before you commit.
3. **Consequence** — the engagement resolves fast and memorably, in a way you
   can tell a story about afterwards.

"Cinematic" is not decoration. A scene is cinematic when the numbers made the
story inevitable: the blaster bolt that dropped a raider in one hit, the thing
in the dunes that ate three colonists because it was simply too big to stop.

**The enemy is mush.** Not imbalance — *sameness*. A world where everything is
within 3× of everything else has no scenes in it.

---

## 1. What the data says right now

Measured, not asserted. These are the violations that justify the work.

### 1.1 Size does not mean danger (the flattest curve in the game)

| body size (human = 1.0) | n | median attack power |
|---|---|---|
| small (0.2–0.6) | 209 | **6** |
| human-ish (0.6–1.5) | 341 | **9** |
| large (1.5–3) | 285 | **14** |
| huge (>3) | 314 | **20** |

A **15× increase in body mass buys 3.3× damage.** And the *maximum* for
human-sized creatures (64) is higher than for large ones (54). The worst
offenders are exactly the animals that should be set-pieces:

- `Paraceratherium` — body size **15**, attack power **19**
- `GR_Paraceramuffalo` — size **16**, power **17**
- `GR_Mechamuffalo` — size **13**, power **6**
- `AA_Behemoth` — size **8**, power **18**

A colonist with a decent rifle is in no real danger from any of them. **The
biggest creatures in the game are currently speed bumps.**

### 1.2 Biomes have no apex, and no vermin

- **42 of 63 biomes have fewer than 2 apex predators** (size ≥ 2 and power ≥ 25).
  Many have zero: `AB_IdyllicMeadows` (22 animals, 0 apex), `AB_MycoticJungle`
  (11, 0), `AB_PropaneLakes` (6, 0).
- **39 of 63 biomes contain no tiny creature at all** (< 0.2 body size) —
  including `LavaField` with 44 animals and `SeaIce` with 31.

So the two ends of your ecology rule — the terror and the vermin — are the two
things most often missing.

### 1.3 Endemism is broken

- `Rat` appears in **38** biomes. `Boomalope` in 31. `GuineaPig` in 25.
- **Only 8% of animals (54 of 669) are unique to a single biome.**

Crossing a biome boundary currently changes the scenery and almost nothing else.

### 1.4 Consumables are thin

- Only **41%** of animals have any renewable yield (milk / wool / egg).
- **346 animals drop no leather at all** — they leave nothing behind but meat.
- 151 distinct leather types exist, but the distribution is long-tailed: most
  animals share a handful of generic hides.

---

## 2. The axes of justification

Nine reasons we would ever touch a value. Any proposed change should name one.

### Axis 1 — Separation over granularity

**Rule: adjacent tiers differ by ≥ 2×, never by 20%.**

Fine gradations are invisible during play. If two things are meant to feel
different, they must differ by a factor the player can perceive without a
spreadsheet. If they cannot be separated by 2×, they should be *merged or cut*,
not tuned. Sameness is the disease; separation is the product.

### Axis 2 — Tech is a threshold, not a slope (weapons)

**Rule: crossing a tech tier should feel like changing games, not upgrading a
stat.**

- A weapon that requires a new technology or introduces a new *effect* must be
  **conspicuously** better — not marginally efficient.
- **Blasters resolve, they do not grind.** Time-to-kill against an unarmoured
  target should be **1–2 shots**. A firefight is decided by positioning,
  cover and who shoots first — never by who has more ammunition patience.
- Balance the drama with **accuracy, cooldown, heat and scarcity**, not by
  shaving damage. A blaster that *misses* is tension. A blaster that *plinks* is
  tedium.
- **New effect = new verb.** Stun, burn, pin, knockback, overpenetration. Effects
  are the reason to carry a second weapon, and the reason a fight has phases.

### Axis 3 — Mass is menace (animals)

**Rule: threat scales superlinearly with size, and the big things are events.**

#### 3.1 The Size Ladder (formalised 2026-08-10)

Human = 1.0, and **human-sized is deliberately unremarkable**. The world runs
from an order of magnitude below us to an order above, commonly — then jumps.

| tier | body size | role | how common |
|---|---|---|---|
| **Vermin** | 0.05 – 0.15 | scale contrast, oddity, speed, comic relief | common |
| **Small** | 0.15 – 0.5 | staple prey, pests, pets | common |
| **Middling** | 0.5 – 2 | the human band — *nothing special happens here* | common |
| **Large** | 2 – 10 | real threats, beasts of burden, big game | **common** |
| — | *10 – 50* | **deliberately empty** | — |
| **VAST** | 50 – 150+ | terrain-scale horrors; threaten structures, vehicles, ships | 1 per region |

**The empty band is the whole design.** If size is a smooth continuum, VAST is
merely "the biggest number" and the player reads it as more-of-the-same. A gap
turns it into a *category change* — the moment you see one you know you are in a
different kind of story. Same reasoning as the tech-threshold rule (Axis 2):
discontinuity is what carries meaning.

**Measured 2026-08-10 — the VAST tier does not exist.** Largest animal in the
whole 562-mod stack is `GR_ArchotechCentipede` at **20**; only 17 animals of
1,194 exceed size 10, and **zero** reach 50. Distribution: 15% below 0.5, 43%
in the human band, 41% large, 1.4% in the 10–50 gap.

Two consequences:
- **VAST must be authored, not selected.** Nothing in the stack can be promoted
  into it by tuning alone; these need bespoke work — and there should be only a
  handful, so that is affordable.
- **The vermin end is underpopulated too** (only 2 animals below 0.1). "Tinyness
  should be common" is currently false and is the cheaper half to fix.

#### 3.2 VAST creatures are terrain, not encounters

At two orders of magnitude the normal combat contract stops applying. A VAST
creature is a **world condition** that happens to be alive:

- It damages **structures**, not just pawns. It can remove a section of base.
- It is answerable at **ship-weapon scale**, by terrain, or by not being there.
- It is **telegraphed** long before contact — tracks, kills, migration rumours,
  the silence of everything else. Never a surprise; always a decision.
- **One per region**, and it should have a *name*, not just a defName.
- Killing one is a **campaign milestone** with a unique, unrepeatable payoff.

#### 3.3 Speed is the tax on mass — and it is currently unpaid

Measured median move speed: tiny/small **3.50**, human band **4.00**, large
**4.20**, huge **4.00**. Big things are marginally *faster* than small ones —
exactly backwards. `GR_ArchotechCentipede` is size 20, power 200, **speed 10**:
a fast unavoidable nightmare, which is the unfair kind.

**Rule: above the human band, every step up in mass buys a step down in
mobility** — slower, or shorter stamina, or territorial, or dormant until
provoked. The player must be able to *choose* the fight. Fast + huge is reserved
for scripted, rare, story-critical horrors, and even then it should be
escapable by terrain.

- Damage and health should rise **faster** than linearly with body size. Anything
  meaningfully larger than a human should require **many** hits from even a good
  weapon, and should be able to kill a colonist in one or two.
- **Counterweight, mandatory:** a thing that can kill you must be *escapable by
  decision*. Big = slow, or telegraphed, or territorial, or asleep. Danger the
  player can see coming and choose to avoid is drama; danger that simply happens
  is a load-game.
- Corollary: **speed is the balancing lever for size.** A huge fast pack animal
  is not a set-piece, it is a rout.

### Axis 4 — Armour gates categories, it does not shave percentages

**Rule: armour changes *which* threats matter, not how much everything hurts.**

- **Leather is anti-claw, not anti-blaster.** It should be genuinely good against
  melee and teeth, and near-worthless against energy weapons.
- **Advanced armour ≈ 5 shots to kill** from a standard blaster. That is a
  contract, and it is what makes armour worth the industry to make.
- This gives materials *identity*: you dress for the wildlife or you dress for
  the war, and being wrong is a real mistake. Uniform damage reduction produces
  one correct answer and no decisions.

### Axis 5 — Ship weapons are a different caliber of thing

**Rule: an order of magnitude, and a category change.**

- Ship weaponry should trivially delete infantry and be answerable only by other
  ship-scale systems, shields, or terrain.
- Its narrative job is to **change the genre of a scene**. When a turbolaser
  enters the story, the question stops being "can we win the firefight" and
  becomes "how do we not be here".
- **Guardrail (pillar §19.5):** player access stays quest-earned and
  infrastructure-bound. Ship weapons are a *threat category*, not a tool the
  colony scales into.

### Axis 6 — Ecology is authored scenes, not a species list

**Rule: every tile must contain at least one story.**

The per-biome contract:

| slot | requirement | why |
|---|---|---|
| **Apex** | ≥ 2 genuinely terrifying — by size, ability, or pack behaviour | the tile has a *predator*, and the player learns its name |
| **Vermin** | ≥ 1 tiny, innocuous, ideally strange or very fast | scale contrast; makes the apex read as huge |
| **Staple** | a mid-tier huntable that defines the local economy | gives the biome a flavour of survival |
| **Signature** | ≥ 1 species found *only* here (or in ecologically adjacent tiles) | makes travel a discovery |

**Endemism rule:** an animal may appear in N biomes only if those biomes are
ecologically adjacent. Generic species (`Rat` in 38 biomes) get cut back hard.
Target: median biomes-per-animal ≤ 3.

### Axis 7 — Everything leaves something behind

**Rule: every creature yields a story object.**

Each notable animal should produce a distinctive consumable — either renewably
or on death. This converts hunting from *calorie acquisition* into *collecting*,
and gives rare creatures value beyond the fight.

Families: **glands** (drugs/medical), **hides** (crafting identity), **organs**
(tech components), **venom/ichor** (weapon coatings), **eggs/milk** (food).

- **Guardrail:** must not create a farm loop. The standing rule holds — never
  ranch a tamed breeding herd into a meat/leather/wool printer. Prefer
  *hunt-drops* and *rare* yields over renewable ones for anything valuable.
- **Uniqueness budget:** we cannot author 1,196 unique consumables. Tier it —
  apex and signature species get bespoke drops; the rest share a small,
  well-named family of materials.

### Axis 8 — Droids obey a different physics

**Rule: droids are not "robot animals". They fight differently.**

- **Physically delicate** unless purpose-built for war — a protocol droid should
  come apart. Combat droids should *look* armoured, and be.
- **Slow.** Droids do not sprint. Their menace is inevitability, not speed.
- **Poor unarmed, better armed.** They are tools that were never meant to brawl.
  A droid with a blaster is a soldier; a droid without one is scrap that walks.
- **No fear, no pain, no bleeding.** They do not rout, cannot be demoralised, and
  ignore effects that work on flesh — so the player must solve them differently
  rather than harder.

### Axis 9 — Alienness is a selection filter

**Rule: prefer the Star-Wars-strange; cut the Earth-mundane.**

Favour unusual silhouettes, non-Earth colour logic, odd locomotion, and
behaviours that carry a story (pack ambush, mimicry, symbiosis, burrowing,
gas-bag flotation). Cut redundant terrestrial fauna that adds a row and no scene
— the contact sheets in `observed/2026-08-13/inventory/contact_sheets/` are the instrument for
this, and they make whole mods judgeable as a block.

**Largeness and tinyness should both be COMMON.** The default RimWorld world is
full of dog-sized things. Ours should be full of things that are either
alarmingly big or startlingly small, because that is what makes the mid-range
feel like *home*.

### Axis 10 — The verb budget: damage is one axis of many

**Rule: a weapon is defined by its VERB. A weapon with a unique verb needs no
damage at all to justify its existence.**

The ion weapon is the template: **virtually zero damage, entirely new
possibility.** We want more of these, not fewer, and they are the cheapest way to
add tactical depth without adding power.

Verbs worth building around: **disable** (ion/EMP), **stun**, **burn**,
**pin/entangle** (nets, adhesives), **blind/sensor-kill**, **fear/rout**,
**corrode** (armour degradation), **displace** (knockback, gravitic),
**suppress** (area denial), **reveal** (marking, tracking).

Three properties make this axis valuable:

1. **It creates rock-paper-scissors without inflation.** Ion trivialises droids
   and does nothing to a rancor. Stun works on flesh and not on machines. Fire
   beats armour and not heat-adapted fauna. The player's answer to a problem is
   *which tool*, not *how much gun* — which is precisely the anti-exponential
   pillar (§Axis 4 / tension 3.4) expressed as a weapon rule.
2. **It makes loadout a real decision.** A squad carrying four identical rifles
   is a spreadsheet; a squad carrying a rifle, an ion gun, a net and a
   flamethrower is a *plan*.
3. **It is deeply Star Wars.** Stun blasters, ion cannons, nets, carbonite,
   tractor beams — the setting's iconic weapons are mostly *not* about damage.

**Corollary — the utility weapon must not be strictly worse.** A zero-damage
weapon has to be the *only* answer to something, or nobody carries it. Every
verb needs at least one enemy class that hard-requires it.

### Axis 11 — The showmanship rule: abilities must actually fire

**Rule: if a creature has an ability, it must use it several times per
encounter — visibly, and often just for fun.**

An ability that triggers once per campaign under rare conditions is authoring
spent on something no player will ever attribute to the creature. Worse, it is
invisible: the player cannot learn a rule they never see.

- **Frequency over potency.** Short cooldowns, low trigger thresholds. A weaker
  ability used five times per fight beats a devastating one used never.
- **Telegraph it.** Wind-up, sound, animation, visual tell. A telegraph is what
  converts an ability from "unfair damage" into "a mechanic I can play against".
- **Idle use is characterisation.** Let creatures use harmless versions of their
  abilities when nothing is happening — spitting, burrowing, inflating,
  flickering, mimicking. This is free personality, it teaches the player the
  ability *before* it matters, and it makes the world feel inhabited rather than
  spawned. **This is the "even just for fun" clause, and it is load-bearing.**
- **Measured gap:** only 2 animals in 1,194 explode on death and only 77 have any
  death action at all. The most common non-production comps are Anomaly
  infrastructure inherited from the base def, not authored behaviour. **The
  ability space is nearly empty** — this is the largest cheap win available.

### Axis 12 — Counterplay plurality

**Rule: every threat has at least two answers, and at least one that is not
"shoot it".**

Fight, flee, trap, terrain, bait, bribe, wall off, out-wait, out-range. A threat
with exactly one answer is a gate; a threat with three is a *situation*. This is
what stops superlinear lethality (Axis 3) from becoming load-scumming, and it is
mandatory for anything VAST.

### Axis 13 — The teaching ladder

**Rule: the world teaches its rules through survivable encounters before it
tests you on them.**

Every dangerous mechanic wants a lesser cousin: juveniles of the apex, a small
pack version, a weak emitter of the same effect, a dormant specimen. The first
time a player meets a mechanic it should cost them a scare; the second time, a
colonist; never the run.

This is also what makes a lethal world *fair* rather than punishing — the
information was always available.

### Axis 14 — Setting physics first

**Rule: define the world's physical laws once; derive balance from them instead
of arbitrating case by case.**

If we settle what is true — energy vs kinetic, what ion does to electronics,
whether deflector shields stop fast projectiles but not slow blades, what
lightsabers cut, how armour interacts with heat — then most balance questions
answer themselves, consistently, forever. Without it every def is a fresh
argument and the world drifts.

This is the single highest-leverage document we do not yet have.

### Axis 15 — Ecology is relationships, not a species list

**Rule: biome rosters are authored as food webs, not menus.**

Per tile, the apex should *hunt* the staple; the vermin should *follow* the apex
to scavenge; something should be *inedible* and know it. Relationships generate
scenes the designer never wrote — the player arrives to find a kill already in
progress, and that is a story.

### Axis 16 — Rarity is a balance lever equal to damage

**Rule: tune how often a thing is seen as deliberately as how hard it hits.**

Encounter frequency determines meaning. A terror seen weekly is a chore; seen
twice a campaign it is legend. Most "too strong" problems are really "too
frequent" problems, and rarity is the cheaper fix — it costs no numbers and
preserves the creature's identity.

### Axis 17 — The attention budget

**Rule: the roster is capped by what a human can hold in their head, not by what
the mods provide.**

A player will meaningfully learn perhaps **60–100** creatures across a campaign:
their look, their threat, their drop. We currently ship **1,196**. The surplus is
not richness, it is noise that dilutes every good creature in the set.

This makes **selection the primary design act** and justifies aggressive cutting
on its own — before any tuning question is asked (see tension 3.5).

### Axis 18 — The Jawa Doctrine: the world is not a ladder

**Rule: progression is lateral, lumpy and lossy. You do not climb this world;
you survive it and occasionally get lucky.**

Standard RimWorld is a treadmill: build wealth → wealth raises raid points →
build better defences → repeat. It is smooth, legible, and it is *precisely the
thing we are trying not to make*. We want a world that is wild, alarming and
barely survivable — one where the story is scavenging, not scaling.

Four mechanisms, and the fourth is the one the physics already gives us:

**(a) Break the wealth→threat coupling.** That single feedback loop is the
engine of linear progression. Threat should track **where you are, what you
provoked, and what season it is** — not how much silver is on the floor. A VAST
creature does not care how rich you are, and neither should a sandstorm.

**(b) Power arrives as shards, not tiers.** The good things are **found**, not
unlocked: one lightsaber, one intact droid brain, one shield generator with
half its charge. Unique, irreplaceable, un-mass-producible. You cannot build the
next rung of a ladder that has no rungs.

**(c) Acquisition out of order is a feature.** You may hold a Jedi's blade
before you own a stone wall. That is not a balance failure — it is the best
story the game can tell, and it is exactly the Jawa fantasy: possessing
something magnificent you did not earn and barely understand.

**(d) Power decays, so it cannot be accumulated.** The physics already does this
work: powered weapons wear out and then **detonate** (`setting_physics.md` L17,
L18); armour ablates away under fire; machinery is one bad day from going up.
Nothing you find is permanent. **You are always scrounging**, because everything
you own is quietly running down — which is the Jawa condition stated as a
mechanic rather than a mood.

**Derives:** the campaign shape stops being a curve and becomes a **series of
lurches** — desperate stretch, sudden windfall, slow decay, desperate stretch.
That is the rhythm of the fiction we are writing, and it is unlike anything a
default RimWorld run produces.

**Guardrail:** lurching is not the same as arbitrary. Every windfall and every
disaster must be *legible in hindsight* — the player should be able to say why
it happened. Randomness we cannot explain is just noise, and noise is not story.

### Axis 18a — The opening tier: what the Jawa can make on day one

**Rule: the crew begins able to make junk, and the SHIP is what unlocks
everything else.**

This is the campaign's central novelty and it should be felt in the first hour.
Jawas are not manufacturers — they are **resellers**. Inheriting a Factory
gravship is an *unprecedented* situation for them, and the opening tier has to
make that legible by being genuinely meagre.

**Craftable from the start, at their own workstations:**
- **Makeshift weapons** — pipe guns, improvised kinetics (the VWE Makeshift tier).
- **Some melee** — blades and tools pressed into service.
- **Basic ion weaponry.** This is the Jawa *signature*, and it is doing three
  jobs at once: it is the one thing they can build themselves, it is the weapon
  that takes machines **intact** rather than destroying them (L17), and taking
  things intact is the entire scavenger economy. Faction identity, starting
  tech and economic doctrine landing on one weapon is as coherent as this design
  gets.

**Everything else is earned:** bought, looted, or unlocked by restoring a
Kolyska subsystem. The ship is the tech tree; the crew is not.

**Rare tools are KEYS, not upkeep.** A small number of specific tools gate
specific actions — a fusioncutter to open a sealed pod, a hydrospanner to
restore a subsystem. They are quest gates, not a maintenance tax. Requiring
tools for ordinary work adds micromanagement rather than story, and the campaign
already carries scarcity pressure from Axis 18d (everything decays). Tools
should be **legibility plus keys**: you can see which Jawa is the engineer, and
occasionally only she can open the door.

### Axis 18b — Droids: repair the body, scavenge the mind

**Rule: parts are manufacturable; minds are not.**

The creed is *"we give the second hand to what others discarded; we do not breed
new hands."* Rendered mechanically:

| layer | rule |
|---|---|
| **Droid parts** — arms, legs, reactors, sensors, shielding, fluid reprocessors | **craftable**, in the existing Makeshift → standard → Advanced tiers |
| **Droid chassis / whole droids** | **not** manufacturable |
| **Droid brain** | **rare loot only** — battlefield salvage, quest reward, trade |

The parts economy already exists and is already tiered exactly right: Outer Rim
Droid Depot ships `OuterRim_DroidArm_Makeshift` / `_Advanced`,
`OuterRim_DroidReactor_Makeshift` / `_Advanced`, plus legs, sensors, damage
shielding and fluid reprocessors. That maps onto Axis 18a without any authoring
— **makeshift parts on day one, advanced parts once the ship wakes up.**

**The brain is the gate, and L17 makes it scarce for free.** Machines detonate
when destroyed, so a brain recovered intact is a genuine prize rather than
loot-table filler. Killing a battle droid usually destroys what you wanted;
**disabling it with ion does not.** The scarcity is not a spawn-rate tuned in a
config — it is a consequence of how this galaxy's engineering works, and the
player can *act* on it by changing weapon.

This also gives the Free Droid Enclaves their treasure: for them, wealth is
**parts and memories**, not silver — and "the neutral droids taught us to tend
our own" is a quest reward that hands over technique, not a factory.

### Axis 19 — Failure should be interesting

**Rule: losing produces a story, not a reload.**

Maimings, prosthetics, lost caravans, a base section collapsed by something too
big to fight — RimWorld's real strength is that defeat generates narrative. Every
threat should have a *survivable-but-costly* failure mode, not just a lethal one.
If the only outcomes are "win" and "load", the encounter is badly built.

---

## 3. The tensions — and how we resolve them

These principles genuinely conflict. Naming the conflicts now prevents
re-litigating them per-item later.

**3.1 "Largeness should be common" vs "large should be terrifying."**
If everything is huge, huge stops signifying. → **Resolution:** size is common,
*apex status* is rare. Threat = size × aggression × ability. Most large creatures
are placid megafauna; a few are hunters. The placid ones make the hunters legible.

**3.2 "Blasters are lethal" vs "advanced armour takes ~5 shots."**
These are the same number pulling opposite ways. → **Resolution:** the 5-shot
contract is *standard blaster vs advanced armour*. Unarmoured is 1–2. A **heavy**
weapon deliberately breaks the contract — which is precisely why heavy weapons
exist and why armour is not an "I win" purchase.

**3.3 "Every animal has a unique consumable" vs 1,196 animals.**
Unaffordable. → **Resolution:** uniqueness budget, tiered by role (§Axis 7).

**3.4 Powerful gear vs the anti-exponential pillar.**
→ **Resolution:** power must be **lateral, not vertical**. New weapons grant new
*options* (effects, ranges, roles), not a bigger number the colony accumulates.
The player's power curve stays flat; their *vocabulary* grows.

**3.5 Tuning vs cutting.**
With 1,196 animals, **cutting is far cheaper than tuning, and improves the game
more.** → **Resolution:** selection is the *first* lever, always. A cut animal
costs zero balance work forever. Only tune what earned its slot.

**3.6 Danger vs fairness.**
Superlinear threat makes the world lethal. → **Resolution:** every lethal thing
must be *avoidable by information* — visible, slow, telegraphed, or territorial.
We are making a world that punishes carelessness, not one that punishes bad luck.

---

## 4. The decision procedure

For any item — animal, weapon, armour, droid — ask in order. Stop at the first
answer that resolves it.

1. **Does it earn a slot?** Unique silhouette, role, or story? → else **CUT**.
2. **What is its one-sentence role?** If it cannot be said in one sentence, it is
   a duplicate → **CUT or MERGE**.
3. **Is it legible?** Does it look and read like what it is? → else **RESKIN /
   RENAME** (this is also where Star Wars theming lands).
4. **Do its numbers match its role?** Check against the tier contracts →
   else **TUNE**.
5. **What does it leave behind?** → else **ADD YIELD**.
6. **Does it break a pillar?** (exponential power, ranch loop, arms race) →
   **GUARDRAIL** it.

---

## 5. How we will know it worked

The point of having measured the stack is that the paradigm is **falsifiable**.
All of these are computable from `observed/2026-08-13/inventory/` + the live dump:

| target | now | goal |
|---|---|---|
| size→power relationship | ~flat (3.3× over 15× mass) | superlinear |
| biomes with ≥ 2 apex | 21 of 63 | 63 of 63 |
| biomes with ≥ 1 tiny | 24 of 63 | 63 of 63 |
| median biomes per animal | high (`Rat` = 38) | ≤ 3 |
| animals endemic to 1 biome | 8% | substantially higher |
| animals leaving a distinct drop | 41% renewable, 346 with no leather | every *notable* species |
| TTK: standard blaster vs unarmoured | — | 1–2 shots |
| TTK: standard blaster vs advanced armour | — | ~5 shots |
| TTK: ship weapon vs anything infantry | — | 1, and it should not have been there |

Re-running the inventory after each pass tells us whether the design actually
landed, instead of whether it felt like it did.
