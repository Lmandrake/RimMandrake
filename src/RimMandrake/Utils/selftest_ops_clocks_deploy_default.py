#!/usr/bin/env python3
"""Class guard for NIGHTLY_COP_FIX_RED_YZWCJJ_JDSB: "an installer defaults --deploy to the Operations deploy" is judged on
the add_argument("--deploy", default=...) call itself, never on the text around it.

The instance: the nightly of 2026-11-04 read ops_watch.py red because the check also required "RM_PULSE_DEPLOY" to be absent
from the file, and ops_watch legitimately READS pulse-deploy's age (DEPLOY_STALE). Its sibling: a substring check reads a
correct default red when the call is wrapped onto two lines. Both are the same class: text judged instead of the call.
Judge: ops_clocks.deploy_default_ok(src). The installers' real sources are judged too.

    python3 src/RimMandrake/Utils/selftest_ops_clocks_deploy_default.py
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.pop("RM_OPS_DEPLOY", None)
import ops_clocks as OC  # noqa: E402

# before the class fix there is no judge: replay the text predicate the 2026-11-04 nightly applied, so the guard shows the instance
judge = getattr(OC, "deploy_default_ok", None) or (lambda src: '__import__("ops_clocks").deploy()' in src and "RM_PULSE_DEPLOY" not in src)
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


GOOD = 'p.add_argument("--deploy", default=__import__("ops_clocks").deploy(),\n                   help="the deploy")\n'
check(judge(GOOD), "the shipped one-line form is a correct default")
check(judge('STALE = os.environ.get("RM_PULSE_DEPLOY", "/x")   # read, not the default\n' + GOOD),
      "a file that also READS RM_PULSE_DEPLOY elsewhere is still a correct default (the 2026-11-04 instance)")
check(judge('p.add_argument(\n    "--deploy",\n    default=__import__("ops_clocks").deploy(),\n    help="the deploy",\n)\n'),
      "the same call wrapped over lines is a correct default")
check(judge('import ops_clocks\np.add_argument("--deploy", default=ops_clocks.deploy())\n'),
      "ops_clocks.deploy() through a plain import is a correct default")
check(not judge('p.add_argument("--deploy", default=os.environ.get("RM_PULSE_DEPLOY", "/home/x"))\n'),
      "a default read from RM_PULSE_DEPLOY is not the Operations deploy")
check(not judge('p.add_argument("--deploy", default="/home/mandrake/rm/bench")\n'), "a hard-wired path is not the deploy")
check(not judge('p.add_argument("--deploy")\n# default=__import__("ops_clocks").deploy()\n'),
      "a comment naming the default is not a default")
check(not judge('p.add_argument("--other", default=__import__("ops_clocks").deploy())\n'),
      "the deploy as some other flag's default is not --deploy's default")
check(not judge("x = (\n"), "a file that does not parse is not judged correct")
for mod in ("ops_watch", "timers_guard", "account_usage", "switching_plan"):
    check(judge((HERE / (mod + ".py")).read_text(encoding="utf-8")), "%s's real source defaults --deploy to the deploy" % mod)

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
