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
