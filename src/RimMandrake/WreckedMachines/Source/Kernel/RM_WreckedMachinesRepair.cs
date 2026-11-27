// Verse-free kernel of the repair on the machine (bar repair_on_the_machine; rules R_uninstall_cancels, R_ground, R_signal): the repair
// record that a machine holds while it is under repair, and every transition of it. The mod's comp (CompWreckedMachine) holds one record
// and calls these functions for each act; it saves the record with Save/Load below. SelfTest/RepairWalk.cs compiles this file alone and
// walks every state and event against a fake game (python3 src/RimMandrake/Utils/selftest_wreckedmachines_repair_walk.py).
// Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib: a `using Verse;` here breaks the self-test build, which is the guard rail.
//
// The three statements the walk reads (models.md, Repair state walk):
//   a cancel never loses the machine          Cancel and Uninstall give back every delivered unit and change no level
//   the level changes only on complete work   Work is the one function that returns a level change, and only from the Working phase
//   the signal fires once for each change     the caller raises one signal for each RM_LevelChange with `changed` set; nothing else does
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace RimMandrake.WreckedMachines
{
    /// <summary>What a machine under repair holds. `phase` None means no repair; the other fields are then empty.</summary>
    public sealed class RM_RepairRecord
    {
        public int phase;
        /// <summary>The level this repair leads to (RM_WreckedMachinesKernel.Kludged or Refurbished).</summary>
        public int target;
        public string[] defs = new string[0];
        public int[] need = new int[0];
        public int[] delivered = new int[0];
        public float workDone, workTotal;
    }

    /// <summary>The one result that changes a machine's level. The caller swaps the machine and raises one signal when `changed` is set.</summary>
    public struct RM_LevelChange
    {
        public bool changed;
        public int from, to;
    }

    public static class RM_WreckedMachinesRepair
    {
        /// <summary>Phases: no repair; ordered, materials still to come; every material in, work under way.</summary>
        public const int None = 0, Ordered = 1, Working = 2;

        /// <summary>Why a repair order is not offered or not available, as flags. The first four take the order off the machine;
        /// the last three leave it on the machine, unavailable, and the order's text names each one.</summary>
        public const int NoHigherLevel = 1, LineOff = 2, Carried = 4, UnderRepair = 8, Research = 16, Ground = 32, Component = 64;

        public static bool Active(RM_RepairRecord r)
        {
            return r != null && r.phase != None;
        }

        /// <summary>Every reason against a new order on this machine now. `projectFinished`: the restoration project of the next level.
        /// `groundOk`: the machine stands on the ground that the next level needs. `componentAtHand`: the colony holds every scarce
        /// part that the next repair needs (only read when `needsComponent`).</summary>
        public static int OrderBlocks(int level, bool lineOn, bool standing, RM_RepairRecord rec, bool projectFinished, bool groundOk,
            bool needsComponent, bool componentAtHand)
        {
            int b = 0;
            if (level < RM_WreckedMachinesKernel.Wrecked || level >= RM_WreckedMachinesKernel.Refurbished) b |= NoHigherLevel;
            if (!lineOn) b |= LineOff;
            if (!standing) b |= Carried;
            if (Active(rec)) b |= UnderRepair;
            if (!projectFinished) b |= Research;
            if (!groundOk) b |= Ground;
            if (needsComponent && !componentAtHand) b |= Component;
            return b;
        }

        /// <summary>The player sees the order on the machine (it may still be unavailable).</summary>
        public static bool OrderOffered(int blocks)
        {
            return (blocks & (NoHigherLevel | LineOff | Carried | UnderRepair)) == 0;
        }

        public static bool OrderAvailable(int blocks)
        {
            return blocks == 0;
        }

        /// <summary>Give the order: fills `rec` and returns true, or changes nothing and returns false (a block, or a cost that makes no
        /// sense). An entry with a count of zero is left out; a repair that needs no material starts in the Working phase.</summary>
        public static bool Order(int level, int blocks, RM_RepairRecord rec, IList<string> defs, IList<int> counts, float workTotal)
        {
            if (rec == null || blocks != 0 || defs == null || counts == null || defs.Count != counts.Count) return false;
            var d = new List<string>();
            var n = new List<int>();
            for (int i = 0; i < defs.Count; i++)
            {
                if (counts[i] < 0 || string.IsNullOrEmpty(defs[i]) || d.Contains(defs[i])) return false;
                if (counts[i] == 0) continue;
                d.Add(defs[i]);
                n.Add(counts[i]);
            }
            rec.target = level + 1;
            rec.defs = d.ToArray();
            rec.need = n.ToArray();
            rec.delivered = new int[d.Count];
            rec.workDone = 0f;
            rec.workTotal = !(workTotal >= 1f) ? 1f : workTotal;      // also catches NaN
            rec.phase = d.Count == 0 ? Working : Ordered;
            return true;
        }

        /// <summary>How many more of `def` the repair still takes (0 for a def it does not use, or when no delivery is open).</summary>
        public static int Missing(RM_RepairRecord rec, string def)
        {
            if (rec == null || rec.phase != Ordered) return 0;
            int i = Array.IndexOf(rec.defs, def);
            return i < 0 ? 0 : rec.need[i] - rec.delivered[i];
        }

        /// <summary>Put `count` of `def` into the repair. Returns how many it took; the rest stays with the hauler. The last unit moves
        /// the repair to the Working phase. `siteOk`: the line is on, the machine stands, and its ground is the next level's.</summary>
        public static int Deliver(RM_RepairRecord rec, string def, int count, bool siteOk)
        {
            if (!siteOk || count <= 0) return 0;
            int take = Math.Min(count, Missing(rec, def));
            if (take <= 0) return 0;
            rec.delivered[Array.IndexOf(rec.defs, def)] += take;
            bool all = true;
            for (int i = 0; i < rec.need.Length; i++) all &= rec.delivered[i] >= rec.need[i];
            if (all) rec.phase = Working;
            return take;
        }

        /// <summary>Add work. The one place a level changes: when the work is complete the materials are used up, the record is emptied
        /// and the change is returned. Work on a repair that is not in the Working phase, or on a site that is not ok, does nothing.</summary>
        public static RM_LevelChange Work(int level, RM_RepairRecord rec, float amount, bool siteOk)
        {
            var none = new RM_LevelChange { changed = false, from = level, to = level };
            if (rec == null || rec.phase != Working || !siteOk || !(amount > 0f)) return none;
            if (rec.target != level + 1) return none;         // a record that does not belong to this level never moves it
            rec.workDone += amount;
            if (rec.workDone < rec.workTotal) return none;
            int to = rec.target;
            Clear(rec);
            return new RM_LevelChange { changed = true, from = level, to = to };
        }

        /// <summary>Cancel: every delivered unit comes back (def, count), the work done is lost, the level does not change.</summary>
        public static List<KeyValuePair<string, int>> Cancel(RM_RepairRecord rec)
        {
            var back = new List<KeyValuePair<string, int>>();
            if (rec == null) return back;
            for (int i = 0; i < rec.defs.Length; i++)
                if (rec.delivered[i] > 0) back.Add(new KeyValuePair<string, int>(rec.defs[i], rec.delivered[i]));
            Clear(rec);
            return back;
        }

        /// <summary>An uninstall order (rule R_uninstall_cancels): a machine that may be moved cancels its repair first and gives the
        /// materials back; one that may not be moved refuses, and its repair goes on.</summary>
        public static bool Uninstall(RM_RepairRecord rec, bool movable, out List<KeyValuePair<string, int>> back)
        {
            back = movable ? Cancel(rec) : new List<KeyValuePair<string, int>>();
            return movable;
        }

        private static void Clear(RM_RepairRecord rec)
        {
            rec.phase = None;
            rec.target = 0;
            rec.defs = new string[0];
            rec.need = new int[0];
            rec.delivered = new int[0];
            rec.workDone = 0f;
            rec.workTotal = 0f;
        }

        public static string LevelName(int level)
        {
            switch (level)
            {
                case RM_WreckedMachinesKernel.Wrecked: return "Wrecked";
                case RM_WreckedMachinesKernel.Kludged: return "Kludged";
                case RM_WreckedMachinesKernel.Refurbished: return "Refurbished";
                case RM_WreckedMachinesKernel.Original: return "Original";
                default: return "none";
            }
        }

        public static string PhaseName(RM_RepairRecord rec)
        {
            return !Active(rec) ? "none" : rec.phase == Ordered ? "ordered" : "working";
        }

        /// <summary>The line the mod's proof type answers for Repair(thing), and the walk prints for the same state.</summary>
        public static string ProofLine(RM_RepairRecord rec)
        {
            var sb = new StringBuilder("REPAIR ").Append(PhaseName(rec));
            if (!Active(rec)) return sb.Append(" | next none | delivered  | work 0/0").ToString();
            sb.Append(" | next ").Append(LevelName(rec.target)).Append(" | delivered ");
            bool first = true;
            for (int i = 0; i < rec.defs.Length; i++)
            {
                if (rec.delivered[i] <= 0) continue;
                if (!first) sb.Append(',');
                sb.Append(rec.defs[i]).Append(':').Append(rec.delivered[i]);
                first = false;
            }
            sb.Append(" | work ").Append(((int)rec.workDone).ToString(CultureInfo.InvariantCulture)).Append('/')
              .Append(((int)rec.workTotal).ToString(CultureInfo.InvariantCulture));
            return sb.ToString();
        }

        /// <summary>The record as one line of text, which is how the comp saves it. Load(Save(r)) is r.</summary>
        public static string Save(RM_RepairRecord rec)
        {
            if (!Active(rec)) return "";
            var sb = new StringBuilder();
            sb.Append(rec.phase).Append('|').Append(rec.target).Append('|')
              .Append(rec.workDone.ToString("R", CultureInfo.InvariantCulture)).Append('|')
              .Append(rec.workTotal.ToString("R", CultureInfo.InvariantCulture)).Append('|');
            for (int i = 0; i < rec.defs.Length; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append(rec.defs[i]).Append(':').Append(rec.need[i]).Append(':').Append(rec.delivered[i]);
            }
            return sb.ToString();
        }

        /// <summary>Read a saved record. Text that is empty or does not parse gives an empty record (no repair) and `ok` false for the
        /// second: a damaged save loses the repair order, never the machine.</summary>
        public static RM_RepairRecord Load(string text, out bool ok)
        {
            var rec = new RM_RepairRecord();
            ok = true;
            if (string.IsNullOrEmpty(text)) return rec;
            try
            {
                string[] p = text.Split('|');
                if (p.Length != 5) throw new FormatException();
                int phase = int.Parse(p[0], CultureInfo.InvariantCulture), target = int.Parse(p[1], CultureInfo.InvariantCulture);
                float done = float.Parse(p[2], CultureInfo.InvariantCulture), total = float.Parse(p[3], CultureInfo.InvariantCulture);
                string[] rows = p[4].Length == 0 ? new string[0] : p[4].Split(',');
                var defs = new string[rows.Length];
                var need = new int[rows.Length];
                var del = new int[rows.Length];
                bool all = true;
                for (int i = 0; i < rows.Length; i++)
                {
                    string[] f = rows[i].Split(':');
                    if (f.Length != 3 || f[0].Length == 0) throw new FormatException();
                    defs[i] = f[0];
                    need[i] = int.Parse(f[1], CultureInfo.InvariantCulture);
                    del[i] = int.Parse(f[2], CultureInfo.InvariantCulture);
                    if (need[i] <= 0 || del[i] < 0 || del[i] > need[i]) throw new FormatException();
                    all &= del[i] == need[i];
                }
                if ((phase != Ordered && phase != Working) || (phase == Working) != all || !(total >= 1f) || !(done >= 0f) || done >= total
                    || (target != RM_WreckedMachinesKernel.Kludged && target != RM_WreckedMachinesKernel.Refurbished))
                    throw new FormatException();
                rec.phase = phase;
                rec.target = target;
                rec.workDone = done;
                rec.workTotal = total;
                rec.defs = defs;
                rec.need = need;
                rec.delivered = del;
            }
            catch (Exception)
            {
                ok = false;
                return new RM_RepairRecord();
            }
            return rec;
        }
    }
}
