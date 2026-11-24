#!/usr/bin/env python3
"""role_launch.py — the Dispatcher's role launcher (item DISPATCHER_BUILD_ROLE_LAUNCH_FROM_SCHEDULE; spec
design/RimMandrake/dispatcher_design_2026-10-26.md §3, §6). dispatcher.decide() calls decide_roles(); dispatcher.execute()
calls launch() / stop(). A program: it decides nothing the schedule and the role files do not say.

What it runs: every role in dispatcher_schedule.json `roles` that is `enabled` AND carries the launch keys
(LAUNCH_KEYS: instructions, seat, clone, model, ledger_item). An enabled role without them
is still an ALARM, as in v3.0: switching on a role nobody can run must be loud.

When: the role's clock slots — `quick_checks_local` (Conductor) or `runs_local` (Operations), local "HH:MM" — each
once per local day, launched in the first tick at or after the slot and no later than `slot_late_s` after it (a
missed slot is journaled, never run late). The slot equal to `economy_pass_local` is the economy pass, which carries
that slot's running check with it. A role with `after_role` (Conductor -> Operations) launches a slot only after that role's own
scheduled run for the slot it follows (08:00 -> 07:30, 20:00 -> 19:30; never an alarm run or yesterday's late run)
finished done and none is going (after_ready); it is decided after that role in each tick. Operations
also runs once per OPEN ops_watch alarm crossing, and once per worsening of one (<key>@worse<n>) (`alarm_runs`): `alarms_seen` is pruned to the alarms open now, so
one that clears runs again when it re-crosses (review W, W1); alarms already open when the role is first enabled run
once too (no baseline). One alarm run covers every open alarm not yet run, and alarm runs are at least
`alarm_run_gap_s` (ALARM_RUN_GAP_S) apart; alarms are read only from a MEASURED reading whose alarms dict is readable
(a blind tick prunes nothing and runs no alarm). An OPEN alarm whose reading is already back under the line
(clear_seen >= 1) buys no alarm run until it re-breaches (recovering_keys). A run of a mode in `model_by_mode` gets
that model (Operations' alarm runs: sonnet), the message of an alarm run carries its alarm rows and
`scope_by_mode[mode]`, and `launch_args` adds narrowing claude flags (LAUNCH_ARGS_OK) -- OPS_ROLE_SHRINK_RUN_COST.
One run per role at a time.

Weekdays (item DISPATCHER_BUILD_WEEKDAY_AND_EVENT_TRIGGERS): a slot may name its days, "Wed 09:00" or
"Mon,Thu 10:00" (parse_slot; an unreadable slot is an alarm and the role does not run).

Gates, in order, each journaled (and each refusal an ALARM when it needs a human):
  1. off switch: the role's `off_file` exists (its first line is the reason) -> skip the slot, no alarm.
  2. the ops_watch reading (status.json, `ops_status`): REFUSED with an alarm when it is missing, unreadable, older
     than `ops_stale_s` (45 min, conductor.md), its account cannot be resolved, or the account's runway or
     week_left_pct point is UNMEASURED. (conductor.md's table puts UNMEASURED/stale in AMBER; the build brief of
     2026-10-27 says refuse: refusing is the stricter of the two, so a quick run never launches on a blind reading.)
     EXCEPT a role with `degraded_reading_ok: true` (EVERY role by default since owner 2026-11-02, token limits
     advisory everywhere, TOKEN_LIMITS_TAME_BARK_NO_BITE; first Operations, the role that reads the watch; items
     OPERATIONS_FIX_RUNS_BLIND_WHEN_STALE and the 2026-11-01 brief): it launches with a
     noted alarm, its message marking the reading UNMEASURED and saying to diagnose the watch first. Caps and the
     account gate still apply; only a role that sets it false is still refused.
     The account is the switcher-registry label whose email is the one this machine is logged in as
     (account_usage.registry()/live_email()): no account is named here.
  3. caps: the run's budget = its cap; it is REFUSED (alarm) when today's spend plus that budget
     passes `daily_token_cap`. Today's spend = tokens of finished runs (measured from the transcript when the result
     is missing) + the full budget of runs still going. A role with `caps_advisory: true` (EVERY role by default
     since owner 2026-11-02: "Nothing gets killed or stopped for that"; first Operations, e7069d65ba) is never refused,
     held, skipped or shrunk by a budget, daily cap or daily alarm-run count: overspend raises an immediate alarm
     instead (overspend_day, overbudget).
  4. account (dispatcher.account_gate, account_pick.py): the schedule's `account_pick` rule, asked at the moment of
     release; a SWITCH pick holds the launch (journaled once per slot) until the machine is switched or the slot is
     missed. The launch records the account it runs on.

Tokens: a finished run's `claude -p --output-format json` usage, ALL FOUR fields (input, cache_creation,
cache_read, output), per model, each weighted by that model's list price for it (MODEL_PRICES, run_tokens: unit
weighted_v2, one uncached Opus 5.5 input token = 1, so a cap measures cost, not context re-reads, and figures of
different models compare; ROLE_CAPS_REMEASURE_ON_REAL_RUNS, RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT). The
result's modelUsage (the whole process, subagents included) is read when present, else its usage as the run's model;
a model not in the table leaves the run UNMEASURED with the name. Every cap, budget, daily spend and overbudget
alarm here is in these units; the raw sum is kept beside it on the run as `raw_tokens`. A run over its budget is an ALARM after the fact: `claude -p` has no
token stop and nothing here stops a run at its token budget: the budget is checked on its result (the dollar
run_budget_usd stop is spend_watchdog.py's, from outside). No role is told its budget or spend (owner 2026-11-16); only a
`token_aware` role (Operations, the Conductor) is told the account's reading in its launch message; every other role is
token-blind and is told neither (owner 2026-10-27; review T, F1/F2). A run still going after
`run_max_s` is stopped (its claude_bounded scope and its unit) with an alarm; it stays `running` and the stop is
re-issued each tick until systemd says the unit AND its claude_bounded scope are inactive/failed (claude lives in the
scope, outside the unit; the scope is resolved while the unit runs). supervise_roles() does this for every persisted
run before PAUSE, a blind tick or a disabled role can end the tick (review round Q).

How it launches (proved 2026-10-27, D:\\ClaudeWork\\rimmandrake\\role_launch_2026-10-27\\proof\\RESULT.md): as its OWN
transient user service, `systemd-run --user --collect --unit rm-role-<name>-<epoch>`, which runs
`claude_bounded.sh -p <prompt> --model <alias> --output-format json` in the role's clone. The dispatcher tick is a
oneshot unit whose cgroup systemd kills when it exits; a child started there (even setsid) died before
claude_bounded made its scope, while the transient unit ran on and finished. PATH gets claude's directory: the user
manager's PATH has no ~/.local/bin. The model is the schedule's alias; claude resolves it from its own settings
(the GenAiSwitch route vars, genai_env.py's MODEL_VARS), and the id actually used is read back from the result.

Every launch, refusal, finish and stop is a dispatcher action: journaled, and noted on the role's `ledger_item`
(an alarm-run's note goes on its alarm item) when --apply. Dry-run launches nothing.
Names no host, account or model id.
"""
import calendar
import hashlib
import json
import math
import os
import re
import shlex
import signal
import subprocess
import sys
import time
import uuid
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_tmp  # noqa: E402  (the run's own TMPDIR: TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP)
import role_clones  # noqa: E402  (a role's own clone: RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES)

AUTH_BACKS_PER_DAY = 2
OVER_REPEAT, OVER_WINDOW_S = 3, 7 * 86400
# overbudget_repeat is a RATE (OPERATIONS_RUN_FIX_HALF_A_MILLION_HABIT): at least OVER_REPEAT overruns in the window
# AND at least OVER_RATE of the role's measured finished runs there. Operations runs ~25 times a day, so a bare
# "3 in 7 days" fired on any budget short of its maximum; a role whose budget sits near p90 overruns ~10%.
OVER_RATE = 0.2
AUTH_TEXT_MAX = 400     # an auth death's result IS the short API error; a long result merely quotes one
AUTH_RX = re.compile(r"failed to authenticate|oauth session expired|login expired|please run /login|"
                     r"authentication_failed", re.I)
# A run the ACCOUNT ended (ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS; owner 2026-11-04: "You could just poke the agents
# to continue where they were."): claude -p's result says is_error, terminal_reason api_error, api_error
# usage_limit_reached / api_error_status 429 ("You've hit your weekly limit · resets 12pm (America/Los_Angeles)",
# measured on 9 runs of the 2026-11-04 outage). Not a role failure: no role:<name>:failed. After real usage it is
# RESUMABLE: rs["resume"] holds its session, and once the reset its message names has passed (or RESUME_WAIT_S when it
# names none) and the account gate goes, the next tick relaunches it on the same unit template, slice and budget with
# `--resume <session>` and a continue prompt, at most RESUME_MAX times in a chain. A 0-usage death stays a fresh run
# on the normal schedule (it did no work to keep).
ACCOUNT_ERRORS = ("usage_limit_reached", "rate_limit", "rate_limit_error", "overloaded_error")
LIMIT_RX = re.compile(r"hit your (?:\w+ )?limit|usage limit|rate limit", re.I)
# budget: danger=a run resumes on a dead account at every tick; ends no work: a wait before the next try
RESUME_WAIT_S = 3600        # no reset named: try again after an hour (a still-dead account just waits again)
RESUME_MAX = 3              # resumes in a row that did no work; past it the run is given up, said. A leg that did work
#                             and then ended on the account spends none (failure_class: ACCOUNT LIMIT). The danger is a
#                             login that fails only for role runs (10-30: three such runs spent the day's limits)
# A Cloudflare challenge page ("Please run /login · API Error: 403 Attention Required! | Cloudflare", 2026-11-13) is
# transient, not a dead login: a run that did work and died on one is resumed ONCE after CLOUDFLARE_RETRY_S; one that did
# none gets its slot back (auth_failed_back). RIMMANDRAKE_RESCUE_STRANDED_CONDUCTOR_CLOUDFLARE_SAID_LOGIN.
CLOUDFLARE_RETRY_S = 120
CLOUDFLARE_RX = re.compile(r"attention required!?\s*\|\s*cloudflare", re.I)    # = login_watch.CLOUDFLARE_RX
# budget: danger=a resume nobody can launch stays for ever; ends no work: the resume is dropped, said
RESUME_TTL_S = 2 * 86400    # a resume not launchable for this long is dropped, said

LAUNCH_KEYS = ("instructions", "seat", "clone", "model", "ledger_item")
# Token limits are ADVISORY for every role (owner 2026-11-02, TOKEN_LIMITS_TAME_BARK_NO_BITE: "Please make token limits
# advisory at this time everywhere. Nothing gets killed or stopped for that, but it might call attention from another
# agent (Conductor, Operations) to investigate and THAT agent may determine it needs to be killed for evidence-based
# reasons."): caps_advisory and degraded_reading_ok default true, so no budget, daily cap or blind runway reading
# refuses, holds or shrinks a run; overspend_day / overbudget / role:<name>:ops raise the attention line instead. A role
# that sets either key false is back on the strict gates (kept, and tested, for when he lifts this).
ROLE_DEFAULTS = {"slot_late_s": 3600, "run_max_s": 1800, "caps_advisory": True, "degraded_reading_ok": True}
ALARM_WORSE_SEP = "@worse"             # an alarm re-raised for getting worse is a new key, so it earns a new run: <key>@worse<n>
# extra claude flags a schedule entry may add (`launch_args`): only ones that narrow what a run loads. A role run
# that uses no MCP tool drops every MCP server's tools and instructions (OPS_ROLE_SHRINK_RUN_COST: 56,333 -> 48,098
# tokens of start context, re-read every turn); no flag that touches permissions, settings or auth.
LAUNCH_ARGS_OK = frozenset(("--strict-mcp-config", "--disable-slash-commands", "--exclude-dynamic-system-prompt-sections"))
# `slim_start: true` (RIMMANDRAKE_SLIM_OPERATIONS_START_PACKAGE_HALF_IS_UNRELATED, owner by card 2026-11-19, "Slim the
# start package"): the run's --settings also drop the owner's personal CLAUDE.md (written for his interactive seats) and
# auto-memory. Measured 2026-11-19 by probe: `--setting-sources project,local` does NOT drop ~/.claude/CLAUDE.md (it
# loads as a parent-directory file) and would drop the user settings' promptCacheTtl and plugins; `claudeMdExcludes`
# in --settings does drop it. The project CLAUDE.md stays.
def user_claude_mds():
    """The user-level CLAUDE.md paths a slim run excludes: ~/.claude/CLAUDE.md, and CLAUDE_CONFIG_DIR's if set."""
    out = [os.path.join(os.path.expanduser("~"), ".claude", "CLAUDE.md")]
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    if cfg and os.path.join(cfg, "CLAUDE.md") not in out:
        out.append(os.path.join(cfg, "CLAUDE.md"))
    return out


def slim_settings():
    return {"claudeMdExcludes": user_claude_mds(), "autoMemoryEnabled": False}


ROLE_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def doc_sections(path, headings):
    """-> the `## ` sections of a markdown file whose heading text starts with each of `headings`, in that order, as
    one text. Raises ValueError naming a heading the file lacks (or one that matches twice), OSError if unreadable."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    starts = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    out = []
    for h in headings:
        hit = [i for i in starts if lines[i][3:].startswith(h)]
        if len(hit) != 1:
            raise ValueError("%s: heading %r matches %d sections, not 1" % (path, h, len(hit)))
        end = next((j for j in starts if j > hit[0]), len(lines))
        out.append("\n".join(lines[hit[0]:end]).strip())
    return "\n\n".join(out)


def launch_scope(job):
    """Pure. The `inline_by_mode` key of a due job: "incident" for an incident-only run (run_now_job set its
    `incident`), else its mode; an incident run that covers a slot (`covers`) is that slot's full run, so its mode."""
    return "incident" if job.get("incident") and not job.get("covers") else job["mode"]


def inline_instructions(role, scope, root=None):
    """-> (text, None) with the sections `inline_by_mode[scope]` names from the role's instructions, or (None, None)
    when the scope inlines nothing, or (None, cause) when they could not be read: the launch then says so and the run
    reads the whole file (an Operations run is never refused for a doc; RIMMANDRAKE_SLIM_OPERATIONS_START_PACKAGE_HALF_IS_UNRELATED)."""
    heads = (role.get("inline_by_mode") or {}).get(scope)
    if not heads:
        return None, None
    path = os.path.join(root or ROLE_REPO, role["instructions"])
    try:
        return doc_sections(path, heads), None
    except (OSError, ValueError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
MODELS_OK = ("opus", "sonnet")         # model_by_mode: Sonnet is the floor (Agent_Policy; Haiku banned 2026-10-31)
ALARM_KEY_PREFIX = "alarm:"            # an Operations-only alarm (no ledger item) in alarms_seen: "alarm:<aid>" (V2)
ALARM_RUN_GAP_S = 3600                 # at least this long between two alarm runs of a role (review W, W1)
# budget: danger=a dead ops reading read as current; ends no work: the launch gate says that the reading is old
OPS_STALE_S = 45 * 60
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")      # time.localtime().tm_wday order
ACTIVE = ("active", "activating", "deactivating", "reloading")
# the only states that end a run; anything else ("unknown", a failed query) is busy. "not-found" is a unit or scope
# systemd CONFIRMS it has no record of (collected by --collect, or never created because a pre-step failed first):
# absent, so ended() still needs the scope terminal and the marker scan empty (ROLE_UNITSTATE_FIX_GHOST_RUNS_NEVER_LEAVE)
TERMINAL = ("inactive", "failed", "not-found")
NOT_FOUND_RX = re.compile(r"could not be found|not found|not loaded|no such unit", re.I)
FUTURE_TOL_S = 300                     # a reading stamped further ahead than this is a clock fault, not fresh
USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
# The ONE token measure (weighted_v2, RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT; the owner, 2026-11-16: "I
# want you to properly weight tokens by the model as well so they are more comparable."): each usage field weighted
# by THAT model's own list price for it, divided by the list price of one uncached REF_MODEL input token. One
# weighted token = the list cost of one uncached Opus 5.5 input token, whatever model spent it.
# MODEL_PRICES is the one table (list $ per million tokens: input, 5-minute cache write, 1-hour cache write, cache
# read, output). Source: Anthropic's pricing page, fetched 2026-11-16 (platform.claude.com/docs/en/about-claude/
# pricing.md; copy D:\ClaudeWork\rimmandrake\weighted_v2\pricing_2026-11-16.md). Checked against the CLI's own
# modelUsage costUSD: every costBasis "list" entry of 177 in dispatcher\detached\*.out.json (Opus 5.5 163, Sonnet 5.5
# 12, Fable 5.2 2) matches to 1e-6 (selftest_weighted_v2_by_model V2); the two Fable 5.2 entries with costBasis
# "unknown" are priced by the CLI at Opus 5.5 rates, so a run's costUSD is not trusted for spend. Haiku 5.5 is tiered
# by prompt size and its <=100K-token tier is the row here: 3 of 3 measured entries match it exactly (the residue is
# web-search fees, $10 per 1,000 searches, which weigh no tokens); its >100K tier is 5x and would be undercounted.
# A model not in the table raises UnknownModel by name: there is no fallback weight. Was weighted_v1 (to 2026-11-16):
# weights relative to the SAME model's input token (TOKEN_WEIGHTS below, kept for converting old records), so an
# Opus and a Fable figure were not comparable and Opus 5.5 cache reads weighed 0.1 where their price is 0.05.
TOKEN_UNIT = "weighted_v2"             # stamped on each finished run: the unit of its `tokens`
REF_MODEL = "claude-opus-5-5"
PRICE_FIELDS = ("input_tokens", "cache_write_5m", "cache_write_1h", "cache_read_input_tokens", "output_tokens")
MODEL_PRICES = {m: dict(zip(PRICE_FIELDS, (Fraction(x) for x in p))) for m, p in {
    "claude-fable-5-2": ("8", "10", "16", "0.20", "40"),
    "claude-fable-5-1": ("10", "12.50", "20", "0.25", "50"),
    "claude-fable-5": ("10", "12.50", "20", "1", "50"),
    "claude-opus-5-5": ("4", "5", "8", "0.20", "20"),
    "claude-opus-5": ("5", "6.25", "10", "0.50", "25"),
    "claude-opus-4-8": ("5", "6.25", "10", "0.50", "25"),
    "claude-opus-4-7": ("5", "6.25", "10", "0.50", "25"),
    "claude-opus-4-6": ("5", "6.25", "10", "0.50", "25"),
    "claude-opus-4-5": ("5", "6.25", "10", "0.50", "25"),
    "claude-sonnet-5-5": ("2", "2.50", "4", "0.10", "10"),
    "claude-sonnet-5": ("2", "2.50", "4", "0.20", "10"),
    "claude-sonnet-4-6": ("3", "3.75", "6", "0.30", "15"),
    "claude-sonnet-4-5": ("3", "3.75", "6", "0.30", "15"),
    "claude-haiku-5-5": ("0.10", "0.125", "0.20", "0.01", "0.50"),
    "claude-haiku-4-5": ("1", "1.25", "2", "0.10", "5"),
}.items()}
# Standard-speed, global-inference rates: fast mode's premium and the US-inference 1.1x are price modifiers, not
# tokens, and are not weighed (every run in the records reads usage.speed "standard").
# weighted_v1, for converting records stamped with it (tokens_v2) and nothing else.
TOKEN_WEIGHTS = {"input_tokens": Fraction(1), "cache_write_5m": Fraction(5, 4), "cache_write_1h": Fraction(2),
                 "cache_read_input_tokens": Fraction(1, 10), "output_tokens": Fraction(5)}
# run-now (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE): a one-shot run asked for by hand, held in the dispatcher state as
# st["roles"][R]["run_now"] and launched by the next tick through every gate a scheduled run passes. A request the
# ticks could not launch for this long (busy, account hold) expires, said; refusals (off, ops, cap) consume it.
# budget: danger=a hand request starts a run that nobody waits for any more; ends no work: the request expires, said
RUN_NOW_TTL_S = 3600
RUN_NOW_MODES = ("run", "quick", "economy")
# The one alias table (design/specs/2026-11-22-run-spend-and-model-alias/boundary.md): the variable that names each
# alias's model id, as genai_env.py's MODEL_VARS (~/dev/Lodestar/bin/lib/genai_env.py) names it. resolve_model prices an alias through it; launch_model gives the id a tier launches as.
MODEL_VARS = {"fable": "ANTHROPIC_DEFAULT_FABLE_MODEL", "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
              "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL", "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL"}
TIERS = ("fable", "opus", "sonnet")   # the owner's ladder 2026-11-12: Sonnet is the floor; Haiku is banned (2026-10-31)
# With no variable set (a subscription), the CLI resolves these aliases itself. It resolved "fable" to claude-fable-5-1
# (measured 2026-11-12 and 2026-11-16), and the ladder means Fable 5.2, so a Fable launch needs its variable.
CLI_ALIASES = ("opus", "sonnet")
SETTINGS = os.path.expanduser("~/.claude/settings.json")


# ---------------------------------------------------------------- paths and readings

def wsl_path(p):
    """D:\\x\\y -> /mnt/d/x/y (schedule paths are written Windows-native for the owner)."""
    if p and len(p) > 2 and p[1] == ":" and p[2] in "\\/":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p


def ops_status_path(sch):
    if sch.get("ops_status"):
        return wsl_path(sch["ops_status"])
    for m in sch.get("measure") or []:
        if m.get("name") == "ops_watch" and m.get("out"):
            return os.path.join(wsl_path(m["out"]), "status.json")
    return None


def utc_epoch(iso_s):
    try:
        return calendar.timegm(time.strptime(iso_s, "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        return None


def finite(v):
    """A real number: int/float, not bool, not NaN/inf (Python's json accepts NaN and Infinity)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def ops_reading(status, account, now, stale_s=OPS_STALE_S, model=None):
    """Pure. status = parsed status.json (or None), account = resolved label (or None).
    -> {"state": "MEASURED", "account", "runway", "runway_m", "week_left", "week_left_m", "at", "week_limit"}
       or {"state": "UNMEASURED", "why"}.
    model = the run's model (alias or id): week_left is then the LOWER of the all-models point and that model's own
    weekly limit (`accounts.<label>.model_week_left_pct.<scope>`, ops_watch), week_limit names which one; a model
    with no such point reads the all-models figure (RIMMANDRAKE_READ_FABLE_WEEKLY_METER_USAGE_LINE_NEVER_SHOWED)."""
    if not isinstance(status, dict):
        return {"state": "UNMEASURED", "why": "ops_watch status.json missing or unreadable"}
    at = utc_epoch(status.get("at"))
    if at is None:
        return {"state": "UNMEASURED", "why": "ops_watch status.json has no readable 'at'"}
    if at - now > FUTURE_TOL_S:
        return {"state": "UNMEASURED", "why": "ops_watch status.json 'at' %s is %d min in the FUTURE (clock or file "
                "wrong)" % (status.get("at"), (at - now) // 60)}
    if now - at > stale_s:
        return {"state": "UNMEASURED", "why": "ops_watch status.json is STALE: at %s, %d min old (> %d)"
                % (status.get("at"), (now - at) // 60, stale_s // 60)}
    if not account:
        return {"state": "UNMEASURED", "why": "the account this machine runs on is not resolved (registry/live email)"}
    pts = status.get("points") or {}
    if not isinstance(pts, dict):
        return {"state": "UNMEASURED", "why": "ops_watch status.json 'points' is not a mapping"}
    out = {"state": "MEASURED", "account": account, "at": status.get("at")}
    for key, name in (("runway", "runway"), ("week_left_pct", "week_left")):
        p = pts.get("accounts.%s.%s" % (account, key)) or {}
        if not isinstance(p, dict):
            p = {}
        if p.get("m") not in ("MEASURED", "ESTIMATE") or not finite(p.get("v")):
            return {"state": "UNMEASURED", "why": "accounts.%s.%s is %s%s%s" % (
                account, key, p.get("m") or "absent", (" (%s)" % p["why"]) if p.get("why") else "",
                "" if p.get("m") not in ("MEASURED", "ESTIMATE") else ", value %r not a finite number" % (p.get("v"),))}
        out[name], out[name + "_m"] = float(p["v"]), p["m"]
    out["week_limit"] = "all models"
    if model:
        import account_usage as AU
        pre = "accounts.%s.model_week_left_pct." % account
        scopes = {k[len(pre):]: v for k, v in pts.items() if k.startswith(pre) and isinstance(v, dict)}
        scope = AU.scope_for(model, scopes)
        p = scopes.get(scope) or {}
        if scope and p.get("m") in ("MEASURED", "ESTIMATE") and finite(p.get("v")) and float(p["v"]) < out["week_left"]:
            out["week_left"], out["week_left_m"], out["week_limit"] = float(p["v"]), p["m"], scope
    return out


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_role(role):
    """Raises ValueError naming the first schedule value decide_roles cannot use (review round U, N5): a role with a
    bad value is skipped with an alarm, never allowed to raise through the whole tick."""
    if role.get("runner", "claude") not in ("claude", "codex"):
        raise ValueError("runner must be claude or codex")
    if "throttle_bands" in role:
        raise ValueError("throttle_bands are retired (the Conductor, 2026-11-23; nothing reads them): remove the key")
    if "slot_when" in role:
        raise ValueError("slot_when is retired with the Arbiter (CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED): remove the key")
    if "cover_window_s" in role and not (_num(role["cover_window_s"]) and role["cover_window_s"] >= 0):
        raise ValueError("cover_window_s %r is not a number >= 0" % (role["cover_window_s"],))
    if "pre_launch_max_s" in role and not (_num(role["pre_launch_max_s"]) and role["pre_launch_max_s"] > 0):
        raise ValueError("pre_launch_max_s %r is not a number > 0" % (role["pre_launch_max_s"],))
    for k in ("run_token_cap", "quick_token_cap", "economy_token_cap", "daily_token_cap", "incident_token_cap"):
        if role.get(k) is not None and not (_num(role[k]) and role[k] >= 0):
            raise ValueError("%s %r is not a number >= 0" % (k, role[k]))
    # run_budget_usd: the HARD per-run spend stop, enforced from outside by spend_watchdog.py (was claude's --max-budget-usd
    # until owner 2026-11-16: the agent is never told its spend) (owner 2026-11-12: "Don't let any burn go
    # to 90M this time ok?"); the token caps above stay advisory
    if role.get("run_budget_usd") is not None and not (_num(role["run_budget_usd"]) and role["run_budget_usd"] > 0):
        raise ValueError("run_budget_usd %r is not a number > 0" % (role["run_budget_usd"],))
    la = role.get("launch_args", [])
    if not (isinstance(la, list) and all(isinstance(x, str) and x in LAUNCH_ARGS_OK for x in la)):
        raise ValueError("launch_args %r: each must be one of %s" % (la, ", ".join(sorted(LAUNCH_ARGS_OK))))
    mbm = role.get("model_by_mode", {})
    if not (isinstance(mbm, dict) and all(isinstance(v, str) and v in MODELS_OK for v in mbm.values())):
        raise ValueError("model_by_mode %r: each model must be one of %s" % (mbm, ", ".join(MODELS_OK)))
    sbm = role.get("scope_by_mode", {})
    if not (isinstance(sbm, dict) and all(isinstance(v, str) for v in sbm.values())):
        raise ValueError("scope_by_mode %r is not a mapping of mode to text" % (sbm,))
    ibm = role.get("inline_by_mode", {})
    if not (isinstance(ibm, dict) and all(isinstance(v, list) and v and all(isinstance(h, str) and h for h in v)
                                          for v in ibm.values())):
        raise ValueError("inline_by_mode %r is not a mapping of mode to a list of headings" % (ibm,))
    if "slim_start" in role and not isinstance(role["slim_start"], bool):
        raise ValueError("slim_start %r is not true or false" % (role["slim_start"],))
    if "caps_advisory" in role and not isinstance(role["caps_advisory"], bool):
        raise ValueError("caps_advisory %r is not true or false" % (role["caps_advisory"],))
    for k in ("slot_late_s", "run_max_s"):
        # the time bounds are never optional: None would override ROLE_DEFAULTS and crash supervision on every tick;
        # 0 would stop every run at once (review V, V3)
        if not (_num(role.get(k)) and role[k] > 0):
            raise ValueError("%s %r is not a number > 0" % (k, role.get(k)))
    # decide_roles reads only TODAY's slots: a late window past local midnight would drop the slot silently after
    # midnight (neither launched nor journaled missed). Refuse it loudly (review night).
    for t in role.get("quick_checks_local") or role.get("runs_local") or []:
        h, m = parse_slot(t)[1].split(":")
        if (int(h) * 60 + int(m)) * 60 + role["slot_late_s"] >= 86400:
            raise ValueError("slot %r + slot_late_s %r crosses local midnight" % (t, role["slot_late_s"]))


def codex_reading():
    """Use the Codex meter, never a Claude account's headroom, for an opted-in run."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Utils"))
    import agent_runner
    try:
        p = agent_runner.quota_gate()
    except agent_runner.Refused as e:
        return {"state": "UNMEASURED", "why": str(e)}
    return {"state": "MEASURED", "account": None, "at": iso(time.time()),
            "runway": p.get("codex.runway", {}).get("v"),
            "week_left": 100 - p["codex.week_used_pct"]["v"],
            "runway_m": p.get("codex.runway", {}).get("m", "UNMEASURED"), "week_left_m": "MEASURED"}


def codex_stop(cfg, r):
    """Pure. A Codex role's hard stop line: `codex_stop_week_left_pct` (DesignerCodex: 25, the brief of
    RIMMANDRAKE_DRAFT_BIOME_DESIGNER_PASSES_WITH_CODEX_BEFORE_RESET: "stop launching drafts at 25% left"). Not a token
    cap (those stay advisory): it keeps the week's Codex quota for the work already in the pipeline. -> why, or None."""
    line = cfg.get("codex_stop_week_left_pct")
    if cfg.get("runner") != "codex" or not _num(line) or r.get("state") != "MEASURED" or r.get("degraded"):
        return None
    left = r.get("week_left")
    if _num(left) and left < line:
        return "Codex week %.1f%% left, under the %g%% stop line (codex_stop_week_left_pct); held until the reset" % (
            left, line)
    return None


def parse_slot(s):
    """Pure. "HH:MM" (every day) | "Wed 09:00" | "Mon,Thu 10:00" -> (frozenset of tm_wday or None, "HH:MM").
    Raises ValueError on anything else: a slot the launcher cannot read is an alarm, never a guess."""
    parts = str(s).split()
    if len(parts) not in (1, 2):
        raise ValueError("slot %r: want 'HH:MM' or 'Ddd[,Ddd] HH:MM'" % (s,))
    hhmm = parts[-1]
    hm = hhmm.split(":")
    if len(hm) != 2 or not all(x.isdigit() for x in hm) or int(hm[0]) > 23 or int(hm[1]) > 59:
        raise ValueError("slot %r: time %r is not HH:MM" % (s, hhmm))
    if len(parts) == 1:
        return None, hhmm
    days = set()
    for d in parts[0].split(","):
        if d.strip().title() not in WEEKDAYS:
            raise ValueError("slot %r: weekday %r is not one of %s" % (s, d, ",".join(WEEKDAYS)))
        days.add(WEEKDAYS.index(d.strip().title()))
    return frozenset(days), hhmm


def weekday(t):
    return time.localtime(t).tm_wday


def slots(role, day=None):
    """-> [(slot, mode, cap)] in schedule order; slot is the schedule's string ("09:00", "Wed 09:00"). day (an epoch)
    keeps only the slots that run on that local weekday. Raises ValueError on an unreadable slot."""
    times = role.get("quick_checks_local") or role.get("runs_local") or []
    quick = "quick_token_cap" in role
    qcap = role.get("quick_token_cap") if role.get("quick_token_cap") is not None else role.get("run_token_cap")
    out = []
    for t in times:
        days, hhmm = parse_slot(t)
        if day is not None and days is not None and weekday(day) not in days:
            continue
        # a cap of 0 is a cap (the launch is then refused), never a fall-back to another cap (review night r3)
        if hhmm == role.get("economy_pass_local") and role.get("economy_token_cap") is not None:
            out.append((t, "economy", role["economy_token_cap"]))
        else:
            out.append((t, "quick" if quick else "run", qcap))
    return out


def slot_epoch(now, slot):
    """The epoch of a slot ("HH:MM" or "Ddd HH:MM": the weekday is the caller's filter) on now's local day."""
    lt = time.localtime(now)
    h, m = (int(x) for x in str(slot).split()[-1].split(":"))
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, h, m, 0, 0, 0, -1))


def day_of(t):
    return time.strftime("%Y-%m-%d", time.localtime(t))


def slot_key(day, slot):
    """The ONE done/run key of a scheduled slot: "YYYY-MM-DD <slot as the schedule writes it>" ("2026-10-28 07:30",
    "2026-10-28 Wed 07:30"). Writers (the due list) and readers (after_slots) both build it here, so a weekday slot's
    parent and dependent agree (review dispatcher-full #6)."""
    return "%s %s" % (day_of(day), slot)


def prev_day(now):
    """An epoch on the local CALENDAR day before now's (noon of it): now - 86400 lands two days back just after a
    spring-forward midnight (a 23-hour day) (review dispatcher-full #7). mktime normalises day 0 to the month before."""
    lt = time.localtime(now)
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday - 1, 12, 0, 0, 0, 0, -1))


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def read_ledger():
    """The ledger as every production reader sees it (model.read(), no argument: history + every shard) folded into
    a World. Raises on a malformed line (model.read reports, never skips)."""
    import importlib.util
    mod = sys.modules.get("rimflow_model_ro")
    if mod is None:
        spec = importlib.util.spec_from_file_location(
            "rimflow_model_ro", os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules["rimflow_model_ro"] = mod
    events = mod.read()
    return {"events": events, "world": mod.replay(events=events)}


def _usage_vals(result):
    """-> the usage dict and its four fields, or (None, None) when any is missing, not a whole non-negative number, or
    a bool: an absent field is unknown spend, never zero (review Q 8)."""
    u = result.get("usage") if isinstance(result, dict) else None
    if not isinstance(u, dict):
        return None, None
    vals = [u.get(k) for k in USAGE_KEYS]
    if not all(finite(v) and v >= 0 and float(v).is_integer() for v in vals):
        return None, None
    return u, dict(zip(USAGE_KEYS, (int(v) for v in vals)))


def raw_tokens(result):
    """Pure. The unweighted sum of the four usage fields (kept on the run for the record), or None (UNMEASURED)."""
    u, v = _usage_vals(result)
    return None if v is None else sum(v.values())


class UnknownModel(KeyError):
    """A model id (or alias) MODEL_PRICES has no row for: weighed by no fallback, it is named and raised."""

    def __str__(self):
        return self.args[0] if self.args else "unknown model"


_MODEL_TAIL_RX = re.compile(r"(\[1m\]|@[\w.:-]+|-v\d+(:\d+)?|-\d{8})$")


def resolve_model(model):
    """-> the MODEL_PRICES key of `model`, or raise UnknownModel naming it. Accepts a bare id, a provider-prefixed id
    (anything before its "claude-" part is dropped), a dated, versioned or [1m] suffix, any case, and a CLI alias
    (MODEL_VARS, read as model_id reads it: the env, then ~/.claude/settings.json; never assumed)."""
    if not isinstance(model, str) or not model.strip():
        raise UnknownModel("no model given: weighted tokens need the model that spent them (MODEL_PRICES)")
    name = model.strip().lower()
    if name in MODEL_VARS:
        env = model_id(name)
        if not env:
            raise UnknownModel("model alias %r: its env var %s is unset, so its model is unknown (MODEL_PRICES)"
                               % (model, MODEL_VARS[name]))
        return resolve_model(env)
    i = name.rfind("claude-")
    mid = name[i:] if i >= 0 else name
    while True:
        cut = _MODEL_TAIL_RX.sub("", mid)
        if cut == mid:
            break
        mid = cut
    if mid not in MODEL_PRICES:
        raise UnknownModel("unknown model %r (as %r): not in role_launch.MODEL_PRICES; add its list prices from "
                           "Anthropic's pricing page, there is no fallback weight" % (model, mid))
    return mid


def tier(model):
    """The ladder tier a model name means: 'claude-fable-5-2', 'Opus' and 'us.anthropic.claude-opus-5-5-v1:0' are
    faults of form, repaired to 'fable' / 'opus' / 'opus'. A name that holds no tier, or two, comes back as given, so a
    gate on TIERS still refuses it (Haiku is banned). Seen 2026-11-21: a full id was refused three times and a mod
    paused."""
    if not isinstance(model, str):
        return model
    low = model.strip().lower()
    hits = [t for t in TIERS if t in low]
    return hits[0] if len(hits) == 1 else model


def launch_model(model, env=None):
    """-> the `claude --model` argument for `model`: its tier's id from the environment (model_id); with no variable,
    the bare alias for a tier the CLI resolves itself (CLI_ALIASES). A Fable launch with no variable raises
    UnknownModel naming it: the CLI's own "fable" launched claude-fable-5-1. A name that is no tier comes back as
    given, for the caller's gate to refuse."""
    t = tier(model)
    if t not in TIERS:
        return model
    v = model_id(t, env)
    if v:
        return v
    if t in CLI_ALIASES:
        return t
    raise UnknownModel("model %r: its env var %s is unset in the environment and in %s, so the id it launches as is "
                       "unknown (the CLI's own alias %r launched claude-fable-5-1)" % (model, MODEL_VARS[t], SETTINGS, t))


def model_weights(model):
    """-> {PRICE_FIELDS: Fraction}: `model`'s list price per field / REF_MODEL's input price (weighted_v2)."""
    ref = MODEL_PRICES[REF_MODEL]["input_tokens"]
    return {k: p / ref for k, p in MODEL_PRICES[resolve_model(model)].items()}


def _whole(x):
    return finite(x) and x >= 0 and float(x).is_integer()


def _weigh(model, inp, w5, w1, read, out):
    """Exact weighted_v2 of one model's usage fields (a Fraction). An all-zero entry weighs 0 without resolving its
    model (the CLI's "<synthetic>" turns spend nothing)."""
    if not (inp or w5 or w1 or read or out):
        return Fraction(0)
    W = model_weights(model)
    return (inp * W["input_tokens"] + w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"]
            + read * W["cache_read_input_tokens"] + out * W["output_tokens"])


def _split(cw, a, b):
    """Cache writes split by TTL when the two parts are whole and add up; else all at the dearer 1h rate."""
    if _whole(a) and _whole(b) and int(a) + int(b) == cw:
        return int(a), int(b)
    return 0, cw


MU_KEYS = ("inputTokens", "cacheCreationInputTokens", "cacheReadInputTokens", "outputTokens")


def _model_usage_tokens(mu):
    """modelUsage {model: {inputTokens, ...}} -> exact weighted_v2 (Fraction), or None when any entry's four fields are
    not whole numbers (UNMEASURED). An absent field reads 0 here: the CLI omits a field it never billed."""
    tot = Fraction(0)
    for m, x in mu.items():
        if not isinstance(x, dict):
            return None
        vals = [x.get(k, 0) for k in MU_KEYS]
        if not all(_whole(v) for v in vals):
            return None
        inp, cw, read, out = (int(v) for v in vals)
        w5, w1 = _split(cw, x.get("cacheCreationEphemeral5mInputTokens"), x.get("cacheCreationEphemeral1hInputTokens"))
        tot += _weigh(m, inp, w5, w1, read, out)
    return tot


def run_tokens(result, model=None):
    """Pure. A `claude -p --output-format json` result -> its spend in weighted_v2 tokens (MODEL_PRICES), rounded up, or
    None (UNMEASURED). Reads result["modelUsage"] when present: the whole process, subagents included, per model (the
    CLI's costUSD is the same sum). Else result["usage"] (four fields, as _usage_vals), weighed as `model`. Cache
    writes are split by TTL when the split adds up, else weighed at the dearer 1h rate (never a guess in the cheap
    direction). An unknown or missing model raises UnknownModel by name: it is never weighed as some other model. The
    run is failed and its spend counted at its budget when UNMEASURED."""
    mu = result.get("modelUsage") if isinstance(result, dict) else None
    if isinstance(mu, dict) and mu:
        tot = _model_usage_tokens(mu)
        return None if tot is None else int(math.ceil(tot))
    u, v = _usage_vals(result)
    if v is None:
        return None
    w5, w1 = (_split(v["cache_creation_input_tokens"], (u.get("cache_creation") or {}).get("ephemeral_5m_input_tokens"),
                     (u.get("cache_creation") or {}).get("ephemeral_1h_input_tokens"))
              if isinstance(u.get("cache_creation"), dict) else (0, v["cache_creation_input_tokens"]))
    if not any(v.values()):
        return 0
    return int(math.ceil(_weigh(resolve_model(model), v["input_tokens"], w5, w1, v["cache_read_input_tokens"],
                                v["output_tokens"])))


def covers_subagents(result):
    """True when run_tokens(result) read modelUsage, which already holds the run's subagents: a caller adding their
    transcripts on top would count them twice."""
    mu = result.get("modelUsage") if isinstance(result, dict) else None
    return isinstance(mu, dict) and bool(mu) and _model_usage_tokens(mu) is not None


def model_usage_of(result):
    """-> the four raw fields (and TTL split) per model of a result's modelUsage, for a run record to keep, or None."""
    mu = result.get("modelUsage") if isinstance(result, dict) else None
    if not isinstance(mu, dict) or not mu:
        return None
    keep = MU_KEYS + ("cacheCreationEphemeral5mInputTokens", "cacheCreationEphemeral1hInputTokens")
    return {m: {k: x[k] for k in keep if k in x} for m, x in mu.items() if isinstance(x, dict)}


V1_UNIT = "weighted_v1"


def stored_unit(rec):
    """-> the unit of a stored spend figure (a detached or role run record, a RUN_SPEND line, a stage record's spend
    row): its token_unit, else weighted_v1. Every writer stamps its unit; a record with none was written before the
    weighted_v2 switch (2026-11-16 23:05 PST): 0 of 405 unstamped detached records with tokens ended after it, and the
    committed rows with none were stamped from their run records (measured 2026-11-22,
    design/specs/2026-11-22-run-spend-and-model-alias/equivalence.md). The one reader of a figure's unit."""
    u = rec.get("token_unit") if isinstance(rec, dict) else None
    return u if isinstance(u, str) and u.strip() else V1_UNIT


def tokens_v2(rec):
    """A stored spend record ({tokens, token_unit, model, model_usage?}) -> (weighted_v2 tokens or None, basis).
    basis "v2": already weighted_v2, returned as it is (never weighted twice). "v1_usage": a weighted_v1 record that
    kept its per-model usage, recomputed from it. "v1_bound": a weighted_v1 record with only its figure, times its
    model's input weight -- an UPPER bound (v1 weighed cache reads at 0.1, and no model's read price is above 0.1x its
    input price), marked so. "unmeasured": no figure. "unit <name>": a unit this cannot convert (None). The unit is
    stored_unit's. A model MODEL_PRICES cannot price raises UnknownModel by name."""
    if not isinstance(rec, dict):
        return None, "unmeasured"
    t = rec.get("tokens")
    unit = stored_unit(rec)
    if unit == TOKEN_UNIT:
        return (None if t is None else int(t)), ("v2" if t is not None else "unmeasured")
    if unit != V1_UNIT:
        return None, "unit %s" % unit
    mu = rec.get("model_usage")
    if isinstance(mu, dict) and mu:
        tot = _model_usage_tokens(mu)
        if tot is not None:
            return int(math.ceil(tot)), "v1_usage"
    if t is None:
        return None, "unmeasured"
    return int(math.ceil(int(t) * model_weights(rec.get("model"))["input_tokens"])), "v1_bound"


PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")


def _transcript_files(run, projects):
    """-> the transcript files of `run`: its pinned session (`--session-id`, launch) and that session's subagents, or
    for a run launched before the pin, the one recent transcript whose first lines name its unit."""
    import glob
    sid = run.get("session")
    if sid:
        return sorted(glob.glob(os.path.join(projects, "*", sid + ".jsonl"))
                      + glob.glob(os.path.join(projects, "*", sid, "subagents", "*.jsonl")))
    tag = "role launch %s]" % run.get("unit")
    for f in glob.glob(os.path.join(projects, "*", "*.jsonl")):
        try:
            if os.path.getmtime(f) < run.get("at", 0) - 60:
                continue
            with open(f, encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh):
                    if i >= 12:
                        break
                    if tag in line and '"type":"user"' in line.replace(" ", ""):
                        return [f]
        except OSError:
            continue
    return []


def transcript_usage(run, projects=PROJECTS):
    """A run with no result (killed at run_max_s, frozen by a stop, a torn out file) is measured from its transcript
    instead of being counted at its budget (OPS_ROLE_DIAGNOSE_STARVED_AT_FOUR_RUNS: a frozen 11-02 run spent 261,105
    weighted and was charged 450,000). -> a `usage` dict in the result's shape (the four USAGE_KEYS and the
    cache_creation TTL split), or None (UNMEASURED: no transcript, or no assistant turn in it). Each API message is
    logged once per content block with the same usage; the last line of each message id is taken (matches the result
    json exactly on rm-role-operations-1793627400). A resumed run (resume_of) counts only turns from its launch on."""
    since = run.get("at") if run.get("resume_of") else None
    per = {}
    for f in _transcript_files(run, projects):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"assistant"' not in line:
                        continue
                    try:
                        e = json.loads(line)
                    except ValueError:
                        continue
                    m = e.get("message") if isinstance(e, dict) and e.get("type") == "assistant" else None
                    if since is not None and (utc_epoch(str(e.get("timestamp") or "")[:19] + "Z") or 0) < since:
                        continue     # a resumed session's file also holds the turns of the run it continues
                    if isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("id"):
                        per[(f, m["id"])] = (m["usage"], m.get("model"))
        except OSError:
            continue
    if not per:
        return None
    return _sum_usage(per.values())


def _sum_usage(pairs):
    """[(message usage, message model)] -> the summed `usage` (USAGE_KEYS + cache_creation when every write was
    split) with "model_usage": the same per model in modelUsage's shape, so run_tokens(transcript_result(tu)) weighs
    each model at its own prices. None when a field is not a whole non-negative number."""
    tot = {k: 0 for k in USAGE_KEYS}
    split = {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0}
    whole = True
    mu, unsplit = {}, set()
    for u, model in pairs:
        e = mu.setdefault(str(model or "?"), {"inputTokens": 0, "cacheCreationInputTokens": 0,
                                              "cacheReadInputTokens": 0, "outputTokens": 0,
                                              "cacheCreationEphemeral5mInputTokens": 0,
                                              "cacheCreationEphemeral1hInputTokens": 0})
        for k, mk in zip(USAGE_KEYS, MU_KEYS):
            v = u.get(k) or 0
            if not (finite(v) and v >= 0):
                return None
            tot[k] += int(v)
            e[mk] += int(v)
        c = u.get("cache_creation")
        if isinstance(c, dict):
            for k, mk in (("ephemeral_5m_input_tokens", "cacheCreationEphemeral5mInputTokens"),
                          ("ephemeral_1h_input_tokens", "cacheCreationEphemeral1hInputTokens")):
                split[k] += int(c.get(k) or 0)
                e[mk] += int(c.get(k) or 0)
        elif u.get("cache_creation_input_tokens"):
            whole = False
            unsplit.add(str(model or "?"))
    for m in unsplit:          # a model with an unsplit write: all its writes at the dearer 1h rate (_split)
        mu[m].pop("cacheCreationEphemeral5mInputTokens")
        mu[m].pop("cacheCreationEphemeral1hInputTokens")
    if whole:
        tot["cache_creation"] = split            # run_tokens uses it only when it adds up; else all at the 1h rate
    tot["model_usage"] = mu
    return tot


def transcript_result(tu):
    """A transcript_usage dict -> a result-shaped dict run_tokens weighs per model (its modelUsage), or None."""
    if not isinstance(tu, dict):
        return None
    return {"usage": {k: v for k, v in tu.items() if k != "model_usage"}, "modelUsage": tu.get("model_usage") or {}}


def run_spend(r):
    """A run record's spend in TOKEN_UNIT for a cap: tokens_v2's figure (a weighted_v1 record converted, the model read
    from model_id, else model). UNMEASURED counts its budget: no figure, a unit it cannot convert, or a model
    MODEL_PRICES cannot price. Never 0 for a figure it could not weigh."""
    try:
        t, _basis = tokens_v2(dict(r, model=r.get("model_id") or r.get("model")))
    except UnknownModel:
        t = None
    return r.get("budget", 0) if t is None else t


def spent_today(rs, now):
    day = day_of(now)
    tot = 0
    for r in rs.get("runs") or []:
        if r.get("runner") == "codex":
            continue
        if r.get("day") != day:
            continue
        tot += run_spend(r)
    return tot


def finished_in_window(rs, now):
    """Pure. Measured finished runs in the overrun window: the fin_at stamps, or (state written before fin_at
    existed) the finished runs still on record with tokens, whichever is more; never below 1."""
    fin = len([t for t in rs.get("fin_at") or [] if now - t < OVER_WINDOW_S])
    kept = len([r for r in rs.get("runs") or [] if r.get("state") != "running" and r.get("tokens") is not None
                and now - r.get("at", 0) < OVER_WINDOW_S])
    return max(fin, kept, 1)


def overspend_day(name, rs, item, daily, spent, budget, now, act, did):
    """An advisory-capped role (`caps_advisory`, Operations, owner 2026-11-02) is never refused for money; a day
    that passes its expected total (daily_token_cap) raises an IMMEDIATE alarm instead, once a day: a note on its
    item and a RAISE FIRST line in the Conductor log, so the cost is fixed fast without starving the watch."""
    if rs.get("overspend_day") == day_of(now):
        return
    rs["overspend_day"] = day_of(now)
    act(do="alarm", kind="role:%s:overspend_day" % name, ticket=item, note=True, conductor_log=True,
        why="%s is over its expected day: %d weighted used today%s > daily_token_cap %d; %s" % (
            name, spent, " + %d for this run" % budget if budget else "", daily, did),
        raise_first="%s is spending past its expected day (advisory cap %d): file an item and cut its cost now; "
                    "never starve it." % (name, daily))


def prompt(role, mode, trigger, reading, budget, cap, spent, unit, rows=None, reasons=None,
           scope=None, root=None):
    """The launch message. Every role is spend-blind (owner 2026-11-16): no message states its budget, cap or spend. Only
    a `token_aware: true` role (Operations; the Conductor, owner 2026-10-31) is told the ACCOUNT's reading; every other
    role is token-blind (owner 2026-10-27): its message carries no runway, week, budget or cap,
    and no order to watch one (review T, F1). Nothing stops a run at its budget mid-run: the real bounds are
    `run_max_s` (wall time) and the after-the-fact accounting (supervise_roles), both the Dispatcher's (F2).
    `scope` (default `mode`; "incident" for an incident-only run) picks `inline_by_mode`: those sections of the
    instructions ride in the message, so the run does not open the file (RIMMANDRAKE_SLIM_OPERATIONS_START_PACKAGE_HALF_IS_UNRELATED)."""
    inline, blind_doc = inline_instructions(role, scope or mode, root)
    lines = ["[RimFlow Dispatcher — a program, not a person; role launch %s]" % unit,
             ("You are the RimFlow %s role, run headless by the Dispatcher. Your instructions for this trigger are "
              "the sections of %s below; do what they say, then stop. Do not open that file on this run." % (
                  role["name"], role["instructions"])) if inline else
             "You are the RimFlow %s role, run headless by the Dispatcher. Read %s and do what it says for this "
             "trigger, then stop." % (role["name"], role["instructions"]),
             ("INLINE INSTRUCTIONS UNAVAILABLE (%s): read the file instead." % blind_doc) if blind_doc else "",
             "Trigger: %s %s." % (mode, trigger)]
    if mode == "alarm" and rows:
        # the alarm rows and the instructions that apply, so the run does not spend turns finding them
        # (OPS_ROLE_SHRINK_RUN_COST; `scope_by_mode` is schedule data)
        lines += ["The alarms this run covers (ops_watch status.json, at launch):"] + list(rows)
    if reasons:
        # a re-run of a rejected stage close: every reason in full (RELENTLESS_ROLE_LAUNCH_HARDEN_CAUSE_BOOK; the
        # trigger above carries at most four, cut to 400 characters)
        lines += ["Your previous run's result was REJECTED for these %d reason(s); fix every one:" % len(reasons)] + [
            "- %s" % r for r in reasons]
    if role.get("scope_by_mode", {}).get(mode):
        lines.append(role["scope_by_mode"][mode])
    if inline:
        lines += ["----- your instructions (from %s) -----" % role["instructions"], inline, "----- end of instructions -----"]
    if role.get("token_aware") is True:
        lines += ["Account reading: runway %.2f %s, week left %.0f%% %s; ops_watch status at %s." % (
                      reading["runway"], reading["runway_m"], reading["week_left"], reading["week_left_m"],
                      reading["at"]),
                  ("DEGRADED READING: %s. The ops reading is UNMEASURED (runway and week left above are placeholders, not readings): diagnose the watch first (ops_watch status.json, its unit and timer) and report it before any work that relies on the reading." % reading["degraded"]) if reading.get("degraded") else ""]
        # no line on this run's own budget or spend (owner 2026-11-16: "I don't like how you're telling the agent how
        # much it's spent"): the line above is the account's state, the run's own spend stays on its record
    lines = [x for x in lines if x]
    lines.append("You work as seat %s in %s. Never take the bridge, restart the game or deploy." % (
        role["seat"], role["clone"]))
    return "\n".join(lines)


# ---------------------------------------------------------------- decide (pure but for obs)

def supervise_roles(sch, st, obs, now, act):
    """Every persisted run still `running`, of every role (enabled or not, in the schedule or not), checked on every
    tick BEFORE anything can end the tick early: PAUSE, a blind `claude agents`, a disabled role (review Q 1). A run
    stays `running` (busy, its budget counted) until systemd says its unit is inactive/failed: a stop is re-issued
    every tick until then (review Q 2), and any other unit state ("unknown", a failed query) is UNMEASURED, busy and
    alarmed, never a finish (review Q 3). -> the set of role names with a run in flight."""
    rst = st.setdefault("roles", {})
    by_name = roles_by_name(sch)
    busy = set()
    # cause attaches a busy book refused (owe_cause_attach): asked again each tick. They stay in the state until
    # execute carries one out (settle_cause_owed), so a tick fenced or killed before it runs loses none
    for o in st.get("cause_owed") or []:
        if isinstance(o, dict) and o.get("key"):
            act(do="role_cause_attach", role=o.get("role"), key=o["key"], said=o.get("said"), at_s=o.get("at_s"),
                note=False, why="%s rejection: attach to cause %s (retried: the book was busy)" % (
                    o.get("role") or "role", o["key"]))
    for name, rs in sorted(rst.items()):
        if not isinstance(rs, dict):
            continue
        try:
            _supervise_one(name, rs, dict(ROLE_DEFAULTS, **(by_name.get(name) or {})), obs, now, act, busy)
        except Exception as e:  # noqa: BLE001 - one role's bad run or value never stops the others' supervision (V3)
            busy.add(name)      # unknown: kept busy, never launched over
            act(do="alarm", kind="role:%s:supervise" % name, ticket=(by_name.get(name) or {}).get("ledger_item"),
                note=True, why="role %s supervision raised %s: %s; its runs are kept as running and checked again "
                "next tick" % (name, type(e).__name__, str(e)))
    return busy


def role_shape_error(r):
    """Pure. -> None, or why this roles entry cannot be keyed or ordered: name must be a nonempty string and
    after_role absent/null or a string. Checked before any map or ordering is built, so a JSON list or object there
    is skipped with an alarm instead of raising TypeError through every role (ROLE_LAUNCH_HARDEN_FLOOR_AND_ODD_NAMES)."""
    if not isinstance(r, dict):
        return "entry is a %s, not a mapping" % type(r).__name__
    if not (isinstance(r.get("name"), str) and r["name"].strip()):
        return "name %r is not a nonempty string" % (r.get("name"),)
    if r.get("after_role") is not None and not isinstance(r["after_role"], str):
        return "role %s: after_role %r is not a string" % (r["name"], r["after_role"])
    return None


def _named(r):
    return isinstance(r, dict) and isinstance(r.get("name"), str) and bool(r["name"].strip())


def roles_by_name(sch):
    """{name: role} over the schedule's roles entries that are mappings with a nonempty string name; anything else is
    skipped here (decide_roles alarms it), so one malformed entry cannot raise through the tick (review V, V3; a list
    as a name is unhashable: ROLE_LAUNCH_HARDEN_FLOOR_AND_ODD_NAMES)."""
    return {r["name"]: r for r in sch.get("roles") or [] if _named(r)}


def decide_order(roles):
    """Pure. Roles in decide order: each after the role its after_role names (whole chains, not just one level:
    review night r3), otherwise schedule order. A cycle or a name not in the list ends the chain; an entry with no
    usable name or a non-string after_role is depth 0 (decide_roles skips it with an alarm before it gets here)."""
    by = {r["name"]: r for r in roles if _named(r)}

    def depth(r):
        seen, d = set(), 0
        while _named(r) and isinstance(r.get("after_role"), str) and r["after_role"] in by and r["name"] not in seen:
            seen.add(r.get("name"))
            r, d = by[r["after_role"]], d + 1
        return d
    return sorted(roles, key=depth)


def max_s_of(run, cfg):
    """A run's wall-time bound: its recorded run_max_s, else the role's run_max_s + pre_launch_max_s, else the
    default, whichever is first a positive number (a None or 0 from an older schedule never reaches a comparison:
    review V, V3). pre_launch_max_s (ARBITER_MEASURE_PRELAUNCH_EVIDENCE_TIME) is the pre-steps' own budget: the
    bound counts from launch, so without it the pre-steps would eat the role's run_max_s."""
    role_max = cfg.get("run_max_s")
    if _num(role_max) and role_max > 0 and _num(cfg.get("pre_launch_max_s")):
        role_max += cfg["pre_launch_max_s"]
    for v in (run.get("run_max_s"), role_max, ROLE_DEFAULTS["run_max_s"]):
        if _num(v) and v > 0:
            return v
    return ROLE_DEFAULTS["run_max_s"]


def _supervise_one(name, rs, cfg, obs, now, act, busy):
    """One role's persisted runs (supervise_roles' body, guarded per role there)."""
    for run in rs.get("runs") or []:
        if run.get("state") != "running":
            if run.get("close_owed") and run.get("concept"):
                # its stage close raised after the run was marked finished: retried every tick until it returns
                try:
                    res = obs["result"](run)
                except Exception:  # noqa: BLE001 - the close needs only the run; the result only shapes a route
                    res = None
                close_concept(name, rs, cfg, run, res if isinstance(res, dict) else {}, run.get("tokens"), now, act,
                              obs)
            continue
        ustate = obs["unit_state"](run["unit"])
        if ustate in ACTIVE and not run.get("scope") and obs.get("scope"):
            # a run recorded before the scope was named at creation (no `marker`): learn claude_bounded's
            # MainPID-named scope while the unit's MainPID still exists (review round R, D)
            run["scope"] = obs["scope"](run["unit"], run.get("seat") or cfg.get("seat"))
        if ustate in TERMINAL:
            ustate = ended(run, ustate, obs)
        if ustate not in TERMINAL:
            busy.add(name)
            if ustate.startswith("unit "):
                act(do="alarm", kind="role:%s:scope" % name, ticket=run.get("item"), note=True,
                    why="%s run %s: %s; kept as running, checked again next tick" % (name, run["unit"], ustate))
            elif ustate not in ACTIVE:
                act(do="alarm", kind="role:%s:unit" % name, ticket=run.get("item"), note=True,
                    why="%s run %s unit state UNMEASURED (%s): kept as running, retried next tick"
                    % (name, run["unit"], ustate))
            max_s = max_s_of(run, cfg)
            if now - run["at"] >= max_s:
                tries = run.get("stop_tries", 0)
                run["stop_tries"] = tries + 1
                act(do="role_stop", role=name, unit=run["unit"], scope=run.get("scope"),
                    unit_gone=ustate.startswith("unit "),     # stop the scope alone: the unit was collected
                    marker=run.get("marker"), force=tries >= 2,     # TERM the run's stray processes, KILL from #3
                    since=run.get("at"),
                    seat=run.get("seat") or cfg.get("seat"), ticket=run.get("item"), note=tries == 0,
                    why="%s run %s still %s after %d s (run_max_s %d): stop #%d" % (
                        name, run["unit"], ustate, now - run["at"], max_s, tries + 1))
                if tries == 0:
                    act(do="alarm", kind="role:%s:overtime" % name, ticket=run.get("item"), note=True,
                        why="%s run %s passed run_max_s %d" % (name, run["unit"], max_s))
                else:
                    act(do="alarm", kind="role:%s:stop_failed" % name, ticket=run.get("item"), note=True,
                        conductor_log=True, raise_first="%s run will not stop: its slot stays held." % name,
                        why="%s run %s still %s after %d stop(s): NOT confirmed stopped, kept as running"
                        % (name, run["unit"], ustate, tries))
            continue
        res = obs["result"](run)
        if run.get("concept") and not isinstance(res, dict):
            # no model output: stage5_program may have closed the run itself (no model started, nothing charged)
            try:
                pc = (obs.get("program_closed") or program_closed)(run["concept"], run["unit"])
            except Exception as e:  # noqa: BLE001 - unread: the run is harvested as before (a failed run, alarmed)
                pc = ("error", "its stage.json could not be read: %s" % e)
            if pc and pc[0] == "closed":
                run.update(state="done", tokens=0, raw_tokens=0, token_unit=TOKEN_UNIT, by="program")
                act(do="role_done", role=name, unit=run["unit"], ticket=run.get("item"), note=True,
                    why="%s run %s closed by program at stage 5 (%s%s): no model started, 0 tokens" % (
                        name, run["unit"], pc[1].get("outcome"),
                        " to stage %s" % pc[1].get("to") if pc[1].get("outcome") == "return" else ""),
                    blind=blind(name, "completed", run.get("mode"), run["unit"]))
                finish_slot_alarms(rs, run)
                close_concept(name, rs, cfg, run, {}, 0, now, act, obs)
                continue
            cs = judge_stopped(run, now, obs)
            if cs:
                # RIMMANDRAKE_CHARGE_NOTHING_FOR_JUDGE_STOPPED_RUN: the coverage judge stopped the concept and the unit
                # exited STOP_EXIT before claude started; charged 0, closed at 0, and its alarm is the stop's own
                run.update(state="done", tokens=0, raw_tokens=0, token_unit=TOKEN_UNIT, by="judge_stop",
                           coverage_stop=cs)
                act(do="role_done", role=name, unit=run["unit"], ticket=run.get("item"), note=True,
                    why="%s run %s stopped by the stage-5 coverage judge at %s (%s): no model started, 0 tokens" % (
                        name, run["unit"], cs.get("at"), cs.get("why") or "?"),
                    blind=blind(name, "completed", run.get("mode"), run["unit"]))
                finish_slot_alarms(rs, run)
                close_concept(name, rs, cfg, run, {}, 0, now, act, obs)
                continue
        if run.get("concept") and isinstance(res, dict):
            try:
                pc = (obs.get("program_closed") or program_closed)(run["concept"], run["unit"])
            except Exception:  # noqa: BLE001 - only the alarm below reads it
                pc = None
            if pc and pc[0] == "error":
                act(do="alarm", kind="role:%s:stage5_program" % name, ticket=run.get("item"), note=True,
                    why="%s run %s on %s: the stage-5 program step did not run, the Designer ran as today: %s" % (
                        name, run["unit"], run["concept"], pc[1]))
        is_codex = run.get("runner") == "codex" or (isinstance(res, dict) and res.get("runner") == "codex")
        if is_codex:
            run["runner"] = "codex"
            run["codex_usage"] = codex_usage(run, res)
        alias = run.get("model_id") or (mode_model(cfg, run.get("mode")) if cfg.get("model") else None)
        unknown = None

        def weigh(r):
            nonlocal unknown
            try:
                return run_tokens(r, alias)
            except UnknownModel as e:   # weighed as no other model: UNMEASURED, named in the record and the note
                unknown = str(e)
                return None
        tok = weigh(res)
        res_tok = tok
        raw = raw_tokens(res)
        mu = model_usage_of(res)
        if tok is None and not is_codex and obs.get("transcript"):
            tu = obs["transcript"](run)          # no usable result: measure what it spent, never charge the budget
            if tu is not None:
                tok, raw = weigh(transcript_result(tu)), raw_tokens({"usage": tu})
                mu = tu.get("model_usage")
                run["token_source"] = "transcript"
        tok = session_part(rs, run, tok, res)   # a resumed mend: its own part of the session (designer_mend)
        run["tokens"] = tok                     # weighted_v2 (MODEL_PRICES): what caps and spend read
        run["raw_tokens"] = raw                 # the unweighted sum, for the record only
        run["token_unit"] = TOKEN_UNIT          # a run without it predates the weighting (its tokens are raw)
        if mu and "session_tokens" in run:
            run["session_model_usage"] = mu     # the whole session's fields, never read as this run's own
        elif mu:
            run["model_usage"] = mu             # raw per-model fields: any later unit is recomputed from these
        if unknown and tok is None:
            run["unknown_model"] = unknown
        run["state"] = "failed" if (not isinstance(res, dict) or res.get("is_error") or
                                    (not is_codex and res_tok is None)) else "done"
        res = res if isinstance(res, dict) else {}
        models = sorted(res.get("modelUsage") or {})
        act(do="role_done", role=name, unit=run["unit"], ticket=run.get("item"), note=True,
            why=("%s %s run %s %s: Codex usage %s; recorded separately from Claude budgets" % (
                name, run.get("mode"), run["unit"], run["state"], json.dumps(run["codex_usage"])) if is_codex else
                "%s %s run %s %s%s: %s weighted tokens of a %d budget (raw %s), model %s, %s" % (
                name, run.get("mode"), run["unit"], run["state"],
                " (after %d stop(s))" % run["stop_tries"] if run.get("stop_tries") else "",
                ("%d (from its transcript, no result)" % tok if run.get("token_source") == "transcript" else tok)
                if tok is not None else "UNMEASURED (counted at its budget%s)" % (
                    ": " + run["unknown_model"] if run.get("unknown_model") else ""),
                run.get("budget") or 0, run["raw_tokens"] if run["raw_tokens"] is not None else "?",
                ",".join(models) or "?",
                # an auth failure reports subtype `success` with is_error: "failed ... success" hid it on 10-30
                "%s%s" % (res.get("subtype") or "no result",
                          " but is_error (%s)" % (res.get("terminal_reason") or "?") if res.get("is_error") else ""))),
            # a token-blind role reads its ledger item: its note is a FIXED outcome (blind_note), never the result's
            # subtype or text; the journal and Operations' item keep `why` (review dispatcher-full #2)
            blind=blind(name, "completed" if run["state"] == "done" else "failed", run.get("mode"), run["unit"]))
        finish_slot_alarms(rs, run)
        if run.get("concept"):
            close_concept(name, rs, cfg, run, res, tok, now, act, obs)
        daily = cfg.get("daily_token_cap")
        if cfg.get("caps_advisory") is True and daily is not None and spent_today(rs, now) > daily:
            overspend_day(name, rs, run.get("item") or cfg.get("ledger_item"), daily, spent_today(rs, now), 0, now,
                          act, "its run %s just finished" % run["unit"])
        if tok is not None:      # every measured finish (an overrun counts failed ones too): the OVER_RATE denominator
            rs["fin_at"] = [t for t in rs.get("fin_at") or [] if now - t < OVER_WINDOW_S] + [now]
        if tok is not None and tok > (run.get("budget") or 0):
            # advisory caps (owner 2026-11-02): the overrun is the alarm, at once, in the Conductor log too
            loud = {"conductor_log": True, "raise_first": "%s run %s went over its advisory budget: file an item "
                    "and cut its cost now." % (name, run["unit"])} if cfg.get("caps_advisory") is True else {}
            act(do="alarm", kind="role:%s:overbudget" % name, ticket=run.get("item"), note=True,
                why="%s run %s used %d weighted tokens (raw %s), budget %d" % (
                    name, run["unit"], tok, run["raw_tokens"], run.get("budget") or 0), **loud)
            # the day's spend already counts the real tokens, so the daily cap answers one overrun by itself; a
            # role that keeps overrunning has a wrong budget, and only a person can reset that
            over = [t for t in rs.get("over_at") or [] if now - t < OVER_WINDOW_S] + [now]
            rs["over_at"] = over
            if len(over) >= OVER_REPEAT and len(over) >= OVER_RATE * finished_in_window(rs, now):
                act(do="alarm", kind="role:%s:overbudget_repeat" % name, ticket=run.get("item"), note=True,
                    conductor_log=True, blind=blind(name, "overbudget", run.get("mode"), run["unit"]),
                    why="%s ran over budget %d times in 7 days (of %d measured runs): its budget or its scope is "
                    "wrong" % (name, len(over), finished_in_window(rs, now)),
                    raise_first="%s keeps overrunning: re-set its budget or narrow its scope." % name)
        acct = account_death(res) if run["state"] == "failed" and not is_codex else None
        if acct == "cloudflare" and not run.get("tokens") and not run.get("resume_of"):
            acct = None                                  # no work to resume: its slot comes back (auth_failed_back)
        if acct:
            # the account ended it, not the role: no role:<name>:failed (ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS)
            rec, why = resume_record(run, res, acct, now, cfg, resume_account(obs))
            old = rs.get("resume") if isinstance(rs.get("resume"), dict) else None
            if rec and old and old.get("of") != rec["of"]:
                # two chains cut off: the run that did more work is kept, the other one's session is named
                keep = rec if (rec.get("tokens") or 0) >= (old.get("tokens") or 0) else old
                gone = old if keep is rec else rec
                act(do="role_hold", role=name, ticket=gone.get("item"), note=True,
                    why="%s resume of %s dropped for %s's (more work): its work stays in session %s" % (
                        name, gone.get("unit"), keep.get("unit"), gone.get("session")))
                rec = keep
                if keep is old:
                    why = "the pending resume of %s did more work and is kept" % old.get("unit")
            if rec:
                rs["resume"] = rec
            act(do="role_hold", role=name, ticket=run.get("item"), note=True,
                blind=blind(name, "failed", run.get("mode"), run["unit"]),     # a closed-set outcome: true, and no alarm
                why="%s run %s ended on the account (%s), not a role failure: %s" % (
                    name, run["unit"], acct, ("resumable: session %s resumes at %s (resume %d of %d)" % (
                        rec["session"], iso(rec["due"]), rec["n"], RESUME_MAX)) if rec else "not resumed, " + why))
        elif run["state"] == "failed":
            text = res.get("result") or run.get("err_tail") or ""
            back = auth_failed_back(rs, run, text, now) if not is_codex else False
            act(do="alarm", kind="role:%s:failed" % name, ticket=run.get("item"), note=True, conductor_log=True,
                raise_first="%s run failed%s." % (name, ": its slot is given back, it reruns once the login works"
                                                  if back else ""),
                # a blind role's item gets the fixed line only: the result text is outside text (a usage-limit
                # message names no token word); the full why goes to Operations' item (dispatcher.route_note)
                blind=blind(name, "failed", run.get("mode"), run["unit"]),
                why="%s run %s ended without a good result (%s)" % (
                    name, run["unit"], ("usage UNMEASURED%s: " % (" (%s)" % run["unknown_model"]
                                                                if run.get("unknown_model") else "")
                                        if res and tok is None else "")
                    + (text or ("no result text" if res else "no result file"))))
        run.pop("consumed", None)                        # read only just above; runs stay in state for 2 days
    rs["runs"] = [r for r in rs.get("runs") or [] if r.get("state") == "running" or r.get("close_owed")
                  or now - r["at"] < 2 * 86400]


def account_death(res):
    """Pure. A claude -p result -> the account error that ended it ("usage_limit_reached", "429", ...), or None. Only an
    is_error result whose api_error / api_error_status / short text says the account refused counts; an auth death
    (AUTH_RX) is login_watch's and auth_failed_back's, not this."""
    if not isinstance(res, dict) or not res.get("is_error"):
        return None
    if len(str(res.get("result") or "")) <= AUTH_TEXT_MAX and CLOUDFLARE_RX.search(str(res.get("result") or "")):
        return "cloudflare"                              # before AUTH_RX: its text says "Please run /login" too
    err = str(res.get("api_error") or "")
    if err in ACCOUNT_ERRORS:
        return err
    if res.get("api_error_status") == 429:
        return "429"
    text = str(res.get("result") or "")
    if res.get("terminal_reason") == "api_error" and len(text) <= AUTH_TEXT_MAX and LIMIT_RX.search(text) \
            and not AUTH_RX.search(text):
        return "limit"
    return None


def limit_reset_at(text, at):
    """-> the epoch the limit message names as its reset (login_watch.limit_reset), or None."""
    try:
        import login_watch as LW
    except ImportError:
        try:
            from rimflow import login_watch as LW
        except ImportError:
            return None
    return LW.limit_reset(text, at)


def resume_record(run, res, err, now, cfg, account=None):
    """Pure but for the clock it is handed. -> rs["resume"] for a run the account ended after real usage, or (None, why)
    when it is not resumable. The chain count comes from the run (a resumed run carries resume_n)."""
    n = int(run.get("resume_n") or 0)
    if not run.get("tokens") and not run.get("resume_of"):   # a resume that died at once still holds the chain's work
        return None, "it used no tokens, so the next scheduled run starts fresh"
    if not (res.get("session_id") or run.get("session")):
        return None, "no session id on record to resume"
    if run.get("concept"):
        return None, "a stage-machine run is reopened by its stage, never resumed"
    import failure_class as FC
    worked = bool(run.get("tokens")) and not FC.read(FC.ACCOUNT, err).counts
    if n >= RESUME_MAX and not worked:
        return None, "it was resumed %d times in a row with no work done (RESUME_MAX)" % n
    if err == "cloudflare" and run.get("resume_error") == "cloudflare":
        return None, "it died on a Cloudflare challenge once already and was retried once"
    text = str(res.get("result") or "")
    reset = None if err == "cloudflare" else limit_reset_at(text, now)
    wait = cfg.get("cloudflare_retry_s", CLOUDFLARE_RETRY_S) if err == "cloudflare" else cfg.get("resume_wait_s", RESUME_WAIT_S)
    return {"of": run.get("resume_of") or run["unit"], "unit": run["unit"], "session": res.get("session_id") or
            run.get("session"), "account": account, "mode": run.get("mode"), "budget": run.get("budget"), "slot": run.get("slot"),
            "item": run.get("item") or cfg.get("ledger_item"), "error": err,
            "tokens": run.get("tokens"), "n": 1 if worked else n + 1, "at": now,
            "due": reset if reset is not None else now + wait}, None


def resume_account(obs):
    """-> the account the machine runs on now (obs["account"]), or None unread."""
    try:
        return obs["account"]() if obs.get("account") else None
    except Exception:  # noqa: BLE001 - unread: resume_due waits for the reset instead
        return None


def resume_prompt(cfg, rec, unit):
    """The continue message a resumed run gets (its session already holds the original task and its work)."""
    # states no spend or budget (owner 2026-11-16, RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN)
    return ("You are %s, resumed. Your run %s was cut off by the account (%s); the account answers again. Continue "
            "exactly where you left off: finish the task this session was given, and end the way that task says a run "
            "ends. Do not start the task over. This is resume %d of at most %d (unit %s)." % (
                cfg.get("name"), rec["unit"], rec["error"], rec["n"], RESUME_MAX, unit))


def resume_due(name, rs, cfg, now, act, busy, gate, account=None, tick_launch=None):
    """decide_roles' resume step for one role. -> True when this tick is spent on the resume (launched, or held so no
    fresh run is launched over the context it would continue), False to decide the role as usual. Due once the reset
    its message named has passed, or at once when the machine now runs on another account than the one that refused
    it; either way the account gate must go. Kept RESUME_TTL_S past its due time, then dropped, said."""
    rec = rs.get("resume")
    if not isinstance(rec, dict) or not rec.get("unit") or not rec.get("session"):
        rs.pop("resume", None)
        return False
    due = float(rec.get("due") or 0)
    if now - max(float(rec.get("at") or 0), due) > RESUME_TTL_S:
        rs.pop("resume", None)
        act(do="role_hold", role=name, ticket=rec.get("item"), note=True,
            why="%s resume of %s dropped: not launchable for %d s past its due time; its work stays in session %s" % (
                name, rec.get("unit"), RESUME_TTL_S, rec.get("session")))
        return False
    if name in busy:
        return True             # one run at a time; the resume goes once the running one ends
    switched = bool(account and rec.get("account") and account != rec["account"])
    if now < due and not switched:
        if rs.get("resume_hold") != [rec["unit"], "due"]:
            rs["resume_hold"] = [rec["unit"], "due"]
            act(do="role_hold", role=name, why="%s holds for the resume of %s at %s (the account's reset): no fresh "
                "run over the work it continues" % (name, rec["unit"], iso(due)))
        return True
    go, pk = gate("role_launch") if gate else (True, {})
    if not go:
        if rs.get("resume_hold") != [rec["unit"], "gate"]:
            rs["resume_hold"] = [rec["unit"], "gate"]
            act(do="role_hold", role=name, why="%s resume of %s held: %s" % (name, rec["unit"], pk.get("why")))
        return True
    unit = "rm-role-%s-%d" % (name.lower(), int(now))
    # built before anything is consumed: a raise here leaves the resume pending (review V, V7)
    kw = dict(do="role_launch", role=name, unit=unit, ticket=rec.get("item"), note=True, mode=rec.get("mode"),
              budget=rec.get("budget") or 0, slot="resume of %s" % rec["unit"], seat=cfg["seat"],
              run_max_s=max_s_of({}, cfg), account=pk.get("account"), resume=rec["session"],
              resume_of=rec.get("of") or rec["unit"], resume_n=rec.get("n") or 1, resume_error=rec.get("error"),
              why="%s resume %s of %s (cut off by the account: %s, after %s weighted tokens%s), budget %s, unit %s, "
              "session %s" % (name, rec.get("n"), rec["unit"], rec.get("error"), rec.get("tokens"),
                              "; now on another account" if switched and now < due else "", rec.get("budget"), unit,
                              rec["session"]),
              blind=blind(name, "launched", rec.get("mode"), unit), message=resume_prompt(cfg, rec, unit))
    rs.pop("resume_hold", None)
    rs["pending_launch"] = {"unit": unit, "mode": "resume", "resume": rec}
    rs.pop("resume")
    if tick_launch is not None:
        tick_launch[name] = unit
    act(**kw)
    if tick_launch is not None:
        tick_launch.pop(name, None)
    busy.add(name)
    return True


def auth_failed_back(rs, run, text, now):
    """A run killed by a lost login did no work: its slot and alarm mark go back so it runs again
    (10-30: three such runs spent the day's limits). At most AUTH_BACKS_PER_DAY per role, so a login
    that fails only for role runs cannot loop. -> True when given back."""
    used = rs.get("auth_backs") if (rs.get("auth_backs") or {}).get("day") == day_of(now) else {"day": day_of(now), "n": 0}
    p = run.get("consumed")
    if not (p and len(str(text)) <= AUTH_TEXT_MAX and (AUTH_RX.search(str(text)) or CLOUDFLARE_RX.search(str(text)))) \
            or run.get("tokens") \
            or used["n"] >= AUTH_BACKS_PER_DAY or rs.get("pending_launch"):
        return False
    if any(r.get("at", 0) > run["at"] for r in rs.get("runs") or []):    # a later run already moved the marks
        return False
    rs["pending_launch"] = p
    if not unlaunch(rs, run["unit"]):
        rs.pop("pending_launch", None)
        return False
    used["n"] += 1
    rs["auth_backs"] = used
    run["tokens"] = 0                                    # it did no work: its budget is not spent either
    return True


# ---- notes for a token-blind role's ledger item (review dispatcher-full #2). A blind item gets ONLY a text built
# here from closed sets: a known role name, a known mode, a dispatcher unit name, and a fixed outcome. Reasons, error
# output, exception text, result subtypes and triggers (alarm keys, ledger event text) are outside text that can
# carry an account id or a figure in words no token list knows: they go to the journal and Operations' item only.
# The closed sets and the renderer live in contracts.blind_core (stdlib only; the 2-minute tick imports it), with a
# pydantic twin contracts.blind.BlindNote (BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF). These names stay for callers.
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.append(_SRC)
from contracts import blind_core as _BC  # noqa: E402

BLIND_ROLES = _BC.NOTE_ROLES
BLIND_MODES = _BC.NOTE_MODES
BLIND_OUTCOMES = _BC.NOTE_OUTCOMES


def blind(role, outcome, mode=None, unit=None):
    """An action's blind-note fields (dispatcher.route_note renders them with blind_note)."""
    return {"role": role, "outcome": outcome, "mode": mode, "unit": unit}


def blind_note(b):
    """Pure. -> the fixed text for a blind item, or None when ANY field is outside its closed set (the note then goes
    to Operations' item, never to the blind one). "dispatcher: Conductor quick run: completed" (the unit name is
    never in the text: its digits are a payload a blind page must not carry). contracts.blind_core.note_text."""
    return _BC.note_text(b)


def ended(run, ustate, obs):
    """The unit is inactive/failed. -> ustate (terminal) only when the run's termination is POSITIVELY established,
    else a "unit ..." reason it is still busy (review dispatcher-full #1). claude lives in claude_bounded's scope,
    outside the unit (its shell traps TERM), so the unit ending is not claude ending:
      - the scope, named at creation (role_scope: claude-seat-<seat>-<unit>.scope, persisted with the run before
        systemd-run), must be inactive/failed too; and
      - no process may still carry the run's RM_ROLE_UNIT=<unit> marker (procs_of: claude and every child inherit
        it), which also covers a clone whose claude_bounded.sh predates CLAUDE_SCOPE_UNIT and named the scope by
        PID. The scan UNMEASURED is busy, never a finish.
    A run recorded before markers existed has only its scope; with no scope resolved it is never retired by the
    clock any more (the old run_max_s "UNCONFIRMED" retirement let a surviving claude overlap the next run)."""
    scope = run.get("scope")
    if not scope:
        return "unit %s, scope never resolved: termination UNCONFIRMED, kept busy (stop claude-seat-%s-* by hand)" \
            % (ustate, run.get("seat") or "?")
    sstate = obs["unit_state"](scope)
    if sstate not in TERMINAL:
        return "unit %s but scope %s %s" % (ustate, scope, sstate)
    if run.get("marker"):
        n = obs["procs"](run["marker"], since=run.get("at")) if obs.get("procs") else None
        n = len(n) if isinstance(n, list) else n
        if n is None:
            return "unit %s, scope %s %s, its process check UNMEASURED" % (ustate, scope, sstate)
        if n:
            return "unit %s, scope %s %s, but %d process(es) marked RM_ROLE_UNIT=%s still run" % (
                ustate, scope, sstate, n, run["marker"])
    return ustate


def after_slots(after_cfg, job, now):
    """Pure. The after_role's slots this scheduled job may follow, newest first: its slots at or before the job's slot
    today, then the previous calendar day's (prev_day) after the job's slot time (24 h back at most). -> slot_key()s
    ("YYYY-MM-DD HH:MM" / "YYYY-MM-DD Wed HH:MM", the done/run keys), empty when it has no slots."""
    mine = slot_epoch(now, job["slot"])
    keys = []
    for day in (now, prev_day(now)):
        for t, _, _ in slots(after_cfg, day):
            e = slot_epoch(day, t)
            if mine - 86400 < e <= mine:
                keys.append((e, slot_key(day, t)))
    return [k for _, k in sorted(keys, reverse=True)]


def after_ready(cfg, rst, busy, job, now, after_cfg=None):
    """`after_role` (Conductor: "each after an Operations run", conductor.md; Producer: after the economy pass): a
    scheduled slot waits until that role's OWN scheduled run for the slot it follows (after_slots: Conductor 08:00 ->
    Operations 07:30 today, 20:00 -> 19:30) finished done, and none of its runs is in flight. An alarm run, or yesterday's run launched
    late, never counts (review round R, B). A parent that is not enabled holds every scheduled slot (review
    dispatcher-full #4). -> None when ready, else why it waits."""
    after = cfg.get("after_role")
    if not after or not job["slot"]:
        return None
    if not (after_cfg or {}).get("enabled"):
        # a disabled parent holds its dependent: a run it finished before it was disabled does not stand in for the
        # checks it no longer makes (review dispatcher-full #4)
        return "%s is not enabled" % after
    if after in busy:
        return "an %s run is still going" % after
    keys = after_slots(after_cfg or {}, job, now)
    if not keys:
        return "%s has no scheduled slots to follow" % after
    ars = rst.get(after) or {}
    for key in keys:
        mine = [r for r in ars.get("runs") or [] if r.get("slot") == key and r.get("mode") != "alarm"]
        if any(r.get("state") == "done" for r in mine):
            return None
        if mine:
            return "the %s %s run ended %s" % (after, key, mine[-1].get("state"))
        how = (ars.get("done") or {}).get(key)
        if how and str(how).startswith("covered by "):
            # an incident run took this slot's place (covered_slot): its own run stands in for the slot's
            cov = [r for r in ars.get("runs") or [] if r.get("slot") == str(how)[len("covered by "):]]
            if any(r.get("state") == "done" for r in cov):
                return None
            return "the %s %s slot was covered by a run that %s" % (
                after, key, ("ended " + str(cov[-1].get("state"))) if cov else "is not on record")
        if how:
            return "the %s %s slot was not run (%s)" % (after, key, how)
        return "the %s %s run has not run yet" % (after, key)
    return "%s has no scheduled slots to follow" % after


def decide_roles(sch, st, obs, now, act, busy=None, gate=None):
    """Mutates st["roles"]; calls act(**kw) per action. obs needs: ops() -> status dict|None, account() -> label|None,
    unit_state(unit) -> str, result(run) -> dict|None, off(path) -> first line|None. busy = supervise_roles()'s
    answer (run here when the caller did not). gate("role_launch") -> (go, pick) is the dispatcher's account pick
    (account_pick.py), asked last, at the moment of release: a held launch keeps its slot due (it is missed only
    after slot_late_s, like any wait)."""
    if busy is None:
        busy = supervise_roles(sch, st, obs, now, act)
    rst = st.setdefault("roles", {})
    by_name = roles_by_name(sch)
    reading_cache = {}
    tick_launch = {}      # role -> the unit decide is launching now, until its role_launch action is built (V7)

    def reading(model=None):
        # one status.json read per tick: the alarm keys come from the same snapshot the reading judged (review night r3);
        # a role's model reads the lower of the all-models and that model's weekly limit (same snapshot)
        if "r" not in reading_cache:
            reading_cache["s"] = obs["ops"]()
            reading_cache["acct"] = obs["account"]()
            reading_cache["r"] = ops_reading(reading_cache["s"], reading_cache["acct"], now,
                                             sch.get("ops_stale_s", OPS_STALE_S))
        if not model:
            return reading_cache["r"]
        key = ("r", model)
        if key not in reading_cache:
            reading_cache[key] = ops_reading(reading_cache["s"], reading_cache["acct"], now,
                                             sch.get("ops_stale_s", OPS_STALE_S), model=model)
        return reading_cache[key]

    # a role that runs after another is decided after it, so the one it follows is marked/launched first (R, B)
    bad = [r for r in sch.get("roles") or [] if not isinstance(r, dict)]
    if bad:
        act(do="alarm", kind="role:schedule", note=True,
            why="%d roles entr(y/ies) in the schedule are not mappings (%s): skipped; the other roles are decided"
            % (len(bad), ", ".join(type(r).__name__ for r in bad)))
    odd = [role_shape_error(r) for r in sch.get("roles") or [] if isinstance(r, dict) and role_shape_error(r)]
    if odd:
        act(do="alarm", kind="role:schedule:shape", note=True,
            why="%d roles entr(y/ies) in the schedule cannot be keyed or ordered (%s): skipped; the other roles are "
            "decided" % (len(odd), "; ".join(odd)))
    roles = decide_order([r for r in sch.get("roles") or [] if role_shape_error(r) is None])
    def one(role):
        name = role.get("name", "?")
        # a role switched off asks nothing: its request would be refused and its chain given back, every tick
        if role.get("chain_stages") is True and (obs.get("off") or (lambda p: None))(
                wsl_path(role.get("off_file") or "")) is None:
            chain_sweep(name, rst.setdefault(name, {}), dict(ROLE_DEFAULTS, **role), now, act,
                        obs.get("stage_concepts") or stage_concepts, obs.get("rejection_parked"))
        if isinstance(rst.get(name), dict):
            chain_pop(rst[name], now)
        req = (rst.get(name) or {}).get("run_now") if isinstance(rst.get(name), dict) else None
        if not role.get("enabled") and not req:
            old = rst[name].pop("resume", None) if isinstance(rst.get(name), dict) else None
            if isinstance(old, dict):     # a disabled role resumes nothing later, unannounced
                act(do="role_hold", role=name, ticket=old.get("item"), note=True,
                    why="%s resume of %s dropped: the role is disabled; its work stays in session %s" % (
                        name, old.get("unit"), old.get("session")))
            return
        missing = [k for k in LAUNCH_KEYS if not role.get(k)]
        if missing:
            act(do="alarm", kind="role:" + name, note=True, conductor_log=True, why="role %s is enabled but cannot be launched: no %s in the schedule"
                % (name, ", ".join(missing)))
            return
        cfg = dict(ROLE_DEFAULTS, **role)
        if (req or {}).get("runner"):
            cfg["runner"] = req["runner"]
        if cfg.get("runner") == "codex":
            cfg.update(daily_token_cap=None, token_aware=False)
        if role.get("enabled") and cfg.get("after_role") and not (by_name.get(cfg["after_role"]) or {}).get("enabled"):
            act(do="alarm", kind="role:%s:after" % name, ticket=role["ledger_item"], note=True,
                blind=blind(name, "after_disabled"),
                why="role %s runs only after a %s run, and %s is not enabled: its scheduled checks will not run"
                % (name, cfg["after_role"], cfg["after_role"]))
        rs = rst.setdefault(name, {})
        rs.setdefault("done", {})
        rs.setdefault("runs", [])
        try:
            validate_role(cfg)
            today = slots(cfg, now)
            if cfg.get("after_role"):
                slots(dict(ROLE_DEFAULTS, **(by_name.get(cfg["after_role"]) or {})), now)
        except ValueError as e:
            act(do="alarm", kind="role:%s:schedule" % name, ticket=role["ledger_item"], note=True,
                blind=blind(name, "schedule_unreadable"),
                why="role %s NOT RUN: its schedule entry is unreadable: %s" % (name, e))
            return
        # ---- the pipeline's pause: a pipeline role (chain_stages) starts nothing, a resume or a slot included; a
        # run-now on a paused concept is refused at its own check below (owner_held)
        if cfg.get("chain_stages") is True and pipeline_held(
                name, rs, (rs.get("resume") or {}).get("concept") if isinstance(rs.get("resume"), dict) else None, now, act):
            return
        # ---- a run the account cut off after real work goes first, resumed in its own session (account_death)
        if rs.get("resume") and not req and obs["off"](wsl_path(role.get("off_file") or "")) is None \
                and resume_due(name, rs, cfg, now, act, busy, gate, resume_account(obs), tick_launch):
            return
        # ---- what is due now
        due = []
        for i, (hhmm, mode, cap) in enumerate([] if req else today):      # a run-now goes first; slots next tick
            key = slot_key(now, hhmm)
            t = slot_epoch(now, hhmm)
            if key in rs["done"] or now < t:
                continue
            if now - t > cfg["slot_late_s"]:
                rs["done"][key] = "missed"
                act(do="role_hold", role=name, why="%s slot %s missed (tick %d s late > slot_late_s)%s"
                    % (name, hhmm, now - t, ("; it waited: " + rs["waiting"][1]) if (rs.get("waiting") or [None])[0]
                       == key else ""))
                continue
            due.append({"key": key, "slot": hhmm, "first": i == 0, "mode": mode, "cap": cap,
                        "item": role["ledger_item"], "trigger": "slot %s local" % hhmm})
        if role.get("alarm_runs") and not req:
            # alarms_seen holds the OPEN alarms a run already covered (or a cap/off switch passed over). It is
            # pruned to what is open now, so an alarm that clears is eligible again when it re-crosses (review W, W1).
            # Read only from a MEASURED reading with a readable alarms dict: a blind one would prune every key and
            # re-run every open alarm when it reads again (review R, C). No baseline: alarms already open when the
            # role is first enabled run once. One alarm run covers every unseen open alarm, at most one per
            # alarm_run_gap_s.
            open_items = alarm_reading((reading_cache["s"] or {}).get("alarms")) if reading()["state"] == "MEASURED" \
                else None
            if open_items is None:
                if not rs.get("alarm_blind"):
                    act(do="role_hold", role=name, why="%s alarm runs held: %s; none launches until both read" % (
                        name, reading()["why"] if reading()["state"] != "MEASURED"
                        else "ops_watch alarms unreadable in status.json"))
                rs["alarm_blind"] = True
            else:
                rs.pop("alarm_blind", None)
                rs["alarms_seen"] = [k for k in rs.get("alarms_seen") or [] if k in open_items]
                if rs.get("slot_alarms"):       # cleared mid-run: its re-crossing is news to the run that held it
                    rs["slot_alarms"]["keys"] = [k for k in rs["slot_alarms"]["keys"] if k in open_items]
                fresh = [k for k in open_items if k not in rs["alarms_seen"]]
                # back under the line, clearing (OPS_ROLE_SHRINK_RUN_COST): no paid run for a reading that recovered;
                # left unseen, so a re-breach (clear_seen back to 0) is due at once and a clear prunes it
                rec = sorted(recovering_keys((reading_cache["s"] or {}).get("alarms")) & set(fresh))
                if rec:
                    fresh = [k for k in fresh if k not in rec]
                    if rs.get("alarm_recover_hold") != rec:      # journal each recovering set once
                        act(do="role_hold", role=name, why="%s alarm run for %s waits: its reading is already back "
                            "under the line (ops_watch clear_seen >= 1); it clears after its clear passes, a "
                            "re-breach makes it due" % (name, ", ".join(rec)))
                    rs["alarm_recover_hold"] = rec
                else:
                    rs.pop("alarm_recover_hold", None)
                # a repeat alarm a program answers (RIMMANDRAKE_QUIET_OPS_REPEATS_AGING_COUNTS_AS_NEWS, owner's card
                # 2026-11-19): its banded program route reads in band, so the runbook line is noted on its item once
                # and no run is bought; left unseen, so the tick its reading leaves the band launches the run
                prog = program_answered(reading_cache["s"])
                pa = sorted(k for k in fresh if k in prog)
                if pa:
                    fresh = [k for k in fresh if k not in prog]
                    for k in pa:
                        if k not in (rs.get("program_noted") or []):
                            act(do="role_hold", role=name, note=True, ticket=prog[k][0] or role["ledger_item"],
                                why="%s alarm %s: program answer, no run: %s" % (name, k, prog[k][1]))
                rs["program_noted"] = sorted(k for k in set(rs.get("program_noted") or []) | set(pa) if k in open_items)
                if not rs["program_noted"]:
                    rs.pop("program_noted")
                # daily limits, held as data in the schedule (review X, X1): at most alarm_runs_per_alarm_per_day runs
                # for one alarm key and alarm_runs_per_day alarm runs in all, so a flapping alarm cannot make a paid
                # run every cycle. Absent = no limit. Limited keys stay unseen: they wait for tomorrow (or clearing).
                ad = rs.get("alarm_day") if (rs.get("alarm_day") or {}).get("day") == day_of(now) else \
                    {"day": day_of(now), "n": 0, "keys": {}}
                per_key, per_day = cfg.get("alarm_runs_per_alarm_per_day"), cfg.get("alarm_runs_per_day")
                if cfg.get("caps_advisory") is True:
                    # no daily COUNT holds a maintenance run (owner 2026-11-02): every new alarm gets its run. The
                    # per-alarm limit stays: the same alarm flapping is not a new reading (the slot checks read it)
                    per_day = None
                if fresh and per_day is not None and ad["n"] >= int(per_day):
                    capped = fresh
                    fresh = []
                elif fresh and per_key is not None:
                    capped = [k for k in fresh if ad["keys"].get(k, 0) >= int(per_key)]
                    fresh = [k for k in fresh if k not in capped]
                else:
                    capped = []
                if capped and rs.get("alarm_limit_hold") != [day_of(now)] + capped:     # journal each set once a day
                    rs["alarm_limit_hold"] = [day_of(now)] + capped
                    act(do="role_hold", role=name, why="%s alarm run for %s waits: the daily alarm-run limit is used "
                        "(alarm_runs_per_alarm_per_day %s, alarm_runs_per_day %s); the scheduled running checks read "
                        "it" % (name, ", ".join(capped), per_key, per_day))
                gap = int(cfg.get("alarm_run_gap_s", ALARM_RUN_GAP_S))
                last = rs.get("alarm_last_run")
                if fresh and last is not None and now - last < gap:
                    if rs.get("alarm_gap_hold") != fresh:          # journal each waiting set once
                        act(do="role_hold", role=name, why="%s alarm run for %s waits: the last alarm run was %d s "
                            "ago (alarm_run_gap_s %d)" % (name, ", ".join(fresh), now - last, gap))
                    rs["alarm_gap_hold"] = fresh
                elif fresh:
                    rs.pop("alarm_gap_hold", None)
                    # an account alarm has no ledger item (it is Operations' alone, never on a seat queue: review V,
                    # V2): its run notes on the role's own ledger_item; mark() records every key the run covers
                    item = fresh[0].split(ALARM_WORSE_SEP)[0]
                    due.append({"key": "alarm " + fresh[0], "slot": None, "first": False, "mode": "alarm",
                                "cap": cfg.get("run_token_cap"), "seen": fresh,
                                "rows": alarm_rows((reading_cache["s"] or {}).get("alarms"), fresh),
                                "item": role["ledger_item"] if item.startswith(ALARM_KEY_PREFIX) else item,
                                "trigger": "ops_watch alarm " + ", ".join(fresh)})
        rs["done"] = {k: v for k, v in rs["done"].items() if k[:10] >= day_of(now - 2 * 86400)}
        if req:
            if now - float(req.get("at") or 0) > RUN_NOW_TTL_S:
                refuse_now(rs, "expired", now)
                act(do="role_hold", role=name, why="%s run-now by %s (%s) expired: not launchable for %d s (busy or "
                    "held); ask again" % (name, req.get("by"), req.get("why"), RUN_NOW_TTL_S))
                return
            if req.get("concept") and owner_held(name, rs, req["concept"], now, act):
                import pipeline_pause as PP     # a request asked before the hold or pause, or by hand: consumed, not run
                refuse_now(rs, "pipeline paused" if PP.blocks(req["concept"], now) else "owner hold", now)
                return
            due = [run_now_job(cfg, req, now)]
        if not due:
            return
        job = due[0]                                      # one launch per role per tick
        off = obs["off"](wsl_path(role.get("off_file") or ""))
        if off is not None:
            mark(rs, job, "off")
            refuse_now(rs, "off switch", now, job)
            act(do="role_hold", role=name, why="%s %s skipped: off switch %s (%s)" % (
                name, job["trigger"], role.get("off_file"), off or "no reason given"))
            return
        if name in busy:
            return                                      # one run at a time: wait for the running one
        if cfg.get("window_name") and obs.get("window_live"):
            # a standing window of this role (Conductor: the Remote Control window, conductor.md) writes the findings
            # itself: no headless `claude -p` beside it. Held, not marked: the slot waits (missed after slot_late_s).
            # Unreadable holds too. Journaled once per slot, not every tick.
            live, why = obs["window_live"](cfg["window_name"])
            if live is not False:
                if rs.get("window_hold") != job["key"]:
                    rs["window_hold"] = job["key"]
                    act(do="role_hold", role=name, why="%s %s not launched: %s (%s)" % (
                        name, job["trigger"], "conductor window live" if live else "window UNMEASURED",
                        "%s; the window does the check" % why if live else why))
                return
            rs.pop("window_hold", None)
        wait = after_ready(cfg, rst, busy, job, now, dict(ROLE_DEFAULTS, **(by_name.get(cfg.get("after_role")) or {})))
        if wait:
            if (rs.get("waiting") or [None])[0] != job["key"]:      # journal the wait once, not every tick
                act(do="role_hold", role=name, why="%s %s waits: runs after a finished %s run; %s" % (
                    name, job["trigger"], cfg["after_role"], wait))
            rs["waiting"] = [job["key"], wait]
            return
        rs.pop("waiting", None)
        r = codex_reading() if cfg.get("runner") == "codex" else reading(job_model(cfg, job)
                                                                          if cfg.get("model") else None)
        if r["state"] != "MEASURED" and cfg.get("degraded_reading_ok") is True:
            # the role that reports the problem must not be refused by it (owner-authority brief 2026-11-01, Operations
            # slot 07:30 REFUSED 'accounts.system.runway is absent'): launch, say so
            act(do="alarm", kind="role:%s:ops" % name, ticket=job["item"], note=True,
                why="%s %s LAUNCHED on a degraded ops reading: %s" % (name, job["trigger"], r["why"]))
            r = {"state": "MEASURED", "degraded": r["why"], "account": None, "at": "UNREADABLE", "runway": 0.0,
                 "runway_m": "UNMEASURED", "week_left": 0.0, "week_left_m": "UNMEASURED"}
        if r["state"] != "MEASURED":
            refuse_now(rs, "ops reading " + r["state"], now, job)
            act(do="alarm", kind="role:%s:ops" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: %s" % (name, job["trigger"], r["why"]))
            return
        stop = codex_stop(cfg, r)
        if stop:
            # the request stays pending: it launches once the weekly reset lifts the meter back over the line
            if (rs.get("codex_stop") or [None])[0] != job["key"]:
                act(do="alarm", kind="role:%s:codex_stop" % name, ticket=job["item"], note=True, conductor_log=True,
                    why="%s %s HELD: %s" % (name, job["trigger"], stop))
            rs["codex_stop"] = [job["key"], stop]
            return
        rs.pop("codex_stop", None)
        cv = covered_slot(rs, today, now, cfg.get("cover_window_s", COVER_WINDOW_S)) if (
            job.get("manual") or {}).get("covers_slot") else None
        if cv is not None:
            # it covers the next scheduled slot, so it IS that run: that slot's own mode and cap (07:30 is the economy
            # pass), the incidents first, then the slot's full check; never the memory page alone (review g2r2).
            cm, cc = next((m, c) for hh, m, c in today if hh == cv)
            job = dict(job, mode=cm, cap=cc, covers=cv, trigger=(job.get("incident") or {}).get("trigger", job["trigger"]) +
                       "; INCIDENT RUN that also covers the %s slot (%s): do the incidents first, then that slot's full "
                       "check" % (cv, cm))
        # advisory (owner 2026-11-02, e7069d65ba): "a token limit for operations must be advisory only. We can't have the
        # system crash because we couldn't afford to watch." No budget or daily cap refuses, delays, skips or shrinks
        # this role's run; overspend raises an immediate alarm instead (overspend_alarm)
        advisory = cfg.get("caps_advisory") is True
        if not job["cap"] and not advisory:
            refuse_now(rs, "no cap", now, job)
            act(do="alarm", kind="role:" + name, note=True, conductor_log=True, why="role %s has no token cap for %s" % (name, job["mode"]))
            return
        budget = int(job["cap"] or 0)
        spent = spent_today(rs, now)
        daily = role.get("daily_token_cap")           # 0 is a cap of zero; only absent (None) is no cap
        if advisory:
            if daily is not None and spent + budget > daily:
                overspend_day(name, rs, job.get("item") or cfg.get("ledger_item"), daily, spent, budget, now, act,
                              "%s %s LAUNCHED anyway (caps are advisory)" % (name, job["trigger"]))
            daily = None
        if daily is not None and (job["mode"] == "alarm" or job.get("manual")):
            # an alarm or run-now may spend only what the day's scheduled runs not yet run leave (review U, N3; X, X1)
            # an incident run (covers_slot) IS the next scheduled run when that slot is due within cover_window_s: it
            # reads the same open incidents first, so it takes that slot's share instead of asking the daily cap for a
            # second one (INCIDENTS_FIX_ONE_READER); a slot further off keeps its run and its reserve
            # (OPS_NIGHT_GAP_FILL_COVERED_SLOT)
            cover = covered_slot(rs, today, now, cfg.get("cover_window_s", COVER_WINDOW_S)) if (job.get("manual") or {}).get("covers_slot") else None
            reserve = sum(int(c) for hh, m, c in (today if role.get("enabled") else [])
                          if hh != cover
                          and c and slot_key(now, hh) not in rs["done"]
                          # a run-now does not keep budget for a slot already past its late window (it never runs)
                          and not (job.get("manual") and now - slot_epoch(now, hh) > float(cfg["slot_late_s"])))
            if job.get("manual") and spent + budget + reserve > daily:
                refuse_now(rs, "daily cap", now, job)
                act(do="alarm", kind="role:%s:cap" % name, ticket=job["item"], note=True,
                    why="%s %s REFUSED: daily_token_cap %d, %d used today + %d budget + %d kept for the day's "
                        "scheduled runs" % (name, job["trigger"], daily, spent, budget, reserve))
                return
            if (reserve or job["mode"] == "alarm") and spent + budget + reserve > daily:
                if rs.get("event_reserve_day") != day_of(now):          # journalled once a day; the run waits
                    rs["event_reserve_day"] = day_of(now)
                    act(do="role_hold", role=name, why="%s %s waits: the day's scheduled run(s) still to come keep "
                        "their share of the daily cap; it runs once they leave room" % (name, job["trigger"]))
                return
        if daily is not None and spent + budget > daily:
            mark(rs, job, "daily cap")
            act(do="alarm", kind="role:%s:cap" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: daily_token_cap %d, %d used today + %d budget" % (
                    name, job["trigger"], daily, spent, budget))
            return
        go, pk = gate("role_launch") if gate and cfg.get("runner", "claude") == "claude" else (True, {})
        if not go:
            if rs.get("account_hold") != job["key"]:     # journal the hold once per job, not every tick
                act(do="role_hold", role=name, why="%s %s held for the account switch: %s" % (
                    name, job["trigger"], pk.get("why")))
            rs["account_hold"] = job["key"]
            return
        rs.pop("account_hold", None)
        unit = "rm-role-%s-%d" % (name.lower(), int(now))
        concept = (job.get("manual") or {}).get("concept")
        packet = None
        mend = {}
        if concept:
            # a stage-machine role (the Designer): the launcher, not the model, picks the instructions, holds the
            # task budget and refuses a run the state does not allow (designer_stage.py; GPT review 2026-11-03 §2-3)
            try:
                packet, budget = (obs.get("stage_open") or stage_open)(concept, unit, budget)
            except Exception as e:  # noqa: BLE001 - designer_stage.Refused, or an unreadable state: said, not run
                refuse_now(rs, "stage machine: %s" % e, now, job)
                act(do="alarm", kind="role:%s:stage_refused" % name, ticket=job["item"], note=True,
                    why="%s run-now on %s REFUSED by designer_stage: %s" % (name, concept, str(e)))
                return
            pre = (obs.get("coverage_pre") or coverage_pre)(concept)
            if pre:
                job = dict(job, pre_launch=pre)
            else:       # after the coverage judge's refusal: the session that holds the design mends it (designer_mend)
                mend = mend_plan(rs, cfg, job, concept, now, obs.get("projects"))
        # built before anything is consumed: a raise here leaves the slot due (review V, V7)
        message = prompt(cfg, job["mode"], job["trigger"], r, budget, job["cap"] or 0, spent, unit,
                         rows=job.get("rows"), reasons=job.get("reasons"),
                         scope=launch_scope(job))
        if packet:
            message += "\n\n" + packet
        if mend.get("session"):
            import designer_mend as DM
            message = DM.head(mend, unit) + "\n\n" + message
        tick_launch[name] = unit
        # what the launch consumes, so execute can give it back if the launch does not happen (review U, N6)
        rs["pending_launch"] = {"unit": unit, "mode": job["mode"], "key": job["key"],
                                "done": rs["done"].get(job["key"]), "had_done": job["key"] in rs["done"],
                                "alarms_seen": rs.get("alarms_seen"),
                                "alarm_day": json.loads(json.dumps(rs.get("alarm_day"))),
                                "alarm_last_run": rs.get("alarm_last_run")}
        if job.get("manual"):
            cover = covered_slot(rs, today, now, cfg.get("cover_window_s", COVER_WINDOW_S)) if (job["manual"] or {}).get(
                "covers_slot") else None
            if cover is not None:
                ck = slot_key(now, cover)
                rs["pending_launch"]["covered"] = [ck, rs["done"].get(ck), ck in rs["done"]]
                rs["done"][ck] = "covered by " + job["key"]
            rs["pending_launch"]["run_now"] = rs.get("run_now")
            note_chain_unit(rs, unit, rs.get("run_now"), now)
            rs["run_now_last"] = dict(rs.pop("run_now"), outcome="launched", unit=unit, decided=now)
        mark(rs, job, "launch")
        if (job.get("slot") or cv is not None) and role.get("alarm_runs") and reading()["state"] == "MEASURED":
            # (a run covering a slot diagnoses that slot's alarms too: unmarked, they would buy another run, g2r3)
            # finish_slot_alarms: what this scheduled run diagnoses, marked when it finishes done
            keys = alarm_reading((reading_cache["s"] or {}).get("alarms"))
            if keys:
                rs["slot_alarms"] = {"unit": unit, "keys": keys}
        if job["mode"] == "alarm":
            rs["alarm_last_run"] = now        # the gap runs from launched alarm runs only, not from passed-over ones
            ad = rs.get("alarm_day") if (rs.get("alarm_day") or {}).get("day") == day_of(now) else \
                {"day": day_of(now), "n": 0, "keys": {}}
            ad["n"] += 1
            for k in job.get("seen") or []:
                ad["keys"][k] = ad["keys"].get(k, 0) + 1
            rs["alarm_day"] = ad
        act(do="role_launch", role=name, unit=unit, ticket=job["item"], note=True, mode=job["mode"], budget=budget,
            slot=job["key"], seat=role["seat"], run_max_s=max_s_of({}, cfg), account=pk.get("account"),
            why="%s %s, budget %d, %d used today, unit %s, model %s%s" % (
                name, job["trigger"], budget, spent, unit, job_model(cfg, job),
                (", account %s (%s)" % (pk["account"], pk["state"])) if pk.get("account") else "") + (
                    "" if not mend.get("owed") else "; mend resumes session %s: %s" % (mend["session"], mend["why"])
                    if mend.get("session") else "; the mend starts fresh: %s" % mend["why"]),
            **({"resume": mend["session"], "resume_of": mend["of"]} if mend.get("session") else {}),
            # the blind item's note: role, mode, unit and a fixed outcome; execute swaps the outcome for the true one
            # (held / failed: review V, V4), never for a reason or an error text (review dispatcher-full #2)
            blind=blind(name, "launched", job["mode"], unit),
            message=message, **dict({"run_now": job["manual"], "pre_launch": job.get("pre_launch")} if job.get("manual")
                                     else {}, **({"concept": concept} if concept else {})))
        tick_launch.pop(name, None)
        busy.add(name)            # launched this tick: a role that runs after it waits for it (R, B)

    for role in roles:
        # one role's bad schedule value (or a malformed reading) skips THAT role with an alarm; the other roles are
        # still decided and the supervise actions already built still execute (review round U, N5)
        try:
            one(role)
        except Exception as e:  # noqa: BLE001
            nm = role.get("name", "?") if isinstance(role, dict) else "?"
            unit = tick_launch.pop(nm, None)
            if unit and isinstance(rst.get(nm), dict):
                unlaunch(rst[nm], unit)     # it raised after consuming its slot/alarm: give it back (V7)
            act(do="alarm", kind="role:%s:schedule" % nm, ticket=(role.get("ledger_item") if isinstance(role, dict)
                                                                 else None), note=True,
                why="role %s NOT RUN this tick: deciding it raised %s: %s" % (nm, type(e).__name__, str(e)))


def unlaunch(rs, unit):
    """Give back what decide consumed for the launch of `unit` (slot or alarm mark) when
    the launch did not happen: a failed systemd-run, or execute's off/PAUSE recheck. -> True if rolled back."""
    p = rs.get("pending_launch") or {}
    if p.get("unit") != unit:
        return False
    rs.pop("pending_launch", None)
    if p["mode"] == "resume":                 # a resume that did not launch is pending again, not lost
        rs["resume"] = p["resume"]
        return True
    if p["mode"] == "alarm":
        rs["alarms_seen"] = p["alarms_seen"]
        if p.get("alarm_day") is None:
            rs.pop("alarm_day", None)
        else:
            rs["alarm_day"] = p["alarm_day"]
        if p.get("alarm_last_run") is None:
            rs.pop("alarm_last_run", None)
        else:
            rs["alarm_last_run"] = p["alarm_last_run"]
    elif p["had_done"]:
        rs.setdefault("done", {})[p["key"]] = p["done"]
    else:
        rs.setdefault("done", {}).pop(p["key"], None)
    if p.get("covered"):                      # the slot an incident run covered is due again
        ck, was, had = p["covered"]
        if had:
            rs.setdefault("done", {})[ck] = was
        else:
            rs.setdefault("done", {}).pop(ck, None)
    if p.get("run_now") is not None:          # a run-now that did not launch is asked again, not lost
        rs["run_now"] = p["run_now"]
        rs.pop("run_now_last", None)
    return True


def _open_alarms(alarms):
    """Pure. -> [(key, aid, row)] for every OPEN alarm with a key (alarm_keys' rule)."""
    out = []
    for aid, a in (alarms or {}).items() if isinstance(alarms, dict) else ():
        if not isinstance(a, dict) or a.get("state") != "OPEN":
            continue
        n = a.get("worse_n")
        tail = "%s%d" % (ALARM_WORSE_SEP, n) if isinstance(n, int) and not isinstance(n, bool) and n > 0 else ""
        if a.get("item"):
            out.append((a["item"] + tail, aid, a))
        elif a.get("for") == "Operations":
            out.append((ALARM_KEY_PREFIX + str(aid) + tail, aid, a))
    return out


def program_answered(status, table=None):
    """Pure but for reading alarm_routes.json. -> {alarm key: (its ledger item or None, note text)} for each OPEN alarm
    whose every alarm row under that key is on a banded program route reading MEASURED inside its band
    (incident.program_answer): the program writes the runbook line and no alarm run is bought. A routing table that
    does not read answers nothing, so every alarm keeps its run (never a quiet answer on a blind table)."""
    if not isinstance(status, dict):
        return {}
    try:
        import incident as IN
        table = table or IN.load_table()
    except Exception:  # noqa: BLE001 - no table read: no program answers
        return {}
    pts = status.get("points") if isinstance(status.get("points"), dict) else {}
    out, agent = {}, set()
    for k, aid, a in _open_alarms(status.get("alarms")):
        metric = str(aid).split(":", 1)[1] if ":" in str(aid) else str(aid)
        rt = IN.route_of(table, metric)
        ans = IN.program_answer(rt, pts.get(metric))
        if not ans or ans[0] != "program":
            agent.add(k)
            continue
        out[k] = (a.get("item"), "%s (%s; an agent run is called once it leaves the band)" % (rt["runbook"], ans[1]))
    return {k: v for k, v in out.items() if k not in agent}


def alarm_keys(alarms):
    """Pure. ops_watch alarms.json -> the keys of its OPEN alarms: the ledger item filed for it, or, for an alarm
    filed for Operations alone (no ledger item: review V, V2), ALARM_KEY_PREFIX + its alarm id."""
    return {k for k, _aid, _a in _open_alarms(alarms)}


def recovering_keys(alarms):
    """Pure. -> the keys of OPEN alarms whose latest reading is already back under the line (ops_watch's clear
    hysteresis: clear_seen >= 1, it clears after clear_passes such readings; a reading over the line resets it to 0).
    OPS_ROLE_SHRINK_RUN_COST: run 1793686300 (486k weighted) paid for queues.artpipe.stalled_min in exactly this window.
    Such a key buys no alarm run while it recovers; it is not marked seen, so a re-breach makes it due again."""
    out = set()
    for k, _aid, a in _open_alarms(alarms):
        n = a.get("clear_seen")
        if isinstance(n, int) and not isinstance(n, bool) and n >= 1:
            out.add(k)
    return out


def alarm_rows(alarms, keys):
    """Pure. -> one line per alarm key in `keys` (aid, title, since, last reading), in key order, so an alarm run
    starts from the rows instead of spending turns finding them in status.json (OPS_ROLE_SHRINK_RUN_COST)."""
    by = {k: (aid, a) for k, aid, a in _open_alarms(alarms)}
    out = []
    for k in keys:
        if k not in by:
            continue
        aid, a = by[k]
        told = a.get("told") if isinstance(a.get("told"), dict) else {}
        out.append("- %s = %s: %s (since %s, reading %s)" % (k, aid, str(a.get("title") or ""),
                                                              a.get("since"), told.get("v")))
    return out


def alarm_reading(alarms):
    """Pure. -> the sorted keys of the OPEN alarms, or None when the alarms are not readable (absent, not a mapping,
    or ops_watch's UNREADABLE marker): None never prunes alarms_seen."""
    if not isinstance(alarms, dict) or "_alarm_state" in alarms:
        return None
    return sorted(alarm_keys(alarms))


def run_now_cap(cfg, mode):
    """The token cap a run-now of `mode` runs under: the cap the same mode's scheduled run has (slots()). None = the
    role has no run of that mode (the request is refused)."""
    if mode == "economy":
        return cfg.get("economy_token_cap")
    if mode == "quick":
        return cfg.get("quick_token_cap") if "quick_token_cap" in cfg else None
    return cfg.get("run_token_cap") if mode == "run" else None




def run_now_request(sch, a, now):
    """Pure. A run-now request from its CLI fields (role, by, why, mode, concept) -> the
    record kept in st["roles"][role]["run_now"]. Raises ValueError naming the bad field."""
    role = next((r for r in sch.get("roles") or [] if isinstance(r, dict) and r.get("name") == a.get("role")), None)
    if role is None:
        raise ValueError("no role %r in the schedule" % (a.get("role"),))
    by, why = str(a.get("by") or "").strip(), str(a.get("why") or "").strip()
    if not by:
        raise ValueError("--by: say which seat asks")
    if not why:
        raise ValueError("--why: say why this run is asked for")
    cfg = dict(ROLE_DEFAULTS, **role)
    mode = a.get("mode") or ("quick" if "quick_token_cap" in cfg else "run")
    if mode not in RUN_NOW_MODES or run_now_cap(cfg, mode) is None:    # 0 is a cap; the launch applies it (g2r4)
        raise ValueError("mode %r: a run-now runs one of %s that %s has a token cap for" % (
            mode, "/".join(RUN_NOW_MODES), role["name"]))
    concept = str(a.get("concept") or "").strip() or None
    if cfg.get("stage_machine") == "designer_stage":
        if not concept:
            raise ValueError("--concept: %s runs one concept's recorded stage (design/concepts/<Mod>)" % role["name"])
        if role_clones.is_role_clone(cfg.get("clone")) and role_clones.missing_why(cfg["clone"]):
            raise ValueError(role_clones.missing_why(cfg["clone"]))     # not "no stage.json": nothing was looked in
        if not os.path.isfile(os.path.join(concept_dir(cfg, concept), "stage.json")):
            raise ValueError("--concept %s has no stage.json (designer_stage.py init it first)" % concept)
        concept = concept_dir(cfg, concept)
    elif concept:
        raise ValueError("--concept is for a stage-machine role, not %s" % role["name"])
    selected = a.get("runner")
    if selected is not None and selected not in ("claude", "codex"):
        raise ValueError("runner must be claude or codex")
    return dict({"at": now, "by": by, "why": why, "mode": mode},
                **({"runner": selected} if selected else {}), **({"concept": concept} if concept else {}))


def with_parent(req, env):
    """Pure. A run-now asked from inside a detached run carries that run's unit as `parent` (RM_DETACHED_UNIT): the
    launch records it on the run and in stage.json, so a void of the detached run takes exactly the Designer runs and
    judges it launched (run_void.children; RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS)."""
    p = str((env or {}).get("RM_DETACHED_UNIT") or "").strip()
    return dict(req, parent=p) if p else req


def run_now_job(cfg, req, now):
    """Pure. The due job for a run-now request: no slot (no slot gate, no after_role wait), its
    mode's cap, no pre-launch steps."""
    trigger = "run-now by %s: %s" % (req.get("by"), req.get("why"))
    cap = run_now_cap(cfg, req.get("mode"))
    incident = None
    if req.get("covers_slot") and cfg.get("incident_token_cap") is not None:
        # an incident run reads the memory page and its incidents, not the whole digest, at a smaller budget
        # (design/RimMandrake/operations_metronome_strategy_2026-11-02.md §5, §8 step 2; OPS_MEMORY_VET_THEN_WIRE_AFTER_WATCH).
        # One that covers a scheduled slot IS that run: decide_roles gives it back the full cap and trigger (incident)
        incident = {"cap": cap, "trigger": trigger}
        cap = cfg["incident_token_cap"]
        trigger += ("; INCIDENT RUN for %s: read memory.md (beside digest.md) and these incidents, not the whole "
                    "digest (your instructions, Incident runs)" % (", ".join(map(str, req.get("ids") or [])) or
                                                                    "the open incidents"))
    return {"key": "%s run-now %s" % (day_of(now), iso(req.get("at") or now)),
            "slot": None, "first": False, "mode": req.get("mode") or "run", "cap": cap,
            "item": cfg["ledger_item"], "trigger": trigger, "manual": req, "pre_launch": None, "incident": incident,
            "reasons": list(req.get("reasons") or [])}


COVER_WINDOW_S = 7200


def covered_slot(rs, today, now, window_s=COVER_WINDOW_S):
    """Pure. The slot (as the schedule writes it) an incident run covers: today's first scheduled run still to come,
    and only when it is due within `window_s` (role key cover_window_s); None otherwise. A slot further off keeps its
    run and its share of the daily cap: on 11-01 a 14:16 incident run covered the 19:30 slot and nothing judged for
    ~17 h (OPS_NIGHT_GAP_FILL_COVERED_SLOT)."""
    for hh, m, c in today:
        if c and slot_key(now, hh) not in rs.get("done", {}) and slot_epoch(now, hh) > now:
            return hh if slot_epoch(now, hh) - now <= window_s else None
    return None


# a chained run-now consumed with no launch for one of these gives its chain back (it never started: no trial spent,
# owner 2026-11-18); chain_ask asks nothing while a hold or pause stands, and the sweep nothing while the role is off,
# so none is re-asked in a loop. Every other refusal (the stage machine, caps, ops reading) keeps its chain: the
# sweep re-asks a ready concept every tick, and the daily chain cap is the brake on that ask-and-refuse loop
# (design/specs/2026-11-19-void-counters/boundary.md)
CHAIN_BACK_ON = ("expired", "pipeline paused", "owner hold", "off switch")


def refuse_now(rs, how, now, job=None):
    """A run-now refused (or expired) is consumed, said once: one-shot, never retried by the ticks. A no-op for
    a scheduled job. One refused for a CHAIN_BACK_ON cause gives its chain back."""
    if job is not None and not job.get("manual"):
        return
    req = rs.pop("run_now", None)
    if req is not None:
        rs["run_now_last"] = dict(req, outcome="refused: " + how, decided=now)
        if how in CHAIN_BACK_ON and isinstance(req, dict) and req.get("chain_key"):
            give_back_req(rs, req)


def concept_dir(cfg, concept):
    """A run-now's concept folder, resolved against the role's own clone (where the Designer writes it)."""
    return concept if os.path.isabs(concept) else os.path.join(cfg.get("clone") or os.path.dirname(os.path.dirname(_SRC)), concept)


# budget: danger=a hung fetch holds the designer's judge; longest=3.7s (15 fetches sampled at load 20 to 52, 2026-11-24)
def judge_sync(concept, timeout=45, repos=None):
    """Fetch origin into every clone the judge reads before judging a concept: the Dispatcher's own (designer_stage's
    REPO, ~/rm/dispatch) and the concept's (the Designer's clone). designer_stage reads OWNER.jsonl from each working
    tree AND its origin/main (concept_tree.owner_lines), so a fetched ref is enough: no working tree is moved under a
    running Designer. DESIGNER_TURNS_FIX_LEFT_ON_THE_DOORSTEP: ~/rm/dispatch was behind origin and refused
    "WAITING_OWNER: no new owner event" with his answer already published. -> [notes] (a failed fetch is said, and the
    judge goes on with what is on disk: refusing every run because the network blinked is not better)."""
    import designer_stage as DS
    notes = []
    if os.environ.get("RM_JUDGE_SYNC") == "0":     # a selftest's fixture concept: no network fetch of a real clone
        return notes
    for repo in dict.fromkeys(r for r in (repos or (DS.REPO, DS.clone_of(concept))) if r):
        try:
            r = subprocess.run(["git", "-C", repo, "fetch", "-q", "origin", "main"], capture_output=True, text=True,
                               timeout=timeout)
            if r.returncode != 0:
                notes.append("fetch %s exited %d: %s" % (repo, r.returncode, (r.stderr or "").strip()))
        except (OSError, subprocess.SubprocessError) as e:
            notes.append("fetch %s: %s" % (repo, e))
    return notes


def stage_open(concept, unit, budget, commit=False, sync=True, parent=None):
    """designer_stage.open_run: (packet, run budget) or raises. decide previews (commit False, nothing written);
    execute commits just before systemd-run (DESIGNER_STAGES_REBUILD_LAUNCHER_HOLDS_LEASH). Fetches first (judge_sync)."""
    import designer_stage as DS
    notes = judge_sync(concept) if sync else []
    try:
        return DS.open_run(concept, unit, budget or None, repo=DS.REPO, commit=commit,
                           **({"parent": parent} if parent else {}))
    except DS.Refused as e:
        if notes:
            raise DS.Refused("%s (judged without a fresh origin: %s)" % (e, "; ".join(notes)))
        raise


def stage_runner(concept, unit, selected):
    """Persist the runner before a process can start, including interrupted runs."""
    import designer_stage as DS
    st = DS.load_state(concept)
    if (st.get("running") or {}).get("run") != unit:
        raise DS.Refused("stage runner does not name the open run")
    st["runner"] = st["running"]["runner"] = selected
    DS.write_json(DS.state_path(concept), st)


def coverage_pre(concept):
    """The pre-launch step of a Designer run on a concept at stage 5: the coverage judge (coverage_judge.py), so the lock
    run starts signed or with the judge's verdict on file (CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED: nothing used to start
    the signer). None at any other stage. The step itself is a no-op when already signed or the exam does not pass."""
    import designer_stage as DS
    try:
        st = DS.load_state(concept)
    except Exception:  # noqa: BLE001 - stage_open already read it; an unreadable state here adds no step
        return None
    if st.get("stage") != 5 or st.get("status") == "locked":
        return None
    return [["python3", "src/RimMandrake/rimflow/role_launch.py", "stage5-judge", concept],
            ["python3", "src/RimMandrake/rimflow/role_launch.py", "stage5-program", concept]]


def mend_plan(rs, cfg, job, concept, now, projects=None):
    """designer_mend.plan for the Designer run `job` asks on `concept`: the session it resumes after the coverage judge's
    refusal, or why it starts fresh. Never raises: a state it cannot read starts the run fresh, and the launch says so."""
    import designer_mend as DM
    import designer_stage as DS
    try:
        st = DS.load_state(concept)
        last = ([r for r in st.get("results") or [] if isinstance(r, dict)] or [{}])[-1]
        if last.get("stage") != DM.JUDGE or last.get("outcome") != "return":
            return {"owed": False}
        runner = (job.get("manual") or {}).get("runner") or cfg.get("runner", "claude")
        import concept_tree as CT
        try:
            tree = CT.tree_hash(CT.load(concept))
        except (OSError, ValueError):
            tree = None     # the verdict then stands unchecked against the tree, as program_result reads it
        verdict = DS.read_json(os.path.join(concept, "coverage_verdict.json"))
        if runner != "claude":
            return dict(DM.plan([], concept, st, verdict, now, None, tree=tree), session=None,
                        why="a %s run has no claude session to resume" % runner)
        import mod_model as MM
        role = MM.role_for(dict(cfg, model=job_model(cfg, job)), os.path.basename(os.path.normpath(str(concept))))
        return DM.plan(rs.get("runs"), concept, st, verdict, now, role["model"], projects=projects, tree=tree)
    except Exception as e:  # noqa: BLE001 - said on the launch; the run starts fresh, as before
        if not os.path.exists(os.path.join(str(concept), "stage.json")):
            return {"owed": False}
        return {"owed": True, "session": None, "why": "could not look: %s: %s" % (type(e).__name__, e)}


def session_part(rs, run, tok, res):
    """-> the weighted tokens `run` itself spent, when it resumed another run's session (a concept run with resume_of). A
    claude result of a resumed session is the whole session so far (detached_helper.own_part, 26 of 26); a transcript
    measure and a spend_watchdog stop already count this launch only. None = UNMEASURED."""
    if not (run.get("concept") and run.get("resume_of")) or tok is None or run.get("token_source") == "transcript":
        return tok
    import detached_helper as DH
    had = [r.get("session_tokens") if finite(r.get("session_tokens")) else r.get("tokens")
           for r in rs.get("runs") or [] if r is not run and r.get("session") and r.get("session") == run.get("session")]
    had = [x for x in had if finite(x)]
    part, run["session_tokens"] = DH.session_part(tok, max(had) if had else None,
                                                  isinstance(res, dict) and res.get("stopped_by") == "spend_watchdog")
    return part


JUDGE_TIMEOUT_S = 5400  # budget: class=judge


def stage5_judge(concept, runner=None):
    """The first pre-launch step at stage 5: `coverage_judge.py run` only while the concept is still at stage 5 when the
    unit runs. The steps are fixed when the run is asked; a run asked at stage 5 can reopen stage 3 at its open (inputs
    changed), and the judge's skip there handed back an old advisory verdict and exited STOP_EXIT, so the stage-3
    Designer never started (Contagion 2026-11-16, RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING). The check
    lives here, not in coverage_judge.py: that file is part of the judge's calibrated brief. -> the step's exit code."""
    import designer_stage as DS
    try:
        stage = (DS.load_state(concept) or {}).get("stage")
    except Exception:  # noqa: BLE001 - the judge reads the concept itself and says why it cannot
        stage = 5
    if stage != 5:
        print("stage5-judge: %s is at stage %s, not 5: no judge, nothing held" % (os.path.basename(concept), stage))
        return 0
    run = runner or subprocess.run
    judge = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage_judge.py")
    # the judge bounds its own claude (coverage_judge.TIMEOUT_S); this bound only stops a hung step from holding the unit
    # --timeout: coverage_judge.TIMEOUT_S (1500 s) is 3.2 times the longest judge (462 s); its file is the calibrated brief,
    # and an edit of one number there costs a paid calibration
    return run(["python3", judge, "run", concept, "--timeout", str(JUDGE_TIMEOUT_S)], stdin=subprocess.DEVNULL, timeout=6 * 3600).returncode  # budget: class=judge


PRE_DONE_EXIT = 79     # a pre-step that did the run's work itself: the unit ends 0 and the model never starts


def stage5_program(concept, unit=None, sync=True):
    """The second pre-launch step at stage 5, after the judge (RIMMANDRAKE_CARRY_STAGE_FIVE_BY_PROGRAM_TEN_RELAY_RUNS):
    when designer_stage.program_result has the run's result from the verdict alone, write that result.json and close the
    open run through designer_stage.close_run with no model and 0 tokens. -> ("closed", line) | ("designer", why).
    A close that rejects it puts stage.json back as it was (the run open, nothing recorded but one history line) and the
    Designer runs as today. Raises only on an unreadable concept (main says "did not run" and lets the Designer run)."""
    import designer_stage as DS
    import concept_tree as CT
    st = DS.load_state(concept)
    run = (st.get("running") or {}).get("run")
    if not run or (unit and run != unit):
        return "designer", "the open run is %r, not this unit %r" % (run, unit)
    try:
        tree_now = CT.tree_hash(CT.load(concept))
    except (OSError, ValueError) as e:
        return "designer", "the tree is unreadable (%s)" % e
    verdict = DS.read_json(os.path.join(concept, "coverage_verdict.json"))
    res = DS.program_result(dict(st, tree_now=tree_now), verdict, run)
    if res is None:
        return "designer", "the verdict leaves something to decide (%s)" % (
            (verdict or {}).get("verdict") if isinstance(verdict, dict) else "no verdict")
    if sync:
        judge_sync(concept)            # the same fresh origin stage_close reads OWNER.jsonl from
    sp = DS.state_path(concept)
    with open(sp, "rb") as f:
        before = f.read()
    rp = os.path.join(concept, "result.json")
    DS.write_json(rp, res)
    ok, errs = DS.close_run(concept, run, 0, repo=DS.REPO)
    if ok:
        return "closed", "run %s closed by program: stage 5 %s%s, no model started" % (
            run, res["outcome"], " to stage 3" if res["outcome"] == "return" else "")
    with open(sp, "wb") as f:
        f.write(before)
    rej = os.path.join(concept, "result.%s.rejected.json" % DS.safe(run))
    if os.path.exists(rej):
        os.replace(rej, os.path.join(concept, "result.%s.program-rejected.json" % DS.safe(run)))
    st = DS.load_state(concept)
    DS.hist(st, "program_rejected", "run %s: the program's result was rejected (%s); the Designer runs" % (
        run, "; ".join(errs[:3])))
    DS.write_json(sp, st)
    return "designer", "close rejected the program's result: %s" % "; ".join(errs[:3])


def judge_stopped(run, now, obs):
    """-> the concept's coverage_stop ({at, why}) when the stage-5 coverage judge stopped it inside this run's window
    [run.at, now] and no model started (no transcript), else None: the run is harvested as before. An unreadable
    stage.json is None too (a failed run, alarmed, as before)."""
    try:
        st = (obs.get("stage_status") or stage_status)(run["concept"])
    except Exception:  # noqa: BLE001 - unread: harvested as before
        return None
    cs = st.get("coverage_stop") if isinstance(st, dict) else None
    at = utc_epoch(cs.get("at")) if isinstance(cs, dict) else None
    if at is None or st.get("status") != "blocked" or not int(run["at"]) <= at <= now:
        return None
    if obs.get("transcript") and obs["transcript"](run) is not None:
        return None
    return cs


def program_closed(concept, unit):
    """-> ("closed", its stage.json result entry) when stage5_program closed `unit`, ("error", why) when that step did
    not run on it, else None (the Designer ran, as today)."""
    import designer_stage as DS
    st = DS.load_state(concept)
    hit = next((r for r in st.get("results") or [] if isinstance(r, dict) and r.get("run") == unit
                and r.get("by") == "program" and r.get("outcome") != "rejected"), None)
    if hit:
        return "closed", hit
    err = next((h for h in reversed(st.get("history") or []) if isinstance(h, dict) and h.get("what") == "program_error"
                and str(h.get("why") or "").startswith("run %s:" % unit)), None)
    return ("error", err["why"]) if err else None


# budget: danger=a stage close that raises on each tick is tried for ever; ends no work: the close is given up, said to the
# budget: Conductor
CLOSE_OWED_MAX_S = 2 * 86400     # a stage close still raising after this long is given up, said to the Conductor


def codex_usage(run, res):
    """A Codex run's usage: its result line's, else what agent_runner left beside the run's out file (the spend
    envelope, else the streamed events: a unit stopped at run_max_s never prints a result line). Item
    RIMMANDRAKE_READ_CODEX_SPEND_OF_A_KILLED_DESIGNER_RUN; UNMEASURED only when none of the three is readable."""
    u = res.get("codex_usage") if isinstance(res, dict) else None
    if isinstance(u, dict):
        return u
    if not run.get("out"):
        return "UNMEASURED"
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils"))
    import agent_runner as AR
    return AR.usage_of_files(run["out"] + ".spend.json", run["out"] + ".events.jsonl")


def close_concept(name, rs, cfg, run, res, tok, now, act, obs):
    """A finished stage-machine run's close: the stage machine charges the task budget and judges result.json (a
    closing message advances nothing). run["close_owed"] is set BEFORE designer_stage's close and cleared the moment it
    returns, so a close that raises (a transient stage.json read) is retried by every later supervision instead of
    being abandoned behind the run's done/failed state (RELENTLESS_ROLE_LAUNCH_HARDEN_CAUSE_BOOK); a raise after the
    close returned is only said, since a second close would refuse the already-closed run."""
    owed = run.get("close_owed") if isinstance(run.get("close_owed"), dict) else {"since": now, "tries": 0}
    if run.get("runner"):
        cfg = dict(cfg, runner=run["runner"])
    run["close_owed"] = owed
    try:
        if run.get("by") == "program":     # stage5_program closed it in the unit through close_run: accepted there
            ok, errs = True, []
        elif (run.get("runner") == "codex" or res.get("runner") == "codex") and not obs.get("stage_close"):
            import designer_stage as DS
            ok, errs = DS.close_run(run["concept"], run["unit"], repo=DS.REPO,
                                   runner="codex", usage=codex_usage(run, res),
                                   transport_error=(res.get("result") or "no Codex transport result")
                                   if res.get("is_error") or not res or run.get("state") == "failed" else None)
        else:
            ok, errs = (obs.get("stage_close") or stage_close)(run["concept"], run["unit"], tok)
    except Exception as e:  # noqa: BLE001 - said, and owed: the next tick closes it again
        owed["tries"] = int(owed.get("tries") or 0) + 1
        owed["why"] = "%s: %s" % (type(e).__name__, str(e))
        # designer_stage.Refused (the run is no longer the concept's open run: reopened, or closed another way) is
        # final, and so is a close still failing after CLOSE_OWED_MAX_S: both are said once and stop retrying
        final = type(e).__name__ == "Refused" or now - owed["since"] >= CLOSE_OWED_MAX_S
        if final:
            run.pop("close_owed", None)
        act(do="alarm", kind="role:%s:stage_close" % name, ticket=run.get("item"), note=True,
            conductor_log=final or None,
            why="%s run %s on %s: designer_stage close failed: %s; %s (try %d, owed since %s)" % (
                name, run["unit"], run["concept"], str(e),
                "NOT retried: refused by the stage machine" if type(e).__name__ == "Refused" else
                "given up after %d h: a person closes it (designer_stage.py)" % (CLOSE_OWED_MAX_S // 3600)
                if final else "retried next tick", owed["tries"], iso(owed["since"])))
        return
    run.pop("close_owed", None)
    if run.get("by") == "judge_stop":
        # the judge's designed stop: one alarm naming it and its release; no rejection route, so no re-chain onto the
        # blocked concept (whose launch the next tick would refuse as role:<name>:stage_refused)
        cs = run.get("coverage_stop") or {}
        act(do="alarm", kind="role:%s:coverage_stop" % name, ticket=run.get("item"), note=True,
            why="%s run %s on %s: the stage-5 coverage judge stopped it at %s before any model started (%s); not "
                "re-chained. `python3 src/RimMandrake/rimflow/coverage_judge.py release %s --why \"...\"` grants one "
                "more look" % (name, run["unit"], run["concept"], cs.get("at") or "?", cs.get("why") or "?",
                               run["concept"]))
        try:
            (obs.get("stage_land") or stage_land)(run["concept"], run["unit"])
        except Exception as e:  # noqa: BLE001 - said; the files stay on disk and the next close lands them
            act(do="alarm", kind="role:%s:stage_land" % name, ticket=run.get("item"), note=True,
                why="%s run %s on %s: its stage state did not land on origin/main: %s" % (
                    name, run["unit"], run["concept"], str(e)))
        return
    void = None if ok else void_cause(run, res, errs)
    if void:
        try:
            if not (obs.get("stage_void") or stage_void)(run["concept"], run["unit"], void):
                void = None     # nothing to mark: the rejection counts, as before
        except Exception as e:  # noqa: BLE001 - said: the rejection then counts as before
            act(do="alarm", kind="role:%s:stage_void" % name, ticket=run.get("item"), note=True,
                why="%s run %s on %s: its system cause (%s) could not be marked void_system: %s: %s; the rejection "
                    "counts" % (name, run["unit"], run["concept"], void, type(e).__name__, str(e)))
            void = None
    try:
        if void:
            act(do="alarm", kind="role:%s:stage_void" % name, ticket=run.get("item"), note=True,
                why="%s run %s on %s: stage result VOID (void_system: %s): no retry or rejection is spent" % (
                    name, run["unit"], run["concept"], void))
        else:
            act(do="alarm" if not ok else "role_stage", kind="role:%s:stage_rejected" % name,
                ticket=run.get("item"), note=True,
                why="%s run %s on %s: %s" % (name, run["unit"], run["concept"], "stage result accepted" if ok
                                             else "stage result REJECTED: " + "; ".join(errs[:4]) + (
                                             " (+%d more)" % (len(errs) - 4) if len(errs) > 4 else "")))
        # DESIGNER_STAGE_FIX_COMMIT_ITS_OWN_STATE: the advanced stage.json and renamed result files land on
        # origin/main now; before, they sat in the Designer's clone until a person committed them
        try:
            (obs.get("stage_land") or stage_land)(run["concept"], run["unit"])
        except Exception as e:  # noqa: BLE001 - said; the files stay on disk and the next close lands them
            act(do="alarm", kind="role:%s:stage_land" % name, ticket=run.get("item"), note=True,
                why="%s run %s on %s: its stage state did not land on origin/main: %s" % (
                    name, run["unit"], run["concept"], str(e)))
        t = (obs.get("stage_turn") or stage_turn)(run["concept"]) if ok else None
        if t:
            escalate_turn(name, run, t, act)
        if ok:
            forget_rejections(rs, run["concept"])
            chain_next(name, rs, cfg, run, now, act, obs.get("stage_status") or stage_status)
        elif void:
            void_route(name, rs, cfg, run, void, now, act, obs)
        else:
            route_rejection(name, rs, cfg, run, res, list(errs or []), now, act, obs)
    except Exception as e:  # noqa: BLE001 - the close itself happened: said, never retried (it would refuse)
        act(do="alarm", kind="role:%s:stage_close" % name, ticket=run.get("item"), note=True,
            why="%s run %s on %s: after its designer_stage close: %s: %s" % (name, run["unit"], run["concept"],
                                                                      type(e).__name__, str(e)))


def void_cause(run, res, errs):
    """Pure. -> the system cause of a rejected stage close, or None (RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_
    COUNTERS, run_void.py's rule): every reason is designer_stage's "no result.json" AND the machine stopped the run
    before it could write one: stopped at run_max_s (a timeout), or the unit ended with no claude result of its own. A
    claude result (an is_error, a cap, the agent's own end) is the run's: it counts."""
    if not errs or not all(str(e).startswith("no result.json") for e in errs):
        return None
    if res:     # claude answered (an is_error, a cap, the agent's own end), whatever stop was asked: it counts
        return None
    out = run.get("out")
    if out and os.path.exists(out) and not os.access(out, os.R_OK):
        return None     # could not look at its output: never read as "no result" (it counts, as the books had it)
    if run.get("stop_tries"):
        return "stopped at run_max_s after %d stop(s), before it wrote result.json" % run["stop_tries"]
    return "the unit ended with no claude result of its own"


def stage_void(concept, unit, cause):
    """designer_stage.void_rejection: the run's no-result rejection marked void_system -> True when marked."""
    import designer_stage as DS
    return DS.void_rejection(concept, unit, cause)


def note_chain_unit(rs, unit, req, now):
    """A chained run-now launched as `unit`: its chain count is recorded against the unit (rs["chain_units"]), so a
    void_system end can give that one chain back (give_back_chain). Entries older than two days are dropped."""
    if not isinstance(req, dict) or not req.get("chain_key"):
        return
    book = {u: e for u, e in (rs.get("chain_units") or {}).items() if isinstance(e, dict)
            and now - (e.get("at") or 0) < 2 * 86400}
    book[unit] = {"key": req["chain_key"], "stage": req.get("chain_stage"), "at": now}
    rs["chain_units"] = book


def give_back_chain(rs, unit):
    """-> True when the chain that launched `unit` was given back: today's count for its day and concept less one, and
    its stage off the day's stage list (chain_cap_view's forward rule reads both)."""
    e = (rs.get("chain_units") or {}).pop(unit, None)
    return give_back_req(rs, {"chain_key": e.get("key"), "chain_stage": e.get("stage")}) if isinstance(e, dict) else False


def give_back_req(rs, req):
    """-> True when the chain a request was charged (its chain_key and chain_stage) was given back."""
    e = {"key": req.get("chain_key"), "stage": req.get("chain_stage")}
    counts = rs.get("chain_day") or {}
    if not counts.get(e.get("key")):
        return False
    counts[e["key"]] -= 1
    st = (rs.get("chain_stages_day") or {}).get(e["key"])
    if isinstance(st, list) and e.get("stage") in st:
        st.reverse()
        st.remove(e["stage"])
        st.reverse()
    return True


def void_held(rs, concept, now):
    """True when `concept` met run_void.SYSTEM_FAULT_LIMIT void_system runs today (void_route): nothing chains it,
    harvest or sweep, until the day turns, or until a run on it launched after the last of those voids finishes
    done. That run proves the system cause repaired, so the hold lifts and the chain goes on (queues-20261121133600:
    Pyrelands sat ready 4.6 h after an accepted hand run-now, held to the local midnight)."""
    import run_void as RV
    day = day_of(now)
    voids = [f for f in rs.get("void_faults") or [] if isinstance(f, dict) and f.get("day") == day
             and f.get("concept") == concept]
    if len(voids) < RV.SYSTEM_FAULT_LIMIT:
        return False
    last = max((f.get("at") or 0) for f in voids)
    void_units = {f.get("unit") for f in voids}
    return not any(isinstance(r, dict) and r.get("concept") == concept and r.get("state") == "done"
                   and r.get("unit") not in void_units and (r.get("at") or 0) > last for r in rs.get("runs") or [])


def void_route(name, rs, cfg, run, cause, now, act, obs):
    """A void_system stage close (void_cause): no rejection is remembered (no arbiter on a second one), the chain that
    launched the dead run is given back, and the stage is chained again. At run_void.SYSTEM_FAULT_LIMIT void runs on
    one concept in a day it stops as a system fault (alarm role:<Role>:system_fault): nothing is chained and nothing is
    spent. -> "rechained" | "not_chained" | "system_fault"."""
    import run_void as RV
    concept, item, day = run["concept"], run.get("item"), day_of(now)
    vf = [f for f in rs.get("void_faults") or [] if isinstance(f, dict) and f.get("day") == day]
    vf.append({"day": day, "concept": concept, "unit": run["unit"], "cause": cause, "at": now})
    rs["void_faults"] = vf
    n = sum(1 for f in vf if f.get("concept") == concept)
    gave = give_back_chain(rs, run["unit"])     # the dead run's own chain, at the limit too
    head = "%s run %s on %s: VOID (void_system: %s)" % (name, run["unit"], os.path.basename(os.path.normpath(concept)),
                                                        cause)
    if n >= RV.SYSTEM_FAULT_LIMIT:
        act(do="alarm", kind="role:%s:system_fault" % name, ticket=item, note=True, conductor_log=True,
            raise_first="%s: %d runs on %s died of a system cause today; nothing is chained until the cause is read." % (
                name, n, os.path.basename(os.path.normpath(concept))),
            why="%s; %d void_system runs on it today (limit %d, %s): not chained, no retry spent" % (
                head, n, RV.SYSTEM_FAULT_LIMIT, RV.ALARM_ID))
        return "system_fault"
    req = None
    if cfg.get("chain_stages") is True:
        status = obs.get("stage_status") or stage_status
        try:
            stage = (status(concept) or {}).get("stage")
        except Exception:  # noqa: BLE001 - the stage only labels the request
            stage = None
        req = chain_ask(name, rs, cfg, concept, stage, now, act, run["unit"], item, run.get("mode") or "run",
                        "%s run %s was void_system (%s): the stage runs again" % (name, run["unit"], cause),
                        "after its void run %s" % run["unit"])
    act(do="role_hold", role=name, ticket=item, note=True, why="%s -> %s%s" % (
        head, "re-chained" if req else "not chained (no chain_stages, cap reached or already asked)",
        "; its chain given back" if gave else ""))
    return "rechained" if req else "not_chained"


def stage_close(concept, unit, tokens, sync=True):
    """designer_stage.close_run: the run's charge, then its result.json validated -> (accepted, reasons)."""
    import designer_stage as DS
    if sync:
        judge_sync(concept)
    return DS.close_run(concept, unit, tokens, repo=DS.REPO)


def stage_land(concept, unit):
    """designer_stage.land_state: the harvest's stage.json and result files onto origin/main -> its one line."""
    import designer_stage as DS
    return DS.land_state(concept, unit)


# DESIGNER_STAGES_WIRE_NOBODY_PRESSED_GO: a stage-machine role whose row sets chain_stages true chains its own next
# stage. A run whose close is ACCEPTED and leaves the concept at status=ready (stage N done -> N+1, or a return to an
# earlier stage) queues a run-now for that concept, by the Dispatcher, launched by the next decide through every gate a
# hand-pressed run-now passes (off file, account pick, stage_open's refusals). waiting_owner, blocked and
# locked chain nothing (the owner, the dependency or nobody moves them); a REJECTED result chains nothing (its alarm
# stands, and a retry loop would spend unwatched). run_now is one slot per role: a chain that finds it taken waits in
# rs["run_now_queue"] (one entry per concept) and takes the slot once it frees. Before this, every finished stage sat
# ready until queues.designer.stalled_min alarmed (OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV: 3 concepts, 60+ min).
CHAIN_MAX_PER_DAY = 8        # chained launches per concept per day: stages 0-5 plus two returns; a loop past it alarms


def stage_status(concept):
    """-> the concept's stage.json (designer_stage.load_state)."""
    import designer_stage as DS
    return DS.load_state(concept)


def chain_next(name, rs, cfg, run, now, act, status):
    """After an accepted stage close: queue the concept's next run (see CHAIN_MAX_PER_DAY). -> the queued request or
    None. status(concept) -> its stage.json; an unreadable one is said and chains nothing."""
    if cfg.get("chain_stages") is not True or not run.get("concept"):
        return None
    concept = run["concept"]
    try:
        st = status(concept)
    except Exception as e:  # noqa: BLE001 - said; a hand run-now still works
        act(do="alarm", kind="role:%s:chain" % name, ticket=run.get("item"), note=True,
            why="%s run %s on %s: next stage NOT chained, its stage.json is unreadable: %s" % (
                name, run["unit"], concept, str(e)))
        return None
    if not isinstance(st, dict) or st.get("status") != "ready":
        return None
    cfg = dict(cfg, runner=run.get("runner", cfg.get("runner", "claude")))
    return chain_ask(name, rs, cfg, concept, st.get("stage"), now, act, run["unit"], run.get("item"),
                     run.get("mode") or "run", "%s run %s closed" % (name, run["unit"]),
                     "after run %s" % run["unit"])


def owner_held(name, rs, concept, now, act):
    """True when the owner holds `concept`'s mod (mod_owner_hold.json; item RIMMANDRAKE_HOLD_SIX_BIOME_MODS_ONLY_PYRELANDS_
    STAYS): nothing is chained or launched on it. Said once a day per concept as a role_hold note, never an alarm. An
    unreadable hold file holds every concept (nothing can be proved unheld), alarmed once per outage."""
    import mod_owner_hold as OH
    try:
        h = OH.held(concept)
    except OH.Unreadable as e:
        if not rs.get("hold_blind"):
            act(do="alarm", kind="role:%s:mod_owner_hold" % name, note=True, conductor_log=True,
                why="%s: the owner hold file cannot be read, so NO concept is chained or launched: %s" % (name, e))
        rs["hold_blind"] = str(e)
        return True
    rs.pop("hold_blind", None)
    if pipeline_held(name, rs, concept, now, act):
        return True
    if not h:
        return False
    mark = "%s %s" % (day_of(now), OH.key(concept))
    said = [k for k in rs.get("hold_said") or [] if str(k).startswith(day_of(now) + " ")]
    if mark not in said:
        act(do="role_hold", role=name, note=True, why="%s: %s is not chained or launched: %s" % (
            name, OH.key(concept), OH.status(h)))
        said.append(mark)
    rs["hold_said"] = said
    return True


def pipeline_held(name, rs, concept, now, act):
    """True when the pipeline's pause (pipeline_pause.py; item RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED) stands on
    `concept`'s mod, or on the whole pipeline (concept None: pause all only): nothing is chained, resumed or launched.
    A planned stop: said once a day per scope as a role_hold note, never an alarm. An unreadable pause store holds
    everything (a pause that cannot be proved lifted is never read as running), alarmed once per outage."""
    import pipeline_pause as PP
    pst = PP.state(now)
    why = PP.reason(pst, concept)
    if not why:
        rs.pop("pause_blind", None)
        return False
    if pst.get("error") and not rs.get("pause_blind"):
        act(do="alarm", kind="role:%s:pipeline_pause" % name, note=True, conductor_log=True,
            why="%s: %s" % (name, why))
        rs["pause_blind"] = why
    scope = PP.key(concept) if concept else "all"
    mark = "%s %s" % (day_of(now), scope)
    said = [k for k in rs.get("pause_said") or [] if str(k).startswith(day_of(now) + " ")]
    if mark not in said:
        act(do="role_hold", role=name, note=True, why="%s: %s not chained or launched: %s" % (
            name, "%s is" % scope if concept else "nothing is", why))
        said.append(mark)
    rs["pause_said"] = said
    return True


def chain_cap_view(rs, cfg, concept, stage, now):
    """(today's chain counts, today's chain stages, forward) for `concept` at `stage`: THE chain-cap rule, shared by
    chain_ask and by ops_watch's stall reader (chain_capped), so the alarm and the hold cannot disagree. The cap brakes
    loops, not progress (RIMMANDRAKE_PASS_FORWARD_STAGES_PAST_DESIGNER_CHAIN_CAP: on 2026-11-15 Graffiti met it at
    stage 3 and the Conductor pressed stages 3, 4 and 5 by hand): a stage this concept has not been chained at today is
    forward progress and is chained past the cap, up to twice the cap; a stage chained before is a return, and past
    the cap that is the loop the alarm names. (The stage history must cover every chained run of the day: counts with
    no history, as on the day this landed, prove nothing about progress and keep the plain cap.)"""
    day = day_of(now)
    counts = {k: v for k, v in (rs.get("chain_day") or {}).items() if k.startswith(day + " ")}
    key = "%s %s" % (day, concept)
    n, cap = chain_cap(cfg, concept, counts.get(key, 0))
    stages = {k: list(v) for k, v in (rs.get("chain_stages_day") or {}).items() if k.startswith(day + " ")}
    forward = (n >= cap and stage is not None and str(stage) not in stages.get(key, [])
               and len(stages.get(key, [])) == counts.get(key, 0) and n < 2 * cap)
    return counts, stages, forward


def chain_cap(cfg, concept, n):
    """-> (today's chained runs on `concept`, chain_max_per_day) through the control store: `pipe set|add|reset|limit
    <Mod> chain_runs_day ...` moves both (the account is the concept folder's name). An unreadable store reads the raw
    count and cap: chain_ask's owner_held read refuses on that store first, so nothing is chained on it."""
    import pipeline_control as PC
    mod = os.path.basename(os.path.normpath(str(concept)))
    cap = cfg.get("chain_max_per_day", CHAIN_MAX_PER_DAY)
    try:
        return PC.used(mod, "chain_runs_day", n), PC.limit(mod, "chain_runs_day", cap)
    except PC.Unreadable:
        return n, cap


def chain_capped(rs, cfg, concept, stage, now):
    """True when chain_ask would HOLD `concept` on the per-concept daily chain cap right now (a deliberate hold that
    already raised role:<Role>:chain_cap once, so the stall reader must not count it too)."""
    counts, _stages, forward = chain_cap_view(rs, cfg, concept, stage, now)
    n, cap = chain_cap(cfg, concept, counts.get("%s %s" % (day_of(now), concept), 0))
    return n >= cap and not forward


def chain_ask(name, rs, cfg, concept, stage, now, act, chained_from, item, mode, cause, after, reasons=None):
    """Ask (or queue behind the taken slot) one run-now for `concept`, under the per-concept daily cap. -> the request
    or None. Shared by the harvest's chain_next and the decide tick's chain_sweep. `reasons` (a rejected close's, every
    one in full) ride on the request into the launch message (run_now_job, prompt). A concept the owner holds is never
    asked (owner_held)."""
    if owner_held(name, rs, concept, now, act):
        return None
    if void_held(rs, concept, now):
        return None     # role:<Role>:system_fault was raised once by void_route; the sweep asks nothing either
    day = day_of(now)
    key = "%s %s" % (day, concept)
    counts, stages, forward = chain_cap_view(rs, cfg, concept, stage, now)
    n, cap = chain_cap(cfg, concept, counts.get(key, 0))
    rs["chain_stages_day"] = stages
    if n >= cap and not forward:
        said = [k for k in rs.get("chain_cap_said") or [] if str(k).startswith(day + " ")]
        rs["chain_day"] = counts
        if key in said:
            rs["chain_cap_said"] = said
            return None                           # said once today; the sweep re-meets it every tick
        rs["chain_cap_said"] = said + [key]
        act(do="alarm", kind="role:%s:chain_cap" % name, ticket=item, note=True, conductor_log=True,
            raise_first="%s chained %s %d times today: it is looping; look at its stage history." % (
                name, os.path.basename(os.path.normpath(concept)), n),
            why="%s on %s: stage %s ready but NOT chained (%s), %d chained runs today (chain_max_per_day %d)" % (
                name, concept, stage, cause, n, cap))
        rs["chain_day"] = counts
        return None
    rs["chain_day"] = counts
    pending = rs.get("run_now")
    if isinstance(pending, dict) and pending.get("concept") == concept:
        return None                               # already asked for: the pending request runs this stage
    counts[key] = counts.get(key, 0) + 1
    stages.setdefault(key, []).append(str(stage))
    req = {"at": now, "by": "Dispatcher", "mode": mode, "concept": concept, "chained_from": chained_from,
           "chain_key": key, "chain_stage": str(stage),    # a void_system end of its run gives this chain back
           "why": "chain: %s, stage %s ready%s" % (cause, stage, (
               "; delegated: past the daily chain cap of %d on forward progress (stage %s not chained today, run %d "
               "of at most %d)" % (cap, stage, counts[key], 2 * cap)) if forward else "")}
    if cfg.get("runner"):
        req["runner"] = cfg["runner"]
    if reasons:
        req["reasons"] = [str(r) for r in reasons]
    if isinstance(pending, dict):
        queue = [q for q in rs.get("run_now_queue") or [] if isinstance(q, dict) and q.get("concept") != concept]
        rs["run_now_queue"] = queue + [req]
        how = "queued behind the pending run-now on %s" % pending.get("concept")
    else:
        rs["run_now"] = req
        how = "run-now asked"
    act(do="role_hold", role=name, ticket=item, note=True,
        why="%s: %s stage %s ready %s: next stage chained (%s)" % (
            name, os.path.basename(os.path.normpath(concept)), stage, after, how))
    return req


# OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV (3rd recurrence): chain_next fires only when a run's close is harvested,
# so a concept left ready any other way (closed before chain_stages existed, a hand close, a run the harvest never saw,
# a waiting_owner he has answered) sat until queues.designer.stalled_min rang: GimmeSomeSlack and Pyrelands, 4 h+.
# Each decide tick of a chain_stages role now sweeps every concept the stall alarm counts as pending (the same rule:
# designer_stage's ready, or waiting_owner answered) and asks its run once it has waited CHAIN_SWEEP_GRACE_S, through
# chain_ask's cap and slot. Skipped: a concept no run has opened (never_opened), an open run, a last result REJECTED and PARKED (designer_stage.rejection_parked:
# a retry cannot help; parked_record says so, ops_watch's stall reader skips it by the same rule), a concept
# already holding the slot or a queue place, and one a running run of this role works on. A rejected concept that is
# not parked (the path its rejection cited has landed since, or an unlabelled rejection not yet met twice) is
# re-chained with the rejection's reasons (RELAPSE_QUEUES_FIX_DIED_TWICE: GSS sat 6 h after its missing file landed).
# budget: danger=the sweep chains a concept that a harvest is about to chain; ends no work: the sweep leaves it for a later
# budget: sweep
CHAIN_SWEEP_GRACE_S = 600    # a harvest chains at once; the sweep is for what no harvest will ever see


def never_opened(st):
    """True for a concept no run has opened: stage 0, no result, no open run, no `open` row in its history (what
    designer_stage init leaves). The sweep and the Designer stall reader (ops_watch._q_designer) skip it: a new concept
    moves only on a hand run-now, once its mod's readiness list reads READY and `pipe on <Mod>` cites it
    (RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS: init on a new mod was swept into an opus Designer run 10
    min later; the role's enabled false means run-now only and stops no request). A first run that opened and died
    leaves its `open` row, so that concept is swept as before."""
    return (isinstance(st, dict) and st.get("stage") == 0 and not st.get("results") and not st.get("running")
            and not any(isinstance(h, dict) and h.get("what") == "open" for h in st.get("history") or []))


def stage_concepts(repo=None):
    """-> [(concept dir, stage.json, pending-since epoch or None)] over designer_stage.concepts_root(), pending as
    ops_watch's queues.designer reader counts it: ready -> the later of its last history row and its open run's start;
    waiting_owner -> his answer (designer_stage.owner_answered_at), None while he has not answered; else None. An
    unreadable dir, stage.json or OWNER shard raises (the sweep alarms; never a calm nothing)."""
    import glob
    import designer_stage as DS
    root = DS.concepts_root()
    if not os.path.isdir(root):
        raise OSError("concepts dir missing: %s" % root)
    out = []
    for f in sorted(glob.glob(os.path.join(root, "*", "stage.json"))):
        d = os.path.dirname(f)
        st = DS.load_state(d)
        run_at = DS.epoch((st.get("running") or {}).get("at")) if isinstance(st.get("running"), dict) else None
        since = None
        if st.get("status") == "waiting_owner":
            since = DS.owner_answered_at(st, d, repo or DS.REPO)
        elif st.get("status") == "ready":
            hs = [h for h in (st.get("history") or []) if isinstance(h, dict)]
            ts = [t for t in ((DS.epoch(hs[-1].get("at")) if hs else None), run_at) if t is not None]
            since = max(ts) if ts else None
        out.append((d, st, since))
    return out


def chain_sweep(name, rs, cfg, now, act, concepts, parked=None):
    """Ask a run for every orphaned pending concept (see CHAIN_SWEEP_GRACE_S). -> the requests asked. parked(st) ->
    why a rejected concept is parked, or None (default designer_stage.rejection_parked against designer_stage.REPO)."""
    if cfg.get("chain_stages") is not True:
        return []
    try:
        rows = list(concepts())
    except Exception as e:  # noqa: BLE001 - said once per outage; the harvest chain and a hand run-now still work
        if not rs.get("sweep_blind"):
            act(do="alarm", kind="role:%s:chain_sweep" % name, ticket=cfg.get("ledger_item"), note=True,
                why="%s: orphaned ready concepts NOT swept, the concepts cannot be read: %s; alarmed once per outage"
                % (name, str(e)))
        rs["sweep_blind"] = str(e)
        return []
    rs.pop("sweep_blind", None)
    grace = cfg.get("chain_sweep_grace_s", CHAIN_SWEEP_GRACE_S)
    held = {q.get("concept") for q in [rs.get("run_now")] + list(rs.get("run_now_queue") or []) if isinstance(q, dict)}
    held |= {r.get("concept") for r in rs.get("runs") or [] if isinstance(r, dict) and r.get("state") == "running"}
    asked = []
    still_parked = set()
    lane = cfg.get("sweeps_runner")     # a runner lane (Designer: claude, DesignerCodex: codex) sweeps only its own
    for concept, st, since in rows:
        if since is None or not isinstance(st, dict) or st.get("running") or concept in held or now - since < grace:
            continue
        if never_opened(st):
            continue                    # a new concept: only a hand run-now starts it (never_opened)
        if lane and (st.get("runner") or "claude") != lane:
            continue
        if owner_held(name, rs, concept, now, act):
            continue                    # held by the owner: not swept, not parked, no alarm (mod_owner_hold.py)
        res = [r for r in st.get("results") or [] if isinstance(r, dict)]
        reasons = None
        if res and res[-1].get("outcome") == "rejected":
            if parked is None:
                import designer_stage as DS
                parked = DS.rejection_parked
            try:
                why = parked(st)
            except Exception as e:  # noqa: BLE001 - an unreadable cause is parked (no blind retry); the stall reader
                why = "parked rule raised: %s" % str(e)   # meets the same raise and reports itself blind
            if why:
                parked_record(name, rs, cfg, concept, st, res[-1], why, now, act)
                still_parked.add(concept)
                continue
            reasons = [str(w) for w in res[-1].get("why") or []]
        mins = int((now - since) // 60)
        selected = dict(cfg, runner=st["runner"]) if st.get("runner") else cfg
        req = chain_ask(name, rs, selected, concept, st.get("stage"), now, act, "orphan-sweep", cfg.get("ledger_item"),
                        "run", "orphan sweep, %s %d min with nothing chained%s" % (
                            st.get("status"), mins, ", its rejection's cause gone" if reasons is not None else ""),
                        "for %d min with no run chained (orphan sweep)" % mins, reasons=reasons)
        if req:
            held.add(concept)
            asked.append(req)
    said = {c: v for c, v in (rs.get("parked_said") or {}).items() if c in still_parked}
    if said:
        rs["parked_said"] = said                  # one no longer parked leaves: a later parking is said afresh
    else:
        rs.pop("parked_said", None)
    return asked


def parked_record(name, rs, cfg, concept, st, last, why, now, act):
    """A concept the sweep parks leaves a record: an alarm on the ledger and in the Conductor's log, once per day and
    per distinct parking (DESIGNER_RECHAIN_FIX_REJECTS_WAIT_FOREVER). The stall reader skips a parked concept by the
    same rule and the stage_rejected alarm is one kind shared by every concept, rate-limited, so without this a
    concept could wait for good with no line anywhere saying so. The kind carries a hash of stage and masked reasons:
    another concept's parking, or this one's for a new reason, is never swallowed by the repeat limit."""
    sig = "%s|%s" % (st.get("stage"), " ; ".join(sorted(_RUN_RX.sub("#", str(w)) for w in last.get("why") or [])))
    mark = "%s %s" % (day_of(now), hashlib.sha256(sig.encode("utf-8")).hexdigest()[:10])
    book = rs.setdefault("parked_said", {})
    if book.get(concept) == mark:
        return
    book[concept] = mark
    mod = os.path.basename(os.path.normpath(concept))
    act(do="alarm", kind="role:%s:parked:%s:%s" % (name, mod, mark.split()[1]),
        ticket=st.get("item") or cfg.get("ledger_item"), note=True, conductor_log=True,
        why="%s: %s stage %s is PARKED, the orphan sweep will not re-chain it: %s. Rejected run %s at %s: %s" % (
            name, mod, st.get("stage"), why, last.get("run"), last.get("at"),
            "; ".join(str(w) for w in (last.get("why") or [])[:4])))


def chain_pop(rs, now):
    """A free run-now slot takes the oldest chained request waiting for it, stamped now (its TTL starts here)."""
    if rs.get("run_now") is None and rs.get("run_now_queue"):
        q = [x for x in rs["run_now_queue"] if isinstance(x, dict)]
        if q:
            rs["run_now"] = dict(q[0], at=now)
        rs["run_now_queue"] = q[1:]
        if not rs["run_now_queue"]:
            rs.pop("run_now_queue")


def stage_turn(concept):
    """-> the concept's turn that waits on him (designer_stage.pending_turn), or None."""
    import designer_stage as DS
    return DS.pending_turn(concept, repo=DS.REPO)


# ROLES_FIX_REJECTED_STAGE_ROUTES_BY_CAUSE (WP-15, redesign_final.md §2 G21, §5 row 15). A REJECTED stage close chained
# nothing whatever its cause (its alarm stood until a person re-pressed the same role), so a defect in the CHECK or the
# ENVIRONMENT came back to the role that could not fix it. Now the rejection's cause class routes it:
#   module       -> builder: the same role re-chained once, its run told the full reasons (chain_ask, under its cap)
#   check | bar  -> the alarm stands for the checker's owner (RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED:
#                   the Setter seam resat Relentless-era exams only, and every Setter unit it started was refused)
#   environment  -> the cause book: attached to the live cause record (cause_book.attach), never a new item and never
#                   a re-chain; with no live record the alarm stands and Operations' incident files it once
#   unknown / mixed -> builder, with the full reasons (the owner of the work reads them first)
# and a rejection IDENTICAL to the concept's previous one (same stage, class and reasons, run names masked) is not
# looped a second time: its alarm stands (the Relentless-era arbiter is retired with the Setter).
# The class is the Marker's when one labelled the reasons
# (a "[cause:<class>]" tag, evidence.py marker `classes`); unlabelled, it is read off the run: an account death, an
# is_error result or a stopped run is environment; a run that finished and was refused by the program check is module;
# a failed run with nothing more said is unknown.
CAUSE_CLASSES = ("module", "check", "bar", "environment")
CAUSE_ROUTE = {"module": "builder", "check": "setter", "bar": "setter", "environment": "cause_book",
               "unknown": "builder", "mixed": "builder"}
CAUSE_TAG_RX = re.compile(r"\[cause:([a-z]+)\]")
REJECTION_KEEP = 4            # signatures remembered per concept (only the last decides "identical")
_RUN_RX = re.compile(r"rm-role-[a-z]+-\d+|\b\d{6,}\b")


def rejection_cause(errs, run=None, res=None, classes=None):
    """Pure. -> (class, why). class is one of CAUSE_CLASSES, 'mixed' (two or more labelled classes) or 'unknown'."""
    labels = {str(c).lower() for c in (classes or [])}
    labels |= {m.group(1) for e in errs or [] for m in CAUSE_TAG_RX.finditer(str(e))}
    known = labels & set(CAUSE_CLASSES)
    if len(known) > 1:
        return "mixed", "labelled %s" % "+".join(sorted(known))
    if known:
        return next(iter(known)), "labelled %s" % next(iter(known))
    run = run or {}
    acct = account_death(res)
    if acct:
        return "environment", "account death %s" % acct
    if isinstance(res, dict) and res.get("is_error"):
        return "environment", "is_error result (%s)" % (res.get("terminal_reason") or res.get("subtype") or "?")
    if run.get("stop_tries"):
        return "environment", "run stopped after run_max_s (%d stop(s))" % run["stop_tries"]
    if run.get("state") == "done":
        return "module", "the run finished and the program check refused its result"
    return "unknown", "run %s with no result and no environment signal" % (run.get("state") or "?")


def rejection_sig(stage, cls, errs):
    """Pure. Two rejections are identical when stage, class and reasons agree with run names and long ids masked."""
    return "%s|%s|%s" % (stage, cls, " ; ".join(sorted(_RUN_RX.sub("#", str(e)) for e in errs or [])))


def remember_rejection(rs, concept, sig, unit, now):
    """-> True when `sig` repeats the concept's previous rejection. Records it either way (rs["rejections"])."""
    book = rs.setdefault("rejections", {})
    rows = [r for r in book.get(concept) or [] if isinstance(r, dict)]
    again = bool(rows) and rows[-1].get("sig") == sig
    book[concept] = (rows + [{"sig": sig, "unit": unit, "at": now}])[-REJECTION_KEEP:]
    return again


def forget_rejections(rs, concept):
    """An accepted close ends the concept's rejection run: the next rejection is a first again."""
    if concept in (rs.get("rejections") or {}):
        rs["rejections"].pop(concept)
        if not rs["rejections"]:
            rs.pop("rejections")


# RELENTLESS_ROLE_LAUNCH_HARDEN_CAUSE_BOOK: the cause-book seam DECIDES only. It returns the action that carries its
# route out (role_cause_attach), which dispatcher.execute performs through cause_attach, so a dry run (and any decision
# collected without --apply) writes no book.
# budget: danger=a busy cause book holds the tick; ends no work: the attachment is kept and tried again
CAUSE_ATTACH_WAIT_S = 5.0     # cause_attach's wait for the book lock (an ops_watch pass holds it across its filing)
CAUSE_OWED_CAP = 50           # attachments kept to retry while the book stays busy (oldest dropped, said)


def cause_book_path():
    utils = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils")
    if utils not in sys.path:
        sys.path.append(utils)
    import ops_watch
    return ops_watch.ops_dir() / "causes.json"


def to_cause_book(key, said, now, role=None, path=None):
    """The cause-book seam (WP-05 cause_book.py, ops_watch's causes.json). Reads only. -> the role_cause_attach action
    that attaches to the live record of `key`, or None when there is no live record (nothing filed here: the alarm
    stands and Operations files it once). An unreadable book raises (the route says so; the alarm stands)."""
    import cause_book as CB
    if CB.live(CB.load(path or cause_book_path()), key) is None:
        return None
    return dict(do="role_cause_attach", role=role, key=key, said=said, at_s=now, note=False,
                why="%s rejection: attach to cause %s" % (role or "role", key))


def cause_attach(key, said, at_s, path=None, wait_s=CAUSE_ATTACH_WAIT_S):
    """dispatcher.execute's role_cause_attach: load-attach-save under the book's writer lock (cause_book.locked, which
    ops_watch holds for its whole pass). -> True attached, False no live record any more. Raises cause_book.Busy when
    the lock stayed held past wait_s: nothing was written, and the caller keeps the attachment to retry."""
    import cause_book as CB
    path = path or cause_book_path()
    with CB.locked(path, wait_s=wait_s):
        book = CB.load(path)
        if CB.live(book, key) is None:
            return False
        CB.attach(book, key, "role-stage", said, at_s)
        CB.save(path, book)
    return True


def cause_busy():
    """The exception class cause_attach raises on a busy book (cause_book.Busy), for dispatcher.execute's except."""
    import cause_book as CB
    return CB.Busy


def _owed_entry(a):
    return {k: a.get(k) for k in ("role", "key", "said", "at_s")}


def settle_cause_owed(st, a):
    """A cause attach carried out (attached, or no live record): it leaves the owed list, if it was there."""
    e = _owed_entry(a)
    owed = [o for o in st.get("cause_owed") or [] if isinstance(o, dict) and o != e]
    if owed:
        st["cause_owed"] = owed
    else:
        st.pop("cause_owed", None)


def owe_cause_attach(st, a):
    """A cause attach the busy book refused: kept in the dispatcher state (once), re-emitted by every supervise_roles
    until carried out. -> the dropped entry when the cap pushed one out, else None."""
    owed = [o for o in st.get("cause_owed") or [] if isinstance(o, dict)]
    if _owed_entry(a) in owed:
        return None
    owed.append(_owed_entry(a))
    dropped = owed[0] if len(owed) > CAUSE_OWED_CAP else None
    st["cause_owed"] = owed[-CAUSE_OWED_CAP:]
    return dropped


def env_cause_key(name, cls_why):
    """Pure. The cause-book key of an environment rejection: one per role and environment signal."""
    return "role-env|%s|%s" % (name, _RUN_RX.sub("#", cls_why))


def route_rejection(name, rs, cfg, run, res, errs, now, act, obs, classes=None):
    """A rejected stage close -> its route (see CAUSE_ROUTE). Says the route on the ledger; -> the route taken, one of
    builder / setter / cause_book / arbiter / alarm (the seam had nowhere to send it: the stage_rejected alarm stands)."""
    concept, item = run["concept"], run.get("item")
    cls, cls_why = rejection_cause(errs, run, res, classes)
    status = obs.get("stage_status") or stage_status
    try:
        stage = (status(concept) or {}).get("stage")
    except Exception:  # noqa: BLE001 - the stage is only part of the signature here
        stage = None
    sig = rejection_sig(stage, cls, errs)
    again = remember_rejection(rs, concept, sig, run["unit"], now)
    route = "arbiter" if again else CAUSE_ROUTE[cls]
    head = "%s run %s on %s: rejection cause %s (%s)" % (name, run["unit"], os.path.basename(
        os.path.normpath(concept)), cls, cls_why)
    said, taken = None, route
    try:
        if route == "arbiter":
            said, taken = "a 2nd identical rejection: not looped again, no arbiter (retired); alarm stands", "alarm"
        elif route == "setter":
            said, taken = "a %s rejection: the checker's owner owes the fix (no Setter: retired); alarm stands" % cls, \
                "alarm"
        elif route == "cause_book":
            key = env_cause_key(name, cls_why)
            todo = (obs.get("cause_book") or to_cause_book)(key, head, now, role=name)
            if todo is not None:
                act(**todo)
                said = "attached to cause %s (no new item; role_cause_attach)" % key
            else:
                said, taken = "no live cause record %s: alarm stands for Operations to file once" % key, "alarm"
        else:
            req = None
            if cfg.get("chain_stages") is True:
                req = chain_ask(name, rs, cfg, concept, stage, now, act, run["unit"], item, run.get("mode") or "run",
                                "%s run %s rejected (%s): %s%s" % (name, run["unit"], cls, "; ".join(errs[:4]),
                                                                   " (%d reasons in full in the launch message)"
                                                                   % len(errs) if len(errs) > 4 else ""),
                                "after its rejected run %s" % run["unit"], reasons=errs)
            said = "re-chained to %s with the reasons" % name if req else "builder route; not chained (no " \
                "chain_stages, cap reached or already asked): alarm stands"
            taken = "builder" if req else "alarm"
    except Exception as e:  # noqa: BLE001 - said; the stage_rejected alarm already stands
        said, taken = "route %s failed: %s: %s" % (route, type(e).__name__, str(e)), "alarm"
    act(do="role_hold", role=name, ticket=item, note=True, why="%s -> %s: %s" % (head, route, said))
    return taken


def escalate_turn(name, run, t, act):
    """A turn just closed waiting_owner: a Dispatcher escalation line in the Conductor's log, so a live Conductor puts
    each ask to him as a question card now, not when he asks (DESIGNER_TURNS_FIX_LEFT_ON_THE_DOORSTEP)."""
    import designer_stage as DS
    act(do="alarm", kind="role:%s:waiting_owner" % name, ticket=t.get("item") or run.get("item"), note=True,
        conductor_log=True,
        raise_first="%s's turn on %s waits on him: %d ask(s) in %s. Put each to him as a question card now." % (
            name, t["mod"], len(t["asks"]), t.get("turn") or t["dir"]),
        why=DS.turn_line(t))


def stage_abort(concept, unit):
    import designer_stage as DS
    return DS.abort_run(concept, unit)


def mode_model(role, mode):
    """The model alias a run of `mode` gets: the schedule's `model_by_mode[mode]`, else its `model`
    (OPS_ROLE_SHRINK_RUN_COST: Operations triages alarms on sonnet, owner e7069d65ba "cheaper triage model")."""
    return (role.get("model_by_mode") or {}).get(mode) or role["model"]


def job_model(role, job):
    """The model a due job launches on: its run-now request's own `model` when the Dispatcher pinned one (the incident
    clerk's daily deep read: opus, design/specs/2026-11-19-incident-clerk/boundary.md), else mode_model."""
    pinned = (job.get("manual") or job.get("run_now") or {}).get("model")
    return pinned if pinned in MODELS_OK else mode_model(role, job.get("mode"))


def launch_role(role, a):
    """The schedule entry execute launches for action `a`: the entry itself, or a copy carrying the model for this
    run's mode (mode_model); for a run-now, a copy that is enabled for this one launch and runs the request's
    pre-steps (a Designer run at stage 5: coverage_pre)."""
    selected = (a.get("run_now") or {}).get("runner")
    if selected:
        role = dict(role, runner=selected)
    model = job_model(role, a)
    if model != role["model"]:
        role = dict(role, model=model)
    if a.get("resume"):                       # account_death: the cut-off run's session, continued
        role = dict(role, resume_session=a["resume"])
    if not a.get("run_now"):
        return role
    out = dict(role, enabled=True)
    if a.get("concept"):          # a stage-machine run: its concept folder arms the Stop hook role_result_before_stop
        out["designer_dir"] = a["concept"]
        # its mod, so control admits it under that mod (a `pipe off <Mod>` refuses it at its start check), and that
        # mod's builder model pin, read now: a run asked by run-now, the harvest's chain or the orphan sweep alike
        # (mod_model.role_for; design/specs/2026-11-19-mod-model-pin/boundary.md)
        out["mod"] = os.path.basename(os.path.normpath(str(a["concept"])))
        import mod_model as MM
        import control as C
        try:
            pinned = MM.role_for(out, out["mod"])
        except (C.Unreadable, KeyError) as e:   # could not look, or a pin it cannot price: launch() refuses it, said
            out["pin_refused"] = "the builder model pin of %s: %s: %s" % (out["mod"], type(e).__name__, e)
        else:
            if pinned.get("pin"):
                a["why"] = "%s; model pinned for %s: %s, run budget x%g (pipe model)" % (
                    a.get("why") or "", out["mod"], pinned["model"], pinned["pin"]["cap_x"])
            out = pinned
    if a.get("pre_launch"):
        out["pre_launch"] = a["pre_launch"]
    if (a.get("run_now") or {}).get("parent"):     # the unit env names it for the pre-launch judge (RM_PARENT_UNIT)
        out["parent_unit"] = a["run_now"]["parent"]
    return out


def finish_slot_alarms(rs, run):
    """A scheduled run diagnosed what was open as it launched: no alarm run minutes later to say it twice
    (ALARM_RUN_DEDUPE_SAID_IT_TWICE; 2026-10-31 economy 07:30, alarm run 250 s later). A failed run covers nothing. The
    prune at the next alarm reading still re-arms an alarm that clears and re-crosses."""
    sa = rs.get("slot_alarms")
    if not sa or sa.get("unit") != run["unit"]:
        return
    rs.pop("slot_alarms")
    if run["state"] == "done":
        rs["alarms_seen"] = sorted(set(rs.get("alarms_seen") or []) | set(sa["keys"]))


def mark(rs, job, how):
    if job["mode"] == "alarm":
        seen = job.get("seen") or [job["item"]]
        rs["alarms_seen"] = sorted(set(rs.get("alarms_seen") or []) | set([seen] if isinstance(seen, str) else seen))
    else:
        rs["done"][job["key"]] = how


# ---------------------------------------------------------------- side effects (dispatcher.execute calls these)

def model_id(alias, env=None):
    """The id the environment names for alias (MODEL_VARS: the env, then SETTINGS' `env`), or None when no variable
    names it."""
    env = os.environ if env is None else env
    v = (env.get(MODEL_VARS.get(alias, "")) or "").strip()
    if not v:
        try:
            with open(SETTINGS, encoding="utf-8") as f:
                v = ((json.load(f).get("env") or {}).get(MODEL_VARS.get(alias, "")) or "").strip()
        except (OSError, ValueError, AttributeError):
            v = ""
    return v.replace("[1m]", "") or None


def run_paths(root, unit):
    d = os.path.join(root, "roles")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, unit + ".json"), os.path.join(d, unit + ".err")


def role_scope(seat, unit):
    """The claude_bounded scope a role run gets, named by the launcher (CLAUDE_SCOPE_UNIT), known before
    systemd-run and persisted with the run: claude-seat-<seat>-<unit>.scope (review dispatcher-full #1)."""
    return "claude-seat-%s-%s.scope" % (seat, unit)


def _started_at(proc, n, btime):
    """Epoch a /proc process started (stat field 22 / CLK_TCK + boot time), or None when not readable."""
    try:
        with open(os.path.join(proc, n, "stat"), "rb") as f:
            rest = f.read().rsplit(b")", 1)[1].split()
        return btime + int(rest[19]) / float(os.sysconf("SC_CLK_TCK"))
    except (OSError, IndexError, ValueError):
        return None


def _proc_state(proc, n):
    """-> the /proc state letter of pid n ("Z" a zombie), "gone" when it exited, or None when stat cannot be read."""
    try:
        with open(os.path.join(proc, n, "stat"), "rb") as f:
            return f.read().rsplit(b")", 1)[1].split()[0].decode("ascii", "replace")
    except FileNotFoundError:
        return "gone"
    except (OSError, IndexError):
        return None


def _boot_time(proc):
    try:
        with open(os.path.join(proc, "stat"), "rb") as f:
            for line in f:
                if line.startswith(b"btime "):
                    return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return None


SCAN_RETRIES = 3          # re-reads of an unreadable environ before the scan is called blind
SCAN_RETRY_S = 0.05
SINCE_SLACK_S = 5       # clock-tick rounding and boot-time granularity between a run's `at` and its first process


def scan_marked(marker, proc="/proc", uid=None, since=None):
    """-> (pids carrying RM_ROLE_UNIT=<marker>, None) or (the pids it could see, why the scan is blind).
    Blind (review r2 #3): /proc unlistable, or a process whose environ cannot be read and that is not POSITIVELY
    ruled out. Ruled out: it exited mid-scan (entry gone), it is a zombie (its environ is never readable and it runs
    nothing: one `[python3] <defunct>` of this uid made every scan blind, measured 2026-11-19,
    RIMMANDRAKE_SKIP_ZOMBIES_IN_MARKER_SCAN_ONE_DEFUNCT_BLINDS), it belongs to another uid (a run of ours never changes
    uid), or `since` (the run's start, epoch) is given and it started more than SINCE_SLACK_S before it (the marker
    is inherited, so every process of a run is younger than the run). Measured 2026-10-27: this user's systemd,
    (sd-pam) and ssh-agent are same-uid and unreadable (non-dumpable), so without `since` a real scan is blind."""
    want = ("RM_ROLE_UNIT=%s" % marker).encode()
    try:
        names = os.listdir(proc)
    except OSError as e:
        return [], "%s unlistable (%s)" % (proc, type(e).__name__)
    me, out = os.getpid(), []
    uid = os.getuid() if uid is None else uid
    btime = _boot_time(proc) if since is not None else None
    todo = [n for n in names if n.isdigit() and int(n) != me]
    why = {}
    for attempt in range(SCAN_RETRIES + 1):
        if attempt:
            time.sleep(SCAN_RETRY_S)        # a process mid-exec (or just forked) is unreadable for a moment; a
        why = {}                            # non-dumpable one stays so, and only that one makes the scan blind
        again = []
        for n in todo:
            try:
                with open(os.path.join(proc, n, "environ"), "rb") as f:
                    env = f.read()
            except FileNotFoundError:
                continue                    # exited between listdir and open
            except OSError:
                if _proc_state(proc, n) in ("Z", "gone"):
                    continue                # a zombie or exited: carries no live marker (a None state is not ruled out)
                try:
                    owner = os.stat(os.path.join(proc, n)).st_uid
                except FileNotFoundError:
                    continue                # exited
                except OSError:
                    owner = None            # unknown owner: not ruled out
                if owner is not None and owner != uid:
                    continue                # another user's process: never one of our runs
                started = _started_at(proc, n, btime) if btime is not None else None
                if started is not None and started < since - SINCE_SLACK_S:
                    continue                # older than the run: cannot carry its inherited marker
                why[n] = "pid %s (uid %s) environ unreadable" % (n, owner)
                again.append(n)
                continue
            if want in env.split(b"\0"):
                out.append(int(n))
        todo = again
        if not todo:
            break
    blind = why[sorted(why, key=int)[0]] if why else None
    return out, blind


def procs_of(marker, proc="/proc", uid=None, since=None):
    """-> the pids (not ours) carrying RM_ROLE_UNIT=<marker>, or None when the scan is blind (scan_marked): a
    partial scan is never "none" (review r2 #3)."""
    pids, blind = scan_marked(marker, proc, uid, since)
    return None if blind else pids


# budget: danger=the scope ends a run before the Dispatcher's own stop; never reached in the 14 days to 2026-11-24; no record of
# budget: its run
SCOPE_GRACE_S = 600     # the scope's own bound sits this far past run_max_s: the Dispatcher's stop comes first
# budget: danger=a run that ignores SIGTERM holds its slot; its reach leaves no record; no record of its run
SCOPE_STOP_S = 30       # TERM -> KILL escalation of that bound (TimeoutStopSec)


def scope_bound_s(role):
    """The independent wall-time bound (s) of a role run's unit and claude scope: its run_max_s + SCOPE_GRACE_S."""
    return int(max_s_of({}, dict(ROLE_DEFAULTS, **(role or {})))) + SCOPE_GRACE_S


def launch_argv(role, unit, msg, out, err, claude, session=None, tmpdir=None):
    """The transient unit's argv. A role's `pre_launch` (an argv or a list of argvs, run in its clone) runs first inside the same unit,
    its stdout sent to the err file so `out` stays claude's JSON alone; if it exits non-zero, claude never starts
    (the Designer's coverage_judge.py); PRE_DONE_EXIT ends the unit 0 (stage5_program)."""
    bounded = os.path.join(role["clone"], "src", "RimMandrake", "Utils", "claude_bounded.sh")
    path = os.path.dirname(claude) + ":" + os.environ.get("PATH", "/usr/bin:/bin")
    import form_fault as FF     # every launched brief carries the repair line (standing_rulings.md §A fault of form)
    if FF.BRIEF_LINE.strip() not in msg:
        msg = msg.rstrip() + "\n\n" + FF.BRIEF_LINE
    cmd = [bounded, "-p", msg, "--model", role["model"], "--name", "ROLE %s %s" % (role["name"], unit)] \
        + ["--settings", _control_settings(role)] \
        + list(role.get("launch_args") or []) + ["--output-format", "json", "--dangerously-skip-permissions"] \
        + (["--resume", role["resume_session"]] if role.get("resume_session")      # continues that session (resume_due)
           else ["--session-id", session] if session else [])     # its transcript, found when no result is
    selected = role.get("runner", "claude")
    if selected not in ("claude", "codex"):
        raise ValueError("runner must be claude or codex")
    if selected == "codex":
        if role.get("resume_session"):
            raise ValueError("Codex cannot resume a Claude session")
        cmd = ["python3", os.path.join(role["clone"], "src/RimMandrake/Utils/agent_runner.py"),
               "--cwd", role["clone"], "--prompt", msg, "--result", out + ".last.txt",
               "--events", out + ".events.jsonl", "--spend", out + ".spend.json",
               "--timeout", str(scope_bound_s(role))]
        for key, flag in (("codex_model", "--model"), ("codex_effort", "--effort"), ("codex_sandbox", "--sandbox")):
            value = role.get(key) or os.environ.get(key.upper())
            if value:
                cmd += [flag, value]
    elif role.get("run_budget_usd") is not None:
        # the hard per-run stop, enforced from outside: never --max-budget-usd, which tells the agent its spend every
        # turn (owner 2026-11-16, RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN; spend_watchdog.py)
        import spend_watchdog
        cmd = spend_watchdog.wrap(cmd, role["run_budget_usd"], python="python3")
        mine = os.path.join(role["clone"], "src", "RimMandrake", "rimflow", "spend_watchdog.py")
        cmd[1] = mine if os.path.exists(mine) else cmd[1]
    pre = None if role.get("resume_session") else role.get("pre_launch")    # a resume re-screens nothing
    if pre:
        # one argv, or a list of argvs run in order, each only if the one before exited 0
        steps = pre if isinstance(pre, list) and pre and all(isinstance(x, list) for x in pre) else [pre]
        if not all(isinstance(st, list) and st and all(isinstance(x, str) and x for x in st) for st in steps):
            raise ValueError("role %s: pre_launch must be a non-empty argv list or a list of them, got %r"
                             % (role.get("name"), pre))
        # the pre-steps' words are quoted into the script; the claude argv (the message) stays positional, unquoted
        script = " && ".join(" ".join(shlex.quote(x) for x in st) + " 1>&2" for st in steps)
        # a step exiting PRE_DONE_EXIT did the run's work itself (stage5_program): the unit ends 0, the model never starts
        script = '%s; r=$?; [ "$r" -eq 0 ] && exec "$@"; [ "$r" -eq %d ] && exit 0; exit "$r"' % (script, PRE_DONE_EXIT)
        cmd = ["/bin/sh", "-c", script, "role-pre-launch"] + cmd
    own = role_clones.is_role_clone(role["clone"])
    if own:
        # a role's own clone (role_clones.py) is levelled first, so no step and no model runs stale code; a failed
        # sync ends the unit before anything starts (RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES)
        cmd = ["/bin/sh", "-c", './sync 1>&2 || exit %d; exec "$@"' % role_clones.SYNC_FAILED_EXIT, "role-sync"] + cmd
    bound = scope_bound_s(role)
    return ["--user", "--quiet", "--collect",      # systemd-run's arguments; control.launch_unit names the unit
            "-p", "StandardOutput=file:" + out, "-p", "StandardError=file:" + err,
            "--working-directory", role["clone"],
            "--setenv", "AGENT_SEAT=" + role["seat"], "--setenv", "RIMFLOW_SEAT=" + role["seat"],
            # the scope's name, chosen here and persisted with the run, and the marker every process of the run
            # inherits: the two things supervise checks before a run counts as ended (review dispatcher-full #1)
            "--setenv", "CLAUDE_SCOPE_UNIT=" + role_scope(role["seat"], unit)[:-len(".scope")],
            "--setenv", "RM_ROLE_UNIT=" + unit] + (
            # a Designer (Claude) stage run: .claude/hooks/role_result_before_stop.py checks result.json before it ends
            ["--setenv", "RM_DESIGNER_DIR=" + role["designer_dir"]] if role.get("designer_dir") and selected == "claude"
            else []) + (
            # the detached run that asked for this run: the coverage judge in its pre-launch records it (with_parent)
            ["--setenv", "RM_PARENT_UNIT=" + role["parent_unit"]] if role.get("parent_unit") else []) + [
            # the run's own wall-time bound, independent of the Dispatcher (review r2 #2): claude_bounded sets it on
            # the scope (RuntimeMaxSec, TERM, then KILL after SCOPE_STOP_S), and the unit gets the same bound; so a
            # run is ended even if no tick ever supervises it again (timer off, dry-run root, unreadable state)
            "--setenv", "CLAUDE_SCOPE_RUNTIME_MAX=%d" % bound,
            "-p", "RuntimeMaxSec=%d" % bound, "-p", "TimeoutStopSec=%d" % SCOPE_STOP_S] + (
            # what the run left in its own clone is published from there (role_clones.land), however the unit ended
            ["-p", "ExecStopPost=" + land_argv(role, unit)] if own else []) + [
            "-p", "ExecStopPost=" + wrapup_argv(role, unit),
            "--setenv", "PATH=" + path] + tmp_setenv(tmpdir) + ["--"] + cmd


def land_argv(role, unit):
    """role_clones.py land for a role's own clone, from the launcher's copy, in a unit of its own (stoppost_handoff)."""
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "role_clones.py")
    return stoppost_handoff(unit + "-land", ["/usr/bin/python3", tool, "land", "--clone", role["clone"],
                                             "--seat", role["seat"]])


def wrapup_argv(role, unit):
    """The run's deterministic wrap-up (wrapup.py; AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED): systemd runs it however the
    unit ends. The launcher's own copy, not the run's clone (that one may be gone by then). A Relentless worker's clone is
    carried to the item's next worker, so its work in progress is not debris. Handed off to its own unit (stoppost_handoff):
    a walled run's InaccessiblePaths hide the launcher's checkout and the state dir from anything run inside the unit."""
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wrapup.py")
    words = ["/usr/bin/python3", tool, "unit", "--unit", unit, "--seat", role["seat"], "--clone", role["clone"]]
    if role.get("name") == "relentless":
        words.append("--carried")
    return stoppost_handoff(unit + "-wrapup", words)


# what the wrap-up and the `rimflow bridge release` it may run read from the unit's environment. An unset one arrives
# as '' (systemd-run -E, measured 2026-11-06): wrapup.scrub_handoff_env drops it (= wrapup.HANDOFF_ENV)
HANDOFF_ENV = ("PATH", "AGENT_SEAT", "RIMFLOW_SEAT", "RIMFLOW_BRIDGE_SEAT", "RM_ROLE_UNIT",
               "RM_WRAPUP_DIR", "RM_WRAPUP_SEAT_CLONES", "RM_UNDER_SELFTEST", "RM_DATA_ROOT")


def stoppost_handoff(name, words):
    """-> an ExecStopPost= value that starts `words` as a transient unit of its own, outside the stopping unit's sandbox.
    RELENTLESS_WRAPUP_FIX_STOPPOST_NAMESPACE (measured 2026-11-04, systemd 259, user manager): a "+" post still sets up a
    mount namespace when the unit has BindPaths= or TemporaryFileSystem= (the wall always binds ~/.claude/projects) and
    fails 'Failed to set up mount namespacing: Operation not supported', 3 of 3; InaccessiblePaths= alone passes. A
    systemd-run --user from inside the namespace reaches the manager and runs. "-": a failed handoff never fails the unit;
    --quiet: nothing on success, so the unit's StandardOutput=file: result is never touched."""
    env = sum((["-E", k] for k in HANDOFF_ENV), [])
    argv = ["/usr/bin/systemd-run", "--user", "--quiet", "--no-block", "--collect", "--unit", name] + env + ["--"] + words
    return "-" + " ".join(shlex.quote(w) for w in argv)


def _control_settings(role):
    """The run's PostToolUse hook: the stop channel of `pipe stop --write-now | --at-easy-spot` (control.py); a
    `slim_start` role's also drop the owner's personal CLAUDE.md and auto-memory (slim_settings)."""
    import control as C
    s = C.claude_settings(clone=role.get("clone"))
    if role.get("slim_start") is True:
        s = json.dumps(dict(json.loads(s), **slim_settings()))
    return s


def tmp_setenv(tmpdir):
    """The run's own TMPDIR/TMP/TEMP (run_tmp.py): its launcher owns that dir and deletes it when the run is over."""
    return sum((["--setenv", "%s=%s" % kv] for kv in run_tmp.env(tmpdir).items()), []) if tmpdir else []


def prepare_clone(role, runner=subprocess.run, level=None):
    """A role clone's readiness, before any run record exists -> {"refused": text or None, "lv": level's result}.
    Never raises on a missing clone: its maker unit is started (role_clones.make_in_background) and the refusal starts
    MAKING: (a planned hold). A stranded clone is refused STRANDED: with its fix line. The dispatcher runs this before
    it records the run, so a beat cut here (a fetch in level: 09:07Z and 09:35Z on 2026-11-21) gives the slot back
    instead of tracking a run that never started (RIMMANDRAKE_TRACE_DESIGNER_ROLE_CLONE_VANISHED_OPERATIONS_FAILS)."""
    if not role_clones.is_role_clone(role.get("clone")):
        return {"refused": None, "lv": None}
    kind, said = role_clones.make_in_background(os.path.basename(os.path.normpath(role["clone"])), runner=runner)
    if kind != "ready":
        return {"refused": said, "lv": None}
    level = level or (role_clones.level if runner is subprocess.run else None)
    lv = level(role["clone"]) if level else None
    if lv and lv.get("state") == "stranded":
        return {"refused": "%s role %s is NOT RUNNING: its clone %s holds %s. To pass, run: %s" % (
            role_clones.STRANDED, role.get("name"), role["clone"], lv.get("why"), lv.get("fix")), "lv": lv}
    return {"refused": None, "lv": lv}


def launch(role, unit, msg, root, claude, runner=subprocess.run, level=None):
    """-> (ok, out, run-record fields). Starts the transient unit and returns at once. ok False only when
    systemd-run itself said no; a raise (a timeout) leaves the caller's run record in place, since the unit may be up.
    The scope is named by the launcher (role_scope), never looked up: the caller recorded it before this call.
    A role clone is levelled first (role_clones.level; a test's fake runner gets none unless it passes `level`): a
    stranded ledger-only commit is landed and the launch goes on; any other is refused `STRANDED:` with its fix line,
    before a unit or a run record exists (RIMMANDRAKE_LAND_STRANDED_ROLE_COMMIT_OPERATIONS_DEAD_FOUR_HOURS)."""
    out, err = run_paths(root, unit)
    prep = role.get("_prepared") or prepare_clone(role, runner=runner, level=level)
    if prep.get("refused"):
        return False, prep["refused"], {}
    lv = prep.get("lv")
    if role.get("runner", "claude") == "codex":
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Utils"))
        import agent_runner
        try:
            agent_runner.quota_gate()
        except agent_runner.Refused as e:
            return False, str(e), {}
    session = role.get("resume_session") or str(uuid.uuid4())     # claude -p --resume keeps the session id
    # a real launch owns a TMPDIR (run_tmp.py; TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP); a test's fake runner makes no dir
    if role.get("pin_refused"):     # launch_role could not read or price the mod's model pin: nothing starts
        return False, "REFUSED by control: %s" % role["pin_refused"], {}
    tmpdir = run_tmp.prepare(unit) if runner is subprocess.run else None
    import control as C     # the one admission point (control.py)
    mod = role.get("mod") or (os.path.basename(os.path.normpath(role["concept"])) if role.get("concept") else None)
    r = C.launch_unit(launch_argv(role, unit, msg, out, err, claude, session, tmpdir),
                      {"family": "role", "unit": unit, "role": role.get("name"), "mod": mod, "model": role.get("model"),
                       "extra_units": [role_scope(role["seat"], unit)]},
                      runner=runner, clone=role.get("clone"), capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)  # budget: danger=a hung launch holds the Dispatcher's tick; longest=1.3s (admission to start of 1057 runs, control.db)
    text = ((r.stdout or "") + (r.stderr or "")).strip()
    if getattr(r, "refused", False):
        return False, "REFUSED by control: %s" % r.why, {}
    if r.returncode:
        return False, "systemd-run exit %d: %s" % (r.returncode, text), {}
    scope = role_scope(role["seat"], unit)
    said = "" if not lv or lv.get("state") in ("level", None) else (
        "; its clone's stranded ledger commit(s) landed: %s" % ", ".join(lv.get("landed") or []) if lv["state"] == "landed"
        else "; its clone could not be checked for stranded commits (%s: %s), the unit's ./sync decides" % (
            lv["state"], lv.get("why")))
    return True, "unit %s started (scope %s)%s" % (unit, scope, said), {
        "out": out, "err": err, "scope": scope, "marker": unit,
        "runner": role.get("runner", "claude"),
        "model_id": (role.get("codex_model") or os.environ.get("CODEX_MODEL") or "config")
        if role.get("runner") == "codex" else model_id(role["model"]) or (
            role["model"] if str(role["model"]).startswith("claude-") else None), "session": session}


def scope_of(unit, seat, runner=subprocess.run):
    """claude_bounded's scope for the unit (claude-seat-<seat>-<unit MainPID>.scope), or None when not knowable now."""
    try:
        r = runner(["systemctl", "--user", "show", "-p", "MainPID", "--value", unit], capture_output=True, text=True,
                   timeout=30, stdin=subprocess.DEVNULL)
        main_pid = (r.stdout or "").strip() if not r.returncode else ""
    except Exception:  # noqa: BLE001
        main_pid = ""
    return ("claude-seat-%s-%s.scope" % (seat, main_pid)) if main_pid.isdigit() and main_pid != "0" else None


def unit_state(unit, runner=subprocess.run):
    """ActiveState; "not-found" when systemd CONFIRMS it has no such unit; "unknown" when systemctl fails, times out
    or says nothing (supervise_roles keeps it busy). A failed show is absence only on positive evidence: its stderr
    says the unit is not found / not loaded, or a second query reads LoadState=not-found. Anything else (a bus error,
    a timeout, an invalid name) stays "unknown" (ROLE_UNITSTATE_FIX_GHOST_RUNS_NEVER_LEAVE: a collected unit read
    "unknown" and its run was kept busy and re-stopped forever)."""
    try:
        r = runner(["systemctl", "--user", "show", "-p", "ActiveState", "--value", unit], capture_output=True,
                   text=True, timeout=30, stdin=subprocess.DEVNULL)
        state = (r.stdout or "").strip() if not r.returncode else ""
        if state:
            return state
        if r.returncode and NOT_FOUND_RX.search(r.stderr or ""):
            return "not-found"
    except Exception:  # noqa: BLE001
        return "unknown"
    return "not-found" if load_state(unit, runner) == "not-found" else "unknown"


def load_state(unit, runner=subprocess.run):
    """LoadState ("loaded", "not-found", ...), or None when the query fails, times out or says nothing."""
    try:
        r = runner(["systemctl", "--user", "show", "-p", "LoadState", "--value", unit], capture_output=True,
                   text=True, timeout=30, stdin=subprocess.DEVNULL)
        return ((r.stdout or "").strip() or None) if not r.returncode else None
    except Exception:  # noqa: BLE001
        return None


def read_result(run):
    try:
        with open(run["out"], encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, KeyError, TypeError):
        try:
            with open(run.get("err") or "", encoding="utf-8", errors="replace") as f:
                run["err_tail"] = f.read()
        except OSError:
            pass
        return None


def _stop_call(runner, argv, timeout):
    """One systemctl call, never raising: -> its line for the stop result."""
    try:
        r = runner(argv, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001 - a hung or failing systemctl must not skip the other targets (r2 #1)
        return "%s %s raised %s: %s" % (argv[2], argv[-1], type(e).__name__, str(e)[:80])
    if r.returncode == 0:
        return "%s %s ok" % (argv[2], argv[-1])
    return "%s %s exit %d: %s" % (argv[2], argv[-1], r.returncode,
                                  ((r.stdout or "") + (r.stderr or "")).strip())


def _signal_marked(marker, force, procs, kill, since=None):
    """TERM (KILL when force) every process carrying the run's marker that the scan can see, even when it is partly
    blind (the next tick's ended() still holds the run busy then); never raises. -> its line."""
    blind = None
    try:
        if procs:
            pids = procs(marker, since=since)
        else:
            pids, blind = scan_marked(marker, since=since)
    except Exception as e:  # noqa: BLE001
        return "marker scan raised %s: UNMEASURED" % type(e).__name__
    if pids is None:
        return "marker scan UNMEASURED"
    if blind and not pids:
        return "marker scan UNMEASURED (%s)" % blind
    if not pids:
        return "no process marked %s" % marker
    sig, sent = (signal.SIGKILL if force else signal.SIGTERM), 0
    for pid in pids:
        try:
            kill(pid, sig)
            sent += 1
        except Exception:  # noqa: BLE001 - gone, or not ours: the next tick's scan decides
            pass
    return "%s to %d of %d process(es) marked %s%s" % ("KILL" if force else "TERM", sent, len(pids), marker,
                                                       "; scan partly UNMEASURED (%s)" % blind if blind else "")


def stop(unit, scope, runner=subprocess.run, seat=None, unit_gone=False, marker=None, force=False, procs=None,
         kill=os.kill, since=None):
    """The claude process lives in claude_bounded's scope (role_scope, persisted with the run), outside the unit:
    stopping the unit alone would leave it running. Every target is tried on its own and none can stop the others
    (review r2 #1): a systemctl that raises or hangs (its timeout) is one line of the result, never an exit.
      - force (the third stop on): the marked processes get KILL FIRST (no systemd involved, so a hung systemctl
        cannot hold it back), then `systemctl kill --signal=SIGKILL` the scope (its whole cgroup), then the stops;
      - else: `systemctl stop --no-block` the scope, then the unit (queued, never waited on), then TERM the marked.
    A run recorded before scopes were named and with none resolved: resolve it now from the unit's MainPID. Whether
    the stop took is decided by the next tick (supervise: unit, scope AND marker scan), not here. Never raises."""
    said = []
    if not scope and seat and not unit_gone:
        try:
            scope = scope_of(unit, seat, runner)
        except Exception as e:  # noqa: BLE001
            said.append("scope lookup raised %s" % type(e).__name__)
    names = [n for n in (scope, None if unit_gone else unit) if n]
    if marker and force:
        said.append(_signal_marked(marker, True, procs, kill, since))
    if force and scope:
        said.append(_stop_call(runner, ["systemctl", "--user", "kill", "--signal=SIGKILL", scope], 30))
    for n in names:
        said.append(_stop_call(runner, ["systemctl", "--user", "stop", "--no-block", n], 30))
    if marker and not force:
        said.append(_signal_marked(marker, False, procs, kill, since))
    return "; ".join(said) or "nothing to stop (no scope, unit gone, no marker)"


def off_switch(path):
    """-> None when the file is absent, else its first line ('' when empty)."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.readline().strip()
    except OSError:
        return "unreadable"


def read_ops(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, TypeError):
        return None


def resolve_account():
    """The switcher-registry label of the account this machine's sessions are logged in as (account_usage)."""
    utils = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils")
    if utils not in sys.path:
        sys.path.append(utils)
    try:
        import account_usage as AU
        email = AU.live_email()
        for label, mail in AU.registry().items():
            if email and mail == email:
                return label
    except Exception:  # noqa: BLE001
        pass
    return None


# budget: danger=a hung tick holds a hand command with no end; longest=97s (a real --apply tick, 2026-11-06)
def _cli_state(root, wait_s=1000):
    """The live state under the tick's own lock (dispatcher.stop_runs's pattern): a request written beside a tick
    would be lost to its save. -> (lock file, D, state)."""
    import fcntl
    import dispatcher as D
    os.makedirs(root, exist_ok=True)
    lk = open(os.path.join(root, "tick.lock"), "w")
    t0 = time.time()
    while True:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.time() - t0 > wait_s:
                lk.close()
                raise OSError("tick.lock at %s held for %d s" % (root, wait_s))
            time.sleep(2)
    try:
        st = D.load_state(root) if os.path.exists(os.path.join(root, "state.json")) else {}
    except Exception:
        lk.close()
        raise
    return lk, D, st


def main(argv=None):
    """run-now: ask for one run of a role by hand (it need not be enabled); the next dispatcher tick launches it
    through every gate a scheduled run passes (off switch, PAUSE, busy, ops reading, caps, account).
    run-status: what a role's last run-now did."""
    import argparse
    p = argparse.ArgumentParser(prog="role_launch.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run-now")
    r.add_argument("--schedule", help="the dispatcher schedule (default dispatcher_schedule.json)")
    r.add_argument("--root", help="the dispatcher state dir (default the live one)")
    r.add_argument("--role", required=True)
    r.add_argument("--runner", choices=("claude", "codex"), help="override the schedule runner for this run only")
    r.add_argument("--by")
    r.add_argument("--why")
    r.add_argument("--mode", help="/".join(RUN_NOW_MODES) + " (default the role's own scheduled mode)")
    r.add_argument("--concept", help="design/concepts/<Mod> (a stage-machine role, the Designer: required)")
    r.add_argument("--covers-slot", action="store_true", help="this run IS the role's next scheduled run today (its slot is marked covered, the daily cap is asked for one run)")
    r.add_argument("--cancel", action="store_true")
    r.add_argument("--apply", action="store_true")
    s = sub.add_parser("run-status")
    s.add_argument("--root")
    s.add_argument("--role", required=True)
    g = sub.add_parser("stage5-program", help="the stage-5 pre-launch step after the judge (stage5_program)")
    g.add_argument("concept")
    j = sub.add_parser("stage5-judge", help="the stage-5 pre-launch judge step, only while still at stage 5 (stage5_judge)")
    j.add_argument("concept")
    a = p.parse_args(argv)
    if a.cmd == "stage5-judge":
        return stage5_judge(os.path.abspath(a.concept))
    if a.cmd == "stage5-program":
        concept = os.path.abspath(a.concept)
        try:
            how, line = stage5_program(concept, os.environ.get("RM_ROLE_UNIT") or None)
        except Exception as e:  # noqa: BLE001 - a guard that cannot run lets the Designer run, and says so
            line = "stage5-program DID NOT RUN: %s: %s; the Designer runs as today" % (type(e).__name__, e)
            print(line, file=sys.stderr)
            try:
                import designer_stage as DS
                st = DS.load_state(concept)
                DS.hist(st, "program_error", "run %s: %s" % ((st.get("running") or {}).get("run"), line))
                DS.write_json(DS.state_path(concept), st)
            except Exception:  # noqa: BLE001 - the err file keeps the line
                pass
            return 0
        print("stage5-program: %s" % line)
        return PRE_DONE_EXIT if how == "closed" else 0
    import dispatcher as D
    root = a.root or D.state_root(True)
    if a.cmd == "run-status":
        try:
            st = D.load_state(root) if os.path.exists(os.path.join(root, "state.json")) else {}
        except Exception as e:  # noqa: BLE001
            print("UNMEASURED: state unreadable: %s" % e, file=sys.stderr)
            return 2
        rs = (st.get("roles") or {}).get(a.role) or {}
        print(json.dumps({"pending": rs.get("run_now"), "last": rs.get("run_now_last"),
                          "running": [x for x in rs.get("runs") or [] if x.get("state") == "running"]}, indent=1))
        return 0
    now = time.time()
    if not a.cancel:
        try:
            sch = D.load_schedule(a.schedule)
            req = run_now_request(sch, {"role": a.role, "by": a.by, "why": a.why, "mode": a.mode,
                                        "concept": a.concept, "runner": a.runner}, now)
            if a.covers_slot:
                req["covers_slot"] = True
            req = with_parent(req, os.environ)
        except (OSError, ValueError) as e:
            print("REFUSED: %s" % e, file=sys.stderr)
            return 2
        print(json.dumps(req))
    if not a.apply:
        print("dry run: nothing written (--apply writes it)")
        return 0
    try:
        lk, D, st = _cli_state(root)
    except Exception as e:  # noqa: BLE001
        print("UNMEASURED: %s; nothing written" % e, file=sys.stderr)
        return 2
    try:
        rs = st.setdefault("roles", {}).setdefault(a.role, {})
        if a.cancel:
            gone = rs.pop("run_now", None)
            if gone is not None:
                rs["run_now_last"] = dict(gone, outcome="cancelled", decided=now)
            D.save(st, root)
            print("cancelled" if gone else "no request pending")
            return 0
        if rs.get("run_now"):
            print("REFUSED: a run-now is already pending for %s (%s); --cancel it first" % (
                a.role, json.dumps(rs["run_now"])), file=sys.stderr)
            return 1
        rs["run_now"] = req
        D.save(st, root)
        print("requested: the next dispatcher tick decides it (role_launch.py run-status --role %s)" % a.role)
        return 0
    finally:
        lk.close()


if __name__ == "__main__":
    sys.exit(main())
