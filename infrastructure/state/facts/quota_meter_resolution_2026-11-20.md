# Quota meter resolution: is any source finer than a whole percent? (2026-11-20, about 6 AM PST)

## Answer

No provider source is finer than a whole percent, for the three Claude accounts or for Codex. [measured]

- Claude: the usage endpoint, the response headers and `/usage` all carry the same whole percent. The values look
  fractional (`83.0`, `0.83`) but only because of their format. [measured, one call per account, 2026-11-20]
- Codex: the usage endpoint and all 13,557 `used_percent` values in the local rollout files are whole numbers. [measured]
- The only way to get tenths is our own arithmetic: local weighted tokens between two meter steps. One percent of
  an account's week is about 4 to 5 million weighted tokens (weighted_v2). The figure varies by about +-15% from day to
  day. [measured] It sees only this machine's use. [measured]
- Not looked at: the claude.ai and ChatGPT usage web pages (see "Could not look").

## Per-meter sources

Each line: what it gives, resolution, freshness, cost.

### Claude accounts (`system`, `lukas`, `steven`; same result for each)

1. `GET https://api.anthropic.com/api/oauth/usage` (the CLI's own `/usage` source; the path is in the CLI binary,
   header `anthropic-beta: oauth-2025-04-20`). It gives `seven_day.utilization` and `limits[].percent`.
   Resolution: whole percent. Example: `"utilization":83.0` and `"percent":83` (system, week resets 2026-11-25).
   [measured] Fresh: live. Cost: no model call. It uses the account's own access token with no refresh, so only
   a token valid for 15+ more minutes is safe to use (the rule `account_usage.py` already follows). The
   `five_hour` field was `null` for all three (no session window open). [measured]
2. Response headers on an ordinary `/v1/messages` request: `anthropic-ratelimit-unified-7d-utilization` and
   `-5h-utilization`, `-7d-reset` (Unix seconds). Resolution: a fraction with two decimals, so one percent.
   Examples: `0.83` (system), `0.49` (steven), `0.0` (lukas). The `/usage` percentages above were identical on
   the same minute. [measured] The CLI's own documentation string says "two decimals" too. [measured]
   Cost: one 1-token Sonnet 5.5 call per account (done once, this run). It adds nothing over source 1.
3. `/usage` screen via `claude -p /usage` (what `account_usage.py` parses today): whole percent. 8,749 of 8,749
   stored readings are whole numbers. [measured by the Conductor]
4. Statusline JSON `rate_limits.*.used_percentage` (the CLI schema, same server data as source 1): whole percent
   by construction. Not read live this run. [guess ~85%: same figure as source 1]
5. Files under `~/.claude` and `~/.claude-accounts/*`: no usage meter cache found. `capture.json`, `health.json` and
   `account_usage.json` hold login state and our own series, not a provider reading. [measured, listing only]
6. Local arithmetic (transcripts times `MODEL_PRICES`): see "Calibration". Resolution: whatever we compute;
   fresh to the last transcript line; cost: reading local files.

### Codex

1. `GET https://chatgpt.com/backend-api/wham/usage` (endpoint named in the installed `codex` binary 0.167.0;
   auth from `~/.codex/auth.json`, the account's own token). It gives `rate_limit.primary_window.used_percent`,
   `limit_window_seconds`, `reset_after_seconds`, `reset_at`. Resolution: whole percent. Example:
   `"used_percent": 47` (plan `prolite`, 604,800 s window). [measured] Fresh: live. Cost: no model call.
2. Rollout files `~/.codex/sessions/**/rollout-*.jsonl`, key `rate_limits.primary.used_percent` (what
   `csuite_codex_limits.readings` and `ops_watch.c_codex` parse today): whole percent, 13,557 of 13,557 values
   end in `.0`. Latest: `47.0`, 2026-11-20 08:21 UTC. [measured] Fresh: as of the last Codex turn on this machine
   (the collector marks it a floor after 6 h). Cost: reading local files.
3. `codex` CLI status output and response headers: the rollout `rate_limits` record is that data, so no
   finer figure exists there. [guess ~80%] The CLI has no non-interactive status command. [measured: `codex --help`]
4. Local arithmetic for Codex: not done (see "Not done").

## Calibration: weighted tokens per one percent point (Claude, this machine only)

Method: 320,563 deduplicated assistant requests in `~/.claude/projects` since 2026-10-26, each priced with
`MODEL_PRICES` (weighted_v2). Matched to `series.jsonl` readings with `machine=archmagi`, method "live login", the
same week window, gap of 3 h or less, and the account the live account on this machine throughout (the `use`
events in `~/.claude-accounts/log.jsonl`). One step of exactly +1 is a noisy sample, because the true rise lies
between 0 and 2 points. So pool before you trust a figure. [measured]

| account | intervals with a rise | pooled weighted tokens per point | steps of +1: median (p10 to p90) | per-day pooled, days with 5+ points: median (min to max, sd) |
|---|---|---|---|---|
| system | 186 | 4.6 M | 2.94 M (1.13 to 5.00) | 4.45 M (3.63 to 5.92, sd 0.65), 12 days |
| lukas | 146 | 5.1 M | 3.59 M (1.64 to 5.47) | 5.08 M (3.91 to 5.75, sd 0.53), 9 days |
| steven | 85 | 4.0 M | 2.78 M (0.92 to 5.46) | 4.16 M (2.39 to 5.21, sd 0.77), 8 days |

Reading it:
- Step-by-step the figure is useless (p10 to p90 spans a factor of 4 to 6), as expected from a rounded meter.
- Pooled per day it is stable to about +-15% (sd divided by median: 15%, 10%, 19%).
- The pooled figure is biased low-count: the steps of +1 are skewed low because the meter rounds. The pooled
  ratio is the better one. [guess ~70%]
- Local tokens miss everything the same account spends on other machines (the series shows `lukas` on
  `stevedesktop`) and any use outside Claude Code, and list-price weights are not the provider's quota weights.
  So the ratio is an upper bound on cost per point, and drifts when the model mix changes. [measured that other
  machines exist; the size of their share: UNMEASURED]
- Consequence: within one whole-percent step, an estimate of tenths is good to roughly +-0.15 of a point only on
  a day of pooled use, and worse for an hour. [guess ~60%]

## Could not look

- The claude.ai settings/usage page and the ChatGPT/Codex usage page. The `chrome-mine` MCP server failed to
  connect in this run ("Connection closed"), and I did not try the `wsl-windows-plumbing` PowerShell route in this
  one pass. Status: could not look. [guess ~75%: these pages show the same whole percent as the API they call; the Claude page calls
  `/api/oauth/usage` per the CLI's own documentation string]
- The CLI statusline payload live (read from the schema only).

## Not done

- Codex calibration (weighted tokens per point). Codex has no per-request token ledger in our weighted_v2 table; it
  would need a separate unit. UNMEASURED.
- Other machines' share of each account's use.

## Design (do not build yet; the owner agreed to 1% for now)

If tenths between steps are wanted, add a derived field only, never replace the measured percent:
`account_usage.py` reads each account's last two MEASURED readings in one window (file `series.jsonl`, field
`week_pct_used`), sums weighted tokens from `~/.claude/projects/**/*.jsonl` since the last step (priced by `MODEL_PRICES`),
divides by the account's pooled weighted tokens per point over the last 7 days, and adds the result to the reading,
clipped to below the next whole percent, labelled `ESTIMATE` with its +-15% basis. No provider source is read.

Acceptance test, one line: replay `series.jsonl` on archmagi live intervals and require the estimated percent to lie
within 0.5 point of the next measured reading for at least 80% of intervals, and fail on a planted 2x ratio.
Acceptance test: not yet run (it needs the code above).
