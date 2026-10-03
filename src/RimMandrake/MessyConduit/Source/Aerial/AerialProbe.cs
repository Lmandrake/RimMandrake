using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// The aerial lines' state-read channel for validation_aerial.py (same contract as MessyConduitProbe): the script
    /// writes <see cref="request"/> with jawa/mod_settings_field, RM_MapComponent_Aerial services it on its next
    /// MapComponentUpdate (every frame, paused or not), the JSON answer lands in <see cref="result"/> and
    /// <see cref="serial"/> is bumped.
    ///
    /// census | net:x,z | skipreseed:true|false | reseed:id | link:a,b | unlink:a,b | cut:a,b | restring:a,b | kill:id | dismantle:id | explode:x,z,r,dmg
    /// | watchdog | poll | set:field=value | defaults           (ids are thingIDNumber)
    /// </summary>
    public static class AerialProbe
    {
        public static string request = "";
        public static string result = "";
        public static int serial;

        public static void Service(Map map, RM_MapComponent_Aerial comp)
        {
            if (string.IsNullOrEmpty(request) || Find.CurrentMap != map) return;
            string cmd = request.Trim();
            request = "";
            string res;
            try { res = Run(map, comp, cmd); }
            catch (Exception ex) { res = "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":" + S(ex.ToString()) + "}"; }
            result = res;
            serial++;
        }

        private static Thing ById(Map map, int id) => map.listerThings.AllThings.FirstOrDefault(t => t.thingIDNumber == id);

        private static (CompAerialAnchor, CompAerialAnchor) Pair(Map map, string args)
        {
            int[] ids = args.Split(',').Select(s => int.Parse(s.Trim(), CultureInfo.InvariantCulture)).ToArray();
            return (CompAerialAnchor.Of(ById(map, ids[0])), CompAerialAnchor.Of(ById(map, ids[1])));
        }

        private static string Run(Map map, RM_MapComponent_Aerial comp, string cmd)
        {
            if (cmd == "census") return Census(map, comp);
            if (cmd == "watchdog") return Ok(cmd, "\"repairs\":" + comp.Watchdog() + ",\"netRepairs\":" + comp.netRepairs);
            if (cmd == "poll") return Ok(cmd, "\"flips\":" + comp.PollFallen());
            if (cmd == "defaults") { AerialSettings.ResetToDefaults(); AerialSettings.Apply(); return Ok(cmd, ""); }
            if (cmd.StartsWith("net:")) return Net(map, cmd.Substring(4));
            if (cmd.StartsWith("skipreseed:")) { CompAerialAnchor.debugSkipReseed = cmd.EndsWith("true"); return Ok(cmd, "\"value\":" + B(CompAerialAnchor.debugSkipReseed)); }
            if (cmd.StartsWith("reseed:")) { CompAerialAnchor.Reseed(CompAerialAnchor.Of(ById(map, int.Parse(cmd.Substring(7), CultureInfo.InvariantCulture)))); return Ok(cmd, ""); }
            if (cmd.StartsWith("link:"))
            {
                var (a, b) = Pair(map, cmd.Substring(5));
                if (a == null) return Fail(cmd, "first id is not an anchor");
                Thing bt = b?.parent ?? ById(map, int.Parse(cmd.Substring(5).Split(',')[1], CultureInfo.InvariantCulture));
                if (bt == null) return Fail(cmd, "no such target");
                LinkVerdict v = CompAerialAnchor.TryLink(a, bt);
                return Ok(cmd, "\"verdict\":" + S(v.ToString()));
            }
            if (cmd.StartsWith("unlink:")) { var (a, b) = Pair(map, cmd.Substring(7)); return Ok(cmd, "\"done\":" + B(a != null && b != null && CompAerialAnchor.Unlink(a, b))); }
            if (cmd.StartsWith("cut:")) { var (a, b) = Pair(map, cmd.Substring(4)); return Ok(cmd, "\"done\":" + B(a != null && b != null && CompAerialAnchor.Cut(a, b, 0.5f, true))); }
            if (cmd.StartsWith("restring:")) { var (a, b) = Pair(map, cmd.Substring(9)); return Ok(cmd, "\"done\":" + B(a != null && b != null && CompAerialAnchor.Restring(a, b))); }
            if (cmd.StartsWith("kill:") || cmd.StartsWith("dismantle:"))
            {
                bool kill = cmd.StartsWith("kill:");
                Thing t = ById(map, int.Parse(cmd.Substring(kill ? 5 : 10), CultureInfo.InvariantCulture));
                if (t == null) return Fail(cmd, "no such thing");
                if (kill) t.Kill(); else t.Destroy(DestroyMode.Deconstruct);
                return Ok(cmd, "\"destroyed\":" + B(t.Destroyed));
            }
            if (cmd.StartsWith("explode:"))
            {
                string[] p = cmd.Substring(8).Split(',');
                var c = new IntVec3(int.Parse(p[0], CultureInfo.InvariantCulture), 0, int.Parse(p[1], CultureInfo.InvariantCulture));
                float r = float.Parse(p[2], CultureInfo.InvariantCulture);
                int dmg = int.Parse(p[3], CultureInfo.InvariantCulture);
                int before = comp.explosionCuts;
                GenExplosion.DoExplosion(c, map, r, DamageDefOf.Bomb, null, dmg);
                return Ok(cmd, "\"cuts\":" + (comp.explosionCuts - before));
            }
            if (cmd.StartsWith("set:"))
            {
                string[] kv = cmd.Substring(4).Split(new[] { '=' }, 2);
                FieldInfo fi = typeof(AerialSettings).GetField(kv[0], BindingFlags.Public | BindingFlags.Static);
                if (fi == null) return Fail(cmd, "no settings field " + kv[0]);
                object v = fi.FieldType.IsEnum ? Enum.Parse(fi.FieldType, kv[1]) : Convert.ChangeType(kv[1], fi.FieldType, CultureInfo.InvariantCulture);
                fi.SetValue(null, v);
                AerialSettings.Apply();
                return Ok(cmd, "\"value\":" + S(Convert.ToString(fi.GetValue(null), CultureInfo.InvariantCulture)));
            }
            return Fail(cmd, "unknown command");
        }

        private static string Net(Map map, string args)
        {
            string[] p = args.Split(',');
            var c = new IntVec3(int.Parse(p[0], CultureInfo.InvariantCulture), 0, int.Parse(p[1], CultureInfo.InvariantCulture));
            var sb = new StringBuilder();
            PowerNet n = map.powerNetGrid.TransmittedPowerNetAt(c);
            var things = new List<string>();
            foreach (Thing t in c.GetThingList(map))
            {
                if (!(t is ThingWithComps tw)) continue;
                CompPowerTrader tr = tw.GetComp<CompPowerTrader>();
                CompPowerBattery bat = tw.GetComp<CompPowerBattery>();
                CompPower pc = tw.GetComp<CompPower>();
                if (pc == null) continue;
                things.Add("{\"id\":" + t.thingIDNumber + ",\"def\":" + S(t.def.defName) + ",\"faction\":" + S(t.Faction?.Name) +
                           ",\"net\":" + RM_MapComponent_Aerial.NetId(RM_MapComponent_Aerial.Registered(map, pc.PowerNet)) + ",\"compNet\":" + RM_MapComponent_Aerial.NetId(pc.PowerNet) +
                           (tr != null ? ",\"powerOn\":" + B(tr.PowerOn) + ",\"outputW\":" + F(tr.PowerOutput) : "") +
                           (bat != null ? ",\"storedWd\":" + F(bat.StoredEnergy) : "") + "}");
            }
            sb.Append("{\"success\":true,\"cmd\":\"net\",\"x\":" + c.x + ",\"z\":" + c.z + ",\"net\":" + RM_MapComponent_Aerial.NetId(n));
            if (n != null)
                sb.Append(",\"live\":" + B(n.HasActivePowerSource) + ",\"gainW\":" + F(n.CurrentEnergyGainRate() / CompPower.WattsToWattDaysPerTick) +
                          ",\"storedWd\":" + F(n.CurrentStoredEnergy()) + ",\"transmitters\":" + n.transmitters.Count + ",\"powerComps\":" + n.powerComps.Count);
            sb.Append(",\"things\":[" + string.Join(",", things) + "]}");
            return sb.ToString();
        }

        private static string Census(Map map, RM_MapComponent_Aerial comp)
        {
            var sb = new StringBuilder();
            sb.Append("{\"success\":true,\"cmd\":\"census\",\"ticksGame\":" + Find.TickManager.TicksGame);
            var anchors = comp.Anchors.OrderBy(a => a.thingIDNumber).ToList();
            int up = 0, cut = 0, fallenN = 0;
            var rows = new List<string>();
            foreach (CompAerialAnchor a in anchors)
            {
                var links = new List<string>();
                foreach (SpanLink l in a.links)
                {
                    if (l.state == SpanState.Up) up++; else cut++;
                    links.Add("{\"other\":" + (l.other?.thingIDNumber ?? -1) + ",\"state\":" + S(l.state.ToString()) + ",\"hp\":" + F(l.hp) + "}");
                }
                var fl = new List<string>();
                foreach (FallenCord f in a.fallen)
                {
                    FallenLay lay = comp.Lay(a, f);
                    double len = 0;
                    for (int i = 1; i < lay.Pts.Count; i++) len += P2.Dist(lay.Pts[i - 1], lay.Pts[i]);
                    fl.Add("{\"toward\":[" + f.toward.x + "," + f.toward.z + "],\"cutPartner\":" + f.cutPartner + ",\"pts\":" + lay.Pts.Count +
                           ",\"laidLen\":" + F((float)len) + ",\"tip\":[" + F((float)lay.Tip.X) + "," + F((float)lay.Tip.Z) + "],\"blocked\":" + B(lay.Blocked) + "}");
                    fallenN++;
                }
                PowerNet raw = a.PowerComp?.PowerNet;
                PowerNet n = RM_MapComponent_Aerial.NetOf(a);
                rows.Add("{\"id\":" + a.thingIDNumber + ",\"def\":" + S(a.def.defName) + ",\"x\":" + a.Position.x + ",\"z\":" + a.Position.z +
                         ",\"faction\":" + S(a.Faction?.Name) + ",\"net\":" + RM_MapComponent_Aerial.NetId(n) + ",\"compNet\":" + RM_MapComponent_Aerial.NetId(raw) +
                         ",\"gridNet\":" + RM_MapComponent_Aerial.NetId(map.powerNetGrid.TransmittedPowerNetAt(a.Position)) +
                         ",\"netLive\":" + B(n != null && n.HasActivePowerSource) +
                         ",\"fallenLive\":" + (comp.FallenLiveCached(a) is bool fv ? B(fv) : "null") +
                         ",\"links\":[" + string.Join(",", links) + "],\"fallen\":[" + string.Join(",", fl) + "]}");
            }
            var taps = new List<string>();
            foreach (CompPowerTap t in comp.Taps)
            {
                PowerNet v = t.VictimNet(out Thing vt);
                taps.Add("{\"id\":" + t.parent.thingIDNumber + ",\"ourNet\":" + RM_MapComponent_Aerial.NetId(RM_MapComponent_Aerial.Registered(map, t.Trader?.PowerNet)) + ",\"victimNet\":" + RM_MapComponent_Aerial.NetId(RM_MapComponent_Aerial.Registered(map, v)) +
                         ",\"victimFaction\":" + S(vt?.Faction?.Name) + ",\"outputW\":" + F(t.Trader?.PowerOutput ?? 0f) + ",\"powerOn\":" + B(t.Trader?.PowerOn ?? false) +
                         ",\"lastStolenW\":" + F(t.lastStolenW) + ",\"stolenTotalWd\":" + F(t.stolenTotalWd) + ",\"connected\":" + B(t.Trader?.connectParent != null) +
                         ",\"connectFaction\":" + S(t.Trader?.connectParent?.parent?.Faction?.Name) + "}");
            }
            sb.Append(",\"anchors\":[" + string.Join(",", rows) + "]");
            sb.Append(",\"spansUp\":" + up / 2 + ",\"spansCut\":" + cut / 2 + ",\"fallenCords\":" + fallenN);
            sb.Append(",\"netRepairs\":" + comp.netRepairs + ",\"watchdogRuns\":" + comp.watchdogRuns + ",\"roofCuts\":" + comp.roofCuts +
                      ",\"explosionCuts\":" + comp.explosionCuts + ",\"autoLinks\":" + comp.autoLinks + ",\"postfixAppends\":" + AerialPowerScope.appendedCalls);
            sb.Append(",\"spanDraws\":" + comp.lastSpanDraws + ",\"swayDraws\":" + comp.lastSwayDraws + ",\"swayReason\":" + S(comp.lastSwayReason) +
                      ",\"topDraws\":" + comp.lastTopDraws + ",\"glowDraws\":" + comp.lastGlowDraws + ",\"spanMeshes\":" + comp.SpanMeshCount);
            sb.Append(",\"groundVerts\":" + SectionLayer_RM_AerialGround.LastPrintedVerts + ",\"groundFallenPrinted\":" + SectionLayer_RM_AerialGround.LastFallenPrinted +
                      ",\"groundShadowsPrinted\":" + SectionLayer_RM_AerialGround.LastShadowsPrinted);
            sb.Append(",\"altitudes\":{\"pawn\":" + F(AltitudeLayer.Pawn.AltitudeFor()) + ",\"pawnState\":" + F(AltitudeLayer.PawnState.AltitudeFor()) +
                      ",\"span\":" + F(RM_MapComponent_Aerial.SpanAltitude) + ",\"top\":" + F(RM_MapComponent_Aerial.TopAltitude) +
                      ",\"blueprint\":" + F(AltitudeLayer.Blueprint.AltitudeFor()) + ",\"weather\":" + F(AltitudeLayer.Weather.AltitudeFor()) + "}");
            sb.Append(",\"taps\":[" + string.Join(",", taps) + "],\"tapGuardRefused\":" + Patch_ConnectToTransmitter_TapGuard.refused + ",\"tapEventsRaised\":" + TapEvents.raised);
            sb.Append(",\"wind\":" + F(map.windManager.WindSpeed) + ",\"plantSwayPref\":" + B(Prefs.PlantWindSway));
            sb.Append(",\"settings\":{" + string.Join(",", typeof(AerialSettings).GetFields(BindingFlags.Public | BindingFlags.Static)
                .Select(f => S(f.Name) + ":" + S(Convert.ToString(f.GetValue(null), CultureInfo.InvariantCulture)))) + "}");
            sb.Append("}");
            return sb.ToString();
        }

        private static string Ok(string cmd, string body) => "{\"success\":true,\"cmd\":" + S(cmd) + (body.Length > 0 ? "," + body : "") + "}";
        private static string Fail(string cmd, string why) => "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":" + S(why) + "}";
        private static string B(bool b) => b ? "true" : "false";
        private static string F(float f) => float.IsNaN(f) || float.IsInfinity(f) ? "null" : f.ToString("0.####", CultureInfo.InvariantCulture);

        private static string S(string s)
        {
            if (s == null) return "null";
            var sb = new StringBuilder("\"");
            foreach (char ch in s)
            {
                if (ch == '"' || ch == '\\') sb.Append('\\').Append(ch);
                else if (ch < ' ') sb.Append("\\u").Append(((int)ch).ToString("x4"));
                else sb.Append(ch);
            }
            return sb.Append('"').ToString();
        }
    }
}
