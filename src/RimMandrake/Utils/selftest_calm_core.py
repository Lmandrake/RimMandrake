#!/usr/bin/env python3
"""Selftest: the calm map's rules and lease lifecycle. Page: design/specs/2026-11-23-calm-map/boundary.md; one test
per promise. Rule groups also run with a planted fault (at least one red).
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED. Run: python3 src/RimMandrake/Utils/selftest_calm_core.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_tools_units as L   # noqa: E402


def t_calm_only_when_every_control_was_read():
    return L.group("everyread", ["unread"])


def t_each_thing_not_calm_is_named():
    return L.group("named", ["unnamed"])


def t_not_calm_outranks_could_not_read():
    return L.group("outranks", ["outrank"])


def t_an_exception_is_shown_and_checked():
    return L.group("excepted", ["except"])


def t_the_gate_holds_all_but_the_allowed():
    return L.group("gate", ["gate"])


def t_every_breach_is_counted():
    return L.group("breach", ["breach"])


def t_lease_expires_while_paused():
    return L.group("paused_expiry", [])


def t_release_restores_proximity_letters():
    return L.group("letter_restore", [])


def t_arm_tick_follows_game():
    return L.group("arm_tick_follows_game", [])


def t_reassert_keeps_the_lease():
    return L.group("reassert_lease", [])


def main():
    try:
        res = [t_calm_only_when_every_control_was_read(), t_each_thing_not_calm_is_named(), t_not_calm_outranks_could_not_read(),
               t_an_exception_is_shown_and_checked(), t_the_gate_holds_all_but_the_allowed(), t_every_breach_is_counted(),
               t_lease_expires_while_paused(), t_release_restores_proximity_letters(), t_arm_tick_follows_game(),
               t_reassert_keeps_the_lease()]
    except L.Unmeasured as e:
        print("FAIL calm core UNMEASURED: %s" % e)
        return 1
    print("calm core: %d of %d promises hold" % (sum(res), len(res)))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
