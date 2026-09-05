using RimWorld.Planet;
using Verse;

namespace RimMandrake.RaidRedesigner
{
    // Verified against 1.6 source (RimSage) before writing this, per this
    // project's no-guessing rule:
    //   - Verse/Pawn.cs ExitMap (public virtual void ExitMap(bool, Rot4),
    //     lines ~3763-3855) already calls `Find.WorldPawns.PassToWorld(this)`
    //     (default PawnDiscardDecideMode.Decide) at its own tail, BEFORE any
    //     Harmony postfix on ExitMap runs. Calling PassToWorld a second time
    //     with KeepForever at that point hits WorldPawns.PassToWorld's own
    //     `if (Contains(pawn)) { Log.Error(...); return; }` guard and does
    //     NOT upgrade the discard mode -- re-calling it there is a silent
    //     no-op, not the pin the design doc asks for.
    //   - RimWorld/Planet/WorldPawns.cs's PassToWorld(KeepForever) branch does
    //     exactly one thing besides the ordinary AddPawn: add the pawn to
    //     `pawnsForcefullyKeptAsWorldPawns`, exposed publicly as
    //     `ForcefullyKeptPawns`.
    //   - RimWorld/Planet/WorldPawnGC.cs:212 --
    //     `if (Find.WorldPawns.ForcefullyKeptPawns.Contains(pawn)) return "ForceKept";`
    //     -- is the actual GC-exemption gate ("PawnPruner's removal path" per
    //     this item's own verify section); it does not care HOW the pawn got
    //     into that set.
    //   - RimWorld/Faction.cs:1197 pins its own leader with
    //     `Find.WorldPawns.PassToWorld(leader, PawnDiscardDecideMode.KeepForever)`
    //     -- the doc's cited call, confirmed real -- but Faction calls it on a
    //     pawn NOT already in WorldPawns, so the double-call guard above never
    //     fires for that call site.
    // PinForever covers both shapes: if the pawn is already a world pawn (the
    // common case for our hooks, all of which postfix a method that itself
    // already called PassToWorld earlier in the same call), add directly to
    // the same set PassToWorld(KeepForever) would have populated; otherwise
    // call PassToWorld(KeepForever) itself, exactly as Faction does.
    public static class WorldPawnPinning
    {
        public static void PinForever(Pawn pawn)
        {
            if (pawn == null) return;
            WorldPawns worldPawns = Find.WorldPawns;
            if (worldPawns == null) return;

            if (worldPawns.Contains(pawn))
            {
                worldPawns.ForcefullyKeptPawns.Add(pawn);
            }
            else if (!pawn.Spawned)
            {
                worldPawns.PassToWorld(pawn, PawnDiscardDecideMode.KeepForever);
            }
            // else: pawn is still spawned and not yet a world pawn (e.g. the
            // Kidnap postfix fires mid-way through the kidnapper's own
            // ExitMap call, before that call's own PassToWorld runs) --
            // nothing to pin yet. The ExitMap postfix that owns this pawn's
            // eventual departure calls PinForever again once it has, in fact,
            // become a world pawn.
        }
    }
}
