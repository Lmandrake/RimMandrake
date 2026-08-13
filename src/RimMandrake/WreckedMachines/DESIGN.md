# DESIGN — WreckedMachines

_Started 2026-08-12. Implements a ruling that already exists: the **SACRED
SCRAP** decision in `design/Jawa/worldbuilding/ship_deck_plan.md`. That file is the
authority on the campaign fiction and the repair ladder; this file owns only
how the mod realises it._

> ## 🛑 THIS MOD IS PARKED — the whole of it is v2
>
> **Owner, 2026-08-12: stand down.** v1 uses mangled metal salvage on the ship,
> role-played as broken machines, with Research Reinvented and VFE-Factory
> driving progression unchanged. **No part of this mod ships in v1** — not the
> tiers, not the art, not the repair loop, not any research.
>
> `mandrake.wreckedmachines` is undeployed and absent from `ModsConfig.xml`, and
> that is the **intended** state. See `V2.md`.
>
> ⚠️ **Everything below is still true and still correct.** It is a design that is
> finished and waiting, not a design in progress. Read it as the brief for v2.
> The rulings, the verified mechanisms and the two traps it produced all stand —
> a cut mechanism does not invalidate the work that de-risked it.

---

## 1. The three tiers

| Tier | State | Function | Removable? |
|---|---|---|---|
| **Wrecked** | Deformed, scavenged, attacked, missing chunks, corroded | **None.** Occupies its tiles and nothing else. | **No.** Not deconstructible, not haulable, yields nothing if destroyed. |
| **Kludged** | Exposed wiring, patches, mismatched plating, alien tech grafted onto an elegant original | Runs — but only the **simplest recipes** the intact machine offers | No. Advance it or leave it. |
| **Repaired** | Rebuilt by scavengers: holes filled with mismatched metal, cabling routed semi-neatly, a few improvised vents still smoking | Full function | Normal building rules apply |

⚠️ **CHANGED 2026-08-12.** Tier 3 was originally "the donor mod's own building,
untouched", which made this a pure addition. The user's authored brief sequence
makes tier 3 **our art**: a machine visibly rebuilt from the wreck rather than a
factory-fresh original. That is better fiction — the Kolyska's smelter should
never look new again — but it has consequences worth stating:

- The mod now ships art for all three states, so **~207 images** for full
  VFE-Factory coverage rather than ~138.
- If the repaired tier *replaces* VFE's building rather than sitting alongside
  it, WreckedMachines becomes a **retexture** of VFE-Factory, affecting that
  machine everywhere it appears for every colony. If it is a separate def, the
  player can end up with both.

### ✅ RESOLVED by the owner, 2026-08-12 — ship in parallel

> "We will ship our art in parallel to theirs for now, for testing purposes,
> with otherwise identical mechanics underneath."

**Separate defs, not a retexture.** Our three tiers exist alongside
VFE-Factory's own building, which is left completely untouched. The mechanics
below the art are identical to VFE's, so the only difference between our
restored machine and theirs is the texture.

Why this is the right call for now, beyond the owner having made it:

- **It is reversible.** A retexture changes VFE-Factory's smelter in every
  colony forever; a parallel def can be removed by disabling one mod. Until the
  art is proven in play, reversibility is worth more than tidiness.
- **It makes A/B comparison possible in one save.** Both machines can stand on
  the same map, which is the only honest way to judge whether the rendered
  style reads correctly next to the rest of the stack.
- **It defers the hard question rather than answering it wrongly.** "For now"
  and "for testing purposes" are load-bearing: the duplicate-machine problem is
  real and still unresolved, just no longer blocking.

⚠️ **The cost, stated so it is not discovered later.** The player can build or
encounter **both** machines, which is confusing in a real campaign and means two
entries in every build menu and bill list. That is acceptable for testing and is
**not** acceptable at ship. Revisit before this mod goes anywhere near a real
playthrough.
- `restored/` in `art_source/` keeps its name and its job: it is the donor
  reference every tier is drawn and registered against, not a shipped tier.

### Why the wreck cannot be cleared

From `ship_deck_plan.md`, resolving `[DECIDE A]` on 2026-08-06:

> Destroyed/derelict factory machines are **sacred scrap that cannot be touched,
> cleared, deconstructed, or reprocessed until they are repaired.** You may not
> salvage a broken machine for materials, nor bulldoze its rubble to build fresh
> on the cleared floor.

Two payoffs the deck plan already identifies: you cannot strip your own hull for
a material windfall (anti-exponential), and the Jawa reverence for machines gets
mechanical teeth rather than being flavour text.

Mechanically that means the wrecked ThingDef has **no deconstruct designator, no
haul, and no leavings.** It is furniture in the way a boulder is furniture.

#### ⚠️ Conflict to resolve: the "everything detonates" backlog item

Accepted by the owner 2026-08-12 and queued in
`file:///D:/Luke/dev/Rimworld/infrastructure/state/TODO.md` §1: a patch giving droids, workbenches and
machines turret-style `CompProperties_Explosive` blasts, scaled by **energy
density**. Taken literally across the stack, **a destroyed machine detonates and
its wreck is vaporised — which deletes the salvage this mod exists to create.**

The two are reconcilable, and the reconciliation is better fiction than either
alone: **a wreck is already discharged.** Energy score `E = 0` for the wrecked
tier, so it gets no explosive comp at all; only *live, powered* machines go up.
That also means the ladder gains a real hazard — repairing a machine is what
makes it dangerous again.

### ✅ RATIFIED by the owner, 2026-08-12

> "A wreck has no power, hence it cannot explode. **POWER DENSITY explodes, not
> the fact it's a machine.**"

That second clause is the sharper rule and it governs the whole detonation
feature, not just this mod: **the trigger is stored or flowing energy, never
category membership.** "Is it a machine?" is the wrong question and would blow up
every wreck, every unpowered husk and every disconnected bench. The right
question is "how much energy is in it *right now*?"

Consequences worth stating, since they are cheap here and expensive later:

- The wrecked tier takes **no** `CompProperties_Explosive`. Not a small radius —
  none at all.
- The **kludged** tier runs, so it is powered, so it *does* detonate — and being
  a bodged repair it is arguably the most dangerous state of the three. Good
  fiction, and free.
- The energy proxy must read the thing's **current** power state where possible,
  not its def-time maximum. A machine with no conduit is a wreck by another name.

Filed to `TODO.md` §1 as the governing constraint on that feature.

---

## 1b. House style — ✅ CHOSEN by the owner, 2026-08-12

Three candidate treatments of the wrecked smelter were generated and put side
by side against the donor art. The owner chose the **rendered** treatment:
realistic materials and lighting, heavy surface texture, large bold breaches,
no keyline.

This is a **deliberate departure from VFE-Factory's flat, cel-shaded, bold-
outlined house style**, and it was chosen with the reference in view.

⚠️ **The consequence is that the choice propagates.** The three tiers have to
belong to each other, so wrecked, kludged and repaired are now all committed to
this treatment. A rendered wreck sitting beside a flat repaired machine would
read as two different games. If the repaired tier ever reverts to being VFE's
own art untouched (see §1), that tension returns — which makes the "replace or
sit alongside" question below sharper, not softer.

**The known weakness, measured rather than assumed.** At true display size the
rendered treatment reads as a dark rusty box; the donor art stays legible
because of strong value contrast and bright accents. Damage shape survives the
downscale, material detail does not. So every prompt in this style must push
**value contrast** explicitly — bright torn metal edges against deep shadow in
the breaches — rather than asking for more damage or more texture.

The three candidates are kept at
`file:///D:/Luke/dev/Rimworld/src/Jawa/art_bench/smelter/` for comparison if the
decision is ever revisited — `variant_flat.png`, `variant_painterly.png` and the
winner `variant_rendered.png`, which became the wrecked south anchor. They are
tracked in git; **do not delete them**, because the ruling is only re-openable
while the losing candidates exist. That directory was pruned from 89 files to 4
on 2026-08-12 and now carries a `README.md` saying what survives and why.

---

## 2. How a tier is advanced — ⚠️ PARTLY SETTLED, 2026-08-12

**Settled:** *how the player learns to repair a machine.* Studying the wreck is
the primary route — ratified below, with the mechanism verified and costed.

⚠️ **Still open:** the **material** cost of each rung and whether a techprint
gates the last one. The defs ship those two fields marked `⚠️ PROVISIONAL` and
they remain unratified.

Read the ratification first (*"the wreck is the main way to learn"*); the
recommendation above it is the older, pre-investigation proposal and survives
only for the material-cost half.

The original ask was "a kind of research that requires construction materials
plus research-like study." But `ship_deck_plan.md` carries a ruling from
2026-08-06 that points the other way:

> **PROGRESSION SOURCE = QUESTS + TRADE, not research.** The jump to
> ship/factory capability is closed primarily by acquiring capability from the
> world — **not by grinding the bench.**

and a three-gate chain accepted 2026-08-07: **techprint → prototype → research**,
with the explicit warning that **the techprint must remain the true lock**,
because Research Reinvented lets a player build a prototype and then stop
researching.

### Recommendation — pre-investigation, and now only half-live

⚠️ Written before the Research Reinvented investigation below. Its point 3
(*study is a bonus, not a gate*) has been **overtaken by the owner's ruling** —
study is the main route. Points 1 and 2, the material costs, are still the
standing proposal and still unratified.

Advance a tier with **materials + tools + an earned unlock**, and let *study*
accelerate rather than gate:

1. **Wrecked → Kludged.** Cost: salvage feedstock + components + a **tool
   requirement** (Survival Tools Reborn, `3554664966`, is in the stack and is
   the natural lever). No research. This is the Jawa doing what Jawa do.
2. **Kludged → Restored.** Cost: materials + the machine's **real research**
   (`VFE_BasicFactories` for the smelter) gated behind an **earned techprint**,
   per the three-gate chain.
3. **Study is a bonus, not a gate.** Research Reinvented already ships
   `Analyse` — *"nondestructively reverse engineer"* — plus
   `AnalyseProductionFacility` and `PrototypeConstruction`. If the wreck can be
   an analysis target for the project that unlocks the restored machine, the
   player gets "study the wreck to learn how to fix it" from a mod already
   installed, with no second progression system.

### ✅ The "verified limitation" was wrong — the hook exists. Investigated 2026-08-12

**What this section used to say:**

> ⚠️ **Verified limitation:** RR generates opportunities *automatically* from
> what a research project unlocks. Its 1.6 defs expose a **blacklist**
> ModExtension and **no whitelist** — there is no XML hook to declare "studying
> THIS wreck advances THAT project." So point 3 is an *aspiration to test*, not a
> certainty.

That was true of the mechanism it looked at and wrong about the conclusion. The
whitelist exists, it is called something else, and it lives in a directory the
earlier pass did not open: **`Defs/Specials/`**.

`PeteTimesSix.ResearchReinvented.Defs.SpecialResearchOpportunityDef` binds a
**project** to an explicit **list of things**. That is exactly "studying THIS
thing advances THAT project", declared in XML.

**RR ships our own use case as a worked example.** From
`v1.6/Defs/Specials/SpecialResearchOpportunities_Core.xml`:

```xml
<PeteTimesSix.ResearchReinvented.Defs.SpecialResearchOpportunityDef ParentName="SpecialResearchOpportunityBase">
    <defName>RR_autodoor</defName>
    <relationOverride>Ancestor</relationOverride>
    <importanceMultiplier>2.0</importanceMultiplier>
    <project>Autodoors</project>
    <things><li>Door</li></things>
</PeteTimesSix.ResearchReinvented.Defs.SpecialResearchOpportunityDef>
```

Study the predecessor object to advance the project that unlocks its successor.
Substitute *wreck* for *Door* and *the project gating the repaired machine* for
*Autodoors* and the mapping is one-to-one.

#### The proposal — the whole feature, in one def, no C#

```xml
<PeteTimesSix.ResearchReinvented.Defs.SpecialResearchOpportunityDef
    ParentName="SpecialResearchOpportunityBase" MayRequire="PeteTimesSix.ResearchReinvented">
    <defName>WM_AnalyseWreckedSmelter</defName>
    <opportunityType>Analyse</opportunityType>
    <project>VFE_BasicFactories</project>
    <things><li>WM_AutomatedSmelter_Wrecked</li></things>
</PeteTimesSix.ResearchReinvented.Defs.SpecialResearchOpportunityDef>
```

`Analyse` is the right opportunity type and this was **not** obvious — the
near-miss is worth recording. `AnalyseProductionFacility` sounds perfect for a
factory machine and is wrong: its own def is *"Passively practice … while
performing any work at {0}"* with `JobPicker_NoJob`. It needs a pawn **working
at** the building, and a wreck has no work. `Analyse` instead inherits
`AnalysisOpportunity`, whose picker is **`JobPicker_AnalyseInPlaceOrMinified`** —
a pawn walks to the thing and studies it **where it stands**, which is the only
behaviour an immovable wreck can support. Its `shortDesc_Direct` reads
*"Nondestructively reverse engineer {0}"*, which is the sentence this section
asked for a year of design ago.

#### What is verified, and what is not — stated separately on purpose

**Verified against files on disk, not remembered:**

- all ten `SpecialResearchOpportunityDef` fields (`project`, `things`,
  `opportunityType`, `relationOverride`, `forDirect`/`forAncestor`/
  `forDescendant`, `importanceMultiplier`, `rare`, `freebie`) confirmed by
  `strings` on `v1.6/Assemblies/ResearchReinvented.dll`
- `Analyse` and `AnalyseProductionFacility` are real `ResearchOpportunityTypeDef`s
  in `v1.6/Defs/Opportunities/`
- the `Ancestor` value works because **RR ships a def using it**
- **RR is active in the live mod list** — `petetimessix.researchreinvented` and
  `…​.steppingstones`, in a config matching the newest pinned full-stack backup

⚠️ **Not verified: that the opportunity actually appears in game.** This is a
def-level finding. Nothing here has been loaded. `freebie` and the exact
importance weighting are unread, and whether RR offers an opportunity for a
project the player cannot yet start is untested. **Treat the def above as a
prediction with a named test, not as a finished mechanic.**

### ✅ RATIFIED by the owner, 2026-08-12 — the wreck is the main way to learn

> "It should teach them about how to fix that machine… and the associated
> research item it is part of, slowly."

**Option C below.** Studying a wreck is the primary route to the knowledge that
repairs it, and bench theory is the weak fallback rather than the main road.

#### The happy accident: we do not have to build this. RR already ships it.

The instinct was to suppress bench research ourselves. That would have been
wrong, and unnecessary — **RR's own settings already do it, and better**:

| preset | what it does |
|---|---|
| **`applied science`** | *"Theoretical research is disabled. Progress requires experimentation."* — **this is the owner's ruling exactly**, as a one-click player setting |
| `science marches on` | no limit on reverse-engineering gains, theory greatly slowed |
| `default` | theory already `importanceMultiplier 0.0` + `infiniteOverflow` — a fallback, not the road |

Note the last row: even RR's **default** treats bench theory as an overflow
route, not the primary one. The owner's ruling is closer to RR's own design
intent than to a departure from it.

**So the division of labour is:**

- **WreckedMachines supplies the wrecks as study targets.** One
  `SpecialResearchOpportunityDef` per machine. That is our entire contribution.
- **How hard the bench alternative is stays a player setting.** We do not patch
  it, override it, or assume it. A player on `applied science` gets the full
  "wrecks are the only way"; a player on `default` gets "wrecks are much the
  better way". Both are coherent, and neither needs a line from us.

⚠️ **Do not patch RR's category settings from this mod.** They are global — they
govern every research project in the stack, not ours. Changing them to serve one
machine would silently reshape progression for all ~561 mods' research. If the
campaign wants `applied science`, that is a save-level choice the owner makes in
RR's settings, and it should be recorded in the campaign docs rather than
compiled into a factory mod.

#### "Slowly" is already the default, and has a number

`Analyse` sits in the **`ReverseEngineering`** category (`category_Direct` on its
def). Under RR's default preset that category carries:

```
importanceMultiplier 1.25 · targetIterations 5.0 · researchSpeedMultiplier 2.0
```

`targetIterations 5.0` is the "slowly": a wreck is not read once and exhausted —
it takes roughly **five study sessions** to wring out. That is the pace the owner
asked for, already tuned by RR's author, with no number invented by us. If it
proves too fast or too slow in play, the dial to reach for **first** is
`importanceMultiplier` on our own def, because it is scoped to our machine and
touches nothing else.

#### On "that machine AND the research it is part of"

Worth stating plainly, because RimWorld gives one dial where the ruling names
two things. Studying the wreck credits progress to a **research project**, and
that same project is what gates the repaired tier. So in RimWorld's model *"how
to fix this machine"* and *"the research it belongs to"* are **the same object** —
one def delivers both meanings at once.

If the intent was two *separate* tracks — machine-specific know-how that is not
just tech-tree progress — that needs a small per-machine `ResearchProjectDef`
each wreck feeds, with the big project as its prerequisite. It is authorable, it
roughly doubles the def count per machine, and it is **not** what is being
authored now. Flagged so the difference is a decision rather than a discovery.

---

### The three options this replaced, kept for the record

The open question was never "materials or research" — it was whether *study*
could be a mechanic at all. It can. That puts a third option on the table which
was previously unavailable:

| | Wrecked → Kludged | Kludged → Repaired | Study |
|---|---|---|---|
| **A. As recommended above** | materials + tools, no research | materials + research behind a techprint | bonus only |
| **B. Study as accelerator** | same | same | the wreck is an `Analyse` target for the gating project — study speeds it, never unlocks it |
| **C. Study as the gate** | same | the wreck is the *primary* way to progress the project | study replaces grinding the bench |

**C chosen.** I had recommended B as the safe pick; the owner took C, and the
investigation above then showed C costs no more to build than B — the difference
between them is a *player setting*, not a line of XML. My caution was priced
against a cost that turned out not to exist.

⚠️ **The one real risk in C, carried forward:** if wrecks are the main route to a
technology, a colony with no wreck of that machine cannot progress it. On this
campaign that is mostly answered by the premise — the Kolyska's deck is *made* of
dead machines, and map authoring places them — but it stops being answered the
moment the player wants a machine whose wreck is not on their ship. **Do not let
a machine's ONLY route to knowledge be a wreck that the campaign does not
guarantee exists.** Under RR's `default` preset this is self-solving, since bench
theory still overflows; under `applied science` it is real. Worth one check when
the ladder covers more than the pilot.

**Until the defs are written, build art. Art is valid under every option above.**

---

## 3. Restricting the kludged tier's recipes

Free. VFE-Factory drives each machine from `ProcessDefs` (15 of them). The
kludged ThingDef lists a subset. No new mechanics, no C#.

Choose the subset by fiction, not by tier number: a kludged smelter should melt
slag and scrap, not run a precise alloy recipe that needs a working thermal
controller.

---

## 4. Implementation shape (no C#)

Three ThingDefs per machine. The transition is a **construction job**, not a new
system: you build the next tier over the previous one, which consumes the
materials and removes the wreck without ever letting the player *deconstruct* it
for salvage.

This keeps the mod to defs + textures. If a genuine C# need appears, record the
decision here first.

### ✅ DISSOLVED FOR v1, 2026-08-12 — the wrecks are just rubble

> "They will just be rubble for now in our initial v1. We need to speed this
> along and perform some iterative game cycles." — owner

**The blocker below only exists when the wreck is non-deconstructible.** Moving
sacred scrap to `V2.md` §7 removes the conflict outright: all three tiers are now
ordinary deconstructible buildings sharing one vanilla `replaceTags` entry, so
each can be built directly over another. No Replace Stuff dependency, no C#, no
unknowns.

⚠️ **Read the section below before restoring sacred scrap.** The two features are
coupled, and re-enabling `deconstructible=false` on its own restores the fiction
while silently deleting the repair. The likely v2 shape is in `V2.md` §7.

### 🛑 The conflict, kept because v2 walks back into it

**This section used to name Replace Stuff - Continued (WS 3526354009) as "the
compatibility target" for building-over. That was wrong, and it was wrong in the
most expensive direction: the two features this mod is built on are in direct
conflict.** Read from the mod's own shipped source on 2026-08-12, not inferred:

`Source/NewThing/NewThingFrame.cs:75`

```csharp
public static bool CanReplace(this ThingDef newDef, ThingDef oldDef)
{
    if (!oldDef.building?.deconstructible ?? false)
        return false;          // <-- a non-deconstructible target, refused outright
```

and its Harmony postfix on vanilla `GenConstruct.CanReplace`,
`Source/NewThing/CanReplaceNewThingOverOldThing.cs:17`

```csharp
if (((placing as ThingDef)?.IsNonDeconstructibleAttackableBuilding ?? false) ||
    ((existing as ThingDef)?.IsNonDeconstructibleAttackableBuilding ?? false))
{ __result = false; return; }   // <-- forces FALSE even if vanilla said yes
```

**`<deconstructible>false</deconstructible>` — the mechanical expression of
SACRED SCRAP — is precisely the condition that makes building over the wreck
impossible.** The rule that makes a wreck inviolate is the rule that stops it
ever being repaired. Replace Stuff is installed, so that postfix runs and wins.

This would not have produced a single log line. The build order would simply have
been refused, and it would have looked like a placement bug ~25 minutes into a
load. Same family as the terrain-affordance deadlock in §6.

### 🔎 The lead: vanilla 1.6 has its own `replaceTags`, and nobody here knew

Found while reading the above — Replace Stuff's own comment says *"1.6 added some
tags for replacement"*. It is a **top-level `ThingDef` field**, and Core uses it:

```xml
<ThingDef ParentName="FurnitureWithQualityBase">
    <defName>Stool</defName>
    <replaceTags><li>Chair</li></replaceTags>
```

`Stool` and `DiningChair` share `Chair`; the beds share `Bed`. Two defs carrying a
matching tag can be built over one another **natively, with no mod involved**.

If that path also honours non-deconstructible targets, the whole mechanism is one
XML field on two defs and there is no C# and no dependency.

#### ✅ Verified 2026-08-12: `replaceTags` matches `replaceTags`, not `buildingTags`

Re-checked deliberately, because this is a line whose failure produces **no log
line** — if the match were against `buildingTags`, our defs would be silently
wrong and the only symptom would be a blueprint that will not place, 25 minutes
into a load. Every `replaceTags`-bearing def in Core's furniture file:

| def | `replaceTags` | `buildingTags` |
|---|---|---|
| `Stool` | `Chair` | **none** |
| `DiningChair` | `Chair` | **none** |
| `Armchair` | `Chair` | **none** |
| `Couch` | `Chair` | **none** |
| `BedBase` | `Bed` | `Bed` |
| `SleepingSpotBase` | **none** | `Bed` |

The four chairs are mutually replaceable and carry **no `buildingTags` at all**,
so the match cannot be `replaceTags` → `buildingTags`. It is
**`replaceTags` → `replaceTags`.** `BedBase` carrying both is a coincidence of
naming, and `SleepingSpotBase` is the control: it has `buildingTags: Bed` and no
`replaceTags`, and a sleeping spot is not part of the bed replace-group.

**Our three tiers each declare `<replaceTags><li>WM_AutomatedSmelter</li></replaceTags>`,
which is the correct shape.** Also checked, since a mismatch would fail the same
silent way: all three are `size (3,4)`, all `rotatable`, all in the same
`designationCategory` — matching the conditions under which Core's four chairs
interchange.

⚠️ Still not verified, and still needs the load: that the blueprint *actually*
places over an existing tier in game. The def shape is now proven; the runtime
behaviour is not.

⚠️ **Unverified, and it is the one thing v1 cannot ship without:**

1. Does vanilla's `replaceTags` route refuse a non-deconstructible building the
   way Replace Stuff's does? The vanilla implementation was not read — only the
   field, its shape, and Core's use of it.
2. **Replace Stuff's postfix runs after vanilla and forces `false` unconditionally**
   for a non-deconstructible *attackable* building. So even a working vanilla path
   may be overridden while that mod is active.
3. Possible escape, speculative: `IsNonDeconstructibleAttackableBuilding` requires
   the building to be **attackable**. A wreck with `useHitPoints=false` may fall
   outside it. Untested, and it trades away "yields nothing if destroyed" for
   "cannot be destroyed at all" — which may be better fiction anyway.

**Resolve this before authoring more defs.** Every tier ThingDef already written
assumes a transition that currently cannot happen.

---

## 5. Scope reality

**~17 machines in VFE-Factory, all `Graphic_Multi`, 69 textures at ≥512px.**
Two damaged tiers is **~138 images**, each needing consistency across four
rotations of the same physical damage, and each needing maintenance whenever
VFE-Factory updates.

That is the real cost of this mod. It is why the pilot is exactly one machine.

### Pilot: Automated Smelter

Chosen because `ship_deck_plan.md` puts the smelter at **Phase 2** of the repair
ladder — the first machine the player restores, and the one that opens the
salvage loop. If the pipeline works for the smelter it works for everything; if
the art cost is intolerable, we learn it after 8 images instead of 138.

Its measured facts (from `art_source/AutomatedSmelter/MANIFEST.json`):

| | |
|---|---|
| Tiles | 3×4, drawn at 4×5 |
| Facings | 4 (`Graphic_Multi`) |
| Canvas | 512×640 north/south, **640×512 east/west** |
| Art | full colour, ~61% canvas coverage |
| Build cost | Steel 260, ComponentIndustrial 7 |
| Research | `VFE_BasicFactories` |

Note the transposed canvas between facings — the validator checks per file for
exactly this reason, and caught the transposition in testing.

---

## 6. Defs authored 2026-08-12 — what was decided while writing them

`Defs/ThingDefs_Buildings/Buildings_WreckedMachines_AutomatedSmelter.xml` now
holds three ThingDefs: `WM_AutomatedSmelter_Wrecked`, `_Kludged`, `_Repaired`.
Every field is either Core's or copied verbatim from
`VFEFactory_AutomatedSmelter` (donor file and line range quoted at the top of the
XML). Nothing was invented from memory.

### Why these were authored before §2 was ratified

`Defs/PLACEHOLDER.md` gated def authoring on §2. That gate is now crossed
deliberately, and the reasoning is recorded here rather than left implicit:
**§2 governs only two fields** — `<costList>` and `<researchPrerequisites>`.
Texture paths, size, comps, processes, heat, power and the deconstruct rules are
identical under every option §2 offers. Both fields carry a `⚠️ PROVISIONAL`
comment naming §2, so the unratified part is visible in the file rather than in
someone's memory. The placeholder's second gate — `check_sprite.py` passing —
was satisfied first: **12/12 ok, 0 warn, 0 FAIL**.

The provisional values implement §2's own recommendation, minus the part that
cannot be expressed yet:

| rung | cost | research | missing |
|---|---|---|---|
| → kludged | Steel 120, Component 3 | none | the Survival Tools Reborn tool requirement |
| → repaired | Steel 260, Component 7 | `VFE_BasicFactories` | **the techprint gate, which §2 says must be the true lock** |

⚠️ Until a techprint def exists, the repaired tier is gated by research alone —
which is precisely the failure mode §2 warns about, because Research Reinvented
lets a player prototype and then stop researching. Do not read the current file
as an implementation of the recommendation; it is the half of it that XML can
express today.

### `terrainAffordanceNeeded` stays `FactoryFloor` on all three tiers

Considered relaxing the wrecked tier to `Heavy` so a wreck could sit on bare
deck, and rejected it. **A floor cannot be built beneath an occupied cell**, so
a wreck standing on non-factory terrain can never have the kludged tier built
over it — the ladder deadlocks at rung one, silently, and looks like a placement
bug. Keeping the donor's value costs one authoring constraint instead:

> **Map authoring must lay `VFEF_FactoryFloor` under every wreck it places.**

That is also the better fiction — the Kolyska's wrecks died on the factory deck,
not on sand. Flagged for whoever authors the ship interior.

### The wrecked tier is buildable, and that is temporary

It carries `<designationCategory>VFEFactory_Factories</designationCategory>` and
a token Steel 30 cost purely so the ladder can be exercised by hand without dev
mode. **Remove the build entry before ship** — a player should never construct a
wreck. Marked in the XML at the costList.

### The kludged recipe subset — 3 of the donor's 6

Rule applied, per §3's "choose by fiction, not by tier number": *if it is
already mostly metal, the bodge can melt it.* Kept `SmeltMetalFromSlag`,
`SmeltMetalFromMechSlag`, `SmeltWeapon`. Dropped `SmeltApparel` (handling soft
goods without igniting them), `SmeltMetalFromChunk` (separating metal from stone
needs a working thermal stage), `SmeltMechanoid` (needs an intact feed to
swallow a whole body).

Other kludged-tier deviations, all chosen to make "it runs badly" legible in the
inspect pane rather than only in the art: 360 W instead of 300, 20 heat/sec
instead of 14, breakdown factor 6 instead of 3, `canOverclock` false,
MaxHitPoints 300 instead of 450.

⚠️ `VEF_BuildingMaxOverclockFactor` was left at the donor's `1`, **not** zeroed.
Overclocking is blocked by `canOverclock=false` alone. Zero is a value the donor
never uses and VEF's overclock arithmetic has not been read — introducing it
would have been a guess for no gain.

### Detonation, restated where an implementer will hit it

The wrecked tier has **no comps block at all**. The XML says so in a comment
addressed to whoever implements `TODO.md` §1: that def must be skipped
deliberately, not caught by a category-wide patch. The **kludged** tier is
powered and is the one that should gain the blast.

### About.xml was stale and is fixed

Its description still promised *"RESTORED — the donor mod's own building,
unmodified"* and *"the restored tier IS the original"*, both overturned by the
§1 ruling on the same day. Rewritten to describe the repaired tier as our art
and to state the two-entries-in-the-build-menu cost plainly.
