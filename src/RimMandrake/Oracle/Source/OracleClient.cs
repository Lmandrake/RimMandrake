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

        // The retry policy, the candidate order and the command line live in Kernel/OracleKernel.cs (fuzzed offline); this
        // file is the process plumbing around them.
        private static string RunWithRetry(
            string systemPrompt, string userPrompt, int timeoutSeconds, string cliPathOverride)
        {
            return OracleKernel.RunWithRetry(() => OracleKernel.RunOnce(Invoke, systemPrompt, userPrompt, timeoutSeconds,
                cliPathOverride, ref resolvedExecutable, Environment.GetEnvironmentVariable("USERPROFILE"), Environment.GetEnvironmentVariable("HOME")));
        }

        private static string Invoke(string executable, string arguments, string userPrompt, int timeoutSeconds, Action<string> started)
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
                started(executable);

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

                int timeoutMs = OracleKernel.TimeoutMs(timeoutSeconds);
                if (!proc.WaitForExit(timeoutMs))
                {
                    try { proc.Kill(); } catch { /* already gone between the check and the kill */ }
                    throw new TimeoutException("Oracle: claude -p timed out after " + timeoutSeconds + "s");
                }

                // The timed overload returns as soon as the process exits; this
                // one additionally waits for the async output handlers above to
                // finish, without which the last lines can still be in flight.
                proc.WaitForExit();

                return OracleKernel.Classify(proc.ExitCode, stdout.ToString(), stderr.ToString());
            }
        }
    }
}
