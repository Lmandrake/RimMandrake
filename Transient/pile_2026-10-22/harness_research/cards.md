# Decisions from the agent-harness report (2026-10-22) — ready for question cards

## Q1. Should we pay for an outside agent product now?
- **A. No. Build our own test service first, then try products against it. (Recommended)** Buys: every later trial is cheap and fair, and nothing touches the game except our service. Costs: 2-4 days of agent build time before any product trial. Why recommended: no product has shown it works with a live RimWorld, and our bottlenecks are not coding ones.
- **B. Start a Devin Pro ($20/mo) trial now, in parallel.** Buys: early real-world signal on Local Hands and Dynamic Workflows. Costs: your setup and review minutes, plus a second orchestrator competing for the one game.
- **C. Start a Factory or Cursor trial now.** Buys: Missions' plan → milestone → validation loop, or Cursor's local workers. Costs: same as B, and Cursor's Windows worker support is unverified.
- **D. Spend the money on a human instead (part-time tester or contractor block).** Buys: real judgment on harness-vs-mod failures and fixtures. Costs: hiring and onboarding time, and your time to brief them.

## Q2. How should we get more live-test throughput?
- **A. A machine-run belt and save fixtures on the one game we have. (Recommended)** Buys: re-proves run unattended and overnight, with no new hardware. Costs: still one game at a time. Why recommended: cheapest, and it is needed under every other option.
- **B. A + a second RimWorld instance on Archmagi.** Buys: maybe ≥1.5× proofs/hour. Costs: RAM, CPU and Steam risk; only after experiment E1.2 passes.
- **C. A + a dedicated second Windows machine for testing.** Buys: true isolation and no contention with your own play. Costs: hardware and upkeep.
- **D. A + Hyper-V checkpoints of a warmed game.** Buys: instant resets. Costs: unproven with a GPU game, and checkpoints hold old DLLs.

## Q3. Helpers keep colliding in one clone. What isolation do you allow? (Worktrees are OFF by your 2026-10-02 ruling.)
- **A. One full clone per writing helper, plus a serial lander script. (Recommended)** Buys: no more shared-tree push refusals, and parallel writers. Costs: disk space and a lander to build. Conflicts surface at landing. Why recommended: it gives isolation without using worktrees, and the seats already work this way.
- **B. Keep the shared clone with one writer at a time.** Buys: nothing to build. Costs: today's refusals and serial waits continue.
- **C. Lift the worktree ban.** Buys: the cheapest isolation. Costs: reopens whatever led to the 2026-10-02 ruling.
- **D. Send offline-only work to cloud agents (separate sandboxes, PRs).** Buys: zero local collisions for that work. Costs: those agents lack our skills and hooks, and can't build against the RimWorld DLLs.

## Q4. Which decisions may agents take without asking you?
- **A. A narrow written list of technical classes: harness thresholds, test-site choices, refactors inside a mod, and MOD/SITE/HARNESS calls with evidence. Everything taste-related stays yours. (Recommended)** Buys: fewer cards, and your time goes to taste. Costs: an occasional call you'd have made differently. These are logged as `--why "delegated: <class>"`, never as your approval. Why recommended: it starts narrow and can widen after a shadow day.
- **B. None. Keep asking by card.** Buys: full control. Costs: work waits on you, as now.
- **C. Everything except art, north-star bars and anything irreversible, with a timeout default.** Buys: maximum autonomy. Costs: higher risk of design drift.

## Q5. Which experiments may we run first?
- **A. E0 (time budget + account check), E1.0 (GABS fit) and E1.1 (belt robustness) this week. (Recommended)** Buys: facts about where time actually goes, and a trustworthy unattended belt. Costs: about 2 agent-days and one bridge-holding day. Why recommended: every other choice depends on these results.
- **B. All experiments, including the vendor bake-off.** Buys: the fullest answer within two weeks. Costs: more bridge time and some product sign-ups.
- **C. Only E0 for now.** Buys: a cheap look before any build. Costs: slower to any gain.
