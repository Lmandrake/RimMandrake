using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.CathedralPass
{
    [DefOf]
    public static class CathedralPassDefOf
    {
        public static HediffDef RUT_CathedralPass;

        static CathedralPassDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(CathedralPassDefOf));
        }
    }

    // CATHEDRAL_MECHANOID_PASS_VERBS_1 — the GRANT flag and its scope, in one place.
    //
    // Scope is RULED (owner card 2026-09-13, the narrowest reading): faction 13 (the
    // relabelled vanilla Mechanoid faction, Faction.OfMechanoids — droid_ruling.md /
    // FACTION_SPEC.md §13), Cathedral ground only. "Cathedral ground" is a map whose
    // biome is one of the two Rust Cathedral BiomeDefs: RM_RustCathedral (the RM-tier
    // biome mod) or RUT_RustCathedral (the frozen UtinniPatches twin still carrying the
    // world until the terminal paint). Both are looked up by name so neither mod is a
    // hard dependency.
    //
    // The war lab is NOT in scope by construction: the pass only ever applies on a
    // Cathedral-biome map, and the antipode war lab is not one (arc §3, ashfall_research_base.md §6).
    //
    // Grant/Revoke are the public surface the GM-layer verbs will call once
    // CATHEDRAL_REGARD_BLACKBOARD_1 exists; that wiring is not built here.
    public static class CathedralPass
    {
        public static readonly string[] CathedralBiomeDefNames = { "RM_RustCathedral", "RUT_RustCathedral" };

        private static HashSet<BiomeDef> cathedralBiomes;

        public static HashSet<BiomeDef> CathedralBiomes
        {
            get
            {
                if (cathedralBiomes == null)
                {
                    cathedralBiomes = new HashSet<BiomeDef>();
                    foreach (string name in CathedralBiomeDefNames)
                    {
                        BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail(name);
                        if (b != null)
                        {
                            cathedralBiomes.Add(b);
                        }
                    }
                }
                return cathedralBiomes;
            }
        }

        public static bool IsCathedralMap(Map map)
        {
            return map != null && map.Biome != null && CathedralBiomes.Contains(map.Biome);
        }

        public static bool Holds(Pawn pawn)
        {
            return pawn?.health?.hediffSet != null
                && pawn.health.hediffSet.HasHediff(CathedralPassDefOf.RUT_CathedralPass);
        }

        // The pass is extended to the CLAN: only player-faction pawns can receive it.
        public static bool Grant(Pawn pawn)
        {
            if (pawn == null || pawn.Dead || pawn.Faction != Faction.OfPlayer || Holds(pawn))
            {
                return false;
            }
            pawn.health.AddHediff(CathedralPassDefOf.RUT_CathedralPass);
            return true;
        }

        public static bool Revoke(Pawn pawn)
        {
            Hediff h = pawn?.health?.hediffSet?.GetFirstHediffOfDef(CathedralPassDefOf.RUT_CathedralPass);
            if (h == null)
            {
                return false;
            }
            pawn.health.RemoveHediff(h);
            return true;
        }

        // Clan-wide forms for the GM verbs: the pass is granted to, and revoked from,
        // the clan as a whole. Returns how many pawns changed.
        public static int GrantToClan()
        {
            int n = 0;
            foreach (Pawn p in PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_OfPlayerFaction)
            {
                if (Grant(p))
                {
                    n++;
                }
            }
            return n;
        }

        public static int RevokeFromAll()
        {
            int n = 0;
            foreach (Pawn p in PawnsFinder.AllMapsWorldAndTemporary_Alive)
            {
                if (Revoke(p))
                {
                    n++;
                }
            }
            return n;
        }
    }
}
