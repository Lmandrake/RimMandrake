#!/usr/bin/env python3
"""selftest_login_deadline.py: the forewarning of a login's fixed deadline (login_watch.login_deadlines and its step).

Page: design/specs/2026-11-22-login-deadline-forewarning/boundary.md. Each t_<promise> is that page's promise.
Why: on 2026-11-22 the lukas login reached its refreshTokenExpiresAt (06:06:40 PST); the last refresh before it gave an
access token to 10:42 PST, and from then the login was dead until the owner ran /login at 11:20 PST. Nothing warned
before it died, though the deadline was in the credential file for 30 days.
"""
import json
import os
import shlex
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dispatcher as D  # noqa: E402
import login_watch as LW  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0
DAY = 86400.0
SECRET = "sk-ant-ort01-PLANTED-SECRET-must-never-appear"


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (("  (%s)" % detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def vault(d, accts, live="lukas"):
    """accts: {name: deadline epoch s | None (field absent) | 'junk' (unreadable file)}."""
    for a, dl in accts.items():
        os.makedirs(os.path.join(d, a), exist_ok=True)
        p = os.path.join(d, a, ".credentials.json")
        with open(p, "w") as f:
            if dl == "junk":
                f.write("{not json")
                continue
            o = {"accessToken": SECRET, "refreshToken": SECRET, "expiresAt": int((NOW + 3600) * 1000)}
            if dl is not None:
                o["refreshTokenExpiresAt"] = int(dl * 1000)
            json.dump({"claudeAiOauth": o}, f)
    with open(os.path.join(d, "live.json"), "w") as f:
        json.dump({"account": live, "rt_hash": "x"}, f)
    return d


def sch():
    return {"alarm_every_s": 21600, "login_watch": {"enabled": True, "auto_switch": False, "deadline_warn_s": 3 * DAY}}


def obs(root, probe=(True, ""), deadlines=None):
    reader = deadlines or (lambda: LW.login_deadlines(root))
    return {"paused": None, "agents": {"state": "MISSING"},
            "login": {"probe": lambda: probe, "account": lambda: ("lukas", ()), "deadlines": reader}}


def run(st, o, now=NOW):
    acts = []
    hold = LW.step(sch(), st, o, now, lambda **k: acts.append(k), D.iso)
    return hold, acts


def kinds(acts, prefix="login:deadline"):
    return [a for a in acts if a.get("do") == "alarm" and str(a.get("kind", "")).startswith(prefix)]


def have():
    if not hasattr(LW, "login_deadlines"):
        check("login_watch.login_deadlines exists", False, "no forewarning code on this tree")
        return False
    return True


def t_a_login_near_its_deadline_alarms():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        dl = NOW + 2 * DAY
        vault(d, {"lukas": NOW + 40 * DAY, "steven": dl})
        _, a = run({}, obs(d))
        al = kinds(a)
        check("a-login-near-its-deadline-alarms: one alarm, for steven only", len(al) == 1 and "steven" in al[0]["kind"],
              repr([x.get("kind") for x in al]))
        if al:
            x = al[0]
            check("a-login-near-its-deadline-alarms: kind is per account and deadline",
                  x["kind"] == "login:deadline:Archmagi:steven:%d" % int(dl))
            check("a-login-near-its-deadline-alarms: into the ledger and the Conductor log",
                  x.get("note") is True and x.get("conductor_log") is True)
            check("a-login-near-its-deadline-alarms: names the local deadline", D.iso(dl)[:10] in x["why"] or
                  LW._local(dl)[:10] in x["why"], x["why"])
            check("a-login-near-its-deadline-alarms: vault account renews by enroll from a plain terminal",
                  "claude-account enroll steven" in x["raise_first"], x["raise_first"])


def t_the_live_login_renews_from_a_plain_terminal():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        vault(d, {"lukas": NOW + 1 * DAY}, live="lukas")
        _, a = run({}, obs(d))
        al = kinds(a)
        check("the-live-login-renews-from-a-plain-terminal: alarms", len(al) == 1)
        if al:
            rf = al[0]["raise_first"]
            check("the-live-login-renews-from-a-plain-terminal: says live and `claude auth login`, not /login in a window",
                  "live" in al[0]["why"] and "claude auth login" in rf and "not /login in a window" in rf, rf)


def t_a_past_deadline_says_expired():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        vault(d, {"system": NOW - 3600})
        _, a = run({}, obs(d))
        al = kinds(a)
        check("a-past-deadline-says-expired", len(al) == 1 and "EXPIRED" in al[0]["raise_first"],
              repr([(x.get("kind"), x.get("raise_first")) for x in al]))


def t_a_login_far_from_its_deadline_is_quiet():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        vault(d, {"lukas": NOW + 3 * DAY + 60, "steven": NOW + 29 * DAY})
        h, a = run({}, obs(d))
        check("a-login-far-from-its-deadline-is-quiet", not kinds(a) and h is None, repr(a))


def t_an_unreadable_deadline_is_unmeasured_not_quiet():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        vault(d, {"lukas": NOW + 20 * DAY, "steven": None, "system": "junk"})
        r = LW.login_deadlines(d)
        check("an-unreadable-deadline-is-unmeasured-not-quiet: reader says why for each",
              r["lukas"]["deadline"] == NOW + 20 * DAY and r["steven"]["deadline"] is None and r["steven"]["why"]
              and r["system"]["deadline"] is None and r["system"]["why"], repr(r))
        _, a = run({}, obs(d))
        al = kinds(a, "login:deadline:unmeasured")
        check("an-unreadable-deadline-is-unmeasured-not-quiet: one unmeasured alarm per blind account",
              sorted(x["kind"] for x in al) == ["login:deadline:unmeasured:steven", "login:deadline:unmeasured:system"],
              repr([x.get("kind") for x in a]))
    with tempfile.TemporaryDirectory() as d:
        r = LW.login_deadlines(os.path.join(d, "absent"))
        check("an-unreadable-deadline-is-unmeasured-not-quiet: a missing vault is no reading, not an empty set",
              r is None)
        _, a = run({}, obs(os.path.join(d, "absent")))
        check("an-unreadable-deadline-is-unmeasured-not-quiet: a missing vault alarms blind",
              [x["kind"] for x in kinds(a)] == ["login:deadline:blind"], repr([x.get("kind") for x in a]))


def t_the_deadline_check_never_reads_a_token():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        vault(d, {"steven": NOW + DAY, "system": None})
        r = LW.login_deadlines(d)
        _, a = run({}, obs(d))
        blob = json.dumps(r) + json.dumps(a, default=str)
        check("the-deadline-check-never-reads-a-token", SECRET not in blob and "accessToken" not in blob
              and "refreshToken\"" not in blob)


def t_a_renewed_login_ends_the_warning():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        vault(d, {"steven": NOW + DAY})
        st = {}
        _, a1 = run(st, obs(d))
        vault(d, {"steven": NOW + 30 * DAY})            # a fresh sign-in moved the deadline
        _, a2 = run(st, obs(d), NOW + 300)
        check("a-renewed-login-ends-the-warning", len(kinds(a1)) == 1 and not kinds(a2), repr(a2))


def t_one_deadline_read_a_second_apart_is_one_alarm_kind():
    """RIMMANDRAKE_FIX_LOGIN_DEADLINE_ALARM_REKEYS_EACH_REFRESH: one fixed deadline read as ...366, ...367 and ...368
    (told.jsonl 2026-11-24) made three alarm kinds, and each new kind called an Operations run. A new sign-in, days
    later, is a new deadline and a new kind."""
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        st, seen = {}, []
        for i, jitter in enumerate((0.0, 1.0, -1.0, 2.0)):
            vault(d, {"steven": NOW + 2 * DAY + jitter})
            _, a = run(st, obs(d), NOW + 600 * i)
            seen += [x["kind"] for x in kinds(a)]
        check("one-deadline-read-a-second-apart-is-one-alarm-kind: one kind for one deadline", len(set(seen)) == 1,
              repr(sorted(set(seen))))
        vault(d, {"steven": NOW + 6 * DAY})              # a new sign-in four days later, read when it is near
        _, a = run(st, obs(d), NOW + 4 * DAY)
        new = [x["kind"] for x in kinds(a)]
        check("one-deadline-read-a-second-apart-is-one-alarm-kind: a new sign-in is a new kind",
              len(new) == 1 and new[0] not in seen, repr((new, sorted(set(seen)))))

        warned = "login:deadline:Archmagi:steven:%d" % (NOW + 2 * DAY - 1)
        st = {"alarms": {warned: NOW - 600}}            # Dispatcher state from before the fix
        vault(d, {"steven": NOW + 2 * DAY + 2})
        _, a = run(st, obs(d))
        got = [x["kind"] for x in kinds(a)]
        check("one-deadline-read-a-second-apart-is-one-alarm-kind: reuses an already told kind",
              got == [warned], repr(got))


def t_a_broken_deadline_check_never_stops_the_login_probe():
    if not have():
        return
    with tempfile.TemporaryDirectory() as d:
        def boom():
            raise RuntimeError("planted")
        st = {}
        run(st, obs(d, probe=(False, "auth status says not logged in"), deadlines=boom))
        h, a = run(st, obs(d, probe=(False, "auth status says not logged in"), deadlines=boom), NOW + 120)
        check("a-broken-deadline-check-never-stops-the-login-probe: still held and alarmed dead",
              bool(h) and any(x.get("kind", "").startswith("login:expired:") for x in a), repr(a))
        check("a-broken-deadline-check-never-stops-the-login-probe: the break is itself an alarm",
              any(x.get("kind") == "login:deadline:watch" for x in a), repr([x.get("kind") for x in a]))


def t_the_dispatcher_wires_the_reader():
    if not have():
        return
    o = D.login_obs({"login_watch": {"enabled": True}})
    check("the-dispatcher-wires-the-reader", isinstance(o, dict) and callable(o.get("deadlines")), repr(o and list(o)))


def t_each_vault_host_warns_of_its_own_deadlines():
    with tempfile.TemporaryDirectory() as d:
        local, remote = (os.path.join(d, host) for host in ("arch", "steve"))
        dl = NOW - 3600
        vault(local, {"steven": dl})
        epochs = {"steven": dl, "system": 0, "lukas": NOW + DAY}
        vault(remote, epochs)
        with open(os.path.join(remote, "health.json"), "w") as f:     # the live shape: it holds no deadline at all
            json.dump({n: {"observed": 1, "renewed": 1, "warm": None} for n in epochs}, f)
        with open(os.path.join(remote, "live.json"), "w") as f:
            json.dump({"account": "steven"}, f)
        s = sch()
        s["login_watch"]["vault_root"] = local
        o = D.login_obs(s)
        o["probe"] = lambda: (True, "")
        check_output = subprocess.check_output

        def fake_ssh(argv, **kwargs):
            assert argv[0] == "ssh" and argv[-2] == "steve-test"
            command = shlex.split(argv[-1])
            return check_output(command[:-1] + [remote], **kwargs)

        with patch.dict(os.environ, STEVE_WSL="steve-test"), patch.object(LW.subprocess, "check_output", side_effect=fake_ssh):
            _, a = run({}, {"login": o})
        alarms = {x["kind"]: x for x in kinds(a)}
        steven = alarms.get("login:deadline:SteveDesktop:steven:%d" % dl, {})
        check("each-vault-host-warns-of-its-own-deadlines: Dispatcher warns for SteveDesktop's expired steven login",
              "EXPIRED" in steven.get("raise_first", "") and "SteveDesktop" in steven["raise_first"]
              and "claude-account enroll steven" in steven["raise_first"], repr(list(alarms)))
        check("each-vault-host-warns-of-its-own-deadlines: local warning, zero deadline and near deadline are distinct",
              set(alarms) == {"login:deadline:Archmagi:steven:%d" % dl, "login:deadline:SteveDesktop:steven:%d" % dl,
                              "login:deadline:SteveDesktop:system:0", "login:deadline:SteveDesktop:lukas:%d" % (NOW + DAY)},
              repr(list(alarms)))


def t_an_unreadable_host_names_its_cause():
    with tempfile.TemporaryDirectory() as d:
        s = sch()
        s["login_watch"]["vault_root"] = vault(d, {})
        o = D.login_obs(s)
        o["probe"] = lambda: (True, "")
        for reply, cause in ((OSError("down"), "could not look: down"), ("bad json", "failed: invalid deadline reply"),
                             ("{}", None)):
            with patch.object(LW.subprocess, "check_output", side_effect=[reply]):
                h, a = run({}, {"login": o})
            alarms = kinds(a)
            got = alarms[0]["why"] if len(alarms) == 1 else ""
            check("an-unreadable-host-names-its-cause: %s" % (cause or "empty is quiet"),
                  h is None and (not alarms if cause is None else
                                 "SteveDesktop" in got and "UNMEASURED" in got and cause in got), repr(a))


def main():
    for t in (t_a_login_near_its_deadline_alarms, t_the_live_login_renews_from_a_plain_terminal,
              t_a_past_deadline_says_expired, t_a_login_far_from_its_deadline_is_quiet,
              t_an_unreadable_deadline_is_unmeasured_not_quiet, t_the_deadline_check_never_reads_a_token,
              t_a_renewed_login_ends_the_warning, t_one_deadline_read_a_second_apart_is_one_alarm_kind,
              t_a_broken_deadline_check_never_stops_the_login_probe,
              t_the_dispatcher_wires_the_reader, t_each_vault_host_warns_of_its_own_deadlines,
              t_an_unreadable_host_names_its_cause):
        t()
    print("selftest_login_deadline: %s" % ("FAILED %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
