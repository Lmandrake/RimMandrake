# Acceptance test for RIMMANDRAKE_MEND_GRAFFITI_SOAK_SCENE_SUM_HIDES_TAXED_PAWN, second return (coverage judge
# rm-coverage-judge-1794940039 gap g1, stories_not_tax): sc_lived_in_soak must test the SHAPE of each colonist's graffiti
# mood, not its size against the forced control. Size against a capped control (BadMoodBudget) lets a colonist who holds
# a small debuff every day pass (exam e51), and an exemption for "a new mark" lets a rotating run of marks pass (exam k6).
# Each check prints its name; the run prints how many it read and the first that fails.
import json, sys
s = json.load(open(sys.argv[1]))
sc = {x["id"]: x for x in (s["scenes"] if isinstance(s, dict) else s)}.get("sc_lived_in_soak") or {}
ex = json.dumps(sc.get("expect")).lower()
ctl = sc.get("control") or {}
cex = json.dumps(ctl.get("expect")).lower()
cro = json.dumps(ctl.get("rules_out")).lower()
st = json.dumps(sc.get("start")).lower()
checks = [
    ("scene exists", bool(sc)),
    ("trait mix kept in start", "sensitive" in st and "clean freak" in st),
    ("no size comparison against the control", "below the control" not in ex and "summed" not in ex),
    ("per colonist", "each colonist" in ex or "every colonist" in ex),
    ("negative thoughts only, not netted", "negative" in ex and "netted" in ex),
    ("returns to zero", "returns to zero" in ex or "return to zero" in ex),
    ("held on most days of weeks two and three fails", "most days" in ex and "weeks two and three" in ex),
    ("a rotating source counts (k6)", "whatever" in ex and "source" in ex),
    ("only raid or mockery excused (e51)", "raid" in ex and "mock" in ex and "new mark" not in ex),
    ("unforced story kept", "unforced" in ex),
    ("control per colonist", "colonist" in json.dumps(ctl.get("case")).lower()),
    ("control shows sensitive and clean freak never returning to zero",
     "sensitive" in cex and "clean" in cex and ("never return" in cex or "does not return" in cex)),
    ("control rules out a size-only instrument", "size" in cro),
]
bad = [n for n, ok in checks if not ok]
print(("PASS (%d checks)" % len(checks)) if not bad else "FAIL %d of %d: %s" % (len(bad), len(checks), "; ".join(bad)))
sys.exit(0 if not bad else 1)
