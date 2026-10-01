# Nine Faults — the first permanent-choice rite (design exploration, 2026-10-01)

Item: `NINE_FAULTS_PERMANENT_RITE_1`. Status: DRAFT exploration for BENCH; nothing ruled, nothing built.

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

So either a breakdown redirect is a power, and those two are wrong too, or it is a god's folk
habit, and GPT's version was never forbidden. Question Q2 in §8 asks him.

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
  Nine Faults' act without the rite.** Nine Faults must differ from it, and the clean difference
  is that the vessel is not destroyed: it stays standing, broken on purpose, for good.
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

## 5. Fork designs for Nine Faults

Four versions. The common core is the same in all four: the inscription, the nine bulbs failing
in sequence, the vessel miswired in front of everyone, Poor = the vessel burns. What differs is
**what becomes permanent**.

### Fork A. The Fault-Board (a scar, per vessel)

- **The act:** as pitched. The chosen machine is miswired and stays standing.
- **Permanent:** the vessel becomes a *fault-board* for good: unrepairable, undeconstructable, its
  function gone. It is the inverse of sacred scrap. Sacred scrap may not be touched until it is
  repaired; a fault-board may be touched but may never be repaired. It travels with the ship if it
  stood on the ship.
- **God arithmetic:** Zizzik's bank vents in proportion to the vessel's value (Fair 1 step, Good
  2). Ohm and Rekko each take a small permanent knock while it stands. If the board is ever
  destroyed, the knock lifts, and Zizzik is owed.
- **Trade-off:** you lose a real machine and gain a smaller, gentler wake. Repeatable on new
  vessels, so the permanence is local.
- **Law:** clean. A meter step and an ordinary (broken) thing.
- **Verdict:** the honest minimum, and closest to the pitch, but not "game changing". The Gift of
  Working Things already does nearly this.

### Fork B. The Covenant of the Nine (once per campaign: a class of machine given to him)

- **The act:** the organiser names, aloud, the class of machine the vessel stands for: power,
  doors, defences (turrets), workbenches, or droids. The vessel is one of that class. **It can be
  performed once per campaign.** The inscription's dead droid gave him its own mind; the clan
  gives him one kind of thing.
- **Permanent:** from then on, that class is Zizzik's.
  - Every breakdown of that class **feeds** Zizzik instead of banking his wake. Leaving it unfixed
    for a day honours him.
  - Ohm never again takes that class as his: repairs on it no longer please Ohm, and building more
    of it mildly offends him.
  - The class carries a permanent visible mark (a chartreuse fault-tag on the inspect pane and the
    nine-bulb motif on the sprite overlay).
- **Trade-off:** a real fork in how you build. Give him **power**, and outages become worship,
  while Ohm turns away from your generators. Give him **turrets**, and every defensive jam is
  holy, a scary bet. Give him **droids**, and Ohm's own servants are the bad-luck god's: the
  sharpest betrayal in the pantheon, since Ohm *"wants his droid servants back"*.
- **Law:** it bends nothing. It does **not** change how often anything breaks (vanilla's breakdown
  rate is untouched). It changes only which god each breakdown moves, for good.
- **Verdict:** the strongest "game changing" candidate. One decision, campaign-long, visible on
  every machine of the class, and both gods' arithmetic moves.

### Fork C. Ohm's Mirror Broken (once per campaign: the clan takes a side between rivals)

- **The act:** the vessel must be **a machine Ohm loves**: a working droid's charging rack, a
  conduit choir array, or a running droid itself if the clan will bear it. Zizzik and Ohm are
  mirrors (*"the wrong spark against the right one"*). The rite breaks the mirror on one side.
- **Permanent:** the clan has **chosen Zizzik over Ohm**, and both gods remember.
  - Zizzik's wake is permanently **capped**: his bank cannot grow past a ceiling, because a clan
    that once broke the right spark for him is a clan he never needs to teach.
  - Ohm's ceiling is permanently **lowered**: his highest satiation band (and the L boon it opens)
    can never again be reached. He forgives, but he does not forget.
- **Trade-off:** safety from the worst catastrophe, bought with the machine god's best gift, for
  the whole campaign. A Jawa clan that leans on droids should never take it; a clan that has
  lost its droids might.
- **Law:** this is **where a version bends it**. A permanent cap on a catastrophe is a standing
  benefit. It stays inside the law only because it is paid with a permanent loss of equal weight,
  and because it works through a god's state, not a button. If the owner reads "a smaller
  catastrophe forever" as a power, Fork C is out.
- **Verdict:** the most dramatic god-standing fork, and the only one that writes the Ohm–Zizzik
  rivalry into the save. The riskiest to balance.

### Fork D. The Redirect, kept honest (GPT's version through the decoy heap)

- **The act:** as pitched. The vessel becomes a fault-board.
- **Permanent:** the fault-board works as a **great decoy heap**: while it stands, a fraction of
  breakdowns in its room or ship pass to it instead, charring it, until it is spent and falls to
  slag. It cannot be repaired or re-consecrated; one per ship, ever.
- **Trade-off:** a valuable machine traded for a finite, visible buffer against bad luck, which
  ends for good.
- **Law:** under BENCH's sentence this **is** a granted power, which is why it was cut. Under the
  source law it is arguable: it is the same mechanic as the decoy heap folk gesture the owner's
  door ruling already promoted, and the same as the Kept Mistake's Fair outcome. It turns on Q2.
- **Verdict:** the best *game feel* of the four, and GPT's real idea. Only if Q2 says a redirect
  is a god's habit, not a power.

### Side by side

| | A Fault-Board | B Covenant | C Mirror Broken | D Redirect |
|---|---|---|---|---|
| Once per campaign | no (per vessel) | **yes** | **yes** | one per ship |
| What is permanent | a broken machine | a class of machine changes god | two gods' ceilings | a finite buffer that ends |
| Game-changing | low | **high** | **high** | medium |
| Law | clean | clean | bends (paid for) | turns on Q2 |
| Build cost | S | M | M | M |

**BENCH-subagent recommendation:** **Fork B**, with Fork A's fault-board as its readable mark
(the vessel stays standing, unrepairable, as the Covenant's witness). It is the only one that is
both clean under the law and changes how the rest of the campaign is played.

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
| **Zizzik's Nine Faults** (Lantern Deeps, §6 R2) | Zizzik, venting | the pilot | which class of machine is his (Fork B) |
| **The Seating** (register B4; `design/RimMandrake/ancient_machines_design.md` §5.2) | Rekko, feeding | a relic seated into a hull socket; the campaign allows one relic | which relic, in which socket: the ship's one sacred heart |
| **The Salted Keeping** (Wasteland, `biome_rites_pass_2026-10-01.md` §2.2) | Ozzik, venting | the clan's finest thing buried at the place pride ended | today it can be dug up again; sealed, it never can, and Ozzik's pride-meter is permanently lowered |
| **The controlled waking** (register B4; Leaning Scrub form, the Calling-Pyre) | Zizzik, settlement | the bank spent on the player's chosen day | *not* a good candidate: it should stay repeatable, because Zizzik's wake recurs |

**One caution, from the owner's own history** (CLAUDE.md, the Q11a lesson): when a category starts
generating sub-questions, ask whether the category is needed at all before adjudicating inside
it. So the class is a question to put once, after he has ruled on Nine Faults, not a framework
to build first.

## 7. Engine route

Checked against decompiled RimWorld 1.6 with RimSage on 2026-10-01 where marked **VERIFIED**;
everything else is **UNVERIFIED**.

- **The ritual itself:** `PreceptDef` + `RitualPatternDef` + `RitualOutcomeEffectDef` in
  `mandrake.rut.rites`, learned through the found-rites row (`Ideo.AddPrecept(..., fillWith)`,
  already UNMEASURED in `SALVATION_RITES_UNIFICATION_1`). **VERIFIED:** `Ideo.AddPrecept(Precept,
  bool init, FactionDef, RitualPatternDef fillWith)` and `Ideo.RemovePrecept(Precept, bool
  replacing)` both exist.
- **The outcome:** a subclass of `RitualOutcomeEffectWorker_FromQuality`. **VERIFIED:** its
  `Apply` computes quality and outcome, then calls `ApplyExtraOutcome(...)` and
  `ApplyAttachableOutcome(...)` before sending the letter and memories, so the vow is written in
  an override of `ApplyExtraOutcome`, and its text lands in the vanilla outcome letter.
- **Choosing the vessel:** a `RitualObligationTargetFilter` that accepts only a powered,
  undamaged building with `CompBreakdownable` above a value floor (Fork B), or one of Ohm's
  machines (Fork C). **VERIFIED:** `RitualObligationTargetWorker_Thing` and `_ThingDef` exist as
  bases. UNVERIFIED: the cleanest way to put the class choice (Fork B) in the ritual dialog; a
  float menu or a dialog before the ritual starts is the likely route.
- **Breaking the vessel:** **VERIFIED:** `CompBreakdownable.DoBreakdown()` sets the broken flag,
  broadcasts `"Breakdown"` and notifies the map's `BreakdownManager`. The permanent fault-board
  needs a comp of ours that refuses repair (a Harmony prefix on the repair path or a
  designation block; UNVERIFIED which is cleaner).
- **The permanent record:** campaign-wide state belongs in `GameComponent_Ninefold`, which already
  Scribes per-god state. Add one Scribed field: the sealed rites performed and the answer given
  (Fork B: the machine class; Fork C: the two ceilings). **VERIFIED:** both `GameComponent` and
  `WorldComponent` exist as `IExposable` bases; GameComponent follows the save, which is right
  for a campaign vow. Fork C also needs `MoodAmplitude` or a bank ceiling to become per-game
  state, since it is `static readonly` today (read on origin).
- **Fork B's effect:** **VERIFIED:** vanilla breakdowns roll in `CompBreakdownable.CheckForBreakdown()`
  as `Rand.MTBEventOccurs(13680000f, 1f, 1041f)`, a hard-coded constant. Fork B **leaves that
  alone**. It needs only a postfix on `DoBreakdown()` that reads the vow, checks the parent's
  class, and calls Ninefold `ApplyDelta` for Zizzik instead of the default route. The repair-side
  Ohm change is a branch in the existing `Patch_BuildingRepaired`.
- **Fork D's effect:** a prefix on `CheckForBreakdown()` or `DoBreakdown()` that diverts the
  event to the board: the same patch the decoy heap would need, so the two should share one
  implementation.
- **Once only:** the ritual's target filter refuses when the vow flag is set, with the reason
  *"Sealed: the clan gave him …"*. UNVERIFIED whether a sealed ritual should then be removed with
  `RemovePrecept` or stay listed as unperformable; staying listed is more readable.
- **Precedent for an irreversible ritual in vanilla Ideology:** **VERIFIED** that
  `RitualObligationTargetWorker_AnyRitualSpotOrAltar_Scarification` and `_Blinding` exist.
  Ideology already ships rituals whose outcome is permanent (on a pawn's body), so a permanent
  rite is not foreign to the system.
- **Dependency:** Fork C, and any per-call damping, collide with `FLAWED_MASTERWORK_ENGINE_CHECK_1`:
  both want Ninefold to take a modifier it does not take today. Build that once.

## 8. Questions for the owner

Drafts for BENCH's cards. Each one explains its subject in full.

**Q1. Which version of Nine Faults?** Zizzik is the Jawa god of malfunction and bad luck. If he is
starved by a perfectly run colony, he banks a catastrophe and drops it all at once. Nine Faults
is the rite you learn in the Lantern Deeps. The clan breaks one good working machine on purpose,
in front of everyone, to let his spark out where they choose. You called it the first rite with
a permanent decision. There are four ways to make it permanent:
- **A. The scar:** the machine stays forever as a broken, unrepairable fault-board, and Zizzik's
  banked catastrophe shrinks. It can be done again on other machines. Simple, but small.
- **B. The covenant (recommended):** once per campaign, the clan names one kind of machine (power,
  doors, turrets, workbenches or droids) and gives it to Zizzik forever. From then on, that kind
  breaking down pleases him instead of building toward his catastrophe, and Ohm, the machine god,
  turns away from it. Breakdowns happen no more often than before. What changes, for good, is
  which god each breakdown feeds.
- **C. Choosing Zizzik over Ohm:** once per campaign, break one of Ohm's own machines. Zizzik's
  worst catastrophe is capped forever, and Ohm's highest favour can never be reached again.
  Dramatic, but it is close to a permanent benefit.
- **D. GPT's original:** the broken machine soaks up some of the colony's future breakdowns until
  it wears out. The best game feel, but it was cut as a power (see Q2).

**Q2. Is "a breakdown lands on the broken thing instead" a power?** There is a rule that a rite
may not grant a power. Its source is the forbidden-mods list: rituals create cohesion, not
material rewards, so no recruits, animals, goodwill, quest sites, psylinks or artifacts, and the
gods grant no Force or psycasts. The exact phrase "no rite grants a power" was written by an
agent on 2026-10-01 in the biome rites pass, and you have not ruled on it. Two pieces already in
the design do exactly what GPT's Nine Faults did. Zizzik's decoy heap is a folk-gesture building
you promoted on 2026-08-30: a broken thing kept in a room takes some of the room's breakdowns.
The Kept Mistake, a Contagion rite pitched in the same pass, lands an expedition's first mishap on
a decoy. Is diverting a breakdown onto a sacrificed object a god's habit you allow, or a power you
forbid? Whichever you choose also decides the decoy heap and the Kept Mistake.

**Q3. Should the machine survive as a broken shrine, or be destroyed?** The Gift of Working
Things, a Zizzik devotion already designed, destroys a working machine outright for his largest
single offering. If Nine Faults also destroys its machine, the two are the same act. The proposal
is that Nine Faults' machine stays standing, broken on purpose and never repairable, as a mark
everyone walks past. It is the opposite of sacred scrap, which may not be touched until it is
repaired. Keep it standing?

**Q4. Should "permanent choice" become a rare class of rite?** Every rite so far can be repeated,
and moves a god's meter, which moves back. A *sealed rite* could be performed once per campaign,
and its answer would be fixed for good and shown on the Rites tab. The proposal is at most one per
god, three or four in the whole set. The other candidates are: the Seating, where the clan's one
relic is set into the ship for good; and the Salted Keeping, where the clan's finest thing is
buried in a Wasteland crater and could never be dug up again. Or should Nine Faults stay the only
one, which keeps it special?

**Q5 (only if B is chosen). Which machine classes may be offered?** The options are power,
doors, turrets, workbenches and droids. Droids are the sharpest choice, because Ohm wants his
droid servants back and this would give them to his rival forever. Turrets are the scariest,
because every defensive jam becomes holy. Should any class be off the list?
