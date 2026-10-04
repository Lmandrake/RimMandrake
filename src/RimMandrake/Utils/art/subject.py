#!/usr/bin/env python3
"""subject.py — the ONE answer to "what art and what canon belong to this subject?" (ART_SUBJECT_RESOLVER_1).

    python3 src/RimMandrake/Utils/art/subject.py RSW_WraidAlpha [RM_Dorrak ...] [--json]

Spec: design/RimMandrake/art_resolution_rootcause_2026-10-04.md §5.1. Every sheet, census and art tool is meant
to call this instead of its own guess (phase 2 ports them). The subject is a **defName**; an ORIGINAL name (a donor
defName, a canon species slug) is accepted too and maps to our defName, and both are carried on every answer —
owner, 2026-10-04: renders are named by their ORIGINAL name as well as our renamed one, "so we never lose track of
the donor or canon reference during renames". Provenance lives in the art ledger / artpipe records, never in
deployed mod files.

Every hit carries a CONFIDENCE, one of three:
  bound         a durable record ties the picture (or entry) to this subject: ledger variant of the def's texPath,
                collected.jsonl / job install_to of that texPath, a job's target_def/target_original; for canon,
                the INDEX.md defName column.
  name-matched  a spelling match only, with the exact key and where it came from. Job ids are matched on WHOLE
                underscore tokens (a contiguous token run equal to the key) — never a prefix, never the texPath
                folder word (that was B0: every Things/Plant/X row matched every *_plant_* job).
  none          nothing found. NEVER rendered as absence: the `searched` record says which keys were tried
                against which sources and how big each source was.

Read-only. Nothing here writes anywhere.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

REPO = L.REPO_ROOT
TIER_RE = re.compile(r"^(RSW_|RM_|RUT_|rut_|AA_|AB_|A_|SW_|BMT_|VCE_|JOE_|AEXP_|VFEI2_|RG_|ZB_|ZBiome_)")
OURS_RE = re.compile(r"^(RSW_|RM_|RUT_|rut_)")
FAM_RE = re.compile(r"_(north|east|south|west)(_r\d+)?$")
NONBODY_RE = re.compile(r"dess?icc?at|corpse|_mote|halo|filth|skeleton|print|mask|_icon\b", re.I)
VARIANT_WORDS = {"alpha", "juv", "juvenile", "feral", "mature", "elder", "young", "adult", "baby", "calf", "pup",
                 "wild", "matriarch", "queen", "hatchling", "larva", "lesser", "greater", "male", "female"}
BODY_ROLES = {"body", "flying", "swimming", "plant_immature", "plant_leafless"}
MIN_KEY = 4
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")


def stem(name: str) -> str:
    return re.sub(r"^Plant_", "", TIER_RE.sub("", name or ""))


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def words(s: str) -> list[str]:
    return re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", (s or "").replace("_", " "))


def variant_stripped(name: str) -> str:
    """'WraidAlpha' -> 'wraid', 'FaaJuv' -> 'faa'; '' when no variant word was dropped or nothing is left."""
    w = words(stem(name))
    base = [x for x in w if x.lower() not in VARIANT_WORDS]
    return "".join(base).lower() if base and len(base) < len(w) else ""


def token_match(family: str, key: str) -> bool:
    """True when a contiguous run of the family's underscore tokens spells KEY exactly (normalised)."""
    toks = [norm(t) for t in family.split("_") if t]
    for i in range(len(toks)):
        acc = ""
        for t in toks[i:i + 5]:
            acc += t
            if acc == key:
                return True
            if len(acc) >= len(key):
                break
    return False


def res_of_dest(dest: str) -> str | None:
    """'src/<Tier>/<Mod>/Textures/a/b/X_east.png' -> 'a/b/X'."""
    d = (dest or "").replace("\\", "/")
    if "/Textures/" not in d:
        return None
    return L.parse_texfile(d.split("/Textures/", 1)[1])["res"]


class World:
    """Everything the resolver reads, loaded lazily and once. Every root is injectable (selftests)."""

    def __init__(self, src_root: Path | None = None, canon_root: Path | None = None,
                 artpipe_root: Path | None = None, facts_root: Path | None = None, index: "L.Index | None" = None,
                 read_jobs: bool = True):
        self.src = Path(src_root or REPO / "src")
        self.canon_root = Path(canon_root or REPO / "design" / "RimStarWars" / "canon_references")
        if artpipe_root is None:
            sys.path.insert(0, str(HERE.parent / "artpipe"))
            import state_dir  # noqa: E402
            artpipe_root = state_dir.resolve()
        self.artpipe = Path(artpipe_root)
        self.facts = Path(facts_root or REPO / "infrastructure" / "state" / "facts")
        self._index = index
        self.read_jobs = read_jobs
        self._c: dict = {}

    # ── defs ──
    def _defs(self):
        if "defs" in self._c:
            return self._c["defs"]
        D, fwd = {}, {}
        arrow = re.compile(r"\b([A-Za-z][A-Za-z0-9_]{2,})\s*(?:->|→)\s*((?:RSW_|RM_|RUT_|rut_)[A-Za-z0-9_]+)")
        for f in sorted(self.src.rglob("*.xml")):
            s = str(f)
            if "/Defs/" not in s or "/archive" in s.lower():
                continue
            try:
                root = ET.parse(f).getroot()
            except (ET.ParseError, OSError):
                continue
            for d in root:
                if not isinstance(d.tag, str) or d.tag not in ("ThingDef", "PawnKindDef"):
                    continue
                dn = (d.findtext("defName") or "").strip()
                if not dn:
                    continue
                rec = D.setdefault(dn, {"types": [], "label": None, "race": None})
                rec["types"].append(d.tag)
                rec["label"] = rec["label"] or (d.findtext("label") or "").strip() or None
                if d.tag == "PawnKindDef":
                    rec["race"] = (d.findtext("race") or "").strip() or None
            try:
                for m in arrow.finditer(f.read_text(errors="replace")):
                    fwd.setdefault(m.group(1), (m.group(2), f"rename comment in {f.relative_to(self.src.parent)}"))
            except OSError:
                pass
        for p in sorted(self.facts.glob("mlie_creature_defname_map_wave_*.json")):
            try:
                d = json.loads(p.read_text())
            except (OSError, ValueError):
                continue
            items = d["creatures"].items() if isinstance(d.get("creatures"), dict) else d.items()
            for k, v in items:
                if isinstance(v, str) and v.startswith("RSW_") and not k.startswith("_"):
                    fwd.setdefault(k, (v, f"mlie map {p.name}"))
        fwd = {k: v for k, v in fwd.items() if k != v[0]}
        back = defaultdict(dict)
        for orig, (ours, ev) in fwd.items():
            back[ours].setdefault(orig, ev)
        self._c["defs"] = (D, fwd, dict(back))
        return self._c["defs"]

    @property
    def defs(self) -> dict:
        return self._defs()[0]

    @property
    def slots(self) -> dict:
        if "slots" not in self._c:
            self._c["slots"] = L.scan_def_slots(self.src)
        return self._c["slots"]

    @property
    def tex_by_def(self) -> dict:
        if "tbd" not in self._c:
            t = defaultdict(set)
            for tp, ss in self.slots.items():
                for s in ss:
                    if s["role"] in BODY_ROLES:
                        t[s["subject"].split("#")[0]].add(tp)
            for dn, rec in self.defs.items():          # a PawnKindDef draws its race; share both ways
                r = rec.get("race")
                if r and r != dn:
                    both = t.get(dn, set()) | t.get(r, set())
                    if both:
                        t[dn] = set(both)
                        t[r] = set(both)
            self._c["tbd"] = dict(t)
        return self._c["tbd"]

    @property
    def def_by_tex(self) -> dict:
        if "dbt" not in self._c:
            o = defaultdict(set)
            for dn, tps in self.tex_by_def.items():
                for tp in tps:
                    o[tp].add(dn)
            self._c["dbt"] = dict(o)
        return self._c["dbt"]

    # ── canon ──
    @property
    def canon_dirs(self) -> dict:
        """norm(slug) -> slug, entries with a description.md only."""
        if "cdirs" not in self._c:
            self._c["cdirs"] = {norm(p.name): p.name for p in sorted(self.canon_root.iterdir())
                                if p.is_dir() and (p / "description.md").exists()} if self.canon_root.is_dir() else {}
        return self._c["cdirs"]

    @property
    def canon_index(self) -> dict:
        """defName -> slug, from INDEX.md's defName column plus each entry's own '**defName**' line."""
        if "cidx" not in self._c:
            out = {}
            p = self.canon_root / "INDEX.md"
            if p.exists():
                for line in p.read_text().splitlines():
                    m = re.match(r"\|\s*\[([^\]]+)\]\([^)]*\)\s*\|\s*[^|]*\|\s*([^|]*)\|", line)
                    if m:
                        for dn in re.findall(r"[A-Za-z0-9_]+", m.group(2)):
                            out.setdefault(dn, m.group(1))
            for slug in self.canon_dirs.values():
                for line in (self.canon_root / slug / "description.md").read_text(errors="replace").splitlines()[:12]:
                    if line.lower().startswith("**defname"):
                        for dn in re.findall(r"`([A-Za-z0-9_]+)`", line):
                            out.setdefault(dn, slug)
            self._c["cidx"] = out
        return self._c["cidx"]

    def canon_payload(self, slug: str) -> dict:
        d = self.canon_root / slug
        txt = (d / "description.md").read_text(errors="replace")
        secs = {m.group(1).strip().lower(): m.group(2).strip()
                for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", txt, re.S | re.M)}
        imgs = sorted(str(p) for p in d.iterdir() if p.suffix.lower() in IMG_EXT and not p.name.startswith("donor_"))
        return {"slug": slug, "entry": str(d), "images": imgs, "must_show": secs.get("must show", ""),
                "brief": secs.get("visual brief", "")}

    # ── artpipe ──
    @property
    def families(self) -> dict:
        """render family (job id minus facing/_rN) -> sorted job ids, from _artsrc/ dirs and done/ records."""
        if "fams" not in self._c:
            f = defaultdict(set)
            for sub, is_dir in (("_artsrc", True), ("done", False)):
                d = self.artpipe / sub
                if not d.is_dir():
                    continue
                for p in d.iterdir():
                    if is_dir and p.is_dir():
                        f[FAM_RE.sub("", p.name)].add(p.name)
                    elif not is_dir and p.name.endswith(".json") and not p.name.endswith(".manifest.json"):
                        f[FAM_RE.sub("", p.stem)].add(p.stem)
            self._c["fams"] = {k: sorted(v) for k, v in f.items()}
        return self._c["fams"]

    @property
    def job_targets(self) -> dict:
        """Binding fields of every job record (pending/active/done): job id -> {target_def, target_original,
        res}. Only jobs that carry one appear."""
        if "jt" not in self._c:
            out = {}
            paths = []
            if self.read_jobs:
                for sub in ("pending", "active", "done"):
                    d = self.artpipe / sub
                    if d.is_dir():
                        paths += [p for p in d.glob("*.json") if not p.name.endswith(".manifest.json")]

            def rd(p):
                try:
                    j = json.loads(p.read_text())
                except (OSError, ValueError):
                    return None
                td, to = j.get("target_def"), j.get("target_original") or []
                res = j.get("target_texpath") or res_of_dest(j.get("install_to") or "")
                if not (td or to or res):
                    return None
                return j.get("id") or p.stem, {"target_def": td, "target_original": list(to), "res": res}
            with ThreadPoolExecutor(16) as ex:
                for r in ex.map(rd, paths):
                    if r:
                        out[r[0]] = r[1]
            self._c["jt"] = out
            self._c["jobs_read"] = len(paths)
        return self._c["jt"]

    @property
    def collected(self) -> dict:
        """job id -> res, from collected.jsonl (the job's bytes were installed at that texPath)."""
        if "coll" not in self._c:
            out = {}
            p = self.artpipe / "collected.jsonl"
            for line in (p.read_text().splitlines() if p.exists() else []):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                res = res_of_dest(r.get("dest") or "")
                if res and r.get("job_id"):
                    out[r["job_id"]] = res
            self._c["coll"] = out
        return self._c["coll"]

    @property
    def index(self) -> "L.Index":
        if self._index is None:
            self._index = L.Index()
        return self._index

    # ── identity ──
    def identify(self, name: str, extra_originals=()) -> tuple[str, dict]:
        """(our defName, {original name: evidence}). NAME may be ours or an original (donor defName)."""
        D, fwd, back = self._defs()
        ours = name
        originals = {}
        if name not in D and name in fwd:
            ours = fwd[name][0]
            originals[name] = fwd[name][1]
        for o, ev in back.get(ours, {}).items():
            originals.setdefault(o, ev)
        for o in extra_originals or ():
            if o and o != ours:
                originals.setdefault(o, "given by caller")
        return ours, originals


# ───────────────────────────────────────────────────────────── canon ──

def resolve_canon(name: str, world: World | None = None, originals=()) -> dict:
    """-> {subject, originals, match: exact|base-species|none, confidence, slug, entry, images, must_show, evidence,
    searched}. Base-species (variant-stripped name, or a canon creature whose texture this def draws) applies
    to Star Wars-tier and donor names only: an RM_/RUT_ invention drawn with a canon texture is a stand-in, not
    that creature."""
    w = world or World()
    ours, orig = w.identify(name, originals)
    names = [ours] + list(orig)
    label = (w.defs.get(ours) or {}).get("label") or ""
    cidx, cdirs = w.canon_index, w.canon_dirs
    searched = {"INDEX.md defNames": names, "canon dirs (exact)": [], "canon dirs (variant-stripped)": [],
                "texPath twins": [], "sources": {"canon entries": len(cdirs), "INDEX defNames": len(cidx)}}

    def hit(slug, match, conf, ev):
        return dict(w.canon_payload(slug), subject=ours, originals=orig, match=match, confidence=conf,
                    evidence=ev, searched=searched)

    for n in names:
        if n in cidx and norm(cidx[n]) in cdirs:
            return hit(cidx[n], "exact", "bound", f"INDEX.md lists {n} under {cidx[n]}")
    keys = list(dict.fromkeys(k for k in [norm(stem(n)) for n in names] + [norm(label)] if len(k) >= MIN_KEY))
    searched["canon dirs (exact)"] = keys
    for k in keys:
        if k in cdirs:
            return hit(cdirs[k], "exact", "name-matched", f"entry dir {cdirs[k]} == name key {k!r}")
    sw = [n for n in names if not re.match(r"^(RM_|RUT_|rut_)", n)]
    bases = list(dict.fromkeys(b for b in [variant_stripped(n) for n in sw]
                               + ([variant_stripped("".join(x.title() for x in label.split()))] if sw else [])
                               if len(b) >= 3))
    searched["canon dirs (variant-stripped)"] = bases
    for b in bases:
        if b in cdirs:
            return hit(cdirs[b], "base-species", "name-matched", f"variant word dropped: {b!r} -> {cdirs[b]}")
        for dn, slug in sorted(cidx.items()):
            if norm(stem(dn)) == b and norm(slug) in cdirs:
                return hit(slug, "base-species", "name-matched", f"variant word dropped: base def {dn} -> {slug}")
    if sw:
        for n in sw:
            for tp in sorted(w.tex_by_def.get(n, ())):
                for other in sorted(w.def_by_tex.get(tp, ())):
                    if other == n or not other.startswith("RSW_"):
                        continue
                    searched["texPath twins"].append(f"{other} via {tp}")
                    slug = cidx.get(other) or cdirs.get(norm(stem(other)))
                    if slug and norm(slug) in cdirs:
                        return hit(slug, "base-species", "name-matched", f"draws {tp}, the texture of {other} ({slug})")
    return {"subject": ours, "originals": orig, "match": "none", "confidence": "none", "slug": None, "entry": None,
            "images": [], "must_show": "", "evidence": "", "searched": searched}


# ─────────────────────────────────────────────────────────────── art ──

def _role(fam: str) -> str:
    return "nonbody" if NONBODY_RE.search(fam) else "body"


def resolve_art(name: str, world: World | None = None, originals=()) -> dict:
    """-> {subject, originals, texpaths, columns: [{confidence, kind, ref, res, evidence, role}], searched}.
    Bound columns come first; name-matched follow, each naming the key that matched. An empty `columns` is
    'none', and `searched` says what that means."""
    w = world or World()
    ours, orig = w.identify(name, originals)
    tps = sorted(w.tex_by_def.get(ours, set()) | {tp for o in orig for tp in w.tex_by_def.get(o, set())})
    cols, seen = [], set()

    def add(c):
        k = (c["kind"], c["ref"], c.get("res"))
        if k not in seen:
            seen.add(k)
            cols.append(c)

    idx = w.index
    for tp in tps:
        for sha in sorted(idx.by_res.get(tp, ())):
            if idx.is_purged(sha):
                continue
            vs = idx.variants.get(sha, [])
            kinds = sorted({v.get("kind") or "?" for v in vs})
            jobs = sorted({v["job"] for v in vs if v.get("job")})
            add({"confidence": "bound", "kind": "ledger", "ref": sha, "res": tp, "role": "body", "jobs": jobs,
                 "evidence": f"art ledger variant of texPath {tp} ({'/'.join(kinds)})"})
    names = {ours} | set(orig)
    jt = w.job_targets
    bound_jobs = set()
    for jid, t in sorted(jt.items()):
        why = None
        if t["target_def"] in names:
            why = f"job target_def {t['target_def']}"
        elif names & set(t["target_original"]):
            why = f"job target_original {sorted(names & set(t['target_original']))[0]}"
        elif t["res"] and t["res"] in tps:
            why = f"job targets texPath {t['res']}"
        if why:
            bound_jobs.add(jid)
            add({"confidence": "bound", "kind": "job", "ref": FAM_RE.sub("", jid), "job": jid, "res": t["res"],
                 "role": _role(jid), "evidence": why})
    for jid, res in sorted(w.collected.items()):
        if res in tps and jid not in bound_jobs:
            bound_jobs.add(jid)
            add({"confidence": "bound", "kind": "job", "ref": FAM_RE.sub("", jid), "job": jid, "res": res,
                 "role": _role(jid), "evidence": f"collected.jsonl installed it at {res}"})

    # name-matched: whole-token keys over render families
    label = (w.defs.get(ours) or {}).get("label") or ""
    keys = {}
    for n in [ours] + list(orig):
        keys.setdefault(norm(stem(n)), f"stem of {n}")
        v = variant_stripped(n)
        if v:
            keys.setdefault(v, f"variant-stripped stem of {n}")
    if label:
        keys.setdefault(norm(label), f"label {label!r}")
    keys = {k: v for k, v in keys.items() if len(k) >= MIN_KEY}
    bound_fams = {c["ref"] for c in cols if c["kind"] == "job"} | \
        {FAM_RE.sub("", j) for c in cols if c["kind"] == "ledger" for j in c["jobs"]}
    fams = w.families
    for fam in sorted(fams):
        if fam in bound_fams:
            continue
        for k, src in keys.items():
            if token_match(fam, k):
                add({"confidence": "name-matched", "kind": "render", "ref": fam, "res": None, "role": _role(fam),
                     "jobs": fams[fam], "evidence": f"job id token {k!r} ({src})"})
                break
    searched = {"texPaths": tps, "ledger": f"{len(idx.by_res)} texPaths in the art ledger",
                "job records read": w._c.get("jobs_read", 0), "job records carrying a target": len(jt),
                "collected bindings": len(w.collected), "render families": len(fams),
                "name keys (whole-token)": keys, "artpipe": str(w.artpipe)}
    if not w.artpipe.is_dir():
        searched["UNMEASURED"] = f"artpipe state dir {w.artpipe} absent — renders not searched"
    return {"subject": ours, "originals": orig, "texpaths": tps, "columns": cols, "searched": searched}


def resolve(name: str, world: World | None = None, originals=()) -> dict:
    w = world or World()
    a = resolve_art(name, w, originals)
    c = resolve_canon(name, w, originals)
    return {"subject": a["subject"], "originals": a["originals"], "canon": c, "art": a}


def describe_none(searched: dict) -> str:
    """The sentence a sheet prints instead of 'no art' / 'no canon entry'."""
    parts = [f"{k}: {v if not isinstance(v, (list, dict)) else (', '.join(map(str, v)) or '—')}"
             for k, v in searched.items() if k != "sources"]
    return "searched — " + "; ".join(parts) + ". 0 hits."


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="+")
    ap.add_argument("--original", action="append", default=[], help="an original name to carry (repeatable)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    w = World()
    out = [resolve(n, w, a.original) for n in a.names]
    if a.json:
        print(json.dumps(out, indent=1, default=str))
        return 0
    for r in out:
        c, art = r["canon"], r["art"]
        print(f"{r['subject']}  originals={list(r['originals']) or '—'}")
        if c["match"] == "none":
            print(f"  canon: none — {describe_none(c['searched'])}")
        else:
            print(f"  canon: {c['slug']} [{c['match']}, {c['confidence']}] — {c['evidence']}; {len(c['images'])} image(s)")
        n_b = sum(1 for x in art["columns"] if x["confidence"] == "bound")
        n_n = len(art["columns"]) - n_b
        print(f"  art: {n_b} bound, {n_n} name-matched; texPaths {art['texpaths'] or '—'}")
        for x in art["columns"][:12]:
            print(f"    {x['confidence']:12} {x['kind']:6} {x['ref'][:40]:40} {x['evidence']}")
        if not art["columns"]:
            print(f"    none — {describe_none(art['searched'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
