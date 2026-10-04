using System.Collections.Generic;
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

        public RM_CompProperties_FlamePoints Props => (RM_CompProperties_FlamePoints)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            refuelable = parent.GetComp<CompRefuelable>();
            quality = parent.GetComp<CompQuality>();
            glower = parent.GetComp<CompGlower>();
        }

        /// <summary>Fuel state only (flames and glow apply their own settings gates).</summary>
        public bool Burning => refuelable == null || refuelable.HasFuel || !FlameStatuesSettings.consumeFuel;

        public bool FlamesShown => Burning && FlameStatuesSettings.flamePoints;

        // CompGlower polls every sibling IThingGlower; CompRefuelable already darkens it when dry.
        public bool ShouldBeLitNow()
        {
            return FlameStatuesSettings.glow && FlameStatuesSettings.flamePoints && Burning;
        }

        public float QualityScale
        {
            get
            {
                if (!Props.qualityScalingEnabled || !FlameStatuesSettings.qualityScaling || quality == null)
                {
                    return 1f;
                }
                switch (quality.Quality)
                {
                    case QualityCategory.Awful: return 0.5f;
                    case QualityCategory.Poor: return 0.7f;
                    case QualityCategory.Good: return 1.2f;
                    case QualityCategory.Excellent: return 1.4f;
                    case QualityCategory.Masterwork: return 1.7f;
                    case QualityCategory.Legendary: return 2f;
                    default: return 1f;
                }
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned)
            {
                return;
            }
            // a settings change mid-game reaches the glow here (CompGlower only re-polls on comp signals)
            if (glower != null && parent.IsHashIntervalTick(250))
            {
                glower.UpdateLit(parent.Map);
            }
            // "statues never run out": keep the tank topped so CompRefuelable never reports dry.
            if (!FlameStatuesSettings.consumeFuel && refuelable != null && parent.IsHashIntervalTick(250)
                && refuelable.Fuel < refuelable.Props.fuelCapacity)
            {
                refuelable.Refuel(refuelable.Props.fuelCapacity - refuelable.Fuel);
            }
            int interval = Props.fireGlowFleckIntervalTicks;
            if (interval <= 0 || !FlameStatuesSettings.flecks || !FlamesShown)
            {
                return;
            }
            float q = QualityScale;
            int scaled = Mathf.Max(10, Mathf.RoundToInt(interval / q));
            for (int i = 0; i < Props.points.Count; i++)
            {
                // per-point phase so the points do not puff in unison
                if ((Find.TickManager.TicksGame + parent.thingIDNumber + i * 37) % scaled != 0)
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
            int ticks = Find.TickManager.TicksGame + Mathf.Abs(id ^ 0x80FD52);
            Vector3 basePos = parent.DrawPos;
            basePos.y += AltitudeBump;
            int radial = GenRadial.RadialPattern.Length;
            for (int i = 0; i < Props.points.Count; i++)
            {
                RM_FlamePoint p = Props.points[i];
                int step = ticks / 15 + i * 7;
                int frame = Mathf.Abs(step ^ (id * 391 + i * 131)) % frames.Length;
                Vector3 jitter = GenRadial.RadialPattern[Mathf.Abs(step + i * 3) % radial].ToVector3()
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
