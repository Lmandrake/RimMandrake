extern alias flowworks;
// JawaBenchFlowWorksPlaytestHose.cs - the flexible hose's scenes on the FlowWorks playtest runner (2026-10-11).
//
// The hose moved from Gimme Some Slack to FlowWorks at the hose port (2026-10-11), and its two scenes moved with it
// from JawaBenchGssPlaytest.cs, logic and journal records unchanged: hose_bend (the outlet-bend hypothesis for the 9 live
// MX_H FAILs, laid with and without the outlet on the live map) and hose_carry (a real colonist's work-giver deploy /
// move / retract, and a draft mid-carry). JawaBenchFlowWorksPlaytest.cs owns the controller, journal and verdict; it
// destroys each scene's kept fixtures and, for the scenes in PRedErrorScenes, fails a PASS that logged red errors.
//
// EVIDENCE vs SETUP: the reel spawn and DevLayInstant build FIXTURES; the evidence routes are RM_MapComponent_Hoses.EnsureLay,
// the reel's order methods (what the gizmos call), WorkGiver_HoseOrders and the hose job drivers.
//
// COUPLING: unlike the rest of the FlowWorks runner (reflection only), this file compiles against RimMandrakeFlowWorks.dll
// (csproj FlowWorksModDir, extern alias flowworks, InternalsVisibleTo). No member SIGNATURE here names a FlowWorks type,
// so the companion still loads without FlowWorks; jawa/playtest_start refuses first when FlowWorks is absent. The site
// search (GFindRectOn), the spawn (GSpawnOn) and the worker pick (GWorker) are shared with the GSS runner.

using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using GHose = flowworks::RimMandrake.FlowWorks.Hose;
using FSlack = flowworks::RimMandrake.Shared.Slack;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ════════════════════════════════════════════════════════════════ shared GSS fixtures, on a FlowWorks scene

        private static bool GFindRect(PCtx c, IntVec3 near, int w, int h, out CellRect rect) => GFindRectOn(c.map, c.run.seed, near, w, h, out rect);

        private static Thing GSpawn(PCtx c, string defName, IntVec3 at, Rot4? rot = null)
        {
            Thing t = GSpawnOn(c.map, defName, at, rot);
            return t == null ? null : c.Keep(t);
        }

        // ════════════════════════════════════════════════════════════════ hose bend (the 9 live FAILs)
        // 2026-10-06, owner decision by question card (straight lead-out): the hose leaves the nozzle straight for
        // HoseMath.LeadOutStraight cells, then joins the laid hose by a curve never under the minimum radius; a target with no
        // room for that is REFUSED (HoseMath.LeadOutBlocked), which this scene counts as a refusal, not a bar failure.

        private static double GMinBendAt(IList<FSlack.V2> X, double skip, out double sAt)
        {
            double[] s = FSlack.Geo.CumLen(X);
            double L = s[s.Length - 1], best = 99; sAt = -1;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < skip || s[i] > L - skip) continue;
                double th = FSlack.CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (FSlack.V2.Dist(X[i - 1], X[i]) + FSlack.V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9 && seg / th < best) { best = seg / th; sAt = s[i]; }
            }
            return best;
        }

        private static IEnumerable<PWait> GScnHoseBend(PCtx c)
        {
            c.ev["route"] = "reel spawned; DevLayInstant (fixture) to 12 targets round it; geometry from RM_MapComponent_Hoses.EnsureLay (production); the same ends re-laid WITHOUT the outlet on the live map snapshot for the counterfactual";
            Map m = c.map;
            if (!GHose.RM_HoseSettings.enabled) { c.Invalid("hoses switched off in settings"); yield break; }
            if (!GFindRect(c, m.Center + new IntVec3(30, 0, -30), 34, 34, out CellRect r)) { c.Invalid("no clean 34x34 site"); yield break; }
            IntVec3 at = r.CenterCell;
            Thing reel = GSpawn(c, "RM_HoseReel", at);
            if (reel == null) { c.Invalid("RM_HoseReel def missing"); yield break; }
            var rc = reel.TryGetComp<GHose.CompHoseReel>();
            var hc = m.GetComponent<GHose.RM_MapComponent_Hoses>();
            double minR = GHose.RM_HoseSettings.minBendRadius;
            c.ev["minBendSetting"] = minR;
            c.ev["outward"] = rc.Rect.Outward.HasValue ? rc.Rect.Outward.Value.ToString() : null;
            var rows = new List<Dictionary<string, object>>();
            c.ev["lays"] = rows;
            GHose.HoseShapeParams sp = GHose.RM_HoseSettings.Shape();
            sp.MaxLength = rc.MaxLength;
            double st = GHose.HoseMath.LeadOutStraight(sp);
            c.Phase("exec");
            foreach (int rad in new[] { 8, 14 })
                for (int k = 0; k < (rad == 8 ? 8 : 4); k++)
                {
                    double ang = (rad == 8 ? 45.0 * k : 90.0 * k + 45) * Math.PI / 180;
                    var tgt = new IntVec3(at.x + (int)Math.Round(rad * Math.Cos(ang)), 0, at.z + (int)Math.Round(rad * Math.Sin(ang)));
                    string why = rc.DevLayInstant(tgt);
                    GHose.HoseLay lay = why == null ? hc.EnsureLay(rc) : null;
                    var row = PD("target", PCell(tgt), "bearingDeg", Math.Round(ang * 180 / Math.PI), "refused", why ?? (lay == null ? rc.lastLayReason : null));
                    if (lay != null)
                    {
                        double mb = GMinBendAt(lay.Flat, GHose.HoseMath.EndSkip, out double sAt);
                        double beyond = Math.Min(GHose.HoseMath.MinBendRadius(lay.Flat, lay.LeadOutLen + 0.5), GHose.HoseMath.MinBendRadius(lay.Plump, lay.LeadOutLen + 0.5));
                        // counterfactual: the same ends, no outlet (EnsureLay's own call minus startOutward)
                        FSlack.CordWorld w = hc.World();
                        GHose.HoseLay free = GHose.HoseMath.LayAlong(w, GHose.RM_MapComponent_Hoses.Start(rc), rc.TrailCells(), new FSlack.Cell(tgt.x, tgt.z).Centre, sp, rc.Seed);
                        string zone = sAt < 0 ? "none" : sAt <= st ? "straight" : sAt <= lay.LeadOutLen + 0.25 ? "blend" : "beyond";
                        row["leadOutLen"] = Math.Round(lay.LeadOutLen, 2);
                        row["outlet"] = lay.Outlet; row["minBendFlat"] = Math.Round(lay.MinBendFlat, 3); row["minBendPlump"] = Math.Round(lay.MinBendPlump, 3);
                        row["minBendAtS"] = Math.Round(sAt, 2); row["zone"] = zone; row["minBendBeyondBlend"] = Math.Round(beyond, 3);
                        row["flatLen"] = Math.Round(lay.FlatLen, 2); row["maxLength"] = rc.MaxLength; row["overLength"] = lay.FlatLen > rc.MaxLength + 1e-6;
                        row["fellBack"] = lay.FellBack;
                        row["freeMinBend"] = free.Ok ? Math.Round(Math.Min(free.MinBendFlat, free.MinBendPlump), 3) : (object)null;
                        row["barPass"] = Math.Min(lay.MinBendFlat, lay.MinBendPlump) >= 0.95 * minR;
                    }
                    rows.Add(row);
                    rc.ReelIn();
                    yield return PTicks(1);
                }
            c.Phase("observe");
            var laid = rows.Where(x => x.ContainsKey("barPass")).ToList();
            var bad = laid.Where(x => !(bool)x["barPass"]).ToList();
            int inBlend = bad.Count(x => (string)x["zone"] == "blend" || (string)x["zone"] == "straight");
            int freeOk = bad.Count(x => x["freeMinBend"] is double fb && fb >= 0.95 * minR);
            int beyondOk = bad.Count(x => (double)x["minBendBeyondBlend"] >= 0.95 * minR);
            int over = laid.Count(x => (bool)x["overLength"]);
            string hyp = bad.Count == 0 ? "no tight bend to explain"
                : inBlend == bad.Count && freeOk == bad.Count && beyondOk == bad.Count
                    ? "CONFIRMED: every tight bend sits in the outlet straight/blend, the hose beyond the blend holds the radius, and the same ends laid without the outlet bend fine"
                    : "NOT confirmed as sole cause: " + inBlend + "/" + bad.Count + " in the outlet zone, " + beyondOk + "/" + bad.Count + " fine beyond it, " + freeOk + "/" + bad.Count + " fine without the outlet";
            c.ev["hypothesisOutletBend"] = hyp;
            c.ev["laid"] = laid.Count; c.ev["underBar"] = bad.Count; c.ev["overLength"] = over;
            c.ev["refusedNoLeadOut"] = rows.Count(x => (x["refused"] as string) == GHose.HoseMath.LeadOutBlocked);
            if (laid.Count == 0) { c.Invalid("no lay succeeded"); yield break; }
            if (bad.Count == 0 && over == 0) c.Pass("all " + laid.Count + " lays hold >= 95% of the minimum bend radius and the hose length");
            else c.Defect(bad.Count + "/" + laid.Count + " lays bend under 95% of " + minR.ToString("0.00") + " (worst " +
                          (bad.Count > 0 ? bad.Min(x => (double)x["minBendFlat"]).ToString("0.00") : "-") + "), " + over + " over the hose length; outlet hypothesis " + hyp);
        }

        // ════════════════════════════════════════════════════════════════ hose carry (real colonist)

        private static IEnumerable<PWait> GScnHoseCarry(PCtx c)
        {
            c.ev["route"] = "OrderDeploy/OrderMove/OrderRetract (what the gizmos call) -> an undrafted colonist's think tree takes WorkGiver_HoseOrders (Hauling) -> JobDriver_CarryHoseEnd / JobDriver_RetractHose; then a draft mid-carry";
            Map m = c.map;
            Pawn p = GWorker(m);
            if (p == null) { c.Invalid("no free undrafted hauling-capable colonist"); yield break; }
            if (!GFindRect(c, p.Position, 24, 12, out CellRect r)) { c.Invalid("no clean 24x12 site"); yield break; }
            if (!m.reachability.CanReach(p.Position, r.CenterCell, PathEndMode.Touch, TraverseParms.For(p))) { c.Invalid("colonist cannot reach the site"); yield break; }
            Thing reel = GSpawn(c, "RM_HoseReel", new IntVec3(r.minX + 3, 0, r.minZ + 5));
            if (reel == null) { c.Invalid("RM_HoseReel def missing"); yield break; }
            var rc = reel.TryGetComp<GHose.CompHoseReel>();
            int prevPrio = p.workSettings.GetPriority(WorkTypeDefOf.Hauling);
            var steps = new List<Dictionary<string, object>>();
            c.ev["steps"] = steps; c.ev["worker"] = p.LabelShort;
            var fails = new List<string>();
            try
            {
                p.workSettings.SetPriority(WorkTypeDefOf.Hauling, 1);
                IntVec3 t1 = new IntVec3(r.minX + 15, 0, r.minZ + 6), t2 = new IntVec3(r.minX + 12, 0, r.minZ + 10);
                foreach (var stage in new[] { new { name = "deploy", tgt = t1 }, new { name = "move", tgt = t2 }, new { name = "retract", tgt = IntVec3.Invalid } })
                {
                    c.Phase("exec");
                    string why = stage.name == "deploy" ? rc.OrderDeploy(stage.tgt) : stage.name == "move" ? rc.OrderMove(stage.tgt) : rc.OrderRetract();
                    string taker = null; bool forced = false; int t0 = TicksGameSafe();
                    PWait w = PUntil(() => rc.pending == GHose.HosePendingOrder.None &&
                                           (stage.name == "retract" ? rc.carry == GHose.HoseCarryState.Stored : rc.carry == GHose.HoseCarryState.Laid), 6000,
                        () => { if (taker == null && rc.carrier != null) { taker = rc.carrier.LabelShort; forced = rc.carrier.CurJob?.playerForced ?? false; } });
                    if (why == null) yield return w;
                    c.Phase("observe");
                    var lay = rc.HoseOut ? m.GetComponent<GHose.RM_MapComponent_Hoses>().EnsureLay(rc) : null;
                    var row = PD("stage", stage.name, "orderRefused", why, "carry", rc.carry.ToString(), "pending", rc.pending.ToString(), "far", rc.far.ToString(),
                        "taker", taker, "playerForced", forced, "ticks", TicksGameSafe() - t0, "timedOut", why == null && w.timedOut,
                        "trailCells", rc.trail.Count, "trailLength", Math.Round(rc.TrailLength(), 2), "maxLength", rc.MaxLength,
                        "layOk", lay != null, "flatLen", lay != null ? Math.Round(lay.FlatLen, 2) : (object)null);
                    steps.Add(row);
                    if (why != null) fails.Add(stage.name + " order refused: " + why);
                    else if (w.timedOut) fails.Add(stage.name + ": not finished in 6000 ticks (carry " + rc.carry + ", pending " + rc.pending + ", taker " + (taker ?? "none") + ")");
                    else if (forced) fails.Add(stage.name + ": the job was playerForced, not the work-giver route");
                    else if (stage.name != "retract" && lay == null) fails.Add(stage.name + ": the carried hose did not lay (" + rc.lastLayReason + ")");
                    if (fails.Count > 0) break;
                }
                // a draft mid-carry drops the end; undrafting resumes it (autoResumeDroppedHose)
                if (fails.Count == 0)
                {
                    c.Phase("exec");
                    string why = rc.OrderDeploy(t1);
                    yield return PUntil(() => rc.carry == GHose.HoseCarryState.Carrying && rc.TrailLength() >= 3, 4000);
                    Pawn carrier = rc.carrier;
                    bool carrying = rc.carry == GHose.HoseCarryState.Carrying && carrier != null;
                    if (carrying) carrier.drafter.Drafted = true;
                    yield return PTicks(60);
                    string afterDraft = rc.carry.ToString();
                    if (carrier != null) carrier.drafter.Drafted = false;
                    PWait wr = PUntil(() => rc.carry == GHose.HoseCarryState.Laid && rc.pending == GHose.HosePendingOrder.None, 6000);
                    yield return wr;
                    c.Phase("observe");
                    steps.Add(PD("stage", "draft_mid_carry", "orderRefused", why, "wasCarrying", carrying, "afterDraft", afterDraft, "final", rc.carry.ToString(),
                        "resumed", !wr.timedOut, "autoResumeSetting", GHose.RM_HoseSettings.autoResumeDroppedHose));
                    if (!carrying) fails.Add("draft_mid_carry: never saw the hose being carried");
                    else if (afterDraft != "Dropped") fails.Add("drafting the carrier left the hose " + afterDraft + " (expected Dropped)");
                    else if (GHose.RM_HoseSettings.autoResumeDroppedHose && wr.timedOut) fails.Add("undrafted carrier never resumed the dropped hose (" + rc.carry + ")");
                    rc.ReelIn();
                }
            }
            finally { if (p.workSettings != null) p.workSettings.SetPriority(WorkTypeDefOf.Hauling, prevPrio); if (p.Drafted) p.drafter.Drafted = false; }
            if (fails.Count == 0) c.Pass("deploy, move and retract taken by the work giver and finished; a draft mid-carry dropped the end and undrafting resumed it");
            else c.Defect(string.Join("; ", fails));
        }
    }
}
