using System.Linq;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_SITE_BEATS_1 — beats 3-5 read the site chosen at the end of beat 2 (A, C or D; B is cut).
    ///
    /// What is built (all offline, all PROVISIONAL, one Mod Settings toggle <c>siteBeatsEnabled</c>):
    ///   QuestNode_RUT_LineSiteSetup   stores lineSite / lineSiteName / lineSiteFaction (who stewards that site) into the
    ///                                 slate, so beat texts name the place and the lend/ally logic reads one source.
    ///   LineSiteBeats.LendFaction     beat 4: the crafter is lent to the faction that RUNS the site (C Enclaves, D Hive,
    ///                                 A the neutral-ground rule LineTithe already had), not always the Hive.
    ///   QuestNode_RUT_SiteAllies      beat 5: when the strike arrives, the site's faction sends defenders to hold beside
    ///                                 you (a vanilla friendly raid, LordJob_AssistColony), so the allies are the site's own.
    ///
    /// What is NOT built, and why: the caravan TradeRequests to the site's settlement (beat 4) and the separate
    /// defence-site MAP with the line core whose loss fails the beat (beat 5). Both need engine behaviour nobody has
    /// measured (a TradeRequest with four ThingDefs; a site map the player travels to, and Q1=A ordered no line-core
    /// building), so the shuttle and the colony stay where beats 4-5 already run. Filed as live items, not faked.
    /// </summary>
    public static class LineSiteBeats
    {
        public static bool Enabled => UnfinishedLineSettings.siteBeatsEnabled;

        public static string Site => GameComponent_RUT_UnfinishedLine.Get?.EffectiveSite ?? LineSites.A;

        /// <summary>Who stewards the site: the Hive at the Ore Seams, the Enclaves at the other two.</summary>
        public static Faction SiteFaction(string site)
        {
            Faction enclaves = LineFactions.Enclaves;
            Faction hive = LineFactions.Hive;
            Faction f = site == LineSites.D ? hive : enclaves;
            if (f == null || f.defeated) f = site == LineSites.D ? enclaves : hive;
            return f == null || f.defeated ? null : f;
        }

        /// <summary>Beat 4: the faction that gets the lent crafter. Null when the toggle is off or the steward is hostile,
        /// so <see cref="LineTithe.LendFaction"/> keeps its own rule.</summary>
        public static Faction LendFaction()
        {
            if (!Enabled) return null;
            Faction f = SiteFaction(Site);
            return f != null && !f.HostileTo(Faction.OfPlayer) ? f : null;
        }

        /// <summary>Beat 5: the allied defenders' faction, or null (toggle off, no friendly steward, or no combat pawns).</summary>
        public static Faction AllyFaction()
        {
            if (!Enabled) return null;
            Faction f = SiteFaction(Site);
            if (f == null || f.HostileTo(Faction.OfPlayer)) return null;
            return f.def.pawnGroupMakers != null && f.def.pawnGroupMakers.Any(g => g.kindDef == PawnGroupKindDefOf.Combat) ? f : null;
        }

        /// <summary>Sends the defenders to <paramref name="map"/>. Returns a one-line outcome for the proof and the log.</summary>
        public static string SendAllies(Map map)
        {
            Faction ally = AllyFaction();
            if (map == null) return "no map";
            if (ally == null) return "no allies (off, hostile steward or no combat pawns)";
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(IncidentDefOf.RaidFriendly.category, map);
            parms.faction = ally;
            parms.points = UnfinishedLineSettings.siteAllyPoints;
            bool ok = IncidentDefOf.RaidFriendly.Worker.TryExecute(parms);
            return (ok ? "sent " : "FAILED to send ") + ally.def.defName + " defenders at " + parms.points + " points";
        }
    }

    public class QuestNode_RUT_LineSiteSetup : QuestNode
    {
        [NoTranslate] public string storeSiteAs = "lineSite";
        [NoTranslate] public string storeNameAs = "lineSiteName";
        [NoTranslate] public string storeFactionAs = "lineSiteFaction";

        private void Store(Slate slate)
        {
            string site = LineSiteBeats.Site;
            slate.Set(storeSiteAs, site);
            slate.Set(storeNameAs, LineSites.Name(site));
            slate.Set(storeFactionAs, LineSiteBeats.SiteFaction(site));
        }

        protected override bool TestRunInt(Slate slate)
        {
            Store(slate);
            return true;
        }

        protected override void RunInt()
        {
            Store(QuestGen.slate);
        }
    }

    public class QuestPart_RUT_SiteAllies : QuestPart
    {
        public string inSignal;
        public Map map;
        public bool sent;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (sent || signal.tag != inSignal) return;
            sent = true;
            Log.Message("[UnfinishedLine] site allies: " + LineSiteBeats.SendAllies(map));
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref sent, "sent", false);
            Scribe_References.Look(ref map, "map");
        }
    }

    /// <summary>Beat 5: on <c>inSignal</c> the site's faction sends defenders to $map.</summary>
    public class QuestNode_RUT_SiteAllies : QuestNode
    {
        [NoTranslate] public string inSignal;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new QuestPart_RUT_SiteAllies
            {
                inSignal = inSignal.NullOrEmpty() ? slate.Get<string>("inSignal") : QuestGenUtility.HardcodedSignalWithQuestID(inSignal),
                map = slate.Get<Map>("map")
            });
        }
    }

    // jawa/static_call proof (validation.py, site_beats). Read-only: sends nobody.
    public static class UnfinishedLineSiteBeatsProof
    {
        public static string ProofSiteBeats()
        {
            string site = LineSiteBeats.Site;
            Faction lend = LineSiteBeats.LendFaction();
            Faction ally = LineSiteBeats.AllyFaction();
            return "SITEBEATS site=" + site + " enabled=" + LineSiteBeats.Enabled
                + " steward=" + (LineSiteBeats.SiteFaction(site)?.def.defName ?? "none")
                + " lend=" + (lend?.def.defName ?? "default") + " ally=" + (ally?.def.defName ?? "none")
                + " points=" + UnfinishedLineSettings.siteAllyPoints
                + " tithe-lend=" + (LineTithe.LendFaction()?.def.defName ?? "none");
        }

        /// <summary>Sends the allies to the first home map now (skips the quest). Needs a map; changes the game.</summary>
        public static string ProofSendAllies() => LineSiteBeats.SendAllies(Find.AnyPlayerHomeMap);
    }
}
