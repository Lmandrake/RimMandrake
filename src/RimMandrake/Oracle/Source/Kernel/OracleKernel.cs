// Verse-free kernel of the Oracle (llm_ingame_wiring_spec.md): the `claude -p` command line and its Windows quoting, the
// timeout arithmetic, the launch-candidate order, the retry policy, the exit-code / output classification, the per-day call
// budget, the delivery choice (laws #1 and #2) and the main-thread delivery queue. OracleClient and OracleGameComponent call
// this; SelfTest/ compiles this file (and OracleValidator / OracleRegisterBlocks) alone: no Verse, RimWorld or UnityEngine.
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Text;

namespace RimMandrake.Oracle
{
    public static class OracleKernel
    {
        /// <summary>Tool names denied to the child. The Oracle only ever wants text back. Present on 2.1.228 and 2.1.266 alike.</summary>
        public static readonly string[] DeniedTools =
        {
            "Bash", "Edit", "Write", "Read", "Glob", "Grep",
            "WebFetch", "WebSearch", "Task", "NotebookEdit"
        };

        public const string SafeFallbackText =
            "The old machines hum on, patient, waiting for hands that have not yet come.";

        // ── the command line ────────────────────────────────────────────

        /// <summary>Windows CommandLineToArgvW quoting: backslashes are literal except where they precede a quote.</summary>
        public static string QuoteArgument(string arg)
        {
            var sb = new StringBuilder();
            sb.Append('"');
            int i = 0;
            while (i < arg.Length)
            {
                int backslashes = 0;
                while (i < arg.Length && arg[i] == '\\')
                {
                    backslashes++;
                    i++;
                }

                if (i == arg.Length)
                {
                    sb.Append('\\', backslashes * 2);
                }
                else if (arg[i] == '"')
                {
                    sb.Append('\\', backslashes * 2 + 1).Append('"');
                    i++;
                }
                else
                {
                    sb.Append('\\', backslashes).Append(arg[i]);
                    i++;
                }
            }
            sb.Append('"');
            return sb.ToString();
        }

        public static string BuildArguments(string systemPrompt)
        {
            var sb = new StringBuilder();
            sb.Append("-p --output-format text");
            sb.Append(" --system-prompt ").Append(QuoteArgument(systemPrompt ?? string.Empty));
            sb.Append(" --disallowed-tools");
            foreach (string tool in DeniedTools)
            {
                sb.Append(' ').Append(tool);
            }
            return sb.ToString();
        }

        /// <summary>The system prompt of one call: the law, then exactly ONE god's register block (never the whole cast).</summary>
        public static string SystemPrompt(string law, string godBlock) { return law + "\n\n" + godBlock; }

        // ── timeout ─────────────────────────────────────────────────────

        /// <summary>
        /// Process.WaitForExit wants milliseconds as an int: -1 is "forever" and any other negative throws. A settings value
        /// is whatever the file holds, so seconds * 1000 must saturate, never wrap.
        /// </summary>
        public static int TimeoutMs(int timeoutSeconds)
        {
            long ms = (long)Math.Max(1, timeoutSeconds) * 1000L;
            return ms > int.MaxValue ? int.MaxValue : (int)ms;
        }

        // ── launch candidates ───────────────────────────────────────────

        /// <summary>
        /// An explicit setting is taken at its word. Otherwise: the one that last started, "claude" on PATH, then the CLI
        /// installer's own location under the user's home. No candidate is listed twice.
        /// </summary>
        public static List<string> Candidates(string cliPathOverride, string resolved, string userProfile, string home)
        {
            var list = new List<string>();
            if (!string.IsNullOrEmpty(cliPathOverride) && cliPathOverride.Trim().Length > 0)
            {
                list.Add(cliPathOverride.Trim());
                return list;
            }
            if (!string.IsNullOrEmpty(resolved))
            {
                list.Add(resolved);
            }
            if (resolved != "claude")
            {
                list.Add("claude");
            }
            string root = string.IsNullOrEmpty(userProfile) ? home : userProfile;
            if (!string.IsNullOrEmpty(root))
            {
                string installed = Path.Combine(root, Path.Combine(".local", Path.Combine("bin", "claude.exe")));
                if (!list.Contains(installed))   // a resolved candidate that IS the installed path is not tried twice
                {
                    list.Add(installed);
                }
            }
            return list;
        }

        // ── retry policy ────────────────────────────────────────────────

        /// <summary>One retry, and only for what can be transient: a timeout's window is spent, a missing binary stays missing.</summary>
        public static bool IsRetryable(Exception e)
        {
            return !(e is TimeoutException) && !(e is FileNotFoundException);
        }

        public delegate string InvokeFn(string executable, string arguments, string userPrompt, int timeoutSeconds, Action<string> started);

        /// <summary>Tries each launch candidate once; a candidate that cannot be started at all is skipped, anything else propagates.</summary>
        public static string RunOnce(InvokeFn invoke, string systemPrompt, string userPrompt, int timeoutSeconds, string cliPathOverride,
            ref string resolved, string userProfile, string home)
        {
            string arguments = BuildArguments(systemPrompt);
            var notFound = new List<string>();
            foreach (string executable in Candidates(cliPathOverride, resolved, userProfile, home))
            {
                string started = resolved;
                try
                {
                    return invoke(executable, arguments, userPrompt, timeoutSeconds, exe => started = exe);
                }
                catch (Win32Exception)
                {
                    notFound.Add(executable);
                }
                finally
                {
                    // A started-then-failed attempt (timeout, bad exit) still pins the executable that started.
                    resolved = started;
                }
            }
            throw new FileNotFoundException(
                "Oracle: could not start the Claude Code CLI. Tried: " + string.Join(", ", notFound.ToArray()) +
                ". Set an explicit path in Mod Settings if it lives somewhere else.");
        }

        public static string RunWithRetry(Func<string> once)
        {
            Exception lastFailure = null;
            for (int attempt = 0; attempt < 2; attempt++)
            {
                try
                {
                    return once();
                }
                catch (Exception e) when (!IsRetryable(e))
                {
                    throw;
                }
                catch (Exception e)
                {
                    lastFailure = e;
                }
            }
            throw lastFailure ?? new Exception("Oracle: claude -p failed with no exception captured");
        }

        // ── what the child said ─────────────────────────────────────────

        public static string Truncate(string s, int max)
        {
            return string.IsNullOrEmpty(s) || s.Length <= max ? s : s.Substring(0, max) + "...";
        }

        /// <summary>
        /// Exit code 0 = success, anything else = failure; stderr on a good run is noise and never an error. A failure's
        /// diagnostic is stderr, or stdout when stderr is silent (an auth failure prints to stdout). A clean exit with no
        /// output is a failure too. Throws on every failure, returns the trimmed reply otherwise.
        /// </summary>
        public static string Classify(int exitCode, string stdout, string stderr)
        {
            if (exitCode != 0)
            {
                string diagnostic = (stderr ?? string.Empty).Trim();
                if (diagnostic.Length == 0)
                {
                    diagnostic = (stdout ?? string.Empty).Trim();
                }
                throw new Exception("Oracle: claude -p exited " + exitCode + " -- " + Truncate(diagnostic, 300));
            }
            string content = (stdout ?? string.Empty).Trim();
            if (string.IsNullOrEmpty(content))
            {
                throw new FormatException("Oracle: claude -p exited 0 but produced no output");
            }
            return content;
        }

        // ── the kill switch and the daily budget ────────────────────────

        public enum Admission { Call, KillSwitchOff, BudgetExhausted }

        /// <summary>
        /// The day rolls the budget over (even with the switch off), then: switch off -> fallback, budget spent -> fallback,
        /// otherwise the call is counted and made. A refusal never counts as a call.
        /// </summary>
        public static Admission Admit(bool enabled, int today, int budgetPerDay, ref int lastResetDay, ref int callsToday, out string reason)
        {
            reason = null;
            if (today != lastResetDay)
            {
                lastResetDay = today;
                callsToday = 0;
            }
            if (!enabled)
            {
                reason = "kill switch off";
                return Admission.KillSwitchOff;
            }
            if (callsToday >= budgetPerDay)
            {
                reason = "budget exhausted for today (" + callsToday + "/" + budgetPerDay + ")";
                return Admission.BudgetExhausted;
            }
            callsToday++;
            return Admission.Call;
        }

        // ── delivery (laws #1 and #2) ───────────────────────────────────

        public enum DeliveryKind { Live, Fallback, SafeDefault }

        /// <summary>What one request finally delivers: the kind, the text and the log reason (null for a live reply).</summary>
        public sealed class Outcome
        {
            public DeliveryKind Kind;
            public string Text;
            public string Reason;
        }

        /// <summary>A request the kill switch or the budget refused: the fallback ships, held to the live bar.</summary>
        public static Outcome Refused(string refusal, string fallbackText)
        {
            return FromFallback(fallbackText, refusal);
        }

        /// <summary>
        /// The end of one call: a reply that passes the lint ships live; a reply the lint rejects, or any failure of the call,
        /// ships the fallback (itself linted, else the safe default). Exactly one text, always lint-clean (laws #1 and #2).
        /// </summary>
        public static Outcome Resolve(string content, Exception failure, string fallbackText)
        {
            if (failure != null)
            {
                return FromFallback(fallbackText, "call failed: " + failure.Message);
            }
            string text, rejectReason;
            if (ChooseForLive(content, out text, out rejectReason) == DeliveryKind.Live)
            {
                return new Outcome { Kind = DeliveryKind.Live, Text = text };
            }
            return FromFallback(fallbackText, "validator rejected: " + rejectReason);
        }

        private static Outcome FromFallback(string fallbackText, string reason)
        {
            string text, fallbackReject;
            DeliveryKind kind = ChooseFallback(fallbackText, out text, out fallbackReject);
            return new Outcome { Kind = kind, Text = text, Reason = kind == DeliveryKind.SafeDefault ? reason + " | fallback rejected: " + fallbackReject : reason };
        }

        /// <summary>A live reply ships only if the register lint passes it.</summary>
        public static DeliveryKind ChooseForLive(string content, out string text, out string rejectReason)
        {
            if (OracleValidator.TryValidateOhm(content, out rejectReason))
            {
                text = content;
                return DeliveryKind.Live;
            }
            text = null;
            return DeliveryKind.Fallback;
        }

        /// <summary>The fallback is held to the same bar as a live reply; if it fails too, the hardcoded safe text ships.</summary>
        public static DeliveryKind ChooseFallback(string fallbackText, out string text, out string rejectReason)
        {
            if (OracleValidator.TryValidateOhm(fallbackText, out rejectReason))
            {
                text = fallbackText;
                return DeliveryKind.Fallback;
            }
            text = SafeFallbackText;
            return DeliveryKind.SafeDefault;
        }
    }

    /// <summary>The main-thread delivery queue: a delivery that throws must not lose the ones queued behind it.</summary>
    public sealed class OracleDeliveryQueue
    {
        private readonly ConcurrentQueue<Action> pending = new ConcurrentQueue<Action>();
        public int Count { get { return pending.Count; } }
        public void Enqueue(Action a) { pending.Enqueue(a); }

        public int Drain(Action<Exception> onError)
        {
            int ran = 0;
            Action action;
            while (pending.TryDequeue(out action))
            {
                try
                {
                    action();
                }
                catch (Exception e)
                {
                    onError(e);
                }
                ran++;
            }
            return ran;
        }
    }
}
