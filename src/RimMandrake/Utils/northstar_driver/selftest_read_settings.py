"""selftest: site.read_settings treats a game-printed float ("1") as equal to a source-parsed default (1.0).
The string compare it replaced refused every Wastes live run at preflight (WASTELAND_LIVE_SUITE_FAILS_ACC_BIOMES_1)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from northstar_driver import site  # noqa: E402


class FakeSession:
    def __init__(self, values):
        self.values = values

    def call(self, tool, **kw):
        return {"success": True, "value": self.values[kw["field"]]}


def main():
    eq = site.setting_equals
    cases = [("1", 1.0, True), ("3", 3.0, True), ("60", 60.0, True), ("0.25", 0.25, True), ("1.5", 1.0, False),
             ("True", True, True), ("False", True, False), ("true", True, True), ("7", 7, True), ("x", 1.0, False),
             (None, 1.0, False), ("abc", "abc", True)]
    fails = [(g, w) for g, w, ok in cases if eq(g, w) != ok]
    assert not fails, "setting_equals wrong on %s" % fails
    expect = {"stormDoseMultiplier": 1.0, "gripperTheftMtbHours": 3.0, "enableStorms": True, "middenshellLureRange": 60.0}
    game = FakeSession({"stormDoseMultiplier": "1", "gripperTheftMtbHours": "3", "enableStorms": "True",
                        "middenshellLureRange": "60"})
    assert site.read_settings(game, "T", expect) == {}, site.read_settings(game, "T", expect)
    off = FakeSession(dict(game.values, gripperTheftMtbHours="4"))
    assert site.read_settings(off, "T", expect) == {"gripperTheftMtbHours": "4"}
    print("selftest_read_settings: all passed")


if __name__ == "__main__":
    main()
