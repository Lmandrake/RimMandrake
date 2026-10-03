# Salvation rites — unification audit and build plan (2026-10-02)

_BENCH audit for `SALVATION_RITES_UNIFICATION_1`. Audit and plan only: nothing filed, nothing built.
Register audited: `design/Jawa/salvation_rites_2026-10-01.md` §(b) as of `48de81477`. The owner accepted
every pitched rite on 2026-10-02 (typed: *"Accept all rites for now."*) and asked, 2026-10-01 (typed):
*"Rites are allowed everywhere. I may not have liked the rites. Please explain them to me again."*
§1 is that explanation. `SALVATION_RITES_RENORMALIZE_PASS_1` (gods, kinds, outcomes) is not done here._

## 1. What a rite is (for the owner)

**A rite is a ceremony the clan holds to deal with one of its nine gods.** In game it is an ordinary
RimWorld ritual: you pick a spot, choose an organiser and attendees, they gather and act it out for an
hour or two, and it ends with a quality (poor to excellent) and an outcome. What makes ours different is
what the outcome does: it moves one god's mood on the Ninefold engine (the gods' hidden "how satisfied
am I" numbers), and the gods then decide whether to answer with events, weather and luck. The player
never sees a number; they see the world lean.

**How a player meets one.** Three ways:
- **Given:** the Salvation ideoligion starts with its rites (funeral, feasts, the scrap jubilee).
- **Revealed:** the Rites research tab (*"revealed, not bought"*) opens rows as the clan learns old
  lore (Antiquities stages).
- **Found:** most new rites are discovered in a biome. A pawn studies an inscription at a place that
  explains the rite (a meter torn off its post, a droid with nine wires crossed). The study gives a
  rubbing; reading the rubbing on the Rites tab teaches the rite to the colony, and from then on it can
  be held **anywhere** its condition is met (ruled: rites allowed in every biome). Each found rite has
  one condition: darkness, a storm, a crater, a found machine, a dying man's ledger.

**The nine gods, one line each** (`divine_satiation_engine.md` §2.0b):

| God | Is the god of |
|---|---|
| Ishko the Unmaskable | stillness, hiding, the prepared dark, the grave |
| Ohm the All-Current | the living machine: power, droids, running engines |
| Oomo the Unspilled | shared water and the family: thirst, kin, food, increase |
| Mob'Unloo the Ever-Owed | the ledger: debt, trade, fair exchange |
| Rekko of the Second Hand | salvage, repair, the discarded woken again |
| Ta'Baa the Unrooted | flight, leaving, never putting down roots |
| Zizzik the Spark-Maker | malfunction, bad luck, the trickster (Ohm's mirror) |
| Sh'kaar the All-Searing | the killing sun, exposure, time; dangerous and hungry, never evil |
| Ozzik the Shamed | ambition and pride, and the grief under them; feeds Sh'kaar and Zizzik |

**The kinds of appeasement, one line each:**

| Kind | What the rite does to the god |
|---|---|
| feeding | gives the god what it wants, raising its satisfaction |
| settlement | balances the god's ledger: a debt named and paid, a bank spent |
| starving | denies a hungry god what feeds it (only Sh'kaar and Zizzik are treated this way) |
| venting | bleeds off a dangerous build-up safely (Ozzik's pride, Sh'kaar's war-heat) |
| warding | keeps a god's attention pointed away for a while |
| consolation | lays grief down, so the god stops dwelling on a loss |
| invitation | calls all nine at once to speak (the array, the hull liturgy, the feast) |

## 2. Reconciliation table

**Method.** Every `.xml`/`.cs` under `src/` was searched for `PreceptDef`, `RitualPatternDef`,
`RitualBehaviorDef`, `RitualOutcomeEffectDef`, ritual workers, `LordJob_Ritual`, `ResearchMod`
subclasses, `CompStudiable`, and every register rite's name (CamelCase and spaced). Descriptions of the
hits were read.

**What exists in `src/` (the whole list):**

| Built thing | Where | What it is |
|---|---|---|
| 5 `ResearchProjectDef`s + tab | `src/RimUtinni/Rites/Defs/RUT_Rites_Research.xml` (`mandrake.rut.rites`, "Salvation Rites") | the B1 liturgy rows; research only, no ritual, no C#, no assembly |
| `RM_Ishko_RitualOutcome_PlaceSacredMark` + worker | `src/RimMandrake/SacredGraffiti/Defs/RitualOutcomeEffects.xml`, `Source/SacredGraffiti.cs` | outcome effect for the Dark Vigil; **no caller anywhere**; names a god inside an RM mod (tier violation the register already flags) |
| The Return (Sun-Debt) | `src/RimUtinni/UtinniPatches/Defs/PreceptDefs/RUT_TheReturn.xml` + `src/RimMandrake/Stillsand/Source/RM_WaterLedger.cs` | full ritual: precept, pattern, behavior, target filter, outcome worker; **another faith's** rite |
| Revering the Holy Flame | `src/RimUtinni/UtinniPatches/Defs/PreceptDefs/RUT_HolyFlamePrecepts.xml` + `Patches/HolyFlame_RitualistWiring.xml` | precept for any Ritualist ideo; not a Salvation rite |
| Deep tribes' fire rite | `src/RimUtinni/PyrelandsMechanics/Source/LordJob_RUT_FireRite.cs`, `PyrelandsFireRite.cs` | an incident-driven LordJob, not a ritual precept; another faith's |
| Ninefold `ApplyDelta(God, float, reason)` | `src/RimMandrake/Ninefold/Source/GameComponent_Ninefold.cs:257` | the call every rite outcome will make; built |
| The Salvation's 23 rituals | `src/Jawa/ideoligion/The Salvation.rid` | in the ideoligion file, donor/vanilla workers |

`mandrake.rut.aftermath` (`src/RimUtinni/AftermathRites/`) is **not** rites despite the folder name: it
is eight `RM_AftermathRuleDef` data rows for the Aftermath plot engine. A name trap, nothing more.

**Salvation ritual rites built: 0.** Of 42 found rites (counted below), **0 built**, 14 have a build
item (all `proposed`, none claimed), 28 have none.

### 2a. Every register row

Status column = register status. "Item" = a filed build item. All "Built?" answers are **no** unless
stated.

**B1 Liturgy tab** (all five BUILT as research only; no ritual behind any)

| Rite | God | Kind | Built? | Gap |
|---|---|---|---|---|
| The Scrap Shrine | Rekko | feeding | research row only | no ritual, no outcome |
| Conduit Choir | Ohm | feeding | research row only | same |
| God-Speaker Array | all nine | invitation | research row only | same; needs the array building |
| Liturgy of the Hull | all nine | invitation | research row only | same |
| The Gods Speak Back | all nine | Council of Voices | research row only | needs the RimAI/Cradle-Mind voice layer (§5c) |

**B2 Abyss found rites** (SPECCED; no item)

| Rite | God | Kind | Condition | Built? | Gap |
|---|---|---|---|---|---|
| The Dark Vigil | Ishko | feeding | absolute darkness | no (its outcome effect exists, uncalled) | darkness gate, discovery chain, item |
| The Blind Offering | Mob'Unloo | settlement | absolute darkness | no | same + overnight item-vanish worker |
| The Snuffing | Sh'kaar | starving | makes the dark | no | same + light-extinguish behaviour |
| The Lightless Burial | Ozzik (interim) | consolation | absolute darkness | no | funeral variant; renormalize pending |
| The Unlit Wedding | Oomo, Ishko | variant | absolute darkness | no | wedding variant, not counted |

**B3 the `.rid`'s 23 rituals** (IN .RID): exist and work through donor/vanilla workers. God, kind and
condition unmapped for all 23. Gap: the mapping is `SALVATION_RITES_RENORMALIZE_PASS_1` work.

**B4 pantheon-design rites** (prose specs; none built, none has an item)

| Rite | God | Kind | Condition | Gap |
|---|---|---|---|---|
| The Reckoning (launch-rite) | Ta'Baa | feeding | a launch | no spec beyond prose; Ninefold already patches launch |
| Machine-funeral | Ohm | feeding | a machine's end | prose only |
| The Seating | Rekko | feeding | a seated relic | specced in `ancient_machines_design.md` §5.2 |
| The Unburdening | Ozzik | venting | wealth destroyed | specced (F13) |
| Controlled waking / Calling-Pyre | Zizzik | settlement | a chosen moment | specced; counted in Zizzik's cap |
| Nine-Course Ninefold Feast | all nine | invitation | a feast | accepted 2026-10-02 |
| Triggered rites (6 occasions) | all nine | invitation | the event | prose only |

**B5 devotions** (28 acts, SPECCED in `devotional_sacrifice_catalog.md`; acts a rite may frame, not
ritual precepts). None built. By god: Zizzik 4 (incl. Nine Faults), Ishko 3, Ohm 3, Oomo 3, Mob'Unloo 3,
Rekko 3, Ta'Baa 3, Sh'kaar 3, Ozzik 3 (incl. the Unburdening). Gap: none owed until a rite frames one.

**B6 biome-pitched, mostly other faiths**

| Rite | God / faith | Built? | Note |
|---|---|---|---|
| The Return | Sun-Debt | **yes** (see above) | other faith; stays in UtinniPatches |
| Deep tribes' fire rite | deep tribes | **yes** (LordJob) | other faith |
| Revering the Holy Flame | Sh'kaar, any Ritualist | **yes** (precept) | other faith |
| The Rite of Tipping | unassigned | no | accepted 2026-10-02; **only a name** in the Warscar review list, no description, no god, no faith (Q3) |
| The Watch | — | — | RULED OUT |
| Pilgrim camps | — | — | lore ladder, not a rite |
| The pool rites | → B15 Refused Toll | — | resolved |
| Offering and forgetting | Deep Desert Tribes | no | DRAFT, other faith |

**B7 to B17: the found rites** (all no; "Item" is the filed build)

| Rite | God | Kind | Home | Item | Gap |
|---|---|---|---|---|---|
| The Sunning | Oomo | feeding | Contagion | none | condition: a Burn active |
| The Unfinished Laid Down | Rekko | consolation | Contagion | none | target: an Unfinished at the burn line |
| The Kept Mistake | Zizzik | warding | Contagion | none | offering: a broken thing left |
| The Storm's Receipt | Mob'Unloo | feeding | Wasteland | none | target: storm-exhumation site |
| The Salted Keeping | Ozzik | venting | Wasteland | none | offering: finest thing buried in a crater |
| The Inherited Wreck | Rekko | settlement | Wasteland | none | target: expedition wreck |
| The Returned | Ta'Baa | consolation | Blue Desert | none | target: a body the line gave up |
| The Charged Reed | Ishko | feeding | Blue Desert | none | reworked by card; whistle item scaled by tier |
| The Chime Vigil | Oomo | warding | Cracked Lands | none | window: the chime window |
| The Mud Claim | Rekko | feeding | Cracked Lands | none | window: after a recede |
| The Filtered Cup | Oomo | consolation | Cauldron | none | target: a filter converter's first water |
| The Engine Hour | Ohm | feeding | Cauldron | none | window: ground loud, no bloom |
| The Capping | Zizzik | starving | Cauldron | none | target: an uncapped vent, no flame |
| The Anvil Gift | Sh'kaar | venting | Forge | none | offering: a weapon into lava |
| The Flawed Masterwork | Ozzik | feeding | Forge | `FLAWED_MASTERWORK_ENGINE_CHECK_1` (check, not build) | engine check first |
| The Stall-Hold | Ishko | feeding | Leaning Scrub | none | window: a Stall |
| The Shade Tithe | Sh'kaar | warding | Long Shade | none | window: golden hour, new roof |
| The Shadow Walk | Ta'Baa | feeding | Long Shade | none | window: a gloomcast |
| The Last Track | Ohm | consolation | Stillsand | none | target: a dead crawler |
| The Unspilled March | Oomo | feeding | Stillsand | none | window: a mirage |
| The Deserter's Welcome | Ohm | feeding | Warscar | none | window: hospice waking day 7+ |
| The Vindication Walk | Ta'Baa | consolation | Warscar | none | window: a Settling |
| The Cold Ledger | Mob'Unloo | consolation | Nightside Ice | none | target: a calved ledger tablet |
| Zizzik's Nine Faults | Zizzik (Rekko pays) | feeding | Lantern Deeps | `NINEFOLD_FAVOUR_ODDS_BUILD_1` | also builds the favour-odds def type |
| The Answering | Ohm | settlement | Lantern Deeps | `LANTERNDEEPS_ANSWERING_RITE_BUILD_1` | |
| The Struck Glass | Zizzik | feeding | Pyrelands | `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` | |
| The Felled Noon | Sh'kaar | feeding | Webwork | `WEBWORK_FELLED_NOON_RITE_1` | |
| The Ceded Room | Ozzik | venting | Greentide | `GREENTIDE_CEDED_ROOM_RITE_1` | |
| The Open Boast | Ozzik | feeding | Warscar | `WARSCAR_OPEN_BOAST_RITE_1` | |
| The Mending Weld | Rekko | feeding | Rust Cathedral | `RUSTCATHEDRAL_MENDING_WELD_RITE_1` | |
| The Stranger's Overhaul | Ohm | feeding | Rust Cathedral | `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` | |
| The Unjoining | Ta'Baa | feeding | the Rot | `ROT_UNJOINING_RITE_1` | |
| The Sinking | Ishko | warding | the Sump | `SUMP_SINKING_RITE_BUILD_1` | |
| Mob'Unloo's Price | Mob'Unloo | venting | the Sump | `SUMP_EFFIGY_RITE_BUILD_1` | |
| The Refused Toll | Mob'Unloo | feeding | Weeping Stones | `WEEPINGSTONES_REFUSED_TOLL_RITE_1` | needs a metering-station site |
| The Joining Water | Oomo | unruled | Gelatinous Slime | `GELATINOUSSLIME_JOINING_WATER_RITE_1` (needs owner) | kind unruled; site undrafted |
| The Recall of the Written-Off | Rekko | unruled | the Miasma | `MIASMA_RECALL_WRITTEN_OFF_RITE_1` | kind unruled |

**Does the built state match the register?** Yes where it can be checked: every row the register calls
BUILT is built (B1 as research, B6's three other-faith rites), and nothing it calls SPECCED or RULED is
secretly built. The unification criterion *"No Salvation rite def lives outside `mandrake.rut.rites`"* is
met only vacuously (there are none) except `RM_Ishko_RitualOutcome_PlaceSacredMark`, still in
SacredGraffiti.

### 2b. Register defects found (text, not judgement)

1. **B13** calls the Shadow Walk and the Vindication Walk "pitched"; both are accepted (B7 rows).
2. **B15** says *"Oomo keeps his one slot"*; B16 put Oomo at five.
3. **B7's heading** says "other ten biomes, accepted 2026-10-02", but the Cold Ledger row is Nightside Ice,
   ruled 2026-10-01 by card (an eleventh biome).
4. **The cap count is inconsistent.** Zizzik's five includes the controlled waking, a **B4** pantheon rite;
   Rekko's count explicitly excludes the Seating, also B4, *"as at every earlier count"*. See §3 and Q1.
5. The register's kinds list omits **invitation** and the B16/B17 "unruled" rows; §1 above adds invitation.

## 3. Rites per god vs cap

Cap: **five found rites per god** (card 2026-10-02 09:23). Counted from B2, B7 to B17, plus the controlled
waking because the register counts it for Zizzik. The Unlit Wedding (variant) is not counted.

| God | Found rites | Count | vs cap |
|---|---|---|---|
| Ishko | Dark Vigil, Charged Reed, Stall-Hold, Sinking | 4 | one under |
| Ohm | Engine Hour, Last Track, Deserter's Welcome, Answering, Stranger's Overhaul | 5 | at cap |
| Oomo | Sunning, Chime Vigil, Filtered Cup, Unspilled March, Joining Water | 5 | at cap |
| Mob'Unloo | Blind Offering, Storm's Receipt, Cold Ledger, Mob'Unloo's Price, Refused Toll | 5 | at cap |
| Rekko | Unfinished Laid Down, Inherited Wreck, Mud Claim, Mending Weld, Recall | 5 | at cap |
| Ta'Baa | Returned, Shadow Walk, Vindication Walk, Unjoining | 4 | one under |
| Zizzik | controlled waking (B4), Kept Mistake, Capping, Nine Faults, Struck Glass | 5 | at cap |
| Sh'kaar | Snuffing, Anvil Gift, Shade Tithe, Felled Noon | 4 | one under |
| Ozzik | Lightless Burial, Salted Keeping, Flawed Masterwork, Ceded Room, Open Boast | 5 | at cap |
| **Total** | | **42** | |

**No god is over cap from the accept-all**: the register had already counted every B7 row as if accepted.
Six gods are at cap; Ishko, Ta'Baa and Sh'kaar have one slot each.

**But the count depends on the rule in defect 4.** Counted consistently:
- **Found rites only** (drop the controlled waking): Zizzik 4. Nobody over.
- **Every named Salvation rite incl. B4**: Rekko 6 (+Seating), Ohm 6 (+machine-funeral), Ozzik 6
  (+Unburdening), Ta'Baa 5 (+Reckoning), Zizzik 5. **Three gods over.** That is Q1.

The Rite of Tipping (accepted, no god) can only land on Ishko, Ta'Baa or Sh'kaar without breaking the cap
(Q3).

## 4. Build plan for FOUNDRY

**Principle:** every rite's gods, kinds and deltas live in **XML on the rite's def** (a `DefModExtension`
listing god → delta → reason), never in C#. Then `SALVATION_RITES_RENORMALIZE_PASS_1` is a data edit and
does not block building. All C# goes in a new assembly in `mandrake.rut.rites`
(`RimMandrake.Utinni.Rites`); the mod has none today. Mod Settings: one toggle per rite plus each wave's
tuning, per the standing rule.

**Wave 0: shared machinery (blocks everything).**
1. **Spike, before any other code:** read `Ideo.AddPrecept(..., fillWith)` in RimSage and prove on a
   quicktest that a runtime-added ritual precept gets its obligations and name. Register marks this
   UNMEASURED; the fallback is all found rites shipped in the `.rid` with a "not yet learned"
   `BlockingIssues` comp. The answer decides the shape of item 3.
2. **Rite condition framework:** `RUT_RitualConditionDef` + worker (*holds? how deeply 0..1?*), a
   `RitualOutcomeComp` that blocks start with a reason line, a quality comp scaled by depth, a mid-rite
   watcher (every 250 ticks; on break the rite fails and the condition's named god answers). Build it
   general, not darkness-only: conditions are a **game condition active** (storm, Burn, Stall, gloomcast,
   Settling), a **time window** (golden hour, highest sun, chime window), a **place** (crater, lava, vent),
   a **target thing** (a wreck, a dead crawler, a machine never run), or **darkness**.
3. **Discovery chain:** a base inscription `ThingDef` with `CompStudiable`; a "found rites" row on the
   Rites tab (techprint count 1, commonality 0, LoreStages placeholder text); `RUT_ResearchMod_GrantRite`;
   the discovery letter.
4. **Outcome base:** a `RitualOutcomeEffectWorker` subclass that reads the god-delta extension and calls
   `ApplyDelta` per god per quality band, plus memory/tale hooks.
5. **Move** `RM_Ishko_RitualOutcome_PlaceSacredMark` and its worker into `mandrake.rut.rites`.

**Wave 1: darkness (needs W0; soft-depends `ABYSS_DARK_BUILD_1`).** Dark Vigil, Blind Offering, Snuffing,
Lightless Burial, Unlit Wedding variant. One new item; the register's §(c) is the spec.

**Wave 2: window rites (a condition is active; the rite is the gathering).** Sunning, Stall-Hold, Shadow
Walk, Vindication Walk, Chime Vigil, Unspilled March, Shade Tithe, Engine Hour, Mud Claim, Deserter's
Welcome, Struck Glass (+ its lightning strike), Felled Noon (+ the tree felled). Mostly XML once W0 exists;
each needs its biome's condition def to exist and be readable.

**Wave 3: offering rites (something is given up, buried or broken).** Salted Keeping, Anvil Gift, Kept
Mistake, Capping, Sinking, Mob'Unloo's Price, Ceded Room, Charged Reed, and Nine Faults (already inside
`NINEFOLD_FAVOUR_ODDS_BUILD_1`, which also builds the favour-odds def type that several outcomes here
want; build that first in the wave). Shared piece: an "offering consumed" behaviour stage and a
value-scaled delta.

**Wave 4: target rites (held at a specific found thing).** Unfinished Laid Down, Inherited Wreck,
Returned, Last Track, Storm's Receipt, Cold Ledger, Filtered Cup, Answering, Mending Weld, Stranger's
Overhaul (adds a mid-rite capture/release choice with faction effects). Shared piece: a target filter
keyed on a thing tag or comp.

**Wave 5: bespoke (each needs its own C# or world content).** Joining Water (hediff spread; needs owner
on kind), Unjoining (symbiont purge, launch-window follow-up), Recall of the Written-Off (a salvage-raid
event), Open Boast (delayed challenge, once per colony), Refused Toll (needs the metering-station site),
Flawed Masterwork (after its engine check), the controlled waking.

**Not in this plan:** B4 pantheon rites, triggered rites and the Feast (prose-only; spec first), the
`.rid`'s 23 (renormalize maps them), B5 devotions (acts, not rites), other faiths' rites (built, staying).

**Item housekeeping FOUNDRY will need:** the 14 existing build items all predate W0; each should
be re-pointed to depend on the W0 item rather than build its own gate/discovery code. 28 found rites
have no item yet; filing one item per wave (not per rite) keeps the queue readable.

## 5. Questions for the owner

**Q1. What counts toward a god's limit of five rites?** Right now the count is inconsistent: Zizzik's
"controlled waking" counts, but Rekko's "Seating" (same kind of rite, from the gods' design rather than a
biome) does not.
- **(a) Only rites found in biomes count.** Zizzik drops to four; nobody is over. Simple; the
  gods'-design rites become extras on top.
- **(b) Every rite counts.** Rekko, Ohm and Ozzik go to six, over the limit; three rites would need to
  move or go. Strictest; most work now.
- **(c) Drop the limit.** Nothing to police; some gods will end up with many more rites than others.

**Q2. Build now, or re-sort the gods first?** You said you may not have liked the rites and want to
revisit which god each serves.
- **(a) Build the shared machinery now, rites after the re-sort.** Nothing built gets redone; rites
  appear later.
- **(b) Build everything now, with each rite's gods kept as editable data.** Rites arrive soonest; the
  re-sort becomes a data edit, but it may still change what a rite feels like.
- **(c) Re-sort first, then build.** Cleanest result; nothing playable for longest.

**Q3. The Rite of Tipping (Wasteland) has only a name.** It was accepted with no description, no god and
no faith.
- **(a) Make it a Salvation rite for a god with room** (Ishko, Ta'Baa or Sh'kaar) and design it at the
  Wasteland's next sitting.
- **(b) Make it a local custom of another faith**, like the Sun-Debt's Return; no slot used.
- **(c) Drop it.** The Wasteland already teaches three rites.

**Q4. How would you like to re-review the rites?**
- **(a) One sheet per god** (about five rites each): see a god's whole set at once and judge balance.
- **(b) One sheet per biome**, as they were pitched: judge whether each place's rite fits the place.
- **(c) Keep the accept-all** and only revisit a rite when it is built and you can play it.
