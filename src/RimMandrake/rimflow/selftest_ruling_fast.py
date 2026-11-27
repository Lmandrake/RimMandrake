#!/usr/bin/env python3
"""Selftest of ruling_fast.py (the fast part of an owner ruling). Page: design/specs/2026-11-26-ruling-fast-path/boundary.md.
One test per promise, named as the promise. The doors (the ledger tools, the hold, the two publishes) are stand-ins that
record each call; the rules file is a temp copy. Nothing here writes the live ledger, store or repo.

    python3 selftest_ruling_fast.py          exit 0 all green, 1 a red
RULING_FAST_UNDER_TEST=<file> runs the promises against that copy of the module.
"""
import importlib.util
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))     # time_budget, for a copy of the module that lives elsewhere
sys.dont_write_bytecode = True
UNDER = os.environ.get("RULING_FAST_UNDER_TEST") or os.path.join(HERE, "ruling_fast.py")
FAILS = []


def load():
    spec = importlib.util.spec_from_file_location("ruling_fast", UNDER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


RULES = """# Standing rulings

## Owner hold

- **A hold** is a row in the file.
  - Its words stay.

## Mod Design Versions

Some prose.

### Pyrelands

- Pyrelands 0.1.0 passes first.

## Mod Design Versions, the judge layer

- A judge refuses flaws.
"""
WORDS = "We are not ready to do faction work yet. The tribes sleep until we start faction work much later."


class Doors:
    """Stand-ins for the parts the command composes. Each call is logged as (verb, args)."""

    def __init__(self, rules, items=("ITEM_A", "TICKET_B", "TICKET_C"), mods=("PyrelandsMechanics",), dirty=False,
                 fail=None):
        self.rules, self.items, self.mods, self.is_dirty, self.fail = rules, set(items), set(mods), dirty, fail
        self.log = []

    def _do(self, verb, *a):
        self.log.append((verb,) + a)
        if self.fail == verb:
            raise RuntimeError("%s failed (planted)" % verb)

    def item_exists(self, iid):
        return iid in self.items

    def mod_exists(self, mod):
        return mod in self.mods

    def dirty(self, path):
        return self.is_dirty

    def local_commits(self):
        return []

    def note(self, item, said, text, why):
        self._do("note", item, said)
        return {"ts": "2026-11-26T20:45:58Z", "tsn": "1795725958667522790", "id": item, "ownerSaid": said}

    def hold(self, mod, said, date):
        self._do("hold", mod, said, date)

    def park(self, iid, said, reason, why):
        self._do("park", iid, said)

    def file(self, name, title, caused_by, why):
        self._do("file", name, title, caused_by)

    def publish_ledger(self, msg):
        self._do("publish_ledger", open(self.rules).read())
        return "a" * 40, 1.0

    def publish_text(self, path, msg):
        self._do("publish_text", path, open(self.rules).read())
        return "b" * 40, 2.0


def setup(**kw):
    d = tempfile.mkdtemp(prefix="ruling_fast_")
    p = os.path.join(d, "standing_rulings.md")
    open(p, "w").write(RULES)
    return p, Doors(p, **kw)


def call(RF, doors, rules, argv):
    out = io.StringIO()
    rc = RF.run(RF.parse(argv), doors, rules_path=rules, out=out)
    return rc, out.getvalue()


def t_the_acts_run_in_order():
    RF = load()
    rules, d = setup()
    rc, out = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold", "--hold", "PyrelandsMechanics",
                                  "--park", "TICKET_B"])
    verbs = [e[0] for e in d.log]
    check(rc == 0 and verbs == ["note", "hold", "park", "publish_ledger", "publish_text", "file", "publish_ledger"],
          "the-acts-run-in-order: note, hold, park, ledger landing, text landing, follow-up, its landing (%s, rc %s)"
          % (verbs, rc))
    first_landing = [e for e in d.log if e[0] == "publish_ledger"][0]
    check(WORDS not in first_landing[1],
          "the-acts-run-in-order: the ledger acts land before the text is written")
    text = [e for e in d.log if e[0] == "publish_text"]
    check(bool(text) and text[0][1] == rules, "the-acts-run-in-order: the text lands by a publish of the rules file alone")
    f = [e for e in d.log if e[0] == "file"]
    check(bool(f) and f[0][3] == "ITEM_A", "the-acts-run-in-order: the follow-up is caused by the item")


def t_his_words_go_in_word_for_word_with_the_event_date():
    RF = load()
    rules, d = setup()
    rc, _out = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold"])
    new = open(rules).read()
    flat = " ".join(new.split())
    added = [ln for ln in new.splitlines() if ln not in RULES.splitlines()]
    check(rc == 0 and ('*"%s"*' % WORDS) in flat,
          "his-words-go-in-word-for-word-with-the-event-date: his words are in the file exactly (rc %s)" % rc)
    check("2026-11-26 12:45 PM PST" in flat and "1795725958667522790" in flat and "ITEM_A" in flat,
          "his-words-go-in-word-for-word-with-the-event-date: the bullet carries the event's Pacific time, tsn and item "
          "(%r)" % added)
    sec = new.split("## Owner hold", 1)[1].split("\n## ", 1)[0]
    check(WORDS.split()[0] in sec and new.index("Its words stay.") < new.index(WORDS.split(".")[0][:20]),
          "his-words-go-in-word-for-word-with-the-event-date: the bullet sits at the end of the named section")
    check(new.replace("\n".join(added) + "\n", "", 1) == RULES,
          "his-words-go-in-word-for-word-with-the-event-date: nothing else in the file changed")
    check(all(len(ln) <= 120 for ln in added), "his-words-go-in-word-for-word-with-the-event-date: lines wrap at 120")


def t_only_what_the_caller_names():
    RF = load()
    rules, d = setup()
    rc, _o = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold"])
    check(rc == 0 and not [e for e in d.log if e[0] in ("hold", "park")],
          "only-what-the-caller-names: with no --hold and no --park, nothing is held or parked (%s)" % d.log)
    rules, d = setup()
    rc, _o = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold", "--park", "TICKET_C"])
    check(rc == 0 and [e[1] for e in d.log if e[0] == "park"] == ["TICKET_C"]
          and [e[2] for e in d.log if e[0] == "park"] == [WORDS] and not [e for e in d.log if e[0] == "hold"],
          "only-what-the-caller-names: the one named ticket is parked with his words, and nothing else (%s)" % d.log)


def t_a_bad_call_does_nothing():
    RF = load()
    cases = [
        ("blank words", ["ITEM_A", "--said", "  ", "--section", "Owner hold"], {}),
        ("unknown item", ["NO_SUCH", "--said", WORDS, "--section", "Owner hold"], {}),
        ("unknown ticket", ["ITEM_A", "--said", WORDS, "--section", "Owner hold", "--park", "NO_SUCH"], {}),
        ("unknown mod", ["ITEM_A", "--said", WORDS, "--section", "Owner hold", "--hold", "NoSuchMod"], {}),
        ("no section", ["ITEM_A", "--said", WORDS, "--section", "Nothing like it"], {}),
        ("two sections", ["ITEM_A", "--said", WORDS, "--section", "Mod Design"], {}),
        ("dirty rules file", ["ITEM_A", "--said", WORDS, "--section", "Owner hold"], {"dirty": True}),
    ]
    for what, argv, kw in cases:
        rules, d = setup(**kw)
        rc, out = call(RF, d, rules, argv)
        check(rc != 0 and d.log == [] and open(rules).read() == RULES and "REFUSED" in out and "repair:" in out,
              "a-bad-call-does-nothing: %s is refused before any act, naming the repair (rc %s, acts %s, %r)"
              % (what, rc, d.log, out.strip()[-200:]))
    rules, d = setup()
    rc, out = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Mod Design Versions"])
    check(rc == 0, "a-bad-call-does-nothing: an exact heading wins over a longer one that starts with it (rc %s, %r)"
          % (rc, out.strip()[-200:]))


def t_the_follow_up_holds_the_slow_part():
    RF = load()
    rules, d = setup()
    rc, _o = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold", "--hold", "PyrelandsMechanics"])
    f = [e for e in d.log if e[0] == "file"]
    title = f[0][2] if f else ""
    check(rc == 0 and all(w in title for w in ("CLAUDE.md", "opposite", "tickets", "mod_owner_hold.json")),
          "the-follow-up-holds-the-slow-part: the follow-up names the rule line, the opposite lines, the unnamed tickets "
          "and the hold mirror (%r)" % title)
    rules, d = setup()
    call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold"])
    f = [e for e in d.log if e[0] == "file"]
    check(bool(f) and "mod_owner_hold.json" not in f[0][2],
          "the-follow-up-holds-the-slow-part: with no hold, it names no mirror")
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", f[0][1]], capture_output=True,
                       text=True, timeout=120)  # budget: class=rimflow
    check(r.returncode == 0, "the-follow-up-holds-the-slow-part: the follow-up's name passes namecheck (%s: %s)"
          % (f[0][1], (r.stdout + r.stderr).strip()[-200:]))


def t_at_most_five_lines():
    RF = load()
    rules, d = setup()
    rc, out = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold", "--hold", "PyrelandsMechanics",
                                  "--park", "TICKET_B", "--park", "TICKET_C"])
    lines = out.strip().splitlines()
    check(rc == 0 and 1 <= len(lines) <= 5 and "a" * 12 in out and "b" * 12 in out and "UNDO" in out
          and "FOLLOW-UP" in out,
          "at-most-five-lines: %d lines, with both shas, the follow-up and the undo (%r)" % (len(lines), out))
    rules, d = setup(fail="park")
    rc, out = call(RF, d, rules, ["ITEM_A", "--said", WORDS, "--section", "Owner hold", "--park", "TICKET_B"])
    check(rc != 0 and len(out.strip().splitlines()) <= 5 and "park" in out and "UNDO" in out
          and open(rules).read() == RULES,
          "at-most-five-lines: a failed act stops the rest, names its cause and the undo in at most 5 lines (%r)" % out)


def main():
    for t in (t_the_acts_run_in_order, t_his_words_go_in_word_for_word_with_the_event_date,
              t_only_what_the_caller_names, t_a_bad_call_does_nothing, t_the_follow_up_holds_the_slow_part,
              t_at_most_five_lines):
        try:
            t()
        except Exception as e:      # a crash of one test is a red of that promise, named
            check(False, "%s crashed: %r" % (t.__name__[2:].replace("_", "-"), e))
    print("%s: %d red" % ("RED" if FAILS else "GREEN", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
