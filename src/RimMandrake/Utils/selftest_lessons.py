#!/usr/bin/env python3
"""Selftest for lessons.py: --home warning/line, duplicate hint, stats. Uses a temp LESSONS_ROOT."""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LESSONS = os.path.join(HERE, "lessons.py")
fails = []


def check(name, cond, detail=""):
    if not cond:
        fails.append(name)
        print("FAIL: %s %s" % (name, detail))


def run(root, *args, **env_over):
    env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_ITEM", "WC_ITEM")}   # hermetic: no session item
    env.update(env_over, LESSONS_ROOT=root)
    return subprocess.run([sys.executable, LESSONS] + list(args), env=env, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as root:
    d = os.path.join(root, "infrastructure", "state", "lessons")
    os.makedirs(d)
    now = time.time()

    def stamp(days):
        return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now - days * 86400))

    fixtures = [(2, "BENCH", "a", "alpha beta gamma\nhome: skill-x\n"),
                (10, "FOUNDRY", "b", "delta epsilon\n"),
                (20, "BENCH", "c", "zeta eta\nhome: skill-x\n"),
                (40, "BENCH", "d", "theta iota\nhome: NONE\n")]
    for days, seat, slug, body in fixtures:
        with open(os.path.join(d, "%s-%s-%s.md" % (stamp(days), seat, slug)), "w") as f:
            f.write(body)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# header\n")

    r = run(root, "stats")
    out = r.stdout
    check("stats rc", r.returncode == 0, r.stderr)
    check("stats total", "total: 4" in out, out)
    check("stats seat", "BENCH=3" in out and "FOUNDRY=1" in out, out)
    check("stats age", "<7d=1" in out and "7-14d=1" in out and "14-30d=1" in out and ">30d=1" in out, out)
    check("stats home", "with home: 3, without home: 1" in out and "skill-x=2" in out, out)
    check("stats oldest", "oldest undrained: 40 days" in out, out)

    r = run(root, "add", "kappa lambda mu nu xi omicron", "--seat", "bench")
    check("add no-home warns", "no --home given" in r.stderr and r.returncode == 0, r.stderr)
    r = run(root, "add", "pi rho sigma tau", "--seat", "bench", "--home", "skills/foo")
    check("add home no warn", "no --home" not in r.stderr and r.returncode == 0, r.stderr)
    newest = [n for n in sorted(os.listdir(d)) if "pi-rho" in n]
    check("home line written", newest and open(os.path.join(d, newest[0])).read().splitlines()[-1] == "home: skills/foo")

    check("no session item, no item line", newest and "item:" not in open(os.path.join(d, newest[0])).read())

    # item: the session's item from the environment, an explicit --item over it, NONE for none (design 4.3 kinds)
    def body_of(word):
        return open(os.path.join(d, [n for n in sorted(os.listdir(d)) if word in n][0])).read()
    run(root, "add", "upsilon one", "--home", "foo", RIMFLOW_ITEM="WIDGET_REPAIR_SHAPE")
    check("item line from RIMFLOW_ITEM, before home", body_of("upsilon").splitlines()[-2:]
          == ["item: WIDGET_REPAIR_SHAPE", "home: foo"], body_of("upsilon"))
    run(root, "add", "phi two", "--home", "foo", WC_ITEM="WIDGET_REPAIR_SHAPE")
    check("the retired Whittle loop's WC_ITEM is not read", "item:" not in body_of("phi-two"), body_of("phi-two"))
    run(root, "add", "chi three", "--home", "foo", "--item", "SPROCKET_AUDIT_TEETH", RIMFLOW_ITEM="WIDGET_REPAIR_SHAPE")
    check("--item over the environment", "item: SPROCKET_AUDIT_TEETH\n" in body_of("chi-three"), body_of("chi-three"))
    run(root, "add", "psi four", "--home", "foo", "--item", "NONE", RIMFLOW_ITEM="WIDGET_REPAIR_SHAPE")
    check("--item NONE says so, over the environment", "item: NONE\n" in body_of("psi-four")
          and "WIDGET" not in body_of("psi-four"), body_of("psi-four"))
    run(root, "add", "tau seven quoted\nitem: WIDGET_REPAIR_SHAPE\nfrom another task", "--item", "GADGET_BUILD_FRAME",
        "--home", "foo")
    run(root, "add", "tau eight quoted at the end\nitem: WIDGET_REPAIR_SHAPE", "--item", "GADGET_BUILD_FRAME", "--distinct", "fixture")
    run(root, "add", "omega five", "--home", "foo", RIMFLOW_ITEM="not an id; rm -rf")
    check("a malformed session item is ignored", "item:" not in body_of("omega-five"), body_of("omega-five"))
    for bad in ("lower_case", "GADGET_BUILD"):   # two words is not an item id (three are needed)
        r = run(root, "add", "omega six " + bad, "--item", bad)
        check("a malformed --item refused: " + bad, r.returncode != 0 and "not an item id" in (r.stderr + r.stdout), r.stderr)
    sys.path.insert(0, HERE)
    import lessons as L  # noqa: E402
    check("item_of reads the line", L.item_of(os.path.join(d, [n for n in sorted(os.listdir(d)) if "upsilon" in n][0]))
          == "WIDGET_REPAIR_SHAPE")
    p_of = lambda w: os.path.join(d, [n for n in sorted(os.listdir(d)) if w in n][0])
    check("item_of reads only the footer, not an item: line in the text",
          (L.item_of(p_of("tau-seven")), L.item_of(p_of("tau-eight"))) == ("GADGET_BUILD_FRAME", "GADGET_BUILD_FRAME"),
          (L.item_of(p_of("tau-seven")), L.item_of(p_of("tau-eight"))))
    check("item_of: NONE said, nothing recorded", (L.item_of(p_of("psi-four")), L.item_of(p_of("omega-five")))
          == ("NONE", None))
    check("home_of still reads home after an item line",
          L.home_of(os.path.join(d, [n for n in sorted(os.listdir(d)) if "upsilon" in n][0])) == "foo")

    r = run(root, "add", "alpha beta gamma delta", "--home", "NONE")
    check("near-twin refused, names the twin and both ways through",
          r.returncode == 2 and "alpha beta gamma" in r.stdout + r.stderr and "--merge" in r.stdout + r.stderr
          and "--distinct" in r.stdout + r.stderr, r.stdout + r.stderr)
    check("near-twin refusal writes nothing", not [n for n in os.listdir(d) if "delta" in n and "alpha" in n])
    r = run(root, "add", "alpha beta gamma", "--home", "NONE")
    check("exact duplicate refused", r.returncode == 2, r.stdout + r.stderr)
    r = run(root, "add", "alpha beta gamma delta", "--home", "NONE", "--distinct", "covers the delta case only")
    check("--distinct writes the lesson", r.returncode == 0 and "possible duplicates" not in r.stdout, r.stdout + r.stderr)
    dn = [n for n in sorted(os.listdir(d)) if "alpha-beta-gamma-delta" in n]
    check("--distinct records the reason before the footer", dn and open(os.path.join(d, dn[0])).read().splitlines()
          == ["alpha beta gamma delta", "distinct: covers the delta case only", "home: NONE"], dn)
    r = run(root, "add", "alpha beta gamma delta again", "--distinct", "  ")
    check("--distinct with a blank reason refused", r.returncode != 0, r.stdout + r.stderr)
    r = run(root, "add", "alpha beta gamma epsilon\nsecond line", "--home", "NONE", "--merge", "nonexistent.md")
    check("--merge into a file that is not a lesson refused", r.returncode != 0 and "nonexistent" in r.stdout + r.stderr, r.stdout + r.stderr)
    r = run(root, "add", "x", "--merge", "README.md")
    check("--merge into README refused", r.returncode != 0, r.stdout + r.stderr)
    r = run(root, "add", "x y z", "--merge", "a.md", "--distinct", "why")
    check("--merge with --distinct refused", r.returncode != 0, r.stdout + r.stderr)
    target = [n for n in sorted(os.listdir(d)) if n.endswith("-BENCH-a.md")][0]
    before = set(os.listdir(d))
    r = run(root, "add", "alpha beta gamma lambda\nnew detail line", "--home", "NONE", "--merge", target)
    check("--merge succeeds", r.returncode == 0, r.stdout + r.stderr)
    check("--merge creates no new file", set(os.listdir(d)) == before, set(os.listdir(d)) ^ before)
    merged = open(os.path.join(d, target)).read().splitlines()
    check("--merge appends the text before the footer, keeping the footer",
          merged == ["alpha beta gamma", "", "alpha beta gamma lambda", "new detail line", "home: skill-x"], merged)
    r = run(root, "add", "alpha beta gamma delta", "--home", "NONE", "--merge", os.path.join("infrastructure", "state", "lessons", target))
    check("--merge accepts the path `add` prints", r.returncode == 0, r.stdout + r.stderr)
    r = run(root, "add", "", "--home", "NONE")
    check("empty lesson keeps FAIL", r.returncode != 0 and "empty lesson" in r.stdout + r.stderr)
    # could not look: a lesson that cannot be read is not "no twin"
    bad = os.path.join(d, "20261101T000001Z-BENCH-unreadable.md")
    os.makedirs(bad)   # a directory where a lesson file should be: open() raises
    r = run(root, "add", "nothing similar whatsoever banana", "--home", "NONE")
    check("unreadable lesson is could-not-look (rc 3, cause named), nothing written",
          r.returncode == 3 and "unreadable" in r.stdout + r.stderr and not [n for n in os.listdir(d) if "banana" in n],
          (r.returncode, r.stdout + r.stderr))
    os.rmdir(bad)
    r = run(root, "add", "completely unrelated words here", "--home", "NONE")
    check("distinct lesson accepted", r.returncode == 0, r.stdout + r.stderr)
    check("no dup hint", "possible duplicates:" not in r.stdout, r.stdout)
    # A lesson headed by era_history_mark.py still matches on its own words, and the label alone matches nothing.
    with open(os.path.join(d, "20261101T000000Z-BENCH-marked.md"), "w") as f:
        f.write("HISTORY: retired era (see design/RimMandrake/retired_eras_index_2026-11-18.md; what it names no longer "
                "runs). sprocket flange torque wobble\n")
    r = run(root, "add", "sprocket flange torque wobble", "--home", "NONE")
    check("a HISTORY-headed lesson is still found as a duplicate", "marked" in r.stdout + r.stderr and r.returncode == 2, r.stdout)
    r = run(root, "add", "history retired era design rimmandrake eras index machinery", "--home", "NONE")
    check("the HISTORY label is not lesson text", "marked" not in r.stdout, r.stdout)

if fails:
    print("selftest_lessons: %d FAILED" % len(fails))
    sys.exit(1)
print("selftest_lessons: OK")
