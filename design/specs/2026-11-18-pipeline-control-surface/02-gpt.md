# GPT critique (pass 2)

- consult id: consult-20261118-105324-690292-0a59c8
- earlier blind consult: consult-20261118-103923-596267-fd188b
- model: gpt-6.1-sol
- local time: Wed Nov 18 10:59:22 PST 2026
- tokens: unknown

---

I agree with moving controls out of git and putting admission at the launch boundary. **I would not adopt B+D as written. My pick is a narrower sixth option: one control service that owns authorization and launch, with reserve-then-settle accounting in one SQLite database on native Linux storage.** Keep the existing schedulers initially; make them submit proposals.

I reviewed the inlined text and primary documentation/source. I did not inspect the repository, scratch evidence or live host. “Measured” below therefore means *reported by the design*, unless explicitly verified.

Severity: **Critical** permits unauthorized work or incorrect accounting; **High** breaks a principal requirement; **Medium** weakens operation, evidence or estimates.

1. **Critical — The options omit the strongest incremental architecture.**

   Option E unnecessarily bundles SQLite with migrating *all* pipeline state. A service can initially own only controls, authorization, reservations, run identities, settlement and audit. Stage documents and existing scheduling logic can remain where they are.

   The flow should be:

   `scheduler proposal → control service → transactionally authorize/reserve → launch → reconcile → settle`

   Compared with B, this eliminates independently versioned admission implementations across clones and makes switches, reservations and audit commit together. Compared with full E, it avoids rewriting every reader immediately.

   Costs missing from this alternative are service supervision, IPC/API compatibility, recovery, backups, launch reconciliation and a deliberate availability dependency. Those costs are justified here: B needs equivalent coordination and recovery machinery, distributed across log writers and readers.

   **Confirm:** implement the same pause/concurrency/crash scenarios against both designs. Prefer the one with fewer independently coordinated writes and authoritative decision points, not fewer initial lines of code.

2. **Critical — B has a pause-versus-launch race.**

   This execution is allowed by the specification:

   `admit reads ON → pipe off commits → systemd-run starts work`

   Moving a check into a primitive narrows the race; it does not close it. `ExecCondition` adds another check but also leaves a check-to-execution interval.

   Define an explicit ordering contract. For example: pause commits a new control revision, cancels unstarted reservations, and prevents further start authorizations. A launch that crossed the defined start boundary earlier is reported as an existing run. A stronger “nothing pending may start after this command returns” operation must drain or cancel outstanding starts before acknowledging success.

   The control service must serialize pause with its launch protocol. Merely using SQLite, or returning an authorization token to an arbitrary caller, is insufficient.

   **Confirm:** block execution immediately after admission, issue pause, then release the blocker. Test both orderings and require the documented result.

3. **Critical — Allowances need reservation, not retrospective subtraction.**

   With one look remaining, two callers can both observe one remaining and launch. Later voiding cannot undo those two evaluations.

   In one transaction, validate controls and scope, check every applicable allowance, reserve the required quantities, create the run and record the launch intent. For each resource account:

   `available = grants + adjustments − settled charges − outstanding reservations`

   Accounts need explicit keys such as mod, product version, stage visit, resource type and accounting window. Reserve all applicable resources together. Settlement converts reservations into charges or releases them, exactly once. A later void reverses identified charges, exactly once.

   SQLite provides the transaction machinery; the application must supply the correct invariants and constraints. [SQLite transaction documentation](https://sqlite.org/lang_transaction.html)

   **Confirm:** submit simultaneous requests against one remaining look; exactly one receives a reservation. Repeat settlement and void requests; balances must remain unchanged after the first application.

4. **Critical — SQLite cannot transact with systemd; crash recovery is still required.**

   Both B and the proposed service must handle:

   - Reservation committed, process dies before starting the unit.
   - Unit starts, but the launcher dies before recording success.
   - A response is lost and the caller retries.
   - The unit finishes before its completion event is recorded.

   Use a durable launch-intent/outbox record, an idempotency key, a predetermined unique unit name and reconciliation against systemd plus durable runner receipts. An ambiguous start must be investigated, not retried under a fresh identity.

   Do not release a reservation merely because its lease expired while the old process might still run. First fence or establish termination. Disable unmanaged automatic payload restarts, or model each restart attempt explicitly.

   **Confirm:** kill the service at every boundary above. Recovery must produce neither duplicate work nor duplicate charges.

5. **Critical — “Bypass = 0 by construction and test” is overstated.**

   A call-site search cannot prove completeness. It misses direct D-Bus calls, subprocess wrappers, alternate binaries, direct model API calls and future launchers. A PATH shim is easily bypassed by `/usr/bin/systemd-run`.

   More fundamentally, agents running as the same user who owns the user manager, controls and credentials retain the ability to bypass cooperative conventions. If the requirement is a hard guarantee, isolate launcher authority and model credentials behind the service, with workers unable to obtain equivalent authority directly. Otherwise describe the guarantee as protection against mistakes in cooperating code.

   Validate declared mod, stage, role and cap against authoritative state; trusting arbitrary declarations lets callers evade controls by mislabelling work.

   **Confirm:** attempt an absolute-path launch, direct D-Bus launch, alternate-prefix launch and direct API invocation from the worker’s actual security context.

6. **High — Option A is unsuitable as the permanent core, but its critique contains avoidable limitations.**

   Concatenated local status, unchanged bypasses and auto-publish delays describe this particular implementation, not necessary properties of a thin CLI. A thin front door could query live state and call a central admission API.

   A’s real weaknesses are partial multi-store writes, ambiguous partial success, different locking rules and substantial per-operation compensation logic. Auto-publishing operational controls also introduces unrelated code landing and test failures into an emergency command.

   Improve A by using adapters as migration infrastructure, with a stable CLI and explicit receipts. Route pause through the new authority immediately; avoid auto-publish for live controls.

   **Confirm:** interrupt a multi-store command after each write. The command must accurately identify what took effect and what requires recovery.

7. **Critical — B’s JSONL design is a transaction system without a specified commit protocol.**

   `acts.jsonl`, `view.json`, `runs.jsonl` and existing counters cannot be committed atomically by renaming `view.json`. A matching hash establishes correspondence to some log contents, not a consistent transaction across all these stores.

   Missing details include lock scope, reader synchronization, durable flushes, acknowledgement after durability, idempotency, sequence allocation, schema migration, disk-full handling, checkpoints and interrupted repair. Hashing the entire history on every read also makes the claimed cache less useful.

   “Repair drops a torn last line” is particularly dangerous: that line might contain an acknowledged pause. Preserve damaged evidence, establish the last committed boundary, and remain closed until recovery resolves uncertainty.

   A file journal can be made correct. Here, SQLite avoids implementing much of that machinery manually.

   **Confirm:** inject failures between every append, flush, cache replacement and acknowledgement. No acknowledged hold may disappear.

8. **High — `control.adjust(mod, counter, raw)` cannot express several listed resources correctly.**

   A scalar adjustment cannot reconstruct “three consecutive non-passes.” Voiding the middle event changes sequence semantics. It also cannot safely attribute historical charges to stage visits or versions without those identities.

   `set` needs ordering semantics: does setting usage to zero establish a baseline at that revision, or override all future raw usage? Grants, remaining allowance and used allowance must be distinct concepts. Refusal alarms, retry limits and merit trials may need different compensation policies.

   Record per-run charges against typed resource accounts. Derive streaks from ordered, valid events. During migration, use explicit opening balances and reconcile against the old counters.

   **Confirm:** void a middle streak event, void a run from a previous visit, and issue `set` while another run completes. Check every affected consumer.

9. **Medium — Option C is rejected using a false coupling.**

   Declarative intent, event history, storage and admission are separate choices. Desired state can hold limits, switches and queue order while an accounting ledger holds reservations and consumption. Updating observed consumption does not inherently destroy auditability.

   Nor does declarative control require rewriting all 4,633 lines at once. Introduce a typed control model and extract pure decision functions incrementally. C still needs authoritative admission for external launchers.

   Improve C by declaring **limits and intent**, rather than treating “remaining” as an independently editable historical fact.

   **Confirm:** adapt one existing decision path to consume the typed snapshot without changing its scheduling behavior.

10. **High — Claims 12* and 13: transient drop-ins work on upstream v259, but the version explanation is wrong.**

    **Yes:** on upstream systemd v259, drop-ins—including applicable hyphen-prefix drop-ins—can apply to transient services created by `systemd-run`. Transient-unit drop-in support arrived in **v252**. Prefix drop-ins already appear in the **v239** documentation; “requires ≥246” is not the correct feature boundary. [v252 release notes](https://raw.githubusercontent.com/systemd/systemd/v252/NEWS), [v239 unit documentation](https://raw.githubusercontent.com/systemd/systemd/v239/man/systemd.unit.xml)

    `ConditionPathExists=` belongs in `[Unit]`; `ExecCondition=` belongs in `[Service]`. A condition can also be supplied explicitly when creating a transient unit, for example:

    ```bash
    systemd-run --user \
      --property='ConditionPathExists=/absolute/path/to/permit' \
      /bin/true
    ```

    The v259 property parser supports condition assignments. A regular template service started through `systemctl` is another option. [v259 property implementation](https://raw.githubusercontent.com/systemd/systemd/v259/src/shared/bus-unit-util.c)

    These mechanisms do not automatically propagate a condition from the dispatch service to every child unit. Each created unit must receive it through an applicable drop-in, explicit property or template.

    **Confirm:** run the probe on the actual manager, using a payload marker and inspecting effective conditions/drop-ins. Test both condition outcomes. The provided probe does not itself establish all those facts.

11. **High — Claim 14 is substantially correct; D still needs stronger result handling.**

    A normal `ExecCondition` exit of 1–254 skips the remaining commands without marking the service failed; exit 255 or abnormal termination is different. Non-`--wait` `systemd-run` treats a skipped start job as success. This is supported by the implementation, not merely a guess. [Service documentation](https://www.freedesktop.org/software/systemd/man/259/systemd.service.html), [start-job result handling](https://raw.githubusercontent.com/systemd/systemd/v259/src/shared/bus-wait-for-jobs.c)

    Also, the default `Type=simple` can report successful startup before the payload executable is successfully invoked. `Type=exec` improves that, but does not prove application readiness or successful work. [systemd-run documentation](https://www.freedesktop.org/software/systemd/man/259/systemd-run.html)

    Consequently, charge on validated settlement, never on launcher exit code alone. Distinguish refusal, condition skip, startup fault, unknown outcome and completed work.

    **Confirm:** test condition exits 1 and 255, a missing executable, application initialization failure and lost completion output.

12. **High — D is useful containment, not an independent universal gate.**

    Correct the prefix census: `rm-judge.service.d` applies to that exact unit; a family such as `rm-judge-*.service` needs the corresponding trailing-hyphen prefix directory.

    A slice can group runs for stopping, but stopping it is not a durable pause: later launches can activate it again. A launcher can also omit the slice. Keep the control service outside the slice it stops.

    `ConditionPathExists=!PAUSE` is insufficient for the unreadable-store requirement: absence of a pause marker does not establish a readable, initialized authority. Prefer a gate that reports store failure explicitly. Conditions are evaluated at start, not continuously, and do not stop existing work. [Unit condition semantics](https://www.freedesktop.org/software/systemd/man/259/systemd.unit.html)

    **Confirm:** stop the slice and attempt another launch; test an unknown prefix, missing store, permission denial and launch without the slice.

13. **High — Claim 15* is unverified; claim 26 is too broad.**

    “Drvfs locking is unreliable” conflates several mechanisms:

    - On legacy 9P paths without a filesystem `flock` operation, Linux can provide a local kernel `flock` lock.
    - The WSL kernel’s legacy 9P byte-range-lock path differs from its 9P2000.L implementation.
    - Local locking does not establish exclusion against Windows writers, separate mounts or other clients.

    Those distinctions are visible in the [WSL kernel implementation](https://raw.githubusercontent.com/microsoft/WSL2-Linux-Kernel/linux-msft-wsl-6.6.y/fs/9p/vfs_file.c) and [Linux flock fallback](https://raw.githubusercontent.com/torvalds/linux/v6.6/fs/locks.c). Existing `tick.lock` files prove none of the required exclusion or durability properties.

    SQLite warns about faulty filesystem locking; WAL also has shared-memory and same-host requirements. Neither supports an unconditional verdict for every mount called “drvfs.” [SQLite corruption guidance](https://sqlite.org/howtocorrupt.html), [WAL documentation](https://sqlite.org/wal.html)

    I would put either authoritative implementation on native Linux storage now. Windows can invoke the CLI through WSL or read exports; visibility does not require hosting the live database on `D:`.

    **Confirm:** record the actual WSL/kernel version, filesystem, protocol and mount options. Test competing processes through every supported access path, then crash durability separately. Never replace the inode of a lock file while relying on locks held on it.

14. **High — An unreadable authority needs an operational recovery contract.**

    B correctly specifies fail-closed admission, but omits missing/uninitialized stores, disk-full writes, unavailable service, stale readable caches and failure to append an admission record.

    Require a successful durable reservation before launch. A missing production store must not silently bootstrap into ON from repository defaults. Cached ON state must not authorize work when authority cannot be consulted.

    Existing runs may finish under previously recorded authorization, but completion receipts need durable retry. Keep emergency stopping and diagnostics available when the database is unavailable. Recovery must restore holds and reconcile outstanding runs before admitting new ones.

    **Confirm:** test missing files, permission denial, full disk, unavailable service and stale cache. Each must cause zero new authorized work and a specific error.

15. **Critical — Two clones can still disagree and duplicate work under B.**

    Shared controls do not synchronize scheduling state. Two ticks can see the same stage and both propose the same work. Different clone versions can fold or interpret acts differently. `RM_CONTROL_DIR` can accidentally point a production process at a different authority.

    Use one production endpoint, protocol negotiation, authoritative resource/visit identities and a uniqueness constraint for equivalent outstanding work. Enforce concurrency slots centrally. Reject stale-stage proposals. Treat exports and old repository controls as records after cutover, not competing defaults that can resurrect stale intent.

    Printing a tree and SHA improves diagnosis; it does not establish a coherent live snapshot.

    **Confirm:** run two differently versioned clients against the same mod concurrently, including conflicting queue edits and a stage change.

16. **Critical — “Undo any act” is not a generic inverse.**

    Example: A sets a limit to five, B sets it to two, then undoing A restores its recorded “before” value and overwrites B. Or A grants a look, a run consumes it, and undoing A leaves a deficit.

    Define undo as a new compensating act with dependency and revision checks. Remove a specific hold by identity; do not restore an old snapshot of all switches. Preserve later unrelated changes. Where resources have already been consumed, expose the resulting deficit or offer an explicit resolution.

    This still meets the owner’s requirement: provide a concrete correction command, rather than claiming history is frozen. It does not justify silently pretending dependent effects never occurred.

    **Confirm:** test `set → set → undo first`, `grant → consume → undo grant`, repeated undo, and undo after stage advancement.

17. **Critical — Voiding accounting does not revoke a stage advancement.**

    A judge run can produce a pass, advance the stage, and enable later work before it is voided. Refunding its look leaves those effects intact.

    Separate **charge validity** from **evidence validity**. A refunded system-fault run need not invalidate every artifact automatically; invalidating acceptance evidence must trigger dependency analysis. Record transitions with supporting run IDs and stage generations.

    If invalidated evidence supported advancement, hold affected downstream work and issue an explicit reconciliation: retain the stage under an exception, revalidate it, or move back while invalidating dependent results. Preserve the historical transitions.

    **Confirm:** pass → advance → launch dependent work → void/invalidate the original run. No downstream result may remain silently justified by revoked evidence.

18. **High — Failure classification and spend policy are underspecified.**

    Signal, timeout and missing output do not establish causality. A signal may follow useful completed work; timeout may indicate either a harness fault or product behavior. Keep outcome, cause, evidence validity and accounting disposition as separate fields, including an unknown/reconciliation state.

    The system-fault meter is a good idea, but an **alarm does not bound spend**. Per-run caps do not bound repeated launches, and external watchdogs can have enforcement lag.

    Preserve actual spend permanently. If void spend is excluded from the product allowance, charge it to a separate operational budget with a hard admission limit, backoff and a circuit breaker. Reserve budget headroom for concurrent runs.

    **Confirm:** repeatedly inject system faults, including parallel runs. Merit trials must remain intact while operational limits eventually refuse further work.

19. **High — The forecast promise exceeds what the system can know.**

    Shared `decide` functions help, but importing them from a WorkingDirectory does not reproduce the real scheduler’s complete inputs, environment, configuration or code already loaded in a running process.

    Thirty minutes depends on unknown completion times and outcomes. Other dispatchers and chains also change future state. A dry tick whose one state file has unchanged mtime is not proven side-effect-free.

    Extract a pure planner over a versioned snapshot, explicit clock and explicit external inputs. Use its output for both execution and explanation. Report the next decision as exact for that snapshot; report later actions conditionally: “if this run passes…” Include freshness, revisions and assumptions.

    **Confirm:** compare forecast and execution from identical captured snapshots across every launch path. Exercise time boundaries and external inputs, and detect all writes during planning.

20. **High — “Next tick, therefore ≤60 seconds” and “safe while half migrated” are unsupported.**

    A nominal 60-second timer is not a deadline. systemd timers have accuracy settings, and an already-active target service is not restarted when its timer elapses. Host suspension, load and a long tick add further delay. [Timer documentation](https://www.freedesktop.org/software/systemd/man/259/systemd.timer.html)

    Admission should honor a committed pause immediately; tick observation is separate evidence. A receipt should distinguish committed revision from scheduler-observed revision.

    Early caller checks are not harmless during migration: an old exhausted-counter check can reject before the new refunded balance is consulted. Conversely, unconverted raw launchers remain open until slice 3.

    **Confirm:** use a long-running tick and an old early-out with a newly granted allowance. Maintain a cutover matrix; disable unconverted launch paths rather than describing partial coverage as complete.

21. **Medium — The text supports some arithmetic, but several numerical conclusions need qualification.**

    | Check | Result |
    |---|---|
    | Claim 4*: ~10:20 to ~10:42 | Approximately **22 minutes**, internally consistent; measurements unavailable. |
    | Nominal context arithmetic | `100,000 × 15 = 1.5M`; correct, but not a measured weighted-token bill. |
    | Decision-code size | `3,063 + 1,570 = 4,633`; “about 4,600” is correct. |
    | Claim 10: six-command read | The six commands are unspecified. The first six listed outputs total **16,974 B**, about **16.6 KiB**, or **4,850** at bytes/3.5. |
    | All ten listed outputs | **33,338 B**; summing all of claim 9 does not produce 16 KB. |
    | Three all-unit reads | `6,155 + 3,082 + 4,875 = 14,112 B`. |
    | Claim 19: FlowWorks | `20.1M + 5M = 25.1M > 25.0M`; this supports a projected-cap admission block, not that actual spend already exceeds the ceiling. |
    | `$100 ≈25M weighted tokens` | Implies `$4/M`; the conversion basis and pricing mix are absent. |
    | Claim 25: ~3-minute propagation | Consistent with the quoted timestamps; one sample establishes no bound. |

    Claim 11’s cost dominance needs actual request usage, cache weighting and pricing evidence. Calls per act is a useful usability metric, but not a substitute for measured cost.

    **Confirm:** identify the exact six-command transcript, accounting conversion and per-request billing data.

22. **High — Every starred claim has the following evidence status.**

    | Starred claim | What can be checked here | What would confirm the remainder |
    |---|---|---|
    | **1*** Live dispatch tree | Reported consistently; not independently verified. | Effective unit configuration and actual executed command/config paths. |
    | **2*** No control reads in `detached_helper.launch` | Source absent; grep alone would also miss indirect enforcement. | Function/call-graph review plus behavior tests. |
    | **3*** ~10 paths, three primitive kinds | §2.2 has ten rows; completeness and primitive ownership are unproven. | Census including wrappers, D-Bus and runtime launch tracing. |
    | **4*** 22-minute hold | Arithmetic is consistent. | Timestamped edit, publication and live observations. |
    | **6*** Tick ignores Dispatcher PAUSE | Reported, not checkable from supplied code. | Source review and a live/isolated PAUSE behavior test. |
    | **12*** Transient prefix drop-ins | Supported for upstream **v259**; see finding 10. | Actual-host effective-unit and payload-marker probe. |
    | **15*** drvfs `flock` sufficient | Not established; see finding 13. | Exact deployment/access-path exclusion and durability tests. |
    | **17*** Useful first slice within one hour | An estimate, not a demonstrated fact; its stated scope omits universal coverage. | A timed, integrated landing satisfying explicit acceptance criteria. |
    | **22*** Three builders live at 10:44 | Three IDs are supplied. If epoch suffixes, they encode 10:31:44, 10:31:52 and 10:36:27 Pacific—plausible starts, not proof of liveness. | Timestamped unit/process observations at 10:44. |

    Other unavailable local evidence includes claims **5, 7–9, 20–21, 23–24 and 27**, the deployed version portion of **13**, and the measurements behind **19**. Claims **16 and 18** are unbenchmarked estimates. Claim **24’s stated mtime check is insufficient evidence** even if accurately performed.

    **Confirm:** supply the referenced outputs/source or perform the named checks; do not upgrade reported observations into independently verified facts.

23. **High — The command surface needs precise semantics and real authority.**

    `--owner-said` records text; it does not authenticate permission. Define which principal can lift an owner hold, grant a look or void a merit failure.

    Scope precedence also matters: `on all` should not silently lift an independent per-mod owner hold. Queue membership and queue order should be separate. `add look +1` must state whether it changes grants or usage. Bulk void should capture a fixed set of run IDs, not repeatedly reevaluate a moving time range.

    Keep one-line commands, but add idempotency keys for retried mutations, revision preconditions for conflicting edits, machine-readable output and stable exit codes. Normalize human times to an explicit timezone and instant. Compact output should include the committed revision and remaining blockers.

    **Confirm:** retry a command after losing its response; lift a global pause while a mod hold remains; issue ambiguous-time and conflicting-edit commands.

24. **High — The smallest first slice should establish the authority, not a temporary parallel switch.**

    I would build a supervised local control service, a thin `pipe` client and one SQLite ledger on native Linux storage. Initially support global/per-mod off/on, compact show, audit receipts, idempotent launch requests, and reserve/settle/void for the owner-granted judge look. Keep existing scheduling policy.

    Route every enabled launch family through it at cutover; temporarily disable families that cannot yet comply. Keep all new starts off during the cutover. Maintain existing independent holds until their semantics are explicitly migrated.

    Acceptance should require: both pause-race orderings; two callers competing for one look; duplicate request/settlement/void; unavailable authority; crash before and after systemd start; and accurate status from two clones. Prove with harmless payloads before resuming product work.

    Add the remaining resource families next. Add dependency-aware undo and evidence invalidation before promising “undo any act.” Add forecast after extracting the shared planner. Keep D as tested containment.

    **Confirm:** those invariants pass and the live authority reports complete coverage of enabled launch paths. I would accept that evidence over the proposed one-hour deadline.
