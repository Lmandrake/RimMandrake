# BRIDGE_SELECT_NONCOLONIST_PAWN_1 — the bridge cannot drive a non-colonist pawn's ability

## what is wrong

MEASURED live 2026-09-20 (FOUNDRY, during `PORTED_BEAST_MECHANICS_REBUILD_1`'s
verification pass): **`rimworld/select_pawn` and `ToolMapForPawns` both REFUSE a
non-colonist pawn.** There is no bridge route to select, or to force a mental state on,
a hostile or wild creature.

## why it matters

It is the sole blocker on three criteria of a build that is otherwise proven:

- `PORTED_BEAST_MECHANICS_REBUILD_1` criteria **4, 5 and 6** — the ability gizmo and its
  AI use, the cindermite's chemfuel cone, and settings persistence — all require making
  a **hostile predator** fire a ranged ability on command. Criterion 2 (ferroclaw eats
  steel, 75 → 60, exactly 1/5) and criterion 3's core mechanism are **DEFINITIVELY
  confirmed live**; only this capability gap stands between the item and closing.

More generally: every creature mechanic we rebuild from a donor framework is a mechanic
on a *wild or hostile* pawn. Without this, none of them can be verified except by
waiting for the AI to volunteer the behaviour, which is not a test.

## the two candidate routes

1. **A companion `[Tool]` that selects an arbitrary pawn** and/or forces a mental state
   / triggers a verb on it, bypassing the colonist check. This is the direct fix and the
   `rimbridge-companion` skill is the how-to — the C# pattern, the edit-build-deploy-test
   cycle on a minimal mod list, and `build.py`'s guards.
   ⚠️ **A companion DLL cannot be written while RimWorld is running.** This lands in a
   shutdown window.
2. **A scripted colonist-attacks-first provocation** — spawn a colonist in reach, have it
   attack, and let the predator retaliate. Cheaper, needs no DLL, but it proves the
   ability fires under AI control rather than that the gizmo works, so it cannot close
   criterion 4 on its own.

⇒ Route 1 is the real answer; route 2 is worth doing first if a shutdown window is far
off, because it would close criterion 5 (the cone) immediately.

## spec

A bridge call that takes a pawn id or defName and selects it, and a call that makes it
use a named ability or verb, with neither refusing on faction. Named tools, wired the way
`rimbridge-companion` describes, and verified by the tool appearing in the live tool list
— a newly added tool missing from that list is the known silent failure.

## verify

`PORTED_BEAST_MECHANICS_REBUILD_1` criteria 4, 5 and 6 can be exercised on
`RSW_Voltmaw` and `RSW_Cindermite` in a quicktest without a colonist provoking them.

## criteria

A wild or hostile creature's mechanic can be tested from outside the game, on demand.
