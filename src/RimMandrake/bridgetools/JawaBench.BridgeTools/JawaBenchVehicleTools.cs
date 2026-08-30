// JawaBenchVehicleTools.cs - reading a vehicle's damage from outside the game.
//
// WHY THIS FILE EXISTS
// ====================
// `BRIDGE_READ_VEHICLE_COMPONENTS_1`, out of the finding
// `VEHICLE_HEALTH_TAB_UNREACHABLE_1`.
//
// A Vehicle Framework vehicle IS a `Verse.Pawn`, so every existing pawn tool
// accepts one and every existing pawn tool tells you nothing useful about its
// damage: a vehicle's condition is NOT in `pawn.health.hediffSet`. It lives in a
// component system of the mod's own, which is what the in-game health tab draws.
// Before this file the bridge had no vehicle tools at all - measured 2026-08-22,
// zero of 120 `jawa/…` names touched one - so "is this vehicle damaged, and
// where" could only be answered by a human opening a tab.
//
// EVERYTHING HERE IS REFLECTION, ON PURPOSE
// =========================================
// `JawaBench.BridgeTools.csproj` references only RimBridgeServer.Sdk,
// Assembly-CSharp and UnityEngine.CoreModule. That is deliberate: the companion
// has to load on an install where Vehicle Framework is absent, and a hard
// reference would stop it dead. So the chain is walked by name.
//
// 🔴 THE NAMES BELOW WERE READ OUT OF `Vehicles.dll`'s METADATA TABLES, NOT
// GUESSED. The mod ships DLLs and no source. A reflection lookup that misses
// returns null rather than throwing, so a guessed name would produce an empty
// component list that reads exactly like an undamaged vehicle - the silent
// failure this project has too much of already. Hence: every handle is checked,
// and a miss REFUSES.
//
//     Vehicles.VehiclePawn        extends Verse.Pawn
//       .statHandler              FIELD   -> Vehicles.VehicleStatHandler
//         .components             FIELD   -> List<Vehicles.VehicleComponent>
//           .props                FIELD   -> Vehicles.VehicleComponentProperties
//             .key                FIELD   string, the stable id
//             .label              FIELD   string, what the health tab prints
//           .Health               PROPERTY float
//           .MaxHealth            PROPERTY float
//           .HealthPercent        PROPERTY float
//           .Efficiency           PROPERTY float
//           .Depth                PROPERTY Vehicles.VehicleComponent+VehiclePartDepth
//
// ⚠️ `statHandler` and `components` are FIELDS, not properties. GetProperty
// returns null on both and the whole tool would go quiet.
// ⚠️ `props.health` is an `int` base value; `MaxHealth` is a float that folds in
// SetHealthModifier and AddHealthModifiers. Read the PROPERTY or the numbers are
// wrong on any vehicle carrying a modifier.
// ⚠️ `props.label` can be null - it comes from def XML with no back-fill - so the
// display name falls back to `props.key`.
//
// 🔑 THERE IS NO DAMAGE-TIER ENUM. Every TypeDef in Vehicles.dll extending
// System.Enum was enumerated and none describes component state; the health tab's
// colour bands are hard-coded float thresholds against `Efficiency`. So this tool
// reports the float and does not invent a tier.
//
// THREAD AFFINITY: same rule as every other file here. Everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const string VehiclePawnTypeName = "Vehicles.VehiclePawn";
        private const BindingFlags PubInst = BindingFlags.Public | BindingFlags.Instance;

        /// <summary>
        /// True when this pawn's type IS or DERIVES FROM Vehicles.VehiclePawn.
        ///
        /// 🔑 The base chain is walked rather than comparing the leaf type name.
        /// `VehiclePawn` is public and NOT sealed, so another mod may subclass it,
        /// and an equality test would silently report such a vehicle as "not a
        /// vehicle" - a false negative that looks like an empty result.
        /// </summary>
        private static bool IsVehiclePawn(Pawn p)
        {
            for (Type t = p == null ? null : p.GetType(); t != null; t = t.BaseType)
            {
                if (t.FullName == VehiclePawnTypeName) return true;
            }
            return false;
        }

        /// <summary>Read a public instance property, or null when it is not there.</summary>
        private static object PropOrNull(object obj, string name)
        {
            if (obj == null) return null;
            PropertyInfo pi = obj.GetType().GetProperty(name, PubInst);
            if (pi == null || !pi.CanRead) return null;
            try { return pi.GetValue(obj, null); }
            catch (Exception) { return null; }
        }

        /// <summary>
        /// Read a public OR private instance field, or null when it is not there.
        ///
        /// 🔴 BRIDGE_STORY_ALERT_TALE_TOOLS_1: this used to be PubInst-only, so it could
        /// never find a private field - which is exactly what `jawa/alerts_list` needed
        /// (`AlertsReadout.activeAlerts` is private) and silently could not get. NonPublic
        /// is additive to the existing Public lookup for every other caller: it never
        /// removes a match that worked before, it only adds fields that previously
        /// returned null. Checked every other FieldOrNull call site in the codebase
        /// (JawaBenchPipeTools.cs, JawaBenchSwcpCharacterTools.cs, JawaBenchVehicleAerialTools.cs,
        /// JawaBenchVehicleTools.cs itself) - all read known-public fields on vanilla/VF
        /// types, none relies on the narrower public-only behavior.
        /// </summary>
        private static object FieldOrNull(object obj, string name)
        {
            if (obj == null) return null;
            FieldInfo fi = obj.GetType().GetField(name, PubInst | BindingFlags.NonPublic);
            if (fi == null) return null;
            try { return fi.GetValue(obj); }
            catch (Exception) { return null; }
        }

        [Tool(
            "jawa/vehicle_components",
            Description =
                "Read a Vehicle Framework vehicle's COMPONENT health - the data behind its " +
                "in-game health tab. A vehicle is a Pawn, but its damage is NOT in " +
                "health.hediffSet, so jawa/pawn_health reports a vehicle as undamaged no " +
                "matter how wrecked it is. This walks statHandler.components by reflection, " +
                "so the companion still loads when Vehicle Framework is absent. READ ONLY - " +
                "it changes nothing. Give a pawn id, thingId or name; omit 'pawn' to list " +
                "every spawned vehicle on the map with a one-line summary, which is the " +
                "quickest way to find the id you want. If the reflection chain cannot be " +
                "resolved this REFUSES rather than returning an empty component list, " +
                "because an empty list is indistinguishable from an undamaged vehicle.",
            ResultDescription =
                "success, isVehicle, pawn identity, componentCount, and per component: key, " +
                "label, health, maxHealth, healthPercent, efficiency, depth. Also " +
                "damagedCount and worstEfficiency, which are the two numbers that answer " +
                "'is this thing hurt' without reading the rows. In list mode: vehicles[] " +
                "with thingId, label, componentCount, damagedCount, worstEfficiency.")]
        public static async Task<object> VehicleComponents(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name. Omit to list every spawned vehicle instead.")]
            string pawn = null,
            [ToolParameter(Description = "Only return components whose efficiency is below 1.0. Counts always cover all of them. Default false.")]
            bool damagedOnly = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.CurrentMap == null) return Fail("No current map - is a game loaded?");

                // ---- list mode ------------------------------------------------
                if (string.IsNullOrEmpty(pawn))
                {
                    var found = new List<object>();
                    foreach (Pawn p in Find.CurrentMap.mapPawns.AllPawnsSpawned)
                    {
                        if (!IsVehiclePawn(p)) continue;
                        string err2;
                        List<object> comps = ReadComponents(p, out err2);
                        found.Add(new
                        {
                            thingId = p.ThingID,
                            label = p.LabelShortCap,
                            def = p.def != null ? p.def.defName : null,
                            componentCount = comps == null ? 0 : comps.Count,
                            damagedCount = comps == null ? 0 : CountDamaged(comps),
                            worstEfficiency = comps == null ? (float?)null : WorstEfficiency(comps),
                            note = err2,
                        });
                    }
                    return new
                    {
                        success = true,
                        mode = "list",
                        vehicleCount = found.Count,
                        vehicles = found,
                        note = found.Count == 0
                            ? "No spawned vehicle on this map. A Vehicle Framework vehicle spawns as a PAWN, "
                              + "so jawa/list_things will not show one either."
                            : null,
                    };
                }

                // ---- one vehicle ----------------------------------------------
                string err;
                Pawn v = FindPawn(pawn, out err);
                if (v == null) return Fail(err);

                if (!IsVehiclePawn(v))
                {
                    // Not a failure of this tool - a correct, useful answer.
                    return new
                    {
                        success = true,
                        isVehicle = false,
                        thingId = v.ThingID,
                        label = v.LabelShortCap,
                        def = v.def != null ? v.def.defName : null,
                        type = v.GetType().FullName,
                        note = "This pawn does not derive from " + VehiclePawnTypeName
                               + ". Its damage IS in health.hediffSet - use jawa/pawn_health.",
                    };
                }

                string chainErr;
                List<object> components = ReadComponents(v, out chainErr);
                if (components == null)
                {
                    return Fail(
                        "This IS a vehicle, but its component chain could not be read by reflection: "
                        + chainErr
                        + " REFUSING rather than returning an empty component list, which would "
                        + "look exactly like an undamaged vehicle.",
                        new { thingId = v.ThingID, type = v.GetType().FullName });
                }

                var rows = new List<object>();
                foreach (object row in components)
                {
                    if (!damagedOnly || EfficiencyOf(row) < 1f) rows.Add(row);
                }

                return new
                {
                    success = true,
                    isVehicle = true,
                    thingId = v.ThingID,
                    thingIdNumber = v.thingIDNumber,
                    label = v.LabelShortCap,
                    def = v.def != null ? v.def.defName : null,
                    componentCount = components.Count,
                    damagedCount = CountDamaged(components),
                    worstEfficiency = WorstEfficiency(components),
                    returned = rows.Count,
                    components = rows,
                };
            });
        }

        /// <summary>
        /// pawn -> statHandler -> components -> one anonymous row each.
        /// Returns null and sets <paramref name="err"/> when a link cannot be
        /// resolved; an EMPTY list is a real answer (a vehicle with no components)
        /// and is not an error.
        /// </summary>
        private static List<object> ReadComponents(Pawn v, out string err)
        {
            err = null;
            object handler = FieldOrNull(v, "statHandler");
            if (handler == null)
            {
                err = "field 'statHandler' is absent on " + v.GetType().FullName
                      + " (it is a FIELD, not a property).";
                return null;
            }
            object comps = FieldOrNull(handler, "components");
            if (comps == null)
            {
                err = "field 'components' is absent on " + handler.GetType().FullName + ".";
                return null;
            }
            IEnumerable list = comps as IEnumerable;
            if (list == null)
            {
                err = "'components' is not enumerable; it is " + comps.GetType().FullName + ".";
                return null;
            }

            var rows = new List<object>();
            foreach (object c in list)
            {
                if (c == null) continue;
                object props = FieldOrNull(c, "props");
                string key = FieldOrNull(props, "key") as string;
                string label = FieldOrNull(props, "label") as string;
                object depth = PropOrNull(c, "Depth");
                rows.Add(new
                {
                    key = key,
                    // props.label comes from def XML with no back-fill, so it can be
                    // null on a component that only ever had a key.
                    label = string.IsNullOrEmpty(label) ? key : label,
                    health = AsFloat(PropOrNull(c, "Health")),
                    maxHealth = AsFloat(PropOrNull(c, "MaxHealth")),
                    healthPercent = AsFloat(PropOrNull(c, "HealthPercent")),
                    efficiency = AsFloat(PropOrNull(c, "Efficiency")),
                    depth = depth == null ? null : depth.ToString(),
                });
            }
            return rows;
        }

        private static float? AsFloat(object o)
        {
            if (o == null) return null;
            try { return Convert.ToSingle(o); }
            catch (Exception) { return null; }
        }

        /// <summary>Efficiency of a row built by ReadComponents; 1.0 when unknown.</summary>
        private static float EfficiencyOf(object row)
        {
            object e = row.GetType().GetProperty("efficiency", PubInst) == null
                ? null
                : row.GetType().GetProperty("efficiency", PubInst).GetValue(row, null);
            float? f = AsFloat(e);
            return f.HasValue ? f.Value : 1f;
        }

        private static int CountDamaged(List<object> rows)
        {
            int n = 0;
            foreach (object r in rows) if (EfficiencyOf(r) < 1f) n++;
            return n;
        }

        private static float WorstEfficiency(List<object> rows)
        {
            float worst = 1f;
            foreach (object r in rows)
            {
                float e = EfficiencyOf(r);
                if (e < worst) worst = e;
            }
            return worst;
        }
    }
}
