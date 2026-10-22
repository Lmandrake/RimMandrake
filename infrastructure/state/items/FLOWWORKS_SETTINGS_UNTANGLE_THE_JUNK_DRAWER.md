# FLOWWORKS_SETTINGS_UNTANGLE_THE_JUNK_DRAWER

From the BENCH player's-eye FlowWorks UX review, 2026-10-22, read offline from source (owner's night order: "Keep testing and getting Flow Works absolutely logical, looking great and sensible, and the UI/UX workable for the player."). Behaviour must not change unless the item says so; text-only fixes need a winbuild with DLL + .srchash committed together.

## spec

2. **Settings page grouping**: "Pits, ladders and shooting" holds ~90 controls including liquid
   looks (sheen, wakes, bubbles, see-through), the per-liquid "can fill a cut" list, the water-
   levelling engine (level by surface / exactly level / settles flat), viscosity, sluice doors,
   concealed pits and trench cover. Pipe settings are split three ways ("Liquid machinery",
   "Hoses and pipes", "The liquid tank" — which owns the *pump* on/off; tank Jobs live under Hoses).
   Suggested sections: Digging · Water and levelling · Pits and climbing · Falls, spikes, rails ·
   Pit prisoners · Drowning, poison, slime, exposure · Concealed pits · Combat at pits (cliff
   shooting, trench cover) · How cuts and liquids look · Tanks, pumps, pipes and hoses (one
   section). **Filed `FLOWWORKS_SETTINGS_UNTANGLE_THE_JUNK_DRAWER`.**

## criteria

- A new player can read the changed UI and know what to do next; the old confusing text is gone (grep).
- FlowWorks selftests stay as green as before.

## NEXT

Pick it up offline; no game needed for the text part.
