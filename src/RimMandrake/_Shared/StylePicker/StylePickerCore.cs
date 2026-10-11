using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

// _Shared/StylePicker (hose port step 1, design FINAL §3.8 / v2 §5.2 M4): the def-agnostic half of the per-build style
// picker, linked into GimmeSomeSlack (overhead-line anchors) and FlowWorks (the hose reel). Every type here is INTERNAL, so
// each assembly carries its own copy and its own registry; each mod declares its own thin [HarmonyPatch] classes that call
// one instance's patch bodies below with its own registered defs and its own default look. Never name these types by string.
// What stays OUT of here (G2.3): GSS's bracket-offset injector and anything reading GSS's AerialMaterials.
namespace RimMandrake.Shared.StylePicker
{
    /// <summary>
    /// One mod's style registry: which ThingDefs are styled, their ThingStyleDef per look, the last menu pick per build button
    /// (session only), and the five patch bodies (build-button menu, designator style getter, copy carries style, legacy
    /// unstyled reads as default, frame keeps style). The look is stored on each building in the engine's own style field
    /// (CompStyleable); a building with no stored style READS as the default look's style and is never written.
    /// </summary>
    internal sealed class StylePickerCore
    {
        private readonly Dictionary<ThingDef, ThingStyleDef[]> byDef = new Dictionary<ThingDef, ThingStyleDef[]>();
        private readonly Dictionary<ThingStyleDef, string> lookOf = new Dictionary<ThingStyleDef, string>();
        private readonly Dictionary<ThingDef, string> lastPicked = new Dictionary<ThingDef, string>();
        private readonly string[] looks;
        private readonly Func<string> defaultLook;
        private readonly Func<string, string, bool, string, string> resolve;
        private readonly string tag;

        /// <summary>State read: style defs missing at startup (each a config error, not a silent fallback).</summary>
        public readonly List<string> Missing = new List<string>();
        /// <summary>State read: picks made through the menu or the probe this session.</summary>
        public int picks;
        /// <summary>State read: built things whose style the Frame guard had to restore.</summary>
        public int restored;
        /// <summary>Lock-free fast path for the hot Thing.StyleDef postfix, indexed by ThingDef.index.</summary>
        public bool[] styled;

        /// <param name="tag">log prefix, e.g. "[GimmeSomeSlack]"</param>
        /// <param name="looks">menu order of the looks</param>
        /// <param name="defaultLook">the look unstyled things draw in and new buttons start on (the mod's own setting)</param>
        /// <param name="resolve">(lastPicked, defaultLook, styleOverridden, copiedLook) -> look the button hands the designator</param>
        public StylePickerCore(string tag, string[] looks, Func<string> defaultLook, Func<string, string, bool, string, string> resolve)
        {
            this.tag = tag;
            this.looks = looks;
            this.defaultLook = defaultLook;
            this.resolve = resolve;
        }

        public string[] Looks => looks;
        public string DefaultLook => defaultLook();
        public bool IsLook(string look) => look != null && Array.IndexOf(looks, look) >= 0;

        /// <summary>Register ThingDefs by name; styleDefName(defName, look) names each look's ThingStyleDef.</summary>
        public void Register(IEnumerable<string> defNames, Func<string, string, string> styleDefName)
        {
            foreach (string dn in defNames)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (d == null) { Missing.Add(dn); continue; }
                var arr = new ThingStyleDef[looks.Length];
                for (int i = 0; i < arr.Length; i++)
                {
                    string sn = styleDefName(dn, looks[i]);
                    arr[i] = DefDatabase<ThingStyleDef>.GetNamedSilentFail(sn);
                    if (arr[i] == null) { Missing.Add(sn); continue; }
                    lookOf[arr[i]] = looks[i];
                }
                byDef[d] = arr;
            }
            foreach (string m in Missing) Log.Error(tag + " style def missing: " + m);
            var flags = new bool[DefDatabase<ThingDef>.DefCount + 16];
            foreach (ThingDef d in byDef.Keys) if (d.index < flags.Length) flags[d.index] = true;
            styled = flags;
        }

        public bool IsIndexed(ThingDef d)
        {
            bool[] a = styled;
            return a != null && d != null && d.index < a.Length && a[d.index];
        }

        public bool IsStyled(ThingDef d) => d != null && byDef.ContainsKey(d);

        public ThingStyleDef StyleFor(ThingDef d, string look)
        {
            if (d == null || !byDef.TryGetValue(d, out ThingStyleDef[] arr)) return null;
            int i = Array.IndexOf(looks, look);
            return i >= 0 ? arr[i] : null;
        }

        public string LookOfStyle(ThingStyleDef s) => s != null && lookOf.TryGetValue(s, out string l) ? l : null;

        /// <summary>The style stored on the thing itself (null for a legacy, unstyled building).</summary>
        public static ThingStyleDef RawStyle(Thing t) => (t as ThingWithComps)?.compStyleable?.styleDef;

        /// <summary>The look the thing draws in: its stored style's look, else the default look.</summary>
        public string LookOfThing(Thing t) => LookOfStyle(RawStyle(t)) ?? DefaultLook;

        public string LastPicked(ThingDef d) => d != null && lastPicked.TryGetValue(d, out string l) ? l : null;

        /// <summary>The style our getter hands the designator now.</summary>
        public ThingStyleDef Resolve(Designator_Build des)
        {
            ThingDef d = des?.PlacingDef as ThingDef;
            if (!IsStyled(d)) return null;
            string look = resolve(LastPicked(d), DefaultLook, des.styleOverridden, LookOfStyle(des.styleDef));
            return StyleFor(d, look);
        }

        /// <summary>A menu pick (also a probe's "style:" verb): remember it for this button and leave any "Copy" state.</summary>
        public void Pick(Designator_Build des, string look)
        {
            ThingDef d = des?.PlacingDef as ThingDef;
            if (!IsStyled(d) || !IsLook(look)) return;
            lastPicked[d] = look;
            des.styleOverridden = false;
            des.styleDef = StyleFor(d, look);
            picks++;
        }

        public void ClearPicks() => lastPicked.Clear();

        public List<FloatMenuOption> MenuFor(Designator_Build des)
        {
            var list = new List<FloatMenuOption>();
            ThingDef d = des.PlacingDef as ThingDef;
            string cur = LookOfStyle(Resolve(des));
            string def = DefaultLook;
            foreach (string look in looks)
            {
                ThingStyleDef s = StyleFor(d, look);
                if (s == null) continue;
                string l = look;
                string label = look + (look == cur ? " (current)" : "") + (look == def ? " - default" : "");
                list.Add(new FloatMenuOption(label, () => Pick(des, l), s.UIIcon ?? (Texture2D)Widgets.GetIconFor(d, null, s), Color.white));
            }
            return list;
        }

        // ------------------------------------------------------------------ patch bodies (each mod's thin patch calls these)

        /// <summary>Designator_Build.ProcessInput postfix: the build button opens the look menu, after vanilla selected it.</summary>
        public void ProcessInputPostfix(Designator_Build des, int errorKey)
        {
            try
            {
                if (!IsStyled(des.PlacingDef as ThingDef)) return;
                if (Find.DesignatorManager.SelectedDesignator != des) return;     // vanilla refused (CheckCanInteract)
                List<FloatMenuOption> opts = MenuFor(des);
                if (opts.Count > 0) Find.WindowStack.Add(new FloatMenu(opts));
            }
            catch (Exception ex) { Log.ErrorOnce(tag + " style menu: " + ex, errorKey); }
        }

        /// <summary>Designator_Build.ThingStyleDefNonPreceptSource getter postfix: the picked (or copied) look in every mode.</summary>
        public void StyleGetterPostfix(Designator_Build des, ref ThingStyleDef result)
        {
            if (des.sourcePrecept != null || !IsIndexed(des.PlacingDef as ThingDef)) return;
            result = Resolve(des) ?? result;
        }

        /// <summary>BuildCopyCommandUtility.BuildCopyCommand prefix: a "Copy" of one of our things always carries its look.</summary>
        public void CopyPrefix(BuildableDef buildable, ThingStyleDef style, ref bool styleOverridden)
        {
            if (style != null && IsIndexed(buildable as ThingDef)) styleOverridden = true;
        }

        /// <summary>Thing.StyleDef getter postfix (hot): a legacy unstyled thing reads as the default look's style.</summary>
        public void StyleDefPostfix(Thing t, ref ThingStyleDef result)
        {
            if (result != null || !IsIndexed(t.def)) return;
            result = StyleFor(t.def, DefaultLook);
        }

        internal sealed class FrameState { public ThingStyleDef Style; public IntVec3 Pos; public Map Map; public ThingDef Def; }

        /// <summary>Frame.CompleteConstruction prefix: remember the frame's style (vanilla copies it only for an ideo worker).</summary>
        public FrameState FramePrefix(Frame f)
        {
            if (!(f.def.entityDefToBuild is ThingDef d) || !IsIndexed(d)) return null;
            ThingStyleDef s = RawStyle(f);
            return s != null ? new FrameState { Style = s, Pos = f.Position, Map = f.Map, Def = d } : null;
        }

        /// <summary>Frame.CompleteConstruction postfix: re-apply the remembered style to the built thing.</summary>
        public void FramePostfix(FrameState st)
        {
            if (st?.Map == null) return;
            foreach (Thing t in st.Pos.GetThingList(st.Map))
            {
                if (t.def != st.Def || RawStyle(t) != null) continue;
                t.StyleDef = st.Style;
                t.DirtyMapMesh(t.Map);
                restored++;
            }
        }
    }
}
