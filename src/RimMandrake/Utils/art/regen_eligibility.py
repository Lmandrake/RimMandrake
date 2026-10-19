#!/usr/bin/env python3
"""regen_eligibility.py — the gate every dregen_ (donor-regeneration) job passes before it is filed.

Owner, 2026-10-19: "I ONLY want art queued that has either confirmed NONE, PLACEHOLDER, or DONOR art. If you can't
confirm one of those three, do not queue. If it was previously regenerated and renamed, do not queue."

A job is ELIGIBLE only when EVERY destination it writes (install_to, or target_def + target_texpath, per facing) is
CONFIRMED one of:
  NONE         no picture anywhere: no file in our src Textures (exact, StandIn/ copy, or case twin), none deployed,
               none served by vanilla or a donor mod, and the ledger never saw a render bound to the path.
  PLACEHOLDER  the bytes are a geometric placeholder (placeholder_detect), on placeholder_allowlist.json, or the
               ledger's provenance says placeholder.
  DONOR        the ledger records the bytes as borrowed (variant kind=donor from a NON-mandrake package, provenance
               kind=donor or standin=true), or the path is served only by vanilla/a donor (donor_retire_census:
               DONOR / DONOR_BUNDLE / DONOR_INACTIVE / VANILLA*).
Everything else is REFUSED, with the reason:
  REFUSED_REGEN        the bytes (searched by content hash, at any path) are a render of ours: artpipe kind, an
                       `art install`, provenance accepted / accepted_for_now / regen, or a bulk-accept live event; or
                       a render is already bound to this def+path; or the path was RENAMED: the def no longer draws it
                       and draws one of our renders now, a case twin holds the picture, or the def name was renamed.
  REFUSED_KEPT         an owner keep (trust=ruled, unreleased) names the bytes. The 2026-10-18 stand-in ruling ("Just
                       put in placeholder art for now or donor copies ...") is an install order, not a keep of the art.
  REFUSED_UNCONFIRMED  anything not proven: unknown provenance, a deployed-only copy of ours, an orphan path no def
                       draws, an unreadable file.
Fail closed: if the gate cannot be built (ledger, game-texture index, XML scan), `Gate()` raises GateError and the
caller files NOTHING.

    python3 src/RimMandrake/Utils/art/regen_eligibility.py classify --jobs <jobs.json>... [--failed] [--out <md>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

REPO = HERE.parents[3]
TEXTAGS = {"texPath", "texturePath", "uiIconPath", "wornGraphicPath", "flyingAnimationFramePathPrefix",
           "flyingAnimationFramePathPrefixFemale", "iconPath", "graphicPath", "texPathFemale"}
FACINGS = ("north", "south", "east", "west")
ELIGIBLE = ("NONE", "PLACEHOLDER", "DONOR")
REFUSED = ("REFUSED_KEPT", "REFUSED_REGEN", "REFUSED_UNCONFIRMED")
RANK = {"REFUSED_REGEN": 0, "REFUSED_KEPT": 1, "REFUSED_UNCONFIRMED": 2, "NONE": 3, "PLACEHOLDER": 4, "DONOR": 5}
STANDIN_RULING = "Just put in placeholder art for now or donor copies"
DONOR_CENSUS = {"DONOR", "DONOR_BUNDLE", "DONOR_INACTIVE", "VANILLA", "VANILLA_RETEXTURED", "VANILLA_UNINDEXED"}
REGEN_PROV = ("accepted", "accepted_for_now", "regen")
OWN_PKG = "mandrake."


class GateError(RuntimeError):
    """The gate could not be built or could not judge: the caller files nothing."""


def strip_facing(stem: str) -> str:
    return re.sub(r"_(north|south|east|west)$", "", stem)


def low(s: str) -> str:
    return s.replace("\\", "/").strip("/").lower()


_STANDIN = re.compile(r"^standin/", re.I)


def unstandin(s: str) -> str:
    """Drop a leading StandIn/ in ANY case: Windows resolves Textures/standin/Foo and Textures/StandIn/Foo to one file
    (GPT review 2026-10-19 #1)."""
    return _STANDIN.sub("", s.replace("\\", "/").strip("/"))


def key(s: str) -> str:
    """The case-insensitive, StandIn-free form every path comparison in this gate uses."""
    return low(unstandin(s))


_LOC = re.compile(r"(?:^git:[0-9a-f]+:)?.*?/Textures/(.+)\.png$", re.I)


def res_of_variant(v: dict) -> str | None:
    """The texture res a ledger variant was registered at: `res`, else derived from `loc` (facing stripped)."""
    if v.get("res"):
        return v["res"]
    m = _LOC.match((v.get("loc") or "").replace("\\", "/"))
    return strip_facing(m.group(1)) if m else None


def own_path(ext_tp: str, dn: str) -> str:
    """Where bulk_accept_renders puts a render for a def that drew a vanilla/donor path (same rule, kept in sync)."""
    parts = ext_tp.strip("/").split("/")
    if len(parts) >= 2 and parts[-1].lower().startswith(parts[-2].lower()):
        parts[-2] = parts[-1] = dn
    else:
        parts[-1] = dn + "/" + dn
    return "/".join(parts)


class Gate:
    """Built once per run. Every dependency is injectable so the selftest can drive it on a fake repo."""

    def __init__(self, repo: Path | None = None, idx=None, game_classify=None, game_file=None,
                 placeholder_reason=None, allowlist: dict | None = None):
        # what fresh() needs to rebuild this gate from the CURRENT disk and ledger (GPT review 2026-10-19 #5)
        self._args = dict(repo=repo, idx=idx, game_classify=game_classify, game_file=game_file,
                          placeholder_reason=placeholder_reason, allowlist=allowlist)
        try:
            self.repo = Path(repo or REPO)
            if idx is None:
                import artledger as A
                idx = A.Index()                       # a fresh read of every shard, never the process cache
            elif callable(idx):
                idx = idx()                           # a factory (selftest): called anew by every fresh()
            self.idx = idx
            if game_classify is None or game_file is None:
                gc, gf = self._game()
                game_classify = game_classify or gc
                game_file = game_file or gf
            self.game_classify = game_classify          # res -> {"cat": ..., "by": ..., "file": ...}
            self.game_file = game_file                  # res -> [(packageId, path)] copies the game can read
            if placeholder_reason is None:
                import placeholder_detect as PD
                placeholder_reason = PD.placeholder_reason
            self.placeholder_reason = placeholder_reason
            if allowlist is None:
                p = HERE / "placeholder_allowlist.json"
                allowlist = json.loads(p.read_text()) if p.is_file() else {"entries": []}
            self.ph_paths = {e["path"] for e in allowlist.get("entries", [])}
            self.ph_shas = {e.get("sha256") for e in allowlist.get("entries", []) if e.get("sha256")}
            self._scan()
            self._ledger()
        except GateError:
            raise
        except Exception as e:                                       # noqa: BLE001
            raise GateError(f"eligibility gate could not be built: {type(e).__name__}: {e}") from e

    def fresh(self) -> "Gate":
        """A new gate built from the disk and ledger as they are NOW. Callers re-judge every row with it immediately
        before publishing a job, so a render installed after this gate was built cannot be queued over (#5).
        Raises GateError like the constructor."""
        return Gate(**self._args)

    def recheck(self, rows) -> tuple[list, list]:
        """-> (rows still eligible under a fresh gate, verdicts of rows it now refuses)."""
        g = self.fresh()
        ok, gone = [], []
        for r in rows:
            v = g.classify(r)
            (ok if v["eligible"] else gone).append(r if v["eligible"] else v)
        return ok, gone

    # ───────────────────────────────────────────────────────────── building ──

    @staticmethod
    def _game():
        import gametex as G
        import donor_retire_census as DRC
        ix = G.index()

        def classify(res):
            return DRC.classify(res, ix)

        def files(res):
            r = G.resolve_res(res, ix)
            return [(c.get("packageId") or "", p) for c in r["copies"] for p in c["faces"].values()]
        return classify, files

    def _scan(self):
        src = self.repo / "src"
        self.tex = {}                                 # 'mod/rel' (as on disk, no .png) -> Path
        self.tex_low = defaultdict(list)              # key(rel) (lowercased, no .png, no StandIn/) -> ['mod/Textures/rel']
        self.tex_ci = defaultdict(list)               # 'mod/Textures/rel' lowercased -> ['mod/Textures/rel'] (Windows)
        for troot in src.glob("*/*/Textures"):
            mod = troot.parent.relative_to(self.repo).as_posix()
            for p in troot.rglob("*"):
                if p.suffix.lower() != ".png" or not p.is_file():
                    continue
                rel = p.relative_to(troot).as_posix()[:-4]
                self.tex[f"{mod}/Textures/{rel}"] = p
                self.tex_low[key(rel)].append(f"{mod}/Textures/{rel}")
                self.tex_ci[f"{mod}/Textures/{rel}".lower()].append(f"{mod}/Textures/{rel}")
        self.drawn = defaultdict(set)                 # texture text lowercased -> {defName or xml file}
        self.def_tex = defaultdict(set)               # defName -> {texture texts} (our own defs)
        self.def_draws = defaultdict(set)             # defName -> {key(texture)}: its own XML, its PawnKindDefs, and
        #                                               patches whose xpath names it (#4: per-target-def attribution)
        for x in src.rglob("*.xml"):
            r = x.relative_to(self.repo).as_posix()
            if "/textures/" in r.lower():
                continue
            try:
                root = ET.parse(x).getroot()
            except (ET.ParseError, OSError) as e:      # fail closed (#17): an incomplete scan judges nothing
                raise GateError(f"XML scan failed on {r}: {type(e).__name__}: {e}") from e
            for op in root.iter():
                xp = op.find("xpath") if isinstance(op.tag, str) else None
                if xp is None or not (xp.text or "").strip():
                    continue
                for name in re.findall(r"defName\s*=\s*[\"']([^\"']+)[\"']", xp.text):
                    for el in op.iter():
                        if isinstance(el.tag, str) and el.tag in TEXTAGS and (el.text or "").strip() and not list(el):
                            self.def_draws[name].add(key(el.text))
            for d in root.iter():
                dn = (d.findtext("defName") or "").strip() if isinstance(d.tag, str) else ""
                for el in d:
                    if isinstance(el.tag, str) and el.tag in TEXTAGS and (el.text or "").strip() and not list(el):
                        self.drawn[low(el.text)].add(r)
                if not dn:
                    continue
                race = (d.findtext("race") or "").strip() if d.tag == "PawnKindDef" else ""
                for el in d.iter():
                    if isinstance(el.tag, str) and el.tag in TEXTAGS and (el.text or "").strip() and not list(el):
                        self.def_tex[dn].add(el.text.strip())
                        self.drawn[low(el.text)].add(dn)
                        self.def_draws[dn].add(key(el.text))
                        if race:
                            self.def_draws[race].add(key(el.text))

    def _ledger(self):
        idx = self.idx
        self.regen_sha, self.donor_sha, self.install_sha, self.ph_sha = {}, {}, {}, {}
        for sha, vs in idx.variants.items():
            for v in vs:
                pv = v.get("provenance") or {}
                k = v.get("kind")
                pkg = (v.get("donor_pkg") or pv.get("donor_pkg") or "").lower()
                if k == "artpipe" or pv.get("kind") == "artpipe" or any(pv.get(f) for f in REGEN_PROV):
                    self.regen_sha.setdefault(sha, f"ledger variant {v.get('id')} kind={k} job={v.get('job') or pv.get('job')}")
                elif (k == "donor" and not pkg.startswith(OWN_PKG)) or pv.get("kind") == "donor" or pv.get("standin"):
                    self.donor_sha.setdefault(sha, f"ledger variant {v.get('id')} donor {pkg or pv.get('orig_texpath') or ''}".strip())
                elif k == "install":
                    self.install_sha.setdefault(sha, f"ledger variant {v.get('id')} kind=install ({v.get('loc')})")
                if pv.get("placeholder") or "placeholder" in str(pv.get("kind") or ""):
                    self.ph_sha.setdefault(sha, f"ledger variant {v.get('id')} provenance placeholder")
        for (m, r), ev in idx.live.items():
            why = ev.get("reason") or ""
            if ev.get("sha") and ("bulk accept" in why or why.startswith("artpipe-collect")):
                self.regen_sha.setdefault(ev["sha"], f"ledger live {m}/Textures/{r}: {why[:60]}")
        # regeneration HISTORY: renders of ours and installed art of ours (kind=install, #7), placeholders excepted
        self.history_sha = dict(self.regen_sha)
        for s, why in self.install_sha.items():
            if s not in self.ph_sha and s not in self.ph_shas:
                self.history_sha.setdefault(s, why)
        # renders bound to a def+path (a finished render waiting to install, or one installed then moved)
        self.bound = defaultdict(list)                # (subject key lowercased, key(texpath)) -> [why]
        self.bound_subject = defaultdict(list)        # subject key lowercased -> [(key(texpath), why)]
        for sha, bs in idx.bindings.items():
            if sha not in self.history_sha:
                continue
            for b in bs:
                tp = key(b.get("texpath") or "")
                subj = (b.get("subject") or "")
                self.bound[(subj.lower(), tp)].append(f"binding {b.get('id')} job {b.get('job')}")
                self.bound_subject[subj.lower()].append((tp, f"binding {b.get('id')} job {b.get('job')}"))
        self.by_res_regen = defaultdict(list)         # key(res) -> [why]: a render of ours was once registered there
        for sha, vs in idx.variants.items():
            if sha not in self.history_sha:
                continue
            for v in vs:
                res = res_of_variant(v)
                if res:
                    self.by_res_regen[key(res)].append(self.history_sha[sha])
        for res, shas in idx.by_res.items():
            for s in shas:
                if s in self.history_sha:
                    self.by_res_regen[key(res)].append(self.history_sha[s])
        for (m, r), ev in idx.live.items():           # installed (live) now or before, at any spelling
            if ev.get("sha") in self.history_sha:
                self.by_res_regen[key(strip_facing(r[:-4] if r.lower().endswith(".png") else r))].append(
                    f"ledger live {m}/Textures/{r}")

    # ───────────────────────────────────────────────────────────── judging ──

    def kept(self, sha: str) -> str | None:
        ks = [k for k in self.idx.protected(sha) if not (k.get("said") or "").startswith(STANDIN_RULING)]
        if not ks:
            return None
        k = ks[-1]
        return f"owner keep {k.get('id')} via {Path(k.get('via') or '').name or '?'} said {(k.get('said') or '')[:60]!r}"

    def judge_bytes(self, b: bytes, where: str) -> tuple[str, str]:
        sha = hashlib.sha256(b).hexdigest()
        if sha in self.regen_sha:
            return "REFUSED_REGEN", f"{where}: bytes are a render of ours ({self.regen_sha[sha]})"
        k = self.kept(sha)
        if k:
            return "REFUSED_KEPT", f"{where}: {k}"
        if sha in self.ph_shas or where in self.ph_paths or sha in self.ph_sha:
            return "PLACEHOLDER", f"{where}: placeholder (allowlist/ledger)"
        try:
            why = self.placeholder_reason(b)
        except Exception as e:                                        # noqa: BLE001
            return "REFUSED_UNCONFIRMED", f"{where}: unreadable ({type(e).__name__}); placeholder test UNMEASURED"
        if why:
            return "PLACEHOLDER", f"{where}: {why}"
        if sha in self.donor_sha:
            return "DONOR", f"{where}: {self.donor_sha[sha]}"
        if sha in self.install_sha:
            return "REFUSED_REGEN", f"{where}: installed art of ours, not a donor copy ({self.install_sha[sha]})"
        return "REFUSED_UNCONFIRMED", f"{where}: sha {sha[:12]} has no donor/placeholder provenance in the ledger"

    @staticmethod
    def _cands(rel: str) -> set:
        return {key(rel), key(strip_facing(rel)), key(rel.rsplit("/", 1)[0])}

    def _drawn(self, rel: str) -> bool:
        """Some def or patch of ours draws this path (any def)."""
        return any(c in self.drawn or low("StandIn/" + c) in self.drawn for c in self._cands(rel))

    def _drawn_by(self, dn: str, rel: str) -> bool:
        """THE TARGET DEF draws this path (its XML, its PawnKindDefs, or a patch naming it): #4."""
        return bool(self._cands(rel) & self.def_draws.get(dn, set()))

    def _renamed(self, dn: str, rel: str) -> str | None:
        """A render for this def+path exists in the ledger, or the def now draws a render of ours elsewhere."""
        r0 = key(strip_facing(rel))
        for k in sorted({key(rel), r0}):
            if self.by_res_regen.get(k):
                return f"a render was registered at {k} ({self.by_res_regen[k][0]})"
        if dn:
            for tp, why in self.bound_subject.get(dn.lower(), ()):
                if tp in (key(rel), r0):
                    return f"a render is bound to {dn} at {tp} ({why})"
        return None

    def _def_alias(self, dn: str) -> str | None:
        """The def is gone from our XML: renamed? (subject aliases, renders bound to the old or new subject)."""
        if not dn or dn in self.def_tex:
            return None
        try:
            import artledger as A
            canon = A.canonical_subject(A.subject_key(dn))
        except Exception:                                              # noqa: BLE001
            canon = dn.lower()
        hits = [s for s in self.bound_subject if s.lower() == dn.lower()]
        if hits:
            return f"def {dn} no longer exists and renders are bound to it ({self.bound_subject[hits[0]][0][1]})"
        return f"def {dn} no longer exists in our XML (subject {canon}): renamed or removed"

    def _def_now_regen(self, dn: str) -> str | None:
        for t in sorted(self.def_tex.get(dn, ())):
            t2 = unstandin(t)
            for k in (t2, t2 + "_east", t2 + "_south", t2 + "_north", t2 + "_west"):
                for path in self.tex_low.get(key(k), ()):
                    sha = hashlib.sha256(self.tex[path].read_bytes()).hexdigest()
                    if sha in self.history_sha:
                        return f"{dn} now draws {path}.png, a render of ours"
            for path, p in self.tex.items():                          # Graphic_Random folder
                if key(path.split("/Textures/", 1)[1]).startswith(key(t2) + "/"):
                    if hashlib.sha256(p.read_bytes()).hexdigest() in self.history_sha:
                        return f"{dn} now draws folder {t2} holding a render of ours ({path}.png)"
        return None

    def _judge_all(self, paths, why_prefix: str = "") -> list[tuple[str, str]]:
        return [(c, why_prefix + w) for c, w in
                (self.judge_bytes(self.tex[q].read_bytes(), q + ".png") for q in sorted(set(paths)))]

    def slot_install(self, dest: str, dn: str) -> tuple[str, str]:
        d = dest.replace("\\", "/").lstrip("/")
        dl = d.lower()
        if not dl.startswith("src/") or "/textures/" not in dl or not dl.endswith(".png"):
            return "REFUSED_UNCONFIRMED", f"{dest}: not a src/<mod>/Textures/<rel>.png path"
        i = dl.index("/textures/")
        mod, rel = d[:i], unstandin(d[i + len("/textures/"):-4])     # any-case StandIn/ (#1)
        alias = self._def_alias(dn)
        if alias:
            return "REFUSED_REGEN" if "bound" in alias else "REFUSED_UNCONFIRMED", alias
        if not self._drawn_by(dn, rel):                              # #4: the TARGET def must draw it
            nr = self._def_now_regen(dn)
            if nr:
                return "REFUSED_REGEN", f"{rel}: renamed — {dn} no longer draws it; {nr}"
            if self._drawn(rel):
                return "REFUSED_UNCONFIRMED", f"{rel}: drawn by another def of ours, not by {dn}"
            return "REFUSED_UNCONFIRMED", f"{rel}: no def of ours draws this path (orphan or drawn from C#)"
        rn = self._renamed(dn, rel)                                  # #3: history before any file match
        if rn:
            return "REFUSED_REGEN", f"{rel}: {rn}"
        exact = f"{mod}/Textures/{rel}"
        standin = f"{mod}/Textures/StandIn/{rel}"
        here = set(self.tex_ci.get(exact.lower(), ())) | set(self.tex_ci.get(standin.lower(), ()))
        twins = {q for q in here if q not in (exact, standin)}       # another case spelling: the same file on Windows
        others = {q for q in self.tex_low.get(key(rel), ()) if q not in here}   # another mod of ours, same texPath
        res = self._judge_all(here) + self._judge_all(others, f"same texPath shipped by another mod of ours: ")
        if res:
            cls, why = min(res, key=lambda x: RANK[x[0]])            # every copy must be confirmed (#6)
            if cls == "REFUSED_REGEN" and twins:
                return cls, f"renamed/case twin: {why}"
            if cls in ELIGIBLE and twins:
                return "REFUSED_UNCONFIRMED", f"{exact}.png exists under another case spelling ({sorted(twins)[0]}.png, {cls})"
            if not here:
                why = f"no file at {exact}.png; {why}"
            return cls, why
        return self._game_side(rel, f"{exact}.png")

    def _game_side(self, rel: str, where: str) -> tuple[str, str]:
        res = strip_facing(rel)
        fac = rel[len(res) + 1:] if rel != res else ""
        c = self.game_classify(res)
        cat = c.get("cat")
        if cat == "MISSING":
            return "NONE", f"{where}: no picture in our src, deployed mods, vanilla or donors"
        if cat in DONOR_CENSUS:
            return "DONOR", f"{where}: the game serves {res} from {c.get('by')} ({cat})"
        if cat == "OURS":
            own = [p for pkg, p in self.game_file(res) if pkg.lower().startswith(OWN_PKG)]
            if fac:                                  # judge THIS facing's copies when the game has them (#6)
                same = [p for p in own if Path(str(p)).stem.lower().endswith("_" + fac.lower())]
                own = same or own
            out = []
            for p in own:                            # every copy, every package: the worst decides (#6)
                try:
                    b = Path(p).read_bytes()
                except OSError as e:
                    return "REFUSED_UNCONFIRMED", f"{where}: deployed copy unreadable ({e})"
                out.append(self.judge_bytes(b, f"deployed {p}"))
            if out:
                return min(out, key=lambda x: RANK[x[0]])
            return "REFUSED_UNCONFIRMED", f"{where}: the game serves an OURS copy that could not be located"
        return "REFUSED_UNCONFIRMED", f"{where}: game-texture class {cat!r}"

    def slot_external(self, dn: str, tp: str, facing: str) -> tuple[str, str]:
        t = unstandin(tp.strip())
        suf = f"_{facing}" if facing in FACINGS else ""
        alias = self._def_alias(dn)
        if alias:
            return "REFUSED_REGEN" if "bound" in alias else "REFUSED_UNCONFIRMED", alias
        if key(t) not in self.def_draws.get(dn, set()):
            nr = self._def_now_regen(dn)
            if nr:
                return "REFUSED_REGEN", f"{dn} no longer draws {t}: renamed — {nr}"
            return "REFUSED_UNCONFIRMED", f"{dn} no longer draws {t} (now: {', '.join(sorted(self.def_tex.get(dn, ())))[:120]})"
        op = own_path(t, dn)
        for cand in (op, t):
            rn = self._renamed(dn, cand + suf)
            if rn:
                return "REFUSED_REGEN", rn
        # the EVENTUAL destination (where the installer will write): ANY refusal there refuses the job (#2)
        res = self._judge_all(self.tex_low.get(key(op + suf), ()), "our own path (the eventual destination): ")
        ours = self.tex_low.get(key(t + suf), ())
        res += self._judge_all(ours)                                  # every copy of ours, not the first (#6)
        if not ours:
            folder = [q for q in self.tex if key(q.split("/Textures/", 1)[1]).startswith(key(t) + "/")]
            res += self._judge_all(folder)
            if not folder:
                res.append(self._game_side(t + suf, f"{dn}:{t}{suf}"))
        return min(res, key=lambda x: RANK[x[0]])

    def slots(self, row: dict) -> list[tuple[str, tuple]]:
        dn = row.get("target_def") or ""
        if row.get("facing") in FACINGS:
            fac = [row["facing"]]
        else:
            fac = [f for f in (row.get("facings") or []) if f in FACINGS]
        out = []
        it = row.get("install_to")
        if it:
            if "{facing}" in it:
                for f in fac or ["east", "south", "north"]:
                    out.append((f, ("install", it.replace("{facing}", f), dn)))
            else:
                out.append((row.get("facing") or "single", ("install", it, dn)))
        elif row.get("target_texpath"):
            for f in fac or ["single"]:
                out.append((f, ("external", dn, row["target_texpath"], f)))
        return out

    def classify(self, row: dict) -> dict:
        """-> {id, verdict, eligible, slots: [(facing, verdict, reason)], reason}. Never raises for one row: an error
        on a row is REFUSED_UNCONFIRMED with the exception named."""
        res = []
        try:
            ss = self.slots(row)
            if not ss:
                res.append(("-", "REFUSED_UNCONFIRMED", "row names no install_to and no target_texpath"))
            for f, s in ss:
                cls, why = self.slot_install(s[1], s[2]) if s[0] == "install" else self.slot_external(s[1], s[2], s[3])
                res.append((f, cls, why))
        except Exception as e:                                         # noqa: BLE001
            res.append(("-", "REFUSED_UNCONFIRMED", f"classifier error {type(e).__name__}: {e}"))
        worst = min(res, key=lambda x: RANK[x[1]])
        verdict = worst[1]
        return {"id": row.get("id"), "target_def": row.get("target_def"), "verdict": verdict,
                "eligible": verdict in ELIGIBLE, "slots": res, "reason": worst[2]}


def filter_rows(rows, gate: Gate | None = None):
    """-> (eligible rows, [verdicts of refused rows], {id: verdict}). Raises GateError when the gate cannot be built."""
    gate = gate or Gate()
    ok, refused, all_v = [], [], {}
    for r in rows:
        v = gate.classify(r)
        all_v[r.get("id")] = v
        (ok if v["eligible"] else refused).append(r if v["eligible"] else v)
    return ok, refused, all_v


# ─────────────────────────────────────────────────────────────── report ──

def _failed_jobs(art: Path):
    out = []
    for f in sorted((art / "failed").glob("dregen_*.json")):
        if f.name.endswith(".manifest.json"):
            continue
        j = json.loads(f.read_text())
        m = art / "failed" / (f.stem + ".manifest.json")
        note = ""
        if m.is_file():
            mm = json.loads(m.read_text())
            tail = json.dumps(mm)
            note = "429" if "429" in tail else ("derived" if "derivation impossible" in tail else "other")
        j["_cause"] = note
        out.append(j)
    return out


TAGS = [("bytes are a render of ours", "render of ours at the destination (hash)"),
        ("installed art of ours", "installed art of ours (not a donor copy)"),
        ("renamed", "renamed: the def now draws a render of ours elsewhere"),
        ("a render is bound", "a finished render is already bound to this def+path"),
        ("a render was registered", "a render was registered at this path before"),
        ("owner keep", "owner keep on the bytes"),
        ("no donor/placeholder provenance", "bytes of unknown provenance"),
        ("case spelling", "case twin of the destination"),
        ("no def of ours draws", "orphan path: no def draws it"),
        ("no longer draws", "def no longer draws the job's texpath"),
        ("no longer exists", "def no longer exists"),
        ("the game serves", "vanilla/donor serves the path (census)"),
        ("ledger variant", "donor bytes per ledger"),
        ("placeholder", "geometric placeholder"),
        ("no picture in our src", "nothing anywhere")]


def tag(v) -> str:
    r = v["reason"]
    t = next((t for k, t in TAGS if k in r), "other: " + r[:60])
    if "another mod of ours" in r:
        t += " (via another mod's copy)"
    return f"{v['verdict']}: {t}"


def report(jobs_ps, out: Path, art: Path):
    gate = Gate()
    lines = ["# dregen_ eligibility, 2026-10-19 (src/RimMandrake/Utils/art/regen_eligibility.py)", "",
             'Owner, 2026-10-19: "I ONLY want art queued that has either confirmed NONE, PLACEHOLDER, or DONOR art. '
             'If you can\'t confirm one of those three, do not queue. If it was previously regenerated and renamed, '
             'do not queue."', "",
             "Measured against today's src/, the art ledger, and the game-texture index. A row is eligible only if "
             "every facing it writes is confirmed. Nothing was filed or requeued.", ""]
    allc = Counter()
    unclass = []
    for jp in jobs_ps:
        J = json.loads(Path(jp).read_text())
        vs = [gate.classify(r) for r in J["rows"]]
        c = Counter(v["verdict"] for v in vs)
        allc.update(c)
        lines += [f"## {Path(jp).name}: {len(vs)} rows", "", "| class | rows |", "|---|---:|"]
        lines += [f"| {k} | {c.get(k, 0)} |" for k in ELIGIBLE + REFUSED] + [""]
        why = Counter(tag(v) for v in vs)
        lines += ["By reason:", ""] + [f"- {n} × {w}" for w, n in sorted(why.items())] + [""]
        unclass += [v for v in vs if v["verdict"] == "REFUSED_UNCONFIRMED"]
    lines += ["## All job lists together", "", "| class | rows |", "|---|---:|"]
    lines += [f"| {k} | {allc.get(k, 0)} |" for k in ELIGIBLE + REFUSED] + [""]
    fj = _failed_jobs(art)
    fv = [(j, gate.classify(j)) for j in fj]
    fc = Counter(v["verdict"] for _, v in fv)
    cc = Counter(j["_cause"] for j in fj)
    lines += [f"## The failed dregen_ jobs: {len(fj)} job files in failed/ (causes: "
              + ", ".join(f"{k or 'no manifest'} {n}" for k, n in cc.most_common()) + ")", "",
              "| class | jobs |", "|---|---:|"] + [f"| {k} | {fc.get(k, 0)} |" for k in ELIGIBLE + REFUSED] + [""]
    fw = Counter(tag(v) for _, v in fv)
    lines += ["By reason:", ""] + [f"- {n} × {w}" for w, n in sorted(fw.items())] + [""]
    el = [(j, v) for j, v in fv if v["eligible"]]
    lines += [f"### Eligible to requeue (dry run, NOT filed): {len(el)}", "", "| job | cause | class | why |",
              "|---|---|---|---|"]
    lines += [f"| `{j['id']}` | {j['_cause']} | {v['verdict']} | {v['reason'][:110]} |" for j, v in el] + [""]
    lines += [f"### Refused: {len(fv) - len(el)}", "", "| job | class | why |", "|---|---|---|"]
    lines += [f"| `{j['id']}` | {v['verdict']} | {v['reason'][:130]} |" for j, v in fv if not v["eligible"]] + [""]
    lines += ["## Destinations that could not be classified (REFUSED_UNCONFIRMED, job lists)", "",
              "| row | why |", "|---|---|"]
    lines += [f"| `{v['id']}` | {v['reason'][:150]} |" for v in unclass] + [""]
    out.write_text("\n".join(lines))
    print(f"job lists: {dict(allc)}; failed: {dict(fc)}; eligible failed {len(el)}/{len(fj)}; wrote {out}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("classify")
    c.add_argument("--jobs", nargs="+", required=True, type=Path)
    c.add_argument("--out", required=True, type=Path)
    c.add_argument("--artpipe", type=Path, default=None)
    a = ap.parse_args(argv)
    import bulk_accept_renders as BA
    try:
        report(a.jobs, a.out, a.artpipe or BA.ART)
    except GateError as e:
        print(f"GATE FAILED, nothing judged: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
