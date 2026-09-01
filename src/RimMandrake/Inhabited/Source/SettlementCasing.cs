using System.Collections.Generic;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// What the colony now knows about a settlement -- SETTLEMENT_VISIT_LOOP_1.
    ///
    /// Deliberately NOT full map state. A settlement's actual map is destroyed
    /// on departure exactly like a wilderness Inhabited place (Patch_MapRemoval
    /// recalls the roster and the map itself is gone). "Casing" is the residue:
    /// the small, cheap facts a return visit can read WITHOUT holding the whole
    /// map in memory -- how many times we have been here, which district labels
    /// were composed last time, and whether the gate has ever searched us.
    ///
    /// Held on WorldObject_InhabitedSettlement and deep-scribed with it, the same
    /// pattern InhabitedStock uses for a small IExposable sub-tracker.
    /// </summary>
    public class SettlementCasing : IExposable
    {
        /// <summary>True after the first arrival. A second visit reads this
        /// rather than re-deriving "have we been here" from anything else.</summary>
        public bool everVisited;

        /// <summary>Game tick of the most recent arrival. -1 if never.</summary>
        public int lastVisitTick = -1;

        /// <summary>How many times the colony has arrived here.</summary>
        public int visitCount;

        /// <summary>District labels composed on past visits, most recent last.
        /// Duplicates are not stored -- this is "what we know exists", not a
        /// visit log.</summary>
        public List<string> knownDistrictLabels = new List<string>();

        /// <summary>Whether the gate has ever actually been observed searching
        /// leavers here. Distinct from the manifest's own securityProfile field:
        /// that is the true rule, this is what the colony has SEEN.</summary>
        public bool searchesLeaversObserved;

        /// <summary>The last observed outcome, valid only if searchesLeaversObserved.</summary>
        public bool knownSearchesLeavers;

        /// <summary>Record an arrival. Called once per map generation, from the
        /// compose step -- arrival and compose are one beat in the lifecycle.</summary>
        public void RecordArrival(int tick)
        {
            everVisited = true;
            visitCount++;
            lastVisitTick = tick;
        }

        /// <summary>Record that a district label was composed on this visit.</summary>
        public void RecordDistrictComposed(string label)
        {
            if (label.NullOrEmpty())
            {
                return;
            }
            if (!knownDistrictLabels.Contains(label))
            {
                knownDistrictLabels.Add(label);
            }
        }

        /// <summary>Record the outcome of a departure-time gate-search check.</summary>
        public void RecordGateSearch(bool searched)
        {
            searchesLeaversObserved = true;
            knownSearchesLeavers = searched;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref everVisited, "everVisited", false);
            Scribe_Values.Look(ref lastVisitTick, "lastVisitTick", -1);
            Scribe_Values.Look(ref visitCount, "visitCount", 0);
            Scribe_Collections.Look(ref knownDistrictLabels, "knownDistrictLabels", LookMode.Value);
            Scribe_Values.Look(ref searchesLeaversObserved, "searchesLeaversObserved", false);
            Scribe_Values.Look(ref knownSearchesLeavers, "knownSearchesLeavers", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && knownDistrictLabels == null)
            {
                knownDistrictLabels = new List<string>();
            }
        }
    }
}
