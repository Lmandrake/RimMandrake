# GREENTIDE_WASP_SWARM_1 — the jungle's insect danger: tiny wasps, hives on plants, stings that stack

## the ruling

**Owner, 2026-09-22.** Asked what fills the Greentide's empty insect axis — offered a new
creature, dropping the axis, or a brood riding the existing plants — he **wrote in a fourth
answer that takes the best half of two of them**:

> *"Let's do some very small, numerous wasps that boil out of hives attached to plants. They are
> easy to kill and sting you for a very small irritating HEDIFF, but multiple stings add up
> quickly and overwhelm."*

⇒ **A new creature of ours (so the fauna law is satisfied), whose hives live on the plants we are
already building (so it costs no separate nest and ties the insect axis to the flora axis).**

🔑 **The threat model is arithmetic, not lethality.** Every single wasp is trivial — easy to
kill, one negligible hediff. The danger is that nothing about any individual sting tells you to
stop, and the count does. ⇒ **The content is the moment a player realises they are already past
the point where retreating is cheap.** That is the same shape as the ant hive's *"you decide how
deep to go, and then you decide too late"*, expressed in the open instead of in a corridor.

## 🔑 This is the FOURTH occurrence of one mechanism — build it once

A hive attached to a plant that **boils out** when disturbed is an alarm that propagates from a
plant-borne Thing. That is already three other things:

- **`RM_CompPlantAlarm`** (`src/RimMandrake/CreatureBehaviors/Source/`) — shipped. Radius alarm
  that fires when the carrying Thing takes damage or on a public trigger, content-blind, zero
  hardcoded species.
- **`HOSTILE_MOBILE_PLANTS_1`** — his ruling that a woken ambusher activates if others of its
  kind activate nearby.
- **`FEVERWOOD_ANT_HIVE_DUNGEON_1`** — the hive that notices, rallies and hunts.

⇒ ⛔ **Do not write a fourth alarm.** This is the cleanest and smallest of the four, which makes
it the best place to *prove* the shared mechanism before the hive dungeon needs it. The
propagation bound that item already names applies here with a twist: **wasp propagation is the
wasps themselves**, so the bound is a spawn count and a hive count per map, not a chain depth.

## the design

### The names — checked, 2026-09-23

**`RM_Skerrel`** — the wasp. **`RM_SkerrelGall`** — the hive on the plant.

MEASURED by the Wookieepedia search API (the method in the roster's §3g) and by grep across `src/`:
`skerrel` returns **NO HITS** on either. ⚠️ Two other candidates were rejected by the same check —
`vimmick` and `nesquith` both returned fuzzy page hits — which is the check doing its job.

🔑 **"Gall" is deliberate and it is not decoration.** A gall is what an insect's larvae actually grow
inside on a living plant, so *"hives attached to plants"* stops being an arbitrary placement and becomes
the one real-world mechanism it resembles. Like `bole`, it is a structure word rather than an Earth
*plant* name, so §6's naming ban does not reach it.

### The hosts — the roster already said where they live

⛔ **Do not invent host plants.** Two rows of the 22-row flora roster were written as explicitly
insect-attracting *before this creature existed*, and they name the gap this creature fills:

- **`RM_Sarquin`** (row 17, the sugar plant) — its own job line reads *"the drip is why insects are
  there, and the insects are why something bigger is."* ⇒ **Primary host.** The galls hang in the
  drip-tentacles, and the sugar is what the colony lives on.
- **`RM_Nemmer`** (row 7, fruit too big for its branch) — *"the fruit-fall draws everything that eats
  fruit, and then everything that eats those."* ⇒ **Canopy host**, so the threat exists at two heights
  rather than only at ground level.

🔑 **The skerrels ARE the insects both rows were already referring to.** That closes a loop rather than
adding a creature, and it is the same shape as the ant hive's farm chamber being already implied by the
thornbug-theft ruling. ⇒ Two hosts, no new fiction, and a player who learns *"sugar means wasps"* has
learned a real rule about the biome.

### The wasp

- **Tiny and trivial individually** — the smallest body size and hit points we ship, killable by
  anything, including a colonist swatting with no weapon. ⛔ It must never be individually threatening;
  the threat is arithmetic and nothing else.
- 🔴 **It FLIES**, per the standing rule that a creature airborne in the fiction is airborne in the game.
  Flight is the **stat** `MaxFlightTime > 0` plus `FlightCooldown` and the `race` flight fields —
  ⛔ there is no `canFly` bool, and race flags alone give a grounded animal that reads as configured.
  ⚠️ **Omit `canLeaveMapFlying`**: a skerrel lairs in its gall and must not fly off the map.
- ⚠️ **Ship it with no wing-beat animation at first, deliberately.** The flying animation is a whole-body
  directional flip-book (`flyingAnimationFramePathPrefix` + `flyingAnimationFrameCount`, north/east/south
  with west mirrored) and Core's own birds ship 8 frames each. At the counts this creature exists in, that
  is a lot of art for a 1-cell subject. With no frames, `GetBestFlyAnimation` returns null and it flies
  plainly — correct behaviour. 🔑 **Never block flight waiting on frames.**

### The sting — the whole feature is this curve

One sting is a **negligible, irritating** hediff. Stings **accumulate**, and the accumulation is what
kills. ⇒ Three properties it must have, and they are design requirements rather than tuning:

1. **One sting must be genuinely ignorable** — not "small", *ignorable*. If the first sting prompts a
   reaction, the trap never closes.
2. **The accumulation must be visible before it is fatal**, or the death is a surprise rather than a
   consequence. The player has to be able to see they are losing and choose to keep going.
3. 🔴 **It must be survivable by withdrawing, not only by winning.** The owner ruled the stench smoke
   repels skerrels, so a prepared player has a hard counter — ⇒ the unprepared player's answer is
   **leaving**, and the curve has to leave time for that.

⚠️ *"Multiple stings add up quickly and overwhelm"* is his wording, and *quickly* is the hard part: fast
enough to be frightening, slow enough that retreat is a real option and not a formality.

### The bound

Per `REACTION_MECHANISM_GENERALISE_1` and its spec: a gall boiling out is **one reaction event with a
shared budget**, so the bound is *total wasps per event and per map*, never per-gall.

⛔ **Per-gall caps are not a bound.** Ten galls each releasing "only" a dozen is a hundred and twenty
wasps with no rule broken — that is precisely the failure that spec exists to prevent. 🔑 And here the
bound is a **performance** limit before it is a balance one, which is why this creature is the right
consumer to prove the mechanism on: its ceiling is measurable rather than a matter of taste.

## ⚠️ UNMEASURED — engine questions, and the Mac has no game, no def dump, no decompiler

⛔ Name no field, class or value for any of these from reasoning.

1. **Whether many tiny pawns are affordable at all.** "Very small, numerous" is a performance
   question before it is a design one, and it is the one that can kill the feature. Read what the
   base game's own swarming insects do about count.
   ⚠️ **And flight compounds it** — the flight fields are known (they are recorded in CLAUDE.md from the
   decompiled engine), but whether *many* flying pawns cost more than many walking ones is not, and the
   answer decides whether the count bound is set by flight or by the pawn count alone.
2. **How a hediff stacks from repeated identical applications** — whether severity accumulates on
   one instance or many instances coexist, and what caps it.
3. **Whether a hive can be a Thing attached to a plant** rather than a building on the ground,
   and what happens to the hive when the plant is cut or burns.
4. **What "boil out" is mechanically** — spawning pawns on trigger, versus a dormant group that
   wakes. These have different save/load and performance consequences.
5. **Whether a swarm can be made to lose interest** and return, which is what makes retreat a
   real option rather than a death sentence.

## spec

1. **Design this as the shared reaction mechanism's first proof**, in `mandrake.rm.creaturebehaviors`,
   extending `RM_CompPlantAlarm`'s comp-plus-extension pattern. State the spawn/hive bound.
2. Establish the five mechanism questions on the Desktop. ⛔ Author nothing before that, and
   answer question 1 first — if count is unaffordable, the whole shape changes.
3. ✅ **Hosts are named** — `RM_Sarquin` and `RM_Nemmer`, both already written as insect-attracting.
   ⇒ What remains is **what a player sees before disturbing a gall**: a gall that cannot be spotted is
   not a decision, and both hosts are plants a player has a reason to approach.
4. Design the sting so it is **negligible once and frightening twenty times** — that curve is the
   feature. ⚠️ Not a detail: if one sting is ignorable and twenty are survivable, there is nothing
   here.
5. Mod Settings toggle and tuning per the standing every-mod-ships-settings rule — swarm size and
   sting severity are exactly the "a number is the experience" case.

## verify

Wasps are ours, live only in the Greentide, and their hives sit on named plants of our own
roster. Their reaction uses the shared alarm mechanism rather than a fourth implementation, with
a stated bound. One sting is trivial; an ignored swarm is lethal.
⛔ No live-proven claim from the Mac.

## criteria

You kill the first six without thinking, and then you look at the screen.

## Watch out

- 🔴 **Performance is the real risk here, not balance.** Numerous tiny pawns is the one thing in
  this design that could be simply impossible at the count that makes it work. Measure before
  designing around a number.
- ⚠️ **A swarm you cannot escape is not tension, it is a death notice.** The wasps must lose
  interest, be outrunnable, or be stoppable by something the player can carry — otherwise the
  correct play is never to enter the jungle, which deletes the biome.
- 🔴 **The stench smoke DOES repel wasps — owner, 2026-09-22: one tool, all the biome's animals.**
  ⇒ **A player carrying smoke has a full answer to this hazard**, so the wasps' threat window is
  narrow by design: early, unprepared, out of smoke, or surprised too deep to throw. ⛔ Do not
  compensate by making the swarm nastier — the ruling means smoke is the jungle's key tool and the
  wasps are what teaches you to carry it. ⚠️ **The real risk this creates is the opposite one:** if
  smoke is cheap and stacks, the wasps become a non-event after the first encounter. Bound the smoke's
  cost, not the wasps' damage.
- ⛔ **Do not let the hives become a farmable resource** (honey, chitin, venom for the toxin
  grenade) without a bound. A hazard you harvest on purpose is fine — that is the Frenzy's whole
  design — but it must cost something each time.
