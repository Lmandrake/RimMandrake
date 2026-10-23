using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P3):
    /// the overhead-span kinds read off the map. GSS's aerial machinery (links, auto-link, cut/re-string, fallen halves, span
    /// mesh, shadow) is shared by every kind; what differs per kind is here: range, sag, strand count, drip/sway, power.
    ///
    /// The pipe kind's numbers are FlowWorks' Mod Settings (pipe poles are FlowWorks content: the def, the placement rule and,
    /// in phase 5, the liquid-net edge live there). FlowWorks holds no reference to this assembly; it finds
    /// <see cref="RegisterPipeProfile"/> by name and hands over live getters, the same soft seam as
    /// RM_FallenWireShock.RegisterLiveWireSource. Unregistered, the pipe kind uses AerialKinds' defaults.
    ///
    /// Phase-5 seam (the liquid net's long-range edge, FlowWorks): <see cref="UpSpans"/> lists the strung spans of a kind on a
    /// map, once each; <see cref="RegisterSpansChanged"/> is called back on every span topology change (link, unlink, cut,
    /// re-string, an anchor despawned or landed), so the net can rebuild.
    /// </summary>
    public static class AerialLineProfiles
    {
        private static Func<float> pipeMaxSpan, pipeSag;
        private static readonly List<Action<Map>> spansChanged = new List<Action<Map>>();

        /// <summary>State read: how many times a pipe profile was registered (1 after FlowWorks' startup).</summary>
        public static int PipeProfileRegistrations;
        /// <summary>State read: span-change callbacks fired (all listeners count once per fire).</summary>
        public static int SpansChangedFired;

        /// <summary>Public entry point for FlowWorks: the pipe kind's longest span (cells) and sag factor, read live.</summary>
        public static void RegisterPipeProfile(Func<float> maxSpan, Func<float> sag)
        {
            pipeMaxSpan = maxSpan;
            pipeSag = sag;
            PipeProfileRegistrations++;
        }

        /// <summary>Public entry point for FlowWorks (phase 5): called with the map whenever its spans change. Registering the
        /// same delegate twice is a no-op.</summary>
        public static void RegisterSpansChanged(Action<Map> callback)
        {
            if (callback != null && !spansChanged.Contains(callback)) spansChanged.Add(callback);
        }

        public static bool PipeRegistered => pipeMaxSpan != null;

        private static Func<bool> pipeOn;
        /// <summary>State read: how many times a pipe-pole switch was registered (1 after FlowWorks' startup).</summary>
        public static int PipeSwitchRegistrations;

        /// <summary>PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES (owner by card 2026-10-21: "Their own switch."): FlowWorks hands over
        /// its pipe-pole Mod Setting, read live. Every GSS aerial gate then reads the switch of the anchor's own kind
        /// (<see cref="KindOn"/>), so the power-lines master switch no longer hides or stops pipe poles. Unregistered (an older
        /// FlowWorks), pipe poles count as on.</summary>
        public static void RegisterPipeSwitch(Func<bool> on)
        {
            pipeOn = on;
            PipeSwitchRegistrations++;
        }

        public static bool PipeOn
        {
            get
            {
                if (pipeOn == null) return true;
                try { return pipeOn(); }
                catch (Exception e)
                {
                    Log.ErrorOnce("[GimmeSomeSlack] the registered pipe-pole switch threw; treating pipe poles as on: " + e.Message, 0x7A1E5D);
                    return true;
                }
            }
        }

        /// <summary>Is this kind of overhead line switched on (power: GSS's master; pipe: FlowWorks' pipe-pole switch)?</summary>
        public static bool KindOn(AerialLineKind k) => AerialKinds.KindOn(k, AerialSettings.enabled, PipeOn);

        /// <summary>A power-master-dependent behaviour (auto-link, wire-down alert, owner-change cut) for this kind.</summary>
        public static bool KindBehaviour(AerialLineKind k, bool powerSetting) =>
            AerialKinds.KindBehaviour(k, AerialSettings.enabled, PipeOn, powerSetting);

        /// <summary>Any kind of overhead line on: the map-wide draw and the ground layer run, filtering per anchor. Pipe poles
        /// exist only with FlowWorks, which registers its profile at startup, so without it only the power switch counts.</summary>
        public static bool AnyKindOn => AerialSettings.enabled || (PipeRegistered && PipeOn);

        private static float Read(Func<float> f, float fallback)
        {
            if (f == null) return fallback;
            try { return f(); }
            catch (Exception e)
            {
                Log.ErrorOnce("[GimmeSomeSlack] the registered pipe-pole profile threw; using the defaults: " + e.Message, 0x7A1E5B);
                return fallback;
            }
        }

        public static float PipeMaxSpanRaw => Read(pipeMaxSpan, AerialKinds.PipeMaxSpanDefault);
        public static float PipeSagRaw => Read(pipeSag, AerialKinds.PipeSagDefault);

        public static AerialLineKind KindOf(ThingDef d) => d?.GetModExtension<AerialAnchorExtension>()?.lineKind ?? AerialLineKind.Power;

        public static float RangeFor(AerialLineKind k) =>
            AerialKinds.RangeFor(k, AerialSettings.maxSpan, k == AerialLineKind.Pipe ? PipeMaxSpanRaw : 0f);

        public static float SagFor(AerialLineKind k) =>
            AerialKinds.SagFor(k, AerialSettings.sag, k == AerialLineKind.Pipe ? PipeSagRaw : 0f);

        /// <summary>What one strung span of this kind is called in gizmos and messages.</summary>
        public static string Noun(AerialLineKind k) => k == AerialLineKind.Pipe ? "pipe span" : "wire";

        /// <summary>The look a styled thing of ANOTHER mod's picker draws in (a pipe pole's style is FlowWorks', named
        /// &lt;def&gt;_&lt;Look&gt;): the style def name's last part when it is one of the four looks, else null.</summary>
        public static string LookFromStyleName(ThingStyleDef s)
        {
            string n = s?.defName;
            if (n.NullOrEmpty()) return null;
            int i = n.LastIndexOf('_');
            string look = i >= 0 ? n.Substring(i + 1) : null;
            return AerialStyles.IsLook(look) ? look : null;
        }

        /// <summary>The look an anchor draws in: a power anchor's own GSS style (StylePicker); a pipe anchor's FlowWorks style,
        /// read from its name, else the default look.</summary>
        public static string LookOfThing(Thing t)
        {
            // POLE_CABLE_FIX_FORGOT_TO_SAG (live 2026-10-23): an unstyled pipe pole DRAWS its engine StyleDef (RM_PipePole_Scrapper)
            // while the span fell through to GSS's DefaultLook (Modern) and drew the red Modern PipeSpan; the span follows the drawn pole.
            if (t != null && KindOf(t.def) == AerialLineKind.Pipe)
                return LookFromStyleName(StylePicker.RawStyle(t)) ?? LookFromStyleName(t.StyleDef) ?? StylePicker.DefaultLook;
            return StylePicker.LookOfThing(t);
        }

        /// <summary>The look a pole of this def will be built in when the designator holds this style (placement ghost).</summary>
        public static string LookOfPick(ThingDef def, ThingStyleDef picked)
        {
            if (KindOf(def) == AerialLineKind.Pipe) return LookFromStyleName(picked) ?? StylePicker.DefaultLook;
            return StylePicker.LookOfStyle(picked) ?? StylePicker.DefaultLook;
        }

        /// <summary>Phase-5 seam: every strung (Up) span of this kind on the map, once each (owner end first), as the two anchor
        /// THINGS. A cut span, or one whose far end is gone or on another map, is not listed.</summary>
        public static List<KeyValuePair<Thing, Thing>> UpSpans(Map map, AerialLineKind kind)
        {
            var r = new List<KeyValuePair<Thing, Thing>>();
            RM_MapComponent_Aerial comp = map?.GetComponent<RM_MapComponent_Aerial>();
            if (comp == null) return r;
            foreach (CompAerialAnchor a in comp.Anchors)
            {
                if (a.Kind != kind) continue;
                foreach (SpanLink l in a.links)
                {
                    if (l.state != SpanState.Up || l.other == null || !l.other.Spawned || l.other.Map != map) continue;
                    if (!AerialMath.Owns(a.thingIDNumber, l.other.thingIDNumber)) continue;
                    r.Add(new KeyValuePair<Thing, Thing>(a.parent, l.other.parent));
                }
            }
            return r;
        }

        /// <summary>Reflection-friendly overload (FlowWorks passes the kind's name, "Pipe").</summary>
        public static List<KeyValuePair<Thing, Thing>> UpSpans(Map map, string kind) =>
            UpSpans(map, kind == "Pipe" ? AerialLineKind.Pipe : AerialLineKind.Power);

        /// <summary>Called by RM_MapComponent_Aerial.Notify_SpansChanged (every topology change funnels through it).</summary>
        internal static void FireSpansChanged(Map map)
        {
            if (map == null || spansChanged.Count == 0) return;
            SpansChangedFired++;
            for (int i = 0; i < spansChanged.Count; i++)
            {
                try { spansChanged[i](map); }
                catch (Exception e)
                {
                    Log.ErrorOnce("[GimmeSomeSlack] a span-change listener threw: " + e.Message, 0x7A1E5C + i);
                }
            }
        }
    }
}
