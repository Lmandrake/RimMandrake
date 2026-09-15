<!-- status: DESIGN, filed 2026-09-15 from the bench session recorded in
     infrastructure/state/items/RAKATAN_ARCHOTECH_MACHINES_1.md. That item is
     the authority on what the owner said and ruled; this file is the design
     that follows from it. Where the two differ, the item wins and this file
     is wrong. Nothing on the item's "Still open" list is decided here.
     Written on the laptop: the game, ModsConfig.xml, RimSage, the def dump
     and `measure` were all unreachable, so every claim that needed one of
     them is marked UNVERIFIED and collected in §8. -->

# ANCIENT MACHINES — the grade ladder, and the two layers above it

## 0. Concept in three sentences

Ancient machines do not break, they sag: found at a fraction of the capability
their makers built into them, they still turn over, and a scavenger can drag
one part of the way back but never all the way. There are exactly three states
a found machine can be in — **Defunct**, **Kludged**, **Refurbished** — one
ladder for every ancient thing, fixed installation or carried relic, and half
of the original is the ceiling no hand ever passes. Everything else in this
design is about who climbs the ladder, what it costs, and — two layers up,
where the gods live — what it means that they climbed it.

---

## 1. Architecture — three layers, dependencies downward only

Ruling 0. Each layer requires the one below it and no layer ever reaches up.

| # | layer | tier | packageId | may say "Rakatan"? |
|---|---|---|---|---|
| 1 | **the machine mod** (today `WreckedMachines`) | `RimMandrake` | `mandrake.rm.wreckedmachines` (exists) | ⛔ never |
| 2 | **the Rakatan skin** | `RimStarWars` | `mandrake.rsw.<name>` (does not exist) | ✅ yes |
| 3 | **the Salvation pack** | `RimUtinni` | `mandrake.rut.salvation` (does not exist) | ✅ yes |

**Layer 1 is complete and playable in a vanilla game.** Generic ancient wrecked
machines, no faction, no setting, no gods, no ship. The test of whether the
neutrality is real is whether it could be published to strangers as-is; the
discipline that keeps it real is that not one Rakatan word — not a defName, not
a label, not a description, not a comment — may appear in it.

That discipline is **violated on disk today**, in the one place a stranger
would look first: `About/About.xml`'s description opens *"The Kolyska's factory
did not fail politely"* and *"The Jawa do not clear them away."* See §10.

**One clarification the layer table needs.** The nine-god scalars do not live in
layer 3. They live in **`mandrake.rm.ninefold`** — a shipped `RimMandrake`-tier
engine (`src/RimMandrake/Ninefold/`) holding the satiation/mood vector, the band
ladder and eighteen event hooks, and already ruled to be the RM half of the
"RM engine + RUT Salvation pack" split (`NAMING_SCHEME_PLAN.md` §7.1, owner
card 2026-09-08). So layer 3 depends on **two** RimMandrake mods, not one, and
the divine reaction in §5 is implemented by layer 3 calling Ninefold — never by
layer 1 knowing that Ninefold exists.

```
        layer 3   mandrake.rut.salvation
                    │              │
        layer 2   mandrake.rsw.… ──┤
                    │              │
        layer 1   mandrake.rm.wreckedmachines    mandrake.rm.ninefold
```

**What ruling 0 buys, and what it costs.** It buys a publishable base mod and it
dissolves per-relic divine allegiance as a permanent property of the machine
mod. It costs an integration surface: because layer 1 must not know about gods,
**layer 1 has to publish a neutral "this machine changed grade" signal that
layer 3 can subscribe to.** Without one, layer 3's only routes are to Harmony-
patch layer 1's construction (reaching down into a sibling's internals) or to
patch vanilla construction and filter by defName (fragile, and it re-couples
the layers through a string). The in-repo pattern for a soft, no-assembly-
reference subscription already exists: Ninefold's own `ChronicleSubscriber`
binds to the Chronicle engine by reflection, with no `modDependency` and no
assembly reference in either direction. **This is not a nicety. §5 is not
buildable without it, and §9.2-A explains why no existing hook covers it.**

---

## 2. The grade ladder

Ruling 1. Three grades, discrete states, each with its own stat block and its
own sprite. Not a capacity curve, not a per-subsystem wear model. One ladder
for every ancient thing.

| grade | of original | reads as |
|---|---|---|
| **Defunct** | 0.0001 | inert. A sacred object, not a machine. |
| **Kludged** | 0.2 | works, badly, visibly bodged. |
| **Refurbished** | 0.5 | the ceiling. Half of what its makers built. |

Ruling 2 caps it: nothing equals or exceeds the original. Ruling 3's arithmetic
follows and is **derived, not spoken** — if Refurbished is half of original and
still beats modern rim-tech, then original is at least 2× modern. It is on the
open list; nothing below is balanced against it.

### 2.1 What the ratios are ratios OF

Two shapes of machine, and the ladder is easy on one and hard on the other.

**Scalar machines** have a single number for capability. A battery's capability
is stored charge; the ratios apply exactly and unambiguously, and the fiction
lands for free — *"their batteries just slowly lose capacity over millennia yet
still work"* is a spec, not a metaphor. This is the case the owner reached for
to explain the idea, and it is the easiest case there is.

**Compound machines** have no single number. A factory's capability is
throughput × recipe breadth × uptime × input efficiency, and those four axes do
not live in the same file. **If the ladder is defined only on the easy case it
will be defined by accident on the hard one** — so the ladder needs a
per-machine **capability contract**: one line per treated machine naming which
axis or axes carry the ratio. §2.2 works the pilot through and shows why.

### 2.2 Worked example — the Automated Smelter

Real values, read from
`src/RimMandrake/WreckedMachines/Defs/ThingDefs_Buildings/Buildings_WreckedMachines_AutomatedSmelter.xml`
and from the donor facts quoted in its own header (`VFEFactory_AutomatedSmelter`,
size 3×4, 300 W, heatPerSecond 14, Steel 260 + ComponentIndustrial 7).

| axis | Defunct (`_Wrecked`) | Kludged | Refurbished (`_Repaired`) | donor = "modern" |
|---|---|---|---|---|
| recipes | none — no comps at all | 3 of 6 | **6 of 6** | 6 of 6 |
| power | none | 360 W | **300 W** | 300 W |
| heat/sec | none | 20 | **14** | 14 |
| breakdown factor | — | 6 | **3** | 3 |
| overclock | — | `false` | **`true`**, factor 1 | true, factor 1 |
| MaxHitPoints | 450 | 300 | **450** | 450 |
| WorkToBuild | 800 | 3000 | **5000** | 5000 |
| cost | Steel 30 (token) | Steel 120 + Comp 3 | **Steel 260 + Comp 7** | Steel 260 + Comp 7 |

The bold column is the problem. **The shipped top tier is field-for-field
identical to the donor's modern machine, deliberately** — the XML says so at
its own costList: *"Identical to the donor, per the owner's 'otherwise
identical mechanics underneath'. Every field below this line matches
`VFEFactory_AutomatedSmelter` except texPath, defName, label and description.
Keep it that way — this def is the A/B comparison target."* That instruction
was correct for an art comparison and is **void under rulings 1–3**: a
Refurbished machine must *beat* modern rim-tech, and this one merely equals it.

The middle rung, by contrast, is roughly right by accident. Three of six
recipes, worse power, worse heat, twice the breakdown rate, no overclock —
call that ~0.4–0.5 of the donor, which is what 0.2/0.5 = 0.4 of Refurbished
demands if Refurbished sits just above modern.

**So the pilot's numbers need one rung rebuilt, and the rebuild runs into a
file we do not own.** The axes our own ThingDef can move against the donor
without touching donor content are: power draw, heat, breakdown factor, hit
points, and the overclock factor. Of the four capability axes:

- **Recipe breadth is hard-capped.** The donor already offers all six. A
  Refurbished machine cannot beat modern by breadth; there is nothing above six.
- **Throughput lives in the donor's `ProcessDef`s**, not in our ThingDef.
  Expressing 0.2 or 0.5 as a real speed ratio means either per-grade copies of
  those defs, or a per-building speed multiplier the processor comp reads —
  UNVERIFIED whether one exists (§8 U2).
- **Input efficiency** is in the same donor defs. Same constraint.
- **Uptime and power efficiency are ours.** A Refurbished ancient machine that
  draws 200 W where the modern one draws 300 W, and almost never breaks, reads
  correctly as *better than anything the rim builds* without touching a donor
  file. This is the cheapest honest route to "exceeds modern".
- **Overclock headroom is ours and is the most expressive axis** — the donor
  ships factor 1, and a value above 1 would say "this thing has reserve the rim
  cannot match." But `VEF_BuildingMaxOverclockFactor`'s arithmetic has never
  been read; DESIGN.md §6 refused to guess it once already and that refusal
  stands (§8 U1).

**Recommendation, for a one-line ruling:** the capability contract for a
VFE-Factory machine is *power efficiency + uptime + overclock headroom*, with
recipe breadth carrying the Defunct→Kludged step only. Throughput stays out of
it until someone reads the donor's ProcessDefs on the Windows machine.

### 2.3 The ladder's steps are wildly uneven, and that prices the gate

0.0001 → 0.2 is a factor of **2000**. 0.2 → 0.5 is a factor of **2.5**.

The first rung is the whole game: a sacred object becomes a machine. The second
is a polish: a bad machine becomes a good one. If both rungs cost the same in
Ancient Components the first is a steal and the second is an insult, so the
component cost should be shaped like the ladder — cheap to wake a thing, dear
to finish it. That is a tuning statement, not a ruling; it is here because the
arithmetic makes it non-obvious in exactly one direction.

### 2.4 Defunct's 0.0001 is doctrine, not a trickle

0.0001 exists to say *this is not dead*, which is the whole engineering
character: a modern machine breaks, an ancient machine sags. It is not an
instruction to ship a machine that produces one ingot per century.

- On a **compound** machine, implement Defunct as **inert** — the shipped def
  already does exactly this (no comps block at all, `tickerType Never`,
  `isInert true`), and that is right: a powered comp doing nothing still costs
  a tick and still prints an inspect line promising something that will never
  arrive.
- On a **scalar** machine, implement it **literally** — a battery holding a
  ten-thousandth of its charge is harmless, cheap, and delivers the fiction
  perfectly the first time a player checks it.

The shipped Defunct description must change either way: *"It has no power in it
and nothing to give"* states the opposite of the doctrine (§10).

### 2.5 Worth scales with size — and where that lands

Ruling 1: a factory is worth far more than a battery at the same grade. In
RimWorld the only expression of a building's worth is its market value, derived
from its cost list — and the shipped Defunct tier costs **Steel 30**, a token
put there as a testing affordance. A sacred relic the ship loves currently
appraises at nothing.

Give relics real worth and three things follow, none of them optional:

1. **Market value feeds colony wealth feeds raid points.** A reliquary of large
   relics is a threat multiplier. The campaign intends to replace wealth-based
   raid scaling with the Visibility dial (`colony_visibility_stat.md`, F12) but
   only *at the actual raid call sites* — until that lands, a relic hoard raises
   raid difficulty by existing.
2. **Ozzik's shipped matrix page counts "wealth milestones" as a DEED +.**
   Collecting relics feeds the pride meter whether anyone designs it to or not.
3. **The floor makes the hoard appreciate on its own** (§4.2). A collection that
   climbs a grade without the player acting is a wealth curve with no player
   input — which is exactly the shape the anti-exponential pillar exists to
   refuse.

None of that argues against worth-by-size. It argues that worth-by-size is a
*balance* lever wired to three other systems, and it should be tuned with them
in view rather than set once per machine and forgotten.

---

## 3. What each layer owns

Precise enough to place a file. "→" means the layer above may reference the
layer below's defName; the reverse never happens.

| thing | layer | where it goes |
|---|---|---|
| the three grade ThingDefs per machine | 1 | `src/RimMandrake/WreckedMachines/Defs/ThingDefs_Buildings/` |
| grade art, 3 × 4 facings per machine | 1 | `…/Textures/WreckedMachines/<Family>/<Machine>/<Grade>/` |
| the `replaceTags` step between grades | 1 | on the ThingDefs themselves |
| Ancient Components (the resource ThingDef) | 1 | `…/Defs/ThingDefs_Items/` |
| the per-machine restoration `ResearchProjectDef` | 1 | `…/Defs/ResearchProjectDefs/` (exists) |
| the RR `SpecialResearchOpportunityDef` (study) | 1 | `…/Defs/Specials/` (exists) |
| mobile-structure grade defs | 1 | same as fixed — one ladder |
| worth-by-size scaling | 1 | cost lists per machine |
| the capability contract per machine | 1 | `MACHINES.md` gains a column |
| Mod Settings for all of the above | 1 | `…/Source/` + `Assemblies/` — **does not exist yet**, see §7 |
| the treated-machine register | 1 | `MACHINES.md` |
| **Rakatan labels, descriptions, lore text** | 2 | patches over layer 1's defs |
| **Rakatan art reskins** | 2 | its own `Textures/`, texPath overrides |
| **archotech ⇒ Rakatan reinterpretation of vanilla/mod content** | 2 | patches; nothing new, only renaming |
| reliquary socket buildings on the hull | 3 | `src/RimUtinni/…/Defs/ThingDefs_Buildings/` |
| the seated-relic comp + save/load persistence | 3 | `…/Source/` — needs an assembly |
| the veneration precept | 3 | a `PreceptDef` **and** the `.rid`, see §5.2 |
| the Seating ritual | 3 | ritual defs + the same `.rid` constraint |
| every per-god reaction to a grade step | 3 | calls `Ninefold`, by reflection |
| the ship-raises-the-floor mechanic | 3 | `…/Source/`, a GameComponent |
| the Utinni's own wreck placement | 3 | map authoring, not a def |
| the sacred-scrap deconstruct restriction | 3 | it is a precept/policy, so it is the clan's |

**Two placements worth stating because they look like layer 1 and are not.**
Sacred scrap is a *clan rule* — `wrecked_machines_resurrection.md` item 4 ruled
it a precept/restriction rather than `deconstructible=false`, and a precept is
the campaign's. And the Utinni's deck full of dead machines is map authoring,
not a mod feature: layer 1 supplies the machines, layer 3 decides that this ship
is made of them.

---

## 4. The two improvement paths

### 4.1 Manual refurbishment — components plus tech from the ship

Owner, verbatim: *"refurbishment requires Ancient Components, a truly scarce and
valuable resource as well as the tech to do so (from the ship)."*

- **Ancient Components** are the gate on every grade step. Scarcity is the
  balance lever with the shortest wire: it caps the number of Refurbished
  machines in a campaign without nerfing what Refurbished means.
- **The capability is granted, not built.** There is no bench the player raises
  to unlock refurbishment; the ship hands it over as she recovers. The player's
  capability arc and the ship's healing arc are one arc.
- The step itself is ordinary construction over a shared `replaceTags`
  footprint — vanilla 1.6, no C#, the mechanism already on the defs. Its runtime
  behaviour is the mod's oldest unpaid debt (§8 U6).
- Where Ancient Components come from is on the open list.

### 4.2 The floor — the ship's recovery

Owner, verbatim on the timing: *"players will be manually upgrading systems for
quite some time long before the ship gets the ability to 'bring everything up
to some base level' across the board. It raises the floor to save the players
from manually repairing everything all the time."*

So: **late, and its purpose is relief from chore-work.** Not a mid-game tide
that lifts the player's work into irrelevance, and not a reward — a hand taking
over a task that has stopped being interesting. Components buy the peak; the
ship guarantees the minimum.

### 4.3 Where the ship's own capability comes from — the coupling ruling 6 does not dissolve

Ruling 6 keeps two economies apart: *"The Urns feed antiquities, not the
artifacts."* Antiquities' 48 read artifacts stay their own progression; Rakatan
relics move the gods instead.

That separation is real at the top and rejoined underneath, and the spec should
say so rather than let someone discover it:

- Refurbishment tech comes **from the ship** (ruling: §4.1).
- The ship's recovery is driven by the **urn loop** — `06_the_ship.md`: her
  archive regenerates one urn at a time, and `antiquities_design.md` §2.1's
  *techprint radiation* emits techprints for "ship function, manufacturing
  capability, or ship repair" into THE SHIP tree's economy.
- Therefore **urns fund refurbishment indirectly**, through the ship, even
  though no urn ever touches a relic.

That is coherent and arguably better than a hard wall — the two loops meet in
the one place the campaign wants everything to meet. But it means "the artifacts
and the urns are separate economies" is only true of the *items*, not of the
*progression*, and the antiquities doc and this one should agree about it.

**A second coupling in the same place.** `06_the_ship.md`'s *Restoration, not
manufacture* ruling (2026-09-04) already governs the ship's module recovery:
integrations only ever REPAIR her factory modules, never build new ones, and the
modules wake in a **fixed, fully authored order** — Mill, Loom, Galley, Farm,
Press, Machining Bay, Apothecary, Assembler. If the floor's auto-refurbishment
touches machines aboard the ship, it is operating in the same territory as that
authored sequence. Whether the floor *is* that sequence seen from another angle,
or a second mechanism beside it, is not stated anywhere. It should be.

### 4.4 The tension the owner flagged — framed, not decided

Two paths that both raise a machine's grade must not make each other pointless,
and with only three grades there is very little room between them. This is on
the open list; what follows is only the shape of the ruling, so it can be one
line.

The floor can sit at Defunct (meaningless), Kludged (relief: every relic
eventually works, badly, and the player's hand is what makes one good), or
Refurbished (the ship finishes the game — and Ancient Components stop buying
anything, contradicting ruling 8's "components buy the PEAK", because there
would be no peak above the floor).

⇒ **The owner's own words may already dissolve this.** *"the ship's auto-repair
systems … refurbish ever-larger machines onboard automatically"* describes a
progression axis of **size**, not grade: a fixed target grade that reaches
steadily bigger machines, so the meter is "how large a thing can she handle
now" rather than "how high can the floor go". On that reading grade-room was
never the constraint, and the arithmetic problem disappears. Recorded as a
reading, not a ruling.

---

## 5. Sacredness — layer 3 only

Ruling 5. Sockets plus precept, layered; none of it is layer 1's.

### 5.1 Reliquary sockets

Relics are seated in reliquary sockets on the hull. **Persistent, not
consumed** — a seated relic is still the relic, and can presumably be taken out
again. Each seating grants a boon. This is why the object is a socket and not a
crafting input: the collection is meant to be walked past and looked at.

The sockets are on the Utinni's hull, and that is not decoration. Per §4d of
the divine engine, **the ship is the conduit through which any of the nine may
speak, and every one of the nine covets the hull as a body it could live
through.** Seating a Rakatan relic is putting an ancient thing *inside the body
nine gods are competing for*. That is the reason all nine react to it and not
just the god of salvage — and it is the sentence the Seating ritual's flavour
should be built out of.

Whether a **mobile** relic can be seated in a hull socket at all is on the open
list.

### 5.2 The veneration precept, the Seating ritual, and a hard pipeline constraint

The precept venerates seated relics: mood near them, a ritual to seat one, real
fallout for scrapping or selling one. Substantively this is
`wrecked_machines_resurrection.md` item 4's "sacred scrap as a clan rule"
finally getting its home.

**The constraint nobody has priced.** The player's ideoligion is not generated
at runtime — it is `The Salvation.rid`, a fully expanded runtime ideo with 103
precepts, the owner's approved artifact, loaded at game start
(`ideoligion/APPROVED.md`: *"A `FactionDef` ideo block is a constraint on
generation … There is no field that accepts a `.rid`"*). A new precept therefore
needs **two** things: a `PreceptDef`, and an entry in the `.rid`, injected by
`src/RimMandrake/Utils/build_salvation_rid.py`'s `add_precepts`. That function's
own docstring names the limit:

> *"A precept is only safe to hand-author when its `preceptClass` needs no
> generated content."*

A mood-near-relics precept is the safe shape. **A precept carrying a ritual is
precisely the untested shape** — rituals bring named ritual defs, roles and
outcome effects into an artifact that was expanded once and is treated as
frozen. And `NAMING_SCHEME_PLAN.md`'s hard ordering constraint puts the `.rid`
regeneration *before* any world freeze.

⇒ The Seating ritual is not a late add-on the way a ThingDef is. It rides the
`.rid` build, and it should be scoped and tested there before the sacredness
layer is promised. Marked UNVERIFIED (§8 U10), not asserted.

### 5.3 The divine reaction — both scalars

Ruling 7 in the item records the owner's words — *"The ship has its literall
'mood' (vector among the gods) increased when ancient relic artifacts are
installed on the ship"* — and flags which scalar he meant as UNRULED. The
session resolved it: **both.**

- **Satiation** — the signed per-god ledger, moved by what the colony does. A
  seating writes a **permanent** entry here. This is the ledger, and it should
  read as one: the act is remembered.
- **Mood** — each god's own weather. A seating gives a **temporary, unprinted
  lift**. Canon F8 governs the surfacing absolutely: *"Mood is WEATHER, never a
  number"* — no UI ever prints it, and the seating letter must not either. It
  shows up as a door that does not hesitate, a hum that sweetens, the
  Narrator's adjectives for a week.

**What this costs in the engine, verified in-repo.** Ninefold's public surface
is `GetSatiation`, `GetMood`, `GetBand`, `ApplyDelta(God, float, reason)`,
`IsUnveiled`, `TryFirstContact`, `NotifyViolentDeath`, `Notify_Launched`. The
satiation half is a straight `ApplyDelta` call. **The Mood half has no public
entry point at all** — Mood is a private self-driven random walk
(`StepMoodWalk`), and there is no method that moves it from outside. A
temporary lift also implies decay, which is new saved state.

⇒ Ruling 7 cannot be built in layer 3 alone. It needs a **new, generic
capability in Ninefold**: an external Mood impulse with a decay clock,
`ExposeData`d like the rest of the vector. Generic is the operative word —
Ninefold must gain "something outside can nudge a god's weather", not "relics
nudge a god's weather", or the engine has learned about relics and ruling 0 is
broken from below. (Ninefold's own master switch already gates `ApplyDelta`, so
the new path should be gated the same way for free.)

### 5.4 Reaching for Refurbished, and the fracture it makes

Ruling 4: reaching for the top grade is **pride** — and note the inversion the
item records. The offence is not surpassing the ancients, which ruling 2 makes
impossible anyway. The offence is **presuming you could make their work whole
again.**

Session record: it pleases **⑨ Ozzik** and **⑤ Rekko**, and angers **① Ishko**,
**⑥ Ta'Baa** and **③ Oomo**.

> ⚠️ **Provenance.** `RAKATAN_ARCHOTECH_MACHINES_1` ruling 4 still reads *"Which
> gods anger, and whether Rekko is among them … is UNRULED."* This section is
> written from the session record BENCH carried out of the sitting. If the item
> is the later word, everything in §5.4 is a proposal awaiting one line, not a
> ruling. It cannot be both; the item needs updating or this section does.

Why each, in the terms their own shipped matrix pages already use:

- **Ozzik** — ambition's god. Every advancement feeds him "regardless", and
  refurbishment is advancement wearing a humble face. His satiation is a
  pride-meter that draws fire, so this is a cost, not a reward.
- **Rekko** — salvage's god. His DEEDS + literally include *restoring
  wrecks/ruins-finds*; he cannot be offended by a restoration. And his
  Body-vision is full restoration.
- **Ishko** — a Refurbished machine runs, and a running machine draws power,
  throws heat, makes light and noise. A working factory is a colony that can be
  seen. A reliquary of them cannot be hidden at all.
- **Ta'Baa** — the better a fixed installation works, the more it roots you. His
  L curse is *The Burning of the Root*: he destroys the thing keeping you here.
  A Refurbished factory is that thing, by definition.
- **Oomo** — chambers given to machines instead of broods. He already fights Ohm
  over exactly this, and dislikes even a droid idling in a sleeping room.

**The fracture.** Canon's bloc map (`divine_satiation_engine.md` §4d) files
**Ishko + Ta'Baa + Oomo + Rekko** together as the humble/resilient survival
bloc — hide, flee, seed, restore — and names **Rekko ⇄ Ozzik** as the sharpest
internal war in the pantheon. On this one act, Rekko votes with Ozzik against
his own three blocmates.

That is not a bug in the bloc map; it is the most interesting thing the ladder
does. The bloc holds on *what the ship should become*, and splits on *what the
clan should do this afternoon*. Rekko's alignment is with the deed, not with the
politics: a wreck rewoken is his sacrament regardless of who else is offended,
and he will take the same side as his flat opposite to get it. It gives the
Council of Voices an argument that cannot be predicted from the blocs — and it
gives the player a real, legible choice, because there is no configuration of
piety in which refurbishing is free.

**Two consequences that fall out without new rules.** High Ozzik satiation is
already a standing upward bias on Sh'kaar's and Zizzik's rolls (§8), so
refurbishment feeds both evil gods through the pride channel. And ② **Ohm** is
unnamed by the ruling but his shipped page awards satiation for *"machines built
and powered"* and *"ship systems restored"* — refurbishment is the single most
Ohm-pleasing act in the mod. Leaving him off the list would contradict a page
that has already shipped (→ §9.2-D).

### 5.5 Two canon lines this collides with

Both are single lines in shipped canon, both say the opposite of ruling 4, and
under the house rule wrong material is deleted rather than annotated. Naming
them here so the correction is a decision and not a discovery:

1. **Ozzik's matrix page, DEEDS −**: *"grief-valve: restoring RAKATAN works
   feeds his grief-side gently **without the pride spike**"* — filed under
   humility, and repeated in his L-curse tail. Ruling 4 says reaching for the
   top grade *is* the pride spike. A reconciliation exists and is worth one
   line: **grade decides which face of Ozzik answers.** Kludging a dead ancient
   thing is humble work and feeds the grief-side. Reaching for Refurbished —
   claiming you can make their work whole — is the pride spike. If that is the
   ruling, both matrix lines need the qualifier; if not, one of the two must go.
2. **Rekko's Body-vision**: *"the fully restored original … **Full restoration
   is the only true path.**"* Ruling 2 caps every hand at half of original, so
   Rekko's platform is now **permanently unattainable** — the one god whose
   vision of the ship cannot be delivered, in an endgame that is a contest over
   which vision wins the hull. That is either excellent tragedy (he is the god
   who is right about what to want and wrong about whether it can be had) or a
   hole in the endgame. It should be one of those on purpose.

---

## 6. Study the machine

Ruling 9: the artefact in front of the pawn is the research subject, and the
route is Research Reinvented's `SpecialResearchOpportunityDef` with
`opportunityType Analyse`. **Not Anomaly's study system** — owner-benched
(*"not fun to user"*), and `CompStudiable` gates on monolith level, which this
campaign's `generateMonolith false` never raises.

This is already proven and already on disk. `WreckedMachines/DESIGN.md` §2 says
why that opportunity type and no other, and the reasoning is a near-miss worth
quoting rather than paraphrasing:

> `Analyse` is the right opportunity type and this was **not** obvious — the
> near-miss is worth recording. `AnalyseProductionFacility` sounds perfect for a
> factory machine and is wrong: its own def is *"Passively practice … while
> performing any work at {0}"* with `JobPicker_NoJob`. It needs a pawn **working
> at** the building, and a wreck has no work. `Analyse` instead inherits
> `AnalysisOpportunity`, whose picker is
> **`JobPicker_AnalyseInPlaceOrMinified`** — a pawn walks to the thing and
> studies it **where it stands**, which is the only behaviour an immovable wreck
> can support.

The same section records what was verified against files (all ten
`SpecialResearchOpportunityDef` fields, both opportunity types as real defs, RR
active in the live list) and what was not (that the opportunity actually
appears in game). The shipped def is
`RM_WM_AnalyseWreckedSmelter` → project `RM_WM_AutomatedSmelterRestoration`,
target `RM_WM_AutomatedSmelter_Wrecked`.

Three things the grade ladder adds to it:

1. **Which grade is the study target.** Today it is the Defunct tier alone. That
   is probably right — you learn from the corpse, not from the thing you already
   fixed — but with three grades and two rungs it is now a choice. A second
   opportunity on the Kludged tier, feeding the project that unlocks
   Refurbished, is the obvious shape and is not authored.
2. **The target can vanish.** The def's own header already flags it: after a
   build-over replaces the Defunct machine, the Analyse target is gone. With two
   rungs this gets worse, because the player may want to keep studying after
   rung one.
3. **`targetIterations 5.0`** under RR's default `ReverseEngineering` category is
   the "slowly" the owner asked for, tuned by RR's author rather than invented
   here. The first dial to reach for is our own def's `importanceMultiplier`,
   because it is scoped to our machine. **Do not patch RR's category settings** —
   they are global across the whole stack.

**Mobile structures** (in scope per the item) fit this without a change:
`JobPicker_AnalyseInPlaceOrMinified` handles minified things, which is what a
carried relic is.

---

## 7. Mod Settings — layer 1

House rule, owner 2026-09-12: every mod ships a real settings screen — on/off
per major feature, tuning where a number is the experience, defaults = shipped
behaviour, all-off degrades gracefully.

**Two things must be said before the settings list.**

**(a) `MOD_OPTIONS_RETROFIT_1` currently exempts this mod, on a false premise.**
Its exempt list reads *"Every `*ArtOverride` mod and `WreckedMachines` — pure
texture reskins, no `Source/` dir, nothing to toggle beyond enabling/disabling
the mod itself."* WreckedMachines ships three def files including a
`ResearchProjectDef` and an RR opportunity, and under ruling 0 it becomes the
mod that owns the grade ladder. The exemption is void.

**(b) The house rule and ruling 5 collide.** Ruling 5 notes that
*"WreckedMachines itself may still be able to ship as pure XML, which is worth
protecting."* A settings screen cannot be XML: it needs a `Mod` subclass and a
`ModSettings` subclass — the in-repo pattern is
`src/RimMandrake/Ninefold/Source/RM_NinefoldMod.cs`. So layer 1 must gain an
assembly, or it must be the one mod with no settings screen. **One line from the
owner settles it**; everything below assumes the assembly.

Toggles, all default ON = shipped behaviour:

| setting | type | what off/low does |
|---|---|---|
| grade ladder | on/off | off: no grade defs are buildable; existing ones keep working. The mod becomes art. |
| study the machine (RR Analyse) | on/off | off: no opportunity is offered; the restoration project is reached by bench theory alone |
| mobile relics | on/off | off: only fixed installations get grades |
| Ancient Components as the gate | on/off | off: grade steps cost only ordinary materials — the "I do not want a scarcity economy" switch |
| Ancient Component cost multiplier | slider, default 1.0 | the scarcity dial, which is the balance lever ruling 3 leans on |
| worth-by-size multiplier | slider, default 1.0 | scales relic market value — the wealth/raid-points wire in §2.5 |
| Refurbished capability multiplier | slider, default 1.0 | how far above modern the top grade sits; the axis §2.2 has to choose |
| Defunct destructibility | on/off | whether a Defunct relic can be destroyed at all (§9.2-F) |
| grade-change signal | on/off | publishes the neutral signal layer 3 subscribes to. **Labelled**: off breaks dependent mods' reactions |

**Degradation contract.** With every setting off, layer 1 is a texture pack with
three unbuildable defs and no research hooks — and nothing it once wrote to a
save becomes invalid. Layer 3 must treat the signal being off as "no relics were
seated today", never as an error.

---

## 8. UNVERIFIED — everything this machine could not check

Twelve claims. Every one needs the Windows machine: the game, `ModsConfig.xml`,
RimSage, `measure`, the def dump, or the donor mods on disk. **None of the
defNames, fields or class names below were invented to finish a sentence** —
where a name was not readable in this repo, no name is given.

| # | claim | how to settle it |
|---|---|---|
| U1 | Whether `VEF_BuildingMaxOverclockFactor` above 1 is a usable "exceeds modern" axis, and what VEF's overclock arithmetic actually does | read VEF's overclock code; DESIGN.md §6 already refused to guess it once |
| U2 | Whether VFE-Factory's processor comp exposes **any** per-building speed or efficiency multiplier our ThingDef could set | read the donor's comp + `ProcessDef` fields |
| U3 | The six `VFEFactory_Smelt*` process durations and yields — needed before any ratio is stated numerically | donor defs |
| U4 | Which mod supplies the "archotech battery", and what field holds its capacity. No such vanilla Core def is evidenced anywhere in this repo | RimSage / the dump |
| U5 | Whether a vanilla `replaceTags` build-over runs a deconstruct job. If it does, Ninefold's existing hook fires **−Rekko** and refurbishing a machine *angers* the god of repair | read the vanilla replace path |
| U6 | Whether `replaceTags` places at runtime at all, with and without Replace Stuff - Continued active. The mod's oldest unpaid debt | quicktest (DESIGN.md §4, and it needs a load, not analysis) |
| U7 | Whether the RR `Analyse` opportunity actually surfaces in the research UI for a colonist to take | quicktest |
| U8 | Whether `mandrake.rm.wreckedmachines` is still absent from the live `ModsConfig.xml` — last verified 2026-09-01. This governs whether the ruling-1 rename is free | read `ModsConfig.xml` |
| U9 | Whether any of the six draft `.rws` worlds carry `RM_WM_*` shortHashes | `measure` on the drafts |
| U10 | Whether a **ritual-bearing** precept can be hand-injected into `The Salvation.rid` via `build_salvation_rid.py::add_precepts`, whose docstring restricts safe hand-authoring to precepts needing no generated content | build one and load it |
| U11 | That `CompStudiable` gates on monolith level (asserted by ruling 9; not readable here) | RimSage |
| U12 | Whether vanilla exposes a hook a neutral grade-change signal can ride, and where | RimSage on the construction-completion path |

**Two things that are NOT unverified, stated so they are not re-checked.**
Ninefold's public surface and the absence of any Mood mutator were read directly
from `GameComponent_Ninefold.cs`. Its event magnitudes are *known* untuned — the
source says so itself.

---

## 9. Open questions

### 9.1 Carried forward verbatim from the item's "Still open"

- **Confirm the 2× arithmetic** in ruling 3 — derived, never spoken.
- Where relics are found, and where Ancient Components come from.
- Mobile structures: which ones, and does a mobile relic still seat in a hull
  socket?
- Can the ship's floor ever reach `Refurbished`, or does it stop at `Kludged` —
  with only three grades, the floor has very little room to move. *(§4.4 offers
  a reading that may dissolve this: the owner's own "ever-larger machines"
  describes a size axis, not a grade axis.)*
- Does the reliquary need to be readable by the endgame's contest over the
  ship's future, or does Salvation Engine keep that to itself?

### 9.2 New — exposed by writing this

**A. No existing hook sees a grade step, and the one that might is inverted.**
Ninefold's `Patch_BuildingRepaired` fires on `Notify_BuildingRepaired` when a
building reaches full **hit points** — an HP repair, which is not what a grade
step is. A grade step is a construction job over a shared footprint, so today it
awards Rekko *nothing*: the mod's central sacrament is invisible to the god
engine. Meanwhile `Patch_BuildingDeconstructed` fires **−Rekko (large)** on a
completed deconstruct job, so if a `replaceTags` build-over routes through that
path (U5), refurbishing a machine currently *angers* the god of repair. Either
way the coverage is wrong, and the fix is the neutral signal in §1 — which is
also what makes layer 3 buildable at all. **This is the most consequential
finding in this document.**

**B. Which axis carries the ratio, per machine** (§2.2). Needs a per-machine
capability contract, and the pilot needs its top rung rebuilt because the
shipped one is deliberately identical to the donor.

**C. Does relic worth feed colony wealth and raid points, and should it?**
(§2.5.) It also feeds Ozzik's "wealth milestones", and the floor makes the hoard
appreciate with no player input.

**D. Is ② Ohm pleased by refurbishment?** His shipped matrix page says he must
be — *"machines built and powered"*, *"ship systems restored"*. Ruling 4 names
only Ozzik and "others". Also unstated: ④ Mob'Unloo's view of a relic that is
sacred and therefore unsellable.

**E. Grade-dependent Ozzik, or a canon deletion** (§5.5-1). Does Kludging feed
the grief-side and only Refurbishing feed the pride spike, or does one of the two
shipped matrix lines go?

**F. Can a Defunct ancient machine be destroyed at all?** The shipped def has
`useHitPoints True` and `leaveResourcesWhenKilled false`. "It is ROBUST, it
SURVIVES" argues for a thing that cannot be killed — which would also be the
speculative escape DESIGN.md §4 named for the Replace Stuff conflict
(`useHitPoints=false` puts it outside
`IsNonDeconstructibleAttackableBuilding`). One ruling settles a fiction question
and a mechanical one at once.

**G. Is the ship's floor the same mechanism as the authored module-wake
sequence?** `06_the_ship.md` already fixes the order — Mill, Loom, Galley, Farm,
Press, Machining Bay, Apothecary, Assembler — with authored, permanently placed
art per stage. Two mechanisms operating on the same machines aboard the same
ship need to know about each other (§4.3).

**H. Does the mod keep the name `WreckedMachines`?** "Wrecked" is now the name of
*one grade of three*, and the base mod may not say Rakatan. The packageId
`mandrake.rm.wreckedmachines` is compliant and cheap to keep; the display name
owes `RimMandrake: <Name>` per the naming grammar either way.

**I. Which layer owns the duplicate-machine decision?** DESIGN.md §1 accepts, for
testing only, that the player sees both VFE's smelter and ours — *"not
acceptable at ship"*, and still unresolved. Under the three-layer split it is
now unclear whether retexturing the donor is layer 1's call (a generic mod
replacing a generic mod's art) or layer 2's (a reskin).

**J. Does the study target survive rung one, and is there a second opportunity?**
(§6.)

---

## 10. Required edits elsewhere — enumerated, NOT made

Ruling 1 renames the shipped tiers (`_Wrecked` → `_Defunct`, `_Repaired` →
`_Refurbished`; `_Kludged` already matches), and rulings 0–9 make a number of
existing statements wrong. Nothing below was changed by this pass.

**Rename cost, first, because it decides the order of work.** Per
`WRECKED_MACHINES_RESURRECTION_1` (checked against the live `ModsConfig.xml`
2026-09-01), `mandrake.rm.wreckedmachines` is **not enabled** and has never been
loaded, so its defNames cannot be baked as shortHashes into any savegame. The
rename is free **today**. It stops being free the moment the mod is enabled or
the world is frozen — `NAMING_SCHEME_PLAN.md`'s hard ordering constraint. Do it
before either, and re-verify U8 first.

### 10.1 `src/RimMandrake/WreckedMachines/DESIGN.md`

| where | what is now wrong |
|---|---|
| L3–6 header | names `ship_deck_plan.md` as *"the authority on the campaign fiction and the repair ladder"*. The ladder's authority is ruling 1; the fiction moves to layers 2–3 |
| L8–18 banner | *"Everything below is still true and still correct"* — false after rulings 1–3 |
| L22–28 §1 table | tier names; and the Wrecked row's **Function: None** contradicts 0.0001 / degrades-gracefully |
| L26 | *"Not deconstructible, not haulable, yields nothing if destroyed"* describes the deferred sacred-scrap state, not what ships (`deconstructible true`); and "not haulable" cannot be a ladder-wide rule now that mobile relics are in scope |
| L28 | Repaired = *"Full function"* — must exceed modern, not equal the donor |
| L43–69 §1 | the parallel-def / duplicate-machine question is live but no longer knows which layer owns it (§9.2-I) |
| L457, L481 | *"~25 minutes into a load"* — superseded by the measured ~15 min |
| L152–157 | candidate art path `file:///D:/Luke/dev/Rimworld/src/Jawa/art_bench/smelter/` — a pre-migration `D:` path. Verify before trusting the "do not delete" instruction that depends on it |
| L562 | lists the three defNames — rename |
| L577–590 §6 | the provisional cost table's rung labels "→ kludged / → repaired" |

### 10.2 `src/RimMandrake/WreckedMachines/V2.md`

**Recommend deletion, not annotation.** The file is a v1-deferral register whose
whole premise was lifted 2026-08-31, and its top line is exactly the
supersede-in-place banner the house rule forbids. Two facts in it are still
load-bearing and must land in `DESIGN.md` or here before it goes: the Replace
Stuff conflict, and the §7 coupling (`deconstructible=false` is what kills the
repair). Specifically false today:

| where | what is now wrong |
|---|---|
| L1–3 | a supersede-in-place banner over a file of dead premises |
| L13–30 | *"THE WHOLE MOD IS v2 NOW"*, *"v1 ships no part of this mod"* |
| L31–34 | absence from `ModsConfig.xml` described as *"now the intended state"* |
| L65–76 §1 | *"v1 has two states, not three"* — ruling 1 fixes three |
| L94–100 §3 | techprint gate; predates `TECHPRINT_FACTION_GATING_1` blocking it |
| L127–143 §7 | sacred scrap's "likely v2 shape" — now ruled, elsewhere, and it is a precept, so it is layer 3's |
| L145–155 §8 | *"v1 ships **no** `SpecialResearchOpportunityDef`"* — one ships |
| L156–174 §9 | *"the repair loop … Stood down"* — it ships |
| L177–188 | *"## In v1 — Nothing from this mod."* |

Keep: §5 (duplicate machine) is still live and belongs in `DESIGN.md`.

### 10.3 `src/RimMandrake/WreckedMachines/README.md`

| where | what is now wrong |
|---|---|
| L5–7 | *"wrecked → kludged → restored"* — and "restored" was never a shipped tier |
| L9–12 | *"STATUS: ART PIPELINE ONLY. No defs are authored yet, the mod is not enabled … nothing is deployed"* — three def files exist and the DEPLOY_HOLD was lifted |
| L21–22 | *"`Defs/` … Empty until art exists"*, *"`Textures/` … Empty"* |
| L60–61 | *"`restored/` … **This is tier 3**"* — contradicted by DESIGN.md §1's own correction |
| L104 | *"A cold game load costs ~23–30 minutes"* |
| L116 | *"No C# and no Harmony patching of our own"* — changes with §7's assembly |
| L133 | `ship_deck_plan.md` as *"The authority"* on the ladder |

### 10.4 `src/RimMandrake/WreckedMachines/MACHINES.md`

| where | what is now wrong |
|---|---|
| L199–202 | 🔴 *"The restored tier is the donor's own building, unmodified — this mod never replaces or retextures the original"* — **flatly wrong**, reversed by DESIGN.md §1 on 2026-08-12 and by the About.xml rewrite the same day. Highest priority in this file |
| L14–16 | table columns `wrecked / kludged / repaired` |
| L16 | `Defs: ⬜` (not started) — three def files exist |
| L20, L63, L211 | section headings per grade name |
| L149–170 | the candidate queue has no mobile-structure entries (now in scope) and no capability-contract column (§2.1) |

### 10.5 `Defs/ThingDefs_Buildings/Buildings_WreckedMachines_AutomatedSmelter.xml`

| where | what is now wrong |
|---|---|
| L59, L133, L254 | defNames `_Wrecked` / `_Kludged` / `_Repaired` |
| L60, L134, L255 | labels |
| L61 | *"It has no power in it and nothing to give"* — states the opposite of the degrades-gracefully doctrine |
| L256 | *"It does everything the original did."* — breaks ruling 2 (never equals the original) **and** ruling 3 (must exceed modern) in one sentence |
| L272–276 | the *"Keep it that way"* instruction to match the donor field-for-field — **void**; this is the §2.2 rebuild |
| L64, L138, L259 | texPaths, coupled to the `Textures/…/<Grade>/` folder names |
| L74–79, L101 | the Defunct tier's build entry + token Steel 30 — *"Remove designationCategory before ship"*, and worth-by-size (§2.5) now argues the cost list means something |
| L90–91 | `useHitPoints True` + `leaveResourcesWhenKilled false` — §9.2-F |
| L104–107, L112–117, L190, L306–310 | comments naming "the wrecked tier" and the v1 cut |
| header L12–52 | the whole ruling block predates rulings 0–9 |

### 10.6 The other two def files

- `Defs/Specials/SpecialResearchOpportunities_WreckedMachines.xml` — L56 defName
  `RM_WM_AnalyseWreckedSmelter`, L60 target `RM_WM_AutomatedSmelter_Wrecked`.
  Its header's open risks stay accurate.
- `Defs/ResearchProjectDefs/ResearchProjects_WreckedMachines.xml` — L52
  description says *"the wrecked automated smelter **on the ship's own deck**"*:
  grade name, and the location is now too narrow (wrecks seed in three habitats
  per the resurrection spec, and mobile relics have no deck). The Ship-tree tag
  and techprint notes stay accurate.

### 10.7 `src/RimMandrake/WreckedMachines/About/About.xml`

- 🔴 **The description is campaign lore inside the `RimMandrake` layer** — *"The
  Kolyska's factory did not fail politely"*, *"The Jawa do not clear them
  away"*. This is the clearest ruling-0 violation on disk. The Jawa/Kolyska
  framing moves to layer 2/3; layer 1's storefront text describes generic
  ancient machines.
- The three-state block (WRECKED / KLUDGED / REPAIRED) — names, plus *"Dead …
  does nothing, cannot be removed"* (contradicts 0.0001 and the shipped
  `deconstructible true`) and *"Full function"*.
- `<name>Wrecked Machines</name>` — owes the `RimMandrake: <Name>` display
  grammar, and see §9.2-H on whether the name survives at all.

### 10.8 Tooling and texture folders (one coupled decision)

`validation.py`, `Source/briefs.py`, `check_sprite.py`, `fit_sprite.py`,
`grab_source_art.py`, `sheet.py` carry the tier strings across ~48 lines —
notably `grab_source_art.py` L187/L208's `("restored", "wrecked", "kludged",
"repaired")` and `briefs.py` L172/L258. Tooling is naming-scheme-exempt, **but
the `art_source/` and `Textures/` folder names are what `texPath` points at**,
so either the folders move with the defNames or the folder names stay and
deliberately diverge from the grades. Decide it once, both sides together.

### 10.9 `design/Jawa/wrecked_machines_resurrection.md`

| where | what is now wrong |
|---|---|
| L45 item 1 | *"Tier ladder, art pipeline, replaceTags loop: **unchanged**"* — the ladder changed, in names and in ratios |
| L52–53 item 2 | *"restoration rows live in THE SHIP tree (Rekko-neutral register)"* — needs reconciling with ruling 4, which makes reaching the top grade prideful rather than neutral |
| L63–66 item 4 | sacred scrap as *"ideology precept / restriction"* — correct in substance, but it sits in the machine mod's design doc and a precept is layer 3's |
| — | the doc knows nothing of the three layers, Ancient Components, the floor, mobile structures or the grade ratios |

### 10.10 `design/Jawa/divine_satiation_engine.md`

| where | what is now wrong |
|---|---|
| L1223–1224 | Ozzik DEEDS − *"restoring RAKATAN works feeds his grief-side gently without the pride spike"* — contradicts ruling 4 (§5.5-1) |
| L1243–1244 | the same claim again, in Ozzik's L-curse tail |
| L810 | Rekko's Body-vision *"Full restoration is the only true path"* — made unattainable by ruling 2 (§5.5-2) |
| L1112–1136 | ⑤ Rekko's page: DEEDS + *"restoring wrecks"* is grade-blind and now has three rungs to read against; his L curse *The Rewoken* has acquired a literal namesake |
| L378–381 | the bloc map — the humble bloc splits on this act (§5.4) and should say so |
| §1, L19–31 | this doc owns the two-scalar mechanics, so ruling 7's "both scalars, Mood unprinted" belongs here |

### 10.11 `design/Jawa/antiquities_design.md`

- L172–175: *"Antiquities completions are Rekko-tagged, pride-neutral — reading
  what was always written is restoration, not transcendence."* Sits beside
  ruling 4's "restoration is pride". Reconcilable in one line — reading is not
  pride, refurbishing is — but both docs must say the same line.
- §2.1 L149–155 techprint radiation: this is the mechanism that funds
  refurbishment tech from the urn loop (§4.3). Say so, so ruling 6's separation
  claim stays honest about what it separates.

### 10.12 `infrastructure/state/canon.yml`

- L1996–2000, `archotech_is_rakatan.src`: *"Found defunct, weakly functional or
  semi-functional"* — ruling 1 deletes that ladder. The entry needs the three
  named grades, the ratios, and the "nothing equals the original" cap. It is
  also silent on the three-layer architecture.
- L1480–1495, `wrecked_machines.src`: doctrine intact, but predates rulings 0–2
  and the grade renames.

### 10.13 Queue and plan files

- `infrastructure/state/items/MOD_OPTIONS_RETROFIT_1.md` L101–102 — withdraw the
  WreckedMachines exemption; both clauses of its stated reason are false (§7a).
- `design/NAMING_SCHEME_PLAN.md` L55 (§3) and L185 (Phase 3) — both name **two**
  destinations for this mod ("core" + "Rekko-relic hooks extract to RimUtinni").
  Ruling 0 has three: add the `RimStarWars` Rakatan skin. L24's tier test row
  ("WreckedMachines core") stays correct.
- `infrastructure/state/items/RAKATAN_ARCHOTECH_MACHINES_1.md` — ruling 7 still
  reads *"UNRULED which scalar … Ask before building"* and ruling 4 still reads
  *"Which gods anger, and whether Rekko is among them … is UNRULED."* The
  session resolved both (§5.3, §5.4). Either the item records that, or §5.3 and
  §5.4 of this file are proposals and should say so.
