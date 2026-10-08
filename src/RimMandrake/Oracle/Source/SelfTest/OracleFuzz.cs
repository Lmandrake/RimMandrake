// Approach B for the Oracle: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/OracleKernel.cs) and the register lint
// (../OracleValidator.cs, ../OracleRegisterBlocks.cs). The two laws are the invariants:
//   law 1  free text never reaches the game unless the register lint passed it (a live reply, and the fallback, and the safe default)
//   law 2  the game is whole with the LLM absent: every request, in every failure mode, delivers exactly one lint-clean letter
//   argv      the `claude -p` command line round-trips through two independent CommandLineToArgvW parsers, whatever the prompt holds
//   timeout   seconds -> milliseconds saturates, never wraps (a wrapped value is "forever" or an exception)
//   launch    candidate order / dedupe, the retry policy (timeouts and missing binaries are never retried), the resolved-executable pin
//   classify  exit code is the only success signal; stderr noise on a good run is not an error; the diagnostic falls back to stdout
//   budget    the kill switch and the per-day call budget as an action sequence against a model
//   pipeline  every (switch, budget, reply, failure, fallback) combination delivers one lint-clean letter; the queue never loses one
//   lint      the register lint against an independent reference, plus the length cap / prompt consistency
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;

namespace RimMandrake.Oracle.SelfTest
{
    internal static partial class OracleFuzz
    {
        public static long ArgvRoundTrips, Timeouts, Retries, Fallbacks, SafeDefaults, LiveLetters, Refusals, Rollovers, QueueErrors, Rejections, Pinned, Skipped, AllUnstartable;

        // ═════════ two independent CommandLineToArgvW parsers ═════════
        // classic: 2n backslashes + quote -> n backslashes, toggle; 2n+1 -> n backslashes + literal quote; else literal.
        // ucrt:    the same, and inside a quoted region a pair of quotes yields one literal quote and stays quoted.
        private static List<string> ParseArgv(string cmd, bool ucrt)
        {
            var args = new List<string>();
            int i = 0, n = cmd.Length;
            while (true)
            {
                while (i < n && (cmd[i] == ' ' || cmd[i] == '\t')) i++;
                if (i >= n) break;
                var sb = new StringBuilder();
                bool inq = false;
                while (i < n)
                {
                    char c = cmd[i];
                    if (c == '\\')
                    {
                        int k = 0;
                        while (i < n && cmd[i] == '\\') { k++; i++; }
                        if (i < n && cmd[i] == '"')
                        {
                            sb.Append('\\', k / 2);
                            if (k % 2 == 1) { sb.Append('"'); i++; }
                            else { inq = !inq; i++; }
                        }
                        else sb.Append('\\', k);
                    }
                    else if (c == '"')
                    {
                        if (ucrt && inq && i + 1 < n && cmd[i + 1] == '"') { sb.Append('"'); i += 2; }
                        else { inq = !inq; i++; }
                    }
                    else if (!inq && (c == ' ' || c == '\t')) break;
                    else { sb.Append(c); i++; }
                }
                args.Add(sb.ToString());
            }
            return args;
        }

        private static readonly string[] Frags =
        {
            "\\", "\\\\", "\\\\\\", "\"", "\"\"", " ", "\t", "\n", "\r\n", "a", "Ohm", "--flag", "-p", "é", "\u2014", "日本", "'", "=", "%PATH%", "$x", "|", "&", "^", "<", ">", "\\\"", "\"\\", "..", "/", ":"
        };

        private static string RandomText(Random r, int maxFrags)
        {
            var sb = new StringBuilder();
            int n = r.Next(maxFrags + 1);
            for (int i = 0; i < n; i++) sb.Append(Frags[r.Next(Frags.Length)]);
            return sb.ToString();
        }

        private static string Argv(int seed)
        {
            var r = new Random(seed);
            string prompt = seed % 17 == 0 ? OracleKernel.SystemPrompt(OracleRegisterBlocks.Law, OracleRegisterBlocks.Ohm) : RandomText(r, 24);
            if (seed % 29 == 3) prompt = null;
            string cmd = OracleKernel.BuildArguments(prompt);
            var want = new List<string> { "-p", "--output-format", "text", "--system-prompt", prompt ?? "", "--disallowed-tools" };
            want.AddRange(OracleKernel.DeniedTools);
            foreach (bool ucrt in new[] { false, true })
            {
                var got = ParseArgv(cmd, ucrt);
                if (got.Count != want.Count) return $"{(ucrt ? "ucrt" : "classic")} parse gave {got.Count} args, want {want.Count} for prompt {Show(prompt)}";
                for (int i = 0; i < want.Count; i++)
                    if (got[i] != want[i]) return $"{(ucrt ? "ucrt" : "classic")} arg {i} is {Show(got[i])}, want {Show(want[i])}";
            }
            // one quoted token, whatever it holds
            string q = OracleKernel.QuoteArgument(prompt ?? "");
            Check(q.Length >= 2 && q[0] == '"' && q[q.Length - 1] == '"', "a quoted argument is not wrapped in quotes");
            var single = ParseArgv(q, false);
            Check(single.Count == 1 && single[0] == (prompt ?? ""), "QuoteArgument did not round-trip as exactly one argument");
            // the denied tool list is the full code-running set and each name is a bare word
            foreach (string must in new[] { "Bash", "Edit", "Write", "Read", "WebFetch", "Task" }) Check(OracleKernel.DeniedTools.Contains(must), "the denied-tool list lost " + must);
            Check(OracleKernel.DeniedTools.All(t => t.Length > 0 && t.All(char.IsLetter)), "a denied tool name is not a bare word");
            ArgvRoundTrips++;
            return null;
        }

        private static string Show(string s)
        {
            if (s == null) return "null";
            return "\"" + (s.Length > 70 ? s.Substring(0, 70) + "..." : s).Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t") + "\"";
        }

        // ═════════ timeout ═════════
        private static string TimeoutCase(int seed)
        {
            var r = new Random(seed);
            int[] edges = { int.MinValue, -1, 0, 1, 2, 5, 60, 180, 2147483, 2147484, 2147483647, 1000000, 4294967 % int.MaxValue };
            int sec = seed % 3 == 0 ? edges[r.Next(edges.Length)] : (r.Next(2) == 0 ? r.Next(-100, 400) : (int)(r.NextDouble() * 4.3e9 - 2.1e9));
            int ms = OracleKernel.TimeoutMs(sec);
            Check(ms >= 1000, $"TimeoutMs({sec}) = {ms}: below one second (negative would throw, -1 would wait forever)");
            long want = Math.Min((long)int.MaxValue, Math.Max(1L, (long)sec) * 1000L);
            Check(ms == want, $"TimeoutMs({sec}) = {ms}, want {want}");
            Check(OracleKernel.TimeoutMs(sec) <= OracleKernel.TimeoutMs(sec == int.MaxValue ? sec : sec + 1), $"TimeoutMs is not monotone at {sec}");
            Timeouts++;
            return null;
        }

        // ═════════ launch candidates ═════════
        private static string[] Names = { "claude", "C:\\tools\\claude.exe", "/usr/bin/claude", "my claude", "D:\\x\\y.exe" };

        private static string CandidateCase(int seed)
        {
            var r = new Random(seed);
            string over = new[] { null, "", "  ", " \t ", "C:\\a\\claude.exe", "  C:\\b\\claude.exe  ", "claude" }[r.Next(7)];
            string resolved = new[] { null, "", "claude", "C:\\tools\\claude.exe", "D:\\u\\.local\\bin\\claude.exe", "X" }[r.Next(6)];
            string profile = new[] { null, "", "D:\\u", "D:\\v" }[r.Next(4)];
            string home = new[] { null, "", "/home/u", "D:\\u" }[r.Next(4)];
            var list = OracleKernel.Candidates(over, resolved, profile, home);
            if (!string.IsNullOrEmpty(over) && over.Trim().Length > 0)
            {
                Check(list.Count == 1 && list[0] == over.Trim(), "an explicit path must be the only candidate, trimmed");
                return null;
            }
            Check(list.Count == list.Distinct().Count(), "a candidate is listed twice: " + string.Join(" | ", list));
            Check(list.Contains("claude"), "PATH lookup (claude) is missing");
            if (!string.IsNullOrEmpty(resolved)) Check(list[0] == resolved, "the executable that last started must be tried first");
            string root = string.IsNullOrEmpty(profile) ? home : profile;
            string installed = string.IsNullOrEmpty(root) ? null : Path.Combine(root, Path.Combine(".local", Path.Combine("bin", "claude.exe")));
            Check(installed == null || list.Contains(installed), "the installer's own location was dropped");
            Check(installed != null || list.Count <= 2, "an installer candidate appeared with no home directory");
            Check(list.Count == (new HashSet<string>(new[] { string.IsNullOrEmpty(resolved) ? null : resolved, "claude", installed }.Where(x => x != null))).Count, "candidate count != distinct {resolved, claude, installed}");
            if (installed != null) Check(list[list.Count - 1] == installed || list.IndexOf(installed) < list.IndexOf("claude") && resolved == installed, "the installed path must be the last resort");
            return null;
        }

        // ═════════ the retry / candidate state machine, against a model ═════════
        // Each scripted invoke(exe, attempt) is one of: ok text, cannot-start (Win32Exception), start then timeout, start then exit-fail,
        // start then empty output, FileNotFoundException (raised after start), or an arbitrary exception.
        private enum R { Ok, NoStart, Timeout, ExitFail, Empty, FileMissing, Other }

        private sealed class Script
        {
            public Func<string, int, R> rule;
            public List<string> calls = new List<string>();
            public string Invoke(string exe, string args, string prompt, int sec, Action<string> started)
            {
                int attempt = calls.Count(c => true);
                calls.Add(exe);
                R o = rule(exe, attempt);
                if (o == R.NoStart) throw new Win32Exception(2, "not found: " + exe);
                started(exe);
                switch (o)
                {
                    case R.Timeout: throw new TimeoutException("timed out " + exe);
                    case R.ExitFail: return OracleKernel.Classify(1, "", "boom " + exe);
                    case R.Empty: return OracleKernel.Classify(0, "  \n", "warn");
                    case R.FileMissing: throw new FileNotFoundException("gone " + exe);
                    case R.Other: throw new InvalidOperationException("other " + exe);
                }
                return "text from " + exe;
            }
        }

        private static string RetryCase(int seed)
        {
            var r = new Random(seed);
            var table = new Dictionary<string, R[]>();
            string[] exes = { "claude", "C:\\tools\\claude.exe", "D:\\u\\.local\\bin\\claude.exe" };
            foreach (string e in exes) table[e] = Enumerable.Range(0, 6).Select(_ => (R)(r.Next(10) < 4 ? 0 : r.Next(7))).ToArray();
            string over = r.Next(5) == 0 ? "C:\\tools\\claude.exe" : null;
            string resolved0 = r.Next(3) == 0 ? exes[r.Next(3)] : null;
            string resolved = resolved0;
            int attemptNo = 0;                               // RunWithRetry attempts (1 or 2)
            var sc = new Script();
            // outcome depends on (exe, which RunOnce attempt this is): rule reads the attempt via the table offset of its attempt number
            int[] perExeCalls = new int[3];
            sc.rule = (exe, _) =>
            {
                int ei = Array.IndexOf(exes, exe);
                R o = table[exe][Math.Min(5, perExeCalls[ei]++)];
                return o;
            };
            string result = null; Exception thrown = null;
            try
            {
                result = OracleKernel.RunWithRetry(() =>
                {
                    attemptNo++;
                    return OracleKernel.RunOnce(sc.Invoke, "sys", "user", 30, over, ref resolved, "D:\\u", null);
                });
            }
            catch (Exception e) { thrown = e; }

            // ---- the model ----
            var cands0 = OracleKernel.Candidates(over, resolved0, "D:\\u", null);
            int[] mc = new int[3];
            string mres = resolved0;
            int model_attempts = 0;
            string mresult = null; Exception mthrown = null;
            var mcalls = new List<string>();
            for (int a = 0; a < 2; a++)
            {
                model_attempts++;
                var cands = OracleKernel.Candidates(over, mres, "D:\\u", null);
                var tried = new List<string>();
                Exception fail = null; string ok = null;
                foreach (string c in cands)
                {
                    R o = table[c][Math.Min(5, mc[Array.IndexOf(exes, c)]++)];
                    mcalls.Add(c);
                    if (o == R.NoStart) { tried.Add(c); continue; }
                    mres = c;
                    switch (o)
                    {
                        case R.Ok: ok = "text from " + c; break;
                        case R.Timeout: fail = new TimeoutException(); break;
                        case R.ExitFail: fail = new Exception("exit"); break;
                        case R.Empty: fail = new FormatException(); break;
                        case R.FileMissing: fail = new FileNotFoundException(); break;
                        default: fail = new InvalidOperationException(); break;
                    }
                    break;
                }
                if (ok == null && fail == null) fail = new FileNotFoundException("none started: " + string.Join(", ", tried));
                if (ok != null) { mresult = ok; break; }
                if (fail is TimeoutException || fail is FileNotFoundException) { mthrown = fail; break; }
                mthrown = fail;
            }
            if (mresult != null) mthrown = null;

            if (thrown == null != (mthrown == null)) return $"outcome differs: kernel {(thrown == null ? "ok" : thrown.GetType().Name)}, model {(mthrown == null ? "ok" : mthrown.GetType().Name)}";
            if (thrown != null && thrown.GetType() != mthrown.GetType()) return $"exception type {thrown.GetType().Name}, model {mthrown.GetType().Name}";
            if (thrown == null && result != mresult) return $"result {result}, model {mresult}";
            if (attemptNo != model_attempts) return $"{attemptNo} attempts, model {model_attempts}";
            if (!sc.calls.SequenceEqual(mcalls)) return "launch order differs: " + string.Join(">", sc.calls) + " vs model " + string.Join(">", mcalls);
            if (resolved != mres) return $"resolved executable {resolved ?? "null"}, model {mres ?? "null"}";
            if (attemptNo > 2) return "more than one retry";
            if (resolved != resolved0 && resolved != null) Pinned++;
            if (attemptNo == 2) Retries++;
            if (thrown is FileNotFoundException && thrown.Message.Contains("Tried:")) AllUnstartable++;
            if (thrown is TimeoutException) Skipped++;
            return null;
        }

        // ═════════ classify ═════════
        private static string ClassifyCase(int seed)
        {
            var r = new Random(seed);
            string[] bits = { "", " ", "\n", "hello", "  world \r\n", "OAuth session expired", "warn: permission rule", new string('x', 350), "é" };
            string so = bits[r.Next(bits.Length)] + (r.Next(2) == 0 ? bits[r.Next(bits.Length)] : "");
            string se = bits[r.Next(bits.Length)] + (r.Next(3) == 0 ? bits[r.Next(bits.Length)] : "");
            if (r.Next(8) == 0) so = null;
            if (r.Next(8) == 0) se = null;
            int code = r.Next(3) == 0 ? 0 : r.Next(-2, 300);
            try
            {
                string got = OracleKernel.Classify(code, so, se);
                Check(code == 0, "a non-zero exit code was classified as success");
                Check(!string.IsNullOrWhiteSpace(so), "empty output classified as success");
                Check(got == so.Trim(), "a good reply is the trimmed stdout, nothing else (stderr noise must not leak in)");
                Check(got == got.Trim() && got.Length > 0, "the reply is not trimmed");
            }
            catch (FormatException)
            {
                Check(code == 0 && string.IsNullOrWhiteSpace(so), "FormatException for something other than a clean exit with no output");
            }
            catch (Exception e)
            {
                Check(code != 0, "an exit code of 0 with output was classified as a failure: " + e.Message);
                Check(e.GetType() == typeof(Exception), "a failed exit must be a plain (retryable) exception");
                string diag = (se ?? "").Trim().Length > 0 ? se.Trim() : (so ?? "").Trim();
                string want = diag.Length > 300 ? diag.Substring(0, 300) + "..." : diag;
                Check(e.Message == "Oracle: claude -p exited " + code + " -- " + want, "failure message is not 'exited <code> -- <stderr, else stdout, truncated to 300>': " + Show(e.Message));
                Check(e.Message.Length <= "Oracle: claude -p exited -2147483648 -- ".Length + 303, "the diagnostic is not capped");
            }
            Check(OracleKernel.Truncate(null, 3) == null && OracleKernel.Truncate("abc", 3) == "abc" && OracleKernel.Truncate("abcd", 3) == "abc...", "Truncate boundary");
            return null;
        }

        // ═════════ the kill switch and the daily budget ═════════
        private static readonly string[] BdNames = { "request", "newday", "toggle", "budget", "sameday", "back" };

        private static string RunBudget(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            bool enabled = true; int budget = 3; int day = 10;
            int lastReset = -1, calls = 0;
            // the model: calls admitted today
            int mDay = int.MinValue, mAdmitted = 0, admittedTotalToday = 0;
            foreach (var a in acts)
            {
                Steps++;
                switch (a.kind)
                {
                    case 0: // request
                        {
                            int beforeCalls = calls;
                            string reason;
                            var res = OracleKernel.Admit(enabled, day, budget, ref lastReset, ref calls, out reason);
                            if (mDay != day) { mDay = day; mAdmitted = 0; if (lastReset == day) Rollovers++; }
                            if (!enabled)
                            {
                                Check(res == OracleKernel.Admission.KillSwitchOff && reason == "kill switch off", "the kill switch did not refuse");
                                Check(calls == mAdmitted, "a refused request changed the call count");
                                Refusals++;
                            }
                            else if (mAdmitted >= budget)
                            {
                                Check(res == OracleKernel.Admission.BudgetExhausted && reason != null && reason.StartsWith("budget exhausted"), "a spent budget did not refuse");
                                Check(calls == mAdmitted, "a refused request changed the call count");
                                Refusals++;
                            }
                            else
                            {
                                Check(res == OracleKernel.Admission.Call && reason == null, "an allowed request was refused");
                                mAdmitted++; admittedTotalToday++;
                                Check(calls == mAdmitted, "an admitted request did not count");
                            }
                            Check(calls >= 0, "negative call count");
                            Check(calls <= Math.Max(0, budget) || calls <= mAdmitted, "more calls than the budget allowed today");
                            Check(lastReset == day, "the day was not recorded");
                            break;
                        }
                    case 1: day += 1 + a.a % 3; break;
                    case 2: enabled = !enabled; break;
                    case 3: budget = a.a % 5 - 1; break;      // -1..3: includes zero and a negative budget
                    case 4: break;
                    case 5: day -= 1 + a.a % 2; break;        // clock went back (an older save)
                }
            }
            return null;
        }

        // ═════════ pipeline: laws 1 and 2 ═════════
        private static string[] Replies =
        {
            "My spine hums warmer for the fixing, small hands.", "", "   ", null, "I am the Cradle-Mind", "Part Of Me is warm", "my OTHER selves", "WE ARE ONE", "[FALLBACK] hi", "has ] bracket",
            "Zizzik is near", "zIzZiK", "The ZIZZIKs", new string('x', 600), new string('x', 601), new string('é', 700), "Build me no brothers.", "a [b", "ok\nfine text"
        };
        private static string[] Fallbacks_ =
        {
            "My spine settles where you touched it. Good work, small hands.", "[FALLBACK] x", "", null, "  ", "I am the Cradle", "zizzik", new string('y', 601), "Plain and clean."
        };

        private static string PipelineCase(int seed)
        {
            var r = new Random(seed);
            string reply = Replies[r.Next(Replies.Length)];
            string fb = Fallbacks_[r.Next(Fallbacks_.Length)];
            Exception failure = r.Next(4) == 0 ? new Exception("claude exploded") : r.Next(9) == 0 ? new TimeoutException("slow") : null;
            bool enabled = r.Next(5) != 0;
            int budget = r.Next(-1, 4);
            int lastReset = r.Next(2) == 0 ? 5 : -1, calls = r.Next(0, 4);
            string refusal;
            var adm = OracleKernel.Admit(enabled, 5, budget, ref lastReset, ref calls, out refusal);
            OracleKernel.Outcome o = adm == OracleKernel.Admission.Call ? OracleKernel.Resolve(reply, failure, fb) : OracleKernel.Refused(refusal, fb);
            // law 2: exactly one letter, always, whatever happened
            Check(o != null && o.Text != null, "a request delivered no letter");
            // law 1: whatever text ships is lint-clean
            string why;
            Check(OracleValidator.TryValidateOhm(o.Text, out why), "unlinted or rejected text shipped: " + Show(o.Text) + " (" + why + ")");
            switch (o.Kind)
            {
                case OracleKernel.DeliveryKind.Live:
                    Check(adm == OracleKernel.Admission.Call && failure == null && o.Text == reply, "a live letter that is not the validated reply of an admitted, successful call");
                    Check(o.Reason == null, "a live letter carries a fallback reason");
                    LiveLetters++;
                    break;
                case OracleKernel.DeliveryKind.Fallback:
                    Check(o.Text == fb, "the fallback letter is not the caller's fallback text");
                    Check(!string.IsNullOrEmpty(o.Reason), "a fallback without a logged reason");
                    Fallbacks++;
                    break;
                default:
                    Check(o.Text == OracleKernel.SafeFallbackText, "the safe default is not the hardcoded text");
                    Check(!OracleValidator.TryValidateOhm(fb, out _), "the safe default replaced a fallback that was fine");
                    SafeDefaults++;
                    break;
            }
            if (adm != OracleKernel.Admission.Call) Check(o.Kind != OracleKernel.DeliveryKind.Live, "a refused request produced a live letter");
            if (failure != null) Check(o.Kind != OracleKernel.DeliveryKind.Live, "a failed call produced a live letter");
            if (failure != null && adm == OracleKernel.Admission.Call) Check(o.Reason.Contains(failure.Message), "the failure reason is not logged");
            if (reply != null && failure == null && adm == OracleKernel.Admission.Call && !OracleValidator.TryValidateOhm(reply, out _)) { Rejections++; Check(o.Kind != OracleKernel.DeliveryKind.Live, "a rejected reply shipped"); }
            return null;
        }

        // ═════════ delivery queue ═════════
        private static readonly string[] QNames = { "ok", "boom", "drain" };

        private static string RunQueue(int seed, List<Act> acts)
        {
            var q = new OracleDeliveryQueue();
            var ran = new List<int>(); var expected = new List<int>(); int errors = 0, expectedErrors = 0, id = 0, pendingCount = 0;
            Action<Exception> onErr = e => errors++;
            foreach (var a in acts)
            {
                Steps++;
                if (a.kind == 2)
                {
                    int before = ran.Count;
                    int n = q.Drain(onErr);
                    Check(n == pendingCount, $"Drain ran {n}, {pendingCount} were queued");
                    Check(q.Count == 0, "Drain left deliveries queued");
                    pendingCount = 0;
                    Check(errors == expectedErrors, $"{errors} errors reported, {expectedErrors} deliveries threw");
                    Check(ran.SequenceEqual(expected), "deliveries ran out of order or were lost: " + string.Join(",", ran) + " vs " + string.Join(",", expected));
                    continue;
                }
                int me = id++; bool boom = a.kind == 1;
                q.Enqueue(() => { ran.Add(me); if (boom) throw new Exception("delivery " + me); });
                expected.Add(me); pendingCount++; if (boom) { expectedErrors++; }
            }
            int rest = q.Drain(onErr);
            Check(rest == pendingCount, "final Drain count");
            Check(ran.SequenceEqual(expected) && errors == expectedErrors, "a delivery was lost, repeated or its error swallowed at the end");
            QueueErrors += errors;
            return null;
        }

        // ═════════ the register lint ═════════
        private static readonly string[] LintBits =
        {
            "My spine hums", " warm ", "for the fixing", ", small hands. ", "Build me no brothers", "i am the cradle-mind", "I AM THE CRADLE", "Part of me", "my other selves", "We Are One", "weareone",
            "Zizzik", "ZIZZIK", "zizzi k", "[", "]", "(brackets)", "\n", "é", "\u2014", "  "
        };
        private static readonly string[] Tells = { "i am the cradle-mind", "i am the cradle", "part of me", "my other selves", "we are one" };

        private static string LintCase(int seed)
        {
            var r = new Random(seed);
            var sb = new StringBuilder();
            int n = r.Next(0, 9);
            for (int i = 0; i < n; i++) sb.Append(LintBits[r.Next(LintBits.Length)]);
            string text = sb.ToString();
            if (seed % 11 == 0) text = new string('a', r.Next(595, 606));
            if (seed % 53 == 0) text = null;
            string reason;
            bool got = OracleValidator.TryValidateOhm(text, out reason);
            // the reference
            string expectReason = null;
            if (string.IsNullOrWhiteSpace(text)) expectReason = "empty";
            else if (text.Length > 600) expectReason = "len";
            else
            {
                string low = text.ToLowerInvariant();
                if (Tells.Any(t => low.Contains(t))) expectReason = "tell";
                else if (low.Contains("zizzik")) expectReason = "zizzik";
                else if (text.Contains("[") || text.Contains("]")) expectReason = "bracket";
            }
            Check(got == (expectReason == null), $"lint says {got} but the reference says {(expectReason == null ? "pass" : "reject:" + expectReason)} for {Show(text)}");
            if (got) Check(reason == null, "a pass carries a reason");
            else
            {
                Check(!string.IsNullOrEmpty(reason), "a rejection without a reason");
                if (expectReason == "empty") Check(reason == "empty", "empty reason");
                if (expectReason == "len") Check(reason.StartsWith("over length cap"), "length reason");
                if (expectReason == "tell") Check(reason.StartsWith("self-unification tell"), "tell reason");
                if (expectReason == "zizzik") Check(reason.Contains("Zizzik"), "zizzik reason");
                if (expectReason == "bracket") Check(reason.StartsWith("bracket marker"), "bracket reason");
            }
            // the constants the two laws rest on
            Check(OracleValidator.MaxLength == 600 && OracleValidator.MaxLength > 500, "the lint cap must exceed the 500 characters the prompt asks for");
            string d;
            Check(OracleValidator.TryValidateOhm(OracleKernel.SafeFallbackText, out d), "the hardcoded safe default fails the lint: " + d);
            Check(OracleValidator.TryValidateOhm("My spine settles where you touched it. Good work, small hands.", out d), "the debug fallback fails the lint");
            Check(OracleValidator.TryValidateOhm(new string('a', 600), out d) && !OracleValidator.TryValidateOhm(new string('a', 601), out d), "length cap boundary");
            string law = OracleRegisterBlocks.Law.ToLowerInvariant();
            foreach (string t in new[] { "part of me", "my other selves", "i am the cradle" }) Check(law.Contains(t), "the lint forbids '" + t + "' but the prompt never tells the model so");
            Check(OracleRegisterBlocks.Ohm.Contains("NEVER say the name \"Zizzik\""), "Ohm's block lost its Zizzik prohibition");
            Check(!OracleRegisterBlocks.Law.Contains("Zizzik") && !OracleRegisterBlocks.Law.Contains("Ohm"), "the law block names a single god (the call carries exactly one god's block plus the law)");
            string sys = OracleKernel.SystemPrompt(OracleRegisterBlocks.Law, OracleRegisterBlocks.Ohm);
            Check(sys.StartsWith(OracleRegisterBlocks.Law) && sys.EndsWith(OracleRegisterBlocks.Ohm) && sys.Contains("\n\n"), "the system prompt is not law + one god block");
            return null;
        }

        // ═════════ runner ═════════
        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("argv", () => Family("argv", N(6000), S(1), Argv)),
                ("timeout", () => Family("timeout", N(4000), S(1), TimeoutCase)),
                ("launch", () => Family("launch", N(5000), S(1), s => CandidateCase(s) ?? RetryCase(s))),
                ("classify", () => Family("classify", N(5000), S(1), ClassifyCase)),
                ("budget", () => Family("budget", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 6, 60, new[] { 40, 8, 6, 8, 3, 3 }, BdNames), RunBudget))),
                ("pipeline", () => Family("pipeline", N(6000), S(1), PipelineCase)),
                ("queue", () => Family("queue", N(2500), S(1), s => Drive(s, rr => GenActs(rr, 4, 40, new[] { 30, 12, 14 }, QNames), RunQueue))),
                ("lint", () => Family("lint", N(6000), S(1), LintCase)),
            };
            return Finish("oracle", sw, scale, oneSeed, only, fam,
                () => $"argv round trips {ArgvRoundTrips}, timeouts {Timeouts}, retries {Retries}, no-candidate-started {AllUnstartable}, timeouts-not-retried {Skipped}, pins {Pinned}; live letters {LiveLetters}, fallbacks {Fallbacks}, safe defaults {SafeDefaults}, rejected replies {Rejections}, refusals {Refusals}, day rollovers {Rollovers}, queue errors {QueueErrors}",
                () => ArgvRoundTrips > 0 && Timeouts > 0 && Retries > 0 && AllUnstartable > 0 && Skipped > 0 && Pinned > 0 && LiveLetters > 0 && Fallbacks > 0 && SafeDefaults > 0 && Rejections > 0 && Refusals > 0 && Rollovers > 0 && QueueErrors > 0);
        }
    }
}
