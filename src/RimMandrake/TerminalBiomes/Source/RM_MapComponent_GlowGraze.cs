using System.Collections.Generic;
using RimMandrake.Shared;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // SUN_SPHERE_GRAZE_PERSIST_1 / LIGHT_LEDGER_ONE_1. What a glow-grazer (the suulk) has eaten off each
    // light, in cells of radius, Scribed so a save keeps it. It reaches the light as the ledger's
    // "tb.graze" subtraction, composed with everything else that sizes the light — before this, the
    // feed wrote GlowRadius directly and a sun-sphere's 60-tick culture step put it straight back, and
    // a reload restored every grazed lamp. Grazing never heals on its own (the behaviour before this
    // change); the light is fed out when what is left falls to the race's destroyBelowRadius.
    public class RM_MapComponent_GlowGraze : MapComponent
    {
        private const string Owner = "tb.graze";

        private Dictionary<Thing, float> graze = new Dictionary<Thing, float>();
        private List<Thing> tmpThings;
        private List<float> tmpValues;

        public RM_MapComponent_GlowGraze(Map map) : base(map) { }

        /// <summary>Takes <paramref name="cells"/> more off this light and returns the radius left.</summary>
        public float Graze(Thing t, CompGlower g, float cells)
        {
            graze.TryGetValue(t, out float had);
            // never store more than the light has to give: a grazed light that later grows back
            // (a sphere maturing) is not owed an ever-growing debt
            float taken = System.Math.Min(had + cells, LightLedger.Scaled(g));
            graze[t] = taken;
            LightLedger.SetSub(g, Owner, taken);
            return LightLedger.Effective(g);
        }

        public void Forget(Thing t)
        {
            graze.Remove(t);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Reassert();
        }

        private void Reassert()
        {
            var dead = new List<Thing>();
            foreach (KeyValuePair<Thing, float> kv in graze)
            {
                Thing t = kv.Key;
                CompGlower g = t?.TryGetComp<CompGlower>();
                if (t == null || t.Destroyed || g == null) { dead.Add(t); continue; }
                LightLedger.SetSub(g, Owner, kv.Value);
            }
            for (int i = 0; i < dead.Count; i++) graze.Remove(dead[i]);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving) graze.RemoveAll(kv => kv.Key == null || kv.Key.Destroyed);
            Scribe_Collections.Look(ref graze, "rmGlowGraze", LookMode.Reference, LookMode.Value, ref tmpThings, ref tmpValues);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (graze == null) graze = new Dictionary<Thing, float>();
                graze.RemoveAll(kv => kv.Key == null);
            }
        }
    }
}
