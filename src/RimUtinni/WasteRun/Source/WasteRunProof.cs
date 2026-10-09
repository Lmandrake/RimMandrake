// WASTE_RUN_SIGNAL_DEBUG_HOOK_1 -- jawa/static_call hooks (type=RimMandrake.Utinni.WasteRun.WasteRunProof) so the waste run can
// be state-read without clicking: ProofGizmo reads whether the cask bay offers the command; ProofPress commits a destination
// through the SAME Commit path the confirm dialog's callback runs (destroys the bays' waste, sends the quest signal).
// ProofGizmo is a pure read. ProofPress MUTATES (irreversible, like the player's click): throwaway quicktest map only.
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.WasteRun
{
    public static class WasteRunProof
    {
        /// <summary>"master=B bays=N waste=N activeRun=questId|none state=.. gizmos=N label=.." Pure read.</summary>
        public static string ProofGizmo(string unused)
        {
            try
            {
                Quest q = WasteRunDisposal.ActiveRun(false);
                int bays = 0, gizmos = 0;
                string label = "none";
                foreach (var bay in WasteRunDisposal.CaskBays())
                {
                    bays++;
                    RUT_CompWasteRunPlanner comp = bay.GetComp<RUT_CompWasteRunPlanner>();
                    if (comp == null) continue;
                    foreach (Gizmo g in comp.CompGetGizmosExtra())
                    {
                        gizmos++;
                        if (g is Command c) label = c.defaultLabel;
                    }
                }
                return "master=" + WasteRunSettings.masterEnabled + " bays=" + bays + " waste=" + WasteRunDisposal.WasteInBays().Count
                    + " activeRun=" + (q == null ? "none" : q.id.ToString()) + " state=" + (q == null ? "n/a" : q.State.ToString())
                    + " gizmos=" + gizmos + " label=" + label
                    + " plannerCompOnBay=" + (WasteRunDisposal.CaskBays().Any(b => b.GetComp<RUT_CompWasteRunPlanner>() != null));
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }

        /// <summary>args = WasteDestination name (DropOnEmpire, FreezeColdSide, EntombAssailants, IgnitePropaneLake, SlimeExperiment).
        /// Returns "signal=.. stateBefore=.. stateAfter=.. wasteBefore=N wasteAfter=N". Needs an Ongoing waste-run quest.</summary>
        public static string ProofPress(string dest)
        {
            try
            {
                WasteDestination d;
                if (!System.Enum.TryParse(dest, out d)) return "ERROR unknown destination '" + dest + "'";
                Quest q = WasteRunDisposal.ActiveRun(true);
                if (q == null) return "ERROR no Ongoing waste-run quest (accept it first)";
                string before = q.State.ToString();
                int wasteBefore = WasteRunDisposal.WasteInBays().Count;
                RUT_CompWasteRunPlanner.Commit(q, d);
                return "signal=" + WasteRunKernel.FullSignal(q.id, d) + " stateBefore=" + before + " stateAfter=" + q.State
                    + " wasteBefore=" + wasteBefore + " wasteAfter=" + WasteRunDisposal.WasteInBays().Count;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }
    }
}
