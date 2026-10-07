# RUSTCATHEDRAL_HULL_BOLTS_BUILD_1 — Hull bolts: living bolts that ride the ship for good, hull pets that are secretly the Cathedral's ears

Caused by `RUSTCATHEDRAL_SCORING_SITTING_1` (turn 1). Mechanism free tier (`mandrake.rm.rustcathedral`);
the ship's realisation, the god's reveal and Regard in the campaign (`mandrake.rut.rites` or
`UtinniPatches`, part 6). Mark 6 (gravship touch). Design:
`design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §4 row 4 (the pitch,
changed by the ruling), §8.

Ruling, owner, typed 2026-10-02: *"Would it be possible for some stowaway bolts to REMAIN on the ship and
continue to function due to the internal systems of the Rakatan nature of the ship? These would be almost
like external hull pets. Resistant to all weather and many damage types. Would also secretly be spies for
the Cathedral to hear through, and the ship would realize that. One of the gods would eventually reveal
this to the Jawa, and then they have a dilemma: remove it (and anger the Cathedral) or leave it (and be
spied upon)."* **What changed from the pitch:** the pitched bolts went still within a day of leaving the
hum; the ruled ones **never** go still aboard. Remnant rebuilding and sun bars were **not chosen** that same
card.

**Name:** *hull bolts* (`RM_HullBolt`). Collision-checked 2026-10-02: 0 repo files for `hull bolt` /
`hullbolt`, 0 artpipe hits; Wookieepedia full-text returns only generic pages on fusion bolts and hull
plating, no creature or object of the name.

Sheet bans hold (`the_rust_cathedral.md` §6): **no player text explains the mind**, and the Cathedral is
never named as a listener in free-tier text. The campaign god names it, in the god's voice, once.

## spec

1. **Boarding.** While a gravship is landed on `RM_RustCathedral`, living bolts (`RM_LivingBolt`) are drawn
   to it: their dance job (`RM_JobGiver_ResonantDance`) prefers substructure-edge cells (a weight, not a
   new job). At liftoff, up to 3 (Mod Settings; default 1 to 3 by a roll, 0 with a chance) bolts within 4
   cells of the substructure become `RM_HullBolt`s and travel aboard. A letter names what was seen: *"A few
   of the dancing bolts are still clinging to the hull."*
2. **What they are aboard.** `ThingDef`/`PawnKindDef RM_HullBolt`, a living-bolt race variant (the same
   body, `RM_BoltFrame`): wild, factionless, never tameable, never hostile. A comp `RM_CompHullBound`
   confines it to the gravship's **outer substructure cells** (the `RM_CompWaterLocked` pattern applied to
   substructure; it never wanders the map or into a room). It dances its figures on the hull, travels in
   every launch, survives space. **Resistant to all weather and many damage types:** no temperature,
   toxic-buildup or vacuum harm; damage factors near zero for Flame, Burn, Frostbite, Toxic, EMP and
   electrical; ordinary physical damage can still kill one (its body is a bolt). It does **not** go still
   off the plateau (the ship keeps it going; that sentence is the most any text says).
   - **Hull pets:** while at least one rides aboard, colonists get a small positive memory now and then on
     seeing one (`ThoughtDef RM_HullBoltsSeen`); a hum reader (`RM_HumReader`, from
     `RUSTCATHEDRAL_BASE_FINISH_BUILD_1`) sees its current figure named in plain words on its inspect pane.
3. **Spied on: what it does, mechanically, and how it reads.** While ≥ 1 hull bolt is aboard, the
   Cathedral **hears** the colony. A game component `RM_GameComponent_HullBoltWitness` keeps a ledger:
   - **Witnessed acts** (data: `RM_CathedralWitnessDef`, tunable): selling `RM_BoltShedCuriosity`,
     `RM_CoolantEelCatch`, `RM_DeadSmartsteel` or `RM_LivePatternMetal` anywhere; butchering any bolt; the
     colony destroying a hull bolt; each with an irritation weight. In the campaign, the patch adds the arc's
     own losses: every mindstone or kyber sale (`CATHEDRAL_REGARD_BLACKBOARD_1`'s inputs, which otherwise
     count only on Cathedral ground, count everywhere while a hull bolt is aboard).
   - **The tell (readable when it happens):** at each witnessed act, every hull bolt stops its dance and
     turns toward the act (a short still job and a mote), wherever the ship is. Nothing explains it.
   - **The consequence:** on the next landing on Rust Cathedral ground the attitude component **starts with
     the ledger's irritation already applied** (capped; the ledger then clears), and the arrival letter
     reads *"The hum is already uneasy."* A hum reader's readout says the same in plain words. In the
     campaign, the same acts post to Regard as they happen.
   - **Nothing is silent:** every witnessed act shows the tell; every landing shows the starting band.
4. **The ship realises (campaign).** After a hull bolt has been aboard for 10 days (Mod Settings), the
   substructure under each hull bolt carries a visible mark (a cold-blue tarnish overlay on those cells) and
   the bolt's inspect line adds *"The hull is cold under it."* That is the ship knowing, shown and never
   said. Free tier: the same mark appears (the ship is a ship in both tiers); only the meaning goes unsaid.
5. **The reveal and the dilemma.**
   - **Campaign: a god reveals it.** When the ship's mark has stood 5 more days and the colony next sees a
     tell, **Ishko** (hiding, ambush, the watcher; *"the Unmaskable"*: the god who knows when the clan is
     being watched) speaks through the Narrator, once, in a letter that names the bolts as the Cathedral's
     ears. The letter offers the dilemma.
   - **Free tier:** the same letter fires, unvoiced by any god, once a hum reader has watched a tell
     (*"They dance the plateau's figures, far from the plateau."*), and offers the same dilemma.
   - **Remove them** (*and anger the Cathedral*): each hull bolt gets a "Pry it off" order (a short job, any
     colonist); a pried bolt becomes a `RM_BoltShedCuriosity`. Each removal adds a large irritation to the
     ledger (applied at the next Cathedral landing, as above) and, in the campaign, a Regard loss event. The
     witnessing stops when none is left.
   - **Leave them** (*and be spied upon*): nothing is removed; the witnessing continues as in part 3 and the
     pets stay. The choice is recorded (no repeat letter); prying one off later is still possible and still
     angers.
   - Either way, Ishko's reaction is the god's own business (no delta specified by the ruling; none is added
     here).
6. **Mod Settings:** on/off; boarding count and chance; witnessed-act weights; irritation cap; realisation
   and reveal delays; the pet memory.

Depends on: `RUSTCATHEDRAL_FREE_NAMES_TIDY_1`, `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` (hum readers; without
them the free-tier reveal waits). Campaign: `CATHEDRAL_REGARD_BLACKBOARD_1` (Regard lines are logged
would-be events until it exists, never silent). Art: `RM_HullBolt` in
`infrastructure/artpipe/art_lists/rustcathedral_turn1_2026-10-02.csv`. ⚠️ `RM_LivingBolt` has no shipped art
yet (its `rut_livingbolt_v1` artpipe jobs failed validation, MEASURED 2026-10-02); the hull bolt is queued as
its own sprite so it does not wait on that.

## criteria

Deterministic state reads through `jawa/get_defs` and debug `[Tool]`s, recorded as cases in
`RUST_CATHEDRAL_FIRST_SCRIPT_1`'s `validation.py` (campaign cases in `src/RimUtinni/Rites/validation.py`):
- Defs resolve: `ThingDef/RM_HullBolt`, `PawnKindDef/RM_HullBolt`, `ThoughtDef/RM_HullBoltsSeen`,
  `RM_CathedralWitnessDef` (≥ 1 def).
- Boarding: launch a gravship from a Rust Cathedral test map with living bolts placed within 4 cells, count
  forced to 2: after landing elsewhere, exactly 2 `RM_HullBolt` exist on the new map, each on a substructure
  cell; after 30,000 simulated ticks every one still stands on a substructure cell and none is downed.
- Resistance: set map temperature to −80 °C and +90 °C for 10,000 ticks each: each hull bolt's hediff set
  holds no Hypothermia, Heatstroke or ToxicBuildup; their damage factors for Flame and EMP read ≤ 0.1.
- Witness: with a hull bolt aboard, selling one `RM_BoltShedCuriosity` adds one ledger entry with the
  configured weight and gives each hull bolt the tell job; with no hull bolt aboard, the same sale adds none.
- Consequence: landing on a Rust Cathedral map with ledger total T sets the attitude component's starting
  irritation to min(T, cap) above its baseline, and the ledger reads empty afterward.
- Realisation: at the configured day count the substructure cells under each hull bolt carry the mark
  (read the overlay set) and the inspect string contains the cold line.
- Reveal: campaign: one Narrator letter tagged Ishko fires once; free tier: the unvoiced letter fires only
  after a hum reader is assigned and a tell occurs.
- Remove: prying one off spawns one `RM_BoltShedCuriosity`, removes the pawn, and adds the removal weight to
  the ledger; with none left, a later sale adds no entry.
- Each Mod Settings toggle off removes exactly its effect.

## Built offline (2026-10-07, FOUNDRY helper; never run in game, not deployed)

- `src/RimMandrake/RustCathedral/Source/Hum/RM_HullBolts.cs`: boarding is a prefix on `GravshipUtility.GenerateGravship`
  (swaps 0-3 living bolts within 4 cells of `engine.ValidSubstructure` for `RM_HullBolt` pawns on outer hull cells; the
  engine's own `Gravship.CopyCellContents` then carries them, since `bringAlongOnGravship` defaults true and `AddThing`
  takes pawns, so there is no custom travel code). `RM_CompHullBound` walks a stray back to the nearest hull cell, holds
  `boardedTick`, the realised mark and the inspect lines. `RM_JobGiver_HullDance` snaps the three plateau figures to hull
  cells. The plateau dance now centres some figures on a landed ship's nearest hull cell (`ShipEdgeAnchor`, 35%).
- Witness: `RM_CathedralWitnessDef` (7 defs: four Sells, Butcher bolt, destroy hull bolt, pry). Hooks are
  `Tradeable.ResolveTrade` (PlayerSells), `Corpse.ButcherProducts` and `Pawn.Kill` (player instigator). Every act makes
  each hull bolt do `RM_HullBoltTell` (stop, face the act on that map, micro sparks).
  `RM_GameComponent_HullBoltWitness` keeps the ledger. The first 250-tick check with a player engine on a Rust Cathedral
  map applies `min(total, cap)` through `RM_MapComponent_BiomeAttitude.AddIrritation`, clears the ledger, sends
  "The hum is already uneasy." and adds "It was uneasy before you landed." to the hum reader readout for a day.
- Realisation is `hullBoltRealiseDays` after boarding: the cold line plus a cold-blue overlay
  (`RM_MapComponent_HullBoltMarks`, the bolt's cell and its last 8 cells). The reveal is `hullBoltRevealDays` after
  the first realisation, at the next tell while a hum reader is on a hull bolt's map. It is the free-tier
  `RM_HullBoltsDilemma` choice letter. After the reveal a right-click "Pry the hull bolt off"
  (`FloatMenuOptionProvider_PryHullBolt`, `JobDriver_PryHullBolt`, 300 ticks) leaves a shed curiosity and records the
  pry weight. Pet memory `RM_HullBoltsSeen` (+2, 1 day) has a 15% chance per colonist every 2500 ticks within 10
  cells with line of sight.
- 12 Mod Settings in the hull-bolt block. All numbers PROVISIONAL. Resistances: mechanoid base, plus VacuumResistance 1
  and damageMultipliers of 0.05 for Flame, Burn, Frostbite, EMP, AcidBurn, ToxGas and ElectricalBurn.
- L0: `validation.hullbolts_problems` (in `static_checks`) and `selftest_rustcathedral_hullbolts.py` 17/17.

Still owed:
- Campaign: Ishko voicing the reveal and Regard posting (`RM_HullBolts.OnWitnessed` is the hook). Kyber and mindstone
  sales also need witness defs, and their defNames are not measured.
- Art: `RM_HullBolt` uses the living bolt's texPath. The artpipe `_artsrc/RM_HullBolt_*` renders have no ruling.
- "Electrical" has no vanilla DamageDef, so it is mapped to ElectricalBurn.
- L1/L2: every criterion above is a live read, owed.
