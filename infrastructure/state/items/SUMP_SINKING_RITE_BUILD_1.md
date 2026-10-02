# SUMP_SINKING_RITE_BUILD_1 — Rite A, the Sinking: one thing of value into the tar

Caused by `SUMP_BEDAZZLE_SITTING_1` (turn 2). Campaign tier, `mandrake.rut.rites` (found rite).
Design: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §6 (Rite A) and §9;
offerings from `Transient/bedazzle_gpt_enrich_2026-10-01/sump_tar_offerings_redo_2026-10-02.md` §1–3
(copy what you need out of it: Transient is binned after ~14 days). Machinery: register
`design/Jawa/salvation_rites_2026-10-01.md` §(d).

Owner, typed, turn 2: *"Throwing one thing in the tar of value lowers heat, erases ownership as part of
RimProperty (perhaps of something you still keep...), and lowers raid frequency."* Offerings by
question card 2026-10-02: the beast sleeps a season; the ancient traps fizzle. Typed on the third:
*"I like Vault forgets, but it should be true about almost anything you own"*.

## spec

**God: unassigned** (open on the turn-3 card, `sump_bedazzle_review_2026-10-01.md` §8 Q1). Build the
god as one def field on the rite's outcome worker so the ruling is a one-line change; until it lands
the rite records no Ninefold delta. **Heat step size and cadence also open** (card Q3): ship them as
Mod Settings numbers with the review doc's placeholders (low 10 / high 40, once a season).

1. **Found / learned.** Inscription: a sunk ring of tar at a Junker barrel yard with a tally board
   listing what went down and no owner beside any of it (`CompStudiable`), placed on Sump maps; rubbing
   → "found rites" row → `RUT_ResearchMod_GrantRite` adds the precept, per §(d). Performable after at
   any tar (the mere, a pond, a poured moat, a tar vault).
2. **Asks.** One object of value, thrown into the tar by the participants, destroyed. Its market value
   (with attendance and roles) sets quality. Value floor is a Mod Settings number. Nothing living or
   dead may be offered (the ritual's target filter refuses pawns and corpses).
3. **Every Sinking, whatever is thrown (his three effects):**
   - **Imperial Heat falls.** Write a history event (offering value, quality, tick) to a
     `GameComponent` the GM blackboard polls; the blackboard lowers Heat by a value-scaled step. This
     overrides the K2 rule "Heat is never scrubbed by success" for this rite only (his words). Heat
     itself lives outside the save in `GM_BLACKBOARD_SHADOW_M4_1`; this item only emits the event.
   - **Raids come less often on this map.** A `GameConditionDef` `RUT_TarLull_Raids` (days left
     visible) that a Harmony postfix on the storyteller's raid roll reads. 🔴 Mechanism UNMEASURED: read
     the storyteller threat comps and the campaign's raid-pacing governors (`required_mods.md`) in
     RimSage / their source before choosing the hook.
   - **Ownership erased, widely.** Through `PROPERTY_CLAIM_ERASE_API_1`, wipe every other party's
     stored claim on almost everything the colony owns on this map: items, buildings, animals, droids
     and mechs. "Almost" is BENCH's reading, kept as a Mod Settings exclusion list, default: humanlike
     pawns (colonists, prisoners, slaves are never property here). Faction suspicion (`FactionRecord`)
     is NOT erased (not ruled). A letter lists each cleansed thing and whose claim was wiped.
4. **The offering's kind adds a rider** (one `RitualOutcomeEffectWorker` dispatching on the offered
   Thing's def/category; each rider is a table row, not a new ritual):
   - **Pitch: the beast sleeps a season.** Offering is bitumen or korveth pitch (`RUT_Bitumen`,
     `RM_KorvethPitch`) at the value floor. Map condition `RM_TarLull_Beast` for one season (15 days, a
     setting): every tar bulge on the map ignores building, digging and pumping wake causes; **an
     explosion still wakes it**, and the letter says so. Harmony prefix on the wake path
     (`RM_CompBeastWakeRelay` → `CompWakeUpDormant`) refusing those causes while the condition runs.
     The mice keep detouring (`RM_MapComponent_DreadField`), so the danger stays visible.
   - **A dig find: ancient traps fizzle.** Offering is a dig-shaft find above a value floor (excludes
     today's placeholder chunks). A `MapComponent` counter set to 3: Harmony postfix where
     `RM_CompWorkedLottery.ArmTrap` arms a trap row; while the counter is above zero the trap resolves
     through the existing `TrapDisarmResult.Disarmed` path, the counter drops, a click then a hiss and a
     puff of tar play. Ban 1 untouched: traps are rolled as often as before; they just do not go off.
     Counter shown on the dig shaft's inspect pane.
   - **Anything else of value:** the three base effects only.
5. **Readable signs.** The offering sinking with a slow bubble; the Narrator voices the Heat change;
   each lull is a map condition with days left; the cleansing letter; the trap click-and-hiss with a
   Narrator line naming which of the three it was. Nothing vanishes without a sign.
6. **Laws.** Cohesion only from the ritual's own outcome (shared memories by quality), never a
   material reward; favour shows through events and odds only, no hediff or stat. One kind of heat:
   "Imperial Heat" is the Empire's attention, not temperature; nothing here touches temperature.
7. **Mod Settings.** On/off for the rite and for each rider and each base effect; value floor; Heat
   step and cadence; raid-lull days and strength; beast-lull days; trap count (default 3); the
   ownership exclusion list.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery, `RUT_ResearchMod_GrantRite`),
`PROPERTY_CLAIM_ERASE_API_1`, `SUMP_TAR_BEAST_BUILD_1` (adds the dig and pump wake causes the beast
rider suppresses), `SUMP_FREE_TIER_MOVE_BUILD_1` (final defNames of pitch/bitumen and the bulge),
`GM_BLACKBOARD_SHADOW_M4_1` (reads the Heat event; this item ships without waiting on it).

## criteria

All deterministic state reads through debug `[Tool]`s, recorded as cases in
`src/RimUtinni/Rites/validation.py` (the mod's functional script; it gains its first C# here):
- Offering a stack of pitch: the map holds `RM_TarLull_Beast` with ~15 days left; a construction wake
  request on a bulge returns refused while a `GenExplosion` within range wakes it.
- Offering a dig find: the map's trap counter reads 3; forcing three trap rolls leaves every
  `RM_CompWorkedLottery` with `TrapArmed == false`, no explosion logged, counter 0; the fourth arms
  normally.
- Any Sinking: the Heat-event component holds one new entry with the offering's value; the raid-lull
  condition is on the map; an item seeded with a foreign `Stolen` claim reads only the colony's claim
  afterwards, a colonist pawn's records are untouched, and the letter names the item.
- The offered Thing is destroyed (no longer spawned or held); trying to offer a pawn or corpse is refused
  with a reason line; no new hediff or stat on any participant.
- Each Mod Settings toggle off removes exactly its effect (one case per toggle).
