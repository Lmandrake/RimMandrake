"""modcheck -- L4a scenario layer on top of rimdrive (L1/L2), per
design/RimMandrake/mod_validation_runner_spec.md.

    from modcheck import Suite

    suite = Suite("RM_PitTraps")

    @suite.chain("pit_capture")
    def pit_capture(t):
        t.clear_area(size=40)
        ...
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)          # sibling-module imports (suite/status/report/runner)
_UTILS = os.path.dirname(_HERE)
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)         # rimdrive lives here

from suite import Suite, Component, TestContext, ExpectationFailed, Precondition  # noqa: E402,F401

__all__ = ["Suite", "Component", "TestContext", "ExpectationFailed", "Precondition"]
