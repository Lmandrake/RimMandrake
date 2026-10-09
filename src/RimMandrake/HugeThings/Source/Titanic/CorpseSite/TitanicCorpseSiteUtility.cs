using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    public static class TitanicCorpseSiteUtility
    {
        /// <summary>The corpse a T3 titan leaves may become a site now: still spawned on this map, the feature on, and still T3.</summary>
        public static bool StillEligible(Corpse corpse, Map map)
        {
            if (corpse == null || corpse.Destroyed || !corpse.Spawned || corpse.Map != map) return false;
            if (!RM_HugeThingsSettings.CorpseSiteActive) return false;
            Pawn inner = corpse.InnerPawn;
            return inner != null && TitanicTierUtility.GetTier(inner) == TitanicTier.T3;
        }

        /// <summary>
        /// CORPSE_SITE_SAFETY_1 (B3.3): the site is an edifice, and GenSpawn wipes any destroyable edifice under its footprint. The
        /// whole rect must be in bounds and free of edifices, or the corpse stays an ordinary corpse.
        /// </summary>
        public static bool SiteFits(IntVec3 pos, Map map, ThingDef siteDef)
        {
            CellRect rect = GenAdj.OccupiedRect(pos, Rot4.North, siteDef.size);
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map) || c.GetEdifice(map) != null) return false;
            }
            return true;
        }

        /// <summary>
        /// Replaces a T3 titan's ordinary single-cell Corpse with the
        /// multi-cell Building_TitanicCorpseSite landmark, carrying over the
        /// exact yield vanilla would have produced (this pawn's real
        /// MeatAmount/LeatherAmount stats and race defs, not a guessed
        /// constant) so the site's harvest pool matches what this specific
        /// creature would have butchered for.
        /// CORPSE_SITE_SAFETY_1 (B3.3): the corpse is destroyed only after the site has actually spawned; a failed preflight or spawn
        /// keeps the corpse (returns false).
        /// </summary>
        public static bool ConvertToSite(Corpse corpse, Map map)
        {
            Pawn inner = corpse.InnerPawn;
            if (inner == null)
            {
                return false;
            }
            ThingDef siteDef = RM_TitanicCreaturesDefOf.RM_TitanicCorpseSite;
            IntVec3 pos = corpse.Position;
            if (!SiteFits(pos, map, siteDef))
            {
                return false;
            }
            string label = inner.LabelCap;
            ThingDef meatDef = inner.RaceProps.meatDef;
            int meatTotal = meatDef != null ? GenMath.RoundRandom(inner.GetStatValue(StatDefOf.MeatAmount)) : 0;
            ThingDef leatherDef = inner.RaceProps.leatherDef;
            int leatherTotal = leatherDef != null ? GenMath.RoundRandom(inner.GetStatValue(StatDefOf.LeatherAmount)) : 0;

            var site = (Building_TitanicCorpseSite)ThingMaker.MakeThing(siteDef);
            site.Setup(label, meatDef, meatTotal, leatherDef, leatherTotal);
            Thing spawned = GenSpawn.Spawn(site, pos, map, WipeMode.VanishOrMoveAside);
            if (spawned == null || !spawned.Spawned)
            {
                return false;
            }
            // Never an instant meat pile beside the landmark (ruling #4): the corpse goes once the site stands.
            if (!corpse.Destroyed)
            {
                corpse.Destroy();
            }
            return true;
        }
    }

    /// <summary>
    /// CORPSE_SITE_SAFETY_1 (B3.1): converting inside the corpse's own SpawnSetup destroyed it while 1.6 Pawn.Kill was still using it
    /// (forbid, CompRottable, lord.AddCorpse, DeathActionWorker, Notify_PawnDied). The patch only queues the corpse here; the
    /// conversion runs on a later tick after revalidating corpse, map, tier and settings. A corpse that cannot become a site
    /// (no room, edifice underneath) is left as an ordinary corpse and is not retried.
    /// </summary>
    public class MapComponent_TitanicCorpseSites : MapComponent
    {
        private List<Corpse> pending = new List<Corpse>();
        private readonly HashSet<int> refused = new HashSet<int>();

        public MapComponent_TitanicCorpseSites(Map map) : base(map)
        {
        }

        public void Enqueue(Corpse corpse)
        {
            if (corpse == null || refused.Contains(corpse.thingIDNumber) || pending.Contains(corpse)) return;
            pending.Add(corpse);
        }

        public override void MapComponentTick()
        {
            if (pending.Count == 0) return;
            List<Corpse> batch = pending;
            pending = new List<Corpse>();
            foreach (Corpse corpse in batch)
            {
                if (!TitanicCorpseSiteUtility.StillEligible(corpse, map)) continue;
                bool ok;
                try
                {
                    ok = TitanicCorpseSiteUtility.ConvertToSite(corpse, map);
                }
                catch (Exception e)
                {
                    ok = false;
                    Log.ErrorOnce("[RimMandrake.TitanicCreatures] corpse-site conversion threw; the corpse stays ordinary: " + e, 0x5171A1);
                }
                if (!ok && corpse != null)
                {
                    refused.Add(corpse.thingIDNumber);
                    Log.Warning("[RimMandrake.TitanicCreatures] " + corpse.LabelCap + " stays an ordinary corpse: no clear 4x4 for its site.");
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref pending, "pendingCorpseSites", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (pending == null) pending = new List<Corpse>();
                pending.RemoveAll(c => c == null);
            }
        }
    }
}
