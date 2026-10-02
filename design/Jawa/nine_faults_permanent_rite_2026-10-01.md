# Nine Faults — the first permanent-choice rite (design exploration, 2026-10-01)

Item: `NINE_FAULTS_PERMANENT_RITE_1`. Status: DRAFT exploration for BENCH; nothing ruled, nothing built.

## THE RULED DESIGN (owner, 2026-10-01, rounds 3 and 4)

### 1. His rulings

**Round 3** (ledger `5f9b8da6a`, typed): *"These aren't good. Carrying broken machinery forever is
too heavy, the player's choose the next landing site not the gods, and you're never allowed to just
write off a god as evil"* · *"It's only ok to leave behind something broken as an offering, and then
it is lost forever"* · by card: build Nine Faults together with real effects for god favour.

**Round 4** (ledger `566d2269a`, typed): *"You're right. Zizzik would be better served by breaking a
new piece of machinery you just found rather than leaving it behind. And leaving things behind that
work is more ta baa."* · *"Yes events and world and subtle probabilities. Thenjawa sjoild receive
very little concrete evidence of the gods remover, but to them it will feel certain they are there
and powerful. Nothing so coarse as hediffs of skill blessings."* · by card: remove "evil" from every
god, everywhere (`GODS_NOT_EVIL_SWEEP_1`, done in the same pass as this doc).

**What stands, together:**
1. **Nine Faults is Zizzik's:** the clan breaks a machine it **has just found**. It is not left
   behind.
2. **Leaving working things behind is Ta'Baa's:** the existing devotion, the Left Behind.
3. **Every offering is lost forever**, and it moves favour from one god to another.
4. **Favour shows only through events, the world, and subtle odds.** No hediffs, no skill or stat
   blessings. The Jawa get almost no concrete evidence, yet feel certain.
5. **The player chooses where the ship lands, never a god.** No god is evil, and no god is the
   clan's enemy.
6. **No breakdown is ever redirected or soaked up.** Nothing broken is carried along.


### 2. Nine Faults (Zizzik): breaking the newly found machine

**The belief.** The first spark through a found machine is Zizzik's. A thing the clan has just
dragged out of a ruin has not yet been anyone's: not Ohm's, who wakes machines, and not Rekko's,
who restores them. Zizzik is the god of things coming apart, and he is owed the chance to take
it first. A clan that gives him its newest find, unused, has paid him before he comes to collect.
This matches the inscription: the dead droid in the Lantern Deeps crossed its own nine wires
before the mindstone could take it.

**When "newly found" applies.** The machine must meet all three:
- **Found on this map.** It came into the clan's hands here, by claiming a ruin building,
  uninstalling one from a wreck or ancient site, or hauling in a minified machine that dropped,
  crashed or was dug up.
- **Never run by the clan.** It has not been switched on, powered or worked at since the clan took
  it.
- **Still on this map.** Once the ship lifts, the chance has gone: a find carried to the next map is
  simply the clan's machine.

The machine is marked "fresh find" when the clan takes it. The mark clears the first time the clan
uses it, or when the ship departs. The Rites tab shows which finds are eligible.

**The rite.** As found in the Lantern Deeps (§6 R2 of the review). Worshippers surround the find and
miswire it, nine faults in sequence, the nine bulbs failing one by one, in front of everyone.
- **What it costs:** the best thing the salvage gave up. The clan offers the machine it has not yet
  had the use of, and it is gone. The rite also takes the participants' hours.
- **Lost forever:** the ninth fault burns the machine out. It is destroyed and leaves a burnt-out
  hulk of slag where it stood, so the loss is readable on the ground.
- **Outcomes:** Poor, the miswiring catches early: a real fire and a smaller offering. Fair, the
  nine faults run true: a full offering. Good, plus a "we gave him the first spark" memory for the
  participants. Excellent, plus an art tale.

**Which favour it moves.** **Zizzik gains. Rekko loses.** A find is Rekko's by nature, because *"a
neglected machine wants the second hand that will wake it"*, and this one will never be woken. The
transfer is sized by the find's market value (Ninefold's Small 3 to Large 15), equal out of Rekko
and into Zizzik, and the outcome quality scales it.

**What it is not.** The clan does not offer its own working machine; that is the Gift of Working
Things (`devotional_sacrifice_catalog.md`, Zizzik), and whether the two stay separate is Q1.
Breakdowns are not redirected, and nothing broken is carried.


### 3. Leaving working things behind is Ta'Baa's: the Left Behind

**Home:** the Left Behind, `design/Jawa/devotional_sacrifice_catalog.md` (Ta'Baa):
*"ACT: at launch, deliberately leave one VALUABLE thing on the old map — chosen, named at the
launch-rite, abandoned. COST: the thing, forever. BUYS: the launch spike enlarged; the next
rooted-clock runs slower (you have proven you can let go). SIGN: from the climbing ship, the left
thing glints once, like a wave."*

**What this design proposes for it** (owed to the catalog entry once he rules; not edited there):

- **What is left:** a **working** building of the clan's, off the ship, marked *"Leave behind"*
  before departure. It must be in working order: a working thing is a real letting-go, whereas a
  broken one is only rubbish left on the ground.
- **Lost forever:** VERIFIED that on a gravship departure Odyssey's `GravshipUtility.AbandonMap`
  sends off every pawn left behind and abandons the map (`Abandon(wasGravshipLaunch: true)`). The
  clan flies away from it, which is not magic. UNVERIFIED whether every departure goes through
  `AbandonMap`.
- **Which favour it moves:** **Ta'Baa gains.** The god whose work the machine did loses, for a
  working thing of his given up:

  | Left behind, working | Loses favour | Canon basis |
  |---|---|---|
  | Power: generator, battery | Ohm | the living machine |
  | Droid support: charger, droid bench | Ohm | *"wants his droid servants back"* |
  | Water, kitchen, freezer | Oomo | the body's waters; Cooking (§2.0c) |
  | Comms, trade beacon | Mob'Unloo | the deal |
  | Salvage workbenches | Rekko | Crafting from salvage (§2.0c) |
  | Research, art, high-tech benches | Ozzik | Intellectual, Artistic, high-tech building (§2.0c) |
  | Turrets, walls of machinery | Ishko | the turtle that outlasts |

  Sized by market value as above. One letter at departure names what was left; the catalog's sign
  (the glint from the climbing ship) is the readable mark.


### 4. How favour shows: events, world and subtle odds

**The rule.** A god's standing **tilts the odds** of a few things in his domain coming to the clan's
map: incidents, traders, finds and weather. Nothing is labelled. No letter says "because Ohm is
pleased". No tooltip, hediff, stat or skill shows it. The player can see the standings in the
Ninefold readout and the Narrator's landing report, and can only *infer* the rest. The Jawa read
the eclipse, the trader and the short circuit as the gods, and nothing in the game contradicts
them.

**Size.** Per god band, applied as a multiplier on each listed incident's chance: Exalted ×1.35,
Content ×1.15, Neutral ×1, Slighted ×0.85, Wrathful ×0.7. Where the row says the reverse, the
factor is inverted. The tilts are subtle enough that no single event proves anything; over a
campaign the pattern is felt.

**The first table.** Every incident below is a vanilla `IncidentDef`, VERIFIED with RimSage in
`Defs/Core/Storyteller/` (Incidents_Map_Misc, Incidents_Map_Special, Incidents_World_Conditions,
Incidents_Map_Disease, Incidents_Map_Threats). Each god's row comes from his canon pleasures in
`divine_satiation_engine.md` §2.0b and §8b.

| God | When he is pleased, more often | And less often | Canon root |
|---|---|---|---|
| Ishko | `Eclipse`; sandstorm and fog weather; `SelfTame` | — | eclipse and sandstorm ↑Ishko (§8b.B); the patience to tame |
| Ohm | `ShipChunkDrop` (machine wreckage falls) | `ShortCircuit` | the living machine; breakdowns ↓Ohm |
| Oomo | `FarmAnimalsWanderIn` | `Disease_Flu` | a slighted Oomo *"lets sickness in"* (§8b.B) |
| Mob'Unloo | `TraderCaravanArrival`, `OrbitalTraderArrival` | — | the deal and the counter-gift |
| Rekko | `ResourcePodCrash` (salvage from the sky) | — | the second hand; things found |
| Ta'Baa | `TravelerGroup`, `HerdMigration` | — | the road, things on the move |
| Zizzik | `Flashstorm`, `SolarFlare` (small sparks, scattered) | `Infestation` | a fed Zizzik keeps his wakes small (§⑦); the starved slumber bank is unchanged |
| Sh'kaar | `HeatWave` | `Eclipse` | the one unsetting sun; an eclipse is his hiding |
| Ozzik | `VisitorGroup` (renown draws visitors) | — | pride is seen; *"a raid that arrives because you grew loud is Ozzik's bill"* stays a later step |

Nine gods and about fifteen tilts in all. **Not in the first pass:** raids and threat points (too
coarse to stay subtle), quests, and the M and L boons. Those are later steps once this one is
felt in play.

**What the Jawa have instead of evidence.** Their own rites and devotions, the Narrator's landing
report of standings, and the world itself. Question Q3 asks whether there should also be a rare
aside: one unattributed line in a vanilla letter, for example *"Some of the clan made Ishko's
sign."*


### 5. What Ninefold needs

All small, and all behind Mod Settings (a master toggle and a strength slider, per the every-mod
settings rule).

- **A def type for tilts** (XML, data not code): `RM_GodFavourTiltDef { god, incident or weather,
  direction }`. The table in §4 becomes about fifteen of these, and BENCH can tune them without C#.
- **The incident hook:** a Harmony postfix on `StorytellerComp.IncidentChanceFinal(IncidentDef,
  IIncidentTarget)`. VERIFIED: it exists, is `protected`, and multiplies `BaseChanceThisGame` by
  the population factors and `ChanceFactorNow` before returning. The postfix multiplies the result
  by the tilt for that def, read from `GameComponent_Ninefold.GetBand(god)` (built).
- **The weather hook:** a postfix on `WeatherDecider.CurrentWeatherCommonality(WeatherDef)`.
  VERIFIED: it exists, and it is `private`, so it is patched by name.
- **The offerings:** two calls to the existing `ApplyDelta`, one per god, from the Nine Faults
  outcome worker (`RitualOutcomeEffectWorker_FromQuality.ApplyExtraOutcome`, VERIFIED) and from a
  prefix on `GravshipUtility.AbandonMap` (VERIFIED) for the Left Behind.
- **The "fresh find" mark:** a small Scribed comp or map-component set, written when the clan
  takes a machine and cleared on first use or at departure. UNVERIFIED: the cleanest seams for
  "taken" (claim, uninstall, haul) and "first use" (power on, first job at a bench).
- **Nothing new is Scribed in Ninefold** beyond what it already saves. The tilts read live bands.
- **Owed alongside, and small:** a Ninefold hook on `CompBreakdownable.DoBreakdown` so ordinary
  breakdowns move Zizzik and Ohm as §8b.B designs. It is not needed for either offering.


### 6. Questions for the owner

**Q1. Who loses favour when Nine Faults breaks a fresh find, and is it the same thing as the Gift of
Working Things?** The proposal is that breaking a machine the clan has just found takes favour from
Rekko and gives it to Zizzik. Rekko is the god of restoring things, and a find is his by nature:
the machine he would have woken. The other option is the machine's own god by kind: Ohm for a
generator, Oomo for a water machine, and so on. Separately, an older devotion, the Gift of Working
Things, already has the clan destroy one of its own working machines for Zizzik. Should that stay
as a separate act (your own machine) beside Nine Faults (a fresh find), or be folded into Nine
Faults?

**Q2. When a working machine is left behind for Ta'Baa, who should lose?** The Left Behind is the
existing Ta'Baa devotion: at launch the clan leaves one valuable thing behind, forever. The
proposal narrows it to working machines and makes it a transfer. Ta'Baa gains, and the god whose
work the machine did loses: Ohm for a generator, Oomo for a water machine, Mob'Unloo for a comms
console. Is that right, or should leaving things behind only please Ta'Baa and cost no other god?

**Q3. Should the gods leave any sign at all?** Favour will only tilt the odds. More traders when
Mob'Unloo is pleased, fewer short circuits when Ohm is, more eclipses when Ishko is, and so on, at
most a third more or less often. Nothing in the game would say a god did it. The question is
whether that is enough, or whether the Narrator should very occasionally add one line to an
ordinary letter, unattributed, such as *"Some of the clan made Ishko's sign."* That would be the
nearest thing to evidence the Jawa ever get.


---

# Round 1 (background; round 1's forks and rounds 2 and 3's shapes were rejected and removed)

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
