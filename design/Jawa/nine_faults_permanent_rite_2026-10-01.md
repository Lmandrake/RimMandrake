# Nine Faults — the first permanent-choice rite (design exploration, 2026-10-01)

Item: `NINE_FAULTS_PERMANENT_RITE_1`. Status: DRAFT exploration for BENCH; nothing ruled, nothing built.

## Round 3: THE RULED DESIGN (owner, 2026-10-01)

### 1. His rulings

Owner, 2026-10-01, typed (ledger `5f9b8da6a`):

> *"These aren't good. Carrying broken machinery forever is too heavy, the player's choose the next
> landing site not the gods, and you're never allowed to just write off a god as evil"*

> *"It's only ok to leave behind something broken as an offering, and then it is lost forever"*

By card, the same sitting: **build Nine Faults together with real effects for god favour.**
Earlier the same day (ledger `8a6f7bc06`) he ruled that breakdowns are never redirected or soaked
up (*"Too magical"*), and that leaving a thing broken moves favour from one god to another.

**So the ruled shape is:** a broken machine is left behind on a map the clan departs, as an
offering. It is lost forever. That moves favour from one god to another.

**Banned, everywhere in this design:**
- carrying broken machinery along;
- gods choosing or steering where the ship lands, because the player picks the site;
- any framing of a god as an enemy or as evil.

**Rechecked: the "front god" does not choose the site.** In the built code
(`GameComponent_Ninefold.ReckonFrontAtLanding`, called from the landing patch) the front is
reckoned **after** the ship has landed where the player chose, as a judgement of the map just
left. Nothing in Ninefold reads or writes a destination. Round 2's phrase "choose which god runs
the next map" is deleted with round 2. One borderline design text is flagged in §8: Ta'Baa's L
boon *Somewhere Better* reveals a site. The god shows a site and the player still chooses
whether to go.


### 2. The offering

**What can be offered.** A building of the clan's own that is **broken down** at the moment of
departure (vanilla's broken-down state, `CompBreakdownable.BrokenDown`, VERIFIED) and that stands
**on the map, not on the ship**. Anything on the ship's substructure is not left behind, so it
cannot be offered (ruled: nothing broken is carried). Droids are not machines here: a droid is a
person to Ohm, and leaving one behind is a separate matter (it is in Q1).

**How it becomes broken.** Either way works:
- **It broke on its own**, a vanilla breakdown the clan chose not to repair; or
- **The Nine Faults rite.** This is the found rite of the Lantern Deeps, and the only way to offer
  a **working** machine. Worshippers surround it and miswire it, nine faults in sequence, the
  nine bulbs failing one by one, until it breaks down in front of everyone. Poor: it burns, and a
  burned machine is not an offering (the fire is Zizzik's, but nothing moves between gods). Fair
  or better: it stands broken and is **dedicated** as an offering. Good or better also brings the
  participants a "we gave it to him" memory; Excellent also brings an art tale.

**How it is offered at departure.** A designation, *"Leave as offering"*, on any broken building
off the ship. The designation is the clan's word; nothing happens until the ship lifts. **At the
launch**, every designated offering still broken and still on the old map is counted, and the
favour moves then, in one Narrator letter that names each machine and the two gods it set
against each other. The old map is then left as it always is.

**Lost forever.** VERIFIED: on a gravship departure Odyssey's `GravshipUtility.AbandonMap` sends
off every pawn left behind and abandons the map's parent (`Abandon(wasGravshipLaunch: true)`).
So the offering is lost by ordinary means, with nothing magical about it: the clan flew away
from it. UNVERIFIED: whether every departure calls `AbandonMap`, or whether a map can survive
the launch (an outpost left behind). If one can, the offering must never be reclaimed; the
letter says so, and reclaiming it is the one thing the gods would take back.

**Its relation to the Left Behind.** The Left Behind (`devotional_sacrifice_catalog.md`, Ta'Baa) is
an existing devotion: at launch, leave one valuable thing on the old map, named at the launch
rite, *"COST: the thing, forever."* Nine Faults is close kin: same moment, same loss. It differs
in three ways. It is a **broken machine**, not any valuable thing. It **moves** favour between
two gods instead of feeding one. And it has a found rite for breaking a good machine on purpose.
Whether the two stay separate or merge is Q1.


### 3. Which gods a machine sets against each other

**Fixed by what the machine is**, so the player chooses *which machine to give up* and thereby
which pair moves. Every pairing is drawn from god canon (`divine_satiation_engine.md` §2.0b,
§2.0c skill grid, §8b). The **keeper** is the god whose work the machine did. He loses favour,
because his thing was given away broken instead of mended. The **receiver** is the god to whom
leaving it unmended is an honour.

| Machine left as an offering | Keeper (favour taken) | Receiver (favour given) | Canon basis |
|---|---|---|---|
| Power: generator, battery, conduit plant | Ohm | Zizzik | §8b.B *"a machine … breaks down → ▲Zizzik, ↓Ohm"*; Zizzik's S demand, *"one breakdown left unfixed"* |
| Droid support: charger, droid workbench | Ohm | Zizzik | Ohm *"wants his droid servants back"* |
| Water: vaporator, filter, purifier | Oomo | Zizzik | Oomo, the body's waters |
| Kitchen and food: stove, nutrient dispenser, freezer | Oomo | Zizzik | Cooking is Oomo's (§2.0c) |
| Comms: comms console, trade beacon | Mob'Unloo | Ishko | the deal is Mob'Unloo's; a silent clan is Ishko's (*"no comms"*) |
| Lights: lamps, sun lamps, floodlights | Ohm | Ishko | the dark is Ishko's |
| Workbenches that make from salvage | Rekko | Zizzik | Crafting from salvage is Rekko's (§2.0c) |
| Research and fine work: research bench, art bench, high-tech fabrication | Ozzik | Zizzik | Intellectual, Artistic and high-tech building are Ozzik's (§2.0c) |
| Defences: turrets, traps with machinery | Ishko | Zizzik | the turtle that outlasts is Ishko's (attrition defence) |

**Size of the transfer:** scaled by the machine's market value, from Small (3) to Large (15)
(`EventMagnitude`), taken from the keeper and given to the receiver in equal measure. A cheap
lamp moves little; a fusion generator moves a lot. **No machine sets a god against himself, and
none frames a god as an enemy.** The keeper is not punished as a villain; he grieves a thing
given away.


### 4. Why losing the machine is the consequence

- **It is real capital, gone.** Components and advanced components are scarce for a scavenger
  clan. A generator left behind is one the next map does not have until it is rebuilt from
  salvage.
- **It is paid once, not carried.** The weight he called *"too heavy"* in round 2 was a cost
  borne forever. This one is paid in full at the moment of leaving, and the clan flies on lighter.
- **The choice is which god.** A clan that wants Ishko's favour leaves the comms console; one that
  wants Zizzik's leaves a generator. Each choice costs a specific god, and the player can read on
  the table above which one.
- **It is permanent by nature, not by rule.** The machine stays on a map nobody returns to, and
  the favour it moved stays moved. Nothing refunds it. Later deeds can move those gods again;
  the offering itself is final.
- **It only matters if favour matters.** That is why it is built together with §5.


### 5. What god favour does in play (first proposal, built together with Nine Faults)

**Principle: favour works through the clan's belief, never through physics.** The canon already
says it: each god *"is a belief that shapes behavior"* (§2.0b). So a god's standing changes how
the Jawa **work** at that god's craft, and how they **feel**. Nothing in the world changes because
a god willed it, and no god chooses where the ship goes.

**One line per god, read from his band.** Content gives a small lift, Exalted a larger one,
Slighted a small drag, Wrathful a larger one, and Neutral nothing. The magnitudes are a first
pass: ±10% for Content and Slighted, ±20% for Exalted and Wrathful.

| God | What his standing changes (the clan's heart in his work) | Canon root |
|---|---|---|
| Ishko | construction speed of walls and doors; taming | §2.0c Construction (doors to outlast), Animals |
| Ohm | research speed; machine and droid work | §2.0c Intellectual; S boon *Steady Current* |
| Oomo | cooking speed; tending the sick | §2.0c Cooking, Medical |
| Mob'Unloo | trade prices, a small step either way | S boon *Thumb on the Scale* |
| Rekko | repair speed; crafting from salvage | S boon *Second Wind* |
| Ta'Baa | walking and caravan speed | S boon *Tailwind* |
| Zizzik | inspiration chance (Content and Exalted only); Slighted and Wrathful bank his wake as already designed | S boon *Creative Sparks*; §⑦ |
| Sh'kaar | shooting and melee accuracy in the open, a small step | §2.0c Shooting and Melee (open fight); S boon *Keen Edge* |
| Ozzik | art speed; quality chance on fine work | S boon *Craftsman's Pride* |

**How it reads:**
- each affected stat's tooltip names the god and his band, for example *"Ohm is Content: +10%"*;
- **one mood thought**, only for the most pleased and the most aggrieved god of the moment
  (for example, *"Rekko is pleased with us"*), so the needs tab carries two lines, never nine;
- the Narrator's letter at each landing reports the standings (the existing front reckoning
  reused as a report, not a steer).

**Why this is small enough.** It is one `StatPart` that reads Ninefold's band, nine table rows,
one ThoughtDef pair and one letter. It needs no new god behaviour, no events and no dispensation
system. The larger designs (boons M and L, demands, the front's actuators) stay where they are,
for later.

**What it does to Nine Faults.** An offering now has a visible price and payoff. Leaving the
generator moves Ohm from Content to Neutral, so research loses its +10%; Zizzik reaches Content,
so inspirations come more often. The player can see the trade before launching.


### 6. Engine route

- **The broken-down test:** VERIFIED `CompBreakdownable.BrokenDown` (`=> brokenDownInt`), set by
  `DoBreakdown()`.
- **The designation:** a `Designator` limited to the clan's buildings whose `BrokenDown` is true
  and which are not on the gravship's substructure (UNVERIFIED: the cleanest substructure test).
- **The moment of departure:** a prefix on `GravshipUtility.AbandonMap(Map)` (VERIFIED to exist,
  Odyssey) counts the map's designated offerings before the map goes, then calls Ninefold
  `ApplyDelta` twice per offering (keeper −, receiver +) and sends the letter. Ninefold already
  patches the launch (`Patch_GravshipLaunched`); UNVERIFIED which of the two seams fires on every
  departure.
- **The rite:** `PreceptDef`, `RitualPatternDef` and a `RitualOutcomeEffectWorker_FromQuality`
  subclass in `mandrake.rut.rites`. Its `ApplyExtraOutcome` (VERIFIED to exist and to be called
  from `Apply`) calls `DoBreakdown()` on the target and sets the offering designation.
- **Favour effects:** one `StatPart` reading `GameComponent_Ninefold.GetBand(god)` (built), applied
  to the stats in §5, plus a ThoughtDef pair. No Scribed state is needed beyond what Ninefold
  already saves.
- **Still missing, and small:** a Ninefold hook on `CompBreakdownable.DoBreakdown` so ordinary
  breakdowns move gods as §8b.B designs. It is not needed for offerings.


### 7. Questions for the owner

**Q1. How should the offering be made, and is it the same thing as "the Left Behind"?** The
proposal has two routes. Any machine that has broken down can be marked *"Leave as offering"*,
and the favour moves when the ship lifts off. The Nine Faults rite is the way to give up a
**working** machine: the clan breaks it on purpose, in front of everyone, and that dedicates it.
There is already a Ta'Baa devotion called the Left Behind, in which the clan leaves one valuable
thing behind at launch, forever, to please Ta'Baa. Should Nine Faults (a broken machine, moving
favour from one god to another) stay a separate thing from the Left Behind (any valuable thing,
pleasing Ta'Baa), or should they become one launch-time offering? And may a broken **droid** be
left as an offering, or is a droid a person to Ohm and never offered?

**Q2. Is "favour shows in the work" the right first effect?** Today, in the code, a god's favour
changes almost nothing. The proposal is that each god's standing nudges the clan's work at his
craft, because the Jawa believe in him: research for Ohm, cooking and nursing for Oomo, repair for
Rekko, trade prices for Mob'Unloo, travel speed for Ta'Baa, and so on. It is +10% or +20% when he
is pleased and the same amount down when he is aggrieved, shown in the tooltip, plus one mood line
for the most pleased god and one for the most aggrieved. Nothing magical happens in the world,
and no god chooses where the ship goes. Is that the right size and kind, or should favour act on
something else first?

**Q3. What should be done about the word "evil" in the pantheon?** You ruled that a god is never
written off as evil. The pantheon of record (locked 2026-08-08) calls Sh'kaar *"the evil sun … an
EVIL god"*, and several docs call Sh'kaar and Zizzik *"the two evil gods"*. One rite kind is even
defined as *"deny an evil god what feeds him"*. The game code carries the same label. Does your
ruling mean the word comes out everywhere, so that they become dangerous, hungry gods but never
evil? Or does it only mean that a player can never turn a god into a permanent enemy, with the
canon wording standing? §8 lists every place it appears.


### 8. Flags for BENCH (other docs; not edited)

**A god framed as evil or as an enemy** (measured with `git grep` on origin/main, 2026-10-01;
counts are matching lines per file):

| File | Lines | What it says |
|---|---|---|
| `design/Jawa/divine_satiation_engine.md` | 9 | Sh'kaar *"EVIL god"*, *"the evil sun"*; *"the two evil gods"* (Zizzik, Sh'kaar); §⑧ heading *"(EVIL; the escalation meter)"* |
| `design/Jawa/salvation_rites_2026-10-01.md` | 3 | the kind **starving** defined as *"deny an evil god what feeds him"*; §c3 *"starving the evil god"* |
| `design/Jawa/narrator_corpus/narrator_frame.md` | 3 | *"No mercy-softening of the evil gods"*; *"a gift from an evil god"* |
| `design/Jawa/god_intercession_spec.md` | 2 | *"The evil gods are targets, never shields"* |
| `design/Jawa/proposals/god_modes_deep_design.md` | 2 | *"The evil gods (Zizzik, Sh'kaar) INVERT the law"* |
| `design/Jawa/worldbuilding/biomes/longshade_bedazzle_review_2026-09-29.md` | 3 | *"an evil sun god, Sh'kaar"* |
| `design/Jawa/biome_rites_pass_2026-10-01.md` | 1 | *"never fed outright, as an evil god should be"* (§12 tally) |
| `design/Jawa/first_contact_chains.md` | 1 | *"The two evil gods and the trap arrive LAST"* |
| `design/Jawa/divine_dilemma_events.md` | 1 | the notation *"▲ = an evil god fed"* |
| `design/Jawa/salvation_engine_build_spec.md` | 1 | *"evil gods front only via their own meters"* |
| `design/Jawa/art/gods/god_render_prompt_spec.md` | 1 | Sh'kaar *"evil light … cruel, malevolent"* |
| `design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md`, `blackcrags_bedazzle_review_2026-09-30.md` | 1 each | evil-god wording |
| `design/RimMandrake/ancient_machines_design.md`, `statue_mods_spec.md`, `statue_expansion_assessment.md`, `atmospheric_base_scheme_catalog.md` | 1 each | *"both evil gods"*, Sh'kaar *"reads evil"* |
| `infrastructure/state/items/SALVATION_RITES_UNIFICATION_1.md`, `SUMP_GASLIGHT_1.md` (and closed `SUMP_UTINNI_LAYER_1.md`, 3) | 1 each | *"starving the evil god"*, the canon quote |
| `src/RimMandrake/Ninefold/Source/God.cs`, `Patch_FireStarted.cs` | 1 each | code comments: *"evil sun, exposure (EVIL god)"* |

Q3 decides what happens to all of these. The pantheon canon is the root; everything else
inherits from it.

**Gods choosing or steering landing sites:** **none found.** Searched for god, front, Narrator
or Ta'Baa near choose, pick, steer, decide or site. The nearest is **Ta'Baa's L boon *Somewhere
Better*** (`divine_satiation_engine.md` §⑥; `narrator_corpus/triad_path.md` §L;
`first_contact_chains.md` Ta'Baa DELIGHT; `proposals/god_modes_deep_design.md` ⑥-P *"multiple
'somewhere better' sites revealed in sequence"*). The god **reveals** a site and the player
decides. That is within the ruling as written; BENCH may want to confirm.

**Redirect or soak of breakdowns (ruled out 2026-10-01):** Zizzik's decoy heap
(`design/Jawa/folk_gesture_mechanics.md` §1); the Kept Mistake's Fair and Good outcomes
(`design/Jawa/biome_rites_pass_2026-10-01.md` §1.3).


---

# Round 1 (background; its forks and round 2's shapes were rejected and removed)

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
