#!/usr/bin/env python3
"""build_fixtures.py - write src/RimMandrake/Utils/fixtures/account_live_cases.json from recorded inputs (run once).

Recorded: the status output of `claude-account --json status` on Archmagi and on SteveDesktop (over ssh, through a
login shell), captured 2026-11-22, and every `use` row of ~/.claude-accounts/log.jsonl, each rendered as the Archmagi
status with `live` set to the row's `to`. Fixture: the broken shapes that the boundary page names. Emails are scrubbed.

    python3 build_fixtures.py ARCHMAGI_STATUS.json STEVEDESKTOP_STATUS.txt [LOG.jsonl]
"""
import json
import os
import re
import sys

TOP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(TOP, "src/RimMandrake/Utils/fixtures/account_live_cases.json")


def scrub(s):
    return re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                  lambda m: m.group(0).split("@")[0].split(".")[0][:6] + "@x.test", s)


def case(name, source, rc, out, kind, live=None, raises=None):
    return {"name": name, "source": source, "rc": rc, "out": out, "raises": raises,
            "want": {"kind": kind, "live": live}}


def main(argv):
    arch = scrub(open(argv[0]).read())
    steve = scrub(open(argv[1]).read())
    log = argv[2] if len(argv) > 2 else os.path.expanduser("~/.claude-accounts/log.jsonl")
    a = json.loads(arch)
    cases = [case("archmagi-real", "recorded: Archmagi status 2026-11-22", 0, arch, "value", a["live"]),
             case("stevedesktop-real-over-ssh", "recorded: SteveDesktop status over ssh 2026-11-22", 0, steve, "value",
                  json.loads(steve)["live"])]
    for line in open(log):
        d = json.loads(line)
        if d.get("op") != "use" or not d.get("to"):
            continue
        st = dict(a, live=d["to"], machine=d.get("machine") or a["machine"])
        cases.append(case("switch-to-%s-%s" % (d["to"], d["ts"]), "recorded: log.jsonl use row %s" % d["ts"], 0,
                          json.dumps(st, indent=2) + "\n", "value", d["to"]))
    clean = arch
    cases += [
        case("warning-line-before", "fixture", 0, "warning: refreshed token\n" + clean, "value", a["live"]),
        case("login-banner-before-and-note-after", "fixture", 0, "Welcome {user}\n" + clean + "\n(note) done {x}\n",
             "value", a["live"]),
        case("acceptance-fake", "fixture: acceptance.sh ACCOUNT", 0,
             'warning: refreshed token\n{"ok": true, "live": "lukas"}\n', "value", "lukas"),
        case("long-padding-before", "fixture: selftest_slot_allocator's long answer", 0,
             " " * 5000 + '{"live": "system", "x": "' + "a" * 4000 + '"}\n', "value", "system"),
        case("no-ok-key", "fixture: switching_plan's fake", 0, '{"machine": "testbox", "live": "system", "armed": false}\n',
             "value", "system"),
        case("cut-at-1000-chars", "fixture", 0, clean[:1000], "failed"),
        case("cut-at-2000-chars-of-a-long-status", "fixture", 0,
             json.dumps(dict(a, pad="p" * 3000), indent=2)[:2000], "failed"),
        case("live-empty-string", "fixture", 0, json.dumps(dict(a, live="")), "empty"),
        case("live-null", "fixture", 0, json.dumps(dict(a, live=None)), "empty"),
        case("live-not-a-string", "fixture", 0, json.dumps(dict(a, live=3)), "empty"),
        case("refused-rc1", "fixture: the switcher's refusal shape", 1,
             '{"ok": false, "refused": "refused: this machine is DISARMED"}\n', "failed"),
        case("not-ok-rc0", "fixture", 0, json.dumps({"ok": False, "live": "beta"}), "failed"),
        case("rc3-with-a-live-name", "fixture", 3, clean, "failed"),
        case("empty-stdout", "fixture", 0, "", "failed"),
        case("garbage", "fixture", 0, "Traceback (most recent call last):\n  oops\n", "failed"),
        case("json-list", "fixture", 0, '[{"x": 1}]', "failed"),
        case("timeout", "fixture", None, None, "could_not_look", raises="timeout"),
        case("not-found", "fixture", None, None, "could_not_look", raises="notfound"),
        case("permission-denied", "fixture", None, None, "could_not_look", raises="oserror"),
    ]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"built_by": "design/specs/2026-11-22-live-account/build_fixtures.py", "cases": cases}, f, indent=1)
        f.write("\n")
    print("%d cases (%d recorded) -> %s" % (len(cases), sum(c["source"].startswith("recorded") for c in cases), OUT))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
