using System;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Hose
{
    /// <summary>
    /// validation_hose.py's state-read channel, the same shape as GimmeSomeSlackProbe / AerialProbe: the script
    /// writes <see cref="request"/> with jawa/mod_settings_field, RM_MapComponent_Hoses answers on its next frame
    /// (paused or not), the JSON lands in <see cref="result"/> and <see cref="serial"/> is bumped.
    ///
    /// census | lay:rx,rz,x,z | check:rx,rz,x,z | reelin:rx,rz | flow:rx,rz=on|off | end:rx,rz=nozzle|cap |
    /// set:field=value | defaults. (rx,rz) is the reel's cell. flow: drives the DEBUG provider (b).
    /// Carry stage S2 (hose_carry_design_2026-10-04.md section 13): order:rx,rz=deploy:x,z|move:x,z|retract|cancel places
    /// the PLAYER's order exactly as the gizmos do; settrail:rx,rz=laid|dropped;x,z;x,z;... stages a walked trail (review map
    /// station 44); gizmos:rx,rz lists the reel's gizmo labels under the CURRENT dev-mode flag (CR7). lay/reelin stay the
    /// instant staging verbs and work with dev mode off.
    /// Carry stage S3: colonists | pawn:id=draft|undraft|tp:x,z|stop | startjob:rx,rz=forced|work;pawnId (the reel's pending
    /// order as a real job for that colonist, through WorkGiver_HoseOrders.JobFor).
    /// </summary>
    public static class HoseProbe
    {
        public static string request = "";
        public static string result = "";
        public static int serial;

        public static void Service(Map map, RM_MapComponent_Hoses comp)
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

        private static int[] Ints(string s) => s.Split(',').Select(x => int.Parse(x.Trim(), CultureInfo.InvariantCulture)).ToArray();

        private static CompHoseReel ReelAt(RM_MapComponent_Hoses comp, int x, int z) =>
            comp.Reels.FirstOrDefault(r => r.parent.OccupiedRect().Contains(new IntVec3(x, 0, z)));   // any cell of the 2x2 reel

        private static string Run(Map map, RM_MapComponent_Hoses comp, string cmd)
        {
            if (cmd == "census") return Census(map, comp);
            if (cmd == "defaults") { HoseSettings.ResetToDefaults(); return "{\"success\":true,\"cmd\":\"defaults\"}"; }
            if (cmd.StartsWith("set:"))
            {
                string[] kv = cmd.Substring(4).Split(new[] { '=' }, 2);
                FieldInfo fi = typeof(HoseSettings).GetField(kv[0], BindingFlags.Public | BindingFlags.Static);
                if (fi == null) return "{\"success\":false,\"error\":\"no settings field " + kv[0] + "\"}";
                object v = fi.FieldType.IsEnum ? Enum.Parse(fi.FieldType, kv[1]) : Convert.ChangeType(kv[1], fi.FieldType, CultureInfo.InvariantCulture);
                fi.SetValue(null, v);
                return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
            }
            if (cmd == "colonists") return Colonists(map);
            if (cmd.StartsWith("pawn:")) return PawnVerb(map, cmd);
            int colon = cmd.IndexOf(':');
            if (colon < 0) return "{\"success\":false,\"error\":\"unknown command\",\"cmd\":" + S(cmd) + "}";
            string verb = cmd.Substring(0, colon), arg = cmd.Substring(colon + 1), val = null;
            int eq = arg.IndexOf('=');
            if (eq >= 0) { val = arg.Substring(eq + 1); arg = arg.Substring(0, eq); }
            int[] a = Ints(arg);
            CompHoseReel r = ReelAt(comp, a[0], a[1]);
            if (r == null) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"no hose reel at " + a[0] + "," + a[1] + "\"}";
            switch (verb)
            {
                case "lay":
                {
                    string why = r.TryLay(new IntVec3(a[2], 0, a[3]));
                    if (why == null) comp.EnsureLay(r);
                    return "{\"success\":" + B(why == null) + ",\"cmd\":" + S(cmd) + ",\"reason\":" + S(why) + ",\"layOk\":" + B(r.lay != null) + "}";
                }
                case "check":
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"reason\":" + S(comp.CheckInstall(r, new IntVec3(a[2], 0, a[3]))) + "}";
                case "reelin":
                    r.ReelIn();
                    return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
                case "flow":
                    r.debugFlowing = val == "on" || val == "true" || val == "1";
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"debugFlowing\":" + B(r.debugFlowing) + ",\"tick\":" + Find.TickManager.TicksGame + "}";
                case "end":
                    r.end = val == "cap" ? HoseEnd.EndCap : HoseEnd.Nozzle;
                    return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
                case "order":
                {
                    string why;
                    string o = val ?? "";
                    if (o.StartsWith("deploy:")) { int[] t = Ints(o.Substring(7)); why = r.OrderDeploy(new IntVec3(t[0], 0, t[1])); }
                    else if (o.StartsWith("move:")) { int[] t = Ints(o.Substring(5)); why = r.OrderMove(new IntVec3(t[0], 0, t[1])); }
                    else if (o == "retract") why = r.OrderRetract();
                    else if (o == "cancel") { r.CancelOrder(); why = null; }
                    else return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"order must be deploy:x,z|move:x,z|retract|cancel\"}";
                    return "{\"success\":" + B(why == null) + ",\"cmd\":" + S(cmd) + ",\"reason\":" + S(why) + ",\"pending\":" + S(r.pending.ToString()) +
                           ",\"pendingAt\":" + Pos(r.pendingAt) + ",\"carry\":" + S(r.carry.ToString()) + "}";
                }
                case "settrail":
                {
                    // laid|dropped;x,z;x,z;... : the first cell should be a reel cell (where the hose leaves the drum)
                    string[] parts = (val ?? "").Split(';');
                    HoseCarryState st = parts[0] == "dropped" ? HoseCarryState.Dropped : HoseCarryState.Laid;
                    var cells = parts.Skip(1).Where(x => x.Trim().Length > 0).Select(x => { int[] t = Ints(x); return new IntVec3(t[0], 0, t[1]); }).ToList();
                    if (cells.Count == 0) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"no cells\"}";
                    r.ReelIn();
                    r.trail.AddRange(cells);
                    r.far = cells[cells.Count - 1];
                    r.carry = st;
                    r.laid = true;
                    r.layKey = null;
                    r.lay = null;
                    r.parent.DirtyMapMesh(map);
                    comp.EnsureLay(r);
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"carry\":" + S(r.carry.ToString()) + ",\"trail\":" + r.trail.Count +
                           ",\"trailLength\":" + D(r.TrailLength()) + ",\"layOk\":" + B(r.lay != null) + "}";
                }
                case "gizmos":
                {
                    var labels = r.CompGetGizmosExtra().OfType<Command>().Select(g => g.Label).ToList();
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"devMode\":" + B(Prefs.DevMode) + ",\"labels\":[" + string.Join(",", labels.Select(S)) + "]}";
                }
                case "devmode":
                {
                    // CR7 staging: devmode:rx,rz=on|off sets the dev-mode flag so the gizmos verb can be read both ways.
                    if (val == "on") Prefs.DevMode = true; else if (val == "off") Prefs.DevMode = false;
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"devMode\":" + B(Prefs.DevMode) + "}";
                }
                case "clearhist":
                    r.history.Clear();
                    return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
                case "startjob":
                {
                    // S3 (CR rows): startjob:rx,rz=forced;<pawnId> | work;<pawnId>. Takes the reel's PENDING order (place it with
                    // order: first) through the WorkGiver's own JobFor, exactly as a colonist would; forced = the right-click
                    // path (drafted pawns too), work = the unforced WorkGiver checks (allowed area, forbidden, Danger.Some).
                    string[] parts = (val ?? "").Split(';');
                    bool forced = parts[0] != "work";
                    Pawn p = parts.Length > 1 ? PawnById(map, parts[1]) : null;
                    if (p == null) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"no such pawn on this map\"}";
                    Verse.AI.Job j = Jobs.WorkGiver_HoseOrders.JobFor(p, r, forced, out string jwhy);
                    if (j == null) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"reason\":" + S(jwhy) + "}";
                    j.playerForced = forced;
                    bool took = p.jobs.TryTakeOrderedJob(j, Verse.AI.JobTag.Misc);
                    return "{\"success\":" + B(took) + ",\"cmd\":" + S(cmd) + ",\"job\":" + S(j.def.defName) + ",\"curJob\":" + S(p.CurJobDef?.defName) +
                           ",\"pending\":" + S(r.pending.ToString()) + ",\"pendingAt\":" + Pos(r.pendingAt) + "}";
                }
            }
            return "{\"success\":false,\"error\":\"unknown verb\",\"cmd\":" + S(cmd) + "}";
        }

        private static string Census(Map map, RM_MapComponent_Hoses comp)
        {
            var sb = new StringBuilder();
            int now = Find.TickManager.TicksGame;
            sb.Append("{\"success\":true,\"cmd\":\"census\",\"tick\":").Append(now)
              .Append(",\"enabled\":").Append(B(HoseSettings.enabled))
              .Append(",\"texturesInstalled\":").Append(B(HoseMaterials.Installed))
              .Append(",\"defaultLook\":").Append(S(Aerial.StylePicker.DefaultLook))
              .Append(",\"styleArtMissing\":[").Append(string.Join(",", HoseMaterials.Missing.Select(S))).Append(']')
              .Append(",\"wireVisibleWidth\":").Append(D(HoseMath.WireVisibleWidth))
              .Append(",\"minBendSetting\":").Append(D(HoseSettings.minBendRadius))
              .Append(",\"transitionTicks\":").Append(HoseSettings.transitionTicks)
              .Append(",\"releaseTicks\":").Append(HoseSettings.releaseTicks)
              .Append(",\"minPlumpDwell\":").Append(HoseSettings.minPlumpDwell)
              .Append(",\"relays\":").Append(RM_MapComponent_Hoses.Relays)
              .Append(",\"lastLayMs\":").Append(RM_MapComponent_Hoses.LastLayMs)
              .Append(",\"feedDraws\":").Append(comp.lastFeedDraws).Append(",\"relayCouplings\":").Append(comp.lastRelayCouplings)
              .Append(",\"fittingsOnTop\":").Append(comp.FittingsOnTopNow())   // MESSYCONDUIT_CABLE_PILE_LOOK_1 rule 3
              .Append(",\"queues\":{\"hose\":").Append(HoseMaterials.Queue).Append(",\"overhead\":").Append(Aerial.AerialMaterials.OverheadQueue)
              .Append(",\"spanMat\":").Append(Aerial.AerialMaterials.Span != null ? Aerial.AerialMaterials.Span.renderQueue : -1).Append('}').Append(",\"reelEndsHidden\":").Append(comp.lastReelEndHidden)
              .Append(",\"retracts\":").Append(RM_MapComponent_Hoses.Retracts)
              .Append(",\"live\":{\"carryDraws\":").Append(comp.lastCarryDraws).Append(",\"clipDraws\":").Append(comp.lastClipDraws)
              .Append(",\"ghostDraws\":").Append(comp.lastGhostDraws).Append(",\"ghosts\":").Append(comp.GhostCount)
              .Append(",\"portCouplings\":").Append(comp.lastPortCouplings).Append(",\"prefixBuilds\":").Append(comp.carryPrefixBuilds)
              .Append(",\"far\":").Append(B(comp.lastFar)).Append(",\"placed\":").Append(HoseEvents.Placed).Append(",\"lifted\":").Append(HoseEvents.Lifted).Append('}')
              .Append(",\"hoses\":[");
            bool first = true;
            foreach (CompHoseReel r in comp.Reels)
            {
                if (!first) sb.Append(',');
                first = false;
                HoseLay lay = comp.EnsureLay(r);
                RM_MapComponent_Hoses.PoseInfo pi = RM_MapComponent_Hoses.Info(r);
                HoseFreeEnd fe = HoseEnds.Read(r);
                sb.Append("{\"id\":").Append(r.parent.thingIDNumber)
                  .Append(",\"kind\":\"Hose\"")
                  .Append(",\"reel\":[").Append(r.parent.Position.x).Append(',').Append(r.parent.Position.z).Append(']')
                  .Append(",\"far\":[").Append(r.far.x).Append(',').Append(r.far.z).Append(']')
                  .Append(",\"laid\":").Append(B(r.laid))
                  .Append(",\"layOk\":").Append(B(lay != null))
                  .Append(",\"carry\":").Append(S(r.carry.ToString()))
                  .Append(",\"carrier\":").Append(r.carrier == null ? "null" : "{\"id\":" + r.carrier.thingIDNumber + ",\"name\":" + S(r.carrier.LabelShort) + ",\"pos\":" + Pos(r.carrier.Position) + "}")
                  .Append(",\"trail\":{\"count\":").Append(r.trail.Count).Append(",\"pulled\":").Append(D(r.TrailLength()))
                  .Append(",\"last\":").Append(r.trail.Count > 0 ? Pos(r.trail[r.trail.Count - 1]) : "null").Append(",\"planned\":").Append(B(r.trail.Count == 0)).Append('}')
                  .Append(",\"pending\":").Append(S(r.pending.ToString()))
                  .Append(",\"pendingAt\":").Append(Pos(r.pendingAt))
                  .Append(",\"wound\":").Append(D(r.wound))
                  .Append(",\"endKind\":").Append(S(fe.Kind.ToString()))
                  .Append(",\"freeEnd\":{\"cell\":").Append(fe.Cell.IsValid ? Pos(fe.Cell) : "null").Append(",\"terrain\":").Append(S(fe.Terrain?.defName ?? ""))
                  .Append(",\"water\":").Append(S(fe.Water?.defName ?? "")).Append(",\"port\":").Append(S(fe.Port?.def.defName ?? ""))
                  .Append(",\"portFaction\":").Append(S(fe.Port?.Faction?.Name ?? "")).Append(",\"describe\":").Append(S(fe.Describe())).Append('}')
                  .Append(",\"draw\":{\"mode\":").Append(S(comp.lastDraw.TryGetValue(r, out string dm) ? dm : "none"))
                  .Append(",\"len\":").Append(D(comp.lastDrawnLen.TryGetValue(r, out double dl) ? dl : 0))
                  .Append(",\"hand\":").Append(comp.lastHand.TryGetValue(r, out Core.V2 hv) ? "[" + D(hv.X) + "," + D(hv.Z) + "]" : "null")
                  .Append(",\"reelArt\":").Append(S(RM_MapComponent_Hoses.ReelGraphic(r))).Append('}')
                  .Append(",\"end\":").Append(S(r.end.ToString()))
                  .Append(",\"state\":").Append(S(r.sm.State.ToString()))
                  .Append(",\"stateSince\":").Append(r.sm.Since)
                  .Append(",\"transitions\":").Append(r.sm.Transitions)
                  .Append(",\"blend\":").Append(D(pi.Blend))
                  .Append(",\"eased\":").Append(D(pi.Eased))
                  .Append(",\"wobbling\":").Append(B(pi.Wobbling))
                  .Append(",\"visibleWidth\":").Append(D(pi.Visible))
                  .Append(",\"widthOverWire\":").Append(D(pi.Visible / HoseMath.WireVisibleWidth))
                  .Append(",\"meshWidthFlat\":").Append(D(HoseMath.MeshWidthFlat(pi.Visible)))
                  .Append(",\"meshWidthPlump\":").Append(D(HoseMath.MeshWidthPlump(pi.Visible)))
                  .Append(",\"provider\":").Append(S(r.lastProvider))
                  .Append(",\"signal\":").Append(B(r.lastSignal))
                  .Append(",\"debugFlowing\":").Append(B(r.debugFlowing))
                  .Append(",\"maxLength\":").Append(D(r.MaxLength))
                  .Append(",\"port\":").Append(S(r.Port(true)?.def.defName))
                  .Append(",\"portKind\":").Append(S(r.portKind.ToString()))
                  .Append(",\"portSide\":[").Append(r.portSide.X).Append(',').Append(r.portSide.Z).Append(']')
                  .Append(",\"portContact\":[").Append(r.portContact.X).Append(',').Append(r.portContact.Z).Append(']')
                  .Append(",\"footprint\":[").Append(r.Rect.X0).Append(',').Append(r.Rect.Z0).Append(',').Append(r.Rect.W).Append(',').Append(r.Rect.H).Append(']')
                  .Append(",\"start\":[").Append(D(r.Rect.Mouth.X)).Append(',').Append(D(r.Rect.Mouth.Z)).Append(']')
                  .Append(",\"relayTo\":").Append(RelayPos(comp.RelayOf(r)))
                  .Append(",\"fedBy\":[").Append(string.Join(",", comp.FeedersOf(r).Select(f => RelayPos(f)))).Append(']')
                  .Append(",\"endPoint\":").Append(r.laid ? EndPos(comp, r) : "null")
                  .Append(",\"retractReason\":").Append(S(r.lastRetractReason))
                  .Append(",\"retractTick\":").Append(r.lastRetractTick)
                  .Append(",\"look\":").Append(S(HoseMaterials.LookOf(r)))
                  .Append(",\"rawStyle\":").Append(S(Aerial.StylePicker.RawStyle(r.parent)?.defName))
                  .Append(",\"style\":").Append(S(r.parent.StyleDef?.defName))
                  .Append(",\"reelState\":").Append(S(RM_MapComponent_Hoses.ReelGraphic(r)))
                  .Append(",\"reelTex\":").Append(S(ReelTex(r)))
                  .Append(",\"hoseTex\":{").Append(string.Join(",", HoseMaterials.For(r).paths.OrderBy(kv => kv.Key).Select(kv => S(kv.Key) + ":" + S(kv.Value)))).Append('}')
                  .Append(",\"history\":[").Append(string.Join(",", r.history.Select(h => "[" + h.Key + "," + S(h.Value.ToString()) + "]"))).Append(']');
                if (lay != null)
                {
                    var pose = HoseMath.Pose(lay, pi.Eased, int.MaxValue / 2, 30, HoseSettings.plumpAmount);
                    sb.Append(",\"pathLen\":").Append(D(lay.PathLen))
                      .Append(",\"flatLen\":").Append(D(lay.FlatLen))
                      .Append(",\"plumpLen\":").Append(D(lay.PlumpLen))
                      .Append(",\"poseLen\":").Append(D(Geo.Length(pose)))
                      .Append(",\"straight\":").Append(D(V2.Dist(lay.Flat[0], lay.Flat[lay.Flat.Count - 1])))
                      .Append(",\"minBendFlat\":").Append(D(lay.MinBendFlat))
                      .Append(",\"minBendPlump\":").Append(D(lay.MinBendPlump))
                      .Append(",\"minBendPose\":").Append(D(HoseMath.MinBendRadius(pose, HoseMath.EndSkip)))
                      .Append(",\"selfIntersects\":").Append(B(HoseMath.SelfIntersects(lay.Flat)))
                      .Append(",\"couplings\":").Append(lay.Couplings.Count)
                      .Append(",\"reelGraphic\":").Append(S(RM_MapComponent_Hoses.ReelGraphic(r)))
                      .Append(",\"joints\":").Append(lay.Joints.Count)
                      .Append(",\"points\":").Append(lay.Flat.Count)
                      .Append(",\"fellBack\":").Append(B(lay.FellBack))
                      .Append(",\"bbox\":[").Append(D(lay.Flat.Min(q => q.X))).Append(',').Append(D(lay.Flat.Min(q => q.Z))).Append(',')
                      .Append(D(lay.Flat.Max(q => q.X))).Append(',').Append(D(lay.Flat.Max(q => q.Z))).Append(']')
                      .Append(",\"centreCells\":[").Append(string.Join(",", lay.Centre.Select(q => "[" + q.Floor.X + "," + q.Floor.Z + "]").Distinct())).Append(']')
                      .Append(",\"geometryHash\":").Append(S(RM_MapComponent_Hoses.GeometryHash(lay).ToString("x16")))
                      .Append(",\"relayEnd\":").Append(RelayEnd(comp, r, lay))
                      .Append(",\"unwalkablePoints\":").Append(lay.Flat.Count(p => !comp.World().IsWalkable(p.Floor)));
                }
                sb.Append('}');
            }
            sb.Append("]}");
            return sb.ToString();
        }

        // ---------------------------------------------------------------- S3 scene verbs: real colonists for the CR rows
        private static Pawn PawnById(Map map, string id)
        {
            if (!int.TryParse(id.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int n)) return null;
            return map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.thingIDNumber == n);
        }

        private static string PawnJson(Pawn p) =>
            "{\"id\":" + p.thingIDNumber + ",\"name\":" + S(p.LabelShort) + ",\"pos\":" + Pos(p.Position) + ",\"drafted\":" + B(p.Drafted) +
            ",\"downed\":" + B(p.Downed) + ",\"job\":" + S(p.CurJobDef?.defName) + ",\"forced\":" + B(p.CurJob?.playerForced ?? false) +
            ",\"driver\":" + S(p.jobs?.curDriver?.GetType().Name) + ",\"toil\":" + (p.jobs?.curDriver?.CurToilIndex ?? -1) + "}";

        /// <summary>colonists: every free colonist on this map with position, draft, job and toil.</summary>
        private static string Colonists(Map map) =>
            "{\"success\":true,\"cmd\":\"colonists\",\"tick\":" + Find.TickManager.TicksGame + ",\"pawns\":[" +
            string.Join(",", map.mapPawns.FreeColonistsSpawned.Select(PawnJson)) + "]}";

        /// <summary>pawn:&lt;id&gt;=draft|undraft|tp:x,z|stop. draft/undraft go through the real Drafted setter (which ends a
        /// player-interruptible job: the CR3 interrupt); tp places the pawn for staging; stop ends his job InterruptForced.</summary>
        private static string PawnVerb(Map map, string cmd)
        {
            string arg = cmd.Substring(5), val = "";
            int eq = arg.IndexOf('=');
            if (eq >= 0) { val = arg.Substring(eq + 1); arg = arg.Substring(0, eq); }
            Pawn p = PawnById(map, arg);
            if (p == null) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"no such pawn on this map\"}";
            if (val == "draft" || val == "undraft")
            {
                if (p.drafter == null) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"pawn cannot be drafted\"}";
                p.drafter.Drafted = val == "draft";
            }
            else if (val.StartsWith("tp:"))
            {
                int[] t = Ints(val.Substring(3));
                var c = new IntVec3(t[0], 0, t[1]);
                if (!c.InBounds(map) || !c.Standable(map)) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"cell not standable\"}";
                p.jobs?.StopAll();
                p.pather?.StopDead();
                p.Position = c;
                p.Notify_Teleported(true, true);
            }
            else if (val == "stop") p.jobs?.EndCurrentJob(Verse.AI.JobCondition.InterruptForced);
            else if (val.Length > 0) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"pawn verb must be draft|undraft|tp:x,z|stop\"}";
            return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"pawn\":" + PawnJson(p) + "}";
        }

        private static string Pos(IntVec3 c) => c.IsValid ? "[" + c.x + "," + c.z + "]" : "null";
        private static string RelayPos(CompHoseReel r) => r == null ? "null" : "[" + r.parent.Position.x + "," + r.parent.Position.z + "]";
        private static string EndPos(RM_MapComponent_Hoses comp, CompHoseReel r)
        {
            V2 e = comp.EndPoint(r, out _);
            return "[" + D(e.X) + "," + D(e.Z) + "]";
        }

        /// <summary>Round 7 (station 42): what is DRAWN at a relay end -- the lay's last point, the coupling's axis, the
        /// signed distance from the relay's edge on the intake side (+ = outside) and whether it lies within that edge,
        /// and the angle (deg) between the last 0.5 cell of the drawn hose and the axis.</summary>
        private static string RelayEnd(RM_MapComponent_Hoses comp, CompHoseReel r, HoseLay lay)
        {
            V2 e = comp.EndPoint(r, out CompHoseReel relay, out V2? inward);
            if (relay == null || !inward.HasValue || lay == null) return "null";
            V2 last = lay.Flat[lay.Flat.Count - 1];
            double off = HoseRelay.EdgeOffset(relay.Rect, inward.Value, last, out bool within);
            V2 tail = (last - HoseMath.PointBack(lay.Flat, 0.5)).Norm();
            double ang = Math.Acos(Math.Max(-1, Math.Min(1, tail.X * inward.Value.X + tail.Z * inward.Value.Z))) * 180 / Math.PI;
            return "{\"drawnEnd\":[" + D(last.X) + "," + D(last.Z) + "],\"endPoint\":[" + D(e.X) + "," + D(e.Z) + "]" +
                   ",\"inward\":[" + D(inward.Value.X) + "," + D(inward.Value.Z) + "],\"edgeOffset\":" + D(off) +
                   ",\"withinEdge\":" + B(within) + ",\"tailAngleDeg\":" + D(ang) + ",\"tolerance\":" + D(HoseRelay.EndTolerance) +
                   ",\"relayLook\":" + S(HoseMaterials.LookOf(relay)) + ",\"relayArt\":" + S(relay.laid ? "deployed" : "stored") + "}";
        }

        /// <summary>The reel art printing now: the deployed (laid, empty drum) path when laid and present, else the stored path.</summary>
        private static string ReelTex(CompHoseReel r)
        {
            Graphic g = r.parent.Graphic;
            if (!(g is Graphic_HoseReel gr)) return g?.path;
            return r.laid && gr.DeployedPath != null ? gr.DeployedPath : gr.path;
        }

        private static string S(string s) => s == null ? "null" : "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "") + "\"";
        private static string B(bool b) => b ? "true" : "false";
        private static string D(double d) => d.ToString("0.####", CultureInfo.InvariantCulture);
    }
}
