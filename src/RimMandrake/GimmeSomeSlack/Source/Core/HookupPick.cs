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
    }
}
