using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.LanternDeeps
{
    /// <summary>
    /// The Deep's collapse-warning bookkeeping, with no Verse type in it so the offline fuzz
    /// (`python3 src/RimMandrake/Utils/selftest_lanterndeeps_fuzz.py`) compiles THIS file. Cells are generic (IntVec3 in the
    /// game). RM_MapComponent_DeepCollapse owns one of these, Scribes its <c>due</c> and <c>forced</c> fields under their own
    /// names, and does the engine side (marking the roof buffer, the warning effects) from what these methods return.
    ///
    /// The cycle: vanilla marks a roof cell to collapse -> <see cref="Filter"/> pulls it out of the marked list and gives it a
    /// warning window (<c>due</c>) -> when the window ends <see cref="Resolve"/> drops it if it is still roofed and unsupported
    /// (or was brought down by force), putting it in <c>released</c> so the resolver the component then re-runs lets it
    /// through without a second warning -> <see cref="EndRelease"/> clears whatever that run did not consume.
    /// </summary>
    public sealed class DeepCollapseState<T>
    {
        public Dictionary<T, int> due = new Dictionary<T, int>();
        public HashSet<T> released = new HashSet<T>();
        /// <summary>Cells brought down by force (a galuush blast): they fall when the warning ends, propped or not.</summary>
        public HashSet<T> forced = new HashSet<T>();

        public int Pending => due.Count;

        /// <summary>
        /// After a load: repair null collections, and drop forced marks that are not pending. Vanilla's roof buffer is not saved,
        /// so a forced cell whose marking was lost (a save between the blast and the filter, or a save made while warnings were
        /// off by an older build) would otherwise make a later, unrelated collapse there ignore its supports.
        /// </summary>
        public void EnsureNotNull()
        {
            if (due == null) due = new Dictionary<T, int>();
            if (forced == null) forced = new HashSet<T>();
            if (released == null) released = new HashSet<T>();
            forced.RemoveWhere(c => !due.ContainsKey(c));
        }

        public void MarkForced(T c)
        {
            forced.Add(c);
        }

        /// <summary>Warning window: the setting's ticks, lengthened by a tame knocker.</summary>
        public static int Window(int baseTicks, bool tameKnocker, float knockerFactor)
        {
            return (int)(baseTicks * (tameKnocker ? knockerFactor : 1f));
        }

        /// <summary>
        /// Vanilla's marked list, filtered in place: cells a previous <see cref="Resolve"/> released stay marked (and are consumed
        /// from <c>released</c>); every other cell is removed and given a window ending at now + window (an already pending cell
        /// keeps its original deadline). Returns true if any cell is newly pending (the caller warns).
        /// </summary>
        public bool Filter(List<T> marked, int now, int window)
        {
            bool fresh = false;
            for (int i = marked.Count - 1; i >= 0; i--)
            {
                T c = marked[i];
                if (released.Remove(c))
                {
                    continue;
                }
                if (!due.ContainsKey(c))
                {
                    due[c] = now + window;
                    fresh = true;
                }
                marked.RemoveAt(i);
            }
            return fresh;
        }

        /// <summary>
        /// Vanilla is about to collapse these cells WITHOUT a warning (warnings switched off, or map generation's roof removal).
        /// They are gone, so neither a pending window nor a forced mark may outlive them: a forced mark left behind would
        /// make a later, unrelated collapse of a rebuilt roof at that cell ignore its supports.
        /// </summary>
        public void PassThrough(List<T> marked)
        {
            for (int i = 0; i < marked.Count; i++)
            {
                forced.Remove(marked[i]);
                due.Remove(marked[i]);
            }
        }

        /// <summary>The pending cells whose window has ended.</summary>
        public List<T> Ripe(int now)
        {
            return due.Where(kv => kv.Value <= now).Select(kv => kv.Key).ToList();
        }

        public struct Resolution
        {
            public List<T> fell;      // to mark and collapse
            public int held;          // roof gone already or propped: nothing falls
        }

        /// <summary>A window ended: the cell falls if it is still roofed and (forced or unsupported); otherwise it is held.</summary>
        public Resolution Resolve(List<T> ripe, Func<T, bool> roofed, Func<T, bool> supported)
        {
            Resolution r = new Resolution { fell = new List<T>() };
            foreach (T c in ripe)
            {
                due.Remove(c);
                bool force = forced.Remove(c);
                if (roofed(c) && (force || !supported(c)))
                {
                    released.Add(c);
                    r.fell.Add(c);
                }
                else
                {
                    r.held++;
                }
            }
            return r;
        }

        /// <summary>
        /// Called after the resolver has been re-run for the released cells. Whatever it did not consume (the engine skipped the
        /// prefix: warnings switched off, map generation) must not wave a later, unrelated marking through without its warning.
        /// </summary>
        public void EndRelease()
        {
            released.Clear();
        }

        /// <summary>The warnings are switched off: every pending cell is due now.</summary>
        public List<T> DueAll()
        {
            List<T> all = due.Keys.ToList();
            foreach (T c in all)
            {
                due[c] = 0;
            }
            return all;
        }
    }
}
