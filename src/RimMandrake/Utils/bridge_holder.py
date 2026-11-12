#!/usr/bin/env python3
"""Who a process holds the bridge AS (RELENTLESS_SEAT_UNTANGLE_FROM_BENCH). Relentless owns its items as BENCH, the key the
Conductor's window also runs under, so a hold keyed on BENCH read as "ours" from both sides. Relentless holds as
RELENTLESS. Any check of "is this hold mine" compares the holder with identity(seat), never with the seat.

Stdlib only and no rimflow import: the preflights run under Windows python.exe, where rimflow's model (fcntl) cannot load."""
import os
import re

ENV = "RIMFLOW_BRIDGE_SEAT"
IN_TEST_ENV = "RIMFLOW_BRIDGE_SEAT_IN_TEST"
RELENTLESS = "RELENTLESS"
# Worker seats with their own ledger shard, queue view, bridge hold and host guard. The tuple keeps its first name
# (it began with the Codex loops); the CLAUDE_* seats are the Claude Whittle loops (infrastructure/whittle_claude/,
# owner order 2026-11-11: two live FlowWorks loops, one per game, plus offline loops on Archmagi).
CODEX_SEATS = ("CODEX_ARCHMAGI_FWDRAIN", "CODEX_STEVEDESKTOP_HUGETHINGS",
               "CLAUDE_ARCHMAGI_FWLIVE", "CLAUDE_STEVEDESKTOP_FWLIVE",
               "CLAUDE_ARCHMAGI_OFFLINE1", "CLAUDE_ARCHMAGI_OFFLINE2", "CLAUDE_ARCHMAGI_OFFLINE3")
HOLDERS = (RELENTLESS,) + CODEX_SEATS


def identity(seat, env=None):
    """-> the name `seat` holds the bridge under. A process Relentless started says RIMFLOW_BRIDGE_SEAT=RELENTLESS; that
    renames BENCH only, so OWNER (`./bridge`, `./game`) and RUNNER stay themselves. A redirected ledger keeps its
    fixture seats unless it asks (RIMFLOW_BRIDGE_SEAT_IN_TEST): a selftest run by a Relentless worker inherits the
    variable, and would otherwise read its BENCH fixtures as a stranger's."""
    env = os.environ if env is None else env
    name = (env.get(ENV) or "").strip().upper()
    if seat != "BENCH" or name not in HOLDERS:
        return seat
    if env.get("RIMFLOW_LEDGER") and not env.get(IN_TEST_ENV):
        return seat
    return name


def held_by(text):
    """-> the holder a BRIDGE mirror or a `bridge who` reading names, else None (free or unreadable). The mirror's `for`
    and `note` lines are free text that can name any seat: only the holding line counts."""
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"(?:HELD|bridge held by)\s+(\S+)", line) or re.match(r"(\S+) holds the bridge\b", line)
        if m:
            return m.group(1)
    return None


def process_env(base=None):
    """-> `base` (default os.environ) for a process Relentless starts. WSLENV carries the name into a python.exe child:
    wsl.exe drops every variable it does not list, and a preflight without it would read the Conductor's hold as ours."""
    out = dict(os.environ if base is None else base)
    out[ENV] = RELENTLESS
    names = [n for n in (out.get("WSLENV") or "").split(":") if n]
    if not any(n.split("/")[0] == ENV for n in names):
        names.append(ENV)
    out["WSLENV"] = ":".join(names)
    return out


def rimflow_env(seat, env=None):
    """-> `env` assignments that run a rimflow child under wsl.exe as this seat (wsl.exe drops the caller's variables).
    RELENTLESS is a holder, not a seat: its ledger seat stays BENCH and only the bridge name changes."""
    if identity(seat, env) == RELENTLESS:
        return ["AGENT_SEAT=BENCH", "%s=%s" % (ENV, RELENTLESS)]
    return ["AGENT_SEAT=%s" % identity(seat, env)]
