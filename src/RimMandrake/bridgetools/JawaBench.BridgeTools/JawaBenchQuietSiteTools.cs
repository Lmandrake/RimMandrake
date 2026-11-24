// JawaBenchQuietSiteTools.cs - jawa/quiet_site: the C# half of the shared quiet isolated test-site profile
// (src/RimMandrake/Utils/modcheck/quiet_site.py; design: Transient/night_20261013/quiet_profile.md).
//
// Two narrow controls the Python profile cannot do with existing tools, each READ BACK:
//   * clearThreats  - Vanish every hostile THREAT STRUCTURE on the current map, using the vitals monitor's own
//                     classifier (JawaBenchVitals.IsThreatStructure), so the site starts with exactly what the monitor
//                     would latch removed and nothing else (TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS,
//                     TESTENV_QUICKTEST_HIVES_HARDEN_EMPTY_NEST, TESTENV_MEGAPEDE_HARDEN_GATECRASHER). keepDefs spares the
//                     mod under test. Vanish = no death action, no corpse, no explosion (same reasoning as kill_hostiles).
//   * proximityLetters - mark every CompProximityLetter on the map as already sent (letterSent = true), so a colonist
//                     walking near a mapgen VoidMonolith does not raise "Fallen monolith" mid-row
//                     (TESTENV_MONOLITH_HARDEN_UNINVITED_GUEST: it is a proximity letter, NOT an incident - read from 1.6
//                     source via rimsage: CompProximityLetter.CompTick checks letterSent, Find.Anomaly.Level == 0, radius 8).
// action=status reads both without writing. Each write is reported per thing.
//
// actions calm | reassert | read | release: the whole calm map in one call (JawaBenchCalm.cs, JawaBenchCalmCore.cs; page
// design/specs/2026-11-23-calm-map/boundary.md). They do not use clearThreats/proximityLetters.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using CC = JawaBench.BridgeTools.JawaBenchCalmCore;
using VT = JawaBench.BridgeTools.JawaBenchVitals;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/quiet_site",
            Description =
                "Quiet isolated test-site controls (test fixture, read back). action=status lists the current map's hostile " +
                "threat structures (the vitals monitor's own classifier: turret, pawn spawner, dormant, condition causer or a " +
                "non-humanlike faction) and every unsent proximity letter (e.g. the Anomaly void monolith). action=apply with " +
                "clearThreats=true VANISHES those structures (no death action) except defNames in keepDefs; with " +
                "proximityLetters=true marks every proximity letter as already sent. Re-reads after writing: threatsAfter must be " +
                "0 (minus kept) for a clean result. " +
                "THE CALM MAP IN ONE CALL: action=calm sets and reads back every control (storyteller, random mental states and diseases, every incident " +
                "at IncidentWorker.TryExecute except allowIncidents, the incident queue frozen, wild-animal arrivals, forced weather, proximity letters; with clear=true it also " +
                "VANISHES hostiles, wild predators, arrivals, threat structures and fires and ends other game conditions, sparing keepDefs/keepIds). action=reassert " +
                "sets again what drifted, with the last calm's arguments (run it after every load). action=read changes nothing. action=release restores " +
                "the switches and proximity-letter flags, ends its forced weather condition and releases its holds. " +
                "verdict is CALM only when every control was READ and none is off; notCalm[] and notRead[] name each thing; notCovered[] lists what no control reads. " +
                "The calm is for ONE game and releases itself after `minutes` (default 30, max 240). Its forced weather is saved with the map: release before a save.",
            ResultDescription =
                "calm/reassert/read/release: success (calm and reassert: verdict is CALM), verdict, calm, controls[] (name, status, detail, things[]), notCalm[], notRead[], excepted[], " +
                "repaired[], couldNotRepair[], errors[], breaches{counts, rows[], lastSeq, dropped}, secondsLeft, notCovered[]. status/apply: success, action, mapId, threats[] (id, def, faction, x, z, turret, spawner, dormant, causer, kept), " +
                "removed[], threatsAfter, kept, letters[] (id, def, label, sentBefore, sentAfter), lettersUnsentAfter, ticksGame.")]
        public static async Task<object> QuietSite(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "status | apply | calm | reassert | read | release", DefaultValue = "status")] string action = "status",
            [ToolParameter(Description = "apply: vanish hostile threat structures", DefaultValue = false)] bool clearThreats = false,
            [ToolParameter(Description = "apply: comma list of defNames NEVER removed (the mod under test)", DefaultValue = null)] string keepDefs = null,
            [ToolParameter(Description = "apply: mark every CompProximityLetter as sent", DefaultValue = false)] bool proximityLetters = false,
            [ToolParameter(Description = "calm: the WeatherDef to force", DefaultValue = "Clear")] string weather = "Clear",
            [ToolParameter(Description = "calm: comma list of IncidentDefs that MAY run (a scene about a raid names its raid)", DefaultValue = null)] string allowIncidents = null,
            [ToolParameter(Description = "calm: comma list of controls the scene takes off (each reads EXCEPTED)", DefaultValue = null)] string except = null,
            [ToolParameter(Description = "calm/reassert: also remove hostiles, wild predators, arrivals, threat structures, fires and other game conditions (DESTRUCTIVE)", DefaultValue = false)] bool clear = false,
            [ToolParameter(Description = "calm: comma list of pawn ids (ThingID or number) never counted or removed (the cast)", DefaultValue = null)] string keepIds = null,
            [ToolParameter(Description = "calm/reassert: lease minutes (calm defaults to 30, max 240). Omit on reassert to keep the deadline or rearm for the last calm's duration.", DefaultValue = null)] double? minutes = null,
            [ToolParameter(Description = "calm/reassert/read: map uniqueID. -1 = current map", DefaultValue = -1)] int mapId = -1,
            [ToolParameter(Description = "calm/reassert/read: return breach rows with seq above this", DefaultValue = 0L)] long sinceSeq = 0)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var a = (action ?? "status").Trim().ToLowerInvariant();
                if (a == "calm" || a == "reassert" || a == "read" || a == "release")
                    return CalmAction(a, weather, allowIncidents, except, clear, keepDefs, keepIds, minutes, mapId, sinceSeq);
                if (a != "status" && a != "apply") return Fail("action must be status, apply, calm, reassert, read or release");
                if (a == "apply" && !clearThreats && !proximityLetters)
                    return Fail("action=apply with neither clearThreats nor proximityLetters would change nothing under a reported success");
                var map = Find.CurrentMap;
                if (Current.Game == null || map == null) return Fail("No game / current map.");
                var player = Faction.OfPlayer;
                var keep = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                if (!string.IsNullOrWhiteSpace(keepDefs))
                    foreach (var k in keepDefs.Split(',')) if (k.Trim().Length > 0) keep.Add(k.Trim());

                var threats = new List<object>();
                var doomed = new List<Building>();
                var bs = new List<Building>(map.listerBuildings.allBuildingsNonColonist);
                for (int i = 0; i < bs.Count; i++)
                {
                    var b = bs[i];
                    bool turret, spawner, asleep, causer;
                    if (!VT.IsThreatStructure(b, player, out turret, out spawner, out asleep, out causer)) continue;
                    bool kept = b.def != null && keep.Contains(b.def.defName);
                    threats.Add(new { id = b.ThingID, def = b.def?.defName, faction = b.Faction?.Name, x = b.Position.x, z = b.Position.z,
                                      turret, spawner, dormant = asleep, causer, kept });
                    if (!kept) doomed.Add(b);
                }

                var removed = new List<object>();
                var errors = new List<string>();
                if (a == "apply" && clearThreats)
                    for (int i = 0; i < doomed.Count; i++)
                    {
                        var b = doomed[i];
                        string id = b.ThingID, def = b.def?.defName;
                        try
                        {
                            if (b.def != null && b.def.destroyable) b.Destroy(DestroyMode.Vanish);
                            else if (b.Spawned) b.DeSpawn(DestroyMode.Vanish);
                            removed.Add(new { id, def, gone = !b.Spawned });
                        }
                        catch (Exception e) { errors.Add(id + ": " + e.GetType().Name + " " + e.Message); }
                    }

                int after = 0, keptN = 0;
                var bs2 = map.listerBuildings.allBuildingsNonColonist;
                for (int i = 0; i < bs2.Count; i++)
                {
                    bool t1, t2, t3, t4;
                    if (!VT.IsThreatStructure(bs2[i], player, out t1, out t2, out t3, out t4)) continue;
                    if (bs2[i].def != null && keep.Contains(bs2[i].def.defName)) keptN++; else after++;
                }

                var letters = new List<object>();
                int unsentAfter = 0;
                var all = map.listerThings.AllThings;
                for (int i = 0; i < all.Count; i++)
                {
                    var tw = all[i] as ThingWithComps;
                    if (tw == null) continue;
                    var c = tw.GetComp<CompProximityLetter>();
                    if (c == null) continue;
                    bool before = c.letterSent;
                    if (a == "apply" && proximityLetters && !before) c.letterSent = true;
                    if (!c.letterSent) unsentAfter++;
                    letters.Add(new { id = tw.ThingID, def = tw.def?.defName, label = c.Props?.letterLabel, sentBefore = before, sentAfter = c.letterSent });
                }

                bool ok = errors.Count == 0 && (a != "apply" || !clearThreats || after == 0) && (a != "apply" || !proximityLetters || unsentAfter == 0);
                return new
                {
                    success = ok, action = a, mapId = map.uniqueID, threats, removed, errors, threatsAfter = after, kept = keptN,
                    letters, lettersUnsentAfter = unsentAfter, ticksGame = TicksGameSafe(),
                    message = ok ? null : "read-back disagrees: threatsAfter=" + after + " lettersUnsentAfter=" + unsentAfter + " errors=" + errors.Count,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        private static object CalmAction(string a, string weather, string allowIncidents, string except, bool clear, string keepDefs,
                                         string keepIds, double? minutes, int mapId, long sinceSeq)
        {
            if (a == "release")
            {
                bool owed = JawaBenchCalm.RestoreOwed;
                var done = owed ? JawaBenchCalm.Restore("released") : new List<string> { "nothing to release: no calm is set" };
                return new { success = !done.Any(d => d.StartsWith("COULD NOT", StringComparison.Ordinal)), action = a, released = owed, restored = done, ticksGame = TicksGameSafe() };
            }
            string err;
            var map = NorthstarMap(mapId, out err);
            if (map == null) return Fail(err);
            if (a == "calm")
            {
                string unknown;
                var ex = CC.ParseNames(except, CC.Controls, out unknown);
                if (unknown != null) return Fail("except: '" + unknown + "' is no control. Controls: " + string.Join(", ", CC.Controls));
                var allow = CC.ParseNames(allowIncidents, DefDatabase<IncidentDef>.AllDefsListForReading.Select(d => d.defName).ToList(), out unknown);
                if (unknown != null) return Fail("allowIncidents: no IncidentDef '" + unknown + "'", DefSuggestions<IncidentDef>(unknown));
                var wd = string.IsNullOrWhiteSpace(weather) ? null : DefDatabase<WeatherDef>.GetNamedSilentFail(weather.Trim());
                if (wd == null) return Fail("No WeatherDef '" + weather + "'.", DefSuggestions<WeatherDef>(weather));
                JawaBenchCalm.WeatherName = wd.defName;
                JawaBenchCalm.Allow = allow;
                JawaBenchCalm.Except = ex;
                JawaBenchCalm.KeepDefs = CC.ParseNames(keepDefs, null, out unknown);
                JawaBenchCalm.KeepIds = CC.ParseNames(keepIds, null, out unknown);
            }
            else if (a == "reassert" && !JawaBenchCalm.EverArmed) return Fail("nothing to reassert: run action=calm first");

            var before = CC.Judge(JawaBenchCalm.ReadAll(map), JawaBenchCalm.Except);
            var errors = new List<string>();
            var rep = before;
            if (a != "read")
            {
                errors = JawaBenchCalm.Apply(map, a == "calm", clear, minutes, "jawa/quiet_site " + a);
                rep = CC.Judge(JawaBenchCalm.ReadAll(map), JawaBenchCalm.Except);
            }
            var wasBad = before.Readings.Where(r => r.Status == CC.NotCalm || r.Status == CC.NotRead).ToList();
            bool Bad(string n) => rep.Readings.Any(r => r.Name == n && (r.Status == CC.NotCalm || r.Status == CC.NotRead));
            string Line(CC.Reading r) => r.Name + ": " + r.Detail + (r.Things.Count > 0 ? " [" + string.Join("; ", r.Things.ToArray()) + "]" : "");
            bool active = JawaBenchCalm.Active();
            return new
            {
                success = a == "read" || (rep.IsCalm && errors.Count == 0), action = a, mapId = map.uniqueID,
                verdict = rep.Verdict, calm = rep.IsCalm,
                controls = rep.Readings.Select(r => new { name = r.Name, status = r.Status, detail = r.Detail, things = r.Things }).ToList(),
                notCalm = rep.Of(CC.NotCalm).Select(Line).ToList(), notRead = rep.Of(CC.NotRead).Select(Line).ToList(),
                excepted = rep.Of(CC.Excepted).Select(r => r.Name).ToList(), allowedIncidents = JawaBenchCalm.Allow.ToList(),
                repaired = a == "read" ? null : wasBad.Where(r => !Bad(r.Name) && r.Name != CC.Arrivals).Select(Line).ToList(),
                couldNotRepair = a == "read" ? null : wasBad.Where(r => Bad(r.Name)).Select(r => r.Name).ToList(),
                errors,
                breaches = new { counts = JawaBenchCalm.Breaches.Counts(), lastSeq = JawaBenchCalm.Breaches.LastSeq, dropped = JawaBenchCalm.Breaches.Dropped,
                                 rows = JawaBenchCalm.Breaches.Since(sinceSeq).Select(b => new { seq = b.Seq, kind = b.Kind, tick = b.Tick, what = b.What }).ToList() },
                queueTicksHeld = JawaBenchCalm.QueueTicksHeld, armTick = JawaBenchCalm.ArmTick,
                secondsLeft = active ? Math.Round(JawaBenchCalm.Lease.UntilS - JawaBenchTpsWatchdog.Now, 0) : 0,
                lastRelease = JawaBenchCalm.Lease.LastRelease, lastRestore = JawaBenchCalm.LastRestore,
                notCovered = CC.NotCovered, ticksGame = TicksGameSafe(),
                message = rep.IsCalm ? null : rep.Verdict + ": " + string.Join(" | ", rep.Of(CC.NotCalm).Concat(rep.Of(CC.NotRead)).Select(Line).ToArray()),
            };
        }
    }
}
