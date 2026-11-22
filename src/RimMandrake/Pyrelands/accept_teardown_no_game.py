"""Acceptance test: Pyrelands _tear_down with no game loaded records no teardown FAIL (nothing map-bound can leak),
but a real refusal on a loaded map still records FAIL. Run from the repo root."""
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Pyrelands"))
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
import validation as V
NOGAME = {"success": False, "message": "No current map. These tools are map-scoped; use the planet-scoped world tool family instead.",
          "state": {"programState": "Entry", "hasCurrentGame": False}}
class S:
    def __init__(self, r): self.r = r
    def call(self, tool, **kw): return self.r(tool)
class T:
    def __init__(self, r):
        self.session = S(r); self.components = []; self.found = []
    def _on_finding(self, c): self.found.append(c)
ok = 0; bad = 0
def check(name, cond):
    global ok, bad
    print(("PASS " if cond else "FAIL ") + name); ok += cond; bad += (not cond)
V._PRIOR.clear(); V._GEN.pop("teardown_bad", None)
t = T(lambda tool: NOGAME); V._tear_down(t, fire=True, weather=True)
check("no game, fire+weather: no teardown FAIL", not any(c.verdict == "FAIL" for c in t.components))
V._PRIOR.clear(); V._GEN.pop("teardown_bad", None)
t = T(lambda tool: {"success": False, "message": "extinguish blew up", "state": {"programState": "Playing", "hasCurrentGame": True}}
      if tool == "jawa/map_fire" else {"success": True, "sizeX": 250, "sizeZ": 250})
V._tear_down(t, fire=True, weather=False)
check("loaded map, extinguish refused: teardown FAIL kept", any(c.verdict == "FAIL" for c in t.components))
V._PRIOR.clear(); V._GEN.pop("teardown_bad", None)
t = T(lambda tool: {"success": True, "sizeX": 250, "sizeZ": 250}); V._tear_down(t, fire=True, weather=True)
check("loaded map, all calls succeed: no teardown FAIL", not any(c.verdict == "FAIL" for c in t.components))
print("%d PASS %d FAIL" % (ok, bad)); sys.exit(1 if bad else 0)
