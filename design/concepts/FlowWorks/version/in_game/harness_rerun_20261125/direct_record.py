#!/usr/bin/env python3
"""Build a testq-shaped done record from a DIRECT modcheck run (no lane), the way
infrastructure/stevedesktop/worker.py read_sheet builds it, so retest.py passed <record> judges it with the same code.

usage: direct_record.py <clone> <modcheck.log> <out record.json> <job id> <mod> <chains,csv> <sha> <game>
A run with no sheet JSON becomes outcome INVALID/HARNESS with the first refusal line (as the worker does), so it FAILS.
"""
import json
import os
import re
import sys

clone, log, out, jid, mod, chains, sha, game = sys.argv[1:9]
sys.path.insert(0, os.path.join(clone, "src/RimMandrake/Utils/testq"))
sys.path.insert(0, os.path.join(clone, "infrastructure/stevedesktop"))
import schema as S                                          # noqa: E402
from worker import expected_rows, expected_row_chains, FIRST_CAUSE_RE   # noqa: E402

text = open(log, encoding="utf-8", errors="replace").read()
names = re.findall(r"Transient[\\/]+modcheck[\\/]+([^\s\\/]+)\.html", text)
sheet = os.path.join(clone, "Transient", "modcheck", names[-1] + ".json") if names else None
data = None
if sheet and os.path.isfile(sheet):
    data = json.load(open(sheet, encoding="utf-8"))
res = {"outcome": None, "cause": None, "rows": [], "sheet": sheet, "game": game, "runner_sha": sha}
if not data:
    first = FIRST_CAUSE_RE.search(text)
    res.update(outcome="INVALID", cause="HARNESS",
               note="no sheet JSON; first: %s" % (first.group(0).strip()[:300] if first else text[-300:]))
else:
    rows = S.rows_from_summary(data.get("summary") or {})
    seen = {r["row"] for r in rows}
    planned = expected_row_chains(text)
    for w in expected_rows(text):
        if w not in seen:
            rows.append({"chain": None, "row": w, "verdict": "NOT_RUN", "validity": None, "freshness": None,
                         "detail": "in modcheck's preview plan, absent from the sheet", "planned_chain": planned.get(w)})
            seen.add(w)
    res.update(outcome="DONE", rows=rows, note="direct run on %s; %s" % (game, S.count_verdicts(rows)))
rec = {"job": {"id": jid, "mod": mod, "selector": {"chains": chains.split(",")}, "source": sha, "lane": "direct:" + game},
       "result": res}
json.dump(rec, open(out, "w", encoding="utf-8"), indent=1)
print("RECORD %s outcome=%s %s" % (out, res["outcome"], res.get("note")))
