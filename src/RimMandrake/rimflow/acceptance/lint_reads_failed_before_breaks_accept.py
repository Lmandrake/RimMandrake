#!/usr/bin/env python3
"""Each promise on the failed-before lint-reads boundary page goes red on a planted fault.

Page: design/specs/2026-11-19-failed-before-reads/boundary.md (written by
RIMMANDRAKE_READ_ONLY_FILES_THAT_FAILED_PILOT_FOUND_ZERO). For each promise, its module is loaded with one planted
fault and that promise's test (selftest_failed_before_reads.py --only t_<name>) must FAIL. Built like
lint_reads_dispatch_trio_breaks_accept.py.

    python3 src/RimMandrake/rimflow/acceptance/lint_reads_failed_before_breaks_accept.py    exit 0 when every fault is caught
"""
import contextlib
import importlib
import importlib.util
import io
import os
import sys

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, R)
ST = "selftest_failed_before_reads"
MUT = [
 ("maturation_autonomy", "t_unreadable_concept_stage_holds_the_designer_lane",
  'row.update(decision="designer_unreadable", why=', 'row.update(decision="designer_wait", why='),
 ("maturation_autonomy", "t_unparseable_stage_time_is_no_time",
  '.timestamp()\n    except ValueError:\n        return None', '.timestamp()\n    except ValueError:\n        return 0.0'),
 ("maturation_hands", "t_blind_ledger_on_road_back_is_named",
  'h["road_back_error"] = "%s: %s" % (e.__class__.__name__, e)\n        return None',
  'h["road_back_error"] = "%s: %s" % (e.__class__.__name__, e)\n        return set()'),
 ("coverage_judge", "t_unreadable_prior_verdict_is_no_baseline",
  "    except DS.Refused:\n        return None\n    import run_void",
  "    except DS.Refused:\n        return {\"verdict\": \"covered\"}\n    import run_void"),
 ("run_void", "t_unreadable_run_record_spend_is_unmeasured",
  "            tok += RL.list_usd_to_weighted(c)\n        else:\n            unm.append(u)",
  "            tok += RL.list_usd_to_weighted(c)\n        else:\n            pass"),
]


def main():
    missed = []
    for mod, test, old, new in MUT:
        with open(os.path.join(R, mod + ".py"), encoding="utf-8") as f:
            src = f.read()
        if src.count(old) != 1:
            print("UNREADABLE %s / %s: the planted fault's text is not in %s.py exactly once" % (mod, test, mod))
            return 3
        for k in [k for k in sys.modules if k in (mod, ST)]:
            del sys.modules[k]
        m = importlib.util.module_from_spec(importlib.util.spec_from_loader(mod, loader=None))
        m.__file__ = os.path.join(R, mod + ".py")
        sys.modules[mod] = m
        exec(compile(src.replace(old, new), m.__file__, "exec"), m.__dict__)
        st = importlib.import_module(ST)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = st.main(["--only", test])
        print("%s %s / %s" % ("caught" if rc else "NOT CAUGHT", mod, test))
        if not rc:
            missed.append(test)
        del sys.modules[mod]    # the next fault, or the clean run, loads the real module again
    print("RESULT: %d of %d planted faults caught" % (len(MUT) - len(missed), len(MUT)))
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
