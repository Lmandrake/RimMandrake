#!/usr/bin/env python3
"""selftest_maturation_now.py: the seven acceptance points of RIMMANDRAKE_BUILD_MATURATION_PAGE_NO_TOKENS_SPENT.

    python3 src/RimMandrake/Utils/selftest_maturation_now.py

1 no model, no network: the page builds with every model variable unset and every socket connect refused
2 every mod with a version/VERSION.json is on the page, its version and Designer step equal to the files
3 the intake count equals owner_queue.py's first-touch count
4 a field the files do not hold prints UNMEASURED, never a guess or a zero
5 in a temp copy, a planted stage change and a planted new mod folder are absent before and shown after
6 two runs on an unchanged tree differ only in the measurement line
7 when stage.json and VERSION.json disagree about a mod, the page says so

Points 4, 5 and 7 run on a temp copy of design/concepts and the held-statement folder (--no-live: the ledger is not read).
Point 6 runs on the live tree twice; a ledger shard or run record that moved between the runs earns one retry.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROG = os.path.join(HERE, "maturation_now.py")
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + detail) if (detail and not ok) else ""))
    if not ok:
        FAILS.append(name)


def run(args, env=None, timeout=120):
    p = subprocess.run([sys.executable, PROG] + args, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def data_of(root, live=False):
    rc, out, err = run(["--root", root, "--json"] + ([] if live else ["--no-live"]))
    if rc != 0:
        raise RuntimeError("maturation_now.py --json exit %d: %s" % (rc, err[-600:]))
    return json.loads(out)


def page_of(root, live=False):
    rc, out, err = run(["--root", root, "--print"] + ([] if live else ["--no-live"]))
    if rc != 0:
        raise RuntimeError("maturation_now.py --print exit %d: %s" % (rc, err[-600:]))
    return out


def temp_tree():
    t = tempfile.mkdtemp(prefix="maturation_now_st_")
    shutil.copytree(os.path.join(REPO, "design", "concepts"), os.path.join(t, "design", "concepts"))
    shutil.copytree(os.path.join(REPO, "design", "RimMandrake", "validation_holding"),
                    os.path.join(t, "design", "RimMandrake", "validation_holding"))
    return t


def mod_of(d, name):
    return next((m for m in d["mods"] if m["name"] == name), None)


def p1_no_model_no_network():
    shim = tempfile.mkdtemp(prefix="maturation_now_net_")
    log = os.path.join(shim, "connects.log")
    with open(os.path.join(shim, "sitecustomize.py"), "w") as f:
        f.write("import socket\n"
                "def _refuse(self, *a, **k):\n"
                "    open(%r, 'a').write(repr(a) + '\\n')\n"
                "    raise OSError('network refused by selftest_maturation_now')\n"
                "socket.socket.connect = _refuse\n"
                "socket.socket.connect_ex = _refuse\n"
                "socket.create_connection = lambda *a, **k: _refuse(None, *a)\n" % log)
    env = {k: v for k, v in os.environ.items()
           if not re.match(r"(ANTHROPIC|CLAUDE|OPENAI|CODEX|GEMINI|AWS_BEDROCK)", k)}
    env["PYTHONPATH"] = shim + os.pathsep + env.get("PYTHONPATH", "")
    rc, out, err = run(["--print"], env=env)
    check("1 builds with model variables unset and sockets refused", rc == 0 and "# Maturation now" in out, err[-400:])
    check("1 no socket connect was attempted", not os.path.exists(log),
          open(log).read()[:300] if os.path.exists(log) else "")
    src = open(PROG, encoding="utf-8").read()
    bad = [w for w in ("import urllib", "import http", "import requests", "import socket", "import anthropic",
                       "claude -p", "\"claude\"", "'claude'") if w in src]
    check("1 the source imports no network client and calls no model", not bad, ", ".join(bad))
    shutil.rmtree(shim, ignore_errors=True)


def p2_every_versioned_mod(d, page):
    files = sorted(glob.glob(os.path.join(REPO, "design", "concepts", "*", "version", "VERSION.json")))
    check("2 the tree has VERSION files to test against", len(files) >= 1, "none found")
    for f in files:
        folder = os.path.basename(os.path.dirname(os.path.dirname(f)))
        if folder.startswith("_"):
            continue
        v = json.load(open(f))
        m = mod_of(d, folder)
        check("2 %s is on the page" % folder, m is not None and m["label"] in page)
        if m is None:
            continue
        check("2 %s version equals the file (%s)" % (folder, v.get("version")), m["version"] == v.get("version"),
              "page %r" % m["version"])
        sj = os.path.join(os.path.dirname(os.path.dirname(f)), "stage.json")
        want = json.load(open(sj)).get("stage") if os.path.exists(sj) else "UNMEASURED"
        check("2 %s Designer step equals stage.json (%s)" % (folder, want), m["designer_step"] == want,
              "page %r" % m["designer_step"])
        card = card_of(page, m["label"])
        check("2 %s card prints version and Designer step" % folder,
              str(v.get("version")) in card and ("step %s" % want if want != "UNMEASURED" else "UNMEASURED") in card)


def card_of(page, label):
    """The one line of the page that holds this mod's card."""
    for line in page.splitlines():
        if 'data-mod="%s"' % label in line:
            return line
    return ""


def p3_intake(d):
    p = subprocess.run([sys.executable, os.path.join(HERE, "owner_queue.py")], capture_output=True, text=True, timeout=120)
    m = re.search(r"^(\d+) first touches open", p.stdout, re.M)
    check("3 owner_queue.py printed its first-touch count", m is not None, p.stdout[-300:] + p.stderr[-300:])
    if m:
        check("3 the intake count equals owner_queue's (%s)" % m.group(1), d["intake"]["count"] == int(m.group(1)),
              "page %r" % d["intake"]["count"])


def p4_unmeasured():
    t = temp_tree()
    try:
        os.makedirs(os.path.join(t, "design", "concepts", "BareMod", "version"))
        json.dump({"mod": "BareMod", "version": "0.0.1"},
                  open(os.path.join(t, "design", "concepts", "BareMod", "version", "VERSION.json"), "w"))
        d = data_of(t)
        m = mod_of(d, "BareMod")
        check("4 a mod with a bare VERSION file is on the page", m is not None)
        if m is None:
            return
        for k in ("state", "designer_step", "bars_total", "bars_met", "judge_rounds", "tokens", "waits_on", "next",
                  "last_move", "held_statements"):
            check("4 BareMod %s prints UNMEASURED" % k, m.get(k) == "UNMEASURED", "got %r" % (m.get(k),))
        card = card_of(page_of(t), m["label"])
        check("4 BareMod card says UNMEASURED and shows no zero",
              card.count("UNMEASURED") >= 8 and not re.search(r">\s*0\s*<|\b0 bars|\b0 tokens|\b0 rounds", card),
              card[:300])
        d2 = data_of(t)       # --no-live: the ledger is not read, so its fields must not read as zero
        check("4 intake count unread prints UNMEASURED, not 0", d2["intake"]["count"] == "UNMEASURED",
              "got %r" % d2["intake"]["count"])
    finally:
        shutil.rmtree(t, ignore_errors=True)


def p5_planted_changes():
    t = temp_tree()
    try:
        before, pb = data_of(t), page_of(t)
        ek = mod_of(before, "ExplosiveKnockback")
        check("5 EK is on the temp page", ek is not None)
        check("5 red before: no PlantedMod on the page", mod_of(before, "PlantedMod") is None and "Planted Mod" not in pb)
        check("5 red before: EK is not at Stage 7", ek is not None and ek["column"] != "7")
        j = os.path.join(t, "design", "concepts", "ExplosiveKnockback", "journal.md")
        txt = open(j).read() if os.path.exists(j) else "# journal\n\n## The mod as it stands\n\n- **Stage now:** x\n"
        txt2 = re.sub(r"(\*\*Stage now:\*\*).*", r"\1 Stage 7, pre-human check (planted by the selftest).", txt, count=1)
        check("5 the planted stage line took", txt2 != txt)
        open(j, "w").write(txt2)
        os.makedirs(os.path.join(t, "design", "concepts", "PlantedMod", "version"))
        json.dump({"mod": "PlantedMod", "version": "0.3.0", "state": "locked"},
                  open(os.path.join(t, "design", "concepts", "PlantedMod", "version", "VERSION.json"), "w"))
        after, pa = data_of(t), page_of(t)
        ek2, pm = mod_of(after, "ExplosiveKnockback"), mod_of(after, "PlantedMod")
        check("5 green after: EK moved to Stage 7", ek2 is not None and ek2["column"] == "7",
              "column %r" % (ek2 or {}).get("column"))
        check("5 green after: EK's card says Stage 7", "Stage 7" in card_of(pa, "Explosive Knockback"))
        check("5 green after: PlantedMod is on the page at 0.3.0", pm is not None and pm["version"] == "0.3.0"
              and "Planted Mod" in pa and "0.3.0" in card_of(pa, "Planted Mod"))
    finally:
        shutil.rmtree(t, ignore_errors=True)


def p5_stage_words():
    sys.path.insert(0, HERE)
    import maturation_now as MN
    for text, want in (("Stage 1 being finished by hand (pilot row 2), 2026-11-14", ("1", False)),
                       ("Stage 1 finished by hand 2026-11-14 11:27 PST (pilot row 2); Stage 2 next", ("2", True)),
                       ("door of Stage 2; the pilot", ("2", True)),
                       ("Stage 2 (preflight) run by hand 2026-11-14 11:31 PST: refuse, 26 refusals", ("2", False)),
                       ("Stages 4 and 5, cycle 2", ("4+5", False)), ("Stage 5, tests first", ("4+5", False)),
                       ("waiting at intake", ("intake", False)), ("version passed 2026-12-01", ("passed", False)),
                       ("being argued", (None, False))):
        got = MN.stage_from_text(text)
        check("5 stage words %r -> %s" % (text[:40], want), got == want, "got %r" % (got,))


def p6_two_runs():
    def stamp():
        fs = glob.glob(os.path.join(REPO, "infrastructure", "state", "ledger", "events", "*.jsonl"))
        return sorted((f, os.path.getmtime(f)) for f in fs)
    for attempt in (1, 2):
        s0 = stamp()
        a, b = page_of(REPO, live=True), page_of(REPO, live=True)
        moved = stamp() != s0
        diff = [(x, y) for x, y in zip(a.splitlines(), b.splitlines()) if x != y]
        same_len = len(a.splitlines()) == len(b.splitlines())
        only_time = same_len and all(x.startswith("**Measured") and y.startswith("**Measured") for x, y in diff)
        if only_time or not moved or attempt == 2:
            check("6 two runs differ only in the measurement line", only_time,
                  "%d lines differ; first: %r" % (len(diff), diff[0] if diff else ("line count", same_len)))
            return


def p7_disagreement():
    t = temp_tree()
    try:
        c = os.path.join(t, "design", "concepts", "GimmeSomeSlack")
        sj, vj = os.path.join(c, "stage.json"), os.path.join(c, "version", "VERSION.json")
        s, v = json.load(open(sj)), json.load(open(vj))
        s["stage"], s["status"] = 5, "locked"
        v["state"] = "locked"
        json.dump(s, open(sj, "w")), json.dump(v, open(vj, "w"))
        m = mod_of(data_of(t), "GimmeSomeSlack")
        check("7 agreeing files: no disagreement on GSS", m is not None and not m["disagree"],
              "got %r" % (m or {}).get("disagree"))
        s["status"] = "blocked"
        json.dump(s, open(sj, "w"))
        d, page = data_of(t), page_of(t)
        m = mod_of(d, "GimmeSomeSlack")
        check("7 locked version, blocked stage.json: the page says they disagree",
              m is not None and m["disagree"] and "disagree" in card_of(page, "Gimme Some Slack").lower())
        s["status"], v["version"] = "locked", "0.2.0"
        json.dump(s, open(sj, "w")), json.dump(v, open(vj, "w"))
        tt = os.path.join(c, "version", "test_table.json")
        json.dump({"mod": "GimmeSomeSlack", "version": "0.1.0", "bars": []}, open(tt, "w"))
        m = mod_of(data_of(t), "GimmeSomeSlack")
        check("7 a version mismatch between VERSION.json and the test table is named",
              m is not None and any("0.2.0" in x and "0.1.0" in x for x in m["disagree"]), "got %r" % (m or {}).get("disagree"))
    finally:
        shutil.rmtree(t, ignore_errors=True)


def main():
    if not os.path.exists(PROG):
        check("maturation_now.py exists", False, PROG)
        print("FAILED: 1")
        return 1
    p1_no_model_no_network()
    d, page = data_of(REPO, live=True), page_of(REPO, live=True)
    p2_every_versioned_mod(d, page)
    p3_intake(d)
    p4_unmeasured()
    p5_planted_changes()
    p5_stage_words()
    p6_two_runs()
    p7_disagreement()
    print("FAILED: %d (%s)" % (len(FAILS), ", ".join(FAILS)) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
