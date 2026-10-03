using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // A trigger watches for one kind of evidence. Subjects are named as STRINGS and
    // resolved at runtime with GetNamedSilentFail, so an entry whose subject's mod is
    // absent loads clean and reads "absent from this world" instead of logging a
    // cross-reference error.
    //
    // Durable facts (a thing on the map, terrain laid, research done, a layer
    // visited, a rung reached) are POLLED by GameComponent_Atlas, which also
    // backfills them when the mod is added to a running save. Transient acts arrive
    // as signals (AtlasTrigger_Signal) or through Atlas.Notify. Polling only ever
    // reads game state; the Atlas never advances another mod's state (design §4,
    // note on entries 12 and 15).
    public abstract class AtlasTrigger
    {
        // True when the poll is costly (a terrain scan) and runs on the slow cadence.
        public virtual bool Expensive => false;

        // False when none of the trigger's subjects exist in this game.
        public abstract bool Available { get; }

        public virtual void ResolveReferences() { }

        public virtual IEnumerable<string> ConfigErrors() { yield break; }

        // Poll: is the evidence present right now?
        public virtual bool Check() => false;

        // Signal / Notify path.
        public virtual bool MatchesSignal(string tag) => false;

        protected static IEnumerable<Map> PlayerMaps()
        {
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                Map m = maps[i];
                if (m == null) continue;
                // A map exists in Find.Maps because the player is there (home,
                // camp, quest site, gravship landing). Every one is a place the
                // clan can see.
                yield return m;
            }
        }

        protected static List<T> Resolve<T>(List<string> names) where T : Def
        {
            var outList = new List<T>();
            if (names == null) return outList;
            foreach (string n in names)
            {
                T d = DefDatabase<T>.GetNamedSilentFail(n);
                if (d != null) outList.Add(d);
            }
            return outList;
        }
    }

    // SEEN: a thing of one of these defs is spawned on any player map in an
    // unfogged cell. Covers creatures (their race ThingDef), plants, buildings,
    // items. playerFactionOnly narrows to things the player owns (built or tamed).
    public class AtlasTrigger_ThingSeen : AtlasTrigger
    {
        public List<string> things = new List<string>();
        public bool playerFactionOnly;
        public int minCount = 1;

        private List<ThingDef> resolved;

        public override bool Available => !Resolved.NullOrEmpty();

        private List<ThingDef> Resolved => resolved ?? (resolved = Resolve<ThingDef>(things));

        public override IEnumerable<string> ConfigErrors()
        {
            if (things.NullOrEmpty()) yield return "AtlasTrigger_ThingSeen with no things";
        }

        public override bool Check()
        {
            List<ThingDef> defs = Resolved;
            if (defs.Count == 0) return false;
            foreach (Map map in PlayerMaps())
            {
                int found = 0;
                for (int d = 0; d < defs.Count; d++)
                {
                    List<Thing> list = map.listerThings.ThingsOfDef(defs[d]);
                    for (int i = 0; i < list.Count; i++)
                    {
                        Thing t = list[i];
                        if (!t.Spawned) continue;
                        if (map.fogGrid.IsFogged(t.Position)) continue;
                        if (playerFactionOnly && t.Faction != Faction.OfPlayer) continue;
                        if (++found >= minCount) return true;
                    }
                }
            }
            return false;
        }
    }

    // USED: a terrain the player made (a canal fill, a sealant pour) is laid on a
    // player map. Scans the terrain grid, so it runs on the slow cadence.
    public class AtlasTrigger_TerrainPresent : AtlasTrigger
    {
        public List<string> terrains = new List<string>();
        public bool unfoggedOnly = true;

        private HashSet<TerrainDef> resolved;

        public override bool Expensive => true;

        private HashSet<TerrainDef> Resolved
            => resolved ?? (resolved = new HashSet<TerrainDef>(Resolve<TerrainDef>(terrains)));

        public override bool Available => Resolved.Count > 0;

        public override IEnumerable<string> ConfigErrors()
        {
            if (terrains.NullOrEmpty()) yield return "AtlasTrigger_TerrainPresent with no terrains";
        }

        public override bool Check()
        {
            HashSet<TerrainDef> set = Resolved;
            if (set.Count == 0) return false;
            foreach (Map map in PlayerMaps())
            {
                TerrainGrid grid = map.terrainGrid;
                foreach (IntVec3 c in map.AllCells)
                {
                    if (!set.Contains(grid.TerrainAt(c))) continue;
                    if (unfoggedOnly && map.fogGrid.IsFogged(c)) continue;
                    return true;
                }
            }
            return false;
        }
    }

    // USED/PERFORMED: any one of these research projects is finished (studied
    // techprints and found-rite inscriptions are research rows in our mods).
    public class AtlasTrigger_ResearchFinished : AtlasTrigger
    {
        public List<string> projects = new List<string>();

        private List<ResearchProjectDef> resolved;
        private List<ResearchProjectDef> Resolved => resolved ?? (resolved = Resolve<ResearchProjectDef>(projects));

        public override bool Available => !Resolved.NullOrEmpty();

        public override bool Check()
        {
            foreach (ResearchProjectDef p in Resolved)
                if (p.IsFinished) return true;
            return false;
        }
    }

    // OBSERVED: a hidden-until-discovered thing has been revealed by its own
    // authority (ShipMemory's containment gate). The Atlas never calls
    // SetDiscovered itself. Hidden() is false for defs the manager does not track,
    // so the def must declare hiddenWhileUndiscovered or this never fires.
    public class AtlasTrigger_HiddenItemDiscovered : AtlasTrigger
    {
        public string thing;

        private ThingDef resolved;
        private bool looked;

        private ThingDef Resolved
        {
            get
            {
                if (!looked) { resolved = DefDatabase<ThingDef>.GetNamedSilentFail(thing); looked = true; }
                return resolved;
            }
        }

        public override bool Available => Resolved != null && Resolved.hiddenWhileUndiscovered;

        public override bool Check()
        {
            ThingDef d = Resolved;
            if (d == null || !d.hiddenWhileUndiscovered) return false;
            return !Find.HiddenItemsManager.Hidden(d);
        }
    }

    // SEEN/PERFORMED: the player has a map on this planet layer (the gravship
    // landed on the sea floor, an orbit, ...).
    public class AtlasTrigger_PlanetLayer : AtlasTrigger
    {
        public string layer;

        public override bool Available => DefDatabase<PlanetLayerDef>.GetNamedSilentFail(layer) != null;

        public override bool Check()
        {
            foreach (Map map in PlayerMaps())
            {
                PlanetLayerDef d = map.Tile.LayerDef;
                if (d != null && d.defName == layer) return true;
            }
            return false;
        }
    }

    // LIVED THROUGH: a game condition is active on a player map, or world-wide.
    public class AtlasTrigger_GameCondition : AtlasTrigger
    {
        public List<string> conditions = new List<string>();

        private List<GameConditionDef> resolved;
        private List<GameConditionDef> Resolved => resolved ?? (resolved = Resolve<GameConditionDef>(conditions));

        public override bool Available => !Resolved.NullOrEmpty();

        public override bool Check()
        {
            foreach (GameConditionDef c in Resolved)
            {
                if (Find.World?.gameConditionManager != null && Find.World.gameConditionManager.ConditionIsActive(c))
                    return true;
                foreach (Map map in PlayerMaps())
                    if (map.gameConditionManager.ConditionIsActive(c)) return true;
            }
            return false;
        }
    }

    // LIVED THROUGH: the current weather on a player map is one of these.
    public class AtlasTrigger_Weather : AtlasTrigger
    {
        public List<string> weathers = new List<string>();

        private List<WeatherDef> resolved;
        private List<WeatherDef> Resolved => resolved ?? (resolved = Resolve<WeatherDef>(weathers));

        public override bool Available => !Resolved.NullOrEmpty();

        public override bool Check()
        {
            List<WeatherDef> ws = Resolved;
            foreach (Map map in PlayerMaps())
                if (ws.Contains(map.weatherManager.curWeather)) return true;
            return false;
        }
    }

    // A pawn of the player's faction carries one of these hediffs.
    public class AtlasTrigger_Hediff : AtlasTrigger
    {
        public List<string> hediffs = new List<string>();

        private List<HediffDef> resolved;
        private List<HediffDef> Resolved => resolved ?? (resolved = Resolve<HediffDef>(hediffs));

        public override bool Available => !Resolved.NullOrEmpty();

        public override bool Check()
        {
            List<HediffDef> hs = Resolved;
            foreach (Map map in PlayerMaps())
            {
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < pawns.Count; i++)
                {
                    Pawn p = pawns[i];
                    if (p.health?.hediffSet == null) continue;
                    for (int h = 0; h < hs.Count; h++)
                        if (p.health.hediffSet.HasHediff(hs[h])) return true;
                }
            }
            return false;
        }
    }

    // PERFORMED: a signal whose tag ends with `tag` was sent, or a mod called
    // Atlas.Notify(tag). Match by EndsWith, because quest signals are prefixed with
    // the quest's own id (the ShipMemory precedent).
    public class AtlasTrigger_Signal : AtlasTrigger
    {
        public string tag;
        public string requiresPackageId;

        public override bool Available
            => !tag.NullOrEmpty() && (requiresPackageId.NullOrEmpty() || ModsConfig.IsActive(requiresPackageId));

        public override IEnumerable<string> ConfigErrors()
        {
            if (tag.NullOrEmpty()) yield return "AtlasTrigger_Signal with no tag";
        }

        public override bool MatchesSignal(string signalTag)
            => !tag.NullOrEmpty() && signalTag != null && signalTag.EndsWith(tag);
    }

    // PERFORMED: a LoreStages reveal ladder (mandrake.rm.lorestages) has reached
    // at least `minStage`. `ladder` is the table's ladderId (RUT_ScarlandsLadder's
    // is "Scarlands"), not its defName. Read by reflection (AtlasCompat), so the
    // Atlas carries no hard dependency.
    public class AtlasTrigger_LoreStage : AtlasTrigger
    {
        public string ladder;
        public int minStage = 1;
        public string requiresPackageId;

        public override bool Available
            => AtlasCompat.LoreStagesAvailable && !ladder.NullOrEmpty()
               && (requiresPackageId.NullOrEmpty() || ModsConfig.IsActive(requiresPackageId));

        public override bool Check() => AtlasCompat.LoreStageOf(ladder) >= minStage;
    }

    // PERFORMED: one of the nine has unveiled itself (mandrake.rm.ninefold's
    // first-contact chain). `god` is the RimMandrake.Ninefold.God enum name:
    // Ishko, Ohm, Oomo, MobUnloo, Rekko, TaBaa, Zizzik, Shkaar, Ozzik.
    public class AtlasTrigger_GodUnveiled : AtlasTrigger
    {
        public string god;

        public override bool Available => AtlasCompat.GodNameValid(god);

        public override bool Check() => AtlasCompat.IsUnveiled(god);
    }
}
