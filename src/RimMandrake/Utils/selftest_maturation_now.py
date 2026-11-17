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
Round 2 (the owner, 2026-11-14 ~12:25 PM PST: yellow arrows where the Conductor intervened, cycling, what needs a reaction,
phone images):
8 every "CONDUCTOR INTERVENED" journal line is parsed and marked; a malformed one is listed under Needs Conductor
9 runs are placed on stages and counted: a stage run twice reads CYCLED x2 with a derived relaunch arrow
10 the reaction lists hold only real things (open question, answered one dropped, hold and release, long run, failed run)
11 what cannot be measured reads UNMEASURED (no run records, no tokens, no dollars, no stage.json), never 0 or blank
12 the phone images: an overview and one per mod, 1080 px wide, portrait
13 a folder with a stage record but no VERSION.json is on the map
14 a run's dollars are the measured cost_usd of its run record (RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER)
15 the slots line names the pipeline's launches apart from the Conductor's (RIMMANDRAKE_SHOW_SLOTS_CONDUCTOR_APART_FROM_MODS)

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
PROG = os.environ.get("MATURATION_NOW_UNDER_TEST") or os.path.join(HERE, "maturation_now.py")   # a mutant, to watch red
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


def page_of(root, live=False, env=None):
    rc, out, err = run(["--root", root, "--print"] + ([] if live else ["--no-live"]), env=env)
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
        txt2 = re.sub(r"(\*\*Stage now:\*\*).*", r"\1 Stage 7, the walk brief (planted by the selftest).", txt, count=1)
        check("5 the planted stage line took", txt2 != txt)
        open(j, "w").write(txt2)
        # RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY: the stage record is the stage; a journal line alone does not move it
        rp = os.path.join(t, "design", "concepts", "ExplosiveKnockback", "version", "stage_record.json")
        if os.path.exists(rp):
            mid = mod_of(data_of(t), "ExplosiveKnockback")
            check("5 a planted journal line alone does not move a mod with a stage record",
                  mid is not None and mid["column"] == ek["column"] and "stage record" in mid.get("stage_from", ""),
                  "column %r from %r" % ((mid or {}).get("column"), (mid or {}).get("stage_from")))
            rec = json.load(open(rp))
            rec["stage"] = "pre_human"
            json.dump(rec, open(rp, "w"))
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
    env = dict(os.environ, MATURATION_NOW_CLOCK=str(__import__("time").time()))   # "so far" minutes cannot tick
    for attempt in (1, 2):
        s0 = stamp()
        a, b = page_of(REPO, live=True, env=env), page_of(REPO, live=True, env=env)
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
        # RIMMANDRAKE_READ_LOCKED_CHANGE_AS_REEXAM_NOT_DISAGREEMENT: his card changed the locked version, the re-pin
        # voided stage 4's exam, the Designer retakes it. Both files are right (Pyrelands, 2026-11-15).
        s["stage"], s["status"] = 4, "ready"
        s.setdefault("history", []).append({"at": "2026-11-15T21:06:06Z", "what": "locked_change", "why": "his card"})
        json.dump(s, open(sj, "w"))
        m = mod_of(data_of(t), "GimmeSomeSlack")
        check("7 a locked change back in the Designer is not a disagreement", m is not None and not m["disagree"],
              "got %r" % (m or {}).get("disagree"))
        s["history"].append({"at": "2026-11-15T22:00:00Z", "what": "lock", "why": "the Designer locked it again"})
        json.dump(s, open(sj, "w"))
        m = mod_of(data_of(t), "GimmeSomeSlack")
        check("7 a Designer lock after the locked change, then not locked: they disagree again",
              m is not None and m["disagree"], "got %r" % (m or {}).get("disagree"))
        s["history"] = [h for h in s["history"] if h.get("what") not in ("locked_change", "lock")]
        s["status"], v["version"] = "locked", "0.2.0"
        json.dump(s, open(sj, "w")), json.dump(v, open(vj, "w"))
        tt = os.path.join(c, "version", "test_table.json")
        json.dump({"mod": "GimmeSomeSlack", "version": "0.1.0", "bars": []}, open(tt, "w"))
        m = mod_of(data_of(t), "GimmeSomeSlack")
        check("7 a version mismatch between VERSION.json and the test table is named",
              m is not None and any("0.2.0" in x and "0.1.0" in x for x in m["disagree"]), "got %r" % (m or {}).get("disagree"))
    finally:
        shutil.rmtree(t, ignore_errors=True)


def MN():
    import importlib.util
    spec = importlib.util.spec_from_file_location("maturation_now_under_test", PROG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GOOD_IV = "- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind hold): Stage 3 held for a planted reason. Source: test."
BAD_IV = "- CONDUCTOR INTERVENED stage three: no parenthesis, no colon form"


def p8_interventions(d, page):
    M = MN()
    g, b = M.parse_interventions(GOOD_IV + "\n" + BAD_IV + "\nplain line\n", "journal")
    check("8 a well-formed line parses: stage 3, kind hold, 12:15 PM PST",
          len(g) == 1 and g[0]["stage"] == "3" and g[0]["kind"] == "hold" and g[0]["when"].startswith("12:15 PM"),
          "got %r" % g)
    check("8 a malformed line is kept as unparsed, not dropped", len(b) == 1 and "stage three" in b[0]["line"], "got %r" % b)
    g2, _ = M.parse_interventions("- CONDUCTOR INTERVENED (stage 5, kind re-pin): x", "j")
    check("8 stage 5 is the 4+5 box; a line without a time reads UNMEASURED",
          g2 and g2[0]["stage"] == "4+5" and g2[0]["when"] == "UNMEASURED", "got %r" % g2)
    g3, b3 = M.parse_interventions("- CONDUCTOR INTERVENED (stage 3, 2026-11-14 13:50 PST, kind bar-added): x", "j")
    check("8 kind bar-added (spec 5 item 5) parses and is not left unparsed",
          g3 and g3[0]["kind"] == "bar-added" and not b3, "got %r / %r" % (g3, b3))
    # the live tree: every journal line is on the page (count measured by grep here, not by the generator)
    want = {}
    for f in glob.glob(os.path.join(REPO, "design", "concepts", "*", "journal.md")):
        n = sum(1 for ln in open(f, encoding="utf-8") if "CONDUCTOR INTERVENED" in ln)
        if n:
            want[os.path.basename(os.path.dirname(f))] = n
    check("8 the live journals hold intervention lines to test against", sum(want.values()) >= 1, "none")
    for folder, n in sorted(want.items()):
        m = mod_of(d, folder)
        got = len([i for i in (m or {}).get("ivs", []) if i.get("source") == "journal"]) + len((m or {}).get("iv_bad", []))
        check("8 %s: %d journal intervention lines, %d on the page" % (folder, n, got), got == n)
        card = card_of(page, (m or {}).get("label", "?"))
        check("8 %s card shows a yellow arrow line per intervention" % folder,
              card.count("<b>➤</b>") >= n, "arrows %d" % card.count("<b>➤</b>"))
    check("8 the picture draws yellow arrows", page.count('fill="%s" stroke' % M.YELLOW) >= len(want))
    t = temp_tree()
    try:
        j = os.path.join(t, "design", "concepts", "FlowWorks", "journal.md")
        open(j, "a").write("\n" + BAD_IV + "\n")
        d2 = data_of(t)
        check("8 a malformed journal line is listed under Needs Conductor",
              any("cannot read" in x and "stage three" in x for x in d2["needs"]["conductor"]), "%r" % d2["needs"]["conductor"][-3:])
    finally:
        shutil.rmtree(t, ignore_errors=True)


def fake_recs(now, item="RIMMANDRAKE_ADVANCE_FOOMOD_OFFLINE"):
    return [{"unit": "u1", "item": item, "model": "opus", "at": now - 7200, "ended": now - 6000, "status": "finished",
             "result": "success (exited 0)", "tokens": 1000, "budget_usd": 15, "out": "/nonexistent"},
            {"unit": "u2", "item": item, "model": "opus", "at": now - 5000, "ended": now - 4000, "status": "finished",
             "result": "timeout (killed KILL)", "tokens": None, "budget_usd": 15, "out": "/nonexistent"},
            {"unit": "u3", "item": item, "model": "opus", "at": now - 3700, "status": "running", "live_state": "running",
             "budget_usd": 15, "out": "/nonexistent"}]


def fake_journal(now):
    import datetime as dt
    from zoneinfo import ZoneInfo

    def h(ts, what):
        return "### %s, %s" % (dt.datetime.fromtimestamp(ts, ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %I:%M %p PST"), what)
    return "\n".join([h(now - 7100, "row 2 done: Stage 1 finished"), h(now - 4900, "Stage 1 again, a second pass"),
                      h(now - 3600, "Stage 3 begins")])


def p9_cycles():
    M = MN()
    now = 1_800_000_000.0
    j = M.parse_journal(fake_journal(now))
    runs = M.runs_for_mods(["FooMod", "BarMod"], fake_recs(now), [], {"FooMod": j}, now, spend=lambda r: ("UNMEASURED", None, "UNMEASURED"))
    r = runs["FooMod"]
    check("9 three runs of a FOOMOD item are FooMod's, none BarMod's", len(r) == 3 and not runs["BarMod"], "%r" % runs)
    check("9 runs placed by the journal headings in their time", [x["stages"] for x in r] == [["1"], ["1"], ["3"]],
          "%r" % [x["stages"] for x in r])
    m = {"column": "3", "label": "Foo Mod", "runs": r, "disagree": [], "his": [], "jquestions": []}
    box = M.stage_boxes(m, r, [], "3")
    check("9 Stage 1 ran twice: cycled 2 with one derived relaunch", box["1"]["cycled"] == 2 and
          sum(1 for i in box["1"]["ivs"] if i.get("derived")) == 1, "%r" % box.get("1"))
    m["boxes"] = box
    lines = [t for _, t in M.box_lines(m, "1", box["1"])]
    check("9 the box says CYCLED with the count", any("CYCLED: this stage has run 2 times" in x for x in lines), "%r" % lines)
    check("9 the live run is in Stage 3's box", box["3"]["cycled"] == 1 and box["3"]["runs"][0]["live"])
    check("9 item names: GSS initials, KNOCKBACK word, a tie names none",
          M.item_mod("RIMMANDRAKE_PROVE_GSS_SWITCHBOARD", ["GimmeSomeSlack", "FlowWorks"]) == "GimmeSomeSlack"
          and M.item_mod("RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH", ["ExplosiveKnockback"]) == "ExplosiveKnockback"
          and M.item_mod("PYRELANDS_FINISH", ["Pyrelands", "PyrelandsMechanics"]) == "Pyrelands"
          and M.item_mod("RIMMANDRAKE_SOMETHING_ELSE", ["Pyrelands"]) is None)
    notes = [{"id": "RIMMANDRAKE_DESIGN_PIPELINE", "text": "see design/concepts/FooMod/journal.md and design/concepts/FooMod/x"}]
    check("9 an item naming no mod is the one its notes cite", M.item_mod("RIMMANDRAKE_DESIGN_PIPELINE", ["FooMod", "BarMod"], notes) == "FooMod")
    # RIMMANDRAKE_SEE_RESCUE_RUN_ON_ITS_MOD: SLACK is too short a word and the notes cite FlowWorks more; the title says
    notes2 = [{"id": "RIMMANDRAKE_LAY_SLACK_X", "text": "design/concepts/FlowWorks/a design/concepts/FlowWorks/b "
               "design/concepts/GimmeSomeSlack/c"}]
    check("9 an item its id does not name is the mod its title names, before its notes",
          M.item_mod("RIMMANDRAKE_LAY_SLACK_X", ["GimmeSomeSlack", "FlowWorks"], notes2) == "FlowWorks"
          and M.item_mod("RIMMANDRAKE_LAY_SLACK_X", ["GimmeSomeSlack", "FlowWorks"], notes2,
                         {"RIMMANDRAKE_LAY_SLACK_X": "Gimme Some Slack: the 21 close-fitting poses"}) == "GimmeSomeSlack"
          and M.item_mod("RIMMANDRAKE_LAY_SLACK_X", ["GimmeSomeSlack", "FlowWorks"], notes2,
                         {"RIMMANDRAKE_LAY_SLACK_X": "lay the poses"}) == "FlowWorks")
    check("9 'stopped before Stage 3' names no Stage 3", M.stages_named("Rows 1-3 done, stopped before Stage 3.") == [])


def p10_reactions():
    M = MN()
    now = 1_800_000_000.0
    j = M.parse_journal(fake_journal(now))
    r = M.runs_for_mods(["FooMod"], fake_recs(now), [], {"FooMod": j}, now, spend=lambda r: ("UNMEASURED", None, "UNMEASURED"))["FooMod"]
    jtext = ("### Questions (open)\n\n1. **Which colour?** asked.\n2. **The g4 weight** (for the Conductor).\n"
             "3. **Already settled.** x\n\n## History\n- the steward answers question 3 here.\n")
    ivs, _ = M.parse_interventions(GOOD_IV, "journal")
    m = {"column": "3", "label": "Foo Mod", "runs": r, "disagree": [], "his": [], "jquestions": M.journal_questions(jtext)}
    m["boxes"] = M.stage_boxes(m, r, ivs, "3")
    n = M.reactions([m], now)
    me, co = " | ".join(n["mandrake"]), " | ".join(n["conductor"])
    check("10 an open question for him is under Needs Mandrake", "Which colour?" in me, me)
    check("10 a question 'for the Conductor' is under Needs Conductor", "The g4 weight" in co and "g4" not in me, co)
    check("10 an answered question is in neither list", "Already settled" not in me + co)
    check("10 a hold is listed with what holds it", "HELD" in co and "planted reason" in co, co)
    check("10 a run live over an hour is listed", "has been live" in co, co)
    check("10 a run that ended non-success is listed", "killed at its time limit" in co, co)
    check("10 a successful run is not listed", "finished OK" not in co, co)
    rel = ivs + M.parse_interventions("- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:30 PST, kind release): go.", "j")[0]
    m["boxes"] = M.stage_boxes(m, r, rel, "3")
    check("10 a hold followed by a release is no longer held", m["boxes"]["3"]["held"] is None)
    r3 = M.runs_for_mods(["FooMod"], fake_recs(now)[:2] * 2, [], {"FooMod": j}, now,
                         spend=lambda r: ("UNMEASURED", None, "UNMEASURED"))["FooMod"]
    for x in r3:
        x["stages"] = ["3"]
    m["boxes"] = M.stage_boxes(m, r3, [], "3")
    check("10 a current stage run 3+ times is listed", any("has run 4 times" in x for x in M.reactions([m], now)["conductor"]))


def p11_unmeasured(d_nolive_page):
    d_nolive_page = re.sub(r"<[^>]+>", "", d_nolive_page)
    M = MN()
    now = 1_800_000_000.0
    r = M.run_view({"unit": "u", "item": "X", "at": now - 100, "ended": now, "status": "finished",
                    "result": "success (exited 0)", "out": "/nonexistent"}, now)
    line = M.run_line(r, 1)
    check("11 a run with no tokens reads weighted tokens UNMEASURED, never 0", "weighted tokens UNMEASURED" in line
          and " 0 " not in line, line)
    # the owner, 2026-11-16: "Please speak in terms of weighted tokens not money." A run's line says weighted tokens
    # and no dollar figure, measured, said or capped (RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_NO_LIVE_HOLD)
    r3 = dict(M.run_view({"unit": "u", "item": "X", "at": now - 100, "ended": now, "status": "finished",
                          "result": "success (exited 0)", "out": "/nonexistent", "tokens": 2_400_000,
                          "budget_usd": 15}, now), usd=4.25, said_usd=2.0, cap=15)
    l3 = M.run_line(r3, 1)
    check("11 a run line says weighted tokens, never dollars", "2.4 M weighted tokens" in l3
          and not re.search(r"USD|\$\s*\d|dollar", l3), l3)
    page = d_nolive_page
    check("11 the page states no dollar figure", not re.search(r"USD ?\d|\$\s*\d", page),
          [x for x in page.splitlines() if re.search(r"USD ?\d|\$\s*\d", x)][:2])
    r2 = M.run_view({"unit": "u", "item": "X", "status": "finished"}, now)
    check("11 a run with no times reads UNMEASURED wall time and outcome", r2["wall"] == "UNMEASURED" and r2["outcome"] == "UNMEASURED", "%r" % r2)
    check("11 no stage.json: Designer cycles UNMEASURED", M.designer_cycles(None) == "UNMEASURED")
    check("11 --no-live: stage boxes say runs UNMEASURED, never 0",
          "Runs at this stage: UNMEASURED" in d_nolive_page and "Runs at this stage: 0" not in d_nolive_page)
    check("11 --no-live: the cycle chip reads UNMEASURED", "cycles UNMEASURED" in d_nolive_page)


def p12_phone():
    import tempfile
    out = tempfile.mkdtemp(prefix="maturation_now_phone_")
    try:
        rc, o, e = run(["--no-live", "--out", out])
        ph = os.path.join(out, "MATURATION_NOW_phone")
        files = sorted(os.listdir(ph)) if os.path.isdir(ph) else []
        mods = [os.path.basename(os.path.dirname(os.path.dirname(f))) for f in
                glob.glob(os.path.join(REPO, "design", "concepts", "*", "version", "VERSION.json"))
                if not os.path.basename(os.path.dirname(os.path.dirname(f))).startswith("_")]
        check("12 the program wrote an overview and one image per mod", rc == 0 and "00_overview.png" in files and
              all("%s.png" % m in files for m in mods), "rc %d files %r %s" % (rc, files, e[-300:]))
        from PIL import Image
        for f in files:
            w, h = Image.open(os.path.join(ph, f)).size
            check("12 %s is 1080 wide and portrait" % f, w == 1080 and h > w, "%dx%d" % (w, h))
    finally:
        shutil.rmtree(out, ignore_errors=True)


def p13_versionless():
    """RIMMANDRAKE_SHOW_VERSIONLESS_MOD_GRAFFITI_ON_MAP: a folder with a stage record but no VERSION.json is on the map."""
    t = temp_tree()
    try:
        cr = os.path.join(t, "design", "concepts")
        def plant(name, stage=None, locked=False):
            os.makedirs(os.path.join(cr, name))
            if stage is not None:
                json.dump({"stage": stage, "status": "locked" if locked else "waiting_owner", "history": []},
                          open(os.path.join(cr, name, "stage.json"), "w"))
        plant("VlLocked", 5, True)
        plant("VlOpen", 1, False)
        plant("VlBare")
        d, page = data_of(t), page_of(t)
        base = len(d["mods"])
        for nm, label in (("VlLocked", "Vl Locked"), ("VlOpen", "Vl Open")):
            m = mod_of(d, nm)
            check("13 %s is on the map data" % nm, m is not None)
            check("13 %s stands at the Designer column on the map" % nm, m is not None and m["column"] == "1", repr((m or {}).get("column")))
            card = card_of(page, label)
            check("13 %s has a card saying no Design Version named yet" % nm, "no Design Version named yet" in card, card[:120])
            check("13 %s invents no version number" % nm, m is not None and m["version"] == "UNMEASURED")
            check("13 %s has a table row" % nm, re.search(r"^\|\s*%s\s*\|[^\n]*no Design Version named yet" % label, page, re.M) is not None)
        check("13 the locked one says the lock is the owner's", "owner" in card_of(page, "Vl Locked").lower())
        check("13 the unlocked one does not claim a lock", "lock is the owner" not in card_of(page, "Vl Open").lower())
        check("13 versionless count in the chip", "%d mods in the pipeline" % len([x for x in d["mods"] if not x["held"]]) in page)
        check("13 no stage record: not a mod, stays in the list", mod_of(d, "VlBare") is None and
              "VlBare" in page and "not placed on the map" in page)
        # a normal versioned mod is unchanged
        ek = mod_of(d, "ExplosiveKnockback")
        check("13 a versioned mod keeps its version and has no versionless words",
              ek is not None and ek["version"] != "UNMEASURED" and "no Design Version named yet" not in card_of(page, "Explosive Knockback"))
    finally:
        shutil.rmtree(t, ignore_errors=True)


def p14_measured_dollars():
    """RIMMANDRAKE_KEEP_RUN_RESULT_WHOLE_FINISH_WRITES_OVER: the run record's measured cost_usd is the run's dollars;
    the record's UNMEASURED stays unmeasured, never 0 and never the cap."""
    M = MN()
    t = tempfile.mkdtemp(prefix="mn_spend_")
    try:
        out = os.path.join(t, "u.out.json")
        with open(out, "w") as f:
            f.write('FINISHED u\n"modelUsage":{}, "result": "I spent about $2 on this"}')
        usd, said, over = M.read_spend({"out": out, "cost_usd": 4.25, "budget_usd": 3})
        check("14 a measured cost_usd in the run record is the run's dollars", usd == 4.25, repr(usd))
        check("14 the run's own word is still read from its result file", said == 2.0, repr(said))
        check("14 measured dollars over the cap read over", over is True, repr(over))
        usd, _, over = M.read_spend({"out": out, "cost_usd": 1.5, "budget_usd": 3})
        check("14 measured dollars under the cap read not over (the run's word does not decide)",
              usd == 1.5 and over is False, repr((usd, over)))
        usd, _, _ = M.read_spend({"out": out, "cost_usd": "UNMEASURED", "budget_usd": 3})
        check("14 a record that says UNMEASURED reads UNMEASURED", usd == M.UNM, repr(usd))
        with open(out, "w") as f:
            f.write('{"type": "result", "total_cost_usd": 0.75}')
        usd, _, _ = M.read_spend({"out": out, "budget_usd": 3})
        check("14 a record without cost_usd still reads a whole result file", usd == 0.75, repr(usd))
    finally:
        shutil.rmtree(t, ignore_errors=True)


def p15_slots():
    """RIMMANDRAKE_SHOW_SLOTS_CONDUCTOR_APART_FROM_MODS: the pipeline lines open with who holds the launch slots, the
    pipeline's launches (ticks.jsonl "launched") apart from the Conductor's; an unreadable source reads UNMEASURED."""
    M = MN()
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import maturation_dispatch as MD  # noqa: E402
    mx = MD.load_cfg().get("max_live", 2)
    t = tempfile.mkdtemp(prefix="mn_slots_")
    old = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = t
    now = __import__("time").time()

    def plant(mods, ticks):
        json.dump({"at": now, "at_pac": "now", "mods": mods}, open(os.path.join(t, "reading.json"), "w"))
        tp = os.path.join(t, "ticks.jsonl")
        if ticks is None:
            if os.path.exists(tp):
                os.remove(tp)
        else:
            with open(tp, "w") as f:
                f.write("".join(json.dumps({"at": now, "launched": [{"mod": m, "unit": u, "item": "X"} for m, u in tk]})
                                + "\n" for tk in ticks))
        errs = []
        got = M.dispatch_pipeline(now, errs)
        return (got[0] if got else ""), got, errs
    try:
        mods = {"Alpha": {"live": ["rm-a1", "rm-a2"], "status": "moving", "for_min": 3},
                "Beta": {"live": ["rm-conductor-b"]}, "Gamma": {"live": []}}
        line, got, errs = plant(mods, [[("Alpha", "rm-a1")], [], [("Alpha", "rm-a2"), ("Gamma", "rm-gone")]])
        check("15 the first pipeline line is the slots line", line.startswith("Slots: 3 live of max_live %s" % mx), line)
        check("15 it counts the pipeline's launches", "2 launched by the pipeline (Alpha 2)" in line, line)
        check("15 it names the Conductor's launch by mod and unit", "1 by the Conductor (Beta: rm-conductor-b)" in line, line)
        check("15 the per-mod lines still follow", any(x.startswith("Alpha: moving") for x in got[1:]), repr(got))
        line, _, _ = plant(mods, None)
        check("15 no ticks file: who launched them reads UNMEASURED, never 0",
              "UNMEASURED" in line and "0 launched" not in line and "3 live" in line, line)
        line, _, _ = plant(mods, [])
        check("15 an empty ticks file reads UNMEASURED too", "UNMEASURED" in line and "0 launched" not in line, line)
        line, _, _ = plant(dict(mods, Delta={"live": "UNMEASURED"}), [[("Alpha", "rm-a1")]])
        check("15 a mod whose live runs cannot be read makes the live count UNMEASURED",
              line.startswith("Slots: UNMEASURED") and "Delta" in line, line)
        line, _, _ = plant({"Alpha": {"live": []}}, [[("Alpha", "rm-a1")]])
        check("15 no live run: 0 live is a measured 0", line.startswith("Slots: 0 live of max_live"), line)
    finally:
        if old is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = old
        shutil.rmtree(t, ignore_errors=True)


def p16_clone_line():
    """RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE: the page's "Pipeline now" list leads with the
    dispatch clone's distance from origin/main, from the tick's reading (behind, and level)."""
    import importlib.util
    import time
    t = tempfile.mkdtemp(prefix="matnow_clone_")
    old = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    try:
        os.environ["RM_MATURATION_DISPATCH_DIR"] = t
        spec = importlib.util.spec_from_file_location("matnow_under_test", PROG)
        mn = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mn)
        now = time.time()
        rd = {"at": now - 30, "at_pac": "now", "mods": {"Foo": {"status": "moving", "for_min": 2}},
              "clone": {"measured": True, "behind": 7, "ahead": 2, "behind_min": 39.0, "level_pac": "11:41 AM"}}
        with open(os.path.join(t, "reading.json"), "w") as f:
            json.dump(rd, f)
        lines = mn.dispatch_pipeline(now, [])
        check("16 the page names a dispatch clone behind origin, how far and for how long",
              bool(lines) and lines[0].startswith("clone: BEHIND origin/main by 7 (ahead 2) for 39.0 min"), repr(lines[:2]))
        rd["clone"] = {"measured": True, "behind": 0, "ahead": 0, "behind_min": 0.0}
        with open(os.path.join(t, "reading.json"), "w") as f:
            json.dump(rd, f)
        lines = mn.dispatch_pipeline(now, [])
        check("16 a level clone reads level, and the mod lines follow it",
              lines[:1] == ["clone: level with origin/main"] and any(x.startswith("Foo: moving") for x in lines),
              repr(lines[:2]))
    finally:
        if old is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = old
        shutil.rmtree(t, ignore_errors=True)


def p17_owed_close():
    """RIMMANDRAKE_FLAG_DETACHED_SUCCESS_LEAVING_ITEM_OPEN: a detached run finish flagged (it ended success with its item
    still open, no LEFT OPEN: note) is a Needs Conductor line on the page while its item stays open."""
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import detached_helper as DH
    mn = MN()
    never = "RIMMANDRAKE_NEVER_FILED_SELFTEST_FIXTURE_ITEM_OWED_CLOSE"     # never on the ledger: reads "absent"
    rec = {"unit": "rm-detached-fixture-owed", "item": never, "status": "finished", "result": "success (exited 0)",
           "at": 1794775111.0, "owed_close": "flagged"}
    was = DH.all_records
    try:
        DH.all_records = lambda root=None: [rec, dict(rec, unit="rm-detached-fixture-clean", owed_close="")]
        lf = mn.live_facts([])
    finally:
        DH.all_records = was
    owed = lf.get("owed") or []
    check("17 the page's live read lists a run that ended success with its item open",
          len(owed) == 1 and ("item %s is still absent from the ledger" % never) in owed[0], repr(owed)[:300])
    t = tempfile.mkdtemp(prefix="matnow_owed_")
    try:
        os.makedirs(os.path.join(t, "design", "concepts"))
        mn.live_facts = lambda mods: {"intake": 0, "intake_why": "", "questions": [], "records": [], "notes": [],
                                      "errors": [], "owed": ["run U ended success; item X is still proposed: close it"]}
        d = mn.gather(t, live=True)
        check("17 a flagged run is a Needs Conductor line",
              any("item X is still proposed" in x for x in d["needs"]["conductor"]), repr(d["needs"]["conductor"])[:300])
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
    p8_interventions(d, page)
    p9_cycles()
    p10_reactions()
    p11_unmeasured(page_of(REPO))
    p12_phone()
    p13_versionless()
    p14_measured_dollars()
    p15_slots()
    p16_clone_line()
    p17_owed_close()
    print("FAILED: %d (%s)" % (len(FAILS), ", ".join(FAILS)) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
