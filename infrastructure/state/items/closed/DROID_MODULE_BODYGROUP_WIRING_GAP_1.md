# DROID_MODULE_BODYGROUP_WIRING_GAP_1 — droid apparel modules cannot be worn

## What was observed (live, quicktest, minimal 25-mod list, 2026-09-10)

Spawned `RSW_DW_KotORDroidColonist_T3UD` (race `RSW_DW_Race_guy762_DroidRace_T3series`),
set it to `PlayerColony`, selected it, and ran the debug action
`Actions\Wear apparel (selected)...\RSW_DW_Module_DroidHardware_agility`.

**Result: `success: true`, but nothing was worn.** The call's own `effects.logs`
carried the real answer:

> `Wouter tried to wear RSW_DW_Module_DroidHardware_agility39456 but he has no
> body parts required to wear it.`

`jawa/pawn_get` before and after showed `apparel: None` both times — independently
confirming the debug action's own log. This is the exact "`success: true` means
the tool ran, not that the game changed" trap (`rimbridge` skill §2).

## Root cause (CONFIRMED, from source)

`RSW_DW_Module_DroidHardware_agility` (and by construction every other module
built on `RSW_DW_ModuleBase_Tech`/`RSW_DW_ModuleApparelBase`,
`Absorbed_KotorDroidModules_{Tech,Armor,Bases}.xml`) declares
`<apparel><bodyPartGroups><li>RSW_DW_BG_ModuleHardware</li></bodyPartGroups></apparel>`.

`RSW_DW_BG_ModuleHardware` / `RSW_DW_BG_ModuleSoftware` / `RSW_DW_BG_ModuleSensor`
are custom `BodyPartGroupDef`s defined in
`Absorbed_KotorDroidModules_Bases.xml`. **Grepped the entire
`src/RimStarWars/Droidworks/` tree: these three groups are declared, and
referenced by every module's `bodyPartGroups`, but are never assigned to any
`BodyPartDef` anywhere** — no custom `BodyDef`, no `PatchOperationAdd` onto
`Bodies/Human.xml`'s parts' `<groups>` lists.

Every Droidworks race traces to `DW_Race_Base` (`Races_Base.xml:50`):
`<race><body>Human</body></race>` — **every droid in this mod uses the
unmodified vanilla Human body.** Vanilla Human parts do not carry these
groups. So **no pawn in the game can satisfy this apparel's requirement** —
the mechanism is unwearable by construction, on any droid, not just the one
tested.

## Why this wasn't caught before — UNMEASURED, plausible theory only

`DROIDWORKS_MODULE_ABSORB_1` closed 2026-09-08 with "A KotOR kind spawns
wearing its modules — live-confirmed 2026-09-08" checked off. That test likely
ran while a donor mod (`guy762.kotorcore` and/or `guy762.kotordroids`) was
still active in the live mod list — the donor may own a patch that adds these
same-named groups to the parts its own droids use, which this mod's own code
never reproduced independently. **Did not confirm this against the donor's
own XML** (a workshop-wide grep timed out; not repeated — this is a plausible
explanation, not a proven one). Whether or not that theory is right, the fact
that stands regardless: this mod's own `src/` has no reproduction path
that survives the donor's absence, and donor retirement is IN FLIGHT right now
(`DROID_RETIRE_KOTORDROIDS_1`, `DROID_RETIRE_ABF_SYNCORE_1`,
`DROID_RETIRE_DEPOT_ASIMOV_1` — all currently blocked, not yet executed).

## spec

Give Droidworks its own, donor-independent way to satisfy these three
`bodyPartGroups` on droid pawns. Options, cheapest first:
1. A `PatchOperationAdd` onto `Bodies/Human.xml`'s relevant `BodyPartRecord`s'
   `<groups>` lists, adding `RSW_DW_BG_ModuleHardware`/`Software`/`Sensor` —
   simplest, but touches the SHARED vanilla Human body (every human-body race
   would gain the slot; check whether that's acceptable or needs a
   Droidworks-only custom `BodyDef` instead).
2. A dedicated `BodyDef` (e.g. `RSW_DW_DroidBody`) cloned from Human with
   these groups added to the appropriate parts, then re-point `DW_Race_Base`'s
   `<race><body>` to it.

## verify

Same live steps this finding used: spawn a Droidworks droid on the minimal
list (no donor active), `PlayerColony` it, select it, run the same debug
action, confirm via `jawa/pawn_get`'s `apparel` field that the module is
actually worn (not just `success: true`), and confirm `hediffs` gains the
matching personality hediff. **This also unblocks
`DROIDWORKS_MODULE_PERSONALITY_1`'s own owed live check** — re-run it once
this closes.

## criteria

Closes on: one module of each family (Tech/Software/Sensor via
`RSW_DW_BG_ModuleHardware`/`Software`/`Sensor`) worn live on a Droidworks
droid, apparel field populated, matching hediff present, with the donor mod
absent from the mod list (the state this campaign is heading toward).
