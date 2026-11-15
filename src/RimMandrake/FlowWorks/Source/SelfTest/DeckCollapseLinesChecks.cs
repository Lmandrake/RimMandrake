// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 3 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P4):
// offline checks on the production collapse selector, fallen-run split and liveness rule (RM_DeckCollapseLinesMath, compiled
// in), the production hook and collapse paths (RM_MapComponent_SuspensionBridges.cs, RM_DeckCollapseLines.cs, read as text) and
// the Gimme Some Slack seam (GSS's RM_FallenWireShock.cs read as text). L1 of the item's verify for phase 3: collapse with a cord
// gives one fallen-wire event and splits the net once; a repeat teardown is idempotent; an unpowered cord shocks nobody; a hose
// on a collapsed deck is cut. Each case has a can-fail. NOT proven here: a pawn in the hole being knocked out by the dropped
// cord in a running game, and the hose reel winding in (L2 live rows, owed).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Collections.Immutable;
using System.Reflection;
using System.Reflection.Emit;
using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DeckCollapseLinesChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Body(string src, string signature)
        {
            int a = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(a >= 0, "missing: " + signature);
            int open = src.IndexOf('{', a);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(a, i - a + 1);
            }
            throw new Exception("unbalanced: " + signature);
        }

        /// <summary>One thing on a square of the row: its line tag (null = not a line), whether it transmits, whether it is gone.</summary>
        private sealed class T
        {
            public int X;
            public LineKind? Kind;
            public bool Source;
            public bool Gone;
        }

        /// <summary>generator(0) | conduit(1) | cord on a deck (2,3,4) | conduit(5) | lamp(6): one power net while the deck stands.</summary>
        private static List<T> Row() => new List<T>
        {
            new T { X = 0, Kind = null, Source = true },
            new T { X = 1, Kind = LineKind.RigidConduit },
            new T { X = 2, Kind = LineKind.FlexCord },
            new T { X = 3, Kind = LineKind.FlexCord },
            new T { X = 4, Kind = LineKind.FlexCord },
            new T { X = 5, Kind = LineKind.RigidConduit },
            new T { X = 6, Kind = null },
        };

        private static readonly int[] Deck = { 2, 3, 4 };

        /// <summary>Net id per cell along the row (-1 = gone): adjacent standing cells share a net.</summary>
        private static int[] Nets(List<T> row)
        {
            var id = new int[row.Count];
            int next = 0;
            for (int i = 0; i < row.Count; i++)
            {
                id[i] = row[i].Gone ? -1 : (i > 0 && !row[i - 1].Gone ? id[i - 1] : next++);
            }
            return id;
        }

        private static int NetCount(List<T> row) => Nets(row).Where(n => n >= 0).Distinct().Count();

        /// <summary>The collapse, as ClearDeckTop + RM_DeckCollapseLines.OnDeckCleared do it: per deck square, select the cords
        /// to drop (and record the square), then destroy everything on it.</summary>
        private static (int dropped, List<(int X, int Z)> fallen) Collapse(List<T> row, bool rulesOn)
        {
            int dropped = 0;
            var fallen = new List<(int X, int Z)>();
            foreach (int x in Deck)
            {
                List<T> sq = row.Where(t => t.X == x).ToList();
                List<T> cords = RM_DeckCollapseLinesMath.CordsToDrop(rulesOn, sq, t => t.Kind, t => t.Gone);
                if (cords.Count > 0)
                {
                    fallen.Add((x, 0));
                    dropped += cords.Count;
                }
                foreach (T t in sq) t.Gone = true;   // ClearDeckTop destroys every building on the square
            }
            return (dropped, fallen);
        }

        /// <summary>Live halves after a collapse: ends are the standing transmitters beside the run; an end is live when its net
        /// holds the generator.</summary>
        private static List<(RM_DeckCollapseLinesMath.Half half, bool live)> Fallen(List<T> row, List<(int X, int Z)> fallen)
        {
            int[] nets = Nets(row);
            var result = new List<(RM_DeckCollapseLinesMath.Half, bool)>();
            foreach (List<(int X, int Z)> run in RM_DeckCollapseLinesMath.Runs(fallen))
            {
                var ends = new List<(int X, int Z)>();
                foreach ((int X, int Z) c in run)
                {
                    foreach (int nx in new[] { c.X - 1, c.X + 1 })
                    {
                        if (nx >= 0 && nx < row.Count && !row[nx].Gone && !run.Contains((nx, 0)) && !ends.Contains((nx, 0))) ends.Add((nx, 0));
                    }
                }
                foreach (RM_DeckCollapseLinesMath.Half h in RM_DeckCollapseLinesMath.Split(run, ends))
                {
                    int net = nets[ends[h.End].X];
                    bool powered = row.Any(t => !t.Gone && t.Source && nets[t.X] == net);
                    result.Add((h, RM_DeckCollapseLinesMath.Live(true, true, true, powered)));
                }
            }
            return result;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("DeckCollapse_cord_drops_one_live_fallen_wire_and_the_net_splits_once", () =>
            {
                List<T> row = Row();
                Assert(NetCount(row) == 1, "standing: one net, the lamp is powered");
                (int dropped, List<(int X, int Z)> fallen) = Collapse(row, true);
                Assert(dropped == 3 && fallen.Count == 3, "can-fail: every cord on the three deck squares falls");
                Assert(NetCount(row) == 2, "can-fail: the net splits into exactly two, generator side and lamp side");
                var halves = Fallen(row, fallen);
                Assert(halves.Count == 2, "a cord cut out of the middle leaves one half per bank");
                Assert(halves.Sum(h => h.half.Cells.Count) == 3 && halves.All(h => h.half.Cells.Contains(h.half.Tip)), "every fallen square belongs to exactly one half, tip included");
                var live = halves.Where(h => h.live).ToList();
                Assert(live.Count == 1 && live[0].half.Cells.Contains((2, 0)), "can-fail: only the half hanging from the generator side is live");
                Assert(live[0].half.Tip.X == 3, "its tip is the square farthest down the run from its end");
                Assert(RM_DeckCollapseLinesMath.LiveMessage(live.Count) != null && RM_DeckCollapseLinesMath.LiveMessage(0) == null,
                    "one message for the live fall, none for a dead one");
                // production: one fallen-wire event per bind that made a live half; the deck squares are recorded through ClearDeckTop
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                string bind = Body(dl, "private void Bind()");
                Assert(bind.Contains("if (live > 0) { LiveFalls++;"), "can-fail: one event per collapse bind, not per square or per half");
                Assert(Body(dl, "public static int OnDeckCleared(Map map, IntVec3 c)").Contains("map.GetComponent<RM_MapComponent_FallenCords>()?.Notify_CordFell(c);"),
                    "the cleared square is handed to the fallen-cord component");
            });

            Case("DeckCollapse_repeat_teardown_is_idempotent", () =>
            {
                List<T> row = Row();
                (int first, List<(int X, int Z)> fallen) = Collapse(row, true);
                (int again, List<(int X, int Z)> more) = Collapse(row, true);
                Assert(first == 3 && again == 0 && more.Count == 0, "can-fail: a second clear of the same squares drops nothing");
                Assert(NetCount(row) == 2, "and splits nothing again");
                var doubled = fallen.Concat(fallen).ToList();
                var runs = RM_DeckCollapseLinesMath.Runs(doubled);
                Assert(runs.Count == 1 && runs[0].Count == 3, "a square recorded twice is one square of one run");
                var a = RM_DeckCollapseLinesMath.Split(runs[0], new List<(int X, int Z)> { (1, 0), (5, 0) });
                var b = RM_DeckCollapseLinesMath.Split(RM_DeckCollapseLinesMath.Runs(fallen)[0], new List<(int X, int Z)> { (1, 0), (5, 0) });
                Assert(a.Count == b.Count && a.Zip(b, (x, y) => x.End == y.End && x.Tip == y.Tip && x.Cells.SequenceEqual(y.Cells)).All(z => z),
                    "re-binding the same squares gives the same halves");
                // production guards: a square is recorded once; gone things are skipped; only a laid hose is cut
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                Assert(Body(dl, "public void Notify_CordFell(IntVec3 c)").Contains("if (pending.Contains(c) || Holds(c)) { return; }"), "can-fail: a fallen square is recorded once");
                Assert(dl.Contains("t => t.Destroyed || !t.Spawned"), "a cord already destroyed is not dropped again");
                Assert(!RM_DeckCollapseLinesMath.HoseCrosses(false, new[] { (3, 0) }, 3, 0), "a hose already reeled in is not cut again");
            });

            Case("DeckCollapse_unpowered_or_disconnected_cord_shocks_nobody", () =>
            {
                List<T> row = Row();
                row[0].Source = false;                                   // the generator is off: no active source anywhere
                var (_, fallen) = Collapse(row, true);
                Assert(Fallen(row, fallen).All(h => !h.live), "can-fail: an unpowered cord falls dead");
                Assert(RM_DeckCollapseLinesMath.Live(true, true, true, true), "can-fail: all four true is live");
                Assert(!RM_DeckCollapseLinesMath.Live(true, true, true, false), "no active source: dead");
                Assert(!RM_DeckCollapseLinesMath.Live(true, false, true, true), "end gone: dead");
                Assert(!RM_DeckCollapseLinesMath.Live(true, true, false, true), "a net the map no longer holds (stale edge): dead");
                Assert(!RM_DeckCollapseLinesMath.Live(false, true, true, true), "rules off: dead");
                Assert(RM_DeckCollapseLinesMath.Split(new List<(int X, int Z)> { (2, 0), (3, 0) }, new List<(int X, int Z)>()).Count == 0,
                    "a run that hangs from nothing makes no half (dropped, never live)");
                Assert(RM_DeckCollapseLinesMath.Split(new List<(int X, int Z)> { (2, 0), (3, 0) }, new List<(int X, int Z)> { (9, 9) }).Count == 0,
                    "an end not beside the run holds nothing");
                // production: GSS gets only live halves, and liveness reads a REGISTERED net
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                Assert(Body(dl, "public IEnumerable<KeyValuePair<IntVec3, IntVec3>> LiveContacts()").Contains("if (!Live(h)) { continue; }"), "can-fail: dead halves give no contact");
                Assert(Body(dl, "public bool Live(RM_FallenCordHalf h)").Contains("map.powerNetManager.AllNetsListForReading.Contains(n)"), "a dropped net never reads powered");
            });

            Case("DeckCollapse_hose_across_a_collapsed_deck_is_reeled_in", () =>
            {
                var trail = new[] { (0, 0), (1, 0), (2, 0), (3, 0) };
                Assert(RM_DeckCollapseLinesMath.HoseCrosses(true, trail, 2, 0), "can-fail: a laid hose over the square is cut");
                Assert(!RM_DeckCollapseLinesMath.HoseCrosses(true, trail, 2, 1), "a hose beside the deck is not");
                Assert(!RM_DeckCollapseLinesMath.HoseCrosses(true, null, 2, 0), "no path, no cut");
                Assert(!RM_DeckCollapseLinesMath.FallsAsWire(LineKind.Hose) && RM_DeckCollapseLinesMath.FallsAsWire(LineKind.FlexCord)
                    && !RM_DeckCollapseLinesMath.FallsAsWire(LineKind.RigidPipe), "only a cord falls as a wire");
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                string hook = Body(dl, "public static int OnDeckCleared(Map map, IntVec3 c)");
                Assert(hook.Contains("RM_DeckCollapseLinesMath.HoseCrosses(r.laid, PathOf(r), c.x, c.z)") && hook.Contains("r.Retract(HoseCutReason);"),
                    "can-fail: the hose router's own retract path cuts it");
                string reel = Src("Hose", "CompHoseReel.cs");
                Assert(Body(reel, "public void Retract(string why)").Contains("ReelIn();"), "retract winds the hose back onto its reel");
            });

            Case("DeckCollapse_every_collapse_path_clears_through_ClearDeckTop", () =>
            {
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(Body(comp, "public static void ClearDeckTop(Map map, IntVec3 c)").Contains("RM_DeckCollapseLines.OnDeckCleared(map, c);"), "can-fail: the hook is in the one funnel");
                Assert(Body(comp, "public void CollapseSpan(Building_SuspensionDeck from, string how)").Contains("ClearDeckTop(map, d.Position);"), "span collapse (broke, taken apart, lost anchor)");
                Assert(comp.Contains("if (st == SpanLoadState.Over && RM_SuspensionSettings.suspensionWeightCollapse)") && comp.Contains("foreach (IntVec3 c in cells) { ClearDeckTop(map, c); }"), "weight overload");
                string deck = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                Assert(Body(deck, "public void DropAlone()").Contains("RM_MapComponent_SuspensionBridges.ClearDeckTop(map, pos);"), "the one-square swing-down");
                Assert(Body(deck, "public override void Destroy(DestroyMode mode = DestroyMode.Vanish)").Contains("b.CollapseSpan(this,"), "a broken or deconstructed square");
                string grav = Src("Pits", "Drawbridge", "RM_DrawbridgeGravship.cs");
                Assert(grav.Contains("comp.CollapseSpan(d, \"was torn loose when the gravship launched\");"), "the gravship launch tears an edge bridge loose");
                // a winch-lost crash is NOT a collapse: the leaf comes down whole and its cords rejoin through the leaf toggle
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string crash = Body(db, "public static void Crash(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)");
                Assert(!crash.Contains("ClearDeckTop") && crash.Contains("Apply(map, r, l);"), "can-fail: the crash lowers the leaf, destroying nothing");
                Assert(Body(db, "public static void Apply(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)").Contains("NotifyToggled(map, changed);"), "lowering re-registers the cords");
            });

            Case("DeckCollapse_GSS_shock_seam_is_soft_and_load_safe", () =>
            {
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                Assert(!csproj.Contains("GimmeSomeSlack.dll") && !csproj.Contains("RimMandrake_GimmeSomeSlack.csproj"), "can-fail: FlowWorks has no compile-time reference to GSS");
                Assert(csproj.Contains("Machinery\\RM_DeckCollapseLinesMath.cs") && csproj.Contains("Machinery\\RM_DeckCollapseLines.cs"), "both files are in the mod build");
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                Assert(dl.Contains("public const string GssShockType = \"RimMandrake.GimmeSomeSlack.Aerial.RM_FallenWireShock\";")
                    && dl.Contains("GenTypes.GetTypeInAnyAssembly(GssShockType)") && dl.Contains("if (t == null) { return;"), "looked up by name; absent GSS is a quiet no-op");
                Assert(dl.Contains("t.GetMethod(\"RegisterLiveWireSource\"") && dl.Contains("new[] { typeof(Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>>) }"),
                    "FlowWorks binds RegisterLiveWireSource by name and its one parameter type (checked against GSS below)");
                Assert(dl.Contains("t.GetMethod(\"LiveWiresChanged\""), "and the change poke by name");
                // GSS is read as COMPILED metadata (the DLL that loads beside FlowWorks), never its source text: the reflection
                // lookups above bind name and parameter types, and nothing else of GSS's signatures (a source pin broke on
                // GSS 63ac285403's new RebuildContacts parameter).
                GssContract.Check(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath(Path.Combine("Rivers", "RM_RiverMath.cs"))),
                    "..", "..", "..", "GimmeSomeSlack", "Assemblies", "RimMandrakeGimmeSomeSlack.dll"));
            });
        }
    }
    /// <summary>What FlowWorks's deck collapse relies on in Gimme Some Slack, read from the compiled DLL: the type its
    /// GenTypes lookup names, the two public static entry points its GetMethod calls bind (name + parameter types), and
    /// the data path behind them (RebuildContacts calls ExternalContacts, which reads the list RegisterLiveWireSource fills).</summary>
    internal static class GssContract
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public const string LiveWireFunc = "System.Func`2<Verse.Map,System.Collections.Generic.IEnumerable`1<System.Collections.Generic.KeyValuePair`2<Verse.IntVec3,Verse.IntVec3>>>";

        public static void Check(string dll)
        {
            Assert(File.Exists(dll), "the GSS DLL is staged: " + dll);
            using (var pe = new PEReader(File.OpenRead(dll)))
            {
                MetadataReader md = pe.GetMetadataReader();
                TypeDefinition type = default;
                bool found = false;
                foreach (TypeDefinitionHandle h in md.TypeDefinitions)
                {
                    TypeDefinition t = md.GetTypeDefinition(h);
                    if (md.GetString(t.Namespace) == "RimMandrake.GimmeSomeSlack.Aerial" && md.GetString(t.Name) == "RM_FallenWireShock") { type = t; found = true; }
                }
                Assert(found, "can-fail: the compiled GSS has the type FlowWorks looks up, RimMandrake.GimmeSomeSlack.Aerial.RM_FallenWireShock");
                Assert((type.Attributes & TypeAttributes.VisibilityMask) == TypeAttributes.Public, "RM_FallenWireShock is public");
                var names = new Names(md);
                MethodDefinition register = One(md, type, names, "RegisterLiveWireSource", "System.Void(" + LiveWireFunc + ")");
                One(md, type, names, "LiveWiresChanged", "System.Void(Verse.Map)");
                HashSet<string> filled = Operands(md, pe, register, ILOpcodeField);
                Assert(filled.Count > 0, "RegisterLiveWireSource keeps its source in a static field");
                MethodDefinition external = Named(md, type, "ExternalContacts");
                Assert(Operands(md, pe, external, ILOpcodeField).Overlaps(filled), "can-fail: ExternalContacts reads the sources RegisterLiveWireSource fills");
                Assert(Operands(md, pe, Named(md, type, "RebuildContacts"), ILOpcodeCall).Contains("ExternalContacts"),
                    "can-fail: GSS feeds the external wires into the same shock and ignition contacts (RebuildContacts calls ExternalContacts)");
            }
        }

        private const int ILOpcodeField = 0x7E, ILOpcodeCall = 0x28;   // ldsfld, call

        private static MethodDefinition Named(MetadataReader md, TypeDefinition type, string name)
        {
            var hits = type.GetMethods().Select(md.GetMethodDefinition).Where(m => md.GetString(m.Name) == name).ToList();
            Assert(hits.Count == 1, "the compiled RM_FallenWireShock has one " + name + " (found " + hits.Count + ")");
            return hits[0];
        }

        private static MethodDefinition One(MetadataReader md, TypeDefinition type, Names names, string name, string want)
        {
            MethodDefinition m = Named(md, type, name);
            MethodSignature<string> sig = m.DecodeSignature(names, null);
            string got = sig.ReturnType + "(" + string.Join(",", sig.ParameterTypes) + ")";
            Assert((m.Attributes & MethodAttributes.Static) != 0 && (m.Attributes & MethodAttributes.MemberAccessMask) == MethodAttributes.Public,
                "can-fail: " + name + " is public static (FlowWorks's GetMethod binds it so)");
            Assert(got == want, "can-fail: the compiled " + name + " is " + got + ", FlowWorks binds " + want);
            return m;
        }

        /// <summary>The names of the fields (ldsfld) or methods (call) one method's IL names, walked opcode by opcode.</summary>
        private static HashSet<string> Operands(MetadataReader md, PEReader pe, MethodDefinition m, int opcode)
        {
            var hits = new HashSet<string>();
            BlobReader il = pe.GetMethodBody(m.RelativeVirtualAddress).GetILReader();
            while (il.RemainingBytes > 0)
            {
                int v = il.ReadByte();
                if (v == 0xFE) v = 0xFE00 | il.ReadByte();
                OpCode op = Ops[unchecked((short)v)];
                switch (op.OperandType)
                {
                    case OperandType.InlineNone: break;
                    case OperandType.ShortInlineBrTarget: case OperandType.ShortInlineI: case OperandType.ShortInlineVar: il.ReadByte(); break;
                    case OperandType.InlineVar: il.ReadInt16(); break;
                    case OperandType.InlineI8: case OperandType.InlineR: il.ReadInt64(); break;
                    case OperandType.InlineSwitch: int n = il.ReadInt32(); for (int i = 0; i < n; i++) il.ReadInt32(); break;
                    default:
                        int token = il.ReadInt32();
                        if (v != opcode) break;
                        EntityHandle h = MetadataTokens.EntityHandle(token);
                        if (h.Kind == HandleKind.FieldDefinition) hits.Add(md.GetString(md.GetFieldDefinition((FieldDefinitionHandle)h).Name));
                        else if (h.Kind == HandleKind.MethodDefinition) hits.Add(md.GetString(md.GetMethodDefinition((MethodDefinitionHandle)h).Name));
                        else if (h.Kind == HandleKind.MemberReference) hits.Add(md.GetString(md.GetMemberReference((MemberReferenceHandle)h).Name));
                        break;
                }
            }
            return hits;
        }

        private static readonly Dictionary<short, OpCode> Ops = typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static)
            .Select(f => (OpCode)f.GetValue(null)).ToDictionary(o => o.Value);

        /// <summary>Type names as C# metadata spells them: Namespace.Name, generics as Name`n&lt;args&gt;.</summary>
        private sealed class Names : ISignatureTypeProvider<string, object>
        {
            private readonly MetadataReader md;
            public Names(MetadataReader md) { this.md = md; }
            public string GetPrimitiveType(PrimitiveTypeCode c) => "System." + c;
            public string GetTypeFromDefinition(MetadataReader r, TypeDefinitionHandle h, byte k) { var t = r.GetTypeDefinition(h); return r.GetString(t.Namespace) + "." + r.GetString(t.Name); }
            public string GetTypeFromReference(MetadataReader r, TypeReferenceHandle h, byte k) { var t = r.GetTypeReference(h); return r.GetString(t.Namespace) + "." + r.GetString(t.Name); }
            public string GetTypeFromSpecification(MetadataReader r, object g, TypeSpecificationHandle h, byte k) => r.GetTypeSpecification(h).DecodeSignature(this, g);
            public string GetGenericInstantiation(string t, ImmutableArray<string> a) => t + "<" + string.Join(",", a) + ">";
            public string GetSZArrayType(string e) => e + "[]";
            public string GetArrayType(string e, ArrayShape s) => e + "[" + new string(',', s.Rank - 1) + "]";
            public string GetByReferenceType(string e) => e + "&";
            public string GetPointerType(string e) => e + "*";
            public string GetPinnedType(string e) => e;
            public string GetModifiedType(string m, string u, bool req) => u;
            public string GetGenericTypeParameter(object g, int i) => "!" + i;
            public string GetGenericMethodParameter(object g, int i) => "!!" + i;
            public string GetFunctionPointerType(MethodSignature<string> s) => "fnptr";
        }
    }
}
