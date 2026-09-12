using RimWorld;
using Verse;

namespace RimMandrake.Utinni.KyberTradePlot
{
    // KYBER_TRADE_PLOT_1 — the deterministic trigger for both quests
    // (RUT_KyberHomesteadVisit, RUT_KyberDonationSmuggle) ships as a baseChance-0
    // GiveQuest incident (same idiom as StructureInjectionsRUT's
    // RUT_GiveQuest_VaultThaw_*), so this class exists for exactly one reason:
    // read the Mod Settings toggle (KyberTradePlotSettings.kyberTradePlotEnabled)
    // before a dev-mode/bridge/GM-layer caller can force either quest, since an
    // XML-only IncidentDef has no field that reads a C# static. No Harmony —
    // this is this mod's OWN IncidentDef's workerClass, set directly in the def,
    // the same no-Harmony subclass idiom UtinniPatches' AmbientShrineGuardians.cs
    // and GeothermalDensityField.cs already use.
    //
    // base.CanFireNowSub (IncidentWorker_GiveQuest, read via rimsage) already
    // gates on QuestScriptDef.CanRun, tile eligibility, and "some colonist or
    // caravan exists somewhere" — none of that is duplicated here.
    public class IncidentWorker_GiveQuest_KyberTradePlot : IncidentWorker_GiveQuest
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!KyberTradePlotSettings.kyberTradePlotEnabled)
            {
                return false;
            }
            return base.CanFireNowSub(parms);
        }
    }
}
