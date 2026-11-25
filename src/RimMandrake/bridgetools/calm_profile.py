#!/usr/bin/env python3
"""calm_profile.py - the certificate lines of the calm profile of BRIDGE v2.0 (stdlib only, pure).

Item RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE. Page: design/specs/2026-11-23-bridge-v2/boundary.md §CALM PROFILE.
A control of the profile reads HELD in the game only when its certificate line is among the lines that the driver passes as
`certified` to `jawa/calm_profile action=arm`. A line is "tap.held": the tap certificate (tap_certificate.py) showed a planted
attempt of that kind HELD, on the loaded identity, in its certification session. This file turns a certificate into those lines:
nothing else may, so a driver cannot claim HELD for a control that no session proved.

  certificate_lines(cert, identity) -> (lines, why)   lines: the "tap.held" lines of a VALID certificate whose "held" route was
                                                      shown; [] with the reason for a missing, refused or foreign certificate
  arm_args(cert, identity, **profile) -> the args of jawa/calm_profile action=arm, with `certified` filled by certificate_lines
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tap_certificate as T  # noqa: E402

# The controls of profile standard/1 that have a certificate line (JawaBenchCalmProfileCore.Catalog): the line is the tap and its
# held route. Every other control reads ARMED UNPROVEN until a session shows its planted breach stopped.
LINES = ("incident.held", "gate.quest.held", "gate.mental.held")


def certificate_lines(cert, identity):
    """-> (lines, why). Only a certificate valid for this loaded identity gives lines, and only for routes it shows."""
    state, reasons = T.validate(cert, identity)
    if state != "valid":
        return [], "%s: %s" % (state, "; ".join(reasons) or "no certificate")
    cov = T.coverage(cert)
    out = []
    for line in LINES:
        tap, route = T.split_need(line)
        if route in (cov.get(tap) or {}).get("covered", []):
            out.append(line)
    return out, "valid certificate; %d of %d lines shown" % (len(out), len(LINES))


def arm_args(cert, identity, driver, **profile):
    """The args of jawa/calm_profile action=arm. `certified` is never taken from the caller."""
    if "certified" in profile:
        raise ValueError("certified comes from the certificate, never from the caller")
    lines, _ = certificate_lines(cert, identity)
    return dict(profile, action="arm", driver=driver, certified=",".join(lines))
