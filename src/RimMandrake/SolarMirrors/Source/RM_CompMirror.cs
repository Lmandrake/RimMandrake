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
        public bool ancient;                            // design §3.4: turns only between its detents; seized until repaired
        public int repairTicks = 1500;                  // freeing an ancient mirror's bearings (plus one component)
        public int cleanTicks = 300;                    // the cleaning job (design §3.2 dust)

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
        // Saved (SOLAR_MIRRORS_BUILD_1): dust (§3.2) and the ancient-field state (§3.4).
        private float dust;
        private bool seized;
        private bool repairRequested;
        private List<IntVec3> detents = new List<IntVec3>();
        private int detentIndex = -1;

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

        public float Dust => dust;
        public bool IsAncient => Props.ancient;
        public bool Seized => seized;
        public bool RepairRequested => seized && repairRequested;
        public IReadOnlyList<IntVec3> Detents => detents;
        public int DetentIndex => detentIndex;
        public bool NeedsCleaning => RM_SolarMirrorsSettings.dustEnabled && dust >= RM_MirrorDustWeathersDef.CleanAt;

        /// <summary>Who may order this mirror about: its owner, or anyone for an unowned ancient mirror.</summary>
        public bool Orderable => parent.Faction == Faction.OfPlayer || Props.ancient && parent.Faction == null;

        public void AddDust(float delta)
        {
            dust = Mathf.Clamp01(dust + delta);
        }

        public void Clean()
        {
            dust = 0f;
            RM_MapComponent_MirrorLight.For(parent.Map)?.RequestPass();
        }

        /// <summary>Mapgen: make this an ancient field mirror, seized, on detent `start`.</summary>
        public void SetAncient(List<IntVec3> detentCells, int start, bool isSeized)
        {
            detents = new List<IntVec3>(detentCells);
            seized = isSeized;
            repairRequested = false;
            detentIndex = -1;
            if (start >= 0 && start < detents.Count)
            {
                CommitAim(detents[start]);
            }
        }

        /// <summary>Mapgen's solver: put the mirror on a detent without any side effect beyond its own state.</summary>
        public void SetDetentDirect(int k)
        {
            if (k < 0 || k >= detents.Count)
            {
                return;
            }
            target = detents[k];
            detentIndex = k;
            pendingTarget = IntVec3.Invalid;
        }

        public void FinishRepair()
        {
            seized = false;
            repairRequested = false;
        }

        public void OrderDetent(int k)
        {
            if (seized || k < 0 || k >= detents.Count)
            {
                return;
            }
            pendingTarget = detents[k];
        }

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
        public bool HoldsTarget => Props.ancient || TrackingNow || !RM_SolarMirrorsSettings.staticSweep;

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
                float r = RM_MirrorKernel.Reflectivity(Props.reflectivity, found, row, RM_SolarMirrorsSettings.reflectivityMultiplier);
                return RM_SolarMirrorsSettings.dustEnabled ? r * RM_MirrorKernel.DustFactor(dust, RM_MirrorDustWeathersDef.MaxLoss) : r;
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
            if (Props.ancient)
            {
                int was = detentIndex;
                detentIndex = detents.IndexOf(cell);
                if (was >= 0 && was != detentIndex && parent.Spawned)
                {
                    RM_MapComponent_MirrorField.For(parent.Map)?.Notify_ReAimed(this);
                }
            }
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
            Scribe_Values.Look(ref dust, "rmMirrorDust", 0f);
            Scribe_Values.Look(ref seized, "rmMirrorSeized", false);
            Scribe_Values.Look(ref repairRequested, "rmMirrorRepairRequested", false);
            Scribe_Values.Look(ref detentIndex, "rmMirrorDetent", -1);
            Scribe_Collections.Look(ref detents, "rmMirrorDetents", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && detents == null)
            {
                detents = new List<IntVec3>();
            }
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!Orderable)
            {
                yield break;
            }
            if (Props.ancient)
            {
                foreach (Gizmo g in AncientGizmos())
                {
                    yield return g;
                }
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

        private IEnumerable<Gizmo> AncientGizmos()
        {
            if (seized)
            {
                yield return new Command_Toggle
                {
                    defaultLabel = "RM_SolarMirrors_Repair".Translate(),
                    defaultDesc = "RM_SolarMirrors_Repair_Desc".Translate(),
                    icon = RM_MirrorTex.Repair,
                    isActive = () => repairRequested,
                    toggleAction = () => repairRequested = !repairRequested
                };
                yield break;
            }
            for (int k = 0; k < detents.Count; k++)
            {
                int d = k;
                Command_Action c = new Command_Action
                {
                    defaultLabel = "RM_SolarMirrors_Detent".Translate(d + 1),
                    defaultDesc = "RM_SolarMirrors_Detent_Desc".Translate(d + 1, detents[d].ToString()),
                    icon = TexCommand.Attack,
                    action = () => OrderDetent(d)
                };
                if (d == detentIndex && !pendingTarget.IsValid)
                {
                    c.Disable("RM_SolarMirrors_Detent_Current".Translate());
                }
                else if (pendingTarget.IsValid && pendingTarget == detents[d])
                {
                    c.Disable("RM_SolarMirrors_Detent_Pending".Translate());
                }
                yield return c;
            }
        }

        /// <summary>Design §3.4 "readable": selecting an ancient mirror ghosts every detent's spot at once.</summary>
        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            if (!Props.ancient || !parent.Spawned)
            {
                return;
            }
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(parent.Map);
            if (comp == null)
            {
                return;
            }
            for (int k = 0; k < detents.Count; k++)
            {
                previewCells.Clear();
                comp.SpotCells(this, detents[k], previewCells);
                Color col = k == detentIndex ? Color.yellow : pendingTarget.IsValid && pendingTarget == detents[k] ? Color.cyan : Color.white;
                GenDraw.DrawFieldEdges(previewCells, col);
                GenDraw.DrawLineBetween(parent.TrueCenter(), GroundPoint(detents[k]), k == detentIndex ? SimpleColor.Yellow : SimpleColor.White);
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
            if (Props.ancient)
            {
                sb.Append((seized ? "RM_SolarMirrors_Inspect_Seized" : "RM_SolarMirrors_Inspect_Freed").Translate());
                sb.AppendLine();
                if (detentIndex >= 0)
                {
                    sb.Append("RM_SolarMirrors_Inspect_Detent".Translate(detentIndex + 1, detents.Count));
                    sb.AppendLine();
                }
            }
            if (RM_SolarMirrorsSettings.dustEnabled && dust > 0.01f)
            {
                sb.Append("RM_SolarMirrors_Inspect_Dust".Translate(dust.ToStringPercent(),
                    (1f - RM_MirrorKernel.DustFactor(dust, RM_MirrorDustWeathersDef.MaxLoss)).ToStringPercent()));
                sb.AppendLine();
            }
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
