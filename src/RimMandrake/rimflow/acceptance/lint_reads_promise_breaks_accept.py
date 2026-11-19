#!/usr/bin/env python3
"""Each promise on the three lint-reads boundary pages goes red on a planted fault.

Pages: design/specs/2026-11-19-{seat-restart,designer-stage,maturation}-reads/boundary.md (written by
RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS). For each promise, its module is loaded with one planted
fault and that promise's test (selftest_<module>_reads.py --only t_<name>) must FAIL.

    python3 src/RimMandrake/rimflow/acceptance/lint_reads_promise_breaks_accept.py    exit 0 when every fault is caught
"""
import contextlib
import importlib.util
import io
import os
import sys

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, R)
MUT = [
 ("seat_restart", "t_unreadable_transcript_is_no_reading",
  "# fail closed: an unreadable or torn tail is no reading at all\n        return None", "# m\n        return {}"),
 ("seat_restart", "t_blind_bridge_reading_holds", 'return "bridge unreadable (%s)" % br.get("why")', "return None"),
 ("seat_restart", "t_unreadable_shard_is_no_reading", "    except OSError:\n        return None\n    # a line that cannot",
  "    except OSError:\n        return []\n    # a line that cannot"),
 ("designer_stage", "t_absent_is_default_unparseable_refuses",
  'raise Refused("%s does not parse: %s" % (os.path.basename(p), e))', "return default"),
 ("designer_stage", "t_unread_owner_shard_is_none", "    if lines is None:\n        return None\n    tsns, delegated",
  "    if lines is None:\n        return []\n    tsns, delegated"),
 ("designer_stage", "t_unread_ledger_is_said_in_the_packet", 'notes.append("ledger UNMEASURED: done items not read")', "pass"),
 ("maturation", "t_absent_only_when_measured", "    except OSError:\n        return False\n    return False",
  "    except OSError:\n        return True\n    return False"),
 ("maturation", "t_mod_json_read_names_its_failure", 'return None, "unreadable JSON"', 'return None, "no file"'),
 ("maturation", "t_unread_ledger_endings_is_none",
  "# a shard that cannot be read: no partial count\n        return None", "# m\n        return {}"),
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
