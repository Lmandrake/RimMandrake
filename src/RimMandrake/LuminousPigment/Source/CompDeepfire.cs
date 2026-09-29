using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.1-§3.3, §10 step 5. Injected into every qualifying ThingDef by
    // CompInjector_Deepfire.cs (Dub's Paint Shop's PaintableDefsInit pattern
    // the spec names) — never added by hand in a def's own XML.
    public class CompProperties_Deepfire : CompProperties
    {
        public CompProperties_Deepfire()
        {
            compClass = typeof(CompDeepfire);
        }
    }

    public class CompDeepfire : ThingComp
    {
        public const int MaxCoats = 3;

        public int coats;

        public CompProperties_Deepfire Props => (CompProperties_Deepfire)props;

        public bool CanAddCoat => coats < MaxCoats;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            RefreshLight();
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            MapComponent_DeepfireLights.Get(map)?.DeregisterThingLight(parent);
            base.PostDeSpawn(map, mode);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref coats, "deepfireCoats", 0);
        }

        // ThingWithComps.Notify_ColorChanged() (Verse/ThingWithComps.cs)
        // already calls this on every comp whenever a Building's paint or a
        // CompColorable's colour changes -- vanilla dye, Dub's Paint Shop,
        // Character Editor and Self Dyeing all end there (spec §3.1), so no
        // Harmony patch is needed for "paint it afterwards -> glow follows".
        public override void Notify_ColorChanged()
        {
            base.Notify_ColorChanged();
            RefreshLight();
        }

        public void AddCoat()
        {
            if (!CanAddCoat) return;
            coats++;
            RefreshLight();
        }

        // Spec §3.3: "clears coats (no refund)".
        public void RemoveAllCoats()
        {
            if (coats == 0) return;
            coats = 0;
            RefreshLight();
        }

        public void RefreshLight()
        {
            if (parent?.Spawned != true) return;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(parent.Map);
            if (mc == null) return;

            if (coats <= 0)
            {
                mc.DeregisterThingLight(parent);
                return;
            }

            Color color = DeepfireColorUtility.GlowColorFor(parent.DrawColor, coats);
            float radius = DeepfireColorUtility.RadiusForCoats(coats);
            mc.RegisterThingLight(parent, color, radius);
        }
    }
}
