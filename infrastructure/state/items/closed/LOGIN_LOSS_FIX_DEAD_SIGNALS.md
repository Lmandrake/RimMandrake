# LOGIN_LOSS_FIX_DEAD_SIGNALS

Owner: "I'm noticing we KEEP not making the system capable to respond to situations like this, wasting time and work."

Census, 10-28 22:00Z to 10-31, journal + ops_watch alarms_log. Scratch: D:\ClaudeWork\rimmandrake\dead_signals\census.txt.
L = landed in, A = who acted before this item. Hours: MEASURED from timestamps unless marked.

| # | signal | L | A | hours lost | now |
|---|---|---|---|---|---|
| 1 | account_usage `auth status failed`, 31 readings | series.jsonl, ops counted ESTIMATE | nobody | 8.1 (05:57-14:05Z, one outage, shared by 2-4) | login_watch probe, 4 min |
| 2 | unwakeable:FOUNDRY ×218 | journal | nobody | same 8.1 | routed (9f35242198), window restarted |
| 3 | role:Operations/Producer:failed, auth text ×3 | item notes | nobody; alarm + event limits spent | ESTIMATE ~7 h of limit-held runs (07:03-14:08Z) | slot given back, Conductor log, launches held |
| 4 | cap:FOUNDRY ×25 | journal only | nobody | 5.3 span, ESTIMATE lost | note + log |
| 5 | account:switch:* ×82 | 7 notes, recommend only | nobody can act | UNMEASURED (owner HOLD by design) | unchanged |
| 6 | TIMER_FAILED crossings | OPS item | Operations proposes, nobody repairs | 47 span, no work lost measured | REMAINS (OPS_TIMER_REPAIR) |
| 7 | STEVE_STALL file_failed ×3 | alarms_log only | nobody | UNMEASURED | REMAINS |
| 8 | ops flags (flow.untriaged_findings 128→143) | digest | read, no action | UNMEASURED | REMAINS |
| 9 | idle_full_queue:FOUNDRY eps 3 | Conductor log | read, no action | 7.0 span | other helper's re-ring work |
| 10 | role:*:overbudget, overtime, scope ×23+ | item notes | nobody | UNMEASURED | failed routed; rest REMAIN |
| 11 | publish failures ×23 (dirty tree 18, push 3, rebase 4) | journal | self-retry next ingest | ESTIMATE under 1 | REMAINS |
| 12 | `hold` owner idle UNMEASURED ×6, `skip` blind agents | journal | nobody | 0 observed | REMAINS |
| 13 | dead:*, cap:recover, peek:, role no key/cap/observer | journal only | nobody | 0, never fired | note + log |
| 14 | tick:raised, tick:unreserved | journal only | nobody | 0, never fired | raised carried to next tick's alarm; unreserved REMAINS |

Dead signals: 14 classes. Automatic switch is built and gated on D:\ClaudeWork\rimmandrake\switching_plan\HOLD, which only the owner lifts.
