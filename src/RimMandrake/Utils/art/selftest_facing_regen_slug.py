#!/usr/bin/env python3
"""facing_regen.slug(): colour variants get distinct slugs; rows that own a plain slug keep it."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import facing_regen as R

def row(t): return {"texPath": t}
g = "RM_LanternDeeps/Fauna/BMT_Caverns/Things/Animal/Gembug/%s/Jewelbug"
s = {c: R.slug(row(g % c)) for c in ("Red", "Green", "Yellow")}
assert len(set(s.values())) == 3, s
assert s["Red"] == "Jewelbug", s
a = R.slug(row("RM_TheRot/Fauna/BMT_PollutedLands/Things/Animal/SmogMoth/Smogapillar"))
b = R.slug(row("swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/SmogMoth/Smogapillar"))
assert a == "Smogapillar" and b != a and b.startswith("Smogapillar_"), (a, b)
assert R.slug(row("Gizka/Gizka")) == "Gizka" and R.slug(row("x/y/Foo")) == "Foo"
# every row of the installed state keeps its slug (state keys are lowercase texPaths, not slugs)
st = Path(__file__).resolve().parents[4] / "Transient/facing_regen_batch_2026-10-16/state.json"
if st.exists():
    items = json.loads(st.read_text())["items"]
    owners = {k for k, v in items.items() if v["status"] == "installed" and k.split("/")[-1] in R.SHARED_BASENAMES}
    # later batches installed more colour variants under hashed slugs (correct); the plain-slug owners must stay installed + plain
    assert R.PLAIN_SLUG_OWNERS <= owners, owners
    for k in owners - R.PLAIN_SLUG_OWNERS:
        assert R.slug(row(k)) != k.split("/")[-1], k
print("selftest_facing_regen_slug OK")
