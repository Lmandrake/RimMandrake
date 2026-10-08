using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Wreckage
{
    // SALVAGE_WRECKAGE_EVERYWHERE_1, design §3e: fresh wrecks are DELIVERED, not generated.
    // A named weighted wreck list, read by the wreck-fall incident here and meant to be read by
    // any other arrival (Miasma post-surge flotsam, the Cracked Lands flood strike) through
    // RM_WreckFall.Drop / RM_WreckListDef.PickWreck. Same element-name-as-key rows as a wreck
    // field (<RM_SomeWreck>1</RM_SomeWreck>), never a <li> form. ALL NUMBERS PROVISIONAL.
    public class RM_WreckListDef : Def
    {
        public List<RM_WreckFieldEntry> wrecks = new List<RM_WreckFieldEntry>();

        public IEnumerable<ThingDef> WreckDefs => wrecks.Where(w => w.thing != null && w.weight > 0f).Select(w => w.thing);

        public bool AnyWreck => wrecks.Any(w => w.thing != null && w.weight > 0f);

        public ThingDef PickWreck()
        {
            return AnyWreck
                ? wrecks.Where(w => w.thing != null && w.weight > 0f).RandomElementByWeight(w => w.weight).thing
                : null;
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (!AnyWreck)
            {
                yield return "no resolvable wreck with weight > 0";
            }
            foreach (RM_WreckFieldEntry w in wrecks)
            {
                if (w.thing != null && w.thing.category != ThingCategory.Building && w.thing.category != ThingCategory.Item)
                {
                    yield return w.thing.defName + " is neither a building nor an item; a skyfaller cannot land it";
                }
            }
        }
    }

    // Data for one wreck-fall IncidentDef. The worker is shared; each IncidentDef names its list,
    // its count and its skyfaller, so a biome layer adds a fall with XML only.
    public class RM_WreckFallExtension : DefModExtension
    {
        public RM_WreckListDef wreckList;

        // Design §3e: 1-4 wrecks per fall.
        public IntRange countRange = new IntRange(1, 4);

        // The incoming-wreck skyfaller; null means RM_WreckFallIncoming (no blast, shrapnel only).
        public ThingDef skyfaller;

        // The 2nd..Nth wreck lands within this many cells of the first ("fell together").
        public int spreadRadius = 5;

        // Optional gate: when set, the fall fires only on a map whose tile carries one of these
        // mutators (the Fall Line's own gate is a mutator, per its arrival spec §3.3).
        public List<TileMutatorDef> requiredMutators;

        public ThingDef Skyfaller => skyfaller ?? DefDatabase<ThingDef>.GetNamedSilentFail("RM_WreckFallIncoming");
    }

    public static class RM_WreckFall
    {
        public static bool MapAllowed(RM_WreckFallExtension ext, Map map)
        {
            if (map == null)
            {
                return false;
            }
            IList<TileMutatorDef> on = map.TileInfo?.Mutators;
            return RM_WreckageKernel.MapAllowed(true, ext.requiredMutators.NullOrEmpty() ? 0 : ext.requiredMutators.Count,
                on != null && !ext.requiredMutators.NullOrEmpty() && ext.requiredMutators.Any(m => on.Contains(m)));
        }

        public static bool TryFindCell(ThingDef skyfaller, ThingDef wreck, Map map, IntVec3 near, int nearMaxDist, out IntVec3 cell)
        {
            // Same finder as IncidentWorker_ShipChunkDrop (RimSage CellFinderLoose.cs:229), with
            // the wreck's own affordance (Walkable for every family, design §3a).
            return CellFinderLoose.TryFindSkyfallerCell(skyfaller, map, wreck.terrainAffordanceNeeded, out cell,
                10, near, nearMaxDist, allowRoofedCells: false, alwaysAvoidColonists: true);
        }

        // Drops count wrecks from list onto map, the first anywhere near the map centre, the rest
        // within spreadRadius of it. Returns how many skyfallers were spawned; firstCell is the
        // first one's cell (invalid when none). Callers other than the incident (flotsam, flood
        // strike) use this directly.
        public static int Drop(Map map, RM_WreckListDef list, int count, ThingDef skyfaller, int spreadRadius, out IntVec3 firstCell)
        {
            firstCell = IntVec3.Invalid;
            if (map == null || list == null || skyfaller == null || count <= 0)
            {
                return 0;
            }
            int dropped = 0;
            for (int i = 0; i < count; i++)
            {
                ThingDef wreck = list.PickWreck();
                if (wreck == null)
                {
                    break;
                }
                IntVec3 near = firstCell.IsValid ? firstCell : map.Center;
                int maxDist = firstCell.IsValid ? spreadRadius : 999999;
                if (!TryFindCell(skyfaller, wreck, map, near, maxDist, out IntVec3 cell))
                {
                    continue;
                }
                Thing thing = ThingMaker.MakeThing(wreck, wreck.MadeFromStuff ? GenStuff.DefaultStuffFor(wreck) : null);
                SkyfallerMaker.SpawnSkyfaller(skyfaller, thing, cell, map);
                if (!firstCell.IsValid)
                {
                    firstCell = cell;
                }
                dropped++;
            }
            return dropped;
        }
    }

    public class RM_IncidentWorker_WreckFall : IncidentWorker
    {
        private RM_WreckFallExtension Ext => def.GetModExtension<RM_WreckFallExtension>();

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms) || !RM_WreckageSettings.wreckFalls)
            {
                return false;
            }
            RM_WreckFallExtension ext = Ext;
            Map map = parms.target as Map;
            if (ext?.wreckList == null || ext.Skyfaller == null || !ext.wreckList.AnyWreck || !RM_WreckFall.MapAllowed(ext, map))
            {
                return false;
            }
            // Any listed wreck that can land is enough to fire.
            return ext.wreckList.WreckDefs.Any(w => RM_WreckFall.TryFindCell(ext.Skyfaller, w, map, map.Center, 999999, out _));
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            RM_WreckFallExtension ext = Ext;
            Map map = parms.target as Map;
            if (ext?.wreckList == null || map == null)
            {
                return false;
            }
            int n = RM_WreckFall.Drop(map, ext.wreckList, ext.countRange.RandomInRange, ext.Skyfaller, ext.spreadRadius, out IntVec3 first);
            if (n <= 0)
            {
                return false;
            }
            Messages.Message("RM_Wreckage_WreckFallMessage".Translate(), new TargetInfo(first, map), MessageTypeDefOf.NeutralEvent);
            return true;
        }
    }
}
