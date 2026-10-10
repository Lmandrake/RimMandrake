using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlameStatues
{
    // FLAME_STATUES_MOD_BUILD_1, statue_mods_spec.md §2.2. Vanilla Graphic_Flicker reads only the FIRST
    // CompFireOverlayBase on a thing, so stacked CompProperties_FireOverlay all draw at one offset; this comp draws a
    // whole SET of flames, each at its own offset, out of phase. Lit = has fuel (or no refuelable) AND the settings.
    public class RM_FlamePoint
    {
        public Vector3 offset;      // cells from parent.DrawPos, same convention as CompProperties_FireOverlay.offset
        public float size = 0.4f;
    }

    public class RM_CompProperties_FlamePoints : CompProperties
    {
        public List<RM_FlamePoint> points = new List<RM_FlamePoint>();
        public bool qualityScalingEnabled = true;
        public int fireGlowFleckIntervalTicks = 90;    // 0 = no flecks

        public RM_CompProperties_FlamePoints()
        {
            compClass = typeof(RM_CompFlamePoints);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (points == null || points.Count == 0)
            {
                yield return "RM_CompProperties_FlamePoints has no points";
            }
            if (parentDef.tickerType != TickerType.Normal)
            {
                yield return "RM_CompProperties_FlamePoints needs tickerType Normal (flecks, free-burn refill)";
            }
        }
    }

    /// <summary>Graphic_Flicker with its frames exposed, so each flame point can pick its own frame.</summary>
    public class RM_FireFrames : Graphic_Flicker
    {
        public Graphic[] Frames => subGraphics;
    }

    public class RM_CompFlamePoints : ThingComp, IThingGlower
    {
        private const float AltitudeBump = 0.03658537f;   // CompFireOverlay.PostDraw's own lift
        private const float MaxJitter = 0.05f;            // Graphic_Flicker.MaxOffset
        private static RM_FireFrames fireFrames;

        private CompRefuelable refuelable;
        private CompQuality quality;
        private CompGlower glower;
        private ThingComp pipeTrader;            // PipeSystem.CompResourceTrader, present only when the Helixien patch applied
        private float lastFuel = -1f;

        // Helixien link (spec §2.3). Member MEASURED 2026-10-10 by ilspycmd on VEF 1.6 PipeSystem.dll:
        // `public bool ResourceOn { get; set; }` on PipeSystem.CompResourceTrader. A failed lookup logs once and the
        // pipenet counts as absent; manual refuel still works.
        private static bool pipeResolved;
        private static Type pipeTraderType;
        private static PropertyInfo pipeResourceOn;

        private static void ResolvePipe()
        {
            if (pipeResolved) return;
            pipeResolved = true;
            pipeTraderType = GenTypes.GetTypeInAnyAssembly("PipeSystem.CompResourceTrader");
            if (pipeTraderType == null) return;   // VE Framework not loaded: no pipenet, not an error
            pipeResourceOn = pipeTraderType.GetProperty("ResourceOn", BindingFlags.Public | BindingFlags.Instance);
            if (pipeResourceOn == null || pipeResourceOn.PropertyType != typeof(bool))
            {
                Log.Warning("[FlameStatues] PipeSystem.CompResourceTrader has no bool ResourceOn; Helixien link off, manual refuel still works.");
                pipeResourceOn = null;
            }
        }

        /// <summary>True while the Helixien pipenet trader on this statue is receiving gas.</summary>
        public bool PipeReceiving
        {
            get
            {
                if (pipeTrader == null || pipeResourceOn == null) return false;
                try { return (bool)pipeResourceOn.GetValue(pipeTrader, null); }
                catch (Exception) { return false; }
            }
        }

        public RM_CompProperties_FlamePoints Props => (RM_CompProperties_FlamePoints)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            refuelable = parent.GetComp<CompRefuelable>();
            quality = parent.GetComp<CompQuality>();
            glower = parent.GetComp<CompGlower>();
            ResolvePipe();
            pipeTrader = null;
            if (pipeTraderType != null && pipeResourceOn != null)
            {
                foreach (ThingComp c in parent.AllComps)
                {
                    if (pipeTraderType.IsInstanceOfType(c)) { pipeTrader = c; break; }
                }
            }
        }

        /// <summary>Fuel state only (flames and glow apply their own settings gates).</summary>
        public bool Burning => RM_FlameKernel.Burning(refuelable != null, refuelable != null && refuelable.HasFuel, FlameStatuesSettings.consumeFuel);

        public bool FlamesShown => RM_FlameKernel.FlamesShown(Burning, FlameStatuesSettings.flamePoints);

        // CompGlower polls every sibling IThingGlower; CompRefuelable already darkens it when dry.
        public bool ShouldBeLitNow()
        {
            return RM_FlameKernel.LitNow(Burning, FlameStatuesSettings.flamePoints, FlameStatuesSettings.glow);
        }

        public float QualityScale => RM_FlameKernel.QualityScale(Props.qualityScalingEnabled, FlameStatuesSettings.qualityScaling,
            quality == null ? -1 : (int)quality.Quality);

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned)
            {
                return;
            }
            // a settings change mid-game reaches the glow here (CompGlower only re-polls on comp signals)
            if (glower != null && parent.IsHashIntervalTick(RM_FlameKernel.PollInterval))
            {
                glower.UpdateLit(parent.Map);
            }
            // "statues never run out": keep the tank topped so CompRefuelable never reports dry.
            float topUp = RM_FlameKernel.RefillAmount(FlameStatuesSettings.consumeFuel, refuelable != null,
                parent.IsHashIntervalTick(RM_FlameKernel.PollInterval), refuelable != null ? refuelable.Fuel : 0f,
                refuelable != null ? refuelable.Props.fuelCapacity : 0f);
            if (topUp > 0f)
            {
                refuelable.Refuel(topUp);
            }
            // Helixien link: a statue on a live pipe gives back what the tank burned since the last poll.
            if (refuelable != null && pipeTrader != null && parent.IsHashIntervalTick(RM_FlameKernel.PollInterval))
            {
                float back = RM_FlameKernel.PipeRefund(FlameStatuesSettings.helixienLink, PipeReceiving,
                    FlameStatuesSettings.consumeFuel, true, refuelable.Fuel, lastFuel);
                if (back > 0f)
                {
                    refuelable.Refuel(back);
                }
                lastFuel = refuelable.Fuel;
            }
            int interval = Props.fireGlowFleckIntervalTicks;
            if (interval <= 0 || !FlameStatuesSettings.flecks || !FlamesShown)
            {
                return;
            }
            float q = QualityScale;
            int scaled = RM_FlameKernel.FleckInterval(interval, q);
            for (int i = 0; i < Props.points.Count; i++)
            {
                // per-point phase so the points do not puff in unison
                if (!RM_FlameKernel.FleckDue(Find.TickManager.TicksGame, parent.thingIDNumber, i, scaled))
                {
                    continue;
                }
                RM_FlamePoint p = Props.points[i];
                Vector3 c = parent.DrawPos + p.offset;
                c.x += Rand.Range(-0.1f, 0.1f);
                c.z += Rand.Range(-0.1f, 0.1f);
                FleckMaker.ThrowFireGlow(c, parent.Map, p.size * q);
            }
        }

        public override void PostDraw()
        {
            base.PostDraw();
            if (!FlamesShown || Props.points.Count == 0)
            {
                return;
            }
            if (fireFrames == null)
            {
                fireFrames = (RM_FireFrames)GraphicDatabase.Get<RM_FireFrames>("Things/Special/Fire",
                    ShaderDatabase.TransparentPostLight, Vector2.one, Color.white);
            }
            Graphic[] frames = fireFrames.Frames;
            if (frames == null || frames.Length == 0)
            {
                return;
            }
            float q = QualityScale;
            int id = parent.thingIDNumber;
            int ticks = RM_FlameKernel.AnimTicks(Find.TickManager.TicksGame, id);
            Vector3 basePos = parent.DrawPos;
            basePos.y += AltitudeBump;
            int radial = GenRadial.RadialPattern.Length;
            for (int i = 0; i < Props.points.Count; i++)
            {
                RM_FlamePoint p = Props.points[i];
                int frame = RM_FlameKernel.FrameIndex(ticks, id, i, frames.Length);
                Vector3 jitter = GenRadial.RadialPattern[RM_FlameKernel.JitterIndex(ticks, i, radial)].ToVector3()
                                 / GenRadial.MaxRadialPatternRadius * MaxJitter;
                float s = p.size * q;
                Vector3 pos = basePos + p.offset + jitter * s;
                Matrix4x4 m = default(Matrix4x4);
                m.SetTRS(pos, Quaternion.identity, new Vector3(s, 1f, s));
                Graphics.DrawMesh(MeshPool.plane10, m, frames[frame].MatSingle, 0);
            }
        }
    }
}
