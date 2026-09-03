using System;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace RimMandrake.Oracle
{
    /// <summary>
    /// Thin OpenAI-compatible chat-completions client. One shared HttpClient
    /// (per .NET guidance, never one-per-call), one hard timeout, one retry.
    ///
    /// JSON is hand-rolled, not via a library. RimWorld ships Mono's own
    /// trimmed Managed/ folder -- it does NOT carry System.Web.Extensions
    /// (JavaScriptSerializer) or Newtonsoft.Json, and a NuGet reference-only
    /// facade compiles fine but throws FileNotFoundException at runtime
    /// because reference assemblies carry no IL bodies to ship. The request
    /// shape here is small and fixed (two strings in, one string out), so a
    /// real JSON round trip buys nothing a careful escape/parse pair can't.
    /// </summary>
    public static class OracleHttpClient
    {
        private static readonly HttpClient Client = new HttpClient();

        /// <summary>
        /// Throws on any failure (timeout, non-200, malformed body, empty
        /// content) -- callers are expected to catch and fall back, per the
        /// spec's law #2: no exception may ever reach the player.
        /// </summary>
        public static async Task<string> RequestChatCompletion(
            string baseUrl, string apiKey, string model,
            string systemPrompt, string userPrompt, int timeoutSeconds)
        {
            string body = "{\"model\":" + JsonString(model) +
                          ",\"messages\":[{\"role\":\"system\",\"content\":" + JsonString(systemPrompt) + "}," +
                          "{\"role\":\"user\",\"content\":" + JsonString(userPrompt) + "}]," +
                          "\"max_tokens\":200,\"temperature\":0.9}";

            string url = baseUrl.TrimEnd('/') + "/chat/completions";

            // Each attempt gets its OWN CancellationTokenSource with a fresh
            // timeout window. A CTS built once outside the loop is already
            // cancelled by the time a second attempt runs, so that attempt
            // would fault instantly -- the retry would buy nothing for the
            // one case it exists for.
            for (int attempt = 0; attempt < 2; attempt++)
            {
                using (var cts = new CancellationTokenSource(TimeSpan.FromSeconds(timeoutSeconds)))
                {
                    // Set only for a non-2xx HTTP response (as opposed to a
                    // transport-level failure below) so the two catch blocks
                    // below can tell which kind of HttpRequestException they
                    // are looking at without inspecting its message text.
                    HttpRequestException statusError = null;
                    try
                    {
                        using (var req = new HttpRequestMessage(HttpMethod.Post, url))
                        {
                            req.Content = new StringContent(body, Encoding.UTF8, "application/json");
                            if (!string.IsNullOrEmpty(apiKey))
                            {
                                req.Headers.Add("Authorization", "Bearer " + apiKey);
                            }

                            using (var resp = await Client.SendAsync(req, cts.Token).ConfigureAwait(false))
                            {
                                string respBody = await resp.Content.ReadAsStringAsync().ConfigureAwait(false);
                                if (resp.IsSuccessStatusCode)
                                {
                                    return ExtractContent(respBody);
                                }

                                int statusCode = (int)resp.StatusCode;
                                statusError = new HttpRequestException(
                                    "Oracle: HTTP " + statusCode + " -- " + Truncate(respBody, 300));

                                // Only 408/429 are worth a second try -- every
                                // other 4xx/5xx (401, 400, 404, ...) will fail
                                // identically on retry, so looping just doubles
                                // the billable call and the latency for nothing.
                                bool retryableStatus = statusCode == 408 || statusCode == 429;
                                if (!retryableStatus)
                                {
                                    throw statusError;
                                }
                            }
                        }
                    }
                    catch (TaskCanceledException e)
                    {
                        // The token that just fired belongs to THIS attempt's
                        // timeout window -- looping again would not be a fresh
                        // chance, cts.Token is already cancelled. Fail now.
                        throw new TimeoutException(
                            "Oracle: request timed out after " + timeoutSeconds + "s", e);
                    }
                    catch (HttpRequestException) when (statusError == null && attempt == 0)
                    {
                        // Transport-level failure (DNS, connection refused,
                        // TLS) rather than an HTTP response -- genuinely
                        // transient, worth the one retry the loop allows.
                    }

                    if (statusError != null)
                    {
                        if (attempt == 1) throw statusError;
                        // else: a retryable status on the first attempt -- fall through and loop again.
                    }
                }
            }
            throw new Exception("Oracle: request failed with no exception captured");
        }

        /// <summary>
        /// Finds the value of "content" inside the first "message" object
        /// inside the first element of "choices" -- i.e.
        /// choices[0].message.content -- by locating those three keys in
        /// order and JSON-unescaping the string value that follows the last
        /// one. Deliberately narrow: this is not a general JSON parser, it
        /// answers exactly the one question this client ever asks.
        /// </summary>
        private static string ExtractContent(string responseBody)
        {
            int choicesIdx = IndexOfKey(responseBody, "choices");
            if (choicesIdx < 0) throw new FormatException("Oracle: no \"choices\" key in response");

            int messageIdx = IndexOfKey(responseBody, "message", choicesIdx);
            if (messageIdx < 0) throw new FormatException("Oracle: no \"message\" key after choices in response");

            int contentIdx = IndexOfKey(responseBody, "content", messageIdx);
            if (contentIdx < 0) throw new FormatException("Oracle: no \"content\" key after message in response");

            int colon = responseBody.IndexOf(':', contentIdx);
            if (colon < 0) throw new FormatException("Oracle: malformed \"content\" value");

            // Walk past whitespace to the first real character of the value
            // and check it is actually the opening quote of a JSON string.
            // Skipping straight to the next '"' (as before) is wrong when the
            // value is `null`, a number, or an object -- it finds the OPENING
            // QUOTE OF THE NEXT KEY instead and returns that key's name as if
            // it were model output. "content":null is a normal shape for
            // reasoning models, tool-call turns, and various OpenAI-compatible
            // local servers, so this has to fail loudly, not guess.
            int i = colon + 1;
            while (i < responseBody.Length && char.IsWhiteSpace(responseBody[i])) i++;
            if (i >= responseBody.Length || responseBody[i] != '"')
            {
                throw new FormatException("Oracle: 'content' was not a JSON string (got null or a non-string value)");
            }
            int quoteStart = i;

            string raw = ExtractJsonStringLiteral(responseBody, quoteStart);
            string content = JsonUnescape(raw);
            if (string.IsNullOrWhiteSpace(content)) throw new FormatException("Oracle: content was empty");
            return content.Trim();
        }

        private static int IndexOfKey(string s, string key, int from = 0)
        {
            string needle = "\"" + key + "\"";
            return s.IndexOf(needle, from, StringComparison.Ordinal);
        }

        /// <summary>quoteStart points at the opening '"'. Returns the raw (still-escaped) text between the quotes.</summary>
        private static string ExtractJsonStringLiteral(string s, int quoteStart)
        {
            var sb = new StringBuilder();
            int i = quoteStart + 1;
            while (i < s.Length && s[i] != '"')
            {
                if (s[i] == '\\' && i + 1 < s.Length)
                {
                    sb.Append(s[i]);
                    sb.Append(s[i + 1]);
                    i += 2;
                }
                else
                {
                    sb.Append(s[i]);
                    i++;
                }
            }
            return sb.ToString();
        }

        private static string JsonString(string s)
        {
            var sb = new StringBuilder();
            sb.Append('"');
            foreach (char c in s ?? string.Empty)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4"));
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
            return sb.ToString();
        }

        private static string JsonUnescape(string raw)
        {
            var sb = new StringBuilder();
            for (int i = 0; i < raw.Length; i++)
            {
                if (raw[i] == '\\' && i + 1 < raw.Length)
                {
                    char n = raw[i + 1];
                    switch (n)
                    {
                        case '"': sb.Append('"'); i++; break;
                        case '\\': sb.Append('\\'); i++; break;
                        case '/': sb.Append('/'); i++; break;
                        case 'n': sb.Append('\n'); i++; break;
                        case 'r': sb.Append('\r'); i++; break;
                        case 't': sb.Append('\t'); i++; break;
                        case 'u':
                            if (i + 5 < raw.Length)
                            {
                                string hex = raw.Substring(i + 2, 4);
                                if (int.TryParse(hex, System.Globalization.NumberStyles.HexNumber, System.Globalization.CultureInfo.InvariantCulture, out int code))
                                {
                                    sb.Append((char)code);
                                    i += 5;
                                }
                                else
                                {
                                    sb.Append(raw[i]);
                                }
                            }
                            else
                            {
                                sb.Append(raw[i]);
                            }
                            break;
                        default:
                            sb.Append(raw[i]);
                            break;
                    }
                }
                else
                {
                    sb.Append(raw[i]);
                }
            }
            return sb.ToString();
        }

        private static string Truncate(string s, int max) =>
            string.IsNullOrEmpty(s) || s.Length <= max ? s : s.Substring(0, max) + "...";
    }
}
