// JawaBenchStorytellerCompsTools.cs - read which incidents each storyteller comp can fire.
//
// ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR A1 (storyteller half): MandrakePatches removes every
// StorytellerDef comps entry with incident AnimaTreeSpawn; nothing on the bridge could read a
// comp's incident (jawa/get_defs is scalar-only and returns StorytellerDef.comps as nothing).
// Source read via rimsage: RimWorld/StorytellerDef.cs (comps: List<StorytellerCompProperties>),
// RimWorld/Storyteller.cs (storytellerComps, built from def.comps), StorytellerComp_OnOffCycle
// (Props.incident / Props.IncidentCategory). Fields are read by REFLECTION over each props
// object's public fields of type IncidentDef, IncidentCategoryDef or a list of IncidentDef, so a
// modded comp props class is covered without naming it. Read only; no GM gate.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static List<string> StorytellerPropsRefs(object props)
        {
            var refs = new List<string>();
            if (props == null) return refs;
            foreach (FieldInfo f in props.GetType().GetFields(BindingFlags.Public | BindingFlags.Instance))
            {
                object v;
                try { v = f.GetValue(props); } catch (Exception) { continue; }
                if (v == null) continue;
                if (v is IncidentDef idef) refs.Add(f.Name + "=IncidentDef:" + idef.defName);
                else if (v is IncidentCategoryDef cdef) refs.Add(f.Name + "=IncidentCategoryDef:" + cdef.defName);
                else if (v is IEnumerable list && !(v is string))
                {
                    foreach (object o in list)
                    {
                        if (o is IncidentDef ld) refs.Add(f.Name + "[]=IncidentDef:" + ld.defName);
                        else if (o is IncidentCategoryDef lc) refs.Add(f.Name + "[]=IncidentCategoryDef:" + lc.defName);
                    }
                }
            }
            return refs;
        }

        [Tool(
            "jawa/storyteller_comps",
            Description =
                "READ ONLY. List every storyteller comp and the incidents / incident categories its props name: " +
                "the RUNNING storyteller's comps (Find.Storyteller.storytellerComps, needs a game) and every " +
                "StorytellerDef's comps (DefDatabase, after patches). Props are read by reflection over public " +
                "fields of type IncidentDef, IncidentCategoryDef or a list of IncidentDef, so a modded props class " +
                "is covered. 'find' counts comps naming that IncidentDef. A comp whose props name no incident or " +
                "category (e.g. a pure threat-cycle comp) is listed with an empty refs list, never skipped.",
            ResultDescription =
                "success, running {storyteller, comps[{index, type, refs[]}]} or null with no game, " +
                "defs[{defName, comps[{index, propsType, refs[]}]}], find, findHitsRunning, findHitsDefs[], ticksGame.")]
        public static async Task<object> StorytellerComps(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Optional IncidentDef defName to count, e.g. AnimaTreeSpawn.")]
            string find = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string needle = string.IsNullOrWhiteSpace(find) ? null : "IncidentDef:" + find.Trim();
                object running = null;
                int hitsRunning = 0;
                Storyteller st = Current.Game == null ? null : Find.Storyteller;
                if (st != null)
                {
                    var comps = new List<object>();
                    List<StorytellerComp> live = st.storytellerComps ?? new List<StorytellerComp>();
                    for (int i = 0; i < live.Count; i++)
                    {
                        List<string> refs = StorytellerPropsRefs(live[i]?.props);
                        if (needle != null && refs.Any(r => r.EndsWith(needle, StringComparison.Ordinal))) hitsRunning++;
                        comps.Add(new { index = i, type = live[i]?.GetType().Name, refs });
                    }
                    running = new { storyteller = st.def?.defName, compCount = live.Count, comps };
                }
                var defs = new List<object>();
                var hitsDefs = new List<string>();
                foreach (StorytellerDef d in DefDatabase<StorytellerDef>.AllDefsListForReading)
                {
                    var comps = new List<object>();
                    List<StorytellerCompProperties> props = d.comps ?? new List<StorytellerCompProperties>();
                    for (int i = 0; i < props.Count; i++)
                    {
                        List<string> refs = StorytellerPropsRefs(props[i]);
                        if (needle != null && refs.Any(r => r.EndsWith(needle, StringComparison.Ordinal))) hitsDefs.Add(d.defName + "#" + i);
                        comps.Add(new { index = i, propsType = props[i]?.GetType().Name, refs });
                    }
                    defs.Add(new { defName = d.defName, compCount = props.Count, comps });
                }
                return (object)new
                {
                    success = true,
                    running,
                    defs,
                    find = needle == null ? null : find.Trim(),
                    findHitsRunning = hitsRunning,
                    findHitsDefs = hitsDefs,
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
