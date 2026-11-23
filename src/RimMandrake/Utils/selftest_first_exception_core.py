#!/usr/bin/env python3
"""Selftest: the first-exception tap's pure rules (JawaBenchFirstExceptionCore.cs). Page:
design/specs/2026-11-23-first-exception-tap/boundary.md; one test per promise, each clean and with a planted fault.
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/Utils/selftest_first_exception_core.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_tools_units as L   # noqa: E402


def t_the_first_is_kept_through_a_flood():
    return L.group("flood", ["flood"])


def t_an_error_is_not_an_exception():
    return L.group("plainerror", ["plainerror"])


def t_a_new_window_keeps_the_sessions_first():
    return L.group("window", ["window"])


def t_not_armed_or_blind_is_never_none_seen():
    return L.group("state", ["state"])


def t_one_error_counts_once():
    return L.group("roads", ["roads"])


def t_memory_is_bounded():
    return L.group("bounded", ["bounded"])


def main():
    try:
        res = [t_the_first_is_kept_through_a_flood(), t_an_error_is_not_an_exception(), t_a_new_window_keeps_the_sessions_first(),
               t_not_armed_or_blind_is_never_none_seen(), t_one_error_counts_once(), t_memory_is_bounded()]
    except L.Unmeasured as e:
        print("FAIL first exception core UNMEASURED: %s" % e)
        return 1
    print("first exception core: %d of %d promises hold" % (sum(res), len(res)))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
