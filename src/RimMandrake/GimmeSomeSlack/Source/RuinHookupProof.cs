using System.Collections.Generic;
using System.Text;
using RimMandrake.Shared.Slack;
using RimWorld;
using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES live proof (jawa/static_call, dev surface only; nothing in the game
    /// calls it; driver FlowWorks/prove_wrecked_links.py). A conduit run ending at every tagged wrecked def's footprint: the cord
    /// snapshot must hook its end into the ruin, as into the repaired tier, while the ruin holds no power comp and the conduit's
    /// net gains no connector or transmitter from it.</summary>
    public static class RuinHookupProof
    {
        private static bool Hooks(CordWorld w, string id, Cell end)
        {
            foreach (MachineInfo m in w.Machines)
                if (m.Id == id && m.Hookups.Contains(end)) return true;
            return false;
        }

        public static string Sweep(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no current map";
            ThingDef conduit = DefDatabase<ThingDef>.GetNamedSilentFail("PowerConduit");
            if (conduit == null || !ConduitVisuals.IsTarget(conduit)) return "REFUSED: PowerConduit is not a drawn cord target";
            bool ok = true;
            int n = 0;
            var sb = new StringBuilder();
            foreach (ThingDef ruinDef in ConduitVisuals.ConduitRuinDefs)
            {
                ThingDef fixedDef = null;
                foreach (string tier in new[] { "_Repaired", "_Refurbished", "_Kludged" })
                    fixedDef ??= DefDatabase<ThingDef>.GetNamedSilentFail(ruinDef.defName.Replace("_Wrecked", tier));
                if (fixedDef == null) { ok = false; sb.Append(" [" + ruinDef.defName + ": no repaired tier]"); continue; }
                IntVec3 at = Site(map, ruinDef.size);
                if (!at.IsValid) return "REFUSED: no clear site near the map centre";
                var made = new List<Thing>();
                try
                {
                    Thing Spawn(ThingDef d, IntVec3 c)
                    {
                        Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
                        // the player's own: an unowned FlowWorks ruin dresses itself with a pump and tank on first spawn
                        if (t.def.CanHaveFaction) t.SetFaction(Faction.OfPlayer);
                        t = GenSpawn.Spawn(t, c, map);
                        made.Add(t);
                        return t;
                    }
                    // the run ends one cell west of the footprint
                    IntVec3 endCell = new IntVec3(at.x - 1, 0, at.z);
                    var end = new Cell(endCell.x, endCell.z);
                    Thing endConduit = null;
                    for (int i = 0; i < 2; i++)
                    {
                        Thing c = Spawn(conduit, new IntVec3(endCell.x - i, 0, endCell.z));
                        if (i == 0) endConduit = c;
                    }
                    map.powerNetManager.UpdatePowerNetsAndConnections_First();
                    PowerNet net = endConduit.TryGetComp<CompPower>()?.PowerNet;
                    int connectors = net?.connectors.Count ?? -1, transmitters = net?.transmitters.Count ?? -1;
                    Thing ruin = Spawn(ruinDef, at);
                    map.powerNetManager.UpdatePowerNetsAndConnections_First();
                    bool ruinHooks = Hooks(CordWorldAdapter.Snapshot(map), "r" + ruin.thingIDNumber, end);
                    PowerNet after = endConduit.TryGetComp<CompPower>()?.PowerNet;
                    bool noNet = ruin.TryGetComp<CompPower>() == null && after != null
                        && after.connectors.Count == connectors && after.transmitters.Count == transmitters;
                    ruin.Destroy(DestroyMode.Vanish);
                    Thing mended = Spawn(fixedDef, at);
                    map.powerNetManager.UpdatePowerNetsAndConnections_First();
                    bool fixedHooks = Hooks(CordWorldAdapter.Snapshot(map), "c" + mended.thingIDNumber, end);
                    bool rowOk = net != null && ruinHooks && fixedHooks && noNet;
                    ok &= rowOk;
                    n++;
                    sb.Append(" [" + ruinDef.defName + " ruinHooks=" + ruinHooks + " repairedHooks=" + fixedHooks + " noNet=" + noNet + " ok=" + rowOk + "]");
                }
                finally
                {
                    foreach (Thing t in made)
                        if (!t.Destroyed) t.Destroy(DestroyMode.Vanish);
                    map.powerNetManager.UpdatePowerNetsAndConnections_First();
                }
            }
            return "RUINHOOKS ok=" + (ok && n > 0) + " n=" + n + sb;
        }

        private static IntVec3 Site(Map map, IntVec2 size)
        {
            foreach (IntVec3 q in GenRadial.RadialCellsAround(map.Center, 40f, true))
            {
                bool clear = true;
                for (int x = -3; x <= size.x + 1 && clear; x++)
                    for (int z = -2; z <= size.z + 1 && clear; z++)
                    {
                        IntVec3 c = new IntVec3(q.x + x, 0, q.z + z);
                        clear = c.InBounds(map) && c.Standable(map) && c.GetThingList(map).Count == 0;
                    }
                if (clear) return q;
            }
            return IntVec3.Invalid;
        }
    }
}
