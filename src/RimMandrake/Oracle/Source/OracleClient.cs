using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace RimMandrake.Oracle
{
    /// <summary>
    /// The Oracle's transport: the Claude Code CLI in non-interactive mode,
    /// launched as a child process. Owner ruling 2026-09-05 (CLAUDE.md, "In-game
    /// LLM access is the Claude Code CLI, never a hosted API key") replaced the
    /// original OpenAI-compatible HTTP client -- no base URL, no model string,
    /// no API key, no local Ollama. Everything else about the Oracle's shape is
    /// unchanged: the call still runs off the tick, still has one hard timeout,
    /// still has one retry, and still throws on every failure so the caller can
    /// ship its prescribed fallback (spec law #2 -- the game is whole with the
    /// LLM absent).
    ///
    /// INVOCATION, VERIFIED 2026-09-08 against the real binaries, not assumed:
    ///
    ///   claude -p --output-format text --system-prompt "&lt;register&gt;"
    ///          --disallowed-tools Bash Edit Write ...        &lt; prompt-on-stdin
    ///
    /// - The model's reply is the WHOLE of stdout, plain text, nothing else.
    ///   (--output-format json wraps it in a large object whose key order is not
    ///   stable between runs; text mode needs no parser at all, so there is no
    ///   parser here to get it wrong.)
    /// - Exit code 0 = success, non-zero = failure. That is the only reliable
    ///   signal: stderr carries unrelated warnings on a PERFECTLY GOOD run
    ///   (an unrelated permission-rule notice was observed on a successful
    ///   call), so a non-empty stderr must never be read as an error.
    /// - The prompt goes in on stdin, not as an argument. Stdin has no length
    ///   limit, and it cannot be swallowed by the variadic --disallowed-tools
    ///   list the way a trailing positional argument can.
    /// - Version skew is real and matters: the owner's Windows binary was
    ///   2.1.228 while this WSL checkout had 2.1.266, and --restricted (the
    ///   obvious way to strip the code-running tools) exists ONLY on the newer
    ///   one -- passing it to the game machine's binary exits 1 with "unknown
    ///   option". Every flag used here is present on BOTH. Do not add a flag to
    ///   this list without checking the version the game machine actually has.
    /// </summary>
    public static class OracleClient
    {
        /// <summary>
        /// Tool names denied to the child. The Oracle only ever wants text back;
        /// an agent with a shell in the RimWorld install directory is not the
        /// deal. Present on 2.1.228 and 2.1.266 alike. An unknown name in this
        /// list is inert -- it is a filter, not a lookup.
        /// </summary>
        private static readonly string[] DeniedTools =
        {
            "Bash", "Edit", "Write", "Read", "Glob", "Grep",
            "WebFetch", "WebSearch", "Task", "NotebookEdit"
        };

        /// <summary>
        /// The candidate that last started successfully. Resolution is only
        /// interesting once: the game process's PATH is whatever Steam handed
        /// it, so the first call may have to try more than one name, and every
        /// call after it should not.
        /// </summary>
        private static string resolvedExecutable;

        /// <summary>
        /// Runs one completion and returns the model's text. Throws on ANY
        /// failure (binary missing, non-zero exit, timeout, empty output) --
        /// callers catch and fall back, per the spec's law #2: no exception may
        /// ever reach the player.
        ///
        /// Blocking work is wrapped in a Task so the caller's await shape is
        /// exactly what it was under the HTTP client.
        /// </summary>
        public static Task<string> RequestCompletion(
            string systemPrompt, string userPrompt, int timeoutSeconds, string cliPathOverride)
        {
            return Task.Run(() => RunWithRetry(systemPrompt, userPrompt, timeoutSeconds, cliPathOverride));
        }

        private static string RunWithRetry(
            string systemPrompt, string userPrompt, int timeoutSeconds, string cliPathOverride)
        {
            Exception lastFailure = null;

            // One retry, as the spec has always specified -- but only for a
            // non-zero exit, which can be a transient upstream error. A timeout
            // is not retried (the window it was given is already spent) and a
            // missing binary is not retried (it will be just as missing).
            for (int attempt = 0; attempt < 2; attempt++)
            {
                try
                {
                    return RunOnce(systemPrompt, userPrompt, timeoutSeconds, cliPathOverride);
                }
                catch (TimeoutException)
                {
                    throw;
                }
                catch (FileNotFoundException)
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

        private static string RunOnce(
            string systemPrompt, string userPrompt, int timeoutSeconds, string cliPathOverride)
        {
            string arguments = BuildArguments(systemPrompt);
            var notFound = new List<string>();

            foreach (string executable in Candidates(cliPathOverride))
            {
                try
                {
                    return Invoke(executable, arguments, userPrompt, timeoutSeconds);
                }
                catch (Win32Exception)
                {
                    // Could not be started at all -- almost always "not on this
                    // process's PATH". Try the next candidate; if none of them
                    // start, that is a FileNotFoundException below, which is a
                    // configuration fact and never worth a retry.
                    notFound.Add(executable);
                }
            }

            throw new FileNotFoundException(
                "Oracle: could not start the Claude Code CLI. Tried: " + string.Join(", ", notFound.ToArray()) +
                ". Set an explicit path in Mod Settings if it lives somewhere else.");
        }

        private static string Invoke(string executable, string arguments, string userPrompt, int timeoutSeconds)
        {
            var psi = new ProcessStartInfo(executable, arguments)
            {
                UseShellExecute = false,
                CreateNoWindow = true,          // never flash a console over the game
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                // A neutral working directory. Claude Code picks up project
                // context from its cwd; started inside the RimWorld install it
                // would read whatever happens to sit there.
                WorkingDirectory = Path.GetTempPath()
            };

            using (var proc = new Process())
            {
                proc.StartInfo = psi;

                var stdout = new StringBuilder();
                var stderr = new StringBuilder();
                proc.OutputDataReceived += (s, e) => { if (e.Data != null) stdout.AppendLine(e.Data); };
                proc.ErrorDataReceived += (s, e) => { if (e.Data != null) stderr.AppendLine(e.Data); };

                proc.Start();
                resolvedExecutable = executable;

                proc.BeginOutputReadLine();
                proc.BeginErrorReadLine();

                // Write the prompt as real UTF-8 bytes over the raw stream. The
                // net472 StandardInput writer uses the console's code page,
                // which mangles anything outside it (an em dash becomes '?');
                // the child reads UTF-8 regardless. Closing stdin is what tells
                // the CLI the prompt is complete -- without it, it waits forever.
                using (var stdin = new StreamWriter(proc.StandardInput.BaseStream, new UTF8Encoding(false)))
                {
                    stdin.Write(userPrompt ?? string.Empty);
                }

                int timeoutMs = Math.Max(1, timeoutSeconds) * 1000;
                if (!proc.WaitForExit(timeoutMs))
                {
                    try { proc.Kill(); } catch { /* already gone between the check and the kill */ }
                    throw new TimeoutException("Oracle: claude -p timed out after " + timeoutSeconds + "s");
                }

                // The timed overload returns as soon as the process exits; this
                // one additionally waits for the async output handlers above to
                // finish, without which the last lines can still be in flight.
                proc.WaitForExit();

                if (proc.ExitCode != 0)
                {
                    throw new Exception(
                        "Oracle: claude -p exited " + proc.ExitCode + " -- " + Truncate(stderr.ToString().Trim(), 300));
                }

                string content = stdout.ToString().Trim();
                if (string.IsNullOrEmpty(content))
                {
                    throw new FormatException("Oracle: claude -p exited 0 but produced no output");
                }
                return content;
            }
        }

        /// <summary>
        /// An explicit setting is taken at its word -- if it is wrong, that is a
        /// visible failure rather than a silent fall-through to some other
        /// binary. Otherwise: PATH first, then the location the CLI's own
        /// installer uses, which is where the owner's copy actually lives but is
        /// not necessarily on a Steam-launched process's PATH.
        /// </summary>
        private static IEnumerable<string> Candidates(string cliPathOverride)
        {
            if (!string.IsNullOrEmpty(cliPathOverride) && cliPathOverride.Trim().Length > 0)
            {
                yield return cliPathOverride.Trim();
                yield break;
            }

            string cached = resolvedExecutable;
            if (!string.IsNullOrEmpty(cached))
            {
                yield return cached;
            }

            if (cached != "claude")
            {
                yield return "claude";
            }

            string home = Environment.GetEnvironmentVariable("USERPROFILE");
            if (string.IsNullOrEmpty(home))
            {
                home = Environment.GetEnvironmentVariable("HOME");
            }
            if (!string.IsNullOrEmpty(home))
            {
                yield return Path.Combine(home, Path.Combine(".local", Path.Combine("bin", "claude.exe")));
            }
        }

        private static string BuildArguments(string systemPrompt)
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

        /// <summary>
        /// Windows CommandLineToArgvW quoting: backslashes are literal except
        /// where they precede a quote, so a run of them before a '"' (or before
        /// the closing quote) has to be doubled. The register blocks are ours,
        /// but they are prose with quotation marks in them, and an unescaped one
        /// would split the argument and hand the rest of the persona to the CLI
        /// as stray flags.
        /// </summary>
        private static string QuoteArgument(string arg)
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

        private static string Truncate(string s, int max) =>
            string.IsNullOrEmpty(s) || s.Length <= max ? s : s.Substring(0, max) + "...";
    }
}
