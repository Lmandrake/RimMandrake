# Nine Faults — the first permanent-choice rite (design exploration, 2026-10-01)

Item: `NINE_FAULTS_PERMANENT_RITE_1`. Status: DRAFT exploration for BENCH; nothing ruled, nothing built.

## Round 2 (owner direction 2026-10-01)

### R2.1 What he ruled

Owner card answers, 2026-10-01, typed (ledger `8a6f7bc06`):

- On the round-1 forks: *"I really like this thinking but it's not quite there yet. None of these
  feel consequential right now"*
- On redirecting breakdowns: *"Too magical. Sacrificing breakdowns yo feed a god makes sense. I
  think my response is the player can choose to not fix something and leave it broken to please
  one god and anger another. It transfers favor from one to another."*
- On the machine's fate (a shrine, destroyed, or the player chooses): *"I don't dig these."*

**What this rules.**

1. **Out:** any redirect or soaking-up of breakdowns, by a building, a rite or an outcome.
2. **The mechanic is his.** The player chooses not to repair something and leaves it broken.
   That pleases one god and angers another: favour **moves** from one god to the other. Nothing is
   created from nothing.
3. **The object is not the point.** What happens to the broken machine as a thing (shrine, slag,
   relic) is not where the consequence lives. The consequence lives in the gods.
4. **The bar is "consequential".** Round 1 failed it.


### R2.2 What favour and anger actually do today (measured)

Read on origin/main `8a6f7bc06`, in `src/RimMandrake/Ninefold/Source/` and every caller of it
under `src/`.

**The state.** Nine satiation values from -100 to +100, in five bands: Wrathful, Slighted,
Neutral, Content (from +20) and Exalted (from +60) (`SatiationBand.cs`). Each god also has a
mood that drifts at random. Every change goes through one verb, `ApplyDelta(god, amount)`, in
steps of 3, 8 or 15 (`EventMagnitude`). Nothing decays except Ta'Baa, who erodes every hour the
ship sits still.

**What reads that state today, in code. This is the whole list:**

| Reader | What it does with favour | Consequential? |
|---|---|---|
| The **front** (`GetFront`, `ReckonFrontAtLanding`) | the loudest god (largest favour, **either sign**) is reckoned "in front" at every landing, and can flip mid-map on a large swing | **not yet.** Nothing outside Ninefold reads the front. Its consumer, `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` (lights, doors, subsystems), is designed and unbuilt |
| **First contact** | a god's first big move sends his introduction letter | flavour |
| **Aftermath rule 6** (`AftermathRuleRunner.OnMentalBreakNearBattle`) | while Zizzik is Content or better, a mental break within two days of a battle can queue an aftermath incident | real, but narrow |
| **Deepfire** (LuminousPigment) | dishes and pigments push deltas; a debug view reads satiation | flavour |

**What moves around machines today, in code:**

- **Repairing** a building: Rekko **+15**, Ohm **+3** (`Patch_BuildingRepaired`).
- **Deconstructing** a repairable building: Rekko **-15**, Zizzik **+3** (`Patch_BuildingDeconstructed`).
- **A droid joining:** Ohm **+15**. Mental break: Zizzik **+15**. Explosions and fires: Zizzik
  **+3** each, among others.
- **A breakdown: nothing.** The design says *"A machine/turret/ship system MALFUNCTIONS or breaks
  down → ▲Zizzik, ↓Ohm — the Ohm⇄Zizzik see-saw firing live"* (`divine_satiation_engine.md`
  §8b.B), but no Ninefold patch touches `CompBreakdownable`. **A broken machine left broken moves
  no god at all today.**

**What favour is designed to do and does not yet.** The boons, demands, taboos and curses per god
(`divine_satiation_engine.md` §3, for example Zizzik's Creative Sparks, his Betrayal and THE
WAKING). The front god's **dispensation**: *"Every front-god ruleset is a boon AND a demand …
weapons online but fuel-hungry engines; thrifty engines but comms silence"*, with the
transponder setting raid weights while that god fronts. And the **pantheon-wide rebellion** (card
ruling V.2): *"any starved front-god can seize actuators … up to the striking image of fitting
restraining bolts on their own gods' hardware."*

**⇒ The honest finding.** In today's build a favour transfer **cannot** be game-changing, because
favour barely does anything yet. The mechanic he chose is right. Its consequence has to come from
one of the things favour is designed to drive, and every shape below names which one it depends
on.


### R2.3 Which gods are in tension over a machine

Every pair below is drawn from the god canon (`divine_satiation_engine.md` §2.0b and §8b), not
invented. In each, a machine **left broken** pleases the first god and angers the second.

| Left broken | Pleased | Angered | Canon basis |
|---|---|---|---|
| **Any machine** | Zizzik | Ohm | §8b.B, the see-saw quoted above; Zizzik's S demand, *"one breakdown left unfixed per reign-day"* |
| **Any repairable thing** | (Zizzik) | **Rekko** | repair is Rekko's single biggest delta in code (+15); *"a relic lost or left to rot"* displeases him |
| **A droid left downed or unrepaired** | Zizzik | **Ohm, hardest** | Ohm *"wants his droid servants back"*; the droid-siding tension, §4c |
| **The ship's engine or thrusters** | **Ishko** | **Ta'Baa** | *"the pantheon's central feud"* (§8b, §2.0d): Ta'Baa is launch and leaving, Ishko is stillness and the eternal lurker |
| **Comms, the trade console, the transponder** | **Ishko** | **Mob'Unloo** | Ishko's L is *"perfect concealment … no comms"*; Mob'Unloo's whole domain is the deal and the counter-gift |
| **Water machines (vaporator, filter)** | Zizzik | **Oomo** | Oomo, god of the body's waters |
| **Lights** | **Ishko** | Ohm | a lamp lit in the field is *"▲Sh'kaar + ↓Ishko (the taboo)"* |
| **Turrets** | (Zizzik) | **Sh'kaar** | Sh'kaar feeds on kills; a silent gun starves him, the one god you *"WANT starving"* |

**The point of the table.** Ohm against Zizzik is the default pair, but it is not the
interesting one. **Which gods a broken thing sets against each other depends on what the thing
is.** A dead engine sets Ishko against Ta'Baa. A dead transponder sets Ishko against Mob'Unloo.
A dead turret starves Sh'kaar. That is where choice enters.


### R2.4 What leaving a thing broken costs, over time

The cost is **the machine's job, every day it stays broken**, and it is entirely ordinary:

- **A generator:** less power every day, so less production and less comfort.
- **A turret:** a hole in the defence at every raid.
- **A vaporator:** less water on a water-starved planet.
- **A transponder or comms console:** no trade calls, no allies reached.
- **The ship's engine:** the ship cannot launch. On a gravship campaign that is the largest cost
  there is. It is also the one that **travels**: a broken ship system is broken on every map
  after this one.
- **Rekko's repair income is forgone:** every unrepaired thing is +15 Rekko never earned.

The cost grows with time and the favour grows with time, so the player is always weighing *how
long can we bear it* against *how much do we want this god's favour moved*.


### R2.5 Shapes

**One fact shapes all three, measured in the built code.** The front is the *loudest* god, and
loudness is the size of his favour **in either direction** (`GetLoudness` = `|satiation|`). So
angering a god does not quiet him. It makes him **louder**. Every transfer pushes two gods toward
the front at once: one pleased and one starved. By the ruled design (V.2), a starved god in
front can seize the ship's actuators. **Leaving things broken is how a player courts a god's
favour and a rival's rebellion with one choice.** That is the consequence already latent in the
system, and every shape below uses it.

In all three, **Nine Faults is the act of breaking on purpose.** The found rite teaches the clan
to choose which machine fails, in front of everyone, instead of waiting for chance. Leaving it
broken afterwards is the ongoing transfer he ruled. No redirect, no soak, no power. The rite
outcome sets only how cleanly the fault is made (Poor: the machine burns and nothing is
transferred). The rite does not decide what happens to the object; the gods decide what it means.

#### Shape 1. The Steered Front (per map, any machine)

- **How:** every broken thing left unrepaired moves favour once a day, by its pair in the R2.3
  table. At each landing the front is reckoned as it already is.
- **Consequence:** the player uses what they leave broken to choose **which god runs the ship on
  the next map**, and that god's dispensation (a boon and a demand) shapes the map.
- **Permanent?** No. It is a lever pulled every map.
- **Cost:** the machines' work, for as long as the player holds out.
- **Depends on:** a breakdown hook in Ninefold (small), and the front's consumer, which is
  designed and unbuilt.
- **Trade-off:** the most flexible, but the least weighty. It is a dial, not a decision.

#### Shape 2. The Ship Carries Its Faults (recommended)

- **How:** Nine Faults may only be performed on **one of the ship's own systems**: a thruster,
  the pilot console, the transponder or comms, the shield, the lights, or a water or power plant
  aboard. **VERIFIED** in Odyssey's `Buildings_Gravship.xml`: `PilotConsole`, `SmallThruster` and
  `LargeThruster` already carry `CompProperties_Breakdownable`; `GravEngine` does not. Once
  broken by the rite, the fault is **sworn**, and it flies with the ship to every map after.
- **Consequence:** the ship is the colony, so the cost is paid **everywhere, for the rest of the
  campaign**, and the transfer runs every day aboard. Each system sets a different pair against
  each other:
  - **Transponder dark:** Mob'Unloo drains into Ishko. No trade calls, no allies; the clan becomes
    a hidden clan, and Mob'Unloo grows loud and starved.
  - **A thruster dead:** Ta'Baa drains into Ishko. The ship launches weaker, or later, or
    heavier-laden (UNVERIFIED what a broken thruster does to a launch). This is the central feud,
    pushed for good.
  - **Lights out aboard:** Ohm drains into Ishko. The clan lives in the dark it prays to.
  - **A droid left down:** Ohm drains into Zizzik. The sharpest betrayal; Ohm's rebellion is the
    one the restraining-bolt arc was written for.
- **Permanent:** **favour moved is never refunded.** A sworn fault can still be repaired, because
  nothing magical stops a pawn with a wrench. But repairing it is a **betrayal of the god it
  fed**: everything he gained swings back against him as anger. The starved god's loudness stays
  where it was. Undoing the choice costs more than making it.
- **Trade-off:** heavy, slow and personal. The player is choosing which god the ship becomes, and
  which god it rebels against, and lives with it on every map.
- **Depends on:** the breakdown hook, a sworn-fault flag Scribed with the ship part (UNVERIFIED
  that comp state survives a gravship launch and landing; the part moves, so it should), and the
  front's consumer.

#### Shape 3. The Rejected God (once per campaign)

- **How:** Nine Faults is performed **once in a campaign**. The clan names the god it turns from,
  breaks one of his machines from the R2.3 table, and swears never to mend it.
- **Consequence:** that god drains every day **for the rest of the campaign** into the god the pair
  names. Inevitably he becomes the loudest and starved. When he fronts, he is the god whose
  rebellion the clan must answer with restraining bolts. The clan has chosen its enemy god on
  purpose.
- **Permanent:** fully. The rite seals and cannot be performed again.
- **Trade-off:** the most dramatic and the most irreversible. It turns one god into the
  campaign's antagonist by choice, and it gives up that god's boons for good. It is also the
  bluntest: one decision, then consequences arrive on their own.
- **Depends on:** the actuator rebellion (designed, card ruling V.2, unbuilt) as well as the
  front's consumer. Without that, it is only a number falling.

#### Side by side

| | 1 Steered Front | **2 Ship Carries Its Faults** | 3 Rejected God |
|---|---|---|---|
| Scope | any machine, per map | the ship's own systems, every map after | one god, whole campaign |
| Irreversible | no | costly to undo (no refund, repair is betrayal) | yes, sealed |
| What it decides | who runs the next map | which god the ship becomes, and which one it angers | which god is the clan's enemy |
| Cost borne | machines' work, while held | a ship system's work, everywhere | one machine plus one god's boons, forever |
| Needs unbuilt | front consumer | front consumer, sworn-fault flag | front consumer, actuator rebellion |

**Recommended: Shape 2.** It is the only one where the cost travels and compounds, which is what
"consequential" asked for. Each ship system brings its own pair from canon, so the choice is
*which* god as well as *whether*. It is irreversible by price rather than by fiat, so it stays
non-magical. **Whatever shape he picks, the consequence is hollow until the front has a consumer.**
`ATMOSPHERIC_BASE_BUILD_PROGRAM_1`, or at least the front-god dispensation, is the real
prerequisite, and that should be said to him plainly.


### R2.6 Questions for the owner

**Q1. Which shape?** Leaving a broken thing unrepaired moves favour from one god to another, as
you ruled. Which pair depends on what the thing is. A dead transponder takes from Mob'Unloo
(trade) and gives to Ishko (hiding). A dead thruster takes from Ta'Baa (leaving) and gives to
Ishko (stillness). A downed droid takes from Ohm and gives to Zizzik. In the code, an angered god
grows *louder*, not quieter, so an angered god can end up "in front" of the ship, starved, and a
starved god in front can seize the ship's lights and doors. There are three ways to make that
consequential:
- **(1) Steered front:** any broken thing, map by map, to choose which god runs the next map.
  Flexible, but not a lasting decision.
- **(2) The ship carries its faults (recommended):** Nine Faults may only break one of the ship's
  own systems, and that fault flies with the ship to every map after. Repairing it later is a
  betrayal of the god it fed, and the favour it moved is never returned.
- **(3) The rejected god:** once a campaign, the clan names a god it turns from and breaks his
  machine for good. He becomes the campaign's enemy god.

**Q2. Should repairing a deliberately broken thing be allowed, but punished?** Nothing magical
stops a colonist from repairing it. The proposal is that the favour it moved stays moved and the
god it fed takes the repair as a betrayal, so the favour swings back as anger. The other options
are that repairing simply stops the transfer with no penalty (gentler, and less permanent), or
that the rite's machine can never be repaired at all (permanent, but a rule rather than a
choice).

**Q3. Should the gods' favour do something real before this is built?** Today, in the code, a
god's favour barely affects play. The "god in front" is worked out at every landing, but nothing
reads it yet. The lights, doors and ship behaviour it is meant to steer are designed and not
built (the atmospheric base program), and so are the gods' boons and the starved-god rebellion.
A breakdown left unfixed moves no god at all yet either. Should Nine Faults wait for the "god in
front" to steer the ship, or should it come first and be the reason that gets built?


### R2.7 Flagged by the no-redirect ruling (not edited)

These diverge from the 2026-10-01 ruling that any redirect or soak of breakdowns is too magical.
**Listed only, not edited**, per the coordinator.

- **Zizzik's decoy heap**, `design/Jawa/folk_gesture_mechanics.md` §1: *"a room containing a decoy
  passes a small fraction of its breakdown rolls to the decoy instead"*. Draft, not built.
- **The Kept Mistake**, Fair and Good outcomes, `design/Jawa/biome_rites_pass_2026-10-01.md` §1.3
  (register B7, pitched): *"the party's first mishap in the Bloom … lands on the decoy instead"*.
- **GPT's Nine Faults** in `Transient/bedazzle_gpt_enrich_2026-10-01/lanterndeeps.md` §5 (a
  Transient file; it ages out on its own).


---

# Round 1 (background; the forks were rejected and removed)

## 1. The owner's words and the pitch

Owner, 2026-10-01, typed: *"This is the first rite with a permanent decision and consequence.
That's pretty cool. Like a game changing decision. We should explore this further."* He picked
the rite for the Lantern Deeps.

The pitch as it stands is `design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md`
§6 R2. Worshippers surround one healthy, powered machine of real value and miswire it, nine
faults in sequence, into a controlled breakdown in front of everyone. Poor: the machine burns.
Fair: Zizzik's meter vents a step. Good: two steps, and the broken vessel stays standing as a
fault-board. Excellent: plus an art tale. It is found as an inscription beside a dead droid that
crossed its own nine wires before the mindstone could take its mind.

GPT's original (`Transient/bedazzle_gpt_enrich_2026-10-01/lanterndeeps.md` §5) had the rite bank
"vented faults". Later natural breakdowns in that settlement would be redirected into the
consecrated vessel, damaging it and using up the charges while the real machines kept running.
BENCH cut that as a granted power.

**What the owner reacted to.** The permanent part of the pitch is small: a good machine is
broken for good. What he called "game changing" is the shape: one deliberate, irreversible act
the clan chooses and lives with. Sections 4 to 6 take that shape seriously.

## 2. The no-powers rule — its actual source

**The exact sentence BENCH cited is BENCH's own prose, pitched and not yet ruled.** It first
appears in `design/Jawa/biome_rites_pass_2026-10-01.md` §0 ("Laws checked on every rite"), added
by `054fc56fe` (2026-10-01, "Biome rites pass: 23 found rites…", status *"PITCHED, owner to
rule"*):

> *"There are no fantasy tropes: no rite grants a power, no god appears, and an outcome is a
> mood, a memory, a ledger entry, a meter step, or an ordinary thing."*

That sentence condenses two older laws, which are the real authority:

1. **`design/Jawa/mods/forbidden_mods.md`, line 126** (in the repo since its re-initialisation,
   `7e9800403`, 2026-08-13; the fluid-ideology entry):
   > *"Ideology's job here is identity/obligation/taboo/ritual, not a stream of
   > specialists/recruits/powers/optimized production. … **Rituals create cohesion, not material
   > rewards** (no ritual-generated recruits/animals/goodwill/quest sites/psylinks/artifacts). At
   > most ONE culturally-important relic with modest mechanical value."*

   `design/Jawa/concept.md` §6's hard-never list repeats it as *"ritual loot payouts"*.
2. **The pantheon canon, `design/Jawa/divine_satiation_engine.md` §2.0b** (moved there 2026-08-20
   from the deleted `jawa_xenotype_and_religion.md`, whose §2.0 ground rules cited
   `forbidden_mods.md`):
   > *"None grant powers (no Force, no psycasts — §2.0 rules bind); each is a **belief that
   > shapes behavior**"*

**What the law actually forbids, read closely.** The source law bans *material rewards* and
*powers* in the Force/psycast sense, and names the list: recruits, animals, goodwill, quest
sites, psylinks, artifacts. It does **not** forbid a rite changing a god's arithmetic. The
Ninefold engine itself grants boons from a god's state (Zizzik's are Creative Sparks, Betrayer's
Gift and The Grand Short-Circuit, `divine_satiation_engine.md` §⑦). So the rite-safe route is
already there: **a rite moves a god; the god's state does the rest.** Every fork below stays on
that route, and says where it would leave it.

**Two inconsistencies the trim exposed. Both are for the owner, not BENCH, to settle.**

- **The Kept Mistake** (`biome_rites_pass_2026-10-01.md` §1.3, Zizzik, pitched in the same pass
  under the same law) has a Fair outcome in which *"the party's first mishap in the Bloom … lands
  on the decoy instead"*. That is the redirect GPT proposed and BENCH cut from Nine Faults.
- **Zizzik's decoy heap** (`design/Jawa/folk_gesture_mechanics.md` §1, draft 2026-08-30,
  promoted by the owner's door ruling to a micro-mechanic and not built) is a 1x1 building that
  *"passes a small fraction of its breakdown rolls to the decoy instead"*. That is a standing
  redirect of breakdowns, already in canon as a building.

Answered by the owner 2026-10-01: any redirect is too magical and OUT (Round 2, R2.1, R2.7).

## 3. What already exists (search before inventing)

Searched on origin/main `b0adb7541`.

- **`mandrake.rut.rites` (`src/RimUtinni/Rites/`)** holds `About.xml`, `RUT_Rites_Research.xml`
  and `validation.py`. **No C#, no `RitualPatternDef`, no outcome worker yet.** Every Salvation
  ritual is still design (`SALVATION_RITES_UNIFICATION_1`).
- **`mandrake.rm.ninefold` (`src/RimMandrake/Ninefold/`)** is built. `GameComponent_Ninefold`
  Scribes per-god satiation, mood, unveiled flags, first-contact queue, violent-death count,
  last-launch tick and the front god. Its public verb is `ApplyDelta(God, amount, reason)`.
  **It has no slumber bank field, no per-god permanent modifier, and no record of a vow.**
  `MoodAmplitude` (Zizzik 0.80) is a `static readonly` array, so nothing can change a god's
  temperament per game today. `FLAWED_MASTERWORK_ENGINE_CHECK_1` found the same gap from the
  other side: there is no per-call damping hook either. Any permanent fork needs one new Scribed
  field in this component (§7).
- **Zizzik in code:** `God.Zizzik` (*"the Spark-Maker – malfunction, betrayal, bad luck"*);
  Aftermath rule 6 reads his band through `NinefoldBandBridge.ZizzikAtLeastContent()`;
  LuminousPigment's Deepfire dishes feed him. **No breakdown mechanic of ours touches
  `CompBreakdownable`** except unrelated power-plant and Gizka code.
- **Zizzik's design, already shipped as design** (`divine_satiation_engine.md` §⑦, *"the banked
  wake"*): feed him and his wakes stay small; starve him (perfect uptime) and he BANKS a wake that
  lands all at once. His M demand is *"a burnt offering (destroy one working thing)"*. The
  controlled-waking rite (register B4, its Leaning Scrub form the Calling-Pyre) spends the bank
  early.
- **The Gift of Working Things** (`design/Jawa/devotional_sacrifice_catalog.md`, Zizzik):
  *"select one FUNCTIONING machine and destroy it at the shrine-heart … BUYS: the largest single
  bank payment available outside a full rite"*, with a small `↓Rekko` on every gift. **This is
  Nine Faults' act without the rite.** Round 2 separates them: Nine Faults' consequence is the
  favour transfer while the thing stays broken, not the machine's fate.
- **Sacred scrap** (`design/Jawa/worldbuilding/ideoligion/`, the ship's destroyed factory machines
  may not be touched until repaired) and **Rekko** (*"scrapping the repairable"* grieves him).
  Breaking a good machine on purpose is a deliberate war with Ohm's and Rekko's pieties, which
  §⑦ already says of Zizzik's feeding.
- **Zizzik's decoy heap** (`folk_gesture_mechanics.md` §1), the standing breakdown redirect (§2
  above). Not built.

## 4. What makes a rite's decision permanent

Every rite in the register so far is a **repeatable transaction**: do the act, move a meter,
come back next season. A meter moves back. A permanent rite is different in kind: **the act
closes a door the player can never reopen, and the campaign remembers which door.** Six things
can be made irreversible, from smallest to largest.

| What is fixed for good | Example | Reach | Feels game-changing? |
|---|---|---|---|
| A thing destroyed | the vessel burned | one object | no: the Gift of Working Things already does this, repeatably |
| A thing changed and kept | the vessel stands forever as an unrepairable fault-board | one object, one map or ship | a little: it is a scar you walk past |
| A mark on the clan | every Jawa present carries "was there at the Nine Faults" for life | the people | moderately: a memory with no end date |
| A god's standing | Ohm will never again fully trust this clan; Zizzik's wake is capped | the pantheon arithmetic, campaign-wide | **yes**: it changes every later reckoning |
| A standing condition | one class of machine is Zizzik's from now on | the whole colony's play | **yes**: it changes what you build |
| A one-time choice | the rite can be performed once per campaign, and only one answer can be given | the campaign | **yes**: it is a fork in the story |

**The four tests a permanent rite should pass.**

1. **Once.** It can be performed once per campaign, or once per subject. Afterwards the Rites tab
   shows it as *sealed*, with what was chosen, instead of offering it again.
2. **Both sides cost.** A permanent choice with only an upside is a power, and the law forbids
   it. Each face of the fork must take something from one god while it gives to another.
3. **Readable forever.** A permanent mark nobody can see is not a consequence (the planet-wide
   rule: nothing vanishes without a readable sign). The vessel, an inscription on the Rites tab, a
   line in every later Ninefold letter.
4. **Through the gods, never around them.** The permanence lives in the Ninefold arithmetic or in
   an ordinary thing. It never gives the player a new button that does something good.

## 6. Should "permanent choice" be a class of rite?

**Yes, but small, and only after Nine Faults proves it.** A permanent rite is exciting because it
is rare. If a dozen rites each lock a fork, the campaign becomes a checklist of vows, and each
one matters less. Proposed shape, for the owner to rule (Q4):

- **Name:** *sealed rites*. Once performed, the Rites tab shows them sealed, with the answer given.
- **Cap:** at most one per god, and probably three or four across the whole register.
- **Every sealed rite passes §4's four tests:** once, both sides cost, readable forever, through
  the gods.
- **Register column:** a `sealed: yes` flag on each row, set during
  `SALVATION_RITES_RENORMALIZE_PASS_1`, rather than a new kind beside the six (feeding,
  settlement, starving, venting, consolation, warding). Sealed is *how long* a rite lasts, not
  *what* it does to a god.

**Candidates from the existing register** (98 rows, `design/Jawa/salvation_rites_2026-10-01.md`
§b), chosen because their act is already irreversible or nearly so:

| Rite | God, kind | Why it could be sealed | The fork it would lock |
|---|---|---|---|
| **Zizzik's Nine Faults** (Lantern Deeps, §6 R2) | Zizzik, venting | the pilot | see Round 2 |
| **The Seating** (register B4; `design/RimMandrake/ancient_machines_design.md` §5.2) | Rekko, feeding | a relic seated into a hull socket; the campaign allows one relic | which relic, in which socket: the ship's one sacred heart |
| **The Salted Keeping** (Wasteland, `biome_rites_pass_2026-10-01.md` §2.2) | Ozzik, venting | the clan's finest thing buried at the place pride ended | today it can be dug up again; sealed, it never can, and Ozzik's pride-meter is permanently lowered |
| **The controlled waking** (register B4; Leaning Scrub form, the Calling-Pyre) | Zizzik, settlement | the bank spent on the player's chosen day | *not* a good candidate: it should stay repeatable, because Zizzik's wake recurs |

**One caution, from the owner's own history** (CLAUDE.md, the Q11a lesson): when a category starts
generating sub-questions, ask whether the category is needed at all before adjudicating inside
it. So the class is a question to put once, after he has ruled on Nine Faults, not a framework
to build first.
