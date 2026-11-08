using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// Herds reach the rare water one at a time, not all on one day. The fire cast is grass-watered (owner, 2026-11-07: "MOSTLY
    /// grass-watered with a very, very slow building thirst need to occasionally increase their density near the rare water";
    /// Patches/RM_Pyrelands_NativesSlowThirst.xml puts FlowWorks' RM_ThirstGrassWateredExtension on the cast). But FlowWorks
    /// starts every need at the same level (RM_ThirstMath.InitialLevel 0.8) and the cast's need falls at the same slow rate, so
    /// on map s (2026-11-07) all 43 natives read thirst 0.72 three days in: every herd on the map would have left for the
    /// pond on the same day, about 19 days after landing (ThirstyBelow 0.3), and again about 27 days after that.
    ///
    /// So each wild herd on a Pyrelands map gets ONE random starting thirst, once: animals of the same kind within HerdRadius
    /// of each other share it, so a herd walks to the water together and the visits spread over the cycle (about one herd
    /// every few days on a map with seven or eight). A herd that lands below ThirstyBelow drinks on the first day. Nothing
    /// here touches the rate, the threshold or dehydration (the extension still keeps an empty native alive).
    ///
    /// FlowWorks stays optional: the need is found by defName and a native without it is skipped. Checked every
    /// CheckIntervalTicks, so a herd that migrates in later is staggered within the hour it arrives.
    /// </summary>
    public class MapComponent_PyrelandsHerdThirst : MapComponent
    {
        private const int CheckIntervalTicks = 2500;
        private const float HerdRadius = 10f;
        /// <summary>Lowest starting level. Just under FlowWorks' ThirstyBelow (0.3), so about one herd in ten drinks on day one.</summary>
        private const float LevelMin = 0.22f;
        private const string GrassWateredExtension = "RM_ThirstGrassWateredExtension";

        private HashSet<int> staggered = new HashSet<int>();
        private List<int> savedIds;
        private static NeedDef thirstDef;
        private static bool resolved;

        public MapComponent_PyrelandsHerdThirst(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 37) return;
            if (!PyrelandsMechanicsGate.On || map.Biome == null || map.Biome.defName != "RM_Pyrelands") return;
            if (!resolved)
            {
                resolved = true;
                thirstDef = DefDatabase<NeedDef>.GetNamedSilentFail("RM_Thirst");
            }
            if (thirstDef == null) return;

            List<Pawn> fresh = null;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Faction != null || p.RaceProps == null || !p.RaceProps.Animal || p.Dead) continue;
                if (staggered.Contains(p.thingIDNumber) || !GrassWatered(p.def)) continue;
                (fresh ?? (fresh = new List<Pawn>())).Add(p);
            }
            if (fresh == null) return;

            float radiusSq = HerdRadius * HerdRadius;
            for (int i = 0; i < fresh.Count; i++)
            {
                Pawn lead = fresh[i];
                if (staggered.Contains(lead.thingIDNumber)) continue;
                float level = Rand.Range(LevelMin, 1f);
                for (int j = i; j < fresh.Count; j++)
                {
                    Pawn q = fresh[j];
                    if (q.def != lead.def || staggered.Contains(q.thingIDNumber)) continue;
                    if ((q.Position - lead.Position).LengthHorizontalSquared > radiusSq) continue;
                    Need n = q.needs?.TryGetNeed(thirstDef);
                    if (n != null) n.CurLevel = level;
                    staggered.Add(q.thingIDNumber);
                }
            }
        }

        private static bool GrassWatered(ThingDef def)
        {
            List<DefModExtension> ext = def.modExtensions;
            if (ext == null) return false;
            for (int i = 0; i < ext.Count; i++)
            {
                if (ext[i] != null && ext[i].GetType().Name == GrassWateredExtension) return true;
            }
            return false;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                // Only the animals still here: the dead and the departed would pile up over a long game.
                savedIds = new List<int>();
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
                {
                    if (staggered.Contains(p.thingIDNumber)) savedIds.Add(p.thingIDNumber);
                }
            }
            Scribe_Collections.Look(ref savedIds, "rmPyreHerdThirstStaggered", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                staggered = savedIds != null ? new HashSet<int>(savedIds) : new HashSet<int>();
                savedIds = null;
            }
        }
    }
}
