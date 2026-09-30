using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 Part 3 — the Cloud Repulsor.
    //
    // Warms up while powered; once warm, every 250 ticks it re-asserts its
    // effect for holdTicks, so the effect dies on its own within holdTicks of
    // power loss, a flick-off, a breakdown, uninstalling or destruction — no
    // permanent condition is ever left behind:
    //   - on a map whose biome carries RM_ContagionSkyExtension: forces the
    //     Burn (RM_MapComponent_ContagionSky.StartBurn, causer = this device),
    //     with the Burn's full UV pressure — "a man-made local Burn";
    //   - on any other surface map: RM_RepulsorClearSky, a vanilla
    //     GameCondition_ForceWeather holding plain Clear — rain/fog-class
    //     weather is cancelled while it runs. Never touches the Burn there.
    // Skipped in vacuum (space) and underground (no sky to repel).
    // The purple beam is drawn at runtime while the effect is live (owner
    // note on the art: "that must be added by the game later when it is on"),
    // using vanilla's own orbital-beam texture tinted violet.
    public class CompProperties_CloudRepulsor : CompProperties
    {
        public int warmupTicks = 2500;
        public int holdTicks = 750;
        public float beamWidth = 1.6f;
        public float beamLength = 14f;
        public Color beamColor = new Color(0.72f, 0.35f, 1f, 0.85f);

        public CompProperties_CloudRepulsor()
        {
            compClass = typeof(CompCloudRepulsor);
        }
    }

    [StaticConstructorOnStartup]
    public class CompCloudRepulsor : ThingComp
    {
        private int warmTicks;

        private static readonly Material BeamMat =
            MaterialPool.MatFrom("Other/OrbitalBeam", ShaderDatabase.MoteGlow, MapMaterialRenderQueues.OrbitalBeam);
        private static readonly MaterialPropertyBlock MatPropertyBlock = new MaterialPropertyBlock();

        public CompProperties_CloudRepulsor Props => (CompProperties_CloudRepulsor)props;

        private CompPowerTrader Power => parent.GetComp<CompPowerTrader>();

        private bool Powered => Power == null || Power.PowerOn;

        public bool Warm => warmTicks >= Props.warmupTicks;

        public bool Emitting => RM_ContagionSettings.cloudRepulsorEnabled && parent.Spawned && Powered && Warm && SkyReachable(parent.Map);

        private static bool SkyReachable(Map map)
        {
            if (map == null) return false;
            if (map.Biome != null && map.Biome.inVacuum) return false;
            if (map.generatorDef != null && map.generatorDef.isUnderground) return false;
            return true;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref warmTicks, "warmTicks", 0);
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(RM_ContagionSky.Interval)) return;
            if (!RM_ContagionSettings.cloudRepulsorEnabled || !Powered)
            {
                warmTicks = 0;
                return;
            }
            if (!Warm)
            {
                warmTicks += RM_ContagionSky.Interval;
                return;
            }
            Map map = parent.Map;
            if (!SkyReachable(map)) return;

            RM_MapComponent_ContagionSky sky = map.GetComponent<RM_MapComponent_ContagionSky>();
            if (RM_ContagionSky.ExtFor(map) != null && sky != null)
            {
                // Forced Burn: this is the device's point on a Contagion map,
                // so it holds even with the natural Burn schedule switched off.
                sky.StartBurn(Props.holdTicks, parent);
                return;
            }

            GameConditionDef clearDef = RM_ContagionSkyDefOf.RM_RepulsorClearSky;
            GameCondition cond = null;
            foreach (GameCondition c in map.gameConditionManager.ActiveConditions)
            {
                if (c.def == clearDef) { cond = c; break; }
            }
            if (cond == null)
            {
                cond = GameConditionMaker.MakeCondition(clearDef, Props.holdTicks);
                cond.conditionCauser = parent;
                map.gameConditionManager.RegisterCondition(cond);
            }
            else if (cond.TicksLeft < Props.holdTicks)
            {
                cond.TicksLeft = Props.holdTicks;
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_ContagionSettings.cloudRepulsorEnabled) return "Disabled in Mod Settings.";
            if (!Powered) return "Unpowered.";
            if (!Warm) return "Warming up: " + (Props.warmupTicks - warmTicks).ToStringTicksToPeriod();
            if (!SkyReachable(parent.Map)) return "No sky here to repel.";
            return RM_ContagionSky.ExtFor(parent.Map) != null
                ? "Holding the storm open: the Burn is forced."
                : "Holding the sky clear.";
        }

        public override void PostDraw()
        {
            base.PostDraw();
            if (!Emitting) return;
            Vector3 drawPos = parent.DrawPos;
            float len = Props.beamLength;
            Vector3 center = drawPos + new Vector3(0f, 0f, len * 0.5f);
            center.y = AltitudeLayer.MetaOverlays.AltitudeFor();
            Color color = Props.beamColor;
            color.a *= 0.9f + Mathf.Sin(Find.TickManager.TicksGame * 0.1f) * 0.1f;
            MatPropertyBlock.SetColor(ShaderPropertyIDs.Color, color);
            Matrix4x4 matrix = default(Matrix4x4);
            matrix.SetTRS(center, Quaternion.identity, new Vector3(Props.beamWidth, 1f, len));
            Graphics.DrawMesh(MeshPool.plane10, matrix, BeamMat, 0, null, 0, MatPropertyBlock);
        }
    }
}
