#!/usr/bin/env python3
"""Each promise on the dispatch trio's lint-reads boundary pages goes red on a planted fault.

Pages: design/specs/2026-11-19-{maturation-dispatch,card-capture}-reads/boundary.md (written by
RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS, the dispatch trio; red_dispatch.py has no page: none of
its places is RARE). For each promise, its module is loaded with one planted fault and that promise's test
(selftest_<module>_reads.py --only t_<name>) must FAIL. Built like lint_reads_promise_breaks_accept.py.

    python3 src/RimMandrake/rimflow/acceptance/lint_reads_dispatch_trio_breaks_accept.py    exit 0 when every fault is caught
"""
import contextlib
import importlib.util
import io
import os
import sys

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, R)
MUT = [
 ("maturation_dispatch", "t_dispatch_state_absent_is_empty_unreadable_raises",
  "    except (OSError, ValueError) as e:\n        raise RuntimeError(\"%s cannot be read",
  "    except (OSError, ValueError) as e:\n        return {}\n        raise RuntimeError(\"%s cannot be read"),
 ("maturation_dispatch", "t_unparseable_time_is_no_time",
  "fromisoformat(str(iso_s)).timestamp()\n    except ValueError:\n        return None",
  "fromisoformat(str(iso_s)).timestamp()\n    except ValueError:\n        return 0.0"),
 ("maturation_dispatch", "t_unreadable_run_record_ends_nothing",
  'rec = rec_of(r["unit"]) or {}\n            done', 'rec = rec_of(r["unit"]) or {"status": "finished"}\n            done'),
 ("card_capture", "t_answer_time_parses_or_is_none", '"%Y-%m-%dT%H:%M:%S"))\n    except ValueError:\n        return None',
  '"%Y-%m-%dT%H:%M:%S"))\n    except ValueError:\n        return 0'),
 ("card_capture", "t_a_card_without_a_readable_time_is_never_matched",
  "        t = _epoch(c.get(\"answered\"))\n", "        t = _epoch(c.get(\"answered\")) or now - 60\n"),
]


def main():
    missed = []
    for mod, test, old, new in MUT:
        with open(os.path.join(R, mod + ".py"), encoding="utf-8") as f:
            src = f.read()
        if src.count(old) != 1:
            print("UNREADABLE %s / %s: the planted fault's text is not in %s.py exactly once" % (mod, test, mod))
            return 3
        for k in [k for k in sys.modules if k in (mod, "selftest_%s_reads" % mod)]:
            del sys.modules[k]
        m = importlib.util.module_from_spec(importlib.util.spec_from_loader(mod, loader=None))
        m.__file__ = os.path.join(R, mod + ".py")
        sys.modules[mod] = m
        exec(compile(src.replace(old, new), m.__file__, "exec"), m.__dict__)
        st = importlib.import_module("selftest_%s_reads" % mod)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = st.main(["--only", test])
        print("%s %s / %s" % ("caught" if rc else "NOT CAUGHT", mod, test))
        if not rc:
            missed.append(test)
    print("RESULT: %d of %d planted faults caught" % (len(MUT) - len(missed), len(MUT)))
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
