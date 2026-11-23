#!/usr/bin/env python3
"""list_stage_view_mutants.py: planted faults in the stage view and the owner's one view; their checks must go red.

Item RIMMANDRAKE_BUILD_ONE_OWNER_VIEW_NO_HOME_COUNT_BESIDE (mutate-your-checker). Each mutant is one realistic fault in
one file; at least one of the checks named for that file must FAIL by its own FAIL line, and the unmutated control of
every check must pass first. A file is mutated IN PLACE (the checks import it from its own folder) and restored in
`finally`; the run ends by proving the bytes are back.

    python3 src/RimMandrake/rimflow/acceptance/list_stage_view_mutants.py     exit 0: controls green, every mutant caught
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(RIMFLOW), "Utils")
F = {"LP": os.path.join(RIMFLOW, "list_pipeline.py"), "LD": os.path.join(RIMFLOW, "list_dispatch.py"),
     "NH": os.path.join(UTILS, "no_home.py"), "OQ": os.path.join(UTILS, "owner_queue.py"),
     "NM": os.path.join(UTILS, "maturation_nonmod.py"), "PR": os.path.join(UTILS, "probe_his_words.py")}
T = {"lp": os.path.join(RIMFLOW, "selftest_list_pipeline.py"), "3b": os.path.join(HERE, "step3b_stage_view_accept.py"),
     "nm": os.path.join(UTILS, "selftest_maturation_nonmod.py"), "ov": os.path.join(UTILS, "selftest_owner_one_view.py"),
     "3": os.path.join(HERE, "step3_one_view_accept.py")}
CHECKS = {"LP": ("lp", "3b", "nm"), "LD": ("lp",), "NH": ("ov", "3"), "OQ": ("ov", "3"), "NM": ("nm",), "PR": ("ov",)}

MUTANTS = [
    ("LP", "a closed item whose check fails reads closed", 'if state == "done" and verdict == "fails":', "if False:"),
    ("LP", "an unmeasured check reads ready", 'if verdict not in ("fails", None):',
     'if verdict not in ("fails", None, "unmeasured"):'),
    ("LP", "a due wait is still waiting", "if isinstance(waits, dict) and (until is None or until > now):",
     "if isinstance(waits, dict):"),
    ("LP", "a stale lane reading is trusted", "elif now - lane_at > LANE_STALE_S:", "elif False:"),
    ("LP", "a run end the tick has not read keeps the old verdict",
     "if newest_end is not None and not live and newest_end > lane_at:", "if False:"),
    ("LP", "the finish's own note counts as a later act",
     'if not isinstance(e, dict) or not e.get("id") or is_machine_act(e):', 'if not isinstance(e, dict) or not e.get("id"):'),
    ("LP", "a conflict is not escalated", 'if st["stage"] in ("trouble", "conflict"):', 'if st["stage"] in ("trouble",):'),
    ("LP", "the oldest group member is the newest", 'and (grp["age_h"] is None or a > grp["age_h"]):',
     'and (grp["age_h"] is None or a < grp["age_h"]):'),
    ("LP", "a blind lane row reads fails", 'if decision == "blind":\n        return "unmeasured"',
     'if decision == "blind":\n        return "fails"'),
    ("LP", "a route to the owner reads ready", 'return _r("review", "routed to the owner: %s" % ask, res)',
     'return _r("ready", "routed to the owner: %s" % ask, res)'),
    ("LP", "a dead promise reads kept", 'd["promise"] = "dead" if g(it, "live_broken") else "kept"',
     'd["promise"] = "kept"'),
    ("LD", "the tick drops the stage", 'stage=row_stage((facts.get("items") or {}).get(r["item"]), r, now))',
     "stage=None)"),
    ("NH", "a source that cannot be read counts zero", "            unm.append(name)\n            continue",
     "            by[name] = 0\n            continue"),
    ("NH", "no readable source reads 0", '"no_home": sum(by.values()) if by else None', '"no_home": sum(by.values())'),
    ("NH", "a run with a later act is still counted", "        if (last_event or {}).get(iid, 0) > end:\n            continue",
     "        if False:\n            continue"),
    ("NH", "a run on a lane item is counted", 'if _g(it, "state") in CLOSED or _g(it, "effect") or now - end > window:',
     'if _g(it, "state") in CLOSED or now - end > window:'),
    ("NH", "the shared reading is never used", "if not fresh:", "if False:"),
    ("NH", "a run that left a wait on its item is counted", 'if _g(it, "wait_until") or _g(it, "blocked"):',
     "if False:"),
    ("NH", "a Maturation stage run is counted", 'if (r.get("env") or {}).get("RM_CONTROL_STAGE"):', "if False:"),
    ("NH", "a run that left a LEFT OPEN: note is counted", "if any(t >= began for t in (left_open or {}).get(iid, [])):",
     "if False:"),
    ("OQ", "an unread count prints 0", 'return "not filed anywhere: %s%s" % (UNM if n is None else n,',
     'return "not filed anywhere: %s%s" % (0 if n is None else n,'),
    ("OQ", "ours is not oldest first", 'rows.sort(key=lambda r: (r["_t"], r["item"]))',
     'rows.sort(key=lambda r: r["item"], reverse=True)'),
    ("OQ", "his question is not escaped in html", 'e(x["q"][:130])', 'x["q"][:130]'),
    ("OQ", "a stale shared view is shown", "or not (0 <= now - v[\"at\"] < fresh_s):", "or False:"),
    ("NM", "a run recorded for mod none makes its item mod work", 'not in ("", "none"):', 'not in ("",):'),
    ("NM", "who is his is not read", "his=bool(his and i in his)", "his=False"),
    ("NM", "the tick's rows are ignored", "lane_row=lane_rows.get(i)", "lane_row=None"),
    ("PR", "a card a hook refused reads answered", 'elif b.get("type") == "tool_result" and not b.get("is_error"):',
     'elif b.get("type") == "tool_result":'),
    ("PR", "a card on screen now reads unanswered", 'out["on_screen"].add(last_ask[1])', "pass"),
]


def run(key):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, T[key]], capture_output=True, text=True, timeout=900, env=env,
                       stdin=subprocess.DEVNULL)
    out = r.stdout + r.stderr
    return r.returncode, [ln for ln in out.splitlines() if ln.startswith("FAIL")], out


def main():
    orig = {k: open(p, encoding="utf-8").read() for k, p in F.items()}
    digest = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in orig.items()}
    for key in T:
        rc, fails, out = run(key)
        if rc != 0:
            print("CONTROL RED: %s fails unmutated, so no mutant result means anything\n%s" % (T[key], out[-1500:]))
            return 3
    print("controls green (%d checks)" % len(T))
    missed = []
    try:
        for fk, name, old, new in MUTANTS:
            src = orig[fk]
            if src.count(old) != 1:
                print("NOT APPLIED  %s: its anchor is %s" % (name, "absent" if not src.count(old) else "not unique"))
                missed.append(name)
                continue
            mut = src.replace(old, new, 1)
            assert mut != src
            with open(F[fk], "w", encoding="utf-8") as f:
                f.write(mut)
            by = []
            for key in CHECKS[fk]:
                rc, fails, _ = run(key)
                if rc != 0 and fails:
                    by.append("%s (%s)" % (os.path.basename(T[key]), fails[0][:90]))
            with open(F[fk], "w", encoding="utf-8") as f:
                f.write(src)
            if by:
                print("CAUGHT       %s: %s" % (name, by[0]))
            else:
                print("NOT CAUGHT   %s" % name)
                missed.append(name)
    finally:
        for k, p in F.items():
            with open(p, "w", encoding="utf-8") as f:
                f.write(orig[k])
    back = all(hashlib.sha256(open(p, encoding="utf-8").read().encode()).hexdigest() == digest[k] for k, p in F.items())
    print("files restored: %s" % ("yes, byte for byte" if back else "NO"))
    print("%d of %d mutants caught" % (len(MUTANTS) - len(missed), len(MUTANTS)))
    return 0 if (not missed and back) else 1


if __name__ == "__main__":
    sys.exit(main())
