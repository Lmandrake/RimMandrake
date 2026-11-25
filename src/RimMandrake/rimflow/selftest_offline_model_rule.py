#!/usr/bin/env python3
"""selftest: the offline model reaches every mod builder from the first build (owner, 2026-11-17: "it feels like the
Fable Rescuer again found that offline modeling is REALLY informative and useful. Sounds like something that should
be instructed to the mod builder in general, yes, from the get-go?"). Item RIMMANDRAKE_TEACH_OFFLINE_MODEL_FIRST_BUILD.

- one source: the marked block in roles/fable_rescue.md step 2; maturation.OFFLINE_MODEL is read from it, and no other
  brief source (rimflow .py, roles/*.md, .claude/agents/*.md) carries a pasted copy of its lines.
- the block says: decision logic runnable offline, on real game code wherever it runs (Verse code that needs no Unity
  player, measured by RIMMANDRAKE_PROBE_OFFLINE_MODEL_LINKING_REAL_GAME_CODE), so an offline test runs the SHIPPED decision; a generator of the situations
  read by the bars' own checks, built before fixing or tuning; the range declared (what it varies, how many cases, what
  it leaves out), never "every case"; proportional (no decision logic: one line instead).
- the offline builder brief (brief_text, for a mod with no records yet: the first build) and the road-back fixer brief
  carry it; the rescue brief (fable_rescue.md) still does, in place.
- it states no spend, cap or budget.
Each check prints what it read.
"""
import glob
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import maturation as M  # noqa: E402
import maturation_autonomy as MA  # noqa: E402

RESCUE = os.path.join(HERE, "roles", "fable_rescue.md")
fails = []


def check(ok, what):
    print("%s %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        fails.append(what)


with open(RESCUE, encoding="utf-8") as fh:
    rescue = fh.read()
block = getattr(M, "OFFLINE_MODEL", "")
check(bool(block), "maturation.OFFLINE_MODEL exists (%d chars)" % len(block))
check(bool(block) and block in rescue, "the rescue brief fable_rescue.md carries the block in place")
reader = getattr(M, "read_offline_model", None)
check(callable(reader) and reader() == block, "OFFLINE_MODEL is read from fable_rescue.md, not written in code")

flatb = re.sub(r"\s+", " ", block)
for words in ("Hunt parameter regimes and regions, not examples.", "Verse", "SHIPPED decision",
              "runnable offline, on real game code wherever it runs",
              "a generator of the situations the mod can be in", "the same checks the bars use",
              "Before any fix or tuning", "what it varies, how many cases it makes, what it leaves out and why",
              "never \"every case\"", "no decision logic"):
    check(words in flatb, "the block says %r" % words)
spend = re.findall(r"(?i)\$\d|\busd\b|budget|\bspend|\bcap\b|\bcaps\b|\btokens?\b", block)
check(not spend, "the block states no spend, cap or budget (found %d: %s)" % (len(spend), spend))

root = tempfile.mkdtemp(prefix="offline_model_st_")
try:
    os.makedirs(os.path.join(root, "design", "concepts", "Mod"))
    text, _ = M.brief_text(root, "Mod")
    check(bool(block) and block in text, "the first offline build brief for a mod with no records carries the block "
          "(%d chars of brief)" % len(text))
finally:
    shutil.rmtree(root, ignore_errors=True)
fb = MA.fixer_brief("RIMMANDRAKE_X_Y_Z", "Mod", 5)
check(bool(block) and block in fb, "the road-back fixer brief carries the block")

# one source: every substantial line of the block appears in no other brief source
lines = [x.strip() for x in block.split("\n") if len(x.strip()) >= 50]
srcs = [p for p in (glob.glob(os.path.join(HERE, "*.py")) + glob.glob(os.path.join(HERE, "roles", "*.md"))
                    + glob.glob(os.path.join(ROOT, ".claude", "agents", "*.md")))
        if os.path.abspath(p) not in (os.path.abspath(RESCUE), os.path.abspath(__file__))]
copies = []
for p in srcs:
    with open(p, encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    copies += ["%s: %s" % (os.path.relpath(p, ROOT), x[:50]) for x in lines if x in t]
check(bool(lines) and not copies, "no pasted copy of the block's %d lines in %d other brief sources (%d found%s)"
      % (len(lines), len(srcs), len(copies), (": " + "; ".join(copies[:3])) if copies else ""))

if fails:
    print("FAIL selftest_offline_model_rule: %d" % len(fails))
    sys.exit(1)
print("PASS selftest_offline_model_rule")
