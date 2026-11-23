// JawaBenchFirstExceptionCore.cs - the PURE half of the first-exception tap (no Verse, no Unity, no Harmony).
// Page: design/specs/2026-11-23-first-exception-tap/boundary.md. Compiled into bridgetools/LiveToolsSelfTest too: a
// `using Verse;` here breaks that build.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchFirstExceptionCore
    {
        internal const int MaxKept = 16, MaxKeys = 256, MaxText = 8000;
        internal const string Seen = "SEEN", NoneSeen = "NONE_SEEN", NonePartial = "NONE_SEEN_PARTIAL", NotArmed = "NOT_ARMED";
        private static readonly Regex Ex = new Regex(@"Exception\b", RegexOptions.CultureInvariant);

        internal static bool IsExceptionText(string text) => text != null && Ex.IsMatch(text);
        internal static string Clip(string s) => s == null || s.Length <= MaxText ? s : s.Substring(0, MaxText) + "... [" + (s.Length - MaxText) + " more characters]";

        /// <summary>What makes two exceptions the same: the first line and the first stack frame.</summary>
        internal static string KeyOf(string text)
        {
            var lines = (text ?? "").Split('\n');
            var at = lines.FirstOrDefault(l => l.TrimStart().StartsWith("at ", StringComparison.Ordinal));
            var k = lines[0].Trim() + "|" + (at ?? "").Trim();
            return k.Length <= 400 ? k : k.Substring(0, 400);
        }

        internal sealed class Entry
        {
            internal long Seq, Repeats;
            internal string Source, Text, Stack, Utc, Thread, ProgramState, Key;
            internal int? Tick;
            internal double UptimeS;
            internal bool IsException;
        }

        /// <summary>The tap's store. Any thread. `fill` reads the costly parts (stack, tick) and runs only for an entry that
        /// is kept, so a storm costs a dictionary lookup per error.</summary>
        internal sealed class Tap
        {
            private readonly object _gate = new object();
            private readonly List<Entry> _kept = new List<Entry>();
            private readonly Dictionary<string, Entry> _byKey = new Dictionary<string, Entry>();
            private readonly Dictionary<string, long> _keys = new Dictionary<string, long>();
            private long _seq, _exceptions, _errors, _silenced, _wExceptions, _wErrors, _notKept, _keysDropped;
            private Entry _sEx, _sErr, _wEx, _wErr;
            internal string Window = "session";
            internal string WindowUtc;

            internal void Note(string source, string text, bool unityException, bool silenced, Action<Entry> fill)
            {
                bool isEx = unityException || IsExceptionText(text);
                lock (_gate)
                {
                    long seq = ++_seq;
                    if (silenced) _silenced++;
                    if (isEx) { _exceptions++; _wExceptions++; } else { _errors++; _wErrors++; }
                    bool firstOfKind = isEx ? (_sEx == null || _wEx == null) : (_sErr == null || _wErr == null);
                    string key = KeyOf(text);
                    Entry known;
                    _byKey.TryGetValue(key, out known);
                    if (known != null) known.Repeats++;
                    if (isEx)
                    {
                        long n;
                        if (_keys.TryGetValue(key, out n)) _keys[key] = n + 1;
                        else if (_keys.Count < MaxKeys) _keys[key] = 1;
                        else _keysDropped++;
                    }
                    bool keep = isEx && known == null && _kept.Count < MaxKept;
                    if (isEx && known == null && !keep) _notKept++;
                    if (!firstOfKind && !keep) return;
                    var e = new Entry { Seq = seq, Source = source, Text = Clip(text), Key = key, IsException = isEx, Repeats = 1 };
                    try { fill?.Invoke(e); } catch (Exception x) { e.Stack = "stack could not be read: " + x.GetType().Name; }
                    e.Stack = Clip(e.Stack);
                    if (keep) { _kept.Add(e); _byKey[key] = e; }
                    if (isEx) { if (_sEx == null) _sEx = e; if (_wEx == null) _wEx = e; }
                    else { if (_sErr == null) _sErr = e; if (_wErr == null) _wErr = e; }
                }
            }

            internal void NewWindow(string label, string utc)
            {
                lock (_gate) { _wEx = null; _wErr = null; _wExceptions = 0; _wErrors = 0; Window = label; WindowUtc = utc; }
            }

            internal Entry SessionException { get { lock (_gate) return _sEx; } }
            internal Entry SessionError { get { lock (_gate) return _sErr; } }
            internal Entry WindowException { get { lock (_gate) return _wEx; } }
            internal Entry WindowError { get { lock (_gate) return _wErr; } }
            internal long Exceptions { get { lock (_gate) return _exceptions; } }
            internal long Errors { get { lock (_gate) return _errors; } }
            internal long WindowExceptions { get { lock (_gate) return _wExceptions; } }
            internal long WindowErrors { get { lock (_gate) return _wErrors; } }
            internal long Silenced { get { lock (_gate) return _silenced; } }
            internal long NotKept { get { lock (_gate) return _notKept; } }
            internal long KeysDropped { get { lock (_gate) return _keysDropped; } }
            internal int DistinctKeys { get { lock (_gate) return _keys.Count; } }
            internal List<Entry> Kept() { lock (_gate) return _kept.ToList(); }
        }

        /// <summary>The state a reader may act on. blind = the channels that could have missed one, empty when none.</summary>
        internal static string State(bool armed, bool seen, ICollection<string> blind)
            => seen ? Seen : !armed ? NotArmed : blind != null && blind.Count > 0 ? NonePartial : NoneSeen;

        /// <summary>One error reaches the tap by two roads: Log.Error (which then calls Unity's logger) and Unity's callback.
        /// Per thread: inside a Log.Error the Unity road is a copy, and an ErrorOnce that never reached Log.Error was silenced.</summary>
        internal sealed class Roads
        {
            private int _depth;
            private bool _onceOpen, _onceReached;
            internal void EnterError() { _depth++; _onceReached = true; }
            internal void ExitError() { if (_depth > 0) _depth--; }
            internal bool UnityIsACopy => _depth > 0;
            internal void EnterOnce() { _onceOpen = true; _onceReached = false; }
            /// <summary>true when the game kept this ErrorOnce silent.</summary>
            internal bool ExitOnce() { bool silent = _onceOpen && !_onceReached; _onceOpen = false; return silent; }
        }
    }
}
