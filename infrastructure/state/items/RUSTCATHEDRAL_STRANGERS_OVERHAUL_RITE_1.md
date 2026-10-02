# RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1 — The Stranger's Overhaul, for Ohm: repair a free droid as a sacred act, then keep it or let it go

Caused by `RUSTCATHEDRAL_SCORING_SITTING_1` (turn 1). Campaign tier, `mandrake.rut.rites`
(`src/RimUtinni/Rites/`, found rite). Design:
`design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §8. Register:
`design/Jawa/salvation_rites_2026-10-01.md` B12 (row added) and §(d) for the found-rite machinery.

Ruling, owner, typed 2026-10-02: *"2nd ritual should be about droids: offer to repair one of the free
droids here as a sacred act. Option to capture it while it is being repaired (pleases trading god, pleases
Ohm, angers prideful god, angers neutral droids, angers Cathedral) or complete the repair and release it
(annoys trading god, pleases Ohm, pleases neutral droids, pleases Cathedral)."*

**Readings (BENCH, recorded in review §8):** the **trading god is Mob'Unloo** (*"God of trade, haggling,
debt, and the sacred exchange"*, `divine_satiation_engine.md` ④; a captured body is *"captured value"* to
him); the **prideful god is Ozzik**; the **neutral droids are the Free Droid Enclaves**
(`RUT_Jawa_FreeDroidEnclaves`; eight of their twelve seats stand on Cathedral ground, sheet §3/§8); **the
Cathedral** is its hum (irritation in `RM_MapComponent_BiomeAttitude`) and, in the arc, its Regard
(`CATHEDRAL_REGARD_BLACKBOARD_1`). The rite belongs to **Ohm** (pleased on both branches, and the droids'
god). **Name:** *the Stranger's Overhaul* (repairing a droid that is not yours); collision-checked
2026-10-02: 0 repo files, 0 artpipe hits; Wookieepedia full-text returns only generic "The Stranger" pages,
no thing of this name. Ohm's found rites: the Engine Hour, the Last Track, the Deserter's Welcome (B7,
pitched), the Answering (B8, ruled), and this: **five, at the cap**.

Applied to the giant: stage 4 of `RUSTCATHEDRAL_WORN_BIT_ARC_1` is this rite with the borehulk as target;
that item multiplies the effects and adds the giant's payoffs. This item builds the rite for any droid.

## spec

**God: Ohm.** Kind: feeding. Each branch calls `GameComponent_Ninefold.ApplyDelta(God, <amount>,
"The Stranger's Overhaul")` once per god it names, the call shape of `SUMP_SINKING_RITE_BUILD_1`, signs per
Ninefold's own convention for "pleased" and "displeased".

1. **Found / learned.** Inscription `RUT_OverhaulChassis`: on Cathedral ground beside the enclaves' holy-city
   road, a droid chassis on its back with its chest panel open and a ring of laid-out tools around it, the
   work clearly stopped halfway and long ago; scratched on the panel in the clan's trade marks: *fixed, not
   kept.* Placed on Rust Cathedral maps by a map GenStep with a chance (never worldgen; the
   `RUT_FelledNoonStump` shape). Rubbing (`CompStudiable`) → the Rites tab's found-rites row →
   `RUT_ResearchMod_GrantRite` adds the precept, per §(d). Performable after on any map.
2. **A free droid to repair, here.** So the rite has its subject where it is found: on Rust Cathedral maps a
   rare incident `RUT_StrandedPilgrimDroid` places one damaged, downed droid of the Free Droid Enclaves on
   the map edge road (an enclave pilgrim broken down on its way to the holy city), with a plain letter. It
   lies there for days (not dying), then is collected by its own kind if no one acts.
3. **Target.** A `RitualObligationTargetFilter` over pawns: a droid (the Droidworks droid predicate, read
   from `src/RimStarWars/Droidworks/`; vanilla mechanoids of non-player factions also qualify), **not the
   colony's**, not hostile, damaged or downed, not a prisoner. Factionless qualifies. The borehulk qualifies
   only under the Worn Bit's stage-4 conditions.
4. **The rite.** Participants gather round the droid; one repairer works on it in place (no bench), a long
   job (Crafting; consumes components scaled to the damage: `ComponentIndustrial`, steel). **Mid-repair**
   (at half progress) a choice letter stops the work with two options:
   - **Capture it while it is being repaired.** The repairer locks the panel: the droid becomes the colony's
     (reuse the ownership transfer `src/RimUtinni/DroidRepairJobs/` already performs in its "you kept it"
     outcome, `QuestPart_DroidRepairJobOutcome`). Effects: Mob'Unloo **pleased**, Ohm **pleased**, Ozzik
     **displeased** (the proud god scorns a theft dressed as a mercy), Free Droid Enclaves goodwill **down**
     (default −20), the Cathedral **angered**: hum irritation up (default +25) and, in the arc, a Regard loss
     event. The rite's outcome quality still sets the shared memories.
   - **Complete the repair and release it.** The work finishes; the droid is healed and walks away under its
     own faction (or off the map, if factionless). Effects: Mob'Unloo **slightly displeased** ("annoys":
     value let go for nothing), Ohm **pleased**, Free Droid Enclaves goodwill **up** (default +15), the
     Cathedral **pleased**: hum irritation down (default −25) and a Regard gain event.
5. **Outcomes: cohesion only.** Shared memories by quality (a released droid gives the warmer memory, a
   captured one an uneasy-proud one). Favour is told by the Narrator and shows only as events and odds,
   never a buff, hediff or stat.
6. **Readable signs:** the open-panelled droid during the rite; the choice letter naming both costs plainly
   (gods by name, the droids, *"the hum will know"*); the faction goodwill line; the hum band; the letter
   after.
7. **Off Cathedral ground** the Cathedral lines do nothing (no hum on the map) except the Regard event,
   which the blackboard may weight by place (its design, not this item's).
8. **Mod Settings:** on/off; every default above; the pilgrim-droid incident chance; inscription chance.

Collision check: `DroidRepairJobs` is a paid shop job brought to you by a customer, judged by the part you
fit; Zizzik's Nine Faults runs a newly found machine; the Answering settles with a machine mind; the
Deserter's Welcome takes in a deserter. None is a rite of repairing a stranger's droid in the open with a
capture-or-release fork.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery), `RUSTCATHEDRAL_FREE_NAMES_TIDY_1`
(attitude names). Soft: `CATHEDRAL_REGARD_BLACKBOARD_1` (until it exists, the Regard events are logged
would-be events, never silent). Blocks: `RUSTCATHEDRAL_WORN_BIT_ARC_1` stage 4. Art:
`infrastructure/artpipe/art_lists/rustcathedral_turn1_2026-10-02.csv` (`RUT_OverhaulChassis`).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded as cases in `src/RimUtinni/Rites/validation.py`:
- Studying `RUT_OverhaulChassis` to completion: the found-rites row lists the Stranger's Overhaul and the
  precept is granted.
- `RUT_StrandedPilgrimDroid` fires only on `RM_RustCathedral` maps; after it, exactly one downed droid of
  `RUT_Jawa_FreeDroidEnclaves` is on the map.
- Target filter on a test map with four droids (colony-owned, hostile, healthy-neutral, damaged-neutral):
  only the damaged neutral is valid; each refusal carries a reason line.
- Capture branch: the droid's faction becomes the player's; Ninefold logs exactly three deltas tagged
  "The Stranger's Overhaul" (Mob'Unloo pleased, Ohm pleased, Ozzik displeased, signs per convention); Free
  Droid Enclaves goodwill changed by the configured capture amount; on a Cathedral map the attitude
  irritation rose by the configured amount.
- Release branch: the droid's faction is unchanged and its downed state cleared; Ninefold logs Mob'Unloo
  displeased (smaller magnitude than the capture's pleased), Ohm pleased; goodwill up by the configured
  amount; irritation down by the configured amount.
- The choice letter fires at half progress (progress read at the letter) and work does not advance while it
  is open.
- No new hediff or stat on any participant.
- Each Mod Settings toggle off removes exactly its effect.
