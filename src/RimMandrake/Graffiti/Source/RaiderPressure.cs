using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    // RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS. The owner's root (raiders "oppress with left-behind threats and marks
    // for future attacks") and his card pick "Sooner or bigger raid": while a hostile faction's mark stands on the colony's walls, that
    // faction's raids come larger (Larger mode) or its return raid comes sooner (Sooner mode), announced by one letter naming the faction
    // and pointing at its marks. The last such mark scrubbed, crossed out or weathered away lifts it (a message, not a letter).
    //
    // A "standing mark" is exactly what the territory thought counts (MapComponent_GraffitiSocial.EnemyMarks): spawned, not crossed out,
    // inside a player home map's Home area, made by a faction hostile to the player. So EnemyClaim and the pressure end together.
    //
    // The record (which factions are pressured, and Sooner mode's return tick) is saved with the game; the mark count is never cached:
    // it is read off the marks themselves when a raid's points are adjusted, so a scrub takes effect on the very next raid.

    public class RM_PressureEntry : IExposable
    {
        public Faction faction;
        public Map map;
        public int since = -1;
        public int returnTick = -1;
        public bool returned;

        public void ExposeData()
        {
            Scribe_References.Look(ref faction, "faction");
            Scribe_References.Look(ref map, "map");
            Scribe_Values.Look(ref since, "since", -1);
            Scribe_Values.Look(ref returnTick, "returnTick", -1);
            Scribe_Values.Look(ref returned, "returned");
        }
    }

    public class GameComponent_RaiderPressure : GameComponent
    {
        private List<RM_PressureEntry> entries = new List<RM_PressureEntry>();

        // for the live proof: what the last refresh announced (not saved)
        public string lastLetterLabel, lastLetterText, lastLift;
        public int lettersSent, liftsSent, returnsFired;

        public GameComponent_RaiderPressure(Game game)
        {
        }

        public static GameComponent_RaiderPressure Get => Current.Game?.GetComponent<GameComponent_RaiderPressure>();

        public IEnumerable<RM_PressureEntry> Entries => entries;

        public static RM_PressureMode Mode => RM_GraffitiSettings.raiderPressureMode == 1 ? RM_PressureMode.Sooner : RM_PressureMode.Larger;

        public static bool IsStanding(Filth_Mark m, Map map)
        {
            Faction f = m?.makerFaction;
            return m != null && m.Spawned && !m.defaced && f != null && f != Faction.OfPlayer && f.HostileTo(Faction.OfPlayer)
                && map.areaManager.Home[m.Position];
        }

        /// <summary>Every standing mark of every hostile faction on the player's home maps, by faction.</summary>
        public static Dictionary<Faction, List<Filth_Mark>> StandingByFaction()
        {
            var by = new Dictionary<Faction, List<Filth_Mark>>();
            if (Faction.OfPlayerSilentFail == null) return by;
            foreach (Map map in Find.Maps)
            {
                if (!map.IsPlayerHome) continue;
                MapComponent_GraffitiSocial social = MapComponent_GraffitiSocial.For(map);
                if (social == null) continue;
                foreach (Filth_Mark m in social.marks)
                {
                    if (!IsStanding(m, map)) continue;
                    if (!by.TryGetValue(m.makerFaction, out List<Filth_Mark> list)) by[m.makerFaction] = list = new List<Filth_Mark>();
                    list.Add(m);
                }
            }
            return by;
        }

        public static int StandingCount(Faction f)
        {
            if (f == null) return 0;
            return StandingByFaction().TryGetValue(f, out List<Filth_Mark> list) ? list.Count : 0;
        }

        /// <summary>The factor a raid of this faction gets right now (1 exactly with no standing mark or the switch off).</summary>
        public static float FactorNow(Faction f)
        {
            return RM_GraffitiKernel.PressureFactor(RM_GraffitiSettings.raiderPressureEnabled, StandingCount(f), RM_GraffitiSettings.raiderPressurePush);
        }

        public override void GameComponentTick()
        {
            if (Find.TickManager.TicksGame % GenTicks.TickRareInterval == 0) Refresh();
        }

        /// <summary>Bring the record in line with the walls: letter on start, message on lift, Sooner mode's return raid when due.</summary>
        public void Refresh()
        {
            bool on = RM_GraffitiSettings.raiderPressureEnabled;
            int now = Find.TickManager.TicksGame;
            Dictionary<Faction, List<Filth_Mark>> by = StandingByFaction();
            entries.RemoveAll(e => e == null || e.faction == null);

            // lifts first: a faction whose last mark is gone, or every faction when the switch is off
            foreach (RM_PressureEntry e in entries.ToList())
            {
                int n = by.TryGetValue(e.faction, out List<Filth_Mark> l) ? l.Count : 0;
                if (RM_GraffitiKernel.PressureChange(true, n, on) != -1) continue;
                entries.Remove(e);
                if (!on) continue;   // switching the feature off is not an in-world event: no message
                lastLift = "The marks of " + e.faction.Name + " are gone from our walls. They have no claim on us now.";
                liftsSent++;
                Messages.Message(lastLift, MessageTypeDefOf.PositiveEvent, historical: true);
            }
            if (!on) return;

            foreach (KeyValuePair<Faction, List<Filth_Mark>> kv in by)
            {
                RM_PressureEntry e = entries.FirstOrDefault(x => x.faction == kv.Key);
                if (e == null && RM_GraffitiKernel.PressureChange(false, kv.Value.Count, on) == 1)
                {
                    e = new RM_PressureEntry { faction = kv.Key, map = kv.Value[0].Map, since = now };
                    entries.Add(e);
                    SendLetter(e, kv.Value);
                }
                if (e == null) continue;
                if (e.map == null || !e.map.IsPlayerHome) e.map = kv.Value[0].Map;
                int ret = RM_GraffitiKernel.PressureReturnTicks(GenDate.TicksPerDay, on, Mode, kv.Value.Count, RM_GraffitiSettings.raiderPressurePush);
                if (ret < 0) e.returnTick = -1;
                else if (!e.returned && e.returnTick < 0) e.returnTick = e.since + ret;
                if (e.returnTick >= 0 && now >= e.returnTick && !e.returned) FireReturn(e);
            }
        }

        private void SendLetter(RM_PressureEntry e, List<Filth_Mark> marks)
        {
            bool sooner = Mode == RM_PressureMode.Sooner;
            float factor = RM_GraffitiKernel.PressureFactor(true, marks.Count, RM_GraffitiSettings.raiderPressurePush);
            int days = sooner ? RM_GraffitiKernel.PressureReturnTicks(GenDate.TicksPerDay, true, RM_PressureMode.Sooner, marks.Count,
                RM_GraffitiSettings.raiderPressurePush) / GenDate.TicksPerDay : 0;
            lastLetterLabel = "Marked by " + e.faction.Name;
            lastLetterText = e.faction.Name + " left " + (marks.Count == 1 ? "its mark" : marks.Count + " marks") + " on our walls: a promise to come back. "
                + (sooner
                    ? "While a mark of theirs stands, expect them back within " + days + " days."
                    : "While a mark of theirs stands, their raids will come about " + factor.ToString("0.#") + " times as strong.")
                + " Scrub or cross out every one of their marks to lift the threat.";
            lettersSent++;
            Find.LetterStack.ReceiveLetter(lastLetterLabel, lastLetterText, LetterDefOf.ThreatSmall, new LookTargets(marks.Cast<Thing>()), e.faction);
        }

        private void FireReturn(RM_PressureEntry e)
        {
            e.returned = true;
            e.returnTick = -1;
            Map map = e.map;
            if (map == null || !e.faction.HostileTo(Faction.OfPlayer)) return;
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, map);
            parms.faction = e.faction;
            parms.forced = true;
            if (IncidentDefOf.RaidEnemy.Worker.TryExecute(parms)) returnsFired++;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref entries, "rmRaiderPressure", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (entries == null) entries = new List<RM_PressureEntry>();
                entries.RemoveAll(e => e == null || e.faction == null);
            }
        }
    }

    /// <summary>Larger mode: a pressured faction's raid points, after the storyteller and before the pawns are made. Every raid path the
    /// colony meets goes through IncidentWorker_Raid.AdjustedRaidPoints (rw16 decomp: IncidentWorker_Raid.TryGenerateRaidInfo :94, and the
    /// quest raid nodes), so this is the one place to push; it acts only on a player home map.</summary>
    [StaticConstructorOnStartup]
    public static class RaiderPressureMod
    {
        static RaiderPressureMod()
        {
            var harmony = new Harmony("mandrake.rm.graffiti.raiderpressure");
            harmony.Patch(AccessTools.Method(typeof(IncidentWorker_Raid), nameof(IncidentWorker_Raid.AdjustedRaidPoints)),
                postfix: new HarmonyMethod(typeof(RaiderPressureMod), nameof(Postfix)));
        }

        public static void Postfix(Faction faction, IIncidentTarget target, ref float __result)
        {
            if (faction == null || !(target is Map map) || !map.IsPlayerHome || !RM_GraffitiSettings.raiderPressureEnabled) return;
            __result = RM_GraffitiKernel.PressurePoints(__result, true, GameComponent_RaiderPressure.Mode,
                GameComponent_RaiderPressure.StandingCount(faction), RM_GraffitiSettings.raiderPressurePush);
        }
    }

    /// <summary>
    /// Live entry points for scene sc_raider_pressure (src/RimMandrake/Graffiti/validation.py::scene_raider_pressure), by jawa/static_call.
    /// Each takes one string split on ';' and answers one line "HEAD key value | key value ..." (or "REFUSED why"), like RM_GraffitiProof.
    /// </summary>
    public static class RM_GraffitiPressureProof
    {
        private static Faction Named(string name)
        {
            name = (name ?? "").Trim();
            return Find.FactionManager.AllFactions.FirstOrDefault(f => f.Name == name);
        }

        /// <summary>"on;mode;push" (mode larger|sooner; any part blank keeps its value) -> the three settings as they now stand.</summary>
        public static string Set(string args)
        {
            string[] a = (args ?? "").Split(';');
            if (a.Length > 0 && a[0].Trim() != "") RM_GraffitiSettings.raiderPressureEnabled = a[0].Trim().ToLowerInvariant() == "true";
            if (a.Length > 1 && a[1].Trim() != "") RM_GraffitiSettings.raiderPressureMode = a[1].Trim().ToLowerInvariant() == "sooner" ? 1 : 0;
            if (a.Length > 2 && a[2].Trim() != "") RM_GraffitiSettings.raiderPressurePush = float.Parse(a[2].Trim(), System.Globalization.CultureInfo.InvariantCulture);
            return "SET on " + RM_GraffitiSettings.raiderPressureEnabled + " | mode " + GameComponent_RaiderPressure.Mode
                + " | push " + RM_GraffitiSettings.raiderPressurePush.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture);
        }

        /// <summary>Another hostile humanlike faction than the named one: the scene's faction B.</summary>
        public static string Other(string args)
        {
            Faction a = Named(args);
            Faction b = Find.FactionManager.AllFactions.FirstOrDefault(f => f != a && !f.IsPlayer && !f.Hidden && !f.defeated && f.def.humanlikeFaction
                && f.HostileTo(Faction.OfPlayer));
            return b == null ? "REFUSED no second hostile humanlike faction" : "OTHER faction " + b.Name + " | standing " + GameComponent_RaiderPressure.StandingCount(b);
        }

        /// <summary>Run the record's refresh now (it otherwise runs every 250 ticks) -> letters and lifts sent so far, and the last of each.</summary>
        public static string Refresh(string args)
        {
            GameComponent_RaiderPressure c = GameComponent_RaiderPressure.Get;
            if (c == null) return "REFUSED no GameComponent_RaiderPressure in this game";
            c.Refresh();
            return "REFRESH letters " + c.lettersSent + " | lifts " + c.liftsSent + " | returns " + c.returnsFired
                + " | letter " + (c.lastLetterLabel ?? "-") + " | lift " + (c.lastLift ?? "-");
        }

        /// <summary>"faction" -> its standing marks, live factor, whether the record holds it, and Sooner mode's ticks to its return.</summary>
        public static string Read(string args)
        {
            Faction f = Named(args);
            if (f == null) return "REFUSED no faction named '" + args + "'";
            GameComponent_RaiderPressure c = GameComponent_RaiderPressure.Get;
            RM_PressureEntry e = c?.Entries.FirstOrDefault(x => x.faction == f);
            int now = Find.TickManager.TicksGame;
            return "PRESSURE standing " + GameComponent_RaiderPressure.StandingCount(f) + " | factor "
                + GameComponent_RaiderPressure.FactorNow(f).ToString("0.###", System.Globalization.CultureInfo.InvariantCulture)
                + " | pressured " + (e != null) + " | returnIn " + (e != null && e.returnTick >= 0 ? (e.returnTick - now).ToString() : "-")
                + " | returned " + (e != null && e.returned)
                + " | faction " + f.Name;
        }

        /// <summary>"faction;points" -> the points a raid of that faction gets at this storyteller budget on the current map, through the very
        /// method the raid uses (IncidentWorker_Raid.AdjustedRaidPoints, edge walk-in, immediate attack), with the push and with the switch off.</summary>
        public static string Points(string args)
        {
            string[] a = (args ?? "").Split(';');
            Faction f = Named(a[0]);
            Map map = Find.CurrentMap;
            if (f == null || map == null || a.Length < 2) return "REFUSED want 'faction;points' on a current map";
            float pts = float.Parse(a[1].Trim(), System.Globalization.CultureInfo.InvariantCulture);
            float pushed = IncidentWorker_Raid.AdjustedRaidPoints(pts, PawnsArrivalModeDefOf.EdgeWalkIn, RaidStrategyDefOf.ImmediateAttack, f, PawnGroupKindDefOf.Combat, map);
            bool was = RM_GraffitiSettings.raiderPressureEnabled;
            RM_GraffitiSettings.raiderPressureEnabled = false;
            float vanilla;
            try { vanilla = IncidentWorker_Raid.AdjustedRaidPoints(pts, PawnsArrivalModeDefOf.EdgeWalkIn, RaidStrategyDefOf.ImmediateAttack, f, PawnGroupKindDefOf.Combat, map); }
            finally { RM_GraffitiSettings.raiderPressureEnabled = was; }
            var ci = System.Globalization.CultureInfo.InvariantCulture;
            return "POINTS in " + pts.ToString("0.##", ci) + " | out " + pushed.ToString("0.##", ci) + " | vanilla " + vanilla.ToString("0.##", ci)
                + " | faction " + f.Name;
        }
    }
}
