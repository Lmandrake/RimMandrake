# WARSCAR_HOSPICE_DESERTERS_1 — the hospice: carry a deserter home and wake it; a deserter walks in

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.7 and §4 #3 (turn-4 IN).
Ruled turn 2: **built before the rainbow pools**. Owner, typed: *"Those droids should be INTERESTING
cases... they all left their owner, ran away, then died a slow death. That's gotta leave some strange
features inside."* Memory texts: **BENCH drafts, the owner edits** (turn 4) — the drafts are
`warscar_bedazzle_cast_2026-09-30.md` §6; build from the owner-edited version of that section.

## spec

1. **Scatter:** `RM_KneelingChassis` (slagged / posed / intact) in rings facing the ruin layout's centre.
   Slagged and posed deconstruct to steel, components, sometimes **`RM_ChassisCore`**; intact
   **minifies** and carries `RM_CompDeserterHistory`, which rolls and saves one
   **`RM_DeserterHistoryDef`**. 0–2 intact per map; never fabricable.
2. **Histories:** seven starting defs (the turn-3 §2.7 table; memory lines from the cast bible §6),
   each = **modifications** (hediffs kept on waking), **damage**, **three memory lines** revealed by stage.
   §GM guard: memories never name the enemy, the side or the god.
3. **`RM_HospiceCradle`**: staged repair, staged over days (ruled): diagnosis (oddities listed) →
   lights (components; memory 1) → twitching limbs (**etchant** from the pools, optional before they
   exist: slower and riskier; may lash out once; memory 2) → voice fragments (a chassis core; speech
   motes; memory 3) → waking. A failure leaves **`RM_FailedChassis`**, which keeps the machine's name
   and oddities on hover and description; studied for research or shredded, never a blank chunk.
   Reuse the WreckedMachines three-state ladder if its code is a comp; otherwise a 5-stage comp.
4. **The pawn: `RM_AncientServitor`**, a mechanoid race with hauling/construction/mining/cleaning and
   **no `CompOverseerSubject`** (so `IsColonyMechRequiringMechanitor` is false: no mechanitor). Verify
   every caller of that method and `GetOverseer()`. Strong worker, balanced by cradle days, parts,
   failure risk and rarity (the owner's principle: never narrowed).
5. **Old tongue step:** the hospice-protocols reading (`WARSCAR_OLD_TONGUE_1`) lowers failure and reveals
   oddities at diagnosis.
6. **A deserter walks in** (turn-4 IN): an `IncidentWorker`, rare, only while the colony has a cradle:
   a damaged servitor walks onto the map heading for the cradle, carrying a history; sometimes a pursuer
   follows. Take it in, or refuse and it kneels at the map edge and stops (stays as a posed chassis).
7. **Campaign swap:** on the RUT twin, intact chassis are canon droid chassis handed to
   Droidworks / `DroidRepairJobs`; histories carry over as data.
8. **Readable signs:** the kneeling rings; posed chassis; cradle stage label and lights; the failed wreck
   that keeps its name; the waking letter (*"It looked at the Cathedral first."*).
9. **Mod Settings:** hospice on/off · intact chassis per map (0–3) · stage length · failure chance ·
   lash-out on/off · deserter walk-in on/off and frequency.

## criteria

- A quicktest Warscar map carries kneeling rings with 0–2 intact chassis, each with a saved history.
- An intact chassis hauled to a cradle passes all five stages with the right inputs and joins as a
  colony mech with no mechanitor; its modification hediffs are present.
- A forced failure produces `RM_FailedChassis` carrying the same name.
- A dev-fired walk-in incident brings a servitor to the cradle.
