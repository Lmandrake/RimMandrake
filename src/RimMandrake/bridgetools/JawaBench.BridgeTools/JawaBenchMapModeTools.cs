// JawaBenchMapModeTools.cs - switch the PLANET view between Map Mode Framework's world
// map modes, so a view mode that exists only as an immediate-mode toolbar button can be
// selected, regenerated and photographed from outside the game.
//
// WHY THIS EXISTS
// ===============
// "Faction Territories and Vassalage" (jaeger972.factionterritories) draws a Voronoi-style
// border around every faction's settlements. It authors nothing and stores nothing: the
// borders are a WORLD VIEW MODE, computed at render time, in the same family as vanilla's
// Temperature/Elevation planet overlays. There is no def to write and no bridge call that
// reaches it, because its selector is a Widgets.ButtonImage drawn every frame inside
// MapModeFramework.MapModeUI - immediate mode, exactly like RimWorld's own world button,
// and therefore not a rimworld/click_ui_target target. Same reason jawa/world_view had to
// exist at all.
//
// THE MECHANISM, READ FROM THE FRAMEWORK'S OWN SHIPPED SOURCE
// ==========================================================
// Map Mode Framework (nozome.mapmodeframework) ships Source/ in its workshop folder, so
// none of this is inferred:
//
//   MapModeFramework.MapModeComponent : Verse.GameComponent
//       public static MapModeComponent Instance     - set in the ctor, so it exists from
//                                                     the moment a Game does
//       public List<MapMode> mapModes               - one runtime MapMode per MapModeDef
//       public MapMode currentMapMode               - the RUNTIME object, not the def
//       public void RequestMapModeSwitch(MapMode)   - what the toolbar button reaches
//       public void SwitchMapMode(MapMode)          - currentMapMode = m;
//                                                     UpdateMapMode(m.def); RegenerateNow();
//       public void RegenerateNow()                 - DoPreRegenerate(); regenerateNow = true
//
//   MapModeFramework.MapMode.OnButtonClick()        - the button's ENTIRE body:
//         if (Instance.currentMapMode == this) return;
//         Instance.RequestMapModeSwitch(this);
//
// So RequestMapModeSwitch IS the button, and this tool calls it rather than an
// equivalent-looking shortcut - the house rule about reproducing the engine's own call
// with the engine's own arguments.
//
// TWO THINGS THAT MAKE THIS LOOK BROKEN WHEN IT IS NOT
// ===================================================
// 1. THE SWITCH IS NOT THE DRAW. SwitchMapMode only sets a flag: regenerateNow = true.
//    WorldLayer_MapMode.ShouldRegenerate reads it, and the border mesh is then rebuilt
//    ASYNCHRONOUSLY by WorldRegenHandler (BuildSubMeshes on a Task, tile by tile).
//    currentMapMode therefore reports the new mode INSTANTLY while the screen still shows
//    the old one. A screenshot taken on the switch call's return photographs the previous
//    mode. That is why this tool returns regenBusy/tilesPrepared/tilesToPrepare: poll them
//    to zero-busy before photographing anything.
// 2. IT NEEDS THE PLANET ON SCREEN. MapModeComponent.GameComponentUpdate returns early
//    unless WorldRendererUtility.WorldRendered, so the per-frame update and the framework's
//    own UI never run on a colony map, and the regeneration only advances through the
//    normal world-render pipeline. Call jawa/world_view first.
//
// REFLECTION, DELIBERATELY
// ========================
// Map Mode Framework is a Workshop mod, not a build-time dependency of this companion, and
// this assembly must load with or without it. Everything below resolves by name through
// GenTypes.GetTypeInAnyAssembly and reports a missing type as DATA - never a throw - the
// same discipline JawaBenchSwcpCharacterTools.cs uses for SWCP.
//
// ⛔ NO jawa/ PREFIXES IN PROSE ANYWHERE IN THIS FILE other than an EXACT, REAL tool name.
// build.py scans the assembly for jawa/... literals and a partial mention becomes a
// phantom tool name and refuses the next deploy.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld.Planet;
using Verse;
using RimBridgeServer.Sdk;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags MmfPublicInstance = BindingFlags.Public | BindingFlags.Instance;
        private const BindingFlags MmfPublicStatic = BindingFlags.Public | BindingFlags.Static;

        private static Type MmfType(string fullName) => GenTypes.GetTypeInAnyAssembly(fullName);

        /// <summary>defName off any object that is a Verse.Def, or null.</summary>
        private static string MmfDefName(object maybeDef) => (maybeDef as Def)?.defName;

        /// <summary>The `def` field/property of a MapMode instance, as a Def.</summary>
        private static Def MmfModeDef(object mapMode)
        {
            if (mapMode == null) return null;
            Type t = mapMode.GetType();
            FieldInfo f = t.GetField("def", MmfPublicInstance);
            if (f != null) return f.GetValue(mapMode) as Def;
            PropertyInfo p = t.GetProperty("def", MmfPublicInstance);
            return p?.GetValue(mapMode, null) as Def;
        }

        [Tool(
            "jawa/world_map_mode",
            Description =
                "Read, and optionally SWITCH, the planet's Map Mode Framework view mode - the " +
                "overlay family that draws faction territory borders, world features and the " +
                "like over the globe. Omit mapModeDefName to read state only; give one to " +
                "select that mode by calling the framework's own RequestMapModeSwitch, which is " +
                "the entire body of the toolbar button's click handler. " +
                "🔴 THE SWITCH IS NOT THE DRAW: the call only raises a regenerate flag, and the " +
                "border mesh is rebuilt asynchronously afterwards, so currentMapMode reports the " +
                "NEW mode while the screen still shows the OLD one. Poll this tool until " +
                "regenBusy is false AND regenerateNow is false before taking any screenshot, or " +
                "you will photograph the previous mode and believe the switch failed. " +
                "🔴 SHOW THE PLANET FIRST with jawa/world_view: the framework's per-frame update " +
                "returns early unless the world is being rendered, so on a colony map the " +
                "regeneration never advances and regenBusy never clears. " +
                "Requires a loaded game and the nozome.mapmodeframework mod active; reports a " +
                "missing framework as data rather than throwing.",
            ResultDescription =
                "success, frameworkPresent, modeBefore/modeAfter (defNames), requested, " +
                "switched, availableModes[] (defName + label + hasWorldLayer), worldRendered, " +
                "regenerateNow, regenBusy, regeneratingMode, tilesPrepared, tilesToPrepare, " +
                "ticksGame. On an unknown mapModeDefName: success false and availableModes[] " +
                "so the caller can see what it could have asked for.")]
        public static async Task<object> WorldMapMode(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "defName of the MapModeDef to switch to, e.g. 'FactionTerritories' for the " +
                "faction-territory borders, or 'Default' to go back to the plain planet. " +
                "Omit to read current state without changing anything.")]
            string mapModeDefName = null,
            [ToolParameter(Description =
                "Bypass the framework's own async request path and call SwitchMapMode directly. " +
                "Only for when RequestMapModeSwitch is wedged behind an interrupted regeneration " +
                "task; the default false reproduces exactly what clicking the button does.")]
            bool forceDirect = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.World == null) return Fail("No world is loaded - a game must be running.");

                Type compType = MmfType("MapModeFramework.MapModeComponent");
                if (compType == null)
                {
                    return Fail(
                        "MapModeFramework.MapModeComponent did not resolve in any loaded assembly. " +
                        "The Map Mode Framework mod (nozome.mapmodeframework) is not active, or " +
                        "its assembly failed to load - check the log for a load error.",
                        new { frameworkPresent = false });
                }

                FieldInfo instanceField = compType.GetField("Instance", MmfPublicStatic);
                object comp = instanceField?.GetValue(null);
                if (comp == null)
                {
                    return Fail(
                        "MapModeComponent.Instance is null. The static is assigned in the " +
                        "component's constructor, so this means no Game object has been " +
                        "constructed yet - load a save before calling.",
                        new { frameworkPresent = true });
                }

                FieldInfo currentField = compType.GetField("currentMapMode", MmfPublicInstance);
                FieldInfo modesField = compType.GetField("mapModes", MmfPublicInstance);
                FieldInfo regenNowField = compType.GetField("regenerateNow", MmfPublicInstance);
                if (currentField == null || modesField == null)
                {
                    return Fail(
                        "MapModeComponent resolved but its currentMapMode/mapModes fields did " +
                        "not - the framework's API changed and this tool needs updating.",
                        new { frameworkPresent = true });
                }

                object modesRaw = modesField.GetValue(comp);
                var modes = new List<object>();
                if (modesRaw is IEnumerable modesEnum)
                {
                    foreach (object m in modesEnum) if (m != null) modes.Add(m);
                }

                var available = modes.Select(m =>
                {
                    Def d = MmfModeDef(m);
                    object worldLayer = null;
                    try
                    {
                        PropertyInfo wl = m.GetType().GetProperty("WorldLayerClass", MmfPublicInstance);
                        worldLayer = wl?.GetValue(m, null);
                    }
                    catch (Exception) { /* reported as hasWorldLayer null below */ }
                    return new
                    {
                        defName = d?.defName,
                        label = d?.label,
                        modeClass = m.GetType().FullName,
                        hasWorldLayer = worldLayer == null ? (bool?)null : true
                    };
                }).ToList();

                object before = currentField.GetValue(comp);
                string modeBefore = MmfDefName(MmfModeDef(before));

                bool switched = false;
                string refusal = null;

                if (!string.IsNullOrEmpty(mapModeDefName))
                {
                    object target = modes.FirstOrDefault(m =>
                        string.Equals(MmfDefName(MmfModeDef(m)), mapModeDefName,
                                      StringComparison.OrdinalIgnoreCase));

                    if (target == null)
                    {
                        return Fail(
                            "No loaded map mode has defName '" + mapModeDefName + "'. See " +
                            "availableModes for what is actually registered - a mode whose def " +
                            "failed to load is absent here rather than erroring.",
                            new { frameworkPresent = true, modeBefore, availableModes = available });
                    }

                    if (ReferenceEquals(target, before))
                    {
                        refusal = "Already on this map mode; the framework's own button returns " +
                                  "early in exactly this case, so nothing was called.";
                    }
                    else
                    {
                        string methodName = forceDirect ? "SwitchMapMode" : "RequestMapModeSwitch";
                        MethodInfo mi = compType.GetMethod(methodName, MmfPublicInstance);
                        if (mi == null)
                        {
                            return Fail(
                                "MapModeComponent has no public instance method '" + methodName +
                                "' - the framework's API changed and this tool needs updating.",
                                new { frameworkPresent = true, modeBefore, availableModes = available });
                        }
                        try
                        {
                            mi.Invoke(comp, new[] { target });
                            switched = true;
                        }
                        catch (TargetInvocationException tie)
                        {
                            return Fail(
                                methodName + " threw: " +
                                (tie.InnerException?.Message ?? tie.Message),
                                new { frameworkPresent = true, modeBefore, availableModes = available });
                        }
                        catch (Exception e)
                        {
                            return Fail(
                                methodName + " could not be invoked: " + e.Message,
                                new { frameworkPresent = true, modeBefore, availableModes = available });
                        }
                    }
                }

                // Read the RAW field back after the call, never the value we hoped for.
                object after = currentField.GetValue(comp);
                string modeAfter = MmfDefName(MmfModeDef(after));

                bool? regenerateNow = null;
                if (regenNowField != null)
                {
                    try { regenerateNow = (bool?)regenNowField.GetValue(comp); }
                    catch (Exception) { /* stays null, reported as unknown */ }
                }

                bool? regenBusy = null;
                string regeneratingMode = null;
                int tilesPrepared = -1, tilesToPrepare = -1;
                Type handler = MmfType("MapModeFramework.WorldRegenHandler");
                if (handler != null)
                {
                    try
                    {
                        PropertyInfo busy = handler.GetProperty("IsBusy", MmfPublicStatic);
                        if (busy != null) regenBusy = (bool?)busy.GetValue(null, null);
                        FieldInfo rm = handler.GetField("regeneratingMapMode", MmfPublicStatic);
                        if (rm != null) regeneratingMode = MmfDefName(MmfModeDef(rm.GetValue(null)));
                        FieldInfo tp = handler.GetField("tilesPrepared", MmfPublicStatic);
                        if (tp != null) tilesPrepared = (int)tp.GetValue(null);
                        FieldInfo tt = handler.GetField("tilesToPrepare", MmfPublicStatic);
                        if (tt != null) tilesToPrepare = (int)tt.GetValue(null);
                    }
                    catch (Exception) { /* every field above stays at its unknown sentinel */ }
                }

                return (object)new
                {
                    success = true,
                    frameworkPresent = true,
                    requested = mapModeDefName,
                    switched,
                    refusal,
                    modeBefore,
                    modeAfter,
                    modeChanged = modeBefore != modeAfter,
                    availableModes = available,
                    worldRendered = WorldRendererUtility.WorldRendered,
                    regenerateNow,
                    regenBusy,
                    regeneratingMode,
                    tilesPrepared,
                    tilesToPrepare,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
