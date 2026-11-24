#!/usr/bin/env python3
"""pager_plants.py — planted faults that selftest_pager.py must catch (mutate-your-checker).

Each plant is one realistic fault in a COPY of pager.py or ops_watch_pager.py; the copy's selftest must print its own
`FAIL:` line. The unmutated control must print ALL PASS first, or nothing is believed.
    python3 src/RimMandrake/Utils/pager_plants.py        CAUGHT n of n (exit 0) / NOT CAUGHT ... (exit 1) / BROKEN (3)
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FILES = ("pager.py", "ops_watch_pager.py", "pager_classes.json", "selftest_pager.py", "rmpaths.py")

# (name, file, anchor, replacement): the fault, written before the run, and where it should go red
PLANTS = [
    ("operations proved by environment alone", "pager.py",
     'if any(s in (unit + ".service", "claude-seat-BENCH-%s.scope" % unit) for s in segs):', "if True:"),
    ("a helper that unset RM_ROLE_UNIT passes", "pager.py",
     'if any(re.match(r"^(claude-seat-[A-Za-z]+-)?rm-[a-z]", s) for s in segs):', "if False:"),
    ("any process with seat BENCH is the Conductor", "pager.py",
     'if any(re.match(r"^claude-seat-BENCH-\\d+\\.scope$", s) for s in segs):', "if True:"),
    ("the class's senders are not checked", "pager.py", "if who not in c[\"senders\"]:", "if False:"),
    ("the dedupe window never holds", "pager.py", "win > 0 and (t - last)", "win < 0 and (t - last)"),
    ("a failed send is recorded as paged", "pager.py", "        first = not isinstance(f, dict)\n",
     "        state[\"open\"][key] = {\"last_paged\": iso(t), \"repeats\": 0}\n        first = not isinstance(f, dict)\n"),
    ("a 200 without a receipt counts as sent", "pager.py",
     'if status == 200 and j.get("status") == 1 and j.get("receipt"):', 'if status == 200:'),
    ("a reading may carry a path", "pager.py", 'READING_RE = re.compile(r"^[A-Za-z0-9 _.,:;=<>%+()#-]{1,200}$")',
     'READING_RE = re.compile(r"^[A-Za-z0-9 _.,:;=<>%+()#/@-]{1,200}$")'),
    ("the user key leaks into the Conductor log", "pager.py", 'note = conductor_line("SENT %s (%s): %s receipt %s%s" % (key, who, body, receipt, (',
     'note = conductor_line("SENT %s (%s): %s receipt %s%s" % (key, who, body + creds["user"], receipt, ('),
    ("one Conductor line per failed attempt", "pager.py", "        if first:   # one line", "        if True:   # one line"),
    ("a torn state reads as empty", "pager.py",
     '        raise ValueError("%s is not a pager state (open, failing)" % p)', '        return {"open": {}, "failing": {}}'),
    ("priority 1, not emergency", "pager.py", "PRIORITY = 2", "PRIORITY = 1"),
    ("check-credentials sends a message", "pager.py", '(API + "/users/validate.json"', '(API + "/messages.json"'),
    ("any goal title is accepted", "pager.py", "        if goal not in titles:", "        if False:"),
    ("a dry run posts", "pager.py", "        if dry_run:\n            rec.update(outcome=DRY_RUN, title=title",
     "        if dry_run:\n            post('x', {})\n            rec.update(outcome=DRY_RUN, title=title"),
    ("missing credentials still post", "pager.py", "        if cred_bad:\n            ok, receipt, why_not = False, None, cred_bad",
     "        if cred_bad:\n            ok, receipt, why_not = pushover_verdict(*post(API, {}))"),
    ("a state write after a sent page raises", "pager.py",
     "            try:\n                write_state(state)\n            except OSError as e:   # the page left",
     "            if True:\n                write_state(state)\n            if False:   # the page left"),
    ("an unwritable pager dir stops the page", "pager.py",
     '        except OSError as e:\n            self.error = "unlocked: %s" % e', "        except OSError as e:\n            raise"),
    ("a crash prints no verdict", "pager.py", "        return _run(a)\n    except Exception as e:",
     "        return _run(a)\n    except ZeroDivisionError as e:"),
    ("a torn state reads 0 failing in the digest", "ops_watch_pager.py",
     '        out["pager.could_not_send"] = _U("%s unreadable: %s" % (sp, e), "faults whose page has not left")',
     '        out["pager.could_not_send"] = _M(0, "faults whose page has not left")'),
    ("the digest ignores the failing streak", "ops_watch_pager.py", "_M(len(fl),", "_M(0,"),
]


def stage(tmp):
    u = os.path.join(tmp, "src", "RimMandrake", "Utils")
    os.makedirs(u)
    for f in FILES:
        shutil.copy(os.path.join(HERE, f), os.path.join(u, f))
    g = os.path.join(tmp, "infrastructure", "state")
    os.makedirs(g)
    shutil.copy(os.path.join(TOP, "infrastructure", "state", "CONDUCTOR_GOALS.md"), g)
    return u


def run(u):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", os.path.join(u, "selftest_pager.py")], capture_output=True, text=True,
                       env=env, timeout=300)
    return r.returncode, r.stdout + r.stderr


def main():
    tmp = tempfile.mkdtemp(prefix="pager_plants_")
    try:
        u = stage(tmp)
        rc, out = run(u)
        if rc != 0 or "ALL PASS" not in out:
            print("BROKEN: the unmutated control is not ALL PASS:\n" + out[-800:])  # cut-ok: test diagnostic display
            return 3
        missed, caught = [], 0
        for name, f, anchor, repl in PLANTS:
            p = os.path.join(u, f)
            orig = open(os.path.join(HERE, f)).read()
            if orig.count(anchor) != 1:
                print("BROKEN: plant %r no longer applies (anchor found %d times in %s)" % (name, orig.count(anchor), f))
                return 3
            with open(p, "w") as fh:
                fh.write(orig.replace(anchor, repl))
            rc, out = run(u)
            with open(p, "w") as fh:
                fh.write(orig)
            if "FAIL:" in out or ("raised" in out and "FAIL" in out):
                caught += 1
                print("caught      %s" % name)
            else:
                missed.append(name)
                print("NOT CAUGHT  %s (rc %d: %s)" % (name, rc, out.strip().splitlines()[-1:] or ""))
        print(("CAUGHT %d of %d" % (caught, len(PLANTS))) if not missed else
              "NOT CAUGHT %d of %d: %s" % (len(missed), len(PLANTS), "; ".join(missed)))
        return 0 if not missed else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
