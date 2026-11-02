using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.LanternDeeps
{
    // DEEP_LAYER_BELT_HARNESS_1: the Deep-only proofs (creep, aurora, collapse, slick, knocker, hush, sipper, tapper,
    // pooler) read their map components off Find.CurrentMap, and those components exist only on a pocket map
    // generated from RM_LanternDeepGenerator (customMapComponents). No bridge verb opens a pocket map, so this does
    // it the player's way minus the walk: find or spawn the RM_LanternDeepMineshaft MapPortal on the current map and
    // ask it for its other map (vanilla MapPortal.GetOtherMap generates the pocket map on first call), then make the
    // Deep current. Called through jawa/static_call by validation.py and prove_deep_harness.py.
    public static class RM_DeepHarness
    {
        public const string PortalDef = "RM_LanternDeepMineshaft";

        // thingIDs of the portals this harness spawned; LeaveDeep removes only these, never a scattered mineshaft.
        private static readonly HashSet<int> spawnedPortals = new HashSet<int>();

        public static bool IsDeep(Map map)
        {
            return map != null && map.GetComponent<RM_MapComponent_DeepCollapse>() != null;
        }

        // arg "furnish" also stands a charged player battery and a fuelled torch lamp in the Deep, which the tapper
        // and sipper proofs need. Idempotent: on a Deep it only furnishes; a portal already on the map is reused.
        public static string EnterDeep(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "no map";
            }
            bool furnish = arg != null && arg.Contains("furnish");
            if (IsDeep(map))
            {
                return Describe("already", map, furnish ? Furnish(map) : "");
            }
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(PortalDef);
            if (def == null)
            {
                return "no def " + PortalDef;
            }
            MapPortal portal = map.listerThings.ThingsOfDef(def).OfType<MapPortal>().FirstOrDefault();
            if (portal == null)
            {
                IntVec3 at = PortalCell(map, def);
                if (!at.IsValid)
                {
                    return "no clear " + def.size.x + "x" + def.size.z + " cell for the portal";
                }
                portal = GenSpawn.Spawn(ThingMaker.MakeThing(def), at, map) as MapPortal;
                if (portal == null)
                {
                    return "portal spawned but is not a MapPortal (thingClass " + def.thingClass + ")";
                }
                spawnedPortals.Add(portal.thingIDNumber);
            }
            Map deep = portal.GetOtherMap();
            if (deep == null || deep == map)
            {
                return "portal at " + portal.Position + " generated no pocket map";
            }
            Current.Game.CurrentMap = deep;
            return Describe("entered", deep, furnish ? Furnish(deep) : "") + " source=" + map.uniqueID + " portal=" + portal.Position;
        }

        // Makes the source map current again and destroys the Deep (and any portal the harness spawned there). arg
        // "keep" leaves the pocket map alive.
        public static string LeaveDeep(string arg)
        {
            Map map = Find.CurrentMap;
            if (!IsDeep(map))
            {
                return "not a Deep";
            }
            Map source = (map.Parent as PocketMapParent)?.sourceMap;
            if (source == null)
            {
                return "Deep has no source map";
            }
            Current.Game.CurrentMap = source;
            if (arg != null && arg.Contains("keep"))
            {
                return "left (kept) current=" + source.uniqueID;
            }
            int deepId = map.uniqueID;
            PocketMapUtility.DestroyPocketMap(map);
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(PortalDef);
            int portals = 0;
            if (def != null)
            {
                foreach (Thing t in source.listerThings.ThingsOfDef(def).Where(t => spawnedPortals.Contains(t.thingIDNumber)).ToList())
                {
                    spawnedPortals.Remove(t.thingIDNumber);
                    t.Destroy(DestroyMode.Vanish);
                    portals++;
                }
            }
            return "left current=" + source.uniqueID + " destroyed=" + deepId + " stillListed=" + Find.Maps.Any(m => m.uniqueID == deepId)
                + " portalsRemoved=" + portals;
        }

        private static string Describe(string verb, Map map, string furnished)
        {
            string comps = string.Join(",", new[]
            {
                map.GetComponent<RM_MapComponent_Creep>() != null ? "Creep" : null,
                map.GetComponent<RM_MapComponent_DeepAurora>() != null ? "Aurora" : null,
                map.GetComponent<RM_MapComponent_DeepCollapse>() != null ? "Collapse" : null,
                map.GetComponent<MapComponent_LanternDeepDarkness>() != null ? "Darkness" : null,
            }.Where(s => s != null));
            return verb + " deep=" + map.uniqueID + " biome=" + map.Biome?.defName + " pocket=" + map.IsPocketMap
                + " size=" + map.Size.x + "x" + map.Size.z + " comps=" + comps + (furnished.Length > 0 ? " " + furnished : "");
        }

        private static IntVec3 PortalCell(Map map, ThingDef def)
        {
            IntVec3 near = map.mapPawns.FreeColonistsSpawned.Select(p => p.Position).FirstOrDefault();
            if (!near.IsValid || near == IntVec3.Zero)
            {
                near = map.Center;
            }
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, 40f, true))
            {
                if (FootprintClear(map, c, def.size))
                {
                    return c;
                }
            }
            return IntVec3.Invalid;
        }

        private static bool FootprintClear(Map map, IntVec3 c, IntVec2 size)
        {
            CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, size).ExpandedBy(1);
            if (!rect.InBounds(map))
            {
                return false;
            }
            foreach (IntVec3 x in rect)
            {
                if (!x.Standable(map) || x.Fogged(map) || x.GetEdifice(map) != null || x.GetFirstPawn(map) != null
                    || x.GetThingList(map).Any(t => t.def.category == ThingCategory.Building || t.def.category == ThingCategory.Item))
                {
                    return false;
                }
            }
            return true;
        }

        // A charged colony battery and a lit torch lamp on open ground near the Deep's centre.
        private static string Furnish(Map map)
        {
            var parts = new List<string>();
            parts.Add("battery=" + Stand(map, "Battery", t =>
            {
                t.TryGetComp<CompPowerBattery>()?.SetStoredEnergyPct(1f);
            }));
            parts.Add("torch=" + Stand(map, "TorchLamp", t =>
            {
                CompRefuelable fuel = t.TryGetComp<CompRefuelable>();
                if (fuel != null)
                {
                    fuel.Refuel(fuel.Props.fuelCapacity);
                }
            }));
            return string.Join(" ", parts);
        }

        private static string Stand(Map map, string defName, System.Action<Thing> ready)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (def == null)
            {
                return "nodef";
            }
            if (map.listerThings.ThingsOfDef(def).Any(t => t.Faction == Faction.OfPlayer))
            {
                foreach (Thing have in map.listerThings.ThingsOfDef(def).Where(t => t.Faction == Faction.OfPlayer))
                {
                    ready(have);
                }
                return "had";
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 25, c => FootprintClear(map, c, def.size), out IntVec3 at))
            {
                return "nocell";
            }
            Thing t2 = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            t2.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(t2, at, map);
            ready(t2);
            return at.ToString();
        }
    }
}
