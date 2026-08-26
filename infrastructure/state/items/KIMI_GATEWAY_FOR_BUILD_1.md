
## spec

Claude Code speaks the Anthropic Messages API (`POST /v1/messages`, header
`anthropic-version: 2023-06-01`). NVIDIA serves OpenAI shape at
`https://integrate.api.nvidia.com/v1/chat/completions`. A translating gateway is
therefore mandatory — pointing `ANTHROPIC_BASE_URL` straight at NVIDIA fails on the
first request.

LiteLLM has a first-class `nvidia_nim/` provider. Pin a clean release:
🔴 **1.82.7 and 1.82.8 shipped credential-stealing malware.** Neither may be installed.

Per-window env, set at launch (env vars are per-shell; a running window cannot be
converted):

    export ANTHROPIC_BASE_URL=http://localhost:4000
    export ANTHROPIC_AUTH_TOKEN=<gateway key>
    unset  ANTHROPIC_API_KEY            # else Claude Code falls back to Anthropic auth
    export ANTHROPIC_MODEL=nvidia_nim/moonshotai/kimi-k3

The NVIDIA key is already on the machine, mode 600, outside the repo:
`/home/mandrake/.config/secrets/nvidia.env` (`NVIDIA_API_KEY`, `nvapi-` prefix),
sourced from `~/.zshrc`. Do not copy it into the repo or into a LiteLLM config that
is committed — reference the env var.

### Measured 2026-08-25 by REP, against the live endpoint

| Reading | Result |
|---|---|
| `moonshotai/kimi-k2.6` | **404 for this account** — listed in `/v1/models`, not invocable. Every doc naming k2.6 or k2.5 is wrong for us |
| `moonshotai/kimi-k3` | **works**, and is not in any of our docs |
| Tool calling on k3 | **CONFIRMED** — `finish_reason: tool_calls`, OpenAI-shaped call, arguments parsed |
| Extra response field | `reasoning_content` — k3 is a thinking model; low `max_tokens` returns `content: None` with `finish_reason: length` |
| 20 rapid calls | **200×5, 429×15** |
| 10 calls at 2 s spacing | 200×1, 429×9 |
| 8 calls at 5 s spacing | 200×1, 429×7 |
| 3 calls after 150 s idle | 429, 429, timeout |
| `meta/llama-3.1-8b-instruct` at that same moment | **200** |

🔑 **The throttle is MODEL-scoped, not account-scoped.** The account is healthy;
`moonshotai/kimi-k3` specifically will not carry sustained traffic on the free tier.
No `retry-after` or `ratelimit-*` headers are returned, so a client cannot pace itself
from the response.

⛔ **This is why the item is not "run BUILD on Kimi".** A seat makes at least one call
per turn plus subagents; at the measured rate the window would stall on nearly every
call. **Kimi is primary with Sonnet 5 as fallback**, so a 429 degrades the turn instead
of stopping the seat.

### 🔴 Measured 2026-08-26 by REP — the nemotron family does NOT hit the kimi wall

`src/RimMandrake/Utils/nemotron_probe.py`, results `research/nemotron_probe.json`.
Same account, same key, same 20-rapid-call shape that returned **200×5 / 429×15** on
`moonshotai/kimi-k3` the night before.

| Model | tool calls | 20 rapid | competence | latency |
|---|---|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b` | ✅ args correct | **200×20** | ✅ | 1.2 s |
| `nvidia/nemotron-3-nano-30b-a3b` | ✅ args correct | **200×20** | ✅ | 1.1 s |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | ✅ args correct | **200×20** | ✅ | 8.7 s, 25 s thinking |
| `nvidia/nemotron-3-ultra-550b-a55b` | — | 200×4 / 503×1 | — | 2.5–20.7 s |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | ✅ args correct | 200×14 / **503×6** | ✅ | 2.6 s |

🔑 **Not one 429 in 80 burst calls.** Every nemotron failure was **503
`ResourceExhausted` / `Service temporarily overloaded`** — shared capacity, not a
per-model quota. ⚠️ **That distinction is the whole finding:** a 503 is transient and a
client retries out of it; kimi-k3's 429 was a wall with no `retry-after` that retrying
made worse. **A nemotron seat degrades; a kimi seat stalls.**

⇒ **The "Kimi primary, Sonnet 5 fallback" design above was shaped by the 429 wall and
should be re-decided.** `nvidia/nemotron-3-super-120b-a12b` carries sustained traffic,
calls tools with correct arguments, and answers a RimWorld def question correctly at
1.2 s. ⛔ **REP is not making that call** — it is DECIDE's, and it also needs the
`Agent_Policy.md` correction this item already flags.

⚠️ **The catalog decays and our docs will rot with it.** 83 models listed 2026-08-26
against **102** on 2026-08-25. Four nemotrons that answered 200 that night —
`nvidia-nemotron-nano-9b-v2`, `llama-3.3-nemotron-super-49b-v1` and `-v1.5`,
`nemotron-nano-12b-v2-vl` — **are no longer listed at all.** Re-run the probe before
trusting any model name here; do not pin one from a doc.

⚠️ **What this did NOT measure:** context window, long-horizon agentic behaviour, or
quality beyond one smoke question. It proves the family is *reachable and toolable*,
which is exactly what kimi-k3 failed. It does not prove a nemotron can run a seat.

## criteria

- LiteLLM running on `localhost:4000`, version pinned and recorded, **not** 1.82.7/1.82.8.
- A Claude Code window launched with the env above completes one real repo task
  end to end, with a `tool_use` block executed through the gateway and all 11 hooks firing.
- LiteLLM `fallbacks` configured so a 429 from `nvidia_nim/moonshotai/kimi-k3` retries on
  Sonnet 5 rather than failing the turn.
- `unset ANTHROPIC_BASE_URL` returns that window to normal — verified, not assumed.

## verify

    curl -s https://integrate.api.nvidia.com/v1/models \
      -H "Authorization: Bearer $NVIDIA_API_KEY" | grep -c kimi-k3     # 1
    curl -s http://localhost:4000/v1/messages -H "anthropic-version: 2023-06-01" \
      -H "Authorization: Bearer $ANTHROPIC_AUTH_TOKEN" -H 'content-type: application/json' \
      -d '{"model":"nvidia_nim/moonshotai/kimi-k3","max_tokens":64,
           "messages":[{"role":"user","content":"reply OK"}]}'          # Anthropic-shaped 200
    pip show litellm | grep -i version                                  # not 1.82.7 / 1.82.8

## Watch out

- **`ANTHROPIC_SMALL_FAST_MODEL` is a second, invisible consumer.** Claude Code uses it for
  background summarisation and titles; leave it on an Anthropic tier or every background
  call also lands in the throttled bucket.
- **A bad result will not cleanly indict Kimi.** Claude Code's system prompt, tool schemas
  and thinking surface are tuned for Claude, and k3's `reasoning_content` has no Anthropic
  equivalent. Kimi behind a translation shim may underperform Kimi native — if the trial goes
  badly we will not know which of the three we measured.
- **`infrastructure/agents/Agent_Policy.md` currently declares this out of scope** and routes
  BUILD to Sonnet 5. It must be corrected in the same act or the next seat declines this work
  as out of policy. That file is DECIDE's.
- The endpoint is NVIDIA's development/prototyping trial, not a production service. Nothing
  shipped may depend on it.
