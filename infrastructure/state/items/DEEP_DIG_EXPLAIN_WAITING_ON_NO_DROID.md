# DEEP_DIG_EXPLAIN_WAITING_ON_NO_DROID

From the BENCH player's-eye FlowWorks UX review, 2026-10-22, read offline from source (owner's night order: "Keep testing and getting Flow Works absolutely logical, looking great and sensible, and the UI/UX workable for the player."). Behaviour must not change unless the item says so; text-only fixes need a winbuild with DLL + .srchash committed together.

## spec

7. **Dig deeper than colonists may**: "Dig to depth" lists every half-metre to 20 m (40 options)
   with "machines only past 2 m" in parentheses; an order past 2 m in a colony with no mechanoid or
   droid digger just sits, with no inspect line or alert saying why. Hide or grey the machine-only
   depths when no machine can dig, or say so on the designation. **Filed `DEEP_DIG_EXPLAIN_WAITING_ON_NO_DROID`.**

## criteria

- A new player can read the changed UI and know what to do next; the old confusing text is gone (grep).
- FlowWorks selftests stay as green as before.

## NEXT

Pick it up offline; no game needed for the text part.
