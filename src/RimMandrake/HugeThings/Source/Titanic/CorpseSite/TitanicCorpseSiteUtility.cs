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
        /// whole rect must be in bounds and empty except for the source corpse; otherwise conversion stays pending.
        /// </summary>
        public static bool SiteFits(IntVec3 pos, Map map, ThingDef siteDef, Corpse source = null)
        {
            CellRect rect = GenAdj.OccupiedRect(pos, Rot4.North, siteDef.size);
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map) || c.GetEdifice(map) != null) return false;
                foreach (Thing thing in c.GetThingList(map))
                    if (thing != source) return false;
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
            if (!StillEligible(corpse, map)) return false;
            Pawn inner = corpse.InnerPawn;
            if (inner == null)
            {
                return false;
            }
            ThingDef siteDef = RM_TitanicCreaturesDefOf.RM_TitanicCorpseSite;
            IntVec3 pos = corpse.Position;
            if (!SiteFits(pos, map, siteDef, corpse))
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
            // Do not spawn an edifice over the corpse: remove it temporarily, then restore it on failure.
            // Nothing else occupies the preflighted rect; GenSpawn therefore has nothing surrounding it to wipe.
            corpse.DeSpawn();
            try
            {
                GenSpawn.Spawn(site, pos, map, WipeMode.VanishOrMoveAside);
            }
            catch
            {
                if (site.Spawned) site.Destroy();
                throw;
            }
            finally
            {
                if (!site.Spawned && !corpse.Destroyed && !corpse.Spawned)
                    GenSpawn.Spawn(corpse, pos, map, WipeMode.VanishOrMoveAside);
            }
            if (!site.Spawned) return false;
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
    /// conversion runs on a later tick after revalidation. Failed placement remains queued and persisted; ordinary T3
    /// butcher products are gated independently, so lack of room cannot bypass the site-only harvest contract.
    /// </summary>
    public class MapComponent_TitanicCorpseSites : MapComponent
    {
        private List<Corpse> pending = new List<Corpse>();
        private int cursor;
        private int nextRetryTick;
        private const int RetryInterval = 250;

        public MapComponent_TitanicCorpseSites(Map map) : base(map) { }

        public void Enqueue(Corpse corpse)
        {
            if (corpse == null || pending.Contains(corpse)) return;
            pending.Add(corpse);
            nextRetryTick = 0;
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            // Include old saves which never recorded pending conversion, as well as references restored by Scribe.
            foreach (Thing thing in map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse))
                if (thing is Corpse corpse && TitanicCorpseSiteUtility.StillEligible(corpse, map)) Enqueue(corpse);
        }

        public override void MapComponentTick()
        {
            if (!RM_HugeThingsSettings.CorpseSiteActive || pending.Count == 0 || Find.TickManager.TicksGame < nextRetryTick) return;
            if (cursor >= pending.Count) cursor = 0;
            Corpse corpse = pending[cursor];
            // Unspawned corpses can be in a holder or caravan: retain the reference until they return to this map.
            bool remove = corpse == null || corpse.Destroyed;
            if (!remove && TitanicCorpseSiteUtility.StillEligible(corpse, map))
            {
                try { remove = TitanicCorpseSiteUtility.ConvertToSite(corpse, map); }
                catch (Exception e)
                {
                    Log.ErrorOnce("[RimMandrake.TitanicCreatures] corpse-site conversion failed; remains pending: " + e, 0x5171A1);
                }
            }
            if (remove) pending.RemoveAt(cursor);
            else cursor++;
            // One attempt per tick; wait between complete rounds of the remaining queue.
            if (cursor >= pending.Count) { cursor = 0; nextRetryTick = Find.TickManager.TicksGame + RetryInterval; }
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
