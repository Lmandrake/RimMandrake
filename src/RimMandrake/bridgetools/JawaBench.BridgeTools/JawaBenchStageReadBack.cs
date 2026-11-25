// JawaBenchStageReadBack.cs - the read-back of a staging tool (BRIDGE v2.0; no Verse, no Unity, no Harmony). Page:
// design/specs/2026-11-23-bridge-v2/boundary.md §THE STAGE READ-BACK. Item RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO.
//
// A staging tool (jawa/set_terrain_batch, jawa/destroy_batch, jawa/spawn_pawn, jawa/build_batch) opens one StageReadBack inside
// its main-thread hop, before its first write. After each write it reads the thing back FROM THE GAME and records it: Want is
// what the request asked, Got is what the game holds. StageReadBack.Reply builds the reply block in the same hop. The block
// says only what was read; a request value reaches it only as a "want" beside a wrong read.
//
// Compiled into bridgetools/StageOpsSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal sealed class StageReadBack
    {
        /// <summary>One write, read back. Op: what was written (terrain, thing, pawn). Id is the game's id: never digested.</summary>
        internal sealed class Row
        {
            internal readonly string Op, Id;
            internal readonly int X, Z;
            internal readonly List<KeyValuePair<string, string>> Wants = new List<KeyValuePair<string, string>>(4);
            internal readonly SortedDictionary<string, string> Gots = new SortedDictionary<string, string>(StringComparer.Ordinal);

            internal Row(string op, string id, int x, int z) { Op = op ?? ""; Id = id; X = x; Z = z; }

            /// <summary>What the request asked for this key.</summary>
            internal Row Want(string key, string value) { Wants.Add(new KeyValuePair<string, string>(key, value)); return this; }

            /// <summary>What the game holds for this key, read after the write.</summary>
            internal Row Got(string key, string value) { Gots[key] = value; return this; }

            /// <summary>Each key whose read value is not the wanted one: (key, want, got).</summary>
            internal List<string[]> Wrong()
            {
                var w = new List<string[]>();
                foreach (var kv in Wants)
                {
                    string got;
                    if (!Gots.TryGetValue(kv.Key, out got)) got = null;
                    if (!string.Equals(kv.Value, got, StringComparison.Ordinal)) w.Add(new[] { kv.Key, kv.Value, got });
                }
                return w;
            }

            internal string Line()
            {
                var sb = new StringBuilder(64);
                sb.Append(Op).Append('|').Append(X.ToString(CultureInfo.InvariantCulture)).Append(',').Append(Z.ToString(CultureInfo.InvariantCulture));
                foreach (var kv in Gots) sb.Append('|').Append(kv.Key).Append('=').Append(kv.Value ?? "~");
                return sb.ToString();
            }
        }

        /// <summary>A thing a clean left in its cells. Blocking: it was in the filter and still stands.</summary>
        internal sealed class LeftThing
        {
            internal string Def, Id, Why;
            internal int X, Z;
            internal bool Blocking;
        }

        internal readonly string Tool;
        internal readonly int FrameOpen;
        private readonly List<Row> _rows = new List<Row>();
        private readonly List<LeftThing> _left = new List<LeftThing>();
        private string _refusal, _refusalWhy;
        private int _rowsAtRefusal;

        /// <summary>Wrong rows listed in the reply (each one is also counted and digested). Guards the reply's size: a batch of
        /// up to 70,000 cells (MaxCells) that all read back wrong would send 70,000 rows over the bridge.</summary>
        internal const int ListedWrong = 50;
        /// <summary>Left things listed (each one counted and digested). The same size guard, for a clean of a whole map.</summary>
        internal const int ListedLeft = 50;

        private StageReadBack(string tool, int frame) { Tool = tool; FrameOpen = frame; }

        /// <summary>Open the read-back of one call, inside its main-thread hop, before its first write.</summary>
        internal static StageReadBack Open(string tool, int frame) { return new StageReadBack(tool, frame); }

        /// <summary>A thing was written: record it, then fill Want and Got from the request and from the game.</summary>
        internal Row Made(string op, string id, int x, int z)
        {
            var r = new Row(op, id, x, z);
            _rows.Add(r);
            return r;
        }

        /// <summary>A clean left this thing in its cells.</summary>
        internal void Left(string def, string id, int x, int z, string why, bool blocking)
        {
            _left.Add(new LeftThing { Def = def, Id = id, X = x, Z = z, Why = why, Blocking = blocking });
        }

        /// <summary>The call is refused by name. The rows made before it stay on the reply.</summary>
        internal void Refuse(string name, string why)
        {
            if (_refusal != null) return;
            _refusal = name ?? "REFUSED";
            _refusalWhy = why;
            _rowsAtRefusal = _rows.Count;
        }

        internal int Count { get { return _rows.Count; } }

        /// <summary>FNV-1a 64 over the sorted lines of the read values (rows and left things). Ids, frames and order are not in it.</summary>
        internal string Digest()
        {
            var lines = new List<string>(_rows.Count + _left.Count);
            foreach (var r in _rows) lines.Add(r.Line());
            foreach (var l in _left) lines.Add("left|" + l.X.ToString(CultureInfo.InvariantCulture) + "," + l.Z.ToString(CultureInfo.InvariantCulture) + "|" + l.Def + "|" + l.Why + "|" + (l.Blocking ? "b" : "k"));
            lines.Sort(StringComparer.Ordinal);
            ulong h = 14695981039346656037UL;
            foreach (var s in lines)
            {
                foreach (char c in s) { h ^= c; h *= 1099511628211UL; }
                h ^= '\n'; h *= 1099511628211UL;
            }
            return h.ToString("x16", CultureInfo.InvariantCulture);
        }

        /// <summary>The reply block, built from the read values. Call it in the same hop as the writes; frameNow is that frame.</summary>
        internal static Dictionary<string, object> Reply(StageReadBack rb, int frameNow)
        {
            var faults = new List<string>();
            var wrongRows = new List<object>();
            int wrong = 0;
            foreach (var r in rb._rows)
            {
                var w = r.Wrong();
                if (w.Count == 0) continue;
                wrong++;
                if (wrongRows.Count >= ListedWrong) continue;
                var keys = new List<object>();
                foreach (var k in w) keys.Add(new Dictionary<string, object> { { "key", k[0] }, { "want", k[1] }, { "got", k[2] } });
                wrongRows.Add(RowOut(r, keys));
            }
            int blocking = 0, kept = 0;
            var left = new List<object>();
            foreach (var l in rb._left)
            {
                if (l.Blocking) blocking++; else kept++;
                if (left.Count < ListedLeft)
                    left.Add(new Dictionary<string, object> { { "def", l.Def }, { "id", l.Id }, { "x", l.X }, { "z", l.Z }, { "why", l.Why }, { "blocking", l.Blocking } });
            }
            bool sameFrame = frameNow == rb.FrameOpen;
            if (!sameFrame) faults.Add("frame_moved");
            if (wrong > 0) faults.Add("read_back_wrong");
            if (blocking > 0) faults.Add("left_behind");
            if (rb._refusal != null) faults.Add("refused");
            var made = new List<object>();
            foreach (var r in rb._rows)
                if (made.Count < ListedWrong) made.Add(RowOut(r, null));
            var o = new Dictionary<string, object>
            {
                { "ok", faults.Count == 0 },
                { "tool", rb.Tool },
                { "faults", faults },
                { "frameOpen", rb.FrameOpen },
                { "frameReply", frameNow },
                { "sameFrame", sameFrame },
                { "rows", rb._rows.Count },
                { "rowsWrong", wrong },
                { "wrong", wrongRows },
                { "made", made },
                { "leftBlocking", blocking },
                { "leftKept", kept },
                { "left", left },
                { "digest", rb.Digest() },
            };
            if (rb._refusal != null)
                o["refusal"] = new Dictionary<string, object> { { "name", rb._refusal }, { "why", rb._refusalWhy }, { "madeBefore", rb._rowsAtRefusal } };
            return o;
        }

        private static Dictionary<string, object> RowOut(Row r, List<object> wrong)
        {
            var got = new Dictionary<string, object>();
            foreach (var kv in r.Gots) got[kv.Key] = kv.Value;
            var o = new Dictionary<string, object> { { "op", r.Op }, { "id", r.Id }, { "x", r.X }, { "z", r.Z }, { "got", got } };
            if (wrong != null) o["wrong"] = wrong;
            return o;
        }
    }
}
