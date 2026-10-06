using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §3.2 (sun-stone) and §5 E1 (solar furnace). A receiver reads
    // the brightest mirror light on its footprint each pass and keeps a lit/unlit state with
    // hysteresis (§3.4), so a flicker of dust does not toggle it. Light is mirror light only:
    // plain sun never lights a receiver, so a sun-stone is a test for "a mirror reaches here".
    public class RM_CompProperties_LightReceiver : CompProperties
    {
        public float litAt = 0.5f;              // PROVISIONAL
        public float unlitBelow = 0.35f;        // PROVISIONAL
        public bool gatesBills;                 // a workbench: bills only while lit (the solar furnace)

        public RM_CompProperties_LightReceiver()
        {
            compClass = typeof(RM_CompLightReceiver);
        }
    }

    public class RM_CompLightReceiver : ThingComp
    {
        private bool lit;
        private float lastLight;

        public RM_CompProperties_LightReceiver Props => (RM_CompProperties_LightReceiver)props;
        public bool Lit => lit;
        public float LastLight => lastLight;

        /// <summary>For a bill-gated bench: may it work now? Off in settings = never (an inert
        /// building, design §3.5 all-off).</summary>
        public bool BillsAllowed => RM_SolarMirrorsSettings.solarFurnace && lit;

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

        public void UpdateLight(RM_MapComponent_MirrorLight comp)
        {
            float best = 0f;
            foreach (IntVec3 c in parent.OccupiedRect())
            {
                best = Mathf.Max(best, comp.LightAt(c));
            }
            lastLight = best;
            lit = RM_MirrorMath.Hysteresis(lit, best, Props.litAt, Props.unlitBelow);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lit, "rmReceiverLit", false);
        }

        public override string CompInspectStringExtra()
        {
            string s = (lit ? "RM_SolarMirrors_Receiver_Lit" : "RM_SolarMirrors_Receiver_Unlit")
                .Translate(lastLight.ToStringPercent(), Props.litAt.ToStringPercent());
            if (Props.gatesBills)
            {
                s += "\n" + (BillsAllowed ? "RM_SolarMirrors_Furnace_Working" : "RM_SolarMirrors_Furnace_Idle").Translate();
            }
            return s;
        }
    }
}
