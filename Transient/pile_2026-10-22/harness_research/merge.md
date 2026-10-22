# Merge: GPT review (gpt_review.md, 41 points) folded into the draft, plus validation

## Disposition of GPT's points
| # | Point (short) | Verdict | Reason / what changed |
|---|---|---|---|
| 1 | Compare whole operating models, not tools | ACCEPT | Report now compares "today / improved Claude Code / vendor orchestrator over the same test service" |
| 2 | Separate orchestration from execution | ACCEPT | Became the spine of R1 (local test service owns the game; anything may submit jobs) |
| 3 | Measure owner minutes per accepted feature | ACCEPT | Every experiment now records owner minutes; slot occupancy demoted |
| 4 | Label evidence precisely | ACCEPT | "Stranded" ≠ "lost"; gaps ≠ "LLM asleep"; 548 rows ≠ coverage. Wording fixed |
| 5 | Time budget before promising gains | ACCEPT | New E0: attribute one belt day's minutes from the logs before building anything |
| 6 | Shrink landscape table to observable capabilities | ACCEPT (partly) | Columns now: local executor, reach to our bridge, orchestration, human channel, evidence. Prices kept, but short |
| 7 | "Every hosted agent is remote Linux" is wrong | ACCEPT | Rewritten: no verified turnkey integration with our game. Several products now have local executors |
| 8 | Devin has a Windows/WSL CLI and Local Hands | ACCEPT, VERIFIED | Confirmed on docs.devin.ai. Local Hands is rolling out gradually, approval-gated, and has no screen control |
| 9 | Devin has Dynamic Workflows | ACCEPT, VERIFIED | Deterministic Python, resumable, 7-day budget. Added to landscape and to the bake-off |
| 10 | Codex cloud has VPN (Tailscale) | ACCEPT, VERIFIED | Our draft line "VPN isn't available" is CONTRADICTED. Removed |
| 11 | Use official Codex pricing | ACCEPT, VERIFIED | Plus $20, Pro from $100 ($100/$200/$500), API key = no cloud features |
| 12 | Cursor docs "explicitly discuss Windows workers" | REJECT as stated | The docs never list Windows as supported. They only say a Windows worker starts without the live workspace. Status: UNVERIFIED |
| 13 | Copilot runners: Ubuntu x64 + Windows 64-bit; AI Credits | ACCEPT, VERIFIED | Both confirmed on docs.github.com and the github.blog 2026-06-01 changelog |
| 14 | Factory pricing + Missions | ACCEPT, VERIFIED | $20/$100/$200 confirmed. Missions require a scriptable QA harness, which we have (the proof scripts) |
| 15 | OpenHands Agent Canvas: local default, ACP for Claude Code/Codex | ACCEPT, VERIFIED | Windows/WSL not stated |
| 16 | Claude Projects: Pro/Max beta, per-user, availability check | ACCEPT, VERIFIED | Added "account check first" (E0) |
| 17 | Keep Claude scheduling limits scoped | ACCEPT | |
| 18 | Vibe Kanban shutdown ≠ dead; "none knows the bridge" is a gap, not a veto | ACCEPT | Softened |
| 19 | Answer.AI is weak purchasing evidence today | ACCEPT | Kept as a caution about supervision cost, not as a verdict on the category |
| 20 | METR has a 2026 update | ACCEPT, VERIFIED | The 2026 post says its newer data is too selection-biased to size the effect and that speedup is likely now. Both cited |
| 21 | Game-QA evidence doesn't transfer | ACCEPT | TITAN was evaluated on two MMORPGs (VERIFIED) |
| 22 | R1: make deploy/cleanup/evidence deterministic, not verdicts; wake agent on timeout/invalid evidence too | ACCEPT | R1 rewritten |
| 23 | E1.1's 80% bar allows false passes | ACCEPT | New bar: zero known-bad variants pass, every case reaches a terminal state, no orphan process |
| 24 | E1.2: ping ≠ independence/throughput | ACCEPT | New bar: ≥1.5× proofs/hour at equal reliability, with Steam env-passing checked |
| 25 | DRM-free edition exists; trigger on XML/fixture changes too | ACCEPT (partly) | Ludeon offers a DRM-free download link (VERIFIED). Our "launch via Steam" rule stays until its reason is re-read |
| 26 | R2: clones move conflicts to integration; ledger authority | ACCEPT | Lander + one ledger writer per clone (rimflow shards are per seat, so each writer gets its own) |
| 27 | E2.1 needs adversarial cases | ACCEPT | Added overlapping edits, an interrupted landing, and a DLL/source mismatch |
| 28 | E2.2 tests offline coding, not management | ACCEPT | Split: E2.2 offline matched trial; the management question moved to the bake-off (E3.3) |
| 29 | R3: explicit delegation policy, not default-as-approval | ACCEPT | Unanswered cards are never recorded as owner approval. Logged with `--why "delegated class X"`, not `--by-card` |
| 30 | E3.1 overturn-rate is wrong metric | ACCEPT | Now severity-weighted, plus rework minutes |
| 31 | Slot occupancy is the wrong objective | ACCEPT | Metric is now dispatch delay on genuinely ready work |
| 32 | Local test service makes vendors interchangeable | ACCEPT | Core of R1 |
| 33 | Evaluate GABS before building lifecycle plumbing | ACCEPT, VERIFIED | The RimBridgeServer README calls GABS "the best way" to use it from a harness. GABS has launch profiles and per-game ownership leases. New E1.0 |
| 34 | Hyper-V checkpoints with memory | DEFER | Running a GPU game inside a VM on Archmagi is an unmeasured feasibility question, and a restored checkpoint holds old DLLs. Listed as an option, not recommended |
| 35 | Versioned save fixtures + warm pools first | ACCEPT | Folded into R1 as the cheaper first step before a second instance |
| 36 | Tick-predicate waits, HeadlessRim, replay | PARTLY | Predicate waits: accept. HeadlessRim: reject for now (3 stars, version unstated, VERIFIED). Replay: note only |
| 37 | Dedicated Windows test machine | ACCEPT as option | On the card as an alternative to a second instance |
| 38 | Hooks, Channels, /loop, /goal before a heartbeat | ACCEPT | R3 now prefers events: completion hooks, Channels (preview), dynamic workflows. A heartbeat only for recovery |
| 39 | `codex exec` JSON-schema classifier | ACCEPT (minor) | Noted as one option for the FAIL classifier. Our gpt_consult already uses codex.exe |
| 40 | Direct orchestration bake-off | ACCEPT | New E3.3: one milestone run through Claude Code dynamic workflows vs Devin (Local Hands + Dynamic Workflows) vs Factory Missions, all against the same test service |
| 41 | Cap WIP; design briefs; human-help baseline | ACCEPT | WIP cap is in R3. A paid human tester/contractor block appears as a card option |

**Our own additions found during validation:** Claude Code **dynamic workflows** (local, a JS script orchestrating subagents, resumable in-session, on all paid plans and third-party providers, no mid-run user input) are a built-in alternative to Devin Dynamic Workflows that already runs where the game is. Neither the draft nor GPT named them.

## Validation of load-bearing claims (second fetch of a primary source, 2026-10-22)
| # | Claim | Status | Sources (both fetched 2026-10-22) |
|---|---|---|---|
| V1 | Devin: Free $0 / Pro $20 / Max $200 / Teams $80 + $40/seat / Enterprise custom; no ACUs on page | VERIFIED | devin.ai/pricing ×2 |
| V2 | Devin Local Hands runs a cloud session's shell/file tools on your machine, per-call approval, no screen control, rolling out | VERIFIED | docs.devin.ai/work-with-devin/local-hands + GPT's independent read |
| V3 | Devin CLI runs locally on Windows, WSL, Linux, macOS | VERIFIED | docs.devin.ai/work-with-devin/devin-cli + GPT |
| V4 | Devin Dynamic Workflows = deterministic Python orchestration, resumable, 7-day max | VERIFIED | docs.devin.ai/work-with-devin/dynamic-workflows + GPT |
| V5 | Answer.AI: 3 successes, 14 failures, 3 inconclusive out of 20 (2025-01-08) | VERIFIED | answer.ai post (html and .md) |
| V6 | METR early-2025: +19% time with AI; devs believed +20% speedup. 2026 update: data too selection-biased; speedup likely now | VERIFIED | metr.org 2025-07-10 + 2026-02-24 posts |
| V7 | Codex cloud cannot reach private networks (draft claim) | CONTRADICTED | learn.chatgpt.com/docs/environments/cloud-environments: Tailscale VPN supported |
| V8 | Codex: Plus $20; Pro from $100; API key gives no cloud features | VERIFIED | learn.chatgpt.com/docs/pricing; secondary thurrott |
| V9 | Linear: assigning @Codex starts a cloud agent; Plus/Pro/Business/Ent/Edu | VERIFIED | linear.app/integrations/codex ×2 |
| V10 | Jules limits 15/3, 100/15, 300/60 (tasks per day / concurrent) | VERIFIED | jules.google/docs/usage-limits ×2 |
| V11 | Copilot coding agent: Ubuntu x64 + Windows 64-bit runners; firewall incompatible with Windows and self-hosted | VERIFIED | github.blog 2026-02-18 + docs.github.com |
| V12 | Copilot bills in AI Credits since 2026-06-01 | VERIFIED | github.blog 2026-06-01 + GPT |
| V13 | Cursor self-hosted cloud agents GA 2026-03-25; outbound-HTTPS worker | VERIFIED | cursor.com/blog + cursor.com/changelog/03-25-26 |
| V14 | Cursor supports Windows workers | UNVERIFIED | cursor.com/docs/cloud-agent/self-hosted lists none; only implies one can start |
| V15 | OpenHands: free MIT self-host; Teams $499/mo (10 users, 5,000 sessions/mo) | VERIFIED | openhands.dev/pricing ×2 |
| V16 | OpenHands Agent Canvas: local default backend; ACP for Claude Code/Codex/Gemini | VERIFIED | docs.openhands.dev + GPT |
| V17 | Factory $20/$100/$200; Missions need a scriptable user-level QA harness | VERIFIED | docs.factory.com pricing + missions; aggregators agree |
| V18 | Claude cloud scheduled tasks: research preview, Pro/Max/Team/Ent, ≥1 h interval, fresh clone, cloud or org self-hosted env | VERIFIED | code.claude.com routines ×2 |
| V19 | Claude Projects: public beta Pro/Max (not Team/Ent), threads can run on your computer via Remote Control, steer from phone | VERIFIED | code.claude.com claude-projects ×2 |
| V20 | Claude self-hosted environments: public beta Team/Ent; Windows not a supported runner host | VERIFIED | self-hosted-environments + quickstart |
| V21 | Agent teams: experimental, off by default, no teammates under `-p`, same-file edits overwrite | VERIFIED | code.claude.com agent-teams ×2 |
| V22 | Claude dynamic workflows: all paid plans + Bedrock/Vertex/Foundry; JS script; resumable in session; no mid-run input; 16 concurrent default | VERIFIED | code.claude.com workflows ×2 |
| V23 | Claude Channels push events into a running local session; research preview | VERIFIED | code.claude.com channels + GPT |
| V24 | RimBridgeServer: GABS recommended; GABS has launch profiles and per-game ownership leases | VERIFIED | github.com/pardeike/RimBridgeServer + github.com/pardeike/GABS + pkg.go.dev |
| V25 | TITAN: 95% completion, 4 new bugs, 8 pipelines, 2 MMORPGs (preprint) | VERIFIED | arxiv abs + html |
| V26 | Our bridge client reads `GABP_SERVER_PORT` | MEASURED | src/RimMandrake/Utils/rimbridge_client.py:84,394 |
| V27 | Two RimWorld instances can run concurrently on Archmagi with separate bridges | UNMEASURED | no source; this is experiment E1.2 |
| V28 | Our login can use cloud scheduled tasks / Projects | UNMEASURED | ANTHROPIC_BASE_URL absent from env and ~/.claude/settings.json (MEASURED); plan tier not checked |

Counts (MEASURED from this table): VERIFIED 23 · CONTRADICTED 1 · UNVERIFIED 1 · MEASURED (repo) 1 · UNMEASURED 2. Total 28 (one of the 28 is the draft claim marked CONTRADICTED; GPT claim #12 is also marked rejected-as-stated under V14).
