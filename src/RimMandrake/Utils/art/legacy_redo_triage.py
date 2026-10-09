#!/usr/bin/env python3
"""legacy_redo_triage.py — triage the 229 legacy replace/redo rulings of Transient/legacy_unqueued_rulings_2026-10-09.md.

    python3 legacy_redo_triage.py            dry run: classify every row, write Transient/legacy_redo_triage_2026-10-09.md
    python3 legacy_redo_triage.py --apply    also file the surviving rows through fill_queue.py (priority 20)

Per row, first match wins:
  GONE_SRC      no file in src/ names the subject (any of its names/aliases) at all
  NO_ROSTER     named in src/ but by no BiomeDef roster or roster patch (xpath-only mentions are removals), and
                no def of ours (ThingDef/PawnKindDef in src/) by any of its names
  NEWER_RULING  a later owner ruling on the subject: a current biome sheet (Transient/biome_ffar/*.decisions.json)
                or the art ledger (infrastructure/state/art/events, by=owner, at later than this ruling)
  REDRAWN       a pending/active/done artpipe job for the subject (target_def/target_original, or a bound/name-matched
                render family from subject.py) created on/after the ruling, or a non-donor ledger variant of its texPath
                dated on/after the ruling
  DUPLICATE     another row of this list is queued for the same subject (the latest ruling wins)
Otherwise QUEUE: the job shape of enact.job_rows (canon image as canon_reference, his note verbatim), priority 20 --
below the 0-9 band art.py enact reserves for current biome-sheet redraws.

Sanity probes (run first, abort when they fail): Neebray (ruled 2026-09-20 on port_swac) must show Neebray jobs
created today (the live cauldronfix_neebray_v2_* jobs; the enact_cabe4675 ones were withdrawn) and not read QUEUE, and `hawkbat` must be found among jobs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import ingest as I  # noqa: E402
import subject as S  # noqa: E402

REPO = L.REPO_ROOT
SRC_MD = REPO / "Transient" / "legacy_unqueued_rulings_2026-10-09.md"
OUT_MD = REPO / "Transient" / "legacy_redo_triage_2026-10-09.md"
PRIORITY = 20
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
BLANKET = re.compile(r"blanket ruling", re.I)
LEG_FILES: set[str] = set()


def parse_ts(x):
    if not isinstance(x, str) or not x:
        return None
    try:
        d = dt.datetime.fromisoformat(x.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d


def read_rows() -> list[dict]:
    """(file, row) pairs from the markdown; verdict/at/note from the decisions JSON itself."""
    rows, cur, doc = [], None, None
    for line in SRC_MD.read_text().splitlines():
        m = re.match(r"### `([^`]+)`", line)
        if m:
            cur = m.group(1)
            LEG_FILES.add(cur)
            doc = json.loads((REPO / cur).read_text()).get("decisions") or {}
            continue
        m = re.match(r"\| (\S+) \| (\S+) \| (\d{4}-\d\d-\d\d) \|", line)
        if cur and m and m.group(1) != "row":
            key = m.group(1)
            v = doc.get(key) or {}
            rows.append({"file": cur, "row": key, "verdict": (v.get("decision") or m.group(2)).strip(),
                         "at": v.get("at") or m.group(3), "note": (v.get("note") or "").strip()})
    return rows


class Jobs:
    """created time + names of every pending/active/done artpipe job (failed and _withdrawn do not count)."""

    def __init__(self, w: S.World):
        self.rec = {}
        self.by_name = defaultdict(list)
        for sub in ("pending", "active", "done"):
            d = w.artpipe / sub
            for p in d.glob("*.json"):
                if p.name.endswith(".manifest.json"):
                    continue
                try:
                    j = json.loads(p.read_text())
                except (OSError, ValueError):
                    continue
                jid = j.get("id") or p.stem
                orig = j.get("target_original") or []
                if isinstance(orig, str):
                    orig = [x for x in re.split(r"[;,]", orig) if x.strip()]
                names = {x.strip() for x in [j.get("target_def") or "", *orig] if x and x.strip()}
                c = parse_ts(j.get("created"))
                self.rec[jid] = {"created": c, "names": names, "state": sub, "facings": j.get("facings") or []}
                for n in names:
                    self.by_name[n].append(jid)

    def after(self, names, when):
        out = set()
        for n in names:
            for jid in self.by_name.get(n, ()):
                c = self.rec[jid]["created"]
                if c and c >= when:
                    out.add(jid)
        return sorted(out)


def newer_sheets() -> dict:
    """name -> [(file, row, at, decision)] over the current biome sheets' decisions."""
    census = json.loads((REPO / "Transient" / "biome_ffar" / "census.json").read_text()).get("biomes") or {}
    out = defaultdict(list)
    for p in sorted((REPO / "Transient" / "biome_ffar").glob("*.decisions.json")):
        try:
            doc = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        crow = {r["key"]: r for r in (census.get(doc.get("biome")) or {}).get("rows") or []}
        for row, v in (doc.get("decisions") or {}).items():
            if not isinstance(v, dict) or not v.get("at") or not (v.get("decision") or v.get("note") or "").strip():
                continue
            names = {row} | set((crow.get(row) or {}).get("defNames") or []) | set((crow.get(row) or {}).get("donors") or [])
            for n in names:
                out[n].append((p.name, row, v["at"], (v.get("decision") or "").strip()))
    return out


def newer_ledger() -> dict:
    """subject_key -> [(at, verdict, source)] of owner rulings in the art ledger NOT from the legacy files."""
    out = defaultdict(list)
    for p in (REPO / "infrastructure" / "state" / "art" / "events").glob("*.jsonl"):
        for line in p.read_text().splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") != "ruling" or e.get("by") != "owner" or not e.get("at"):
                continue
            src = e.get("source_file") or e.get("via") or ""
            if src in LEG_FILES:
                continue
            for k in {e.get("subject_key"), L.subject_key(e.get("row_key") or ""), L.subject_key((e.get("target") or {}).get("row") or "")}:
                if k:
                    out[k].append((e["at"], e.get("verdict"), src))
    return out


class SrcIndex:
    """token -> files for src/**/*.xml; roster mentions = files holding a BiomeDef, minus xpath-only mentions."""

    def __init__(self, src: Path):
        self.tok = defaultdict(set)
        self.biome_files = {}
        for f in src.rglob("*.xml"):
            s = str(f)
            if "/archive" in s.lower():
                continue
            try:
                t = f.read_text(errors="replace")
            except OSError:
                continue
            for m in set(re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", t)):
                self.tok[m.lower()].add(f)
            if "BiomeDef" in t:
                self.biome_files[f] = t

    def named(self, names):
        return sorted({str(f) for n in names for f in self.tok.get(n.lower(), ())})

    def on_roster(self, names):
        hits = []
        for n in names:
            pat = re.compile(r"(?<![\w])" + re.escape(n) + r"(?![\w])", re.I)
            for f in self.tok.get(n.lower(), ()):
                t = self.biome_files.get(f)
                if not t:
                    continue
                for line in t.splitlines():
                    if pat.search(line) and "xpath" not in line.lower():
                        hits.append(f.name)
                        break
        return sorted(set(hits))


def strip_row(k: str) -> str:
    k = re.sub(r"_v\d+(_(east|north|south))?$", "", k)
    return re.sub(r"^[A-Z]_(?=\w{4})", "", k)


def aliases(w: S.World, key: str) -> tuple[str, dict, set]:
    base = strip_row(key)
    ours, orig = w.identify(base)
    names = {key, base, ours} | set(orig)
    stm = S.norm(S.stem(base))
    for dn, rec in w.defs.items():
        if len(stm) >= S.MIN_KEY and (S.norm(S.stem(dn)) == stm or S.norm(rec.get("label") or "") == stm) and dn.startswith(("RM_", "RSW_", "RUT_")):
            names.add(dn)
    return ours, orig, {n for n in names if n}


def classify(rows, w, jobs, srcx, sheets, ledger, probe_only=False):
    res = []
    for r in rows:
        at = parse_ts(r["at"]) or parse_ts(r["at"] + "T00:00:00+00:00")
        ours, orig, names = aliases(w, r["row"])
        out = dict(r, ours=ours, names=sorted(names), at_dt=at)
        a = S.resolve_art(strip_row(r["row"]), w, list(orig))
        out["texpaths"] = a["texpaths"]
        # --- redrawn evidence
        red = list(jobs.after(names, at))
        for c in a["columns"]:
            ids = [c["job"]] if c.get("job") else list(c.get("jobs") or [])
            for fam in ([c["ref"]] if c["kind"] in ("render", "job") else []):
                ids += w.families.get(fam, [])
            for jid in ids:
                rec = jobs.rec.get(jid)
                if rec and rec["created"] and rec["created"] >= at:
                    red.append(jid)
        out["redrawn_jobs"] = sorted(set(red))
        led = []
        for tp in a["texpaths"]:
            for sha in w.index.by_res.get(tp, ()):
                if w.index.is_purged(sha):
                    continue
                for v in w.index.variants.get(sha, []):
                    kind = (v.get("kind") or "")
                    if kind.startswith("donor") or kind == "?":
                        continue
                    d = parse_ts(v.get("date") or "") or parse_ts((v.get("date") or "") + "T00:00:00+00:00")
                    if d and d >= at:
                        led.append(f"{kind}:{sha[:8]}@{v.get('date')}")
        out["redrawn_ledger"] = sorted(set(led))[:5]
        # --- newer ruling
        nr = []
        for n in names:
            for f, row, t, dec in sheets.get(n, ()):
                tt = parse_ts(t)
                if tt and tt > at:
                    nr.append(f"{f}:{row}={dec or 'note'}@{t[:10]}")
        for k in {L.subject_key(n) for n in names}:
            for t, vd, src in ledger.get(k, ()):
                tt = parse_ts(t)
                if tt and tt > at + dt.timedelta(seconds=5):
                    nr.append(f"ledger:{k}={vd}@{t[:10]}")
        out["newer"] = sorted(set(nr))
        out["named_files"] = srcx.named(names)
        out["roster"] = srcx.on_roster(names)
        if not out["named_files"]:
            out["reason"] = "GONE_SRC"
        elif not out["roster"] and not (names & set(w.defs)):
            out["reason"] = "NO_ROSTER"
        elif out["newer"]:
            out["reason"] = "NEWER_RULING"
        elif out["redrawn_jobs"] or out["redrawn_ledger"]:
            out["reason"] = "REDRAWN"
        else:
            out["reason"] = "QUEUE"
        res.append(out)
    return res


def job_row(o, w, jobs) -> dict:
    key = strip_row(o["row"])
    canon = S.resolve_canon(key, w, [])
    refs = canon["images"][:1] if canon.get("match") != "none" else []
    animal = any(re.search(r"pawn|animal", tp, re.I) for tp in o["texpaths"])
    if not o["texpaths"]:
        animal = any(len(jobs.rec[j]["facings"]) > 1 for n in o["names"] for j in jobs.by_name.get(n, ()))
    facings = ["east", "south", "north"] if animal else []
    note = "" if BLANKET.search(o["note"]) else o["note"]
    label = S.norm(S.stem(key)) and re.sub(r"^(AB_|AA_|RSW_|RM_|RUT_|Plant_)", "", key).replace("_", " ")
    sk = L.subject_key(key)
    return {"id": f"legacy_{L.det_id('legacy-redo', o['file'], o['row'], o['at'])[:8]}_{sk}_v1",
            "rimflow_item_id": ITEM, "target_def": key,
            "prompt": (f"Owner's note, verbatim, overrides everything below: \"{note}\" " if note else "")
            + f"RimWorld sprite of the {label}, painterly vanilla-RimWorld house style; redraw it from scratch"
              + (" using the attached canon reference as anatomy guidance only." if refs else "."),
            "canvas_w": 256, "canvas_h": 256, "facings": facings, "priority": PRIORITY, "owner_note": note,
            "canon_reference": refs, "biome_neutral": True}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    w = S.World()
    jobs = Jobs(w)
    srcx = SrcIndex(w.src)
    sheets, ledger = newer_sheets(), newer_ledger()
    rows = read_rows()
    # --- sanity probes
    hawk = [j for n, js in jobs.by_name.items() if "hawkbat" in n.lower() for j in js]
    probe = classify([{"file": "Transient/port_swac_2026-09-20.decisions.json", "row": "Neebray", "verdict": "replace",
                       "at": "2026-09-20T09:34:52-07:00", "note": ""}], w, jobs, srcx, sheets, ledger)[0]
    neebray = [j for j in probe["redrawn_jobs"] if "neebray" in j and jobs.rec[j]["created"].date().isoformat() == "2026-10-09"]
    print(f"PROBE Neebray: reason={probe['reason']} enact jobs found={len(neebray)}; hawkbat jobs={len(hawk)}; "
          f"jobs read={len(jobs.rec)}")
    if not neebray or not hawk or probe["reason"] == "QUEUE":
        print("PROBE FAILED — the sweep cannot see; aborting")
        return 3
    res = classify(rows, w, jobs, srcx, sheets, ledger)
    # duplicates: same subject among would-be-queued rows; latest ruling wins
    q = [o for o in res if o["reason"] == "QUEUE"]
    groups = defaultdict(list)
    for o in q:
        groups[L.subject_key(strip_row(o["row"]))].append(o)
    for g in groups.values():
        g.sort(key=lambda o: o["at_dt"])
        for o in g[:-1]:
            o["reason"] = "DUPLICATE"
            o["dup_of"] = g[-1]["row"]
    queue = [o for o in res if o["reason"] == "QUEUE"]
    jr = [job_row(o, w, jobs) for o in queue]
    ids = {}
    if a.apply and jr:
        jp = REPO / "Transient" / "legacy_redo_triage_2026-10-09_jobs.json"
        jp.write_text(json.dumps(jr, indent=1))
        d = S.Path(w.artpipe)
        fq = [sys.executable, str(HERE.parent / "artpipe" / "fill_queue.py"), "--input", str(jp),
              "--pending-dir", str(d / "pending"), "--active-dir", str(d / "active"),
              "--done-dir", str(d / "done"), "--failed-dir", str(d / "failed")]
        r = subprocess.run(fq, capture_output=True, text=True, cwd=str(REPO))
        print(r.stdout[-1500:], r.stderr[-1500:], "rc", r.returncode)
        if r.returncode:
            return 4
    cnt = Counter(o["reason"] for o in res)
    md = [f"# Legacy redo triage 2026-10-09", "",
          "Script: `src/RimMandrake/Utils/art/legacy_redo_triage.py`. Input: `Transient/legacy_unqueued_rulings_2026-10-09.md` "
          f"({len(rows)} rows). Probes passed before the sweep: Neebray reads {probe['reason']} with {len(neebray)} Neebray jobs created today ({', '.join(neebray[:3])}); "
          f"`hawkbat` matches {len(hawk)} jobs; {len(jobs.rec)} jobs read (pending/active/done).", "",
          "Order of tests, first match wins: GONE_SRC, NO_ROSTER, NEWER_RULING, REDRAWN, DUPLICATE, else QUEUE.",
          "", "## Counts", "", "| reason | rows |", "|---|---|"]
    md += [f"| {k} | {cnt.get(k, 0)} |" for k in ("QUEUE", "GONE_SRC", "NO_ROSTER", "NEWER_RULING", "REDRAWN", "DUPLICATE")]
    md += ["", f"Queued at priority {PRIORITY} (enact files its biome-sheet redraws at 0; 0-9 is reserved): "
           f"{'APPLIED' if a.apply else 'DRY RUN, not yet filed'}.", "", "## Queued", "",
           "| row | verdict | file | job id | facings | canon ref | note |", "|---|---|---|---|---|---|---|"]
    for o, j in zip(queue, jr):
        md.append(f"| {o['row']} | {o['verdict']} | {Path(o['file']).name} | {j['id']} | {','.join(j['facings']) or 'single'} | "
                  f"{'yes' if j['canon_reference'] else 'no'} | {j['owner_note'][:60]} |")
    for reason, title in (("GONE_SRC", "Dropped: no src file names it"), ("NO_ROSTER", "Dropped: named in src, on no roster"),
                          ("NEWER_RULING", "Dropped: newer owner ruling"), ("REDRAWN", "Dropped: redrawn since"),
                          ("DUPLICATE", "Dropped: duplicate of another queued row")):
        md += ["", f"## {title} ({cnt.get(reason, 0)})", "", "| row | file | evidence |", "|---|---|---|"]
        for o in res:
            if o["reason"] != reason:
                continue
            ev = {"GONE_SRC": f"names tried: {', '.join(o['names'][:4])}",
                  "NO_ROSTER": f"named only in {', '.join(Path(f).name for f in o['named_files'][:3])}",
                  "NEWER_RULING": "; ".join(o["newer"][:2]),
                  "REDRAWN": "; ".join((o["redrawn_jobs"][:2] or []) + o["redrawn_ledger"][:1]),
                  "DUPLICATE": f"same subject as {o.get('dup_of')}"}[reason]
            md.append(f"| {o['row']} | {Path(o['file']).name} | {ev[:140]} |")
    OUT_MD.write_text("\n".join(md) + "\n")
    print(dict(cnt), "->", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
