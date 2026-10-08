using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    public class RM_StuffReflectivity
    {
        public ThingDef stuff;
        public float value = 0.7f;
    }

    // SOLAR_MIRRORS_MOD_DESIGN_1 §3.2. Numbers in the defs are PROVISIONAL.
    public class RM_CompProperties_Mirror : CompProperties
    {
        public float reflectivity = 0.7f;              // used when no stuff row matches
        public List<RM_StuffReflectivity> stuffReflectivity;
        public int spotSize = 1;                        // the spot is the mirror's own size (§2.2)
        public float maxRange = 40f;                    // cells of horizontal throw
        public bool tracks;                             // a heliostat: holds its target while powered
        public bool instantAim;                         // aimed by gizmo, no job (needs power when tracks)
        public int reAimTicks = 600;                    // the re-aim job's work, before the settings dial

        public RM_CompProperties_Mirror()
        {
            compClass = typeof(RM_CompMirror);
        }
    }

    public class RM_CompMirror : ThingComp
    {
        // Saved (design §2.7): the committed surface normal, the requested target and pending work.
        private Vector3 normal = Vector3.zero;
        private IntVec3 target = IntVec3.Invalid;
        private IntVec3 pendingTarget = IntVec3.Invalid;

        // Last light pass, for the inspect pane and rendering. Not saved.
        public float lastSource;
        public float lastDelivered;
        public float lastEfficiency;
        public bool lastFired;
        public bool lastRelayed;
        public IntVec3 lastSpotCenter = IntVec3.Invalid;
        public string lastBlocker;
        public Vector3 lastInDir = Vector3.zero;

        public RM_CompProperties_Mirror Props => (RM_CompProperties_Mirror)props;
        public IntVec3 Target => target;
        public IntVec3 PendingTarget => pendingTarget;
        public bool HasPending => pendingTarget.IsValid;
        public bool HasAim => target.IsValid && normal != Vector3.zero;
        public Vector3 CommittedNormal => normal;

        /// <summary>A tracking heliostat re-aimed during the light pass: keep that normal (design §5 E13).</summary>
        public void CommitNormal(Vector3 n)
        {
            normal = n;
        }

        private CompPowerTrader Power => parent.GetComp<CompPowerTrader>();

        /// <summary>True when this mirror tracks its target right now: a heliostat with power.</summary>
        public bool TrackingNow
        {
            get
            {
                if (!Props.tracks)
                {
                    return false;
                }
                CompPowerTrader p = Power;
                return p == null || p.PowerOn;
            }
        }

        /// <summary>The spot stays on the target: a tracking heliostat, or any mirror when the
        /// "static mirrors sweep" setting is off.</summary>
        public bool HoldsTarget => TrackingNow || !RM_SolarMirrorsSettings.staticSweep;

        public float Reflectivity
        {
            get
            {
                bool found = false;
                float row = 0f;
                if (parent.Stuff != null && Props.stuffReflectivity != null)
                {
                    for (int i = 0; i < Props.stuffReflectivity.Count; i++)
                    {
                        if (Props.stuffReflectivity[i].stuff == parent.Stuff)
                        {
                            found = true;
                            row = Props.stuffReflectivity[i].value;
                            break;
                        }
                    }
                }
                return RM_MirrorKernel.Reflectivity(Props.reflectivity, found, row, RM_SolarMirrorsSettings.reflectivityMultiplier);
            }
        }

        /// <summary>The face's centre in map space, at the nominal face height.</summary>
        public Vector3 FacePoint
        {
            get
            {
                Vector3 c = parent.TrueCenter();
                return new Vector3(c.x, RM_MirrorMath.FaceHeight, c.z);
            }
        }

        public static Vector3 GroundPoint(IntVec3 cell)
        {
            return new Vector3(cell.x + 0.5f, 0f, cell.z + 0.5f);
        }

        public Vector3 DirTo(IntVec3 cell)
        {
            return (GroundPoint(cell) - FacePoint).normalized;
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            RM_MapComponent_MirrorLight.For(parent.Map)?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            RM_MapComponent_MirrorLight.For(map)?.Unregister(this);
        }

        public override void ReceiveCompSignal(string signal)
        {
            base.ReceiveCompSignal(signal);
            // Power on/off and flicks change whether a heliostat tracks.
            if (signal == CompPowerTrader.PowerTurnedOnSignal || signal == CompPowerTrader.PowerTurnedOffSignal
                || signal == "FlickedOn" || signal == "FlickedOff")
            {
                RM_MapComponent_MirrorLight.For(parent.Map)?.RequestPass();
            }
        }

        /// <summary>Gizmo order. Instant for a heliostat that tracks; otherwise a re-aim job.</summary>
        public void OrderAim(IntVec3 cell)
        {
            if (Props.instantAim && TrackingNow)
            {
                CommitAim(cell);
                return;
            }
            pendingTarget = cell;
        }

        public void CancelPending()
        {
            pendingTarget = IntVec3.Invalid;
        }

        public void ClearAim()
        {
            target = IntVec3.Invalid;
            normal = Vector3.zero;
            pendingTarget = IntVec3.Invalid;
            RM_MapComponent_MirrorLight.For(parent.Map)?.RequestPass();
        }

        /// <summary>The re-aim job finished, or a heliostat was aimed. A static mirror commits the
        /// NORMAL its aim computes under the light it gets right now (design §2.7): from then on
        /// its spot follows that normal, and so sweeps when the sun moves.</summary>
        public void CommitAim(IntVec3 cell)
        {
            target = cell;
            pendingTarget = IntVec3.Invalid;
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(parent.Map);
            // The light it gets now: the sun for a collector, or the upstream mirror's beam for a
            // relay (recorded by the last pass even when an un-aimed relay could not fire).
            Vector3 inDir = lastInDir != Vector3.zero ? lastInDir
                : comp != null && comp.TrySun(out Vector3 s, out _) ? s : Vector3.up;
            normal = RM_MirrorMath.Normal(inDir, DirTo(cell));
            comp?.RequestPass();
        }

        /// <summary>The normal to use for light arriving from inDir. A tracking mirror re-aims (and
        /// commits it, so a later power cut freezes it there: design §5 E13). Otherwise the saved one.</summary>
        public Vector3 NormalFor(Vector3 inDir)
        {
            if (HoldsTarget && target.IsValid)
            {
                Vector3 n = RM_MirrorMath.Normal(inDir, DirTo(target));
                if (TrackingNow)
                {
                    normal = n;
                }
                return n;
            }
            return normal;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref normal, "rmMirrorNormal", Vector3.zero);
            Scribe_Values.Look(ref target, "rmMirrorTarget", IntVec3.Invalid);
            Scribe_Values.Look(ref pendingTarget, "rmMirrorPendingTarget", IntVec3.Invalid);
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (parent.Faction != Faction.OfPlayer)
            {
                yield break;
            }
            yield return new Command_Action
            {
                defaultLabel = "RM_SolarMirrors_AimAt".Translate(),
                defaultDesc = (Props.instantAim ? "RM_SolarMirrors_AimAt_DescInstant" : "RM_SolarMirrors_AimAt_DescJob").Translate(),
                icon = TexCommand.Attack,
                action = BeginAimTargeting
            };
            if (target.IsValid || pendingTarget.IsValid)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RM_SolarMirrors_ClearAim".Translate(),
                    defaultDesc = "RM_SolarMirrors_ClearAim_Desc".Translate(),
                    icon = TexCommand.ClearPrioritizedWork,
                    action = ClearAim
                };
            }
        }

        private void BeginAimTargeting()
        {
            TargetingParameters tp = new TargetingParameters
            {
                canTargetLocations = true,
                canTargetBuildings = true,
                canTargetPawns = false,
                canTargetItems = false
            };
            Map map = parent.Map;
            Find.Targeter.BeginTargeting(tp,
                t => OrderAim(t.Cell),
                t => DrawPreview(t.Cell),
                t => t.Cell.InBounds(map) && HorizontalDistTo(t.Cell) <= Props.maxRange,
                null, null, null, true,
                t => Widgets.MouseAttachedLabel(PreviewLabel(t.Cell)));
        }

        private float HorizontalDistTo(IntVec3 cell)
        {
            Vector3 f = FacePoint;
            Vector3 g = GroundPoint(cell);
            return Mathf.Sqrt((g.x - f.x) * (g.x - f.x) + (g.z - f.z) * (g.z - f.z));
        }

        private readonly List<IntVec3> previewCells = new List<IntVec3>();

        private void DrawPreview(IntVec3 cell)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(parent.Map);
            if (comp == null || !cell.InBounds(parent.Map))
            {
                return;
            }
            previewCells.Clear();
            comp.SpotCells(this, cell, previewCells);
            bool clear = comp.FirstBlocker(this, cell) == null;
            GenDraw.DrawLineBetween(parent.TrueCenter(), GroundPoint(cell), clear ? SimpleColor.Yellow : SimpleColor.Red);
            GenDraw.DrawFieldEdges(previewCells, clear ? Color.yellow : Color.red);
        }

        private string PreviewLabel(IntVec3 cell)
        {
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(parent.Map);
            if (comp == null || !cell.InBounds(parent.Map))
            {
                return "";
            }
            string blocker = comp.FirstBlocker(this, cell);
            if (blocker != null)
            {
                return "RM_SolarMirrors_Preview_Blocked".Translate(blocker);
            }
            if (!comp.TrySun(out Vector3 s, out _))
            {
                return "RM_SolarMirrors_Preview_NoSun".Translate();
            }
            float eff = RM_MirrorMath.Efficiency(s, DirTo(cell));
            return "RM_SolarMirrors_Preview_Eff".Translate(eff.ToStringPercent());
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            if (pendingTarget.IsValid)
            {
                sb.Append("RM_SolarMirrors_Inspect_Pending".Translate(pendingTarget.ToString()));
            }
            else if (!target.IsValid)
            {
                sb.Append("RM_SolarMirrors_Inspect_Unaimed".Translate());
            }
            else
            {
                sb.Append("RM_SolarMirrors_Inspect_Target".Translate(target.ToString()));
            }
            if (Props.tracks)
            {
                sb.AppendLine();
                sb.Append((TrackingNow ? "RM_SolarMirrors_Inspect_Tracking" : "RM_SolarMirrors_Inspect_Frozen").Translate());
            }
            if (target.IsValid)
            {
                sb.AppendLine();
                if (!lastFired)
                {
                    sb.Append(lastBlocker != null
                        ? "RM_SolarMirrors_Inspect_Blocked".Translate(lastBlocker)
                        : "RM_SolarMirrors_Inspect_Dark".Translate());
                }
                else
                {
                    sb.Append("RM_SolarMirrors_Inspect_Light".Translate(lastDelivered.ToStringPercent(),
                        lastEfficiency.ToStringPercent(),
                        (lastRelayed ? "RM_SolarMirrors_Inspect_FromMirror" : "RM_SolarMirrors_Inspect_FromSun").Translate()));
                    if (lastBlocker != null)
                    {
                        sb.AppendLine();
                        sb.Append("RM_SolarMirrors_Inspect_PartBlocked".Translate(lastBlocker));
                    }
                }
            }
            return sb.ToString();
        }
    }
}
