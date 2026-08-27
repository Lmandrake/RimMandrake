
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

### 🔴 Measured 2026-08-26 by REP — context and a real agentic loop

Two things the availability probe could not reach. Harness:
`src/RimMandrake/Utils/nemotron_agent_trial.py`; results `research/nemotron_agent_*.json`.

**Context — `nvidia/nemotron-3-super-120b-a12b` retrieves at 616k prompt tokens.**
Needle-in-haystack, needle at head / middle / tail, at 12k / 185k / **616k** measured
`prompt_tokens`: **9 of 9 recovered.** ⚠️ It never errors on an over-long prompt, so
*acceptance proves nothing* — the retrieval test is the only thing that distinguishes a
long context from silent truncation. Two cells first returned 503 and both passed on the
first retry, which is the 503-is-transient finding again.

**Agentic loop — a real chain over this repo's def XML.** The model gets `grep_defs` and
`read_def_file` and must find `JawaIon_Stun`, count its stages, and compute decay hours
from `severityPerDay` (0.9 ÷ 1.2 = 0.75 day = **18 h**). Ground truth is
`src/Jawa/JawaIonWeapons/Defs/HediffDefs_JawaIonStun.xml`.

| Model | turns | wall | result |
|---|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b` | 5 | 26 s | ✅ `JawaIon_Stun \| 4 \| 18`, format exact |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 4 | 33 s | ✅ correct |
| `nvidia/nemotron-3-ultra-550b-a55b` | 4 | 22 s | ✅ correct (one 500, retried) |
| `nvidia/nemotron-3-nano-30b-a3b` | **10 (cap)** | 30 s | ⛔ **never answered** |

🔑 **The discriminator is error RECOVERY, not tool-call syntax.** All four emit valid
OpenAI-shaped calls with correct arguments — that is why `nemotron_probe.py` passed all
four. nano-30b then dropped the `src/` prefix on turn 3 (`Jawa/JawaIonWeapons/…`), got a
plain `(no such file: …)`, and **thrashed on `grep_defs` for seven turns — repeating one
pattern verbatim — without ever retrying the read**, though its own turn-2 grep output
held the correct full path. ⚠️ **A one-call probe cannot see this failure class.** Any
model considered for a seat must be run through a multi-turn loop with a deliberate bad
argument in it.

⇒ **`nvidia/nemotron-3-super-120b-a12b` is the candidate**: 20/20 sustained, 616k
retrieval, tools chained over four turns, correct arithmetic, ~1.2 s first token.
⛔ **Still not REP's call to make** — see the `Agent_Policy.md` correction above.

⚠️ **What remains unmeasured:** behaviour under Claude Code's actual system prompt and
11-hook surface, `reasoning_content` with no Anthropic equivalent, and anything
long-horizon. A 5-turn success is not a session.

### 🔴 Measured 2026-08-26 by REP — THE GATEWAY IS BUILT AND A CLAUDE CODE WINDOW RAN ON IT

The thing every previous pass called unmeasured. LiteLLM **1.98.0** in a venv at
`/home/mandrake/.local/venvs/litellm` (system pip refuses under PEP 668 — the venv is
not optional). Config, runnable and committed:
`src/RimMandrake/Utils/litellm_nemotron.yaml`.

    set -a; source ~/.config/secrets/nvidia.env; set +a
    export NVIDIA_NIM_API_KEY="$NVIDIA_API_KEY"
    /home/mandrake/.local/venvs/litellm/bin/litellm \
        --config src/RimMandrake/Utils/litellm_nemotron.yaml --port 4000

**The Anthropic surface works, including the two things expected to break it.**
`/v1/messages` returns Anthropic-shaped JSON; `reasoning_content` arrives as a
`{"type":"thinking"}` block; a tool returns a real `tool_use` block with
`stop_reason: "tool_use"`. ⚠️ The thinking block carries **`"signature": null`** — it
did not break these runs, but nothing has yet exercised a long thinking-block echo.

**A headless Claude Code window completed real repo tasks through it**, inside this
repo, with the session hooks live (the `SessionStart` seat-identity injection fires and
the model still functions):

| task | result |
|---|---|
| 2 files + read `b.txt` (scratch dir) | ✅ correct |
| count FactionDef files + read `Jawa_HuttCartel` `leaderTitle` | ✅ `8 Lord` — both correct |

⚠️ **Claude Code does not recognise the model name** and warns it will assume a 200k
window: `[claude-code:unrecognized_model]`. Pass **`CLAUDE_CODE_MAX_CONTEXT_TOKENS=600000`**
(REP measured 616k retrieval on this model) or the 616k finding is thrown away by the
client, not the server. ⚠️ Also set `ANTHROPIC_API_KEY=` explicitly; without it the
claude.ai OAuth login takes precedence and the window never reaches the gateway.

**Quality tell, minor but real:** asked what `b.txt` contained, the model reported
``1\tbeta`` — it copied the **Read tool's line-number prefix** into the answer as file
content. Correct enough to pass, wrong enough to notice.

🔴 **ONE CRITERION BELOW IS NOT BUILDABLE ON THIS MACHINE, and it is not a to-do.**
"LiteLLM `fallbacks` configured so a 429 retries on **Sonnet 5**" requires an
`ANTHROPIC_API_KEY`. There is none — `~/.config/secrets/` holds `nvidia.env` and nothing
else, and this machine's Claude auth is the **claude.ai OAuth login, which LiteLLM
cannot proxy**. ⇒ The fallback is configured **within the NVIDIA family**
(`nemotron` → `nemotron-lightning`), which is what the *measured* failure mode — 503
shared-capacity, transient — actually needs; Kimi's 429 quota wall left with Kimi.
**Proven, not assumed:** a `nemotron-faultinject` entry pointing at a nonexistent model
answered anyway, and the response's `model` field read
`nvidia_nim/nvidia/nemotron-3.5-lightning-30b-a3b`.

✅ **`unset ANTHROPIC_BASE_URL` returns the window to normal — verified, not assumed.**
A window with the three vars unset answered as `claude-opus-5[1m]`.

### 🔴 Measured 2026-08-26 by REP — LONG-HORIZON, through Claude Code itself

The synthetic 5-turn loop could not answer this; the gateway makes the real test
possible. Task: a five-part chain — grep for a defName, read a **120 KB** file, count
four defs inside it, sum their `combatPower`, cross to a **different mod** for a hediff
decay, then divide. Ground truth
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml | 4 | 546 | 18 | 30.3`.
Run through a real headless Claude Code window, in this repo, hooks live.

| model | turns | wall | score | result |
|---|---|---|---|---|
| `nemotron-3-super-120b-a12b` | 16 | **90 s** | **5/5** | format exact, 656k cumulative input tokens |
| `nemotron-3.5-lightning-30b-a3b` | 8 | 205 s | **5/5** | correct, showed its arithmetic |
| `nemotron-3-nano-30b-a3b` | 10 | 64 s | ⛔ **0/5** | see below |

🔑 **nano-30b failed in a DIFFERENT way than the synthetic loop, and the new failure is
the more dangerous one.** In the bare loop it thrashed on one grep. Here, after ten turns
of real tool use, it **lost the prompt entirely** and replied *"I need to see the actual
questions you'd like answered. Could you please provide the list of questions?"* —
`is_error: false`, exit 0, a fluent and completely empty answer. ⚠️ **Under Claude Code's
full system prompt the small model's instruction retention collapses**, and it collapses
into a *polite request*, not an error. Nothing downstream would flag that as a failure.

⇒ **super-120b is the pick and lightning-30b is the viable second.** Fewer turns is not
better: lightning used half the turns and **2.3× the wall clock**.

⚠️ **Still unmeasured:** anything genuinely long-horizon (this is 16 turns, not a
session), a long `thinking`-block echo against the `"signature": null` above, writes and
edits (both runs were `--disallowedTools Write,Edit,NotebookEdit` deliberately), and
behaviour when a hook REFUSES a call — none of these runs tripped one.

⚠️ **The criteria below say "all 11 hooks". There are 14** (`.claude/settings.json`,
counted 2026-08-26). Do not re-derive the number from that line.

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
