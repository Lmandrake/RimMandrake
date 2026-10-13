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

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
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
                "0 (minus kept) for a clean result.",
            ResultDescription =
                "success, action, mapId, threats[] (id, def, faction, x, z, turret, spawner, dormant, causer, kept), " +
                "removed[], threatsAfter, kept, letters[] (id, def, label, sentBefore, sentAfter), lettersUnsentAfter, ticksGame.")]
        public static async Task<object> QuietSite(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "status | apply", DefaultValue = "status")] string action = "status",
            [ToolParameter(Description = "apply: vanish hostile threat structures", DefaultValue = false)] bool clearThreats = false,
            [ToolParameter(Description = "apply: comma list of defNames NEVER removed (the mod under test)", DefaultValue = null)] string keepDefs = null,
            [ToolParameter(Description = "apply: mark every CompProximityLetter as sent", DefaultValue = false)] bool proximityLetters = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var a = (action ?? "status").Trim().ToLowerInvariant();
                if (a != "status" && a != "apply") return Fail("action must be status or apply");
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
    }
}
