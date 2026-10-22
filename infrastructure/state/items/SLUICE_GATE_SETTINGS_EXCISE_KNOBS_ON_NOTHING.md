# SLUICE_GATE_SETTINGS_EXCISE_KNOBS_ON_NOTHING

From the BENCH player's-eye FlowWorks UX review, 2026-10-22, read offline from source (owner's night order: "Keep testing and getting Flow Works absolutely logical, looking great and sensible, and the UI/UX workable for the player."). Behaviour must not change unless the item says so; text-only fixes need a winbuild with DLL + .srchash committed together.

## spec

3. **Settings that do nothing**: the "Sluice gates" section (on/off + open/shut delays) drives
   `Building_RM_SluiceGate`, which **no def uses**; the player's sluice is `RM_Sluice`, a door
   (`Building_RM_FlowDoor`). Three different things are also called "sluice" (canal sluice door,
   these gate settings, the river *sluice box*). **Filed `SLUICE_GATE_SETTINGS_EXCISE_KNOBS_ON_NOTHING`.**

## criteria

- A new player can read the changed UI and know what to do next; the old confusing text is gone (grep).
- FlowWorks selftests stay as green as before.

## NEXT

Pick it up offline; no game needed for the text part.
