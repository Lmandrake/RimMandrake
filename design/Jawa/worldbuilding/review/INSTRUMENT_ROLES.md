# Review instruments — which one is the DECISION OF RECORD

We now have four ways to review creature art. They are NOT interchangeable, and
only one class of them is authoritative. Written 2026-09-05 after the FiftyOne
prototype, because a second decision store is how review work gets silently lost.

| instrument | role | writes decisions? |
|---|---|---|
| `creature_register.html` (scroll sheet) | drill-down reference: full facts per creature, the hard calls | ✅ **decision of record** |
| `creature_triage.html` (keyboard) | bulk speed — one keypress + auto-advance, ~20-60 min for all 1,165 | ✅ **decision of record** |
| `deck/creature_deck_all_clusters.pptx` | spatial regrouping — drag tiles between decision bands | ⚠️ via explicit read-back only |
| **FiftyOne** (`fiftyone/`) | **worklist builder by NUMBERS** — range-filter and sort on mismatch, px/cell, mass, hits | 🔴 **NO — export only** |

The sheet and the triage tool share **one** `creature_register.decisions.json`
through **one** sidecar, so they cannot disagree.

## 🔴 Why FiftyOne is not the decision of record

It holds state in its own Mongo, so it **forks the decision store**: a stale App
can silently overwrite newer sheet work on export. It also cannot do two things the
sheets can — there is **no note editing in the OSS App** (it writes *tags* only),
and its **uniform thumbnail tiles destroy the relative-scale signal**, which is the
entire point of the `.scale.png` panel. Its tags are multi-valued while a decision
is not (nothing stops `keep` + `cut` coexisting; the exporter resolves by severity,
which is an assumption, not a guarantee).

⇒ **Use FiftyOne to FIND the work, not to record the verdict.** Range-filter to
"the 20 ALARM-badge creatures, worst first" or "sprites under 0.5 px/cell", then
rule on them in the triage tool or the sheet. Always export before rebuilding —
`build_dataset.py` drops and rebuilds, discarding un-exported in-App tagging.

## Operational gotchas
- `fiftyone-db` ships **no mongod for Ubuntu 26.04**; MongoDB 8.0.17 was dropped in
  by hand. **Any `pip install --upgrade fiftyone` wipes it** and the App stops
  starting. Re-drop the binary if that happens.
- Python 3.14 is off Voxel51's supported matrix — expect surprises outside the
  basics (brain/embeddings/plugins).
- Launch: `fiftyone/launch_app.sh 5151`, then `http://127.0.0.1:5151` from Windows.
  🔴 Run it in its own systemd scope (the script does) — heavy Python inside a seat
  cgroup killed a window today.
