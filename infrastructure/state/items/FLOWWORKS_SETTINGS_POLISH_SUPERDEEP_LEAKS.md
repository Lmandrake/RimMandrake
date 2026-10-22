# FLOWWORKS_SETTINGS_POLISH_SUPERDEEP_LEAKS

From the BENCH player's-eye FlowWorks UX review, 2026-10-22, read offline from source (owner's night order: "Keep testing and getting Flow Works absolutely logical, looking great and sensible, and the UI/UX workable for the player."). Behaviour must not change unless the item says so; text-only fixes need a winbuild with DLL + .srchash committed together.

## spec

4. **Developer jargon on the settings page (C# strings)**: "superdeep" (lines ~1012, 1326, 1351,
   1361, 1506, 1563, 1657, 1873 of RimMandrakeFlowWorksMod.cs), "owner decision 2026-10-15",
   "came in with the liquid-types merge", "per that liquid's registry row", "PROVISIONAL",
   "first-guess number" (dig finds, swale, sluice delays), "(owner's pick: 8)", "The fourth
   acquisition route", "the shipped campaign behaviour", "the job-loop bug", "the old rule" /
   "as before" / "how the mod behaved before this", "Shipped:" vs "default" mixed, raw ticks
   ("every 250 ticks", "~700 ticks; a soil cut is 3200"), "Thirst provider". **Filed `FLOWWORKS_SETTINGS_POLISH_SUPERDEEP_LEAKS`.**

5. **Contradictory tooltips about getting out of a pit** (C#): "A ladder is needed to get out"
   says a pit holds you "until a ladder stands in their cell" — ladders hang on a wall square,
   and ramps, portable ladders, climbing gear and jumps are all exits now. "Your own pit takes your
   own people" says "a superdeep cell … to build the ladder". (Folded into item 4.)

8. **Units drift**: bridges/ramps say "squares", pipes/hoses/sprinklers/settings say "cells";
   "level"/"fill level" leaks ("Fill in canal … by one level", "a fill level every N s",
   "Liquid held per hose cell"); tank capacity in kL beside litres everywhere else. Pick
   squares + metres + litres (Folded into item 4.)

10. Dig canal / Fill in canal descriptions never say the work type (Mining) — a new player with
    no miner wonders why nothing digs (C# designator text; folded into item 4).

## criteria

- A new player can read the changed UI and know what to do next; the old confusing text is gone (grep).
- FlowWorks selftests stay as green as before.

## NEXT

Pick it up offline; no game needed for the text part.
