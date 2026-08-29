// JawaBenchPipeTools.cs - the pipe-network domain the roster flagged UNCERTAIN and
// this file resolves as far as source allows: BRIDGE_CAPABILITY_ROSTER.md §4,
// "generic reflective reader over all three frameworks". Owner ruling 2026-08-29,
// asked when the VEF-source-vs-no-source split was found: build all three, verified
// where source exists, a generic dump where it does not, and be honest about which
// is which in the RESULT ITSELF, not just a code comment.
//
// Vanilla RimWorld has power conduits only. Three third-party resource-network
// runtimes are active on the owner's real mod list (measured 2026-08-20):
//   VEF PipeSystem        oskarpotocki.vanillafactionsexpanded.core
//   Rimefeller (oil/fuel)  dubwise.rimefeller
//   Dubs Bad Hygiene Lite  dubwise.dubsbadhygiene.lite
//
// EVERY SIGNATURE FOR VEF PIPESYSTEM WAS READ OUT OF ITS OWN VENDORED SOURCE, NOT
// GUESSED: vendor/mod_sources/VanillaExpandedFramework-main/Source/PipeSystem/
//   PipeSystem/PipeNetManager.cs   : MapComponent, public List<PipeNet> pipeNets
//   PipeSystem/PipeNet.cs          public Map map; BoolGrid networkGrid; PipeNetDef def;
//                                   List<CompResource> connectors; List<CompResourceTrader>
//                                   producers/receivers; List<CompResourceStorage> storages;
//                                   properties: Consumption, Production, Stored,
//                                   AvailableCapacity (all float, private set - read only)
// 🔴 Confirmed by reading the actual class: there is NO "CachedPipeNetManager" type -
// the roster's own note about seeing that name in a `strings` scan was .NET #Strings
// heap suffix compression on a PROPERTY BACKING FIELD elsewhere, not a second class.
// The correct handle is the plain MapComponent lookup this file uses.
//
// 🔴 RIMEFELLER AND DUBS BAD HYGIENE SHIP DLL-ONLY IN THIS REPO'S VENDOR TREE - no
// Source/ folder, Assemblies/ and Defs/ only. Their exact field names are UNVERIFIED.
// Per the owner's ruling, this file still reports on them, via a GENERIC reflective
// dump of whatever public simple-typed fields/properties exist on any MapComponent
// whose type name contains "Rimefeller" or "Hygiene" - and every row in that dump
// carries `verified: false` in the result so a caller cannot mistake it for the
// curated VEF read. Building the companion has never referenced either assembly, on
// purpose - a hard reference would stop the companion loading on any install missing
// the mod (same rule JawaBenchVehicleTools.cs states for Vehicle Framework).
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags PubInstPipe = BindingFlags.Public | BindingFlags.Instance;

        /// <summary>Def.defName off any object by reflection - every Def subclass has it as a public field.</summary>
        private static string DefNameOrNull(object defObj)
        {
            if (defObj == null) return null;
            var v = FieldOrNull(defObj, "defName");
            return v as string;
        }

        /// <summary>Count of any object implementing non-generic ICollection (every List&lt;T&gt; does), or null.</summary>
        private static int? CollectionCountOrNull(object obj)
        {
            var c = obj as ICollection;
            return c != null ? (int?)c.Count : null;
        }

        /// <summary>
        /// A VERIFIED read of one VEF PipeSystem PipeNet, by field/property names
        /// confirmed against the mod's own vendored source (see file header).
        /// </summary>
        private static object ReadVefPipeNet(object pipeNet)
        {
            return new
            {
                verified = true,
                pipeNetDef = DefNameOrNull(FieldOrNull(pipeNet, "def")),
                stored = AsFloat(PropOrNull(pipeNet, "Stored")),
                availableCapacity = AsFloat(PropOrNull(pipeNet, "AvailableCapacity")),
                consumption = AsFloat(PropOrNull(pipeNet, "Consumption")),
                production = AsFloat(PropOrNull(pipeNet, "Production")),
                connectorCount = CollectionCountOrNull(FieldOrNull(pipeNet, "connectors")),
                storageCount = CollectionCountOrNull(FieldOrNull(pipeNet, "storages")),
                producerCount = CollectionCountOrNull(FieldOrNull(pipeNet, "producers")),
                receiverCount = CollectionCountOrNull(FieldOrNull(pipeNet, "receivers")),
            };
        }

        /// <summary>
        /// UNVERIFIED generic dump: every public instance field/property of a
        /// primitive-ish type (bool/numeric/string/enum) on the given component.
        /// No name in this dump is source-confirmed - report it as such.
        /// </summary>
        private static List<object> GenericReflectionDump(object component, int cap)
        {
            var rows = new List<object>();
            var t = component.GetType();

            foreach (var f in t.GetFields(PubInstPipe))
            {
                if (rows.Count >= cap) break;
                if (!IsSimpleType(f.FieldType)) continue;
                object v; try { v = f.GetValue(component); } catch (Exception e) { v = "(threw " + e.GetType().Name + ")"; }
                rows.Add(new { member = f.Name, kind = "field", type = f.FieldType.Name, value = v?.ToString(), verified = false });
            }
            foreach (var p in t.GetProperties(PubInstPipe))
            {
                if (rows.Count >= cap) break;
                if (!p.CanRead || p.GetIndexParameters().Length > 0) continue;
                if (!IsSimpleType(p.PropertyType)) continue;
                object v; try { v = p.GetValue(component, null); } catch (Exception e) { v = "(threw " + e.GetType().Name + ")"; }
                rows.Add(new { member = p.Name, kind = "property", type = p.PropertyType.Name, value = v?.ToString(), verified = false });
            }
            return rows;
        }

        private static bool IsSimpleType(Type t)
        {
            return t.IsPrimitive || t.IsEnum || t == typeof(string) || t == typeof(decimal);
        }

        [Tool(
            "jawa/pipe_net_info",
            Description =
                "Read resource-network state across the three modded pipe frameworks active " +
                "on the owner's mod list: VEF PipeSystem, Rimefeller, Dubs Bad Hygiene. VEF " +
                "PipeSystem is read by VERIFIED field names (from the mod's own vendored " +
                "source) - stored/production/consumption/capacity per net, connector/storage/" +
                "producer/receiver counts. Rimefeller and Dubs Bad Hygiene ship DLL-only here " +
                "with no source to verify against, so those two are read by a GENERIC " +
                "reflection dump of whatever public simple-typed fields exist on their map " +
                "component - every row from them carries verified:false. Framework presence is " +
                "detected by scanning map.components for a type whose name contains " +
                "'PipeSystem.PipeNetManager', 'Rimefeller' or 'Hygiene' - a framework absent " +
                "from the mod list reports present:false, not an error.",
            ResultDescription =
                "success, frameworks[] (name, present, componentType). vefPipeSystem: nets[] " +
                "(verified reads, one per PipeNet). rimefeller/dubsBadHygiene: rawFields[] " +
                "(unverified generic dump, capped) when present.")]
        public static async Task<object> PipeNetInfo(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cap on generic-dump rows per unverified framework. Default 40.")]
            int maxGenericFields = 40)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                object vefManager = null, rimefellerComp = null, hygieneComp = null;
                foreach (var c in map.components)
                {
                    if (c == null) continue;
                    var full = c.GetType().FullName ?? "";
                    if (full.IndexOf("PipeSystem.PipeNetManager", StringComparison.OrdinalIgnoreCase) >= 0) vefManager = c;
                    else if (full.IndexOf("Rimefeller", StringComparison.OrdinalIgnoreCase) >= 0 && rimefellerComp == null) rimefellerComp = c;
                    else if (full.IndexOf("Hygiene", StringComparison.OrdinalIgnoreCase) >= 0 && hygieneComp == null) hygieneComp = c;
                }

                var frameworks = new List<object>
                {
                    new { name = "VEF PipeSystem", present = vefManager != null, componentType = vefManager?.GetType().FullName },
                    new { name = "Rimefeller", present = rimefellerComp != null, componentType = rimefellerComp?.GetType().FullName },
                    new { name = "Dubs Bad Hygiene", present = hygieneComp != null, componentType = hygieneComp?.GetType().FullName },
                };

                object vefResult = null;
                if (vefManager != null)
                {
                    var netsField = FieldOrNull(vefManager, "pipeNets") as IEnumerable;
                    var nets = new List<object>();
                    if (netsField != null)
                        foreach (var n in netsField) nets.Add(ReadVefPipeNet(n));
                    vefResult = new { netCount = nets.Count, nets };
                }

                object rimefellerResult = rimefellerComp != null
                    ? new { note = "UNVERIFIED - no vendored source for Rimefeller's map component. Generic reflection dump.", rawFields = GenericReflectionDump(rimefellerComp, maxGenericFields) }
                    : null;
                object hygieneResult = hygieneComp != null
                    ? new { note = "UNVERIFIED - no vendored source for Dubs Bad Hygiene's map component. Generic reflection dump.", rawFields = GenericReflectionDump(hygieneComp, maxGenericFields) }
                    : null;

                return new
                {
                    success = true,
                    frameworks,
                    vefPipeSystem = vefResult,
                    rimefeller = rimefellerResult,
                    dubsBadHygiene = hygieneResult,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
