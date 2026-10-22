# HOSE_FITTING_RENAME_CAP_IS_NOT_CAPPED

From the BENCH player's-eye FlowWorks UX review, 2026-10-22, read offline from source (owner's night order: "Keep testing and getting Flow Works absolutely logical, looking great and sensible, and the UI/UX workable for the player."). Behaviour must not change unless the item says so; text-only fixes need a winbuild with DLL + .srchash committed together.

## spec

6. **Hose reel "Fitting: nozzle / end cap / open" is looks-only** but sits beside "Free end:
   Capped / Intake / Outflow". A player sets *Fitting: end cap* to stop flow and nothing changes.
   Rename to "End look: …" or derive the look from the role. **Filed `HOSE_FITTING_RENAME_CAP_IS_NOT_CAPPED`.**

9. Hose messages print raw coordinates ("Hose end dropped at (12, 0, 34)") — the LookTarget is
   enough; drop the vector (C#, minor; folded into item 6).

## criteria

- A new player can read the changed UI and know what to do next; the old confusing text is gone (grep).
- FlowWorks selftests stay as green as before.

## NEXT

Pick it up offline; no game needed for the text part.
