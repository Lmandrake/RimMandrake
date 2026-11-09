using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>GSS_CORD_SILENCE_PHANTOM_SPARK (owner 2026-10-16, FW station carry_tanks: "you show one cable going all the
    /// way. But then you draw a second cable that acts disconnected as well."). Vanilla wires a connector to whichever
    /// transmitter it found when it spawned (often a battery, when the conduit came later) and never re-wires it, so a
    /// conduit run can end right beside the machine it powers while the machine's connectParent is somewhere else. Drawing
    /// only the connectParent left that conduit end free: a second, sparking cord. Rule: a connector whose connectParent cell
    /// is not under or beside it, but which has a same-net conduit END (at most one conduit neighbour) under or beside its
    /// footprint, hooks that end instead -- one cord into the machine. A parent conduit that is itself an end stays hooked
    /// too, so the swap never strands it. Verse-free so the selftest runs the production rule.</summary>
    public static class HookupPick
    {
        /// <summary>Cells under the footprint, then the cardinal ring around it, in a fixed order.</summary>
        internal static List<Cell> Touching(MachineInfo m)
        {
            var res = new List<Cell>();
            for (int x = m.X0; x < m.X0 + m.W; x++)
                for (int z = m.Z0; z < m.Z0 + m.H; z++) res.Add(new Cell(x, z));
            for (int x = m.X0; x < m.X0 + m.W; x++) { res.Add(new Cell(x, m.Z0 - 1)); res.Add(new Cell(x, m.Z0 + m.H)); }
            for (int z = m.Z0; z < m.Z0 + m.H; z++) { res.Add(new Cell(m.X0 - 1, z)); res.Add(new Cell(m.X0 + m.W, z)); }
            return res;
        }

        internal static int Degree(CordWorld w, Cell c)
        {
            int n = 0;
            foreach (Cell d in Cell.Dirs4)
            {
                Cell q = c + d;
                if (w.IsConduit(q) && (w.LinkAllowed == null || w.LinkAllowed(c, q))) n++;
            }
            return n;
        }

        /// <summary>Hookup cells for a connector, or null = keep the vanilla-derived wiring. parentCell: the connectParent's
        /// conduit cell (null when the parent is a battery/switch building). sameNet: is this conduit cell on the connector's
        /// own power net.</summary>
        internal static List<Cell> Pick(CordWorld w, MachineInfo m, Cell? parentCell, Func<Cell, bool> sameNet)
        {
            List<Cell> touching = Touching(m);
            if (parentCell.HasValue && touching.Contains(parentCell.Value)) return null;
            foreach (Cell c in touching)
            {
                if (!w.IsConduit(c) || Degree(w, c) > 1 || (sameNet != null && !sameNet(c))) continue;
                var res = new List<Cell> { c };
                if (parentCell.HasValue && w.IsConduit(parentCell.Value) && Degree(w, parentCell.Value) <= 1) res.Add(parentCell.Value);
                return res;
            }
            return null;
        }

        /// <summary>A building that carries power itself (a battery, a generator, a switch) joins every conduit it touches, but a conduit running along its side is one line, not
        /// many (seen in a lived-in colony 2026-11-07: seven cords and a row of strips into one solar panel, the owner's "multiple cables for no reason"). From what it touches: every
        /// conduit END, since a free end beside it would spark; and for a run with no end there, one cell. Two separate runs each keep their cord, because this building is what joins them.
        /// <paramref name="runs"/> is filled once per snapshot, cell to run number.</summary>
        internal static List<Cell> PickCarrier(CordWorld w, IList<Cell> touching, ref Dictionary<Cell, int> runs)
        {
            var res = new List<Cell>();
            if (touching.Count <= 1) { res.AddRange(touching); return res; }
            var served = new HashSet<int>();
            foreach (Cell c in touching)
                if (Degree(w, c) <= 1) { res.Add(c); served.Add(RunOf(w, c, ref runs)); }
            foreach (Cell c in touching)
                if (served.Add(RunOf(w, c, ref runs))) res.Add(c);
            return res;
        }

        private static int RunOf(CordWorld w, Cell c, ref Dictionary<Cell, int> runs)
        {
            runs = runs ?? new Dictionary<Cell, int>();
            if (runs.TryGetValue(c, out int id)) return id;
            id = runs.Count;
            runs[c] = id;
            var open = new Stack<Cell>();
            open.Push(c);
            while (open.Count > 0)
            {
                Cell q = open.Pop();
                foreach (Cell d in Cell.Dirs4)
                {
                    Cell n = q + d;
                    if (w.IsConduit(n) && (w.LinkAllowed == null || w.LinkAllowed(q, n)) && !runs.ContainsKey(n)) { runs[n] = id; open.Push(n); }
                }
            }
            return id;
        }

        /// <summary>Round 3 (owner 2026-11-08 5:18 PM: "solar panels that are connected but no connection is drawn"): vanilla joins buildings that carry
        /// power (PowerNetMaker.ContiguousPowerBuildings, decompiled 1.6) by cardinal adjacency of their footprints, so a solar panel or battery set
        /// against another one is on its net with no conduit of its own. A transmitter building (adapter id "t...") touching no conduit links to a drawn
        /// transmitter it touches, breadth-first so a row of them chains. Idempotent; returns how many links it added.</summary>
        internal static int ChainTransmitters(IList<MachineInfo> ms)
        {
            bool T(MachineInfo m) => m.Id != null && m.Id.StartsWith("t", StringComparison.Ordinal);
            var drawn = new HashSet<MachineInfo>();
            foreach (MachineInfo m in ms) if (m.Hookups.Count > 0 || m.MachineLinks.Count > 0) drawn.Add(m);
            int n = 0;
            for (bool grew = true; grew;)
            {
                grew = false;
                foreach (MachineInfo m in ms)
                {
                    if (drawn.Contains(m) || !T(m)) continue;
                    MachineInfo to = null;
                    foreach (MachineInfo o in ms) if (o != m && drawn.Contains(o) && T(o) && Touch(m, o)) { to = o; break; }
                    if (to == null) continue;
                    m.MachineLinks.Add(to.Id); drawn.Add(m); grew = true; n++;
                }
            }
            return n;
        }

        /// <summary>Do two footprints share an edge (vanilla's cardinal adjacency, not a corner)?</summary>
        internal static bool Touch(MachineInfo a, MachineInfo b)
        {
            bool ox = a.X0 < b.X0 + b.W && b.X0 < a.X0 + a.W, oz = a.Z0 < b.Z0 + b.H && b.Z0 < a.Z0 + a.H;
            bool tx = a.X0 + a.W == b.X0 || b.X0 + b.W == a.X0, tz = a.Z0 + a.H == b.Z0 || b.Z0 + b.H == a.Z0;
            return (oz && tx) || (ox && tz);
        }

        /// <summary>WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES (owner 2026-11-06: "they should ALL draw in the piping and conduit
        /// the same way"): the hookup cells of a wrecked machine, which has no power comp, no connectParent and no net. Only a
        /// conduit under or beside its footprint draws in, one cord per conduit run: the run's first END touching the ruin (so no
        /// free end sparks in the gap), else its first touching cell. Null when no conduit touches it.</summary>
        internal static List<Cell> PickRuin(CordWorld w, MachineInfo m)
        {
            List<Cell> touching = Touching(m);
            List<Cell> res = null;
            var seen = new HashSet<Cell>();
            foreach (Cell c in touching)
            {
                if (!w.IsConduit(c) || seen.Contains(c)) continue;
                var run = new HashSet<Cell> { c };
                var open = new Stack<Cell>();
                open.Push(c);
                while (open.Count > 0)
                {
                    Cell q = open.Pop();
                    foreach (Cell d in Cell.Dirs4)
                    {
                        Cell n = q + d;
                        if (w.IsConduit(n) && (w.LinkAllowed == null || w.LinkAllowed(q, n)) && run.Add(n)) open.Push(n);
                    }
                }
                seen.UnionWith(run);
                Cell pick = c;
                foreach (Cell t in touching)
                {
                    if (run.Contains(t) && Degree(w, t) <= 1) { pick = t; break; }
                }
                (res ??= new List<Cell>()).Add(pick);
            }
            return res;
        }
    }
}
