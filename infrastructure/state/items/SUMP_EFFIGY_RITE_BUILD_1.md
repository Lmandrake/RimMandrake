# SUMP_EFFIGY_RITE_BUILD_1 — Rite B, Mob'Unloo's Price: a good thing and a hated effigy

Caused by `SUMP_BEDAZZLE_SITTING_1` (turn 2). Campaign tier, `mandrake.rut.rites` (found rite).
Design: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §6 (Rite B) and §9.
Machinery: `design/Jawa/salvation_rites_2026-10-01.md` §(d).

Owner, typed, turn 2: *"throwing in one good thing and one hated effigy to Mob'Unloo brings about
unfortunate consequences on someone else, paid for by you."* Empire effigy, typed: *"(3) but it
effectively holds off the Empire for x5 the normal time on this map"*. Faction effigy: all of the next
group arrive tarred (decision taken by question card). None of the redo's three further Rite B
offerings (kept trap, beast eats their camp, skarrids on their road) were taken: Rite B is exactly the
two effigy effects below.

## spec

1. **God: Mob'Unloo** (his words). Kind: settlement. On completion,
   `GameComponent_Ninefold.ApplyDelta(God.MobUnloo, <sized by the good thing's value>, "Mob'Unloo's Price")`
   (read `ApplyDelta`'s sign convention before wiring; size is a Mod Settings number).
2. **Found / learned.** Inscription: at a Junker station's edge, a sunk ring of straw-and-rag effigies
   half-swallowed by the tar, one still holding a carved stormtrooper's helmet, a tally board naming
   what each cost (`CompStudiable`), placed on Sump maps; rubbing → "found rites" row →
   `RUT_ResearchMod_GrantRite`, per §(d). Performable after at any tar.
3. **The effigy item, `RUT_TarEffigy`.** Cheap craftable (straw, cloth, a little wood) at a crafting
   spot or table. Its **target faction is chosen when the bill is made** (a comp storing a `Faction`
   reference, saved, shown in the label: "effigy of the Galactic Empire"), tinted by that faction's
   colour. Allowed targets: any non-player faction the colony knows. ⛔ Never a god (no god is evil or
   an enemy), never the player's own faction or a colonist. The Empire is a faction like any other here
   (the vanilla Empire faction, reskinned).
4. **Asks.** One good thing (the price, destroyed; value floor a Mod Settings number) and one
   `RUT_TarEffigy`, both thrown into the tar and destroyed. Nothing living or dead goes in.
5. **Empire effigy: the hold-off, five times over, on THIS map.** Imperial Heat is untouched. The map the rite is performed on gets a `GameConditionDef`
   `RUT_ImperialHoldOff` (days left visible; shared with `SUMP_SINKING_RITE_BUILD_1`, which calls the same hold-off) lasting **5 × the normal hold-off interval**, during which
   no Empire raid, drop or inspection incident may target this map (Harmony on incident target
   selection for the Empire faction; other maps unaffected). The same multiplier is written as a
   history event the GM blackboard reads, multiplying this map's remaining orbital-detection time by 5.
   "Normal time" is the blackboard's orbital-detection interval, a placeholder today (60,000 ticks in
   `gm_blackboard_shadow.py`); until M4 is real it is a Mod Settings number "normal Empire hold-off
   (days)". 🔴 The vanilla-side Empire raid gate is UNMEASURED: find the incident path the Empire's
   raids take (RimSage) before choosing the hook.
6. **Faction effigy: the next group arrives tarred.** A `WorldComponent` stores one pending curse per
   faction. The **next** group of that faction to arrive on any player map (raid, caravan, visitors,
   quest camp) has **every** member given the tarred condition (`RM_Tarred` after
   `SUMP_FREE_TIER_MOVE_BUILD_1`'s rename: slowed, stinking, filthy, black-coated, leaving a tar trail)
   on arrival; the curse is then consumed. Hook: one postfix where an arriving group's lord is made on a
   player map, filtered by faction. Goodwill untouched; they never learn who did it. One effigy, one
   arrival; two effigies against one faction queue two arrivals.
7. **Paid for by you.** The good thing is gone; nothing comes back. Cohesion only from the ritual's
   own outcome, never a material reward; favour shows through events and odds, no hediff or stat on
   the colony.
8. **Readable signs.** The effigy and the price sinking; for the Empire, the map condition with days
   left and a Narrator line; for a faction, the Narrator names the cursed group the moment it arrives,
   and its members are visibly black-coated and trailing tar.
9. **Mod Settings.** On/off for the rite, the Empire effect and the faction effect; value floor;
   hold-off multiplier (default 5) and normal interval; Mob'Unloo delta size.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery), `SUMP_FREE_TIER_MOVE_BUILD_1`
(`RM_Tarred`), `GM_BLACKBOARD_SHADOW_M4_1` (reads the Empire event; this item ships without waiting
on it).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded as cases in
`src/RimUtinni/Rites/validation.py`:
- Crafting an effigy against faction X: the item's comp reads faction X; the bill offers no god, no
  player faction, no colonist.
- Empire effigy rite on map M: M holds `RUT_ImperialHoldOff` with 5 × the configured interval left; a
  forced Empire raid incident targeting M is refused while one targeting another map fires; the
  Heat-event component shows no Heat change and one hold-off entry.
- Faction effigy against X: the world component holds one pending curse for X; force a raid by X onto a
  quicktest map: every pawn of that lord has the tarred hediff, the curse is cleared, and a second raid
  by X arrives untarred; X's goodwill is unchanged.
- Ninefold reads one Mob'Unloo delta tagged "Mob'Unloo's Price"; both offered things are destroyed;
  offering a pawn or corpse is refused with a reason line.
- Each Mod Settings toggle off removes exactly its effect.
