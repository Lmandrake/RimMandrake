// The in-process deviation record. The host supplies the journal path and the reads and writes.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using C = JawaBench.BridgeTools.JawaBenchCondCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchDeviationCore
    {
        internal static readonly object Absent = new object();

        internal static string FieldRefusal(FieldInfo field)
        {
            if (field.IsLiteral) return "REFUSED: const " + field.Name;
            if (field.IsStatic && field.IsInitOnly) return "REFUSED: static readonly " + field.Name;
            return null;
        }

        internal sealed class Entry
        {
            internal readonly string Kind, Class, Reach, Target, Settings;
            internal readonly object After;
            internal readonly Func<object> Read;
            internal readonly Action<object> Write;
            internal object Before;
            internal bool Attempted;

            internal Entry(string kind, string @class, string reach, string target, string settings, object after,
                           Func<object> read, Action<object> write)
            {
                Kind = kind; Class = @class; Reach = reach; Target = target; Settings = settings;
                After = after; Read = read; Write = write;
            }

            internal Dictionary<string, object> Row() => new Dictionary<string, object>
            {
                ["kind"] = Kind, ["class"] = Class, ["reach"] = Reach, ["target"] = Target,
                ["before"] = Wire(Before), ["after"] = Wire(After),
                ["state"] = Kind == "overlay" ? "UNVERIFIED" : "recorded"
            };
        }

        private static object Wire(object value)
        {
            if (ReferenceEquals(value, Absent)) return new Dictionary<string, object> { ["state"] = "absent" };
            if (value == null || value is bool || value is string) return value;
            if (value is int || value is float || value is double)
            {
                var number = Convert.ToDouble(value, CultureInfo.InvariantCulture);
                if (!double.IsNaN(number) && !double.IsInfinity(number)) return value;
            }
            return Convert.ToString(value, CultureInfo.InvariantCulture);
        }

        internal sealed class Record
        {
            private readonly List<Entry> _live = new List<Entry>();
            private readonly Dictionary<string, KeyValuePair<object, Func<object>>> _defaults =
                new Dictionary<string, KeyValuePair<object, Func<object>>>(StringComparer.Ordinal);
            private readonly Func<string> _path;
            private string _name, _prior, _journalError;
            private bool _looked, _stationDirty, _stampDirty;
            private string _stamp;
            internal string Holder { get; private set; }
            internal bool Tainted { get; private set; }
            internal bool Spoiled { get; private set; }
            internal bool SaveDirty { get; private set; }
            internal bool ProcessDirty { get; private set; }

            internal Record(Func<string> path) { _path = path; }

            internal string PriorJournal
            {
                get
                {
                    if (_looked) return _prior;
                    try
                    {
                        _prior = File.ReadAllText(_path());
                        _looked = true;
                        _journalError = null;
                    }
                    catch (FileNotFoundException) { _looked = true; _journalError = null; }
                    catch (DirectoryNotFoundException) { _looked = true; _journalError = null; }
                    catch (IOException e) { _journalError = e.Message; }
                    catch (UnauthorizedAccessException e) { _journalError = e.Message; }
                    return _prior;
                }
            }

            internal void ObserveDefault(string target, object value, Func<object> read)
                => _defaults[target] = new KeyValuePair<object, Func<object>>(value, read);

            // Only an overlay of an open session blocks the disk write; a standalone set (no holder) leaves it to the mod.
            internal bool BlocksSettings(string settings) => Holder != null && _live.Any(e => e.Settings != null && e.Settings == settings);

            internal string Apply(string holder, string name, IList<Entry> entries, bool canonical = false)
            {
                if (canonical) return "CANONICAL_SAVE: overlay refused";
                if (Spoiled) return "SPOILED: restart the game";
                if (holder == "" || (_live.Count != 0 && Holder != holder))
                    return "NOT_THE_DRIVER: the deviation record belongs to " + (Holder ?? "standalone settings");
                int from = _live.Count;
                string oldName = _name;
                _name = name ?? oldName ?? "settings";
                _stampDirty = true;
                string target = null;
                try
                {
                    foreach (var entry in entries)
                    {
                        target = entry.Target;
                        entry.Before = entry.Read?.Invoke();
                        _live.Add(entry);
                        if (entry.Settings != null) Journal(entry);
                        if (entry.Kind == "overlay")
                        {
                            Tainted = true;
                            SaveDirty = true;
                        }
                        if (entry.Class == "NOT UNDONE")
                        {
                            _stationDirty |= entry.Reach == "station";
                            SaveDirty |= entry.Reach == "save";
                            ProcessDirty |= entry.Reach == "process";
                        }
                        else
                        {
                            entry.Attempted = true;
                            WriteChecked(entry, entry.After);
                        }
                    }
                    Holder = _live.Count == 0 ? null : holder;
                    return null;
                }
                catch (Exception e)
                {
                    string undo = Undo(from);
                    if (undo == null) _name = oldName;
                    else Holder = holder;
                    return target + ": " + e.Message + (undo == null ? "" : "; " + undo);
                }
            }

            internal string Revert(string holder)
            {
                if (_live.Count != 0 && Holder != holder)
                    return "NOT_THE_DRIVER: the deviation record belongs to " + (Holder ?? "standalone settings");
                string error = Undo(0);
                if (error == null) { Holder = null; _name = null; }
                return error;
            }

            private string Undo(int from)
            {
                var errors = new List<string>();
                bool journaled = _live.Skip(from).Any(e => e.Settings != null && e.Attempted);
                _stampDirty = true;
                for (int i = _live.Count - 1; i >= from; i--)
                {
                    var entry = _live[i];
                    try
                    {
                        // A journal failure can leave an entry that was never poked.
                        if (entry.Attempted && !Equals(entry.Read(), entry.Before))
                            WriteChecked(entry, entry.Before);
                        _live.RemoveAt(i);
                    }
                    catch (Exception e) { errors.Add(entry.Target + ": " + e.Message); }
                }
                if (journaled && errors.Count == 0 && !_live.Any(e => e.Settings != null))
                {
                    try { File.Delete(_path()); }
                    catch (Exception e) { errors.Add("journal: " + e.Message); }
                }
                if (errors.Count == 0) return null;
                Spoiled = true;
                return "SPOILED: " + string.Join(", ", errors);
            }

            private static void WriteChecked(Entry entry, object value)
            {
                entry.Write(value);
                if (!Equals(entry.Read(), value)) throw new InvalidOperationException("read-back differed");
            }

            private void Journal(Entry entry)
            {
                _ = PriorJournal;
                var path = _path();
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                using (var stream = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.Read))
                {
                    byte[] bytes = Encoding.UTF8.GetBytes(C.Canon(entry.Row()) + "\n");
                    stream.Write(bytes, 0, bytes.Length);
                    stream.Flush(true);
                }
            }

            internal void Load(bool tuned, bool dirty = false)
            {
                SaveDirty = tuned || dirty;
                _stationDirty = false;
                Tainted |= tuned;
            }

            internal string OverlayStamp
            {
                get
                {
                    if (!_stampDirty) return _stamp;
                    var rows = _live.Where(e => e.Kind == "overlay").Select(e => (object)new List<object> { e.Target, Wire(e.After) }).ToList();
                    _stamp = null;
                    if (rows.Count > 0)
                        using (var sha = SHA256.Create())
                            _stamp = _name + " " + BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(C.Canon(rows))), 0, 6)
                                .Replace("-", "").ToLowerInvariant();
                    _stampDirty = false;
                    return _stamp;
                }
            }

            private static Dictionary<string, object> LiveRow(Entry entry)
            {
                var row = entry.Row();
                if (entry.Read != null)
                {
                    try
                    {
                        object value = entry.Read();
                        row["current"] = Wire(value);
                        row["readBack"] = Equals(entry.After, value) ? "matches" : "differs";
                    }
                    catch (Exception e) { row["readBack"] = "could not look"; row["detail"] = e.Message; }
                }
                return row;
            }

            internal Dictionary<string, object> Receipt()
            {
                var differences = new List<Dictionary<string, object>>();
                foreach (var item in _defaults)
                {
                    var row = new Dictionary<string, object> { ["target"] = item.Key, ["default"] = Wire(item.Value.Key) };
                    try
                    {
                        object value = item.Value.Value();
                        if (Equals(value, item.Value.Key)) continue;
                        row["value"] = Wire(value);
                        row["state"] = "different";
                    }
                    catch (Exception e) { row["state"] = "could not look"; row["detail"] = e.Message; }
                    differences.Add(row);
                }
                return new Dictionary<string, object>
                {
                    ["entries"] = _live.Select(LiveRow).ToList(), ["overlay"] = OverlayStamp ?? "none",
                    ["clean"] = !Tainted && !Spoiled && !ProcessDirty && !SaveDirty && !_stationDirty && _live.Count == 0,
                    ["tainted"] = Tainted, ["spoiled"] = Spoiled, ["saveDirty"] = SaveDirty,
                    ["processDirty"] = ProcessDirty, ["stationDirty"] = _stationDirty,
                    ["priorJournal"] = PriorJournal, ["journalCouldNotLook"] = _journalError, ["differsFromDefault"] = differences
                };
            }
        }
    }
}
