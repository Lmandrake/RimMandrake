#!/usr/bin/env python3
"""absorbed_gate_lint.py -- is any patch of ours gated on a DONOR whose defs we already own an absorbed copy of?

    python3 src/RimMandrake/Utils/absorbed_gate_lint.py [--json OUT] [--src DIR] [--tsv FILE]

Item LIGHTSABER_ABSORB_COPY_DEPLOYED_BESIDE_DONOR. Armoury ships an absorbed copy of lee.theforce.lightsaber's
kyber chain (same defNames, Armoury loads after the donor, so the copy is the def the game keeps), while
UtinniPatches' RUT_LanternDeepGateKyber.xml zeroed the kyber formations' mineableScatterCommonality inside a
PatchOperationFindMod on the donor's NAME. Today the donor is active and the xpath happens to hit both copies.
The day the donor leaves the list the FindMod goes false, the zeroing never runs, our copy's 0.25 scatter leaks
onto every rocky map, and nothing logs (a patch whose gate is false logs nothing). A gate guarding defs we own
must key on the defs (PatchOperationConditional per defName), never on the mod we absorbed them from.

absorbed copy  every src/**.xml whose header says "Absorbed from <packageId>" (the generators' stamp); its
               concrete defNames and abstract Name="" are the names we own for that donor.
donor key      the donor's packageId (case-insensitive) or its display name, from
               design/RimMandrake/mod_archive/ALL_ORIGINAL_MODS.tsv (PatchOperationFindMod matches NAMES).
gate           a PatchOperationFindMod whose <mods> names a donor key -- the ops under <match> are gated -- or
               any patch element carrying MayRequire / MayRequireAnyOf naming a donor packageId.
hit            a gated op whose xpath names defName="X" (or Name="X") for an X our absorbed copy of THAT donor
               defines. Exit 1 on any hit not in ALLOW. Lifecycle (ACTIVE / retired) is reported, not used:
               a live donor's gate is the same latent leak, it just has not fired yet.

SANITY: exit 2 (UNMEASURED) if no absorbed copy, no patch file, or no donor row is found -- a blind instrument
must not print a clean zero.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SRC = os.path.join(REPO, "src")
MODS_TSV = os.path.join(REPO, "design", "RimMandrake", "mod_archive", "ALL_ORIGINAL_MODS.tsv")

# (repo-relative path, donor packageId lowercase) -> why the gate is deliberate. Keep it short and owned.
ALLOW: dict = {}

# (repo-relative path, donor packageId lowercase) -> the filed item that owes the rekey. Reported as OWED, not
# red, so this lint can guard NEW gates today; the item closes by emptying this table, never by growing it.
# Emptied 2026-10-26 (DONOR_GATES_REWIRE_DEAD_SINCE_RETIREMENT): the 7 kotorcore/vaewaste gates were rekeyed
# onto PatchOperationConditional on the target def, so any donor-name gate over an absorbed def is now a HIT.
OWED: dict = {}

ABSORBED_RE = re.compile(r"Absorbed from\s+([A-Za-z0-9_.]+)")
NAME_IN_XPATH_RE = re.compile(r'(?:defName|@Name)\s*=\s*["\']([^"\']+)["\']|defName\s*\[\s*text\(\)\s*=\s*["\']([^"\']+)["\']')
SKIP_DIRS = {".git", "__pycache__", "bin", "obj", "node_modules"}


def _xml_files(root, want_patches=None):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        parts = os.path.relpath(d, root).replace("\\", "/").split("/")
        in_patches = "Patches" in parts
        if want_patches is not None and in_patches != want_patches:
            continue
        for f in files:
            if f.lower().endswith(".xml"):
                yield os.path.join(d, f)


def _head(path, n=4096):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read(n)
    except OSError:
        return ""


def _parse(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None


def absorbed_copies(src=SRC):
    """{donor_pid_lower: {"names": set, "files": [rel]}} from files stamped 'Absorbed from <pid>'."""
    out = {}
    for path in _xml_files(src, want_patches=False):
        m = ABSORBED_RE.search(_head(path))
        if not m:
            continue
        root = _parse(path)
        if root is None:
            continue
        names = set()
        for el in root:
            dn = el.findtext("defName")
            if dn and dn.strip():
                names.add(dn.strip())
            if el.get("Name"):
                names.add(el.get("Name").strip())
        if not names:
            continue
        rec = out.setdefault(m.group(1).lower(), {"names": set(), "files": []})
        rec["names"] |= names
        rec["files"].append(os.path.relpath(path, REPO).replace("\\", "/"))
    return out


def donor_table(tsv=MODS_TSV):
    """{pid_lower: {"name": display name, "lifecycle": str}}."""
    out = {}
    try:
        with open(tsv, encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                pid = (row.get("packageId") or "").strip().lower()
                if pid:
                    out[pid] = {"name": (row.get("name") or "").strip(), "lifecycle": (row.get("lifecycle") or "").strip()}
    except OSError:
        pass
    return out


def _xpath_names(el):
    names = set()
    for sub in el.iter():
        if sub.tag in ("xpath", "success") or sub.tag.endswith("xpath"):
            for a, b in NAME_IN_XPATH_RE.findall(sub.text or ""):
                names.add(a or b)
    return names


def _gates(root, keys_by_pid):
    """Yield (donor_pid, kind, element) for every donor-keyed gate in one patch file."""
    name_to_pid = {}
    for pid, keys in keys_by_pid.items():
        for k in keys:
            name_to_pid[k] = pid
    for el in root.iter():
        cls = el.get("Class") or ""
        if cls.endswith("PatchOperationFindMod"):
            mods = el.find("mods")
            listed = [(li.text or "").strip() for li in (mods if mods is not None else [])]
            match = el.find("match")
            pids = [name_to_pid.get(t) or name_to_pid.get(t.lower()) for t in listed]
            # FindMod is an OR: one listed name that is not a donor (our copy's own mod, as
            # RM_LanternDeepGatePyrinth.xml lists "RimMandrake: Pyrinth") keeps the gate alive.
            if match is not None and pids and all(pids):
                for hit in dict.fromkeys(pids):
                    yield hit, "PatchOperationFindMod(%s)" % " | ".join(listed), match
        for attr in ("MayRequire", "MayRequireAnyOf"):
            v = el.get(attr)
            if not v:
                continue
            for p in v.split(","):
                p = p.strip().lower()
                if p in keys_by_pid:
                    yield p, "%s=%s" % (attr, v), el


def scan(src=SRC, tsv=MODS_TSV, allow=None, owed=None, repo=REPO):
    allow = ALLOW if allow is None else allow
    owed = OWED if owed is None else owed
    copies = absorbed_copies(src)
    donors = donor_table(tsv)
    keys_by_pid = {}
    for pid in copies:
        keys = {pid}
        nm = donors.get(pid, {}).get("name")
        if nm:
            keys.add(nm)
        keys_by_pid[pid] = keys
    hits, allowed, owing, patch_files = [], [], [], 0
    for path in _xml_files(src, want_patches=True):
        root = _parse(path)
        if root is None:
            continue
        patch_files += 1
        rel = os.path.relpath(path, repo).replace("\\", "/")
        seen = set()
        for pid, kind, el in _gates(root, keys_by_pid):
            owned = sorted(_xpath_names(el) & copies[pid]["names"])
            if not owned or (pid, kind, tuple(owned)) in seen:
                continue
            seen.add((pid, kind, tuple(owned)))
            row = {"file": rel, "donor": pid, "lifecycle": donors.get(pid, {}).get("lifecycle", "?"),
                   "gate": kind, "ownedDefs": owned, "absorbedIn": sorted(copies[pid]["files"])[:3]}
            if (rel, pid) in allow:
                allowed.append(row)
            elif (rel, pid) in owed:
                row["owedBy"] = owed[(rel, pid)]
                owing.append(row)
            else:
                hits.append(row)
    live_owed = {(r["file"], r["donor"]) for r in owing}
    stale = sorted("%s [%s]" % k for k in owed if k not in live_owed)
    return {"absorbedDonors": len(copies), "absorbedNames": sum(len(c["names"]) for c in copies.values()),
            "donorRows": len(donors), "patchFiles": patch_files, "hits": hits, "allowed": allowed,
            "owed": owing, "staleOwed": stale}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the full result here")
    ap.add_argument("--src", default=SRC, help="tree to scan (default: the repo's src/)")
    ap.add_argument("--tsv", default=MODS_TSV, help="donor table (default: ALL_ORIGINAL_MODS.tsv)")
    a = ap.parse_args(argv)
    r = scan(src=a.src, tsv=a.tsv)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=1)
    print("absorbed donors %d (%d owned names), donor rows %d, patch files %d" % (
        r["absorbedDonors"], r["absorbedNames"], r["donorRows"], r["patchFiles"]))
    if not r["absorbedDonors"] or not r["patchFiles"] or not r["donorRows"]:
        print("UNMEASURED: the instrument saw no absorbed copy, no patch file or no donor table")
        return 2
    for h in r["hits"]:
        print("HIT %s: %s gate on donor %s [%s] guards defs our absorbed copy owns: %s" % (
            h["file"], h["gate"], h["donor"], h["lifecycle"], ", ".join(h["ownedDefs"][:6])))
    for h in r["owed"]:
        print("OWED %s: %s on donor %s [%s] -> %s" % (h["file"], h["gate"], h["donor"], h["lifecycle"], h["owedBy"]))
    for k in r["staleOwed"]:
        print("STALE OWED %s: no longer a hit -- delete its OWED row" % k)
    print("%d donor-keyed gate(s) over absorbed defs, %d owed, %d allowed, %d stale owed row(s)" % (
        len(r["hits"]), len(r["owed"]), len(r["allowed"]), len(r["staleOwed"])))
    return 1 if (r["hits"] or r["staleOwed"]) else 0


if __name__ == "__main__":
    sys.exit(main())
