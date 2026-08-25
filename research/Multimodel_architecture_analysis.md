# Multi-model architecture: what this project should actually route elsewhere

**REP, 2026-08-24.** Answering `research/KIMI_K2_6_WORKFORCE_EXPANSION.md`.

Every number below is marked **CONFIRMED** (a command was run, here, today) or **UNCERTAIN**.
Where a number decides something expensive and nobody has measured it, it says **UNMEASURED**
and names the ten-minute experiment that would settle it. That distinction is the house style
and it is load-bearing in what follows.

---

## The four answers, before the argument

1. **Could an alternative environment run all four seats?** Yes — and it is not an alternative
   environment. Claude Code reads `ANTHROPIC_BASE_URL`; a LiteLLM gateway has a first-class
   NVIDIA NIM provider. Two environment variables per window and every hook, skill, script,
   queue and bridge call stays exactly where it is. **Perpetually is the word that fails**, not
   *possible* — the free tier is reported at 40 RPM shared account-wide, and whether a finite
   credit pool binds underneath that is UNMEASURED.

2. **Would the results be substantially worse?** In the places we lose, yes — and benchmarks do
   not measure those places. This project's characteristic failure is not "cannot write the
   patch." It is **a plausible answer arriving and someone having to decide whether to believe
   it.** Our own memory is a catalogue of instruments that returned confident wrong numbers.
   That is calibration, not code generation, and SWE-bench Verified says nothing about it.

3. **What can be unburdened?** More than the source document assumes, because our work-packet
   discipline already exists: **29 of 36 open items already carry both `## verify` and
   `## criteria`** (384 of 411 across all history). CONFIRMED. That was listed as the hard
   prerequisite; it is done.

4. **Cheaper Anthropic models with zero infrastructure change?** The mechanism exists, is
   documented in our own skill, and **has never once been used**: the `model` parameter on the
   Agent tool. And the under-considered option in the entire source document is **Sonnet 5,
   which keeps the full 1M context** — every context-based objection to Kimi evaporates for it,
   at no endpoint risk and inside the subscription.

**On art, the premise needs correcting before it can be answered: GPT already draws our pixels.**
The binding constraint is not the model, it is that Codex runs on ChatGPT auth so there is no
`OPENAI_API_KEY`. A whole-mod reskin is now affordable — ~$46 at GPT Image 2 medium, or ~28
minutes free on NVIDIA — and **our own doctrine says do not do it**, for reasons that have
nothing to do with cost.

---

## Part 0 — The ground truth this rests on

Measured today, by four parallel censuses. All CONFIRMED unless marked.

### The queue

| | |
|---|---|
| Items in the ledger | 437 (411 with prose files, 26 spawns) |
| **Open** | **36** — proposed 22 · ready 8 · doing 6 · blocked 0 |
| Closed | 329 done · 50 dropped · 22 superseded |
| Median lifetime of a closed item | **2.89 h** (n=329; mean 10.6 h, max 75.4 h) |
| Ledger | 2,088 events over 3.9 days, ~535/day |
| Events by seat | BUILD 635 · CHECK 618 · DECIDE 541 · OWNER 211 · REP 83 |
| Verification outcomes | pass 81 · **partial 66** · fail 12 |

**41% of verifications land "partial"** — the offline half proved and the live half owed. That
single number is the shape of this project: work is routinely half-decidable without the game.

### The 36 open items, classified by what the work *is*

| Class | n | Examples |
|---|---|---|
| **(e) Tooling / infra maintenance** | **12** | `BRIDGE_ARG_SHAPES_INCONSISTENT_1`, the three `BRIDGE_TOOLS_*_BLOCK_1`, `PAWNKIND_AUDIT_TAGLESS_BLIND_1` |
| **(b) Investigation / measurement** | **11** | `LIVE_HALF_OF_LOAD_1`, `ROLE_KINDS_ARMED_5_OF_5_1`, `XENOTYPE_NONFACTION_SPAWN_ROUTES_1` |
| **(a) Bounded mechanical, testable** | **7** | `AUTHORED_KINDS_MUST_FIELD_1`, `EMPIRE_BLACKSTAR_ALWAYS_WILLING_1`, `ANCIENT_SCATTERBOW_TAG_SEVER_1` |
| **(c) Judgment / design call** | **3** | `THOROUGH_RETAG_WEAPONS_ARMOUR_1`, `TRIM_VALIDATION_LAYERS_1`, `dll-capability-roster-and-cull-a41c02` |
| **(f) Documentation alignment** | **2** | `BUILDABLE_ENTRY_NUMBERS_COLLIDE_1`, `WORLDGEN_CITATIONS_REPOINT_CHECK_1` |
| **(d) Art / visual review** | **1** | `BIOME_FLORA_LOOKS_RIGHT_1` |

**By `needs`: bridge 18 · offline 10 · deploy 4 · game-up 2 · harvest 1 · owner 1.**
By seat: BUILD 20 · CHECK 12 · REP 4 · **DECIDE 0**.

Two things fall straight out of that table:

- **Only 3 of 36 open items are pure judgment.** 32 are bounded, verifiable, or mechanical.
- **18 of 36 need a live bridge.** That constrains *where* work can run — this machine, game up
  — far more than it constrains *which model* runs it. Half our queue is pinned to a locality,
  not to an intelligence tier.

### The artifacts we actually work on

| Artifact | Size |
|---|---|
| `defs.sqlite` | **782 MB** |
| One def-dump capture | **658 MB** across 534 files |
| — `ThingDef.json` alone | **332 MB** |
| Archived `Player.log` | **155 MB** |
| Live `Player.log` | 725 KB |
| `ASHKARR_VIVIFIED_2026-08-24_tiles.csv` | 2.5 MB / 21,873 lines |
| `infrastructure/state/items/` (411 files) | 2.3 MB |
| `EXPECTED_FAILURES_next_load.md` | 145 KB / 2,133 lines |
| `canon.yml` | 64 KB |
| `BUILDABLE.md` | 49 KB |

### What a session loads before doing anything

| | Bytes | ~Tokens |
|---|---|---|
| Global + project `CLAUDE.md` | 30,373 | 7,594 |
| `MEMORY.md` index | 6,406 | 1,602 |
| Seat file (avg; REP worst at 14,242 B) | 11,581 | 2,895 |
| 25 project skill descriptions | 18,174 | 4,543 |
| **Eager subtotal** | **66,534** | **~16,600** |
| `POLICY.md` (read on turn 1 by instruction) | 35,857 | 8,964 |
| **With POLICY.md** | **102,391** | **~25,600** |

### The portability surface

| | |
|---|---|
| Hooks | 11 scripts, 13 registration points, **2,333 active lines** (+1,228 selftest) |
| — pure tool-call interception (portable as-is) | **6 of 11** |
| — text-lifecycle (`Stop`, `UserPromptSubmit`) | 2 |
| — genuinely Claude-Code-bound | 3 |
| Skills | 25 in-repo, 7,139 lines, 380,677 bytes |
| — fully portable prose | **20 of 25** |
| — SKILL.md mentioning "Claude Code", ".claude/", "Read tool" | **zero** |
| Harness-agnostic Python/shell | **239 files, 80,932 lines** |
| — genuinely harness-bound scripts | **4** (`statusline.py`, `broadcast.py`, cli seat-autodetect, `set_agent_window.sh`) |
| MCP | one server, `rimsage`, hosted streamable HTTP — any MCP client attaches |
| RimBridge | not MCP. Raw TCP GABP inside the game. Harness-independent. |

**This is a far more portable system than it looks from inside it.** The intelligence is in
80,932 lines of Python, 7,139 lines of prose that never names its host, and an append-only
ledger. Claude Code supplies a text loop and 2,333 lines of guardrail.

---

## Part 1 — Could an alternative environment run all four seats perpetually?

### The finding: it is not an alternative environment

The source document's Risk #6 says *"Kimi is an API model, not Claude Code… a poor harness can
make a strong model appear weak."* That risk is largely dissolved, because **Claude Code will
talk to a non-Anthropic model without any of our infrastructure moving.**

```
export ANTHROPIC_BASE_URL=http://localhost:4000     # LiteLLM gateway
export ANTHROPIC_AUTH_TOKEN=<gateway key>           # NOT ANTHROPIC_API_KEY
unset  ANTHROPIC_API_KEY                            # or CC falls back to Anthropic auth
export ANTHROPIC_MODEL=nvidia_nim/moonshotai/kimi-k2.6
export ANTHROPIC_SMALL_FAST_MODEL=<something cheap> # background summarisation/titles
```

LiteLLM ships a first-class `nvidia_nim/` provider pointed at
`https://integrate.api.nvidia.com/v1/`. Claude Code hardcodes three model names internally —
`opus`, `sonnet`, `haiku` — and `ANTHROPIC_MODEL` / `ANTHROPIC_SMALL_FAST_MODEL` remap them.

**What does not move:** all 11 hooks (they run around tool calls, indifferent to which endpoint
served the completion) · all 25 skills · rimflow and its ledger · `rimbridge_client.py` and the
game · `deploy_custom_mods.py` · the board and its 60-second publisher · seat identity injection
· the 36 open items · every queue file.

**Environment variables are per-shell, and our seats are already per-window.** So the natural
configuration is not "switch the project to Kimi" — it is a **mixed fleet**:

```
AGENT DECIDE   →  Opus 5           (judgment, propagation, the world)
AGENT CHECK    →  Opus 5           (deciding whether an instrument lied)
AGENT BUILD    →  Kimi via gateway (bounded items with verify + criteria)
AGENT REP      →  Sonnet 5         (state aggregation; escalate to the owner in prose)
```

Four windows, one repo, one ledger, four different providers, zero code changes. The fallback is
`unset ANTHROPIC_BASE_URL` — the graceful degradation the source document asks for is structural,
not something we have to build.

### The ceiling: 40 RPM, and it is the wrong shape for us

The free tier is widely reported at **40 requests per minute, applied at the account level** —
shared across models, not per-model per-window. One NVIDIA forum poster (May 2026) reports it
*"runs out in 2–3 minutes during interactive sessions."*

⚠️ **UNCERTAIN.** I could not find an NVIDIA staff statement confirming the figure, its scope, or
the credit model. The forum thread the source document cites contains **no staff reply** — only
users repeating 40 RPM at each other. Secondary sources contradict each other on credits: some
say 1,000 initial rising to 5,000 on request, others say the credit model was withdrawn in favour
of pure rate limiting. **UNMEASURED, and it is the fact that decides the whole question.**

Take 40 RPM as a working assumption and it lands badly on *our* shape specifically:

- Our doctrine is **fan-out**. `agent-fanout-research` calls four concurrent agents the canonical
  form; `efficient-subagents` budgets **4–6 in flight**. This document was produced by four.
- Four seats each running a tool loop, each with 4–6 subagents, all drawing on **one** 40 RPM
  bucket. A single seat mid-sweep can consume the fleet's entire allowance.

So, honestly:

| Configuration | Verdict |
|---|---|
| Four seats at full tilt, fanning out | **Will not sustain.** 429s inside minutes |
| Four seats throttled (~10 RPM each, queue + backoff) | Plausible, at perhaps a third of current pace |
| One or two seats on Kimi, the rest on Claude | **Comfortable, and the right first experiment** |

**It is not a perpetual-motion machine. It is a second, slower lane** — and one whose terms
NVIDIA can change, since it is explicitly a development/prototyping trial and not a production
service.

### Two risks worth stating plainly

🔴 **LiteLLM 1.82.7 and 1.82.8 shipped credential-stealing malware.** Anthropic's own guidance
says to avoid those versions and rotate credentials if installed. Pin a known-clean release. This
is a real supply-chain hazard on a machine that holds the owner's game, repo and tokens — not a
footnote.

⚠️ **A bad result would not cleanly indict the model.** Claude Code's system prompt, tool schemas
and thinking surface are tuned for Claude. Kimi behind a translation shim may underperform Kimi
native. If we run the experiment and it goes badly, we will not know which of the three we
measured. Worth knowing before we conclude anything from it.

---

## Part 2 — Would the results be substantially worse?

### Reframe: our failures are not coding failures

The source document leads with 80.2% SWE-bench Verified and 66.7% Terminal-Bench, then correctly
warns not to decide from them. It is worth saying *why* they are near-useless here.

SWE-bench grades against a hidden test that passes or fails. **In this project the tests
themselves lie.** Our institutional memory — 43 memory files, `BUILDABLE.md`, the seat rules — is
almost entirely a register of that one failure mode:

- Seven instruments returned confident wrong counts in a single session.
- ~40 bridge calls **report success and change nothing**.
- `PatchOperationConditional` and `PatchOperationFindMod` **both return true on no match** — a
  patch that matches nothing logs nothing.
- An `<li>` in a `LoadDataFromXmlCustom` field discards the **whole def**, silently. It cost 26
  biomes.
- `strings -a -el` on an assembly found **16 of 115** tool names and reported it as a clean answer.
- Cherry Picker's cuts are invisible to the def dump; presence proves nothing.
- Generators lie in their own headers.
- The game-state probe reported ignorance as "silent".
- This seat reported "the bridge is down" **four times** to a socket probe that could never have
  worked from WSL — while its own tool was printing the correct diagnosis on every run.

Every one is the same shape: **a plausible answer arrived, and the job was to disbelieve it.**
That is calibration and skepticism. It is the least benchmarked capability in the industry and
the single most load-bearing one here.

### So: where it will and will not be worse

**Likely fine on Kimi** — because failure is detectable and cheap:

- The **7 bounded-mechanical** items. They have acceptance criteria; the compiler, `validate_patch.py`
  and the selftests are the judge.
- Most of the **12 tooling/infra** items. Loud failure, local context, existing selftests.
- The **2 documentation-alignment** items. Verifiable by grep.
- The mechanical half of the **11 investigations** — running the measurement, collating the rows.

**Likely worse, and asymmetrically expensive:**

- **The moment a tool returns a number and someone must decide whether it is real.** That is
  CHECK's entire job and roughly half of BUILD's. A miscalibrated worker here does not produce a
  failed build; it produces **confident wrong project state** that lands in `facts/`, `canon.yml`,
  `BUILDABLE.md` and `EXPECTED_FAILURES_next_load.md`, and is then cited by items that outlive it.
- **Live bridge writes.** 18 of 36 open items need the bridge; ~40 calls silently no-op; the
  target is a hand-authored, frozen world with no regenerate behind it. High cost of error, weak
  detection — the exact quadrant where you do not economise.
- **Propagation after a ruling.** `deciding-and-superseding` is explicit that a decision which has
  not been propagated has not been made. Doing it means knowing which of 411 items and ~119 design
  docs now contradict the new ruling. This is the one place where breadth of context genuinely is
  the capability.

**The correction tax is worse here than in ordinary software** because our median item closes in
**2.89 hours** into a durable record. A bad close is not a bad pull request you revert. It is a
wrong fact with a citation graph.

### The context argument in the source document is largely wrong for us

The document treats 1M vs 256K as *"architecturally important"* and builds much of its caution on
it. Our measurements say otherwise.

**The artifacts that matter fit in neither window.** `ThingDef.json` is 332 MB. A dump capture is
658 MB. `defs.sqlite` is 782 MB. An archived `Player.log` is 155 MB. These exceed 1M tokens by
two orders of magnitude. **We never read them — we measure them**, which is precisely why
`measuring-large-artifacts` exists and why `block_blind_scan.py` refuses the naive grep.

What actually rides in context is **prose**, and prose here is small: the entire `items/` tree is
2.3 MB; the largest single doc is 145 KB; `canon.yml` is 64 KB. Our whole session preamble is
**~16,600 tokens eager, ~25,600 with POLICY.md** — that is **6.5% to 10% of a 256K window**.

⇒ **Context size is a session-length constraint, not a task constraint.** A 256K window means
more frequent compaction and shorter unbroken working stretches. Annoying; not disqualifying.

And the corollary that the source document never reaches: **Sonnet 5 has the full 1M window.** If
the worry is "the auxiliary worker cannot see enough", Sonnet 5 dominates Kimi on that axis — at
no endpoint risk, no harness risk, no supply-chain risk, and inside the subscription.

---

## Part 3 — What to unburden, and what genuinely needs Opus

### Unburden, in descending order of ratio

| # | Work | Route to | Why it is safe |
|---|---|---|---|
| 1 | **Fan-out subagents** — censuses, sweeps, existence checks, file inventories | **Haiku 4.5** | Already bounded to 1–2k tokens by our own skill, already disposable, already non-authoritative. Zero new files |
| 2 | **The 12 tooling/infra items** | Kimi or Sonnet | Selftests and compiler feedback; failure is loud and local |
| 3 | **The 7 bounded-mechanical items** | Kimi or Sonnet | All carry `## verify` + `## criteria` |
| 4 | **Documentation alignment (2)** | Haiku/Sonnet | Verifiable by grep |
| 5 | **Context preprocessing** (the doc's Option F) | Kimi | Turning a 658 MB capture into a 20 KB subsystem map is exactly what `measure` already does; the model only drives it |
| 6 | **Contact-sheet / review-sheet assembly** | Haiku | The assembly is Python. The model wires arguments |
| 7 | **REP-INTERNAL** — queue state, staleness detection, digest assembly | Sonnet | The board is already 100% instrument-derived and self-reports nothing |

### Keep on Opus

| Work | Why |
|---|---|
| **Deciding whether an instrument told the truth** | CHECK's core. `BUILDABLE.md` exists because instruments lie with a clean number |
| **DECIDE's rulings and their propagation** | Requires holding 411 items and ~119 docs in mind well enough to know what now contradicts the ruling |
| **The world** | *"ONE MAP, NOT A GENERATOR"* · *"iterate by LOOKING"* · realism first. Aesthetic judgment against a photograph |
| **Live bridge writes** | High cost of error, weak detection, frozen target |
| **Talking to the owner** | REP-HUMAN. A mediocre interface costs more human attention than it saves |

### Where I disagree with the source document

- **Option 3 (Kimi as CHECK) is its most attractive-looking idea and its most dangerous one
  here.** Model diversity as a V&V asset is a real effect — but CHECK's actual work is not
  "re-review BUILD's diff." It is adjudicating whether a *measurement* is trustworthy, on a
  register of instruments known to lie. Put the least calibrated worker there and the failure is
  silent, durable and cited. **Invert it: Kimi as ADVERSARY (Option D) feeding CHECK, not
  replacing it.** An adversary that produces a bad counterexample wastes a check; a checker that
  produces a bad pass writes a wrong fact.

- **Option 1 (Kimi shadowing DECIDE) is better than the document's own hedging suggests** —
  because DECIDE currently has **0 open items**. The seat is not capacity-bound. Exploration and
  option-generation ahead of adjudication costs nothing there and could not corrupt state, since
  the adjudication stays with Opus.

- **The work-packet prerequisite is already met.** The document treats it as the hard part
  (*"a successful Kimi strategy may depend heavily on improving our ability to construct small,
  explicit, self-contained work packets"*). **29 of 36 open items already carry both `## verify`
  and `## criteria`; 384 of 411 across all history.** The schema it proposes is very nearly our
  item format already. That is a green light it did not know it had.

---

## Part 4 — Cheaper Anthropic models, with zero infrastructure change

### The mechanism exists and has never been used

**CONFIRMED:** there is no `.claude/agents/` in this repo or in `~/.claude/`. No settings file
anywhere contains a `model` key. The **only** model-selection line in the entire repository is
`skills/efficient-subagents/SKILL.md:52`:

> `- **Cheap model for cheap work.** model: haiku for greps, censuses, existence checks.`

It has never been executed. Every subagent this project has ever spawned inherited the parent's
model — which means **every census, every file sweep, every existence check in this project's
history ran on Opus.**

The fix requires no file, no setting, no restart: the Agent tool takes a `model` parameter.
`model: "haiku"` on the call. That is the whole change.

### The tiers

Cached from the bundled `claude-api` skill's model table (**2026-06-24**; the live check is the
Models API):

| | Context | Input $/MTok | Output $/MTok | vs Opus 5 |
|---|---|---|---|---|
| **Opus 5** | 1M | 5.00 | 25.00 | 1× |
| **Sonnet 5** | **1M** | 2.00 | 10.00 | **2.5× cheaper** |
| **Haiku 4.5** | 200K | 1.00 | 5.00 | **5× cheaper** |

⚠️ **We are on Max, so dollars are a proxy, not the currency.** How Claude Code weights
*subscription* consumption per model is **UNMEASURED by me** — I am using API list prices as a
ratio and saying so rather than quoting a saving I have not measured.

**The headline is not the price. It is that Sonnet 5 keeps the full 1M window.** Sonnet 5 is a
strictly better-understood option than Kimi on the axis the source document cares most about,
and it needed no document to unlock.

### What to do today, in order

1. **Every fan-out/census subagent → `haiku`.** The four that produced this document would have
   been fine on Sonnet; two of them on Haiku. Do it on the next census. No files change.
2. **Run BUILD's seat on Sonnet 5** for the 7 bounded-mechanical and 12 tooling items — `/model`
   is per-window and reversible in one keystroke. This is the single largest allocation saving
   available with no risk of endpoint loss, no gateway, and no new dependency.
3. **Keep DECIDE and CHECK on Opus.** Both are judgment seats and both write durable truth.
4. ⚠️ **Do not run a seat on Haiku.** 200K is easy to overrun in a long working session — it is a
   subagent tier here, not a seat tier.

**This is strictly better than the Kimi route as a first move**: same-day, no gateway, no
supply-chain exposure, no free-trial dependency, and it is reversible mid-sentence. If the goal is
to stop burning Opus on greps, this achieves most of it before NVIDIA is involved at all.

---

## Part 5 — Art: GPT + NVIDIA, and whether a whole-mod reskin is on

### Correcting the premise: GPT already draws our pixels

`skills/generating-images/scripts/codex_image.py` shells out to the Codex CLI
(`codex-cli 0.147.0-alpha.6.6`, a Windows binary invoked from WSL) and asks it in prose to use its
built-in `$imagegen`. The underlying model is **`gpt-image-2`**. CONFIRMED from source.

So "could GPT handle the art regeneration" is already answered: **it is what we run.** The
question is about scale and access, not about model choice.

### The binding constraint is authentication, not intelligence

Codex is on `auth_mode: chatgpt`, so there is **no `OPENAI_API_KEY`**. That one fact costs us,
CONFIRMED from the skill sources:

| Lost | Consequence today |
|---|---|
| Native transparency (`background=transparent`, `output_format=png`) | The entire chroma-key workflow — generate on a flat key, cut with `chroma_key.py`, despill, self-validate |
| Exact `--size` | `gpt-image-2` demands both edges multiple-of-16 and 655k–8.3M px; every RimWorld sprite fails one end, so we generate at a legal *aspect* and downscale premultiplied |
| `--mask`, `--quality` | No inpainting, no quality dial |
| Batch | **One foreground call at a time, 79–93 s each.** Reliable 8-of-9 foreground; fails when batched or backgrounded |

⭐ **The highest-leverage art change available is an OpenAI API key.** It deletes a script and an
entire failure class, and removes the serial 90-second wall. Nothing about Kimi or NVIDIA is
required to get it.

Current per-image list, for sizing (secondary sources; treat as order-of-magnitude):
GPT Image 2 ≈ $0.005 / $0.041 / $0.165 at low/medium/high · GPT Image 1.5 ≈ $0.04.
⚠️ gpt-image-1 shuts down 2026-10-23 and GPT Image 1.5 on 2026-12-01 — **GPT Image 2 is the
migration target**, and anything we build should name it.

### NVIDIA's real contribution to art is specific: FLUX.1 Kontext

build.nvidia.com serves **FLUX.1 Kontext** (`flux.1-kontext-dev`), plus FLUX.2-klein and
Qwen-Image, on OpenAI-compatible endpoints. Kontext is not a text-to-image model — it is an
**instruction-based editing** model built for *object and character consistency across edits*, at
roughly **3–5 s per 1024²**.

That is exactly our primitive. Our problem is never "invent a creature." It is **"make this donor
sprite read as ours without moving the silhouette."** Our own
`src/Jawa/DesertVehicleReskin/Source/recolour_ronto.py` chose a pure HSV delta explicitly because
*"a recolour cannot move a single pixel of silhouette… a regeneration can, and costs a
generation."* Kontext sits precisely between those two poles: more than a recolour, anchored far
harder than a regeneration.

**It deserves a bake-off. It does not deserve a rollout.**

### The scale question, answered — then the reason not to

**1,123 PNGs under `src/`** (1,082 git-tracked). CONFIRMED. But the composition matters:

| | n | What it is |
|---|---|---|
| `RimMandrake_StarWarsRaces` | **876** | **Copied from donor mods** (Star Wars Xenotypes, Outer Rim, BTD REMIX). Regenerating these is redrawing three other creators' work, not reskinning ours |
| `DesertVehicleReskin` | 80 | 30 shipped + 50 source |
| `Jawa_Patches` | 56 | Eopie 21, Bantha 12, Atispec 3, ForsakenDragon 3, 13 faction world icons, 4 misc |
| `mapsynth` · `WreckedMachines` · `KotORBandolierNorthFix` · `art_bench` · 8 fix mods | ~111 | |
| **Actually generated by this pipeline** | **~72** | 12 smelter facings · 30 vehicle textures · 6 Atispec/Behemoth · 24 Bantha/Eopie |

A full 1,123-sprite pass:

| Route | Cost | Wall clock |
|---|---|---|
| GPT Image 2, medium | ~**$46** | batched, hours |
| GPT Image 2, high | ~**$185** | batched, hours |
| FLUX.1 Kontext, NVIDIA free tier | **$0** (if credits permit — UNMEASURED) | ~**28 min** at 40 RPM |
| **Our route today** | $0 | **~28 h serial**, and at ~2 generations per shipped facing, nearer **56 h** |

⇒ **Yes. A whole-mod reskin at scale is now affordable. It was not, a week ago.** That is a real
change and it should be on the record.

### And the project's own doctrine says do not

- `design/Jawa/art/graphics_overhaul_protocol.md` opens: **"Exhaust the def layer before you draw
  a single pixel."** Measured against the live DefDump, **944 of 945** buildable defs accept a
  `<color>` tint with no new art at all.
- The **621-creature art census** — built as a review sheet, **reviewed in full by the owner**,
  frozen 2026-08-23 — returned **588 keep · 21 shrink · 10 replace · 2 redraw**. **21 of the 33
  actions are a def number, not a pixel.** Real new-art demand from the entire cast: **2 redraws**,
  extended by voice to 4.
- A standing **art freeze** is in force: nothing is redrawn until the owner has personally
  verified the art is broken.

⚠️ **A correction while I am here.** Our own recent notes carry *"creature-art pipeline 36/621
reviewed"*. **That is wrong.** 36 was the auto-flag pre-pass — percentile thresholds on
px/contrast/saturation/fill deciding *where he looks first*, and labelled "invented" in its own
header. **He reviewed all 621.** The record is `design/Jawa/fauna/creature_art_decisions.json`,
`frozen: true`, `frozenBy: owner`, `frozenOn: 2026-08-23`.

### The deeper reason cheap generation does not buy a reskin

**The human decision points do not scale, and they are structural, not habitual.** From the skills'
own text:

1. **Does it honour the thing?** The Atispec scored 2,850 px / contrast 0.30 and was pre-filled
   `keep`. The owner overruled it to `redraw` because the creature was worth honouring. *No metric
   in the sheet can see that, which is exactly why he looked.*
2. **Does it read at display size?** The validator measures at source resolution. A soft muzzle
   that collapses into a hard wall at 104 px passed every offline check.
3. **Is the distortion regional?** The validator grades the whole sprite. A **+34.6% width stretch
   inside a vehicle band returned PASS.**
4. **Does it match the donor mod's style?** A style mismatch is more obvious in game than missing
   detail is.
5. **Does it survive the in-game render?** `Graphic_Multi`'s bare-path fallback makes a
   mis-deployed `_south` look fine; `<color>` tints the sprite; a pawnkind rolls its own hair and
   apparel, so the look passes or fails at random.
6. **Is it authorised?** The owner names which assets may be touched.

Generating 1,123 sprites for $46 produces **1,123 sprites nobody has looked at**, in a project
whose art doctrine is *"iterate by LOOKING."* The generator was never the bottleneck. The eye is.

What *is* mechanical, and already is: canvas, alpha presence, fringe, opaque corners, span,
aspect, origin, coverage, fragments, byte-identity, inter-iteration drift — all enforced by
`skills/generating-rimworld-sprites/scripts/validate_sprite.py` (425 lines, 9/9 selftests, every
constant carrying the measurement that set it). Plus decision **prefill**: the review sheets
pre-fill `keep` so the human only records disagreement — **588 of 621 rows were the prefill
standing.** That is the pattern that actually scales human review, and we already have it.

### Recommendation on art

**Not a whole-mod reskin. A whole-mod reskin *capability*, proven on a bounded set.**

1. Get an `OPENAI_API_KEY`. It is the single highest-leverage change and it is independent of
   everything else in this document.
2. Bake off **GPT Image 2** against **FLUX.1 Kontext** on the **30 `DesertVehicleReskin` sprites**
   — the one set where we already have hand-made ground truth to grade against.
3. Grade with `validate_sprite.py`. It already exists, it is calibrated, and its 6% span tolerance
   is exactly the "did the silhouette move" question.
4. If a machine can hold silhouette within that tolerance across 30 sprites unattended, then
   whether to reskin at scale becomes a **design** question for DECIDE and the owner, not a
   technical one. Until then it is not on the table, and cost was never what kept it off.

---

## Part 6 — Risks, and what would make me wrong

| Risk | Status |
|---|---|
| **40 RPM and the credit pool** | Secondary sources only; the forum thread cited by the source document contains **no NVIDIA staff reply**. Sources disagree on whether credits still bind. **UNMEASURED — and it decides "perpetual"** |
| **LiteLLM supply chain** | 1.82.7 / 1.82.8 shipped credential-stealing malware. Pin a clean release; rotate if ever installed. Real hazard on this machine |
| **Attribution of a bad result** | Claude Code's prompts and tool schemas are Claude-tuned. Kimi behind a shim may underperform Kimi native. A poor outcome would not cleanly indict the model |
| **Prompt caching across a gateway** | Unlikely to behave like first-party caching. Our sessions carry heavy stable prefixes (~16.6k tokens eager). On a free endpoint that costs latency, not money — but it costs it every turn |
| **Subscription weighting per model** | I have used API list prices as a ratio. How Max consumption is weighted per model is **UNMEASURED by me** |
| **Endpoint continuity** | An explicit development/prototyping trial. Nothing durable should depend on it. The `unset ANTHROPIC_BASE_URL` fallback makes that structural |
| **Art cost figures** | Per-image dollar figures are calculator estimates from secondary sources, not OpenAI list prices. Order-of-magnitude only |

**What would change my mind:** if the endpoint measurement shows sustained throughput well above
40 RPM with no credit ceiling, the "second slower lane" framing is too pessimistic and a fuller
migration of BUILD becomes attractive. If it shows a hard credit wall at ~1,000–5,000 requests,
Kimi is a spike tool for one-off sweeps and nothing more — and **the Sonnet 5 route in Part 4 is
the entire answer.**

---

## Part 7 — Recommended sequence

Cheapest decisive experiment first. Each settles a question the next depends on.

| # | Action | Cost | Settles |
|---|---|---|---|
| **1** | **Switch fan-out subagents to `haiku`/`sonnet`.** The Agent tool's `model` param, on the next census | **0 min, 0 files** | Nothing — it is simply free money we have been leaving on the table since the skill was written |
| **2** | **Measure the NVIDIA endpoint.** Get a key, fire 100 calls at Kimi, watch for 429 and for any credit counter | **~10 min, free** | **Whether "perpetual" is a real word.** Everything in Part 1 waits on this |
| **3** | **Run BUILD's window on Sonnet 5** (`/model`, per-window, reversible) for the 7 bounded + 12 tooling items | **0 min** | Whether a cheaper Anthropic tier closes our items cleanly — the control condition for any Kimi test |
| **4** | **Stand up LiteLLM → `nvidia_nim`, point ONE window at it.** Give it BUILD. Run one item that already has `## verify` and `## criteria` | **~30 min** | Whether the gateway route works end to end, hooks intact |
| **5** | **The art bake-off.** `OPENAI_API_KEY`; GPT Image 2 vs FLUX.1 Kontext on the 30 vehicle sprites; grade with `validate_sprite.py` | **~1 h** | Whether reskin-at-scale is a technical option at all |
| **6** | **Only then decide topology.** Not before | — | — |

### We already own the measurement instrument

The source document lists thirteen things to measure and proposes building an evaluation harness.
**We do not need to build one.** The ledger already records, per item: who claimed it, who closed
it, how long it took (median 2.89 h), and whether verification returned pass / partial / fail
(81 / 66 / 12 to date). Add the model to the seat and the ledger answers *accepted-work rate per
model* on its own, with no new code and no new file — which is exactly the metric the document
says matters and the one it expects to be hardest to get.

---

## One-paragraph answer, if only one paragraph is read

**Run the mixed fleet, but reach for Sonnet 5 before Kimi.** The gateway route is real and cheap —
two environment variables per window, and none of our 2,333 lines of hooks, 7,139 lines of skills,
80,932 lines of Python or 2,088 ledger events move — but the free endpoint is a 40 RPM lane of
unmeasured durability, and four fanning-out seats will not fit in it. Meanwhile the saving we have
actually been leaving on the table needs no gateway at all: **every census and sweep this project
has ever run went to Opus**, because the one line in our own skill that says to use Haiku has never
been executed. Put the cheap tiers on the disposable workers today, keep Opus where the job is
deciding whether an instrument lied, and treat Kimi as an adversary feeding CHECK rather than a
CHECK replacing it. On art: **GPT already draws our pixels — the missing piece is an API key, not
a model**, and while a 1,123-sprite reskin is now a $46 afternoon, our own census says the entire
cast needs two redraws, and the six things a human must look at do not get cheaper when the
generator does.

---

## Sources

Accessed 2026-08-24. Repository measurements were taken today by four parallel censuses of this
working tree; artifact sizes, item counts, ledger statistics and file inventories are CONFIRMED
locally and need no external citation.

1. [NVIDIA Build — Kimi K2.6](https://build.nvidia.com/moonshotai/kimi-k2.6)
2. [NVIDIA Developer Forum — free-tier rate-limit thread (May 2026, no staff reply)](https://forums.developer.nvidia.com/t/request-nvidia-nim-free-tier-rate-limit-increase-40-rpm-severely-limits-agentic-ai-workflows/369762)
3. [NVIDIA Developer Forum — credits & rate-limit increase requests](https://forums.developer.nvidia.com/t/credit-rate-limit-increase-request-1-000-5-000-credits-40-200-rpm/380932)
4. [LiteLLM — NVIDIA NIM provider](https://docs.litellm.ai/docs/providers/nvidia_nim)
5. [LiteLLM — using Claude Code with non-Anthropic models](https://docs.litellm.ai/docs/tutorials/claude_non_anthropic_models)
6. [Morph — Claude Code + LiteLLM setup, env vars and the malware advisory](https://www.morphllm.com/claude-code-litellm)
7. [NVIDIA NIM for Visual Generative AI — model list (FLUX, FLUX.1 Kontext, Qwen-Image)](https://docs.nvidia.com/nim/visual-genai/latest/models.html)
8. [NVIDIA — flux.1-kontext-dev API reference](https://docs.nvidia.com/nim/reference/black-forest-labs-flux_1-kontext-dev)
9. [Black Forest Labs — FLUX.1 Kontext](https://bfl.ai/models/flux-kontext)
10. [OpenAI — image generation guide (`background`, `output_format`)](https://developers.openai.com/api/docs/guides/image-generation)
11. [OpenAI image API pricing calculator (per-image estimates)](https://costgoat.com/pricing/openai-images)
12. Anthropic model table — cached 2026-06-24 in the bundled `claude-api` skill; live check is the Models API.
