## Options A, B, C

1. **A’s “cheapest per run” claim ignores total work.** Repeated exploration, packet retrieval, and rediscovering implementation rationale can outweigh smaller prompts. Measure cost through accepted completion, including retries and judges. Keep sessions alive across coherent implementation tasks, even if stage boundaries disappear.

2. **A relocates the memory problem into packet generation.** “Everything else is searchable” assumes the agent knows what information is missing. Require task-specific retrieval, source references, explicit omissions, and regression checks for previously missed constraints. A 15k target needs an overflow policy.

3. **B’s “one mind” language oversells transcript reuse.** Resuming supplies conversation history. Every request still reconstructs context, and automatic compaction can discard details. The 120k rotation threshold needs evidence. Test rotation against task boundaries, retrieval accuracy, latency, and actual context usage. [Claude Code session model](https://code.claude.com/docs/en/how-claude-code-works)

4. **B’s fallback can duplicate damage.** A failed resume may follow successful code edits, deployments, or bridge actions. Starting A immediately could repeat them. Reconcile the worktree, outstanding tools, and external effects before retrying. Persisting a session ID alone is inadequate recovery engineering.

5. **C’s stated disadvantages are partly invented.** A seat can have automatic wakeups and supervised overnight execution. All three options already impose two-mod WIP, so C’s throughput ceiling needs a more specific explanation. Its “low correctness risk” also ignores stale context, operator dependence, and changes made outside the dispatcher.

6. **The options mix independent decisions.** Ownership, session retention, scheduling, and storage architecture can vary separately. C also retains warm context, contradicting B’s claimed exclusivity. Sequential judges editing code likewise remain compatible with single-threaded writes. The real requirement is controlled write ownership and evidence invalidation.

## Shared core

7. **Shards solve file contention while leaving state conflicts unresolved.** Two clones can independently acquire a lease or confirm incompatible stages. Timestamp sorting provides an order without establishing which transition was valid. Specify authoritative acceptance, causal prerequisites, expected-state checks, and conflict rejection. “Already solved in rimflow” supplies no inspectable argument here.

8. **A shard per role can still have multiple writers.** Successive holders, stale holders, and multiple dispatcher instances share role names. Use unique producer identities, event IDs, idempotency keys, and atomic append handling. Define recovery from truncated writes, duplicate publication, and concurrent extensions of the same shard.

9. **Lease expiry leaves the old process alive.** It can keep editing code or driving the bridge after takeover. Enforce monotonically increasing fencing tokens at shared mutation boundaries, isolate worktrees, and cancel stale workers. Forty-five minutes copied from another rule establishes neither liveness nor safety.

10. **The authority boundary is mostly declarative.** A holder with ordinary shell access may bypass `modledger append`, impersonate another writer, or change evidence. Enforce authority through filesystem/service credentials and trusted validation. A publish-time hash check catches some modifications after the fact.

11. **Append-only history can preserve authoritative nonsense forever.** Missing schema evolution, correction rules, supersession conflicts, and version scoping make replay ambiguous. Refuted causes require conditions and expiry because later code can make them relevant again. Typed transition rules matter more than accumulating event kinds.

12. **Generated views introduce their own consistency problem.** Specify reducer versions, atomic publication, stale-view detection, and deterministic replay. A global “seq N” is undefined across independent shards. Use an accepted global offset or explicit shard offsets. Separate projections derived from identical inputs still need identical results.

13. **Judge-only confirmation has an unresolved reconciliation hole.** A fresh judge denied earlier findings cannot explicitly verify their resolutions. Silence could mean omission. Use blind discovery followed by targeted verification of prior findings. Define severity, duplicate findings, false positives, arbitration authority, and bounded review loops.

14. **Two passing judges supply uncalibrated reassurance.** Shared models, prompts, bars, and test entry points create correlated misses. Require executable regression evidence, coverage of critical risks, and immutable candidate identities. Every approval needs the code SHA, bars version, dependencies, environment, and relevant live-state identity.

15. **The ledger cannot capture “everything learned” reliably.** A dying process may write nothing. A healthy agent may write confident fiction. One trivial event satisfies the proposed end-of-run check. Capture tool evidence automatically, checkpoint incrementally, and verify durable artifacts against claims. Preserve evidence by content hash.

16. **Per-mod storage leaves cross-mod coordination unresolved.** Shared bridge access, dependencies, global rulings, tooling failures, and owner answers need explicit scope and precedence. Searching every ledger before each question creates latency and semantic deduplication work. A global answer index and resource scheduler need owners too.

17. **The migration estimate is fantasy dressed as helper-run counts.** Redirecting every legacy writer, reconciling contradictory history, preserving IDs, validating reducers, and providing rollback dominate the work. Generate and compare projections before a controlled cutover. Archive legacy evidence with provenance instead of deleting it after a summarised backfill.

## Missing directions and evaluation

18. **D deserves consideration under a central-runtime assumption.** Use one transactional coordinator with a state machine, current-state tables, an audit log, fencing, and an outbox for launches. Git stores code and immutable evidence. Workers submit commands. Sessions remain replaceable. This removes distributed lease and merge-order problems. Offline multi-clone operation would require additional machinery.

19. **The pilot confounds almost everything.** Ledger migration, session reuse, WIP limits, and machinery caps change together. One week on one evolving mod cannot identify their effects. Compare A/B on matched work after stabilising storage. Measure accepted completion time, regressions, owner minutes, total spend, retries, and recovery success. Renaming tickets as findings mechanically improves “items filed/day.”

## Starred claims

20. **★1 and ★2 establish different levels of support.** The text explicitly enumerates six stage locations. The approximately 17 stores cannot be independently reconstructed because categories are grouped inconsistently. Neither underlying census is available here. The 413 item IDs and 1,166 events can coexist, but require clear counting units.

21. **★4 has correct ordering and overstated interpretation.** 1.7 → 2.9 → 4.0 is increasing, approximately +135% overall. The last rate implies roughly 12 qualifying closes over three days. That establishes a reported rate under the chosen rule. It establishes neither improved quality nor the absence of an access bottleneck. Exposure windows, item size, and verification timing matter.

22. **★6 is an estimate with a conditional conclusion.** Bytes/4 provides an approximate token count. The supplied totals cannot reproduce 297k independently. It exceeds the assumed 200k window, while the deployed model’s actual limit remains unspecified. The packet also competes with instructions, code, and tool output. Separately, 9/76 = 11.84%, correctly rounded to 12%.

23. **★8 is unauditable here. ★9 has documented CLI support.** Anthropic explicitly documents `claude -p "…" --resume <session-id>` and session-ID capture through JSON output. Detached systemd reliability still needs a test covering credentials, permissions, transcript persistence, cancellation, and recovery. CLI support alone cannot establish that deployment claim. [Headless documentation](https://code.claude.com/docs/en/headless)

24. **★10 remains workload-dependent.** At Sonnet 4.6 API rates, 120k cached input tokens cost $0.036 per request, versus $0.045 for 15k uncached tokens. If both hit cache, 15k costs $0.0045. A 120k five-minute cache write costs $0.45. New tokens, outputs, expiration, and repeated tool calls change stage totals. Resume preserves history access without guaranteeing a cache hit. Track input categories and incremental spend because resumed CLI totals include earlier runs. [Caching rates](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [Claude Code caching](https://code.claude.com/docs/en/prompt-caching), [CLI accounting](https://code.claude.com/docs/en/headless)

## My pick

25. **D with optional B-style session reuse**, assuming a central coordinator is acceptable. I agree with stabilising durable state before testing resume. I reject committing to the sharded core first. The cited guidance supports feature ownership and independent verification, but supplies no validation for this storage architecture. Start with transactional transitions, recoverable execution, and reproducible evidence. Then measure whether longer sessions improve completion. [Anthropic guidance](https://claude.com/resources/articles/building-multi-agent-systems-when-and-how-to-use-them)