"""amend.py <rows.jsonl> <test> <evidence-substring> <json-fields>: set record fields (never verdict) on the row of <test>
whose evidence path contains <evidence-substring> (visit 12 helper: site_checked read from the proof's own site block,
outcome and class on a non-PASS row). Refuses to touch 'verdict' or 'rc'."""
import json, sys
path, test, ev, fields = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
assert not {"verdict", "rc"} & set(fields), "amend.py never changes a verdict"
rows = [json.loads(l) for l in open(path)]
hit = [r for r in rows if r["test"] == test and ev in r.get("evidence", "")]
assert len(hit) == 1, "matched %d rows" % len(hit)
hit[0].update(fields)
open(path, "w").write("".join(json.dumps(r) + "\n" for r in rows))
print("amended", test, ev, sorted(fields))
