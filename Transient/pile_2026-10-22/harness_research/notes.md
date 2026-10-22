# Harness research — progress (BENCH helper, 2026-10-22)
- [x] 1 setup (setup.md) + pain points
- [x] 2 web research (notes below; primary fetches done)
- [x] 3 three recommendations (draft.md)
- [x] 4 GPT review (gpt_review.md, 41 points, verbatim)
- [x] 5 merge + validate (merge.md: 23 VERIFIED, 1 CONTRADICTED, 1 UNVERIFIED, 1 MEASURED, 2 UNMEASURED)
- [x] 6 report.html + report.md
- [x] 7 cards.md

## Search log (2026-10-22, WebSearch; secondary unless marked)
- Devin: self-serve now quota-based Free/$20 Pro/$200 Max/Teams; Enterprise ACU (pensero.ai, eesel.ai, fast.io) -> verify devin.ai/pricing
- Answer.AI month with Devin: 3 success /14 fail /3 inconclusive of 20 (answer.ai/posts/2025-01-08-devin) PRIMARY
- OpenHands: MIT, local free, cloud BYOK, enterprise self-host (openhands.dev/pricing)
- Codex: in ChatGPT Plus/Pro/Business; $100 Pro tier Apr 2026 (thurrott); Linear @Codex integration (linear.app/integrations/codex)
- Jules: free 15 tasks/day, 3 concurrent; AI Pro/Ultra 5x/20x (yahoo/techcrunch)
- Copilot coding agent: Windows projects Feb 2026 changelog, self-hosted runners Oct 2025 (ARC), firewall off
- Cursor: self-hosted cloud agents GA 2026-03-25; worker outbound HTTPS; tools run on your machine (cursor.com/blog/self-hosted-cloud-agents)
- Factory droids: $20/$100/$200 tiers (aggregators only) THIN
- Claude Code: routines (research preview, cloud, schedule/API/GitHub trigger); agent teams experimental (code.claude.com/docs/en/agent-teams); Agent SDK separate credit from 2026-06-15 (developersdigest, secondary)
- Orchestrators: Vibe Kanban (OSS, company shut down Apr 2026), Claude Squad (tmux+worktrees), Conductor (macOS)
- Game QA: TITAN preprint arXiv 2509.22170 (95% task completion, 4 new bugs), AWS Bedrock Unity test agent blog, modl.ai, Razer QA Companion GDC 2026
- METR RCT: 16 devs, 19% slower, believed 20% faster (secondary coverage)
- GABS (pardeike): MCP server mirroring GABP game bridges -> any MCP agent could reach RimBridge locally
- Primary fetches 2026-10-22: devin.ai/pricing (no ACU, Free/$20/$200/Teams $80+$40, concurrency up to 10 vs unlimited); github changelog 2026-02-18 Windows; github changelog 2025-10-28 ARC; cursor blog self-hosted (GA 2026-03-25) + help page (macOS/Linux, no Windows stated; computer use macOS/Linux workers); code.claude.com agent-teams (experimental, no -p, file-lock task claim); routines->"scheduled tasks" (research preview, Pro/Max/Team/Ent, cloud, min 1 h, fresh clone, can route to self-hosted env); self-hosted envs (public beta, Team/Ent only); Projects (public beta Pro/Max, threads cloud or on your computer via Remote Control, phone); Desktop scheduled tasks (local, machine awake); openhands.dev/pricing (free MIT, Teams $499/mo); linear Codex integration; jules usage limits 15/100/300 per day, 3/15/60 concurrent; GABS pkg.go.dev; arXiv 2509.22170 TITAN; METR blog.
- Account-type note: ANTHROPIC_BASE_URL not set in env or ~/.claude/settings.json at 2026-10-22 (MEASURED) -> cloud features plausibly reachable; eligibility UNMEASURED.
