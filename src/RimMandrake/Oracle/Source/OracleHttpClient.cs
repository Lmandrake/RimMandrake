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

            using (var cts = new CancellationTokenSource(TimeSpan.FromSeconds(timeoutSeconds)))
            {
                Exception lastError = null;
                for (int attempt = 0; attempt < 2; attempt++)
                {
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
                                if (!resp.IsSuccessStatusCode)
                                {
                                    throw new HttpRequestException(
                                        "Oracle: HTTP " + (int)resp.StatusCode + " -- " + Truncate(respBody, 300));
                                }
                                return ExtractContent(respBody);
                            }
                        }
                    }
                    catch (Exception e)
                    {
                        lastError = e;
                    }
                }
                throw lastError ?? new Exception("Oracle: request failed with no exception captured");
            }
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
            int quoteStart = responseBody.IndexOf('"', colon + 1);
            if (colon < 0 || quoteStart < 0) throw new FormatException("Oracle: malformed \"content\" value");

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
