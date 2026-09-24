# The Miasma fauna roster — the arthropod floor, the composters, and what the stranded actually are, 2026-09-23

_MACBENCH, authored against the owner's rulings of 2026-09-23 (this sitting) and the frozen
sheet (`the_miasma.md`). Companion to `miasma_flora_roster_2026-09-23.md`, written the same
sitting and sharing its spine._

---

## READ FIRST — this roster is small on purpose, and it is not the whole cast

The Miasma already carries **32 fauna rows** on `RUT_Miasma` and a 37-row eviction list
(`rosters/the_miasma.json`, authored 2026-09-09). ⛔ **This document does not re-adjudicate
those.** Per the owner's standing ruling of 2026-09-22, biome rosters are handled **biome by
biome at that biome's own sitting**, evictions are stopped, and a rule derived in-session
never overturns a placement a human already approved.

What this document does is author the **five things the sheet books as owed and nobody
built.** Of the five `new_defs` the roster named in September, exactly one exists:

| the sheet's owed creature | state, MEASURED 2026-09-23 |
|---|---|
| warden mother | ⛔ **NOT BUILT — and an earlier line in this document said it was. That was FALSE and is retracted.** `RUT_WardenMother` exists only as an **XML example inside a C# comment** in `RM_CompTerritorialAnchor.cs`, plus a by-name mention in `RM_AnchorGuard.xml`. There is no `ThingDef`, no `PawnKindDef`, nothing spawnable. What IS built is the generic *mechanism* (§6) |
| the crusty arthropods (⭐ his pick) | ⛔ **nothing** — no def, no clade |
| the `karr-` fever-swarm | ⛔ **nothing.** ⚠️ The two shipped `karr-` creatures, `RUT_Karrun` and `RUT_Karrash`, are the **Greentide's and the Scald's** crab-things — they establish the clade's naming and art register, not this biome's swarm |
| the delta-loam composter | ⛔ **nothing** |
| the stranded | ⛔ **nothing** — and this sitting changed what they are (§5) |

⚠️ **`RM_Stranded` exists and is NOT this.** It is a quest — one survivor, six to ten days —
in `src/RimMandrake/StrandedQuest/`. A later pass reaching for that defName will collide with
an unrelated feature. The creatures below must not use it.

---

## 0. The owner's rulings this sitting

| ruling | how it was given | what the roster owes it |
|---|---|---|
| **All four faces of the Miasma are in scope** | decision taken by question card | the arthropod floor, the stranded, the composters and the §7 economies are one sitting, not four |
| **The carnivorous plants eat the scuttlers, never a colonist** | decision taken by question card | 🔴 the floor is now **prey to five plants** as well as to everything that moves. ⇒ Its population has to be big enough to feed both, which is why §2 is four species and not one |
| **The stranded are the sea nursery's failures, not their own species** | decision taken by question card | 🔴 §5 — the stranded stop being a cast and become a **condition** that happens to the nursery's young. Nothing is authored as a "stranded species" |
| **The composters may be part of the arthropod clade** | decision taken by question card (both options chosen, and the overlap was stated on the card) | the loam producer is `RM_Karrobel`, a scuttler — one clade does the food pyramid *and* the soil, rather than two families of small muck-workers competing for the same silhouette |

### The spine is the same as the flora roster's

Every row declares where on the **fresh→brine gradient** it lives — the sheet's own §3
geography, and already a built mechanism (`RM_GradientAxisExtension`,
`RM_GradientSurgeExtension`, shipped 2026-09-13). ⇒ Flora and fauna sort along the same axis,
so a player reading plants is also reading animals.

---

## 1. At a glance

| the floor (`karr-` clade) | the swarm | the nursery | the elders |
|---|---|---|---|
| **karravel** — walks on the mud film, uncountable | **karrathil** — ⭐ the pollinator *and* the plague | the young of the sea roster, crowding the shallows | **warden mother** — ✅ already built |
| **karrobel** — burrows; its castings are the loam | | 🔴 **the stranded** — a condition of those young, not a species | |
| **karrimeth** — the one that masses and moves | | | |
| **karrolun** — hand-sized; the harvest | | | |

---

## 2. The arthropod floor — four scuttlers, and the whole pyramid stands on them

⭐ **The owner's own starred creature for this biome** (sheet §4): *"little armored scuttlers
in uncountable numbers, **eaten by everything**, the trophic floor that supports the great
beasts' growth. Harvestable, renewable, faintly comic; the entire food pyramid stands on
their backs."*

🔴 **Four species, not one, and the reason is load-bearing.** A single scuttler would now be
prey to five carnivorous plants, every juvenile in the nursery, every refugee predator, and a
harvest industry — and it would also have to produce the loam. That is four jobs on one
silhouette. Splitting them along the gradient gives each a distinct read and lets the
population maths differ by species.

⚠️ **They must not read samey, and that risk was named when this face was chosen.** The
defence is that each one's silhouette follows its *job*, not its family: a disc, a digger, a
mass, and a single big one.

| # | defName | label | silhouette FORM | what it looks like | gradient | job | art |
|---|---|---|---|---|---|---|---|
| 1 | `RM_Karravel` | karravel | **flat wide disc, legs entirely hidden beneath** | A coin-flat armoured disc the size of a palm, dull olive with a fine salt bloom, moving as a smooth glide because the legs never show. In numbers they cover the mud film completely and the ground appears to be *sliding*. | fresh to mid | 🔑 **The bulk of the floor and the biome's ambient motion.** §9 asks for *"constant small life"*; this is it. The cheap protein everything eats, and the primary prey of `RM_Nemreth` and `RM_Braskeen`. | **OWED** — must work en masse, not as a hero sprite |
| 2 | `RM_Karrobel` | karrobel | **deep wedge body, front end armoured into a blade** | Thicker than it is wide, tapering to a hardened wedge-shaped head it drives into the muck. Mostly seen half-buried, with only the rear plates and a churned ring of castings showing. Plates banded black and rust, always caked. | anywhere with muck | ⭐ 🔑 **The delta loam is its castings.** The sheet's §7 export and the hopeful mirror of the Scarlands' mortuary guild — and `RM_Pallasheen` germinates only where it has worked, so the plant is this animal's visible receipt. ⇒ The one row that makes an invisible by-product findable. | **OWED** |
| 3 | `RM_Karrimeth` | karrimeth | **small, tall-backed, and only ever seen as a mass** | Individually unremarkable — a thumb-sized humped shell, pale grey, salt-frosted. But karrimeth **only occur in a moving carpet**, thousands strong, flowing around obstacles as one body and audibly clicking. A single one is a straggler. | mid to brine | **The floor's event, not its background.** A karrimeth mass crossing a colony is a nuisance rather than a threat — it strips forage and fills the traps — and it is the one thing that makes the brine end feel populous. Its arrival is the surge's aftermath made visible. | **OWED** — a mass texture, not a creature portrait |
| 4 | `RM_Karrolun` | karrolun | **hand-sized, long-limbed, visibly the biggest of its kin** | A slow, long-legged scuttler the size of a spread hand, its shell a deep iridescent blue-green that fades to chalk when it dies. The only one worth picking up individually. Faintly comic in its deliberateness. | fresh to mid, in the roots | ⭐ **The arthropod harvest** (sheet §7) — the food industry, and the biome's ordinary meat. ⇒ Because it is the *only* one worth harvesting by hand, the industry has a target and the other three stay ambient rather than becoming chores. | **OWED** |

🔑 **One population, four draws on it — and there is already a mechanism for exactly this.**
`RM_CompVerminBreeder` plus `RM_MapComponent_VerminPopulation` (and its alert) already track a
small-creature population and breed it back. ⛔ **Read that before writing any new C# for the
floor** — in the last comparable sitting four of six "new" mechanisms turned out to be
already built, and a scuttler population drawn down by plants, predators and a harvest is
precisely what a vermin-population component is.

---

## 3. The fever-swarm — one creature, and it is both halves of the bargain

Sheet §4, and the sharpest idea in the biome: *"the disease vector and the mangals' only
pollinator, one and the same swarm. **You cannot have the trees without the fever.**"*

| # | defName | label | silhouette FORM | what it looks like | gradient | job | art |
|---|---|---|---|---|---|---|---|
| 5 | `RM_Karrathil` | karrathil | **a loose airborne cloud with no single body to fix on** | Individually a fingernail-length wet-winged thing, gold-dusted; but karrathil are only ever a slow-drifting haze of them, thickest over flowering mangals at the heat of the day. The haze itself is faintly luminous gold — it *is* the green-gold breath the biome is named for, seen close up. | wherever there are flowers | 🔴 ⭐ **The biome's central bargain in one creature.** Every flowering row on the flora roster depends on it, and the 15-day disease clock is the same animal. ⇒ A player who fumigates their holding gets a clean colony and a dying canopy, and that trade is the Miasma working as designed. | **OWED** — a swarm/haze effect, closer to weather than to a pawn |

⚠️ **Two design cautions, both real.**

- 🔴 **It must not become a mere pest.** If killing karrathil is strictly good, the bargain
  collapses. The pollination half has to be mechanically real, which means the flora's
  reproduction needs to be able to *fail* — and whether a `Plant` can be gated on a nearby
  animal at all is an **engine question, UNMEASURABLE on the Mac.** ⇒ Check it on the Desktop
  before this row's mechanics are specified.
- ⚠️ **It is the ONLY pollinator, per the sheet — do not add a second.** A backup pollinator
  is the obvious "balance fix" and it deletes the idea.

---

## 4. The nursery, and a tier problem worth his ruling

The sheet's §4 first ring: the Grey Sea's roster **breeds here** — *"the young here, the
adults in the terminator waters"* — juveniles swarming the shallows, cheap to hunt, and the
arithmetic every scavenger knows: *"don't kill what's small here; its mother is the reason
ships sink."*

**Eight juvenile defs already ship** — `RSW_MeeJuv`, `RSW_FaaJuv`, `RSW_LaaJuv`,
`RSW_YobshrimpJuv`, `RSW_SiltLampreyJuv`, `RSW_RustNipperJuv`, `RSW_OpeeSeaKillerJuv`,
`RSW_DiggerJuvenile` — and seven of them are already cast on this biome. The nursery is the
one ring that is genuinely built.

### 🔴 But every one of them is campaign-tier, and that breaks a standing rule

`sea_beasts_roster.md` is tagged **Tier RimStarWars (`RSW_`)** in its entirety. ⇒ The
franchise-free `mandrake.rm.miasma` would ship with **no nursery at all** — no juveniles, no
crowded shallows, and therefore (per §5) no stranded either. That directly contradicts the
owner's ruling of 2026-09-22:

> *"The top mod without star wars will look precisely the same as the star wars enhanced one
> save for any star wars beasts we populate it with."*

…and the corollary already written into the project's own instructions: **a `RM_` biome does
not get a thin dependency-free fallback roster.**

### ⭐ And the fix is nearly free, because most of that roster is not Star Wars at all

**MEASURED against `sea_beasts_roster.md` this pass: of its 18 creatures, only 7 are canon.**
The canon ones are the opee sea killer, the colo claw fish, the sando aqua monster, the
mee / faa / laa scalefish, and the pale yobshrimp. The other **11 are invented originals** and
the roster says so itself — *"honest originals where it does not"*:

> crimson opee · shale gorger · abyssal colo · thornback colo · elder sando · storm sando ·
> silt lamprey · rust nipper · reefback · starmaw · lanternwhale

🔑 **Under the owner's Q11a ruling an invented exotic name is not franchise IP**, so those 11
belong in the `RM_` tier and always did. Retiering them gives the free mod a real nursery
(and a real Grey Sea) with **no new creatures invented** — the same misfiling
`biome_mod_architecture.md` §7 Q11a was written to catch, and the same mistake the project
records BENCH making in the opposite direction in September.

⛔ **Not done here.** Retiering 11 shipped creatures and their juveniles is a def operation
across two mods, it is Desktop work, and the tier of a shipped roster is his call. ⇒ Filed as
its own question in §7, not executed.

---

## 5. The stranded — ruled this sitting: a condition, not a cast

🔴 **Owner's ruling, decision taken by question card:** the stranded are **the sea nursery's
failures**, not a species of their own — the same creatures as the crowded young in the
shallows, carrying a deformation from the muck.

⇒ **Nothing below is a new animal.** The stranded are what the sheet already describes
happening *to* the nursery's young:

> *"The surge's orphans: endemics cut off in pools when the salt line moves, forced ashore
> between waters — gills going leathery, fins splaying into feet that don't quite work.
> Creatures that look transitional: evolution auditioning, generation by generation, in the
> pools behind the player's base."*

### What this means concretely

| element | what it is | state |
|---|---|---|
| **the trigger** | a juvenile caught in a **stranding pool** when the salt line retreats | ✅ **the mechanism is BUILT** — `RM_StrandingPoolsExtension` shipped 2026-09-13 and has had no creatures to strand |
| **the deformation** | a hediff on an ordinary nursery juvenile — leathered gills, splayed fins, a half-working gait | ⛔ **owed.** The nearest built precedent is `RM_HediffComp_ForgeOnSurvival`, the fever-forging comp, which already turns *surviving something* into a permanent change |
| **the look** | the juvenile's own sprite, altered — not a bespoke creature | ⚠️ **owed, and it is the hard part.** How much a hediff can change an animal's appearance is an **engine question, UNMEASURABLE on the Mac** |
| **the behaviour** | it cannot return to water, and it does not thrive | `RM_JobGiver_ReturnToWater` ships and is the thing to **suppress** for a stranded animal — the tell is an animal trying to reach water it can no longer use |
| **the pay-off** | a stranded animal is easy prey, pitiable, and occasionally survives into something that works | 🔑 **`RM_HediffComp_ForgeOnSurvival` is the natural mechanism** — the biome already pays out for surviving, and this is the same idea applied to an animal instead of a colonist |

🔑 **Why his answer is better than the cast it replaced.** A hand-authored two-or-three
species "stranded" would be the same three odd animals every game, and the auditioning would
be backstory. As a *condition*, the stranded are produced by the surge, from whatever young
happen to be in the wrong pool — so the population differs every game, the salt line's
movement is the cause, and the built stranding-pool code becomes the thing that generates
content rather than terrain decoration.

⚠️ **The cost he accepted, stated plainly:** with the nursery entirely campaign-tier today
(§4), a franchise-free Miasma has no juveniles and therefore **no stranded at all.** §4's
retier is what removes that cost, which is why the two sections are one question.

---

## 6. 🔴 The warden mother — the biome's centrepiece, ruled 2026-09-23

### 🔴 First, a retraction

An earlier line in this document said `RUT_WardenMother` ships. **That was false.** MEASURED
2026-09-23: the name exists only as an **XML example inside a C# comment** in
`RM_CompTerritorialAnchor.cs`, plus a by-name mention in `RM_AnchorGuard.xml`. There is **no
`ThingDef`, no `PawnKindDef`, nothing spawnable.** ⚠️ This is the *"an existence test is not an
identity test"* trap: a grep for the name returns hits, and every one of them is documentation.

⇒ And the `RUT_` prefix in that comment is **wrong for this creature anyway.** The warden mother
is an *invented* creature, not canon IP, so under Q11a and the tier ruling of 2026-09-23 she is
**`RM_WardenMother`** and belongs in the franchise-free mod. Which matters: she is about to
become the biome's best content, and the free tier must have her.

### The owner's ruling, verbatim

> *"Let's make a not-so-gentle giant who can be befriended when its young call out for it and get
> stuck. Means that when it spawns, so do some stranded young (sometimes). It should be able to
> lumber along in the water (and its creche should be in the shallows) but cannot get on dry
> land."*

### 🔑 The whole mechanism is the waterline

She can go anywhere the water goes. She can go nowhere else. Her young gets caught in a pool the
water has **left**. She can hear it. She can see it. Between her and it is a few metres of dry
ground she will never cross in her life.

**You can.**

That is the friendship, and it is one sentence of fiction sitting on one hard movement
constraint. Every step below is either already built or cheap:

| # | step | state |
|---|---|---|
| 1 | a surge recedes and the salt line moves, cutting a pool off | ✅ `RM_GradientSurgeExtension`, `RM_StrandingPoolsExtension` — both shipped 2026-09-13 |
| 2 | a juvenile is caught in it — an ordinary young carrying the stranding condition, per the same sitting's ruling that **the stranded are the nursery's failures, not their own species** | specified §5, ⛔ nothing new invented |
| 3 | ⭐ **the young CALLS.** Audible, locatable, and it does not stop | ⛔ owed — the one piece of pure fiction-to-mechanism work |
| 4 | **she comes**, lumbering through the water toward the call, as far as water goes | ⛔ owed — water-only movement (§ below) |
| 5 | 🔴 **she stops at the waterline, and stays there** | the constraint *is* the drama |
| 6 | you free the young — carry it to open water, or cut a channel so the water reaches it | the channel route leans on `FlowWorks`; carrying is ordinary hauling |
| 7 | freeing it earns **tolerance.** Harvesting or killing it costs far more than tolerance ever bought | ⛔ owed — a tolerance state |

### ⭐ Why "when it spawns, so do some stranded young (sometimes)" is the sharpest part of the ruling

Without it, the entire relationship waits on an **irregular, storm-driven** surge — and hard ban
4 forbids ever making that predictable. A colony could play a whole game and never be offered
the chance. Spawning her *with* a stranded young some of the time means **the offer arrives with
her**, on the first day, and the surge becomes the thing that keeps offering it afterwards.

⇒ So the linkage is not flavour: it is what makes this content reachable at all.

### "Not-so-gentle" — what tolerance is, and what it is emphatically not

🔴 **She is never tamed.** Tolerance means exactly one thing: **you are removed from her target
set.** It does not mean she can be commanded, fed on demand, moved, bonded, hauled, healed,
ridden, or safely crowded.

✅ **And the mechanism for that is already built.** `RM_JobGiver_AnchorDefense` fights *anything
hostile-or-harvesting inside the anchor radius*; `RM_JobGiver_AnchorWander` keeps her near her
anchor. Tolerance is a **predicate on that target test**, not a new AI. ⇒ Harvesting anything
inside her reach puts you straight back into it, tolerated or not — which is the "not-so-gentle"
he asked for, delivered by the code as it already stands.

### Her crèche is the anchor, and it is in the shallows

✅ `RM_CompTerritorialAnchor.SetAnchor()` takes whatever `Thing` it is given, so **the crèche is
the anchor object** and her radius is her reach. ✅ `RM_ScattererValidator_BrineShallowWater`
already validates shallow-water placement, which is precisely where he ruled the crèche goes.

🔑 **This makes her protection GEOGRAPHIC, and that is the best thing about her.** A colony with
its back to open water is nearly unraidable from that side. A colony four tiles inland gets
nothing. ⇒ The player buys as much of her as their building site is brave enough to claim — and
that is a real decision made at settling time, not a toggle.

### The two amendments this ruling makes to the frozen sheet

Recorded here, and **edited in place** in `the_miasma.md` §4 rather than left to contradict a
newer document:

| the sheet said | it now says | why |
|---|---|---|
| *"Enormous, **stationary**, lethal within reach"* | enormous, **lumbering within the water**, lethal within reach, and unable to reach dry land | owner ruling above. She moves; the water is her cage |
| *"Placed set-pieces, **never random spawns**"* | she **spawns**, and sometimes brings stranded young with her | owner ruling above. Her crèche can still be a placed, mapped, named site — §8's *"placed, mapped and named"* survives for the crèche, not for her |

⛔ **Nothing else in §4 moves**, and ⛔ the roster still adds **no second giant** — the eviction of
`AA_OvergrownColossus` is reasoned as *"the giant lane here is owned by warden mothers… a random
giant dilutes them"*, and that holds harder now than before.

### What is actually owed, and the trap sitting in the middle of it

| owed | note |
|---|---|
| `RM_WardenMother` **ThingDef + PawnKindDef** | does not exist in any form. Huge `bodySize`, aquatic, lethal in reach |
| 🔴 **a water-only movement constraint** | **the single new mechanism.** Nothing in this repo does it — `RM_JobGiver_ReturnToWater` gets a stranded animal *back* to water, `RM_LurkingWaterExtension` marks pool terrain, `RM_ScattererValidator_BrineShallowWater` validates placement. None of them forbids leaving water |
| **the young's call** | a locatable, persistent audible cue, and the thing a player learns to recognise |
| **a tolerance state** | per-colony, persisted through save/load, readable to the player — she must *visibly* stop treating you as prey |
| **her ThinkTreeDef** | 🔴 see the trap below |

🔴 **THE TRAP, and `RM_AnchorGuard.xml`'s own comment already names it:** *"assigning this
DutyDef to a pawn requires that pawn's own ThinkTreeDef to actually consult `mindState.duty`
(vanilla's plain Animal ThinkTreeDef does **not**; only Insect-shaped trees do)."* ⇒ A warden
mother given `RM_AnchorGuard` on a plain Animal think tree will **silently ignore the duty
entirely** — she will wander off, defend nothing, and read as a configured creature. The comment
explicitly hands this decision to *this* pass, so it is now owed: either an insect-shaped tree or
our own tree that consults duty.

⚠️ **And `RM_EnvironmentalHazards.csproj` sets `EnableDefaultCompileItems false` and lists every
file**, so the new water-constraint `.cs` needs a `<Compile Include>` line or it compiles into
nothing, with no error. Always a two-file change.

🔴 **Three things here are UNMEASURABLE on the Mac** and ⛔ must not be reasoned out from a doc:
whether a pawn's pathing can be constrained to a terrain set at all; whether a `bodySize` that
large paths through shallow water without breaking; and whether the duty seam behaves on a
non-insect tree. Desktop, before any of this is built.

### ⚠️ For the owner — one thing I did NOT author, on purpose

When I pitched this, part of the idea was that **she eventually dies and you inherit the crèche**,
with every scavenger on the map knowing she's gone. You didn't repeat it, and it is the part most
likely to be resented rather than felt — a scripted loss of a defence a player has spent a
campaign earning. ⇒ **Left out.** She is currently mortal only in the ordinary way. If you want
the clock, it needs to be foreshadowed from the first day, and that is its own ruling.

---

## 7. What is owed

- 🔴 **All five new creatures need art**, and none exists. ⚠️ **Search
  `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl` and any review sheet's
  `.decisions.json` by subject before queueing a single job** — the owner's standing rule of
  2026-09-20. ⚠️ The daemon does not run on the Mac.
- ⭐ **Two of the five are not creature portraits and must not be briefed as such**:
  `RM_Karravel` has to work as a *carpet* and `RM_Karrimeth` only ever appears as a mass,
  while `RM_Karrathil` is closer to a weather effect than a pawn. An art brief that delivers
  three handsome hero sprites has delivered the wrong thing.
- 🔴 **THE QUESTION FOR HIM: retier the 11 invented sea beasts from `RSW_` to `RM_`?** (§4).
  It is the difference between the free mod having a nursery and having none, it invents
  nothing, and Q11a already says an invented name is not IP. Desktop def work across two mods.
- 🔴 **Three engine questions, all UNMEASURABLE on the Mac** — each needs a Desktop pass and
  ⛔ none should be reasoned out from a doc:
  1. Can a plant's reproduction be gated on a nearby animal? (karrathil's pollination half)
  2. How much can a hediff alter an animal's rendered appearance? (the stranded's look)
  3. Can a plant consume a small wild animal at all, and can it be restricted to one species?
     (the flora roster's five predators)
- **Commonalities are slots, not values**, and density stays thick — `animalDensity` 6.5 is
  doctrine, recorded as refugee crowding rather than plenty.
- **This document removes nothing from the live biome def.** The 32 existing fauna rows stand
  until this biome's own roster sitting, per the 2026-09-22 stop on evictions.
- ⛔ **Do not add a second pollinator**, and ⛔ do not add a second giant. Both are the obvious
  balance fix and both delete an idea the sheet is built on.

---

## 8. For the owner

1. 🔴 **The tier question in §4 is the one I most want your answer to.** Eleven of the sea
   roster's eighteen creatures are invented, not canon, and they are all filed as Star Wars.
   Moving them to the franchise-free tier costs no new content and is the difference between
   the free Miasma having a nursery — and therefore stranded animals — or having neither.
2. ⭐ **Your stranded answer made the built code useful.** `RM_StrandingPoolsExtension` has
   been shipping since 2026-09-13 with nothing to strand. As a condition rather than a cast,
   the surge now *generates* the stranded, and they differ every game.
3. ⚠️ **I folded the composters into the scuttler clade** rather than authoring them as a
   separate family, on the overlap I flagged when you chose both. If you wanted them distinct
   — burrowing worms rather than burrowing arthropods — that is one row to change.
4. ⚠️ **The fever-swarm can be ruined by a balance pass.** If killing it is strictly good, the
   biome's central bargain is gone. I have written the caution in, but it depends on an engine
   answer nobody has yet.
5. ⚠️ **`RM_Stranded` is already taken** by an unrelated quest about a stranded traveller. The
   naming needs care so a future search does not conflate a rescue quest with a deformed fish.
