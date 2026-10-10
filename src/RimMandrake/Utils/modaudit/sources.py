#!/usr/bin/env python3
"""modaudit/sources.py - is a mod's source available, and where?  (stage 0 of the mod audit)

    python3 src/RimMandrake/Utils/modaudit/sources.py --budget 240             # extract + verify; resumable
    python3 src/RimMandrake/Utils/modaudit/sources.py --budget 240 --search    # also search GitHub for mods with no URL

Candidates come from what the mod itself says: About.xml <url> and <description>, its README files, and any
.git/config remote in its folder. Patterns: github.com/<owner>/<repo>, gitlab.com/..., codeberg.org/...,
bitbucket.org/..., and the Steam workshop page (from PublishedFileId / workshop folder).

VERIFY is a `gh api repos/<owner>/<repo>` call (public metadata: full_name, license, pushed_at, archived) - capped
per run by --max-requests and cached in ~/.cache/rm_modaudit/gh.json, so a re-run never re-asks. A profile URL
(github.com/<owner> with no repo) is recorded as a candidate, not verified. If the network refuses, the row says
UNVERIFIED, never "no source".

--search (optional, rate-limited to the search API's 30/min) runs `gh search repos "<mod name>" rimworld` for
third-party mods with no candidate and records the top hit as source_kind "github-search" with confidence LOW -
a name match, not proof; an assessor must confirm it.

source_kind: ours | ships-source | github | gitlab | other-git | github-search | steam-only | none
confidence:  MEASURED (verified repo the mod itself links) | INFERRED (link in the mod, unverified, or a search hit)
             | UNVERIFIED (network refused)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
CACHE = os.path.expanduser("~/.cache/rm_modaudit/gh.json")
OUT = os.path.expanduser("~/.cache/rm_modaudit/sources.json")

RX_HOST = re.compile(r"(?:https?://)?(?:www\.)?(github\.com|gitlab\.com|codeberg\.org|bitbucket\.org)/"
                     r"([A-Za-z0-9_.-]+)(?:/([A-Za-z0-9_.-]+))?", re.I)
NOT_OWNERS = {"sponsors", "orgs", "settings", "features", "about", "topics", "marketplace", "login", "issues"}
NOT_REPOS = {"issues", "wiki", "releases", "pulls", "tree", "blob", "archive"}


def extract(text):
    """[(host, owner, repo|None)] from free text, de-duplicated, order kept. Pure; selftested."""
    out, seen = [], set()
    for m in RX_HOST.finditer(text or ""):
        host, owner, repo = m.group(1).lower(), m.group(2), m.group(3)
        if owner.lower() in NOT_OWNERS:
            continue
        if repo:
            repo = re.sub(r"\.git$", "", repo).rstrip(".")
            if not repo or repo.lower() in NOT_REPOS:
                repo = None
        key = (host, owner.lower(), (repo or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append((host, owner, repo))
    return out


_STOP = {"rimworld", "rw", "mod", "mods", "the", "for", "and", "of", "a", "an", "continued", "unofficial", "updated",
         "redux", "edition", "framework_", "1", "16", "15", "14", "v1"}
_SIDECAR = {"patch", "patches", "compat", "compatibility", "checker", "addon", "addons", "fix", "fixes", "translation",
            "translations", "template", "example", "examples", "tools", "test", "tests", "localization"}
_LIBS = {("pardeike", "harmony"): "brrainz.harmony", ("pardeike", "harmonyrimworld"): "brrainz.harmony"}


def name_tokens(s):
    """'RimworldHugsLib-Checker 1.6' -> {'hugs','lib','checker'}. Pure; selftested."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s or "")
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    toks = {t for t in re.split(r"[^a-z0-9]+", s.lower()) if t and t not in _STOP and not t.isdigit()}
    return {t[:-1] if len(t) > 3 and t.endswith("s") and not t.endswith("ss") else t for t in toks}


def resembles(mod_name, repo):
    """True when a repo NAME plausibly is this mod: token Jaccard >= 0.5 and no sidecar word (patch, checker,
    compat, ...) the mod name lacks. Pure; selftested."""
    a, b = name_tokens(mod_name), name_tokens(repo)
    if not a or not b:
        return False
    if (b - a) & _SIDECAR:
        return False
    return len(a & b) / float(len(a | b)) >= 0.5


def reject_reason(pid, mod_name, owner, repo, via_search=False):
    """None when a candidate repo may stand as this mod's source, else why not. Pure; selftested.
    Rejects shared-library repos named in READMEs/descriptions (Harmony, Publicise, MonoMod), wiki repos, and
    (for search hits) repos whose name does not resemble the mod's."""
    o, r = (owner or "").lower(), (repo or "").lower()
    lib = _LIBS.get((o, r))
    if lib and pid != lib:
        return "shared library repo %s/%s, not this mod (only %s is Harmony)" % (owner, repo, lib)
    if o == "rwmt" and r == "publicise":
        return "build tool repo rwmt/Publicise, not this mod"
    if o == "monomod":
        return "MonoMod library repo, not this mod"
    if "wiki" in r:
        return "wiki repo, not source"
    if via_search and not resembles(mod_name, repo):
        return "search hit whose repo name does not resemble the mod name %r" % mod_name
    return None


SEARCHED_WHERE = "about.url, about.description, README files, .git/config"


def reselect(rec, pid, mod_name, cls, ships_source, search_hits=None):
    """Re-judge a cached sources.json record offline (no network) -> a corrected copy. Pure; selftested.
    Every candidate gets verify.status REJECTED + reject_reason when it fails reject_reason(); selection falls
    through to the next candidate, to the mod's own shipped source, to the next resembling search hit, or to
    steam-only/none. A NOT_FOUND repo is never the source. Found-nothing is INFERRED, never MEASURED."""
    import copy
    rec = copy.deepcopy(rec or {"packageId": pid, "candidates": []})
    if cls in ("OURS", "CORE_DLC"):
        return rec
    for k in ("source_url", "license", "last_push", "archived", "verify_status", "search_note", "note"):
        rec.pop(k, None)
    rec.update(source_url=None, source_kind="none", license=None, last_push=None, archived=None, confidence="INFERRED")
    rejected = []
    for c in rec.get("candidates") or []:
        if not c.get("repo"):
            continue
        why = reject_reason(pid, mod_name, c["owner"], c["repo"])
        if why:
            c["verify"] = dict(c.get("verify") or {}, status="REJECTED", reject_reason=why)
            rejected.append("%s/%s" % (c["owner"], c["repo"]))
    for c in rec.get("candidates") or []:
        v = c.get("verify") or {}
        if c.get("host") == "github.com" and c.get("repo") and v.get("status") == "VERIFIED":
            rec.update(source_url=v.get("html_url"), source_kind="github", license=v.get("license"),
                       last_push=v.get("pushed_at"), archived=v.get("archived"), confidence="MEASURED")
            break
    if rec["source_url"] is None:
        for c in rec.get("candidates") or []:
            st = (c.get("verify") or {}).get("status")
            if c.get("repo") and st not in ("REJECTED", "NOT_FOUND"):
                rec["source_url"] = "https://%s/%s/%s" % (c["host"], c["owner"], c["repo"])
                rec["source_kind"] = "github" if c["host"] == "github.com" else (
                    "gitlab" if c["host"] == "gitlab.com" else "other-git")
                rec["confidence"] = "UNVERIFIED" if st in (None, "UNVERIFIED") else "INFERRED"
                rec["verify_status"] = st or "NOT_ASKED (budget)"
                break
    nf = ["%s/%s" % (c["owner"], c["repo"]) for c in rec.get("candidates") or []
          if c.get("repo") and (c.get("verify") or {}).get("status") == "NOT_FOUND"]
    if rec["source_url"] is None and ships_source:
        rec.update(source_kind="ships-source", source_url="(C# source inside the mod folder)", confidence="MEASURED")
    searched = SEARCHED_WHERE
    if rec["source_url"] is None and search_hits is not None:
        searched += ", gh search for the mod name"
        for h in search_hits:
            repo = (h.get("fullName") or "/").split("/", 1)[1]
            why = reject_reason(pid, mod_name, (h.get("fullName") or "/").split("/")[0], repo, via_search=True)
            if why:
                rejected.append("%s (search)" % h.get("fullName"))
                continue
            rec.update(source_kind="github-search", source_url=h.get("url"),
                       license=(h.get("license") or {}).get("key") if isinstance(h.get("license"), dict) else None,
                       last_push=h.get("pushedAt"), archived=h.get("isArchived"), confidence="INFERRED",
                       search_note="search hit whose repo name resembles the mod NAME; not proof - confirm before relying on it")
            break
    if rec["source_url"] is None:
        rec["source_kind"] = "steam-only" if rec.get("steam_url") else "none"
        rec["confidence"] = "INFERRED"
        rec["source_note"] = "no source found (searched: %s)%s%s" % (
            searched, "; NOT_FOUND: " + ", ".join(nf) if nf else "",
            "; REJECTED: " + ", ".join(rejected) if rejected else "")
    elif rejected:
        rec["source_note"] = "REJECTED: " + ", ".join(rejected)
    rec["rejected"] = rejected
    return rec


def git_remote(folder):
    p = os.path.join(folder or "", ".git", "config")
    try:
        return open(p, errors="replace").read()
    except OSError:
        return ""


def readme_text(folder, names):
    out = []
    for rel in names or []:
        try:
            with open(os.path.join(folder, rel), errors="replace") as fh:
                out.append(fh.read(65536))
        except OSError:
            pass
    return "\n".join(out)


def gh_repo(owner, repo, cache, budget):
    key = "%s/%s" % (owner, repo)
    if key.lower() in cache:
        return cache[key.lower()]
    if budget["left"] <= 0:
        return None
    budget["left"] -= 1
    try:
        r = subprocess.run(["gh", "api", "repos/%s" % key, "--jq",
                            "{full_name, html_url, license: .license.spdx_id, pushed_at, archived, fork}"],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"status": "UNVERIFIED", "error": str(e)[:200]}
    if r.returncode == 0:
        res = dict(json.loads(r.stdout), status="VERIFIED")
    elif "Not Found" in (r.stderr + r.stdout) or "404" in r.stderr:
        res = {"status": "NOT_FOUND"}
    else:
        return {"status": "UNVERIFIED", "error": (r.stderr or r.stdout)[:200]}
    cache[key.lower()] = res
    return res


def gh_search(name, cache, budget):
    key = "search:" + name.lower()
    if key in cache:
        return cache[key]
    if budget["left"] <= 0:
        return None
    budget["left"] -= 1
    time.sleep(2.1)                      # search API: 30 requests / minute
    q = re.sub(r"[\[\]()\"']", " ", name)[:80]
    try:
        r = subprocess.run(["gh", "search", "repos", q, "rimworld", "--limit", "3", "--json",
                            "fullName,url,license,pushedAt,isArchived"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"status": "UNVERIFIED", "error": str(e)[:200]}
    if r.returncode != 0:
        return {"status": "UNVERIFIED", "error": (r.stderr or "")[:200]}
    res = {"status": "SEARCHED", "hits": json.loads(r.stdout or "[]")}
    cache[key] = res
    return res


def classify_row(row, disk, cache, budget, do_search):
    pid = row["packageId"]
    d = disk.get(pid) or {}
    ab = d.get("about") or {}
    src = d.get("source") or {}
    wid = d.get("workshop_id")
    rec = {"packageId": pid, "steam_url": ("https://steamcommunity.com/sharedfiles/filedetails/?id=%s" % wid)
           if wid else None, "candidates": [], "source_url": None, "source_kind": "none", "license": None,
           "last_push": None, "archived": None, "confidence": "INFERRED"}
    if row["class"] == "OURS":
        rec.update(source_kind="ours", source_url="git@github.com:Lmandrake/RimMandrake.git (%s)" % (row.get("src") or ""),
                   confidence="MEASURED")
        return rec
    texts = [("about.url", ab.get("url") or ""), ("about.description", ab.get("description") or ""),
             ("readme", readme_text(d.get("folder"), src.get("readme"))), (".git/config", git_remote(d.get("folder")))]
    for where, t in texts:
        for host, owner, repo in extract(t):
            rec["candidates"].append({"where": where, "host": host, "owner": owner, "repo": repo})
    ships = (src.get("cs") or 0) > 0 or (src.get("csproj") or 0) > 0
    for c in rec["candidates"]:
        if c["host"] == "github.com" and c["repo"]:
            v = gh_repo(c["owner"], c["repo"], cache, budget)
            c["verify"] = v
            if v and v.get("status") == "VERIFIED" and rec["source_url"] is None:
                rec.update(source_url=v.get("html_url"), source_kind="github", license=v.get("license"),
                           last_push=v.get("pushed_at"), archived=v.get("archived"), confidence="MEASURED")
    if rec["source_url"] is None:
        repo_c = [c for c in rec["candidates"] if c["repo"]]
        if repo_c:
            c = repo_c[0]
            rec["source_url"] = "https://%s/%s/%s" % (c["host"], c["owner"], c["repo"])
            rec["source_kind"] = "github" if c["host"] == "github.com" else (
                "gitlab" if c["host"] == "gitlab.com" else "other-git")
            st = (c.get("verify") or {}).get("status")
            rec["confidence"] = "UNVERIFIED" if st in (None, "UNVERIFIED") else "INFERRED"
            rec["verify_status"] = st or "NOT_ASKED (budget)"
    if rec["source_url"] is None and ships:
        rec.update(source_kind="ships-source", source_url="(C# source inside the mod folder)", confidence="MEASURED")
    if rec["source_url"] is None and do_search and row["class"] == "THIRD_PARTY" and ab.get("name"):
        s = gh_search(ab["name"], cache, budget)
        if s and s.get("hits"):
            h = s["hits"][0]
            rec.update(source_kind="github-search", source_url=h.get("url"),
                       license=(h.get("license") or {}).get("key") if isinstance(h.get("license"), dict) else None,
                       last_push=h.get("pushedAt"), archived=h.get("isArchived"), confidence="INFERRED",
                       search_note="top hit for the mod NAME; a name match, not proof - confirm before relying on it")
        elif s is not None:
            rec["search_note"] = s.get("status")
    if rec["source_url"] is None:
        if row["class"] == "CORE_DLC":
            rec.update(source_kind="none", confidence="MEASURED", note="Ludeon closed source (decompiled via RimSage)")
        elif wid:
            rec["source_kind"] = "steam-only"
    return rec


def main(argv=None):
    from universe import UNIVERSE_JSON
    import diskfacts
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-requests", type=int, default=450)
    ap.add_argument("--budget", type=float, default=240)
    ap.add_argument("--search", action="store_true")
    a = ap.parse_args(argv)
    rows = json.load(open(UNIVERSE_JSON))["rows"]
    disk = diskfacts.load_all(rows)
    cache = json.load(open(CACHE)) if os.path.isfile(CACHE) else {}
    budget = {"left": a.max_requests}
    t0 = time.time()
    out = json.load(open(OUT)) if os.path.isfile(OUT) else {}
    done = 0
    for r in rows:
        if time.time() - t0 > a.budget:
            break
        prev = out.get(r["packageId"])
        if prev and not (a.search and prev["source_url"] is None and "search_note" not in prev) and \
                prev.get("confidence") != "UNVERIFIED":
            continue
        if r["packageId"] not in disk and r["class"] != "OURS":
            continue
        out[r["packageId"]] = classify_row(r, disk, cache, budget, a.search)
        done += 1
        if done % 25 == 0:
            json.dump(cache, open(CACHE, "w"))
            json.dump(out, open(OUT, "w"))
    json.dump(cache, open(CACHE, "w"))
    json.dump(out, open(OUT, "w"))
    from collections import Counter
    print("sources: %d classified this run, %d total of %d; kinds %s; requests used %d"
          % (done, len(out), len(rows), dict(Counter(v["source_kind"] for v in out.values())),
             a.max_requests - budget["left"]))


if __name__ == "__main__":
    main()
