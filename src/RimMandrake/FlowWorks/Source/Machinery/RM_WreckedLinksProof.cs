using System.Collections.Generic;
using System.Text;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES live proof (jawa/static_call, dev surface only; nothing in the game
    /// calls it; driver FlowWorks/prove_wrecked_links.py). A pipe beside every tagged wrecked def's footprint: its link mask
    /// must equal the same pipe's beside that def's repaired tier and differ from the same pipe alone, and the ruin must hold no
    /// net role and no power comp.</summary>
    public static class RM_WreckedLinksProof
    {
        private static readonly List<Thing> shown = new List<Thing>();

        private static ThingDef PipeDef => DefDatabase<ThingDef>.GetNamedSilentFail(PipeStyles.PipeDef);

        /// <summary>The player's own: an unowned ruin would dress itself with a stolen-goods pump and tank on first spawn
        /// (CompLiquidWorksRuin), which this proof would leave behind.</summary>
        private static Thing Spawn(ThingDef d, IntVec3 at, Map map)
        {
            Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
            if (t.def.CanHaveFaction) t.SetFaction(Faction.OfPlayer);
            return GenSpawn.Spawn(t, at, map);
        }

        private static ThingDef MendedTier(ThingDef ruin)
        {
            foreach (string tier in new[] { "_Repaired", "_Refurbished", "_Kludged" })
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(ruin.defName.Replace("_Wrecked", tier));
                if (d != null) return d;
            }
            return null;
        }

        /// <summary>The first clear block of size+margin round the map centre, for a footprint origin; Invalid when none.</summary>
        private static IntVec3 Site(Map map, IntVec2 size)
        {
            foreach (IntVec3 q in GenRadial.RadialCellsAround(map.Center, 40f, true))
            {
                bool clear = true;
                for (int x = -2; x <= size.x + 1 && clear; x++)
                    for (int z = -2; z <= size.z + 1 && clear; z++)
                    {
                        IntVec3 c = new IntVec3(q.x + x, 0, q.z + z);
                        clear = c.InBounds(map) && c.Standable(map) && c.GetThingList(map).Count == 0;
                    }
                if (clear) return q;
            }
            return IntVec3.Invalid;
        }

        /// <summary>The sweep, spawning and destroying within this call. "RUINLINKS ok=b n=k [def: ...]..."</summary>
        public static string Sweep(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no current map";
            if (!RM_MachinerySettings.pipeLinksIntoMachines) return "REFUSED: pipeLinksIntoMachines is off";
            ThingDef pipeDef = PipeDef;
            if (pipeDef == null) return "REFUSED: the universal pipe is not loaded";
            bool ok = true;
            int n = 0;
            var sb = new StringBuilder();
            foreach (ThingDef ruinDef in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (ruinDef.building?.buildingTags == null || !ruinDef.building.buildingTags.Contains(RM_LiquidJoins.RuinPipeTag)) continue;
                ThingDef fixedDef = MendedTier(ruinDef);
                IntVec3 at = Site(map, ruinDef.size);
                if (!at.IsValid) return "REFUSED: no clear site near the map centre";
                if (fixedDef == null) { ok = false; sb.Append(" [" + ruinDef.defName + ": no repaired tier]"); continue; }
                var made = new List<Thing>();
                try
                {
                    IntVec3 pipeAt = new IntVec3(at.x - 1, 0, at.z);
                    Thing pipe = Spawn(pipeDef, pipeAt, map);
                    made.Add(pipe);
                    int alone = RM_LiquidJoins.LinkMask(pipe);
                    Thing ruin = Spawn(ruinDef, at, map);
                    made.Add(ruin);
                    int mask = RM_LiquidJoins.LinkMask(pipe);
                    bool partner = RM_LiquidJoins.PartnerAt(pipeAt + IntVec3.East, map) == ruin;
                    bool noNet = RM_LiquidNet.RoleOfKind(ruin) == RM_NetRole.None && RM_LiquidNet.RoleOfThing(ruin) == RM_NetRole.None
                        && ruin.TryGetComp<CompPower>() == null;
                    ruin.Destroy(DestroyMode.Vanish);
                    Thing mended = Spawn(fixedDef, at, map);
                    made.Add(mended);
                    int repaired = RM_LiquidJoins.LinkMask(pipe);
                    bool rowOk = alone >= 0 && mask == repaired && mask != alone && partner && noNet;
                    ok &= rowOk;
                    n++;
                    sb.Append(" [" + ruinDef.defName + " alone=" + alone + " ruin=" + mask + " repaired=" + repaired + " partner=" + partner + " noNet=" + noNet + " ok=" + rowOk + "]");
                }
                finally
                {
                    foreach (Thing t in made)
                        if (!t.Destroyed) t.Destroy(DestroyMode.Vanish);
                }
            }
            return "RUINLINKS ok=" + (ok && n > 0) + " n=" + n + sb;
        }

        /// <summary>For the capture: "show" stages the wrecked pump with a pipe run and a conduit run ending at its footprint and
        /// answers "SHOWN x,z,w,h"; "clear" destroys them. The driver takes the picture between the two calls.</summary>
        public static string Stage(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no current map";
            foreach (Thing t in shown)
                if (!t.Destroyed) t.Destroy(DestroyMode.Vanish);
            shown.Clear();
            if (arg != "show") return "CLEARED";
            ThingDef ruinDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_PumpingStation_Wrecked");
            ThingDef conduit = DefDatabase<ThingDef>.GetNamedSilentFail("PowerConduit");
            if (ruinDef == null || conduit == null || PipeDef == null) return "REFUSED: a staged def is not loaded";
            // room for the ruin, three pipe cells on its west, three conduit cells on its east
            IntVec3 q = Site(map, new IntVec2(ruinDef.size.x + 6, ruinDef.size.z));
            if (!q.IsValid) return "REFUSED: no clear site near the map centre";
            IntVec3 at = new IntVec3(q.x + 3, 0, q.z);
            shown.Add(Spawn(ruinDef, at, map));
            for (int i = 1; i <= 3; i++)
            {
                shown.Add(Spawn(PipeDef, new IntVec3(at.x - i, 0, at.z), map));
                shown.Add(Spawn(conduit, new IntVec3(at.x + ruinDef.size.x - 1 + i, 0, at.z), map));
            }
            return "SHOWN " + (at.x - 3) + "," + at.z + "," + (ruinDef.size.x + 6) + "," + ruinDef.size.z;
        }
    }
}
