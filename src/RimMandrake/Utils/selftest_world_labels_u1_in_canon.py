"""Selftest: the canonical start save carries the U1 region labels (WORLD_LABELS_RESTORE_SIZES_MIRROR_WAS_OURS).

Offline, read-only, a few seconds. Reads `planet.start_savegame` from infrastructure/state/canon.yml,
opens that save in world/, and checks every one of the 71 U1 labels:
  - present by name;
  - centre on the U1 plan's tile (the member tile nearest the biggest piece's centroid), within
    label_centre_check.CENTRE_TOL_DEG (a same-tile test);
  - size = the U1 canonical size as later scaled by the owner's LABELS70 card (2026-10-20,
    'Smaller, about 70%'), i.e. world/ASHKARR_LABELS70_2026-10-20_plan.json `after.size`.
Sanity probe: the same check against the U1 `after` sizes must FAIL on size (the instrument sees sizes),
and a centre moved one tile must fail (it sees positions).
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import label_centre_check as LC
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
fails = []


def ok(c, m):
    if not c:
        fails.append(m)


canon = open(os.path.join(REPO, "infrastructure/state/canon.yml"), encoding="utf-8").read()
m = re.search(r"^\s*start_savegame:\s*(\S+)", canon, re.M)
ok(m is not None, "canon.yml has no planet.start_savegame")
save = os.path.join(REPO, "world", m.group(1)) if m else ""
ok(os.path.isfile(save), "canonical start save not in world/: %s" % save)
u1 = json.load(open(os.path.join(REPO, "world/ASHKARR_PARITY_U1_labels_2026-10-20_plan.json"), encoding="utf-8"))["features"]
l70 = {f["name"]: f for f in json.load(open(os.path.join(REPO, "world/ASHKARR_LABELS70_2026-10-20_plan.json"),
                                             encoding="utf-8"))["features"]}
ok(len(u1) == 71 and set(l70) == {f["name"] for f in u1}, "U1 / LABELS70 plans disagree on the label set")

if not fails:
    live = LC.read_save_features(save)
    want = [{"name": f["name"], "after": {"drawCenter": f["after"]["drawCenter"],
                                          "size": l70[f["name"]]["after"]["size"]}} for f in u1]
    bad = LC.check_labels(want, live, "after")
    ok(bad == [], "canonical save vs U1 centres + LABELS70 sizes: %d mismatches %s" % (len(bad), bad[:5]))
    # sanity probes: the instrument can see a size change and a one-tile move
    raw = LC.check_labels(u1, live, "after")
    ok(sum(1 for r in raw if r[1] == "size") >= 60, "probe: unscaled U1 sizes should fail on size (instrument blind?)")
    ok(not any(r[1] == "centre" for r in raw), "probe: U1 centres should pass under both size sets")
    a = live[u1[0]["name"]]["drawCenter"]; rot = math.radians(1.0)
    moved = dict(live); moved[u1[0]["name"]] = dict(live[u1[0]["name"]], drawCenter=(
        a[0] * math.cos(rot) - a[2] * math.sin(rot), a[1], a[0] * math.sin(rot) + a[2] * math.cos(rot)))
    ok(any(r[1] == "centre" for r in LC.check_labels(want, moved, "after")), "probe: a label moved ~1 deg must fail")
    print("labels checked: %d of %d in save %s" % (len(want), len(live), os.path.basename(save)))

if fails:
    print("FAIL:\n  " + "\n  ".join(fails)); sys.exit(1)
print("PASS selftest_world_labels_u1_in_canon")
