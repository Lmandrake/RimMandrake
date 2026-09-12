using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // VAULT_THAW_QUEST_FAMILY_1: the C# gap named in
    // design/Jawa/worldbuilding/vault_thaw_quest_family.md SS5, finding #1.
    // No vanilla QuestPart observes a Building_AncientCryptosleepCasket
    // opening or breaking, and Site.AllEnemiesDefeated fires at arrival on a
    // threat-free map -- so RUT_VaultThaw_V6_Umbra's WAKE and LOOT branches
    // (inSignal site.RUT_SleepersWoken / site.RUT_SleepersLooted, already in
    // the shipped XML) were wired but inert; only LEAVE could fire.
    //
    // This MapComponent is the sender the doc asked for. It does not invent a
    // new mechanic -- it watches the two events vanilla ALREADY models on an
    // AncientCryptosleepCasket and translates whichever happens first into
    // the exact signal string the quest is already listening for:
    //
    //   ejected while the casket survives (Building_Casket.EjectContents,
    //   called either by a colonist's Open job or by combat damage via
    //   Building_AncientCryptosleepCasket.PreApplyDamage) -- the sleepers are
    //   out and hostile, i.e. WOKEN.
    //
    //   the casket itself is destroyed before ever ejecting its contents --
    //   the sleepers went down with it, i.e. LOOTED (the design's chosen
    //   reading: "kills them, plainly").
    //
    // contentsKnown is a protected field on Building_Casket, so it cannot be
    // read from here; HasAnyContents (public) plus Destroyed gives the same
    // two states without needing a patch. No Harmony: only a MapComponent
    // (auto-instantiated per map by the engine, same as
    // GameComponent_WarLabCrater's GameComponent sibling) and public API.
    //
    // Scope: only maps whose Site carries RUT_VaultSite_Type3 (the frozen
    // vault) and has quest tags at all -- i.e. only a live
    // RUT_VaultThaw_V6_Umbra site map runs the watch; every other map no-ops
    // on the first eligibility check and never looks again.
    public class MapComponent_VaultSleepers : MapComponent
    {
        private const string VaultSitePartDefName = "RUT_VaultSite_Type3";
        private const string WokenSignal = "RUT_SleepersWoken";
        private const string LootedSignal = "RUT_SleepersLooted";
        private const int CheckIntervalTicks = 60; // ~1 game second

        private bool checkedEligibility;
        private bool eligible;
        private bool gatheredCaskets;
        private bool resolved; // WAKE or LOOT already sent -- watch is done
        private List<Building_AncientCryptosleepCasket> watched;

        public MapComponent_VaultSleepers(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (resolved)
            {
                return;
            }
            if (!map.IsHashIntervalTick(CheckIntervalTicks))
            {
                return;
            }
            if (!IsEligible())
            {
                resolved = true; // never eligible -- stop checking for good
                return;
            }
            if (!gatheredCaskets)
            {
                GatherCaskets();
            }
            CheckForTransition();
        }

        private bool IsEligible()
        {
            if (checkedEligibility)
            {
                return eligible;
            }
            checkedEligibility = true;
            if (map?.Parent is Site site
                && site.questTags != null
                && site.questTags.Count > 0
                && site.parts != null
                && site.parts.Any(p => p.def != null && p.def.defName == VaultSitePartDefName))
            {
                eligible = true;
            }
            return eligible;
        }

        private void GatherCaskets()
        {
            gatheredCaskets = true;
            watched = map.listerThings.ThingsOfDef(ThingDefOf.AncientCryptosleepCasket)
                .OfType<Building_AncientCryptosleepCasket>()
                .ToList();
            if (watched.Count == 0)
            {
                // Nothing to watch yet (KCSG may still be settling on the
                // very first eligible tick) -- try gathering again next
                // interval rather than declaring the site empty.
                gatheredCaskets = false;
            }
        }

        private void CheckForTransition()
        {
            if (watched == null)
            {
                return;
            }
            foreach (Building_AncientCryptosleepCasket casket in watched)
            {
                if (casket.Destroyed)
                {
                    // Went down with its contents still sealed inside --
                    // never legitimately opened.
                    Send(LootedSignal);
                    return;
                }
                if (!casket.HasAnyContents)
                {
                    // EjectContents already ran (Open job or combat damage):
                    // the sleepers are out and, per
                    // Building_AncientCryptosleepCasket.EjectContents, a
                    // hostile assault lord now exists for them.
                    Send(WokenSignal);
                    return;
                }
            }
        }

        private void Send(string signalPart)
        {
            resolved = true;
            QuestUtility.SendQuestTargetSignals(map.Parent.questTags, signalPart);
        }
    }
}
