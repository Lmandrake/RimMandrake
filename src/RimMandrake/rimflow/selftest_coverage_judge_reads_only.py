#!/usr/bin/env python3
"""selftest_coverage_judge_reads_only: the promise of design/specs/2026-11-20-coverage-judge-reads-only/boundary.md.
The coverage judge's second reader reads and never edits (item RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION,
point 6). The judge itself may fix (design/specs/2026-11-25-blind-readers-fix/boundary.md). No model call."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage_judge as CJ  # noqa: E402


def t_second_reader_cannot_edit():
    schema = {"type": "object"}
    tail = CJ.judge_tail("COVERAGE SECOND READER rm-coverage-judge-1", schema)
    deny = tail[tail.index("--disallowedTools") + 1].split(",") if "--disallowedTools" in tail else []
    good = (sorted(deny) == ["Edit", "NotebookEdit", "Write"] and tail[tail.index("--model") + 1] == CJ.MODEL
            and "COVERAGE SECOND READER rm-coverage-judge-1" in tail and "json" in tail
            and json.loads(tail[tail.index("--json-schema") + 1]) == schema and "--max-budget-usd" not in tail)
    return good, tail


def main():
    good, got = t_second_reader_cannot_edit()
    print("%s  second-reader-cannot-edit%s" % ("PASS" if good else "FAIL", "" if good else "  got: %r" % (got,)))
    print("%s selftest_coverage_judge_reads_only" % ("PASS" if good else "FAIL"))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
