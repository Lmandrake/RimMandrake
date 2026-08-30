using System.Collections.Generic;
using System.Text;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.Pits
{
    // Bridge-reachable test surface for the spawn-mass quicktest matrix
    // (RIMMANDRAKE_PITS_BUILD_1's own stated first verification step).
    //
    // WHY THIS EXISTS. Arming a cover, setting a depth tier and rolling a
    // struggle interval are all GIZMO actions in play - a human clicks them.
    // RimBridge cannot click a gizmo, and it has no reflective field setter
    // (checked: the whole jawa/ + rimworld/ surface has none), so without
    // these the mass-sum trigger could only ever be proven by a human at the
    // keyboard. DebugActionType.ToolMap leaves ARE reachable from the bridge
    // by x/z, which makes every one of these a real, verifiable test hook.
    //
    // "Report" deliberately logs RAW FIELD VALUES, not a verdict, because a
    // bridge call returning success: true is not evidence of anything - the
    // caller reads these lines back out of the call's own log capture.
    public static class PitDebugActions
    {
        private const string CAT = "RMPits";

        // ------------------------------------------------------------ helpers

        private static Building_OpenPit PitAt(IntVec3 c)
        {
            Map map = Find.CurrentMap;
            if (map == null || !c.InBounds(map)) return null;
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Building_OpenPit p) return p;
            }
            return null;
        }

        private static Building_PitDigSite SiteAt(IntVec3 c)
        {
            Map map = Find.CurrentMap;
            if (map == null || !c.InBounds(map)) return null;
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Building_PitDigSite s) return s;
            }
            return null;
        }

        private static void NoPit(IntVec3 c)
        {
            Log.Message("[RMPitsDebug] NO_PIT at " + c);
        }

        // ------------------------------------------------------------ arming

        [DebugAction(CAT, "Arm cover: woven scrap (40kg)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ArmWovenScrap() { Arm(PitCoverTier.WovenScrap); }

        [DebugAction(CAT, "Arm cover: plank lattice (120kg)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ArmPlankLattice() { Arm(PitCoverTier.PlankLattice); }

        [DebugAction(CAT, "Arm cover: reinforced frame (400kg)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ArmReinforcedFrame() { Arm(PitCoverTier.ReinforcedFrame); }

        [DebugAction(CAT, "Uncover (disarm)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void Uncover()
        {
            IntVec3 c = UI.MouseCell();
            Building_OpenPit pit = PitAt(c);
            if (pit == null) { NoPit(c); return; }
            pit.ClearCover();
            Log.Message("[RMPitsDebug] UNCOVER " + pit.def.defName
                + " covered=" + pit.Covered + " coverTier=" + pit.CoverTier);
        }

        private static void Arm(PitCoverTier tier)
        {
            IntVec3 c = UI.MouseCell();
            Building_OpenPit pit = PitAt(c);
            if (pit == null) { NoPit(c); return; }
            pit.SetCover(tier);
            Log.Message("[RMPitsDebug] ARM " + pit.def.defName
                + " covered=" + pit.Covered
                + " coverTier=" + pit.CoverTier
                + " triggerMassKg=" + pit.CoverTier.TriggerMassKg().ToString("F1"));
        }

        // -------------------------------------------------------- depth tier

        [DebugAction(CAT, "Set depth: Shallow",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void DepthShallow() { SetDepth(PitDepthTier.Shallow); }

        [DebugAction(CAT, "Set depth: Deep",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void DepthDeep() { SetDepth(PitDepthTier.Deep); }

        [DebugAction(CAT, "Set depth: Chasm",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void DepthChasm() { SetDepth(PitDepthTier.Chasm); }

        private static void SetDepth(PitDepthTier tier)
        {
            IntVec3 c = UI.MouseCell();
            Building_OpenPit pit = PitAt(c);
            if (pit == null) { NoPit(c); return; }
            pit.DepthTier = tier;
            Log.Message("[RMPitsDebug] DEPTH " + pit.def.defName + " depthTier=" + pit.DepthTier);
        }

        // ------------------------------------------------------------- drive

        [DebugAction(CAT, "Force trigger scan now",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ForceScan()
        {
            IntVec3 c = UI.MouseCell();
            Building_OpenPit pit = PitAt(c);
            if (pit == null) { NoPit(c); return; }
            CompPitCoverTrigger trig = pit.GetComp<CompPitCoverTrigger>();
            if (trig == null) { Log.Message("[RMPitsDebug] NO_TRIGGER_COMP on " + pit.def.defName); return; }
            trig.RunScan();
            Log.Message("[RMPitsDebug] SCAN_DONE " + pit.def.defName
                + " covered=" + pit.Covered + " sprung=" + pit.Sprung);
        }

        [DebugAction(CAT, "Force struggle interval",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ForceStruggle()
        {
            IntVec3 c = UI.MouseCell();
            Building_OpenPit pit = PitAt(c);
            if (pit == null) { NoPit(c); return; }
            int before = pit.OccupantCount;
            pit.RunStruggleInterval();
            Log.Message("[RMPitsDebug] STRUGGLE " + pit.def.defName
                + " occupantsBefore=" + before + " occupantsAfter=" + pit.OccupantCount);
        }

        [DebugAction(CAT, "Advance dig stage",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void AdvanceDigStage()
        {
            IntVec3 c = UI.MouseCell();
            Building_PitDigSite site = SiteAt(c);
            if (site == null)
            {
                Log.Message("[RMPitsDebug] NO_DIGSITE at " + c);
                return;
            }
            CompPitDigStage comp = site.GetComp<CompPitDigStage>();
            if (comp == null) { Log.Message("[RMPitsDebug] NO_DIGSTAGE_COMP on " + site.def.defName); return; }
            string was = site.def.defName + " stages=" + comp.stagesCompleted + "/" + comp.RequiredStages
                + " workLeft=" + comp.workLeftThisStage.ToString("F0");
            comp.AddDigWork(999999f);
            Log.Message("[RMPitsDebug] DIG was[" + was + "] nowAt=" + DescribeCell(c));
        }

        // ------------------------------------------------------------ report

        [DebugAction(CAT, "Report pit state (RAW)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void ReportPit()
        {
            IntVec3 c = UI.MouseCell();
            Map map = Find.CurrentMap;
            Building_OpenPit pit = PitAt(c);
            if (pit == null)
            {
                Building_PitDigSite site = SiteAt(c);
                if (site != null)
                {
                    CompPitDigStage cd = site.GetComp<CompPitDigStage>();
                    Log.Message("[RMPitsDebug] REPORT_DIGSITE def=" + site.def.defName
                        + " id=" + site.ThingID
                        + " pos=" + site.Position
                        + " stagesCompleted=" + (cd == null ? "NO_COMP" : cd.stagesCompleted.ToString())
                        + " requiredStages=" + (cd == null ? "NO_COMP" : cd.RequiredStages.ToString())
                        + " workLeftThisStage=" + (cd == null ? "NO_COMP" : cd.workLeftThisStage.ToString("F0"))
                        + " depthTier=" + (cd == null ? "NO_COMP" : cd.Props.depthTier.ToString())
                        + " openPitDef=" + (cd == null || cd.Props.openPitDef == null ? "NULL" : cd.Props.openPitDef.defName));
                    return;
                }
                NoPit(c);
                return;
            }

            StringBuilder sb = new StringBuilder();
            sb.Append("[RMPitsDebug] REPORT_PIT def=").Append(pit.def.defName);
            sb.Append(" id=").Append(pit.ThingID);
            sb.Append(" pos=").Append(pit.Position);
            sb.Append(" size=").Append(pit.def.size);
            sb.Append(" covered=").Append(pit.Covered);
            sb.Append(" coverTier=").Append(pit.CoverTier);
            sb.Append(" triggerMassKg=").Append(pit.CoverTier.TriggerMassKg().ToString("F1"));
            sb.Append(" depthTier=").Append(pit.DepthTier);
            sb.Append(" sprung=").Append(pit.Sprung);
            sb.Append(" occupants=").Append(pit.OccupantCount);
            sb.Append(" maxOccupants=").Append(pit.MaxOccupants);

            int triggerComps = 0, fittingComps = 0;
            if (pit.AllComps != null)
            {
                for (int i = 0; i < pit.AllComps.Count; i++)
                {
                    if (pit.AllComps[i] is CompPitCoverTrigger) triggerComps++;
                    if (pit.AllComps[i] is CompPitFitting) fittingComps++;
                }
            }
            sb.Append(" triggerCompCount=").Append(triggerComps);
            sb.Append(" fittingCompCount=").Append(fittingComps);
            CompPitFitting fit = pit.GetComp<CompPitFitting>();
            sb.Append(" fitting=").Append(fit == null ? "none" : fit.Props.fittingType.ToString());

            // Standing mass, computed exactly as CompPitCoverTrigger computes it.
            float summed = 0f;
            int standing = 0;
            if (map != null)
            {
                foreach (IntVec3 cell in pit.OccupiedRect())
                {
                    List<Thing> here = cell.GetThingList(map);
                    for (int i = 0; i < here.Count; i++)
                    {
                        if (here[i] is Pawn p && !p.Dead)
                        {
                            standing++;
                            float m = p.GetStatValue(StatDefOf.Mass);
                            summed += m;
                            sb.Append("\n  STANDING ").Append(p.def.defName)
                              .Append(" id=").Append(p.ThingID)
                              .Append(" mass=").Append(m.ToString("F2"))
                              .Append(" bodySize=").Append(p.BodySize.ToString("F2"))
                              .Append(" downed=").Append(p.Downed);
                        }
                    }
                }
            }
            sb.Append("\n  STANDING_COUNT=").Append(standing)
              .Append(" SUMMED_MASS=").Append(summed.ToString("F2"))
              .Append(" THRESHOLD=").Append(pit.CoverTier.TriggerMassKg().ToString("F1"))
              .Append(" WOULD_SPRING=").Append(standing > 0 && summed >= pit.CoverTier.TriggerMassKg());

            foreach (Thing t in pit.GetDirectlyHeldThings())
            {
                if (t is Pawn hp)
                {
                    Hediff pin = hp.health?.hediffSet?.GetFirstHediffOfDef(RMPits_HediffDefOf.RM_PinnedInPit);
                    Hediff exp = hp.health?.hediffSet?.GetFirstHediffOfDef(RMPits_HediffDefOf.RM_PitExposure);
                    Hediff drown = hp.health?.hediffSet?.GetFirstHediffOfDef(RMPits_HediffDefOf.RM_PitDrowning);
                    Hediff tox = hp.health?.hediffSet?.GetFirstHediffOfDef(HediffDefOf.ToxicBuildup);
                    sb.Append("\n  HELD ").Append(hp.def.defName)
                      .Append(" id=").Append(hp.ThingID)
                      .Append(" mass=").Append(hp.GetStatValue(StatDefOf.Mass).ToString("F2"))
                      .Append(" bodySize=").Append(hp.BodySize.ToString("F2"))
                      .Append(" dead=").Append(hp.Dead)
                      .Append(" downed=").Append(hp.Downed)
                      .Append(" healthPct=").Append((hp.health?.summaryHealth?.SummaryHealthPercent ?? -1f).ToString("F3"))
                      .Append(" escapeChance=").Append(PitEscapeUtility.EscapeChance(hp, pit.DepthTier).ToString("F3"))
                      .Append(" pinnedSev=").Append(pin == null ? "none" : pin.Severity.ToString("F3"))
                      .Append(" exposureSev=").Append(exp == null ? "none" : exp.Severity.ToString("F3"))
                      .Append(" drowningSev=").Append(drown == null ? "none" : drown.Severity.ToString("F3"))
                      .Append(" toxicSev=").Append(tox == null ? "none" : tox.Severity.ToString("F3"))
                      .Append(" stunned=").Append(hp.stances != null && hp.stances.stunner != null
                          ? hp.stances.stunner.Stunned.ToString() : "n/a")
                      .Append(" hediffs=[");
                    if (hp.health != null && hp.health.hediffSet != null)
                    {
                        bool first = true;
                        foreach (Hediff h in hp.health.hediffSet.hediffs)
                        {
                            if (!first) sb.Append(',');
                            first = false;
                            sb.Append(h.def.defName).Append(':').Append(h.Severity.ToString("F2"));
                        }
                    }
                    sb.Append(']');
                }
                else
                {
                    sb.Append("\n  HELD_NONPAWN ").Append(t.def.defName);
                }
            }

            Log.Message(sb.ToString());
        }

        private static string DescribeCell(IntVec3 c)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "NO_MAP";
            StringBuilder sb = new StringBuilder();
            foreach (Thing t in c.GetThingList(map))
            {
                if (sb.Length > 0) sb.Append(',');
                sb.Append(t.def.defName);
                if (t is Building_OpenPit p) sb.Append("(depth=").Append(p.DepthTier).Append(")");
            }
            return sb.Length == 0 ? "EMPTY" : sb.ToString();
        }
    }
}
