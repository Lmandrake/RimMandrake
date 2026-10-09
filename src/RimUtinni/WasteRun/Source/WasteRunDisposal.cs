using System.Collections.Generic;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.WasteRun
{
    // Finds the active waste-run quest and the waste held in the player's cask bays.
    public static class WasteRunDisposal
    {
        public static Quest ActiveRun(bool ongoingOnly)
        {
            List<Quest> quests = Find.QuestManager.QuestsListForReading;
            for (int i = 0; i < quests.Count; i++)
            {
                Quest q = quests[i];
                if (q.root != null && q.root.defName == WasteRunKernel.QuestScriptDefName
                    && (q.State == QuestState.Ongoing || (!ongoingOnly && q.State == QuestState.NotYetAccepted)))
                {
                    return q;
                }
            }
            return null;
        }

        public static IEnumerable<Building_Storage> CaskBays()
        {
            ThingDef bayDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_CaskBay");
            if (bayDef == null) yield break;
            List<Map> maps = Find.Maps;
            for (int m = 0; m < maps.Count; m++)
            {
                if (!maps[m].IsPlayerHome) continue;
                List<Building> bays = maps[m].listerBuildings.AllBuildingsColonistOfDef(bayDef);
                for (int i = 0; i < bays.Count; i++)
                {
                    if (bays[i] is Building_Storage s) yield return s;
                }
            }
        }

        public static List<Thing> WasteInBays()
        {
            List<Thing> found = new List<Thing>();
            foreach (Building_Storage bay in CaskBays())
            {
                if (bay.slotGroup == null) continue;
                foreach (Thing t in bay.slotGroup.HeldThings)
                {
                    if (WasteRunKernel.IsWaste(t.def.defName)) found.Add(t);
                }
            }
            return found;
        }

        // Destroys every waste stack in every cask bay; returns the stack count.
        public static int DisposeAll()
        {
            List<Thing> waste = WasteInBays();
            for (int i = 0; i < waste.Count; i++)
            {
                if (!waste[i].Destroyed) waste[i].Destroy();
            }
            return waste.Count;
        }
    }

    public class RUT_CompProperties_WasteRunPlanner : CompProperties
    {
        public RUT_CompProperties_WasteRunPlanner()
        {
            compClass = typeof(RUT_CompWasteRunPlanner);
        }
    }

    // Added to RM_CaskBay by Patches/RUT_CaskBay_WasteRunPlanner.xml. While a waste run is
    // Ongoing and the bays hold waste, the bay offers one command per enabled destination.
    public class RUT_CompWasteRunPlanner : ThingComp
    {
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (!WasteRunSettings.masterEnabled || parent.Faction != Faction.OfPlayer) yield break;
            Quest quest = WasteDisposalQuest();
            if (quest == null) yield break;
            yield return new Command_Action
            {
                defaultLabel = "Waste run: choose destination",
                defaultDesc = "Haul everything in the cask bays to a destination and be done with it. Every destination is a verdict; the choice cannot be taken back.",
                icon = parent.def.uiIcon,
                action = delegate { OpenMenu(quest); }
            };
        }

        private static Quest WasteDisposalQuest()
        {
            Quest q = WasteRunDisposal.ActiveRun(true);
            return q != null && WasteRunDisposal.WasteInBays().Count > 0 ? q : null;
        }

        private static void OpenMenu(Quest quest)
        {
            List<FloatMenuOption> options = new List<FloatMenuOption>();
            foreach (WasteDestination d in System.Enum.GetValues(typeof(WasteDestination)))
            {
                if (!WasteRunSettings.DestinationEnabled(d)) continue;
                WasteDestination dest = d;
                options.Add(new FloatMenuOption(WasteRunKernel.Label(dest), delegate
                {
                    Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                        WasteRunKernel.Label(dest) + "? This cannot be undone.",
                        delegate { Commit(quest, dest); }, destructive: true));
                }));
            }
            if (options.Count > 0) Find.WindowStack.Add(new FloatMenu(options));
        }

        internal static void Commit(Quest quest, WasteDestination dest)
        {
            if (quest.State != QuestState.Ongoing) return;
            WasteRunDisposal.DisposeAll();
            Find.SignalManager.SendSignal(new Signal(WasteRunKernel.FullSignal(quest.id, dest)));
        }
    }

    // Offers the run only when a cask bay really holds waste.
    public class RUT_IncidentWorker_WasteRunOffer : IncidentWorker_GiveQuest
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms)) return false;
            return WasteRunKernel.CanOffer(WasteRunSettings.masterEnabled, WasteRunSettings.offerEnabled,
                WasteRunDisposal.WasteInBays().Count, WasteRunDisposal.ActiveRun(false) != null);
        }
    }

    // Stores a faction found by FactionDef defName in the slate. Quest generation aborts
    // when it is absent (the Empire destroyed), so the run is simply never offered then.
    public class RUT_QuestNode_GetFactionByDef : QuestNode
    {
        [NoTranslate]
        public SlateRef<string> storeAs;
        public SlateRef<string> factionDefName;

        protected override bool TestRunInt(Slate slate)
        {
            Faction f = Lookup(slate);
            if (f == null) return false;
            slate.Set(storeAs.GetValue(slate), f);
            return true;
        }

        protected override void RunInt()
        {
            Faction f = Lookup(QuestGen.slate);
            if (f != null) QuestGen.slate.Set(storeAs.GetValue(QuestGen.slate), f);
        }

        private Faction Lookup(Slate slate)
        {
            string name = factionDefName.GetValue(slate);
            foreach (Faction f in Find.FactionManager.AllFactionsListForReading)
            {
                if (f.def.defName == name && !f.defeated) return f;
            }
            return null;
        }
    }
}
